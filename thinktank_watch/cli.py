from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import httpx

from .audit import write_audit_report
from .archive import write_article
from .brief import write_daily_brief
from .config import load_institutions, load_priority_rules, load_topics
from .fetch import check_pdf, fetch_detail, fetch_feed_candidates, fetch_list_candidates, fetch_sitemap_candidates, make_client
from .kb import append_kb_index, write_institution_table
from .models import ArticleCandidate, Institution
from .scoring import score_candidate
from .state import ArticleState


DEFAULT_CONFIG = Path("config")


def _load_config():
    institutions = load_institutions(DEFAULT_CONFIG / "institutions")
    topics = load_topics(DEFAULT_CONFIG / "topics.yaml")
    priorities = load_priority_rules(DEFAULT_CONFIG / "priorities.yaml")
    return institutions, topics, priorities


def _select_institutions(institutions: list[Institution], batch: int | None, slug: str | None) -> list[Institution]:
    selected = institutions
    if batch is not None:
        selected = [item for item in selected if item.batch <= batch]
    if slug:
        selected = [item for item in selected if item.slug == slug]
    return selected


def fetch_status_from_http_error(exc: httpx.HTTPError) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return f"detail_error:{exc.response.status_code}"
    return f"detail_error:{exc.__class__.__name__}"


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
            if backfill:
                base = [
                    *fetch_feed_candidates(institution, limit=limit),
                    *fetch_list_candidates(client, institution, limit=limit),
                    *fetch_sitemap_candidates(client, institution, limit=limit),
                ]
            else:
                base = fetch_feed_candidates(institution, limit=limit)
                if not base:
                    base = fetch_list_candidates(client, institution, limit=limit)
            institution_count = 0
            for candidate in base:
                if institution_count >= limit:
                    break
                if candidate.url in seen_urls:
                    continue
                seen_urls.add(candidate.url)
                institution_count += 1
                if include_details:
                    try:
                        candidate = fetch_detail(client, institution, candidate)
                        candidate = check_pdf(client, candidate)
                    except httpx.HTTPError as exc:
                        candidate.fetch_status = fetch_status_from_http_error(exc)
                collected.append(candidate)
    return collected


def evaluate(args: argparse.Namespace) -> int:
    institutions, topics, priorities = _load_config()
    selected = _select_institutions(institutions, args.batch, args.institution)
    candidates = collect_candidates(selected, args.limit, include_details=not args.no_details)
    scored = [score_candidate(item, topics, priorities) for item in candidates]
    for item in sorted(scored, key=lambda row: (row.priority, -row.score, row.institution_slug)):
        print(
            f"[{item.priority}/{item.score}] {item.institution_slug} | "
            f"{item.published_date or 'undated'} | {item.title} | {item.url}"
        )
        if item.topic_tags:
            print(f"  topics: {', '.join(item.topic_tags)}")
        if item.pdf_url:
            print(f"  pdf: {item.pdf_url} ({item.pdf_status})")
    return 0


def audit(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    institutions, topics, priorities = _load_config()
    selected = _select_institutions(institutions, args.batch, args.institution)
    candidates = collect_candidates(selected, args.limit, include_details=not args.no_details)
    scored = [score_candidate(item, topics, priorities) for item in candidates]
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
        for item in candidates:
            item = score_candidate(item, topics, priorities)
            if state.seen(item.url) and not args.refresh:
                continue
            archive_path = ""
            if item.priority in {"P0", "P1", "P2"}:
                archive_path = str(write_article(args.archive_root, item))
            state.upsert(item, archive_path)
            written.append(item)
        write_daily_brief(args.brief_root, run_date, written)
        if not args.skip_kb:
            append_kb_index(written, run_date, args.kb_root)
            write_institution_table(institutions, args.kb_root)
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
        for item in candidates:
            item = score_candidate(item, topics, priorities)
            if state.seen(item.url) and not args.refresh:
                continue
            archive_path = ""
            if item.priority in {"P0", "P1", "P2"}:
                archive_path = str(write_article(args.archive_root, item))
            state.upsert(item, archive_path)
            written.append(item)
        write_daily_brief(args.brief_root, run_date, written)
        if not args.skip_kb:
            append_kb_index(written, run_date, args.kb_root)
            write_institution_table(institutions, args.kb_root)
    finally:
        state.close()
    print(f"backfill_date={run_date} institutions={len(selected)} candidates_written={len(written)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="thinktank-watch")
    sub = parser.add_subparsers(dest="command", required=True)

    eval_parser = sub.add_parser("evaluate", help="Fetch and score candidates without writing archive files.")
    eval_parser.add_argument("--batch", type=int, default=1)
    eval_parser.add_argument("--institution")
    eval_parser.add_argument("--limit", type=int, default=5)
    eval_parser.add_argument("--no-details", action="store_true")
    eval_parser.add_argument("--dry-run", action="store_true", help="Alias for evaluate compatibility.")
    eval_parser.set_defaults(func=evaluate)

    audit_parser = sub.add_parser("audit", help="Fetch candidates and write a source health CSV without archiving.")
    audit_parser.add_argument("--batch", type=int, default=1)
    audit_parser.add_argument("--institution")
    audit_parser.add_argument("--limit", type=int, default=5)
    audit_parser.add_argument("--date")
    audit_parser.add_argument("--no-details", action="store_true")
    audit_parser.add_argument("--output")
    audit_parser.set_defaults(func=audit)

    daily = sub.add_parser("run-daily", help="Run daily fetch, archive, brief, and KB index update.")
    daily.add_argument("--batch", type=int, default=1)
    daily.add_argument("--institution")
    daily.add_argument("--limit", type=int, default=20)
    daily.add_argument("--date")
    daily.add_argument("--refresh", action="store_true")
    daily.add_argument("--skip-kb", action="store_true")
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
    backfill_parser.add_argument("--archive-root", default="archive")
    backfill_parser.add_argument("--brief-root", default="briefs")
    backfill_parser.add_argument("--state", default="state/articles.sqlite")
    backfill_parser.add_argument("--kb-root", default=str(Path(r"C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库")))
    backfill_parser.set_defaults(func=backfill)

    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
