from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import httpx

from .audit import write_audit_report
from .archive import write_article
from .brief import load_daily_brief_candidates, write_daily_brief
from .config import load_institutions, load_priority_rules, load_topics
from .fetch import (
    check_pdf,
    enrich_detail_text_from_pdf,
    fetch_detail,
    fetch_feed_candidates,
    fetch_list_candidates,
    fetch_sitemap_candidates,
    interleave_candidate_groups,
    make_client,
)
from .kb import append_kb_index, write_institution_table
from .models import ArticleCandidate, Institution
from .restore import rebuild_state_from_archive
from .scoring import score_candidate
from .state import ArticleState


DEFAULT_CONFIG = Path("config")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def _load_config():
    institutions = load_institutions(DEFAULT_CONFIG / "institutions")
    topics = load_topics(DEFAULT_CONFIG / "topics.yaml")
    priorities = load_priority_rules(DEFAULT_CONFIG / "priorities.yaml")
    return institutions, topics, priorities


def _select_institutions(institutions: list[Institution], batch: int | None, slug: str | None) -> list[Institution]:
    selected = institutions
    if slug:
        return [item for item in selected if item.slug == slug]
    if batch is not None:
        selected = [item for item in selected if item.batch <= batch]
    return selected


def fetch_status_from_http_error(exc: httpx.HTTPError) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return f"detail_error:{exc.response.status_code}"
    return f"detail_error:{exc.__class__.__name__}"


def priority_allows(priority: str, minimum: str = "P3") -> bool:
    if priority not in PRIORITY_ORDER:
        return False
    if minimum not in PRIORITY_ORDER:
        raise ValueError(f"Unsupported priority: {minimum}")
    return PRIORITY_ORDER[priority] <= PRIORITY_ORDER[minimum]


def write_limit_reached(written_count: int, write_limit: int | None) -> bool:
    return bool(write_limit) and written_count >= write_limit


def candidate_matches_include_terms(candidate: ArticleCandidate, include_terms: list[str] | None) -> bool:
    terms = [term.lower().strip() for term in (include_terms or []) if term.strip()]
    if not terms:
        return True
    haystack = " ".join(
        [
            candidate.title,
            candidate.chinese_title,
            candidate.url,
            candidate.summary,
            candidate.chinese_summary,
            candidate.pdf_url,
            " ".join(candidate.keywords),
            " ".join(candidate.subjects),
            " ".join(candidate.topic_tags),
        ]
    ).lower()
    return any(term in haystack for term in terms)


def institution_fetch_limit(institution: Institution, limit: int) -> int:
    if institution.run_limit > 0:
        return min(limit, institution.run_limit)
    return limit


def published_date_sort_value(value: str) -> int:
    if len(value or "") < 10:
        return 0
    try:
        return int(value[:10].replace("-", ""))
    except ValueError:
        return 0


def candidate_is_future(candidate: ArticleCandidate, run_date: str) -> bool:
    if len(candidate.published_date or "") < 10 or len(run_date or "") < 10:
        return False
    try:
        published = date.fromisoformat(candidate.published_date[:10])
        current = date.fromisoformat(run_date[:10])
    except ValueError:
        return False
    return published > current


def sort_for_writing(candidates: list[ArticleCandidate]) -> list[ArticleCandidate]:
    return sorted(
        candidates,
        key=lambda item: (
            PRIORITY_ORDER.get(item.priority, 99),
            -item.score,
            -published_date_sort_value(item.published_date),
            item.institution_slug,
            item.title,
        ),
    )


def detail_fetch_failed(candidate: ArticleCandidate) -> bool:
    return candidate.fetch_status.startswith("detail_error")


def should_archive_candidate(candidate: ArticleCandidate) -> bool:
    return candidate.priority in {"P0", "P1", "P2"} and not detail_fetch_failed(candidate)


def write_run_brief(args: argparse.Namespace, run_date: str, written: list[ArticleCandidate]) -> None:
    candidates = written
    if not args.skip_kb:
        indexed = load_daily_brief_candidates(args.archive_root, args.kb_root, run_date)
        if indexed:
            candidates = indexed
    write_daily_brief(args.brief_root, run_date, candidates)


def collect_candidates(
    institutions: list[Institution],
    limit: int,
    include_details: bool,
    backfill: bool = False,
) -> list[ArticleCandidate]:
    collected: list[ArticleCandidate] = []
    seen_urls: set[str] = set()
    with make_client() as client:
        for institution in institutions:
            item_limit = institution_fetch_limit(institution, limit)
            if backfill:
                base = interleave_candidate_groups(
                    [
                        fetch_feed_candidates(institution, limit=item_limit),
                        fetch_list_candidates(client, institution, limit=item_limit),
                        fetch_sitemap_candidates(client, institution, limit=item_limit),
                    ]
                )
            else:
                base = fetch_feed_candidates(institution, limit=item_limit)
                if not base:
                    base = fetch_list_candidates(client, institution, limit=item_limit)
            institution_count = 0
            for candidate in base:
                if institution_count >= item_limit:
                    break
                if candidate.url in seen_urls:
                    continue
                seen_urls.add(candidate.url)
                institution_count += 1
                if include_details:
                    try:
                        candidate = fetch_detail(client, institution, candidate)
                        candidate = check_pdf(client, candidate)
                        candidate = enrich_detail_text_from_pdf(client, candidate)
                    except httpx.HTTPError as exc:
                        candidate.fetch_status = fetch_status_from_http_error(exc)
                collected.append(candidate)
    return collected


def evaluate(args: argparse.Namespace) -> int:
    institutions, topics, priorities = _load_config()
    selected = _select_institutions(institutions, args.batch, args.institution)
    candidates = collect_candidates(selected, args.limit, include_details=not args.no_details, backfill=args.backfill)
    scored = [
        item
        for item in [score_candidate(item, topics, priorities) for item in candidates]
        if candidate_matches_include_terms(item, getattr(args, "include_terms", None))
    ]
    for item in sorted(scored, key=lambda row: (row.priority, -row.score, row.institution_slug)):
        print(
            f"[{item.priority}/{item.score}] {item.institution_slug} | "
            f"{item.published_date or 'undated'} | {item.title} | {item.url}"
        )
        if item.topic_tags:
            print(f"  topics: {', '.join(item.topic_tags)}")
        if item.pdf_url:
            print(f"  pdf: {item.pdf_url} ({item.pdf_status})")
        if item.fetch_status not in {"feed_ok", "list_ok", "sitemap_ok", "detail_ok"}:
            print(f"  status: {item.fetch_status}")
    return 0


def audit(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    institutions, topics, priorities = _load_config()
    selected = _select_institutions(institutions, args.batch, args.institution)
    candidates = collect_candidates(selected, args.limit, include_details=not args.no_details)
    scored = [
        item
        for item in [score_candidate(item, topics, priorities) for item in candidates]
        if candidate_matches_include_terms(item, getattr(args, "include_terms", None))
    ]
    output = Path(args.output) if args.output else Path("reports") / f"{run_date}_source_health.csv"
    path = write_audit_report(output, scored)
    print(f"audit_date={run_date} institutions={len(selected)} candidates={len(scored)} report={path}")
    return 0


def run_daily(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    institutions, topics, priorities = _load_config()
    selected = _select_institutions(institutions, args.batch, args.institution)
    state = ArticleState(args.state)
    written: list[ArticleCandidate] = []
    try:
        candidates = collect_candidates(selected, args.limit, include_details=True)
        scored = sort_for_writing(
            [
                item
                for item in [score_candidate(item, topics, priorities) for item in candidates]
                if candidate_matches_include_terms(item, getattr(args, "include_terms", None))
            ]
        )
        for item in scored:
            if not priority_allows(item.priority, args.min_priority):
                continue
            if candidate_is_future(item, run_date):
                continue
            if state.seen(item.url) and not args.refresh:
                continue
            if write_limit_reached(len(written), args.write_limit):
                break
            if detail_fetch_failed(item):
                state.upsert(item, "")
                continue
            archive_path = ""
            if should_archive_candidate(item):
                archive_path = str(write_article(args.archive_root, item))
            state.upsert(item, archive_path)
            written.append(item)
        if not args.skip_kb:
            append_kb_index(written, run_date, args.kb_root)
            write_institution_table(institutions, args.kb_root)
        write_run_brief(args, run_date, written)
    finally:
        state.close()
    print(f"run_date={run_date} institutions={len(selected)} candidates_written={len(written)}")
    return 0


def backfill(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    institutions, topics, priorities = _load_config()
    selected = _select_institutions(institutions, args.batch, args.institution)
    state = ArticleState(args.state)
    written: list[ArticleCandidate] = []
    try:
        candidates = collect_candidates(selected, args.limit, include_details=True, backfill=True)
        scored = sort_for_writing(
            [
                item
                for item in [score_candidate(item, topics, priorities) for item in candidates]
                if candidate_matches_include_terms(item, getattr(args, "include_terms", None))
            ]
        )
        for item in scored:
            if not priority_allows(item.priority, args.min_priority):
                continue
            if candidate_is_future(item, run_date):
                continue
            if state.seen(item.url) and not args.refresh:
                continue
            if write_limit_reached(len(written), args.write_limit):
                break
            if detail_fetch_failed(item):
                state.upsert(item, "")
                continue
            archive_path = ""
            if should_archive_candidate(item):
                archive_path = str(write_article(args.archive_root, item))
            state.upsert(item, archive_path)
            written.append(item)
        if not args.skip_kb:
            append_kb_index(written, run_date, args.kb_root)
            write_institution_table(institutions, args.kb_root)
        write_run_brief(args, run_date, written)
    finally:
        state.close()
    print(f"backfill_date={run_date} institutions={len(selected)} candidates_written={len(written)}")
    return 0


def rebuild_state(args: argparse.Namespace) -> int:
    count = rebuild_state_from_archive(args.archive_root, args.state)
    print(f"archive_root={args.archive_root} state={args.state} records_restored={count}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="thinktank-watch")
    sub = parser.add_subparsers(dest="command", required=True)

    eval_parser = sub.add_parser("evaluate", help="Fetch and score candidates without writing archive files.")
    eval_parser.add_argument("--batch", type=int, default=1)
    eval_parser.add_argument("--institution")
    eval_parser.add_argument("--limit", type=int, default=5)
    eval_parser.add_argument("--no-details", action="store_true")
    eval_parser.add_argument("--backfill", action="store_true", help="Evaluate feeds, lists, and sitemap backfill sources without writing.")
    eval_parser.add_argument("--include-term", dest="include_terms", action="append", default=[])
    eval_parser.add_argument("--dry-run", action="store_true", help="Alias for evaluate compatibility.")
    eval_parser.set_defaults(func=evaluate)

    audit_parser = sub.add_parser("audit", help="Fetch candidates and write a source health CSV without archiving.")
    audit_parser.add_argument("--batch", type=int, default=1)
    audit_parser.add_argument("--institution")
    audit_parser.add_argument("--limit", type=int, default=5)
    audit_parser.add_argument("--date")
    audit_parser.add_argument("--no-details", action="store_true")
    audit_parser.add_argument("--include-term", dest="include_terms", action="append", default=[])
    audit_parser.add_argument("--output")
    audit_parser.set_defaults(func=audit)

    daily = sub.add_parser("run-daily", help="Run daily fetch, archive, brief, and KB index update.")
    daily.add_argument("--batch", type=int, default=1)
    daily.add_argument("--institution")
    daily.add_argument("--limit", type=int, default=20)
    daily.add_argument("--date")
    daily.add_argument("--refresh", action="store_true")
    daily.add_argument("--skip-kb", action="store_true")
    daily.add_argument("--min-priority", choices=sorted(PRIORITY_ORDER), default="P3")
    daily.add_argument("--write-limit", type=int, default=0, help="Maximum number of new allowed records to write. 0 means unlimited.")
    daily.add_argument("--include-term", dest="include_terms", action="append", default=[])
    daily.add_argument("--archive-root", default="archive")
    daily.add_argument("--brief-root", default="briefs")
    daily.add_argument("--state", default="state/articles.sqlite")
    daily.add_argument("--kb-root", default=str(Path(r"C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库")))
    daily.set_defaults(func=run_daily)

    backfill_parser = sub.add_parser("backfill", help="Initialize archive from feeds, list pages, and configured sitemaps.")
    backfill_parser.add_argument("--batch", type=int, default=1)
    backfill_parser.add_argument("--institution")
    backfill_parser.add_argument("--limit", type=int, default=200)
    backfill_parser.add_argument("--date")
    backfill_parser.add_argument("--refresh", action="store_true")
    backfill_parser.add_argument("--skip-kb", action="store_true")
    backfill_parser.add_argument("--min-priority", choices=sorted(PRIORITY_ORDER), default="P3")
    backfill_parser.add_argument("--write-limit", type=int, default=0, help="Maximum number of new allowed records to write. 0 means unlimited.")
    backfill_parser.add_argument("--include-term", dest="include_terms", action="append", default=[])
    backfill_parser.add_argument("--archive-root", default="archive")
    backfill_parser.add_argument("--brief-root", default="briefs")
    backfill_parser.add_argument("--state", default="state/articles.sqlite")
    backfill_parser.add_argument("--kb-root", default=str(Path(r"C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库")))
    backfill_parser.set_defaults(func=backfill)

    rebuild_parser = sub.add_parser("rebuild-state", help="Rebuild local dedupe state from archived Markdown files.")
    rebuild_parser.add_argument("--archive-root", default="archive")
    rebuild_parser.add_argument("--state", default="state/articles.sqlite")
    rebuild_parser.set_defaults(func=rebuild_state)

    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
