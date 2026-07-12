from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import httpx

from .audit import write_audit_report
from .archive import write_article
from .brief import (
    inspect_weekly_comic_report,
    load_daily_brief_candidates,
    load_weekly_archive_candidates,
    weekly_comic_run_dir,
    write_periodic_brief,
    write_weekly_comic_prompts,
)
from .config import load_institutions, load_priority_rules, load_search_profiles, load_topics
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
from .focus import innovation_support_sort_rank, is_innovation_support_candidate
from .kb import append_kb_index, write_institution_table
from .models import ArticleCandidate, Institution
from .restore import rebuild_state_from_archive
from .scoring import score_candidate
from .state import ArticleState


DEFAULT_CONFIG = Path("config")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
DEFAULT_BACKFILL_LOOKBACK_YEARS = 3
DEFAULT_DAILY_LOOKBACK_DAYS = 30
DEFAULT_WEEKLY_LOOKBACK_DAYS = 7
DEFAULT_EXPANDED_SEARCH_PROFILE = "broad_innovation_support"


def _load_config():
    institutions = load_institutions(DEFAULT_CONFIG / "institutions")
    topics = load_topics(DEFAULT_CONFIG / "topics.yaml")
    priorities = load_priority_rules(DEFAULT_CONFIG / "priorities.yaml")
    return institutions, topics, priorities


def resolve_search_profile(name: str | None):
    if not name:
        return None
    profiles = load_search_profiles(DEFAULT_CONFIG / "search_profiles.yaml")
    try:
        return profiles[name]
    except KeyError as exc:
        available = ", ".join(sorted(profiles)) or "none"
        raise ValueError(f"Unsupported search profile: {name}. Available profiles: {available}") from exc


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


def innovation_support_quota(write_limit: int | None) -> int:
    if not write_limit:
        return 0
    return max(1, write_limit // 2)


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
    return any(include_term_matches_haystack(term, haystack) for term in terms)


def candidate_matches_search_profile(candidate: ArticleCandidate, profile) -> bool:
    if profile is None:
        return True
    if profile.include_terms and not candidate_matches_include_terms(candidate, profile.include_terms):
        return False
    if profile.topic_tags_any and not (set(profile.topic_tags_any) & set(candidate.topic_tags)):
        return False
    if profile.exclude_governance_only and innovation_support_sort_rank(candidate) == 2:
        return False
    return True


def candidate_matches_filters(candidate: ArticleCandidate, args: argparse.Namespace, profile=None) -> bool:
    return candidate_matches_search_profile(candidate, profile) and candidate_matches_include_terms(
        candidate,
        getattr(args, "include_terms", None),
    )


def include_term_matches_haystack(term: str, haystack: str) -> bool:
    if re.fullmatch(r"[a-z0-9]{1,3}", term):
        return re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", haystack) is not None
    return term in haystack


def filter_unseen_candidates(candidates: list[ArticleCandidate], state_path: str | Path) -> list[ArticleCandidate]:
    state = ArticleState(state_path)
    try:
        return [item for item in candidates if not state.seen(item.url)]
    finally:
        state.close()


def filter_unarchived_candidates(candidates: list[ArticleCandidate], state_path: str | Path) -> list[ArticleCandidate]:
    state = ArticleState(state_path)
    try:
        return [item for item in candidates if not state.archived(item.url)]
    finally:
        state.close()


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


def parse_candidate_date(value: str) -> date | None:
    if len(value or "") < 10:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def candidate_is_future(candidate: ArticleCandidate, run_date: str) -> bool:
    published = parse_candidate_date(candidate.published_date)
    current = parse_candidate_date(run_date)
    if not published or not current:
        return False
    return published > current


def subtract_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year - years)
    except ValueError:
        return value.replace(year=value.year - years, day=28)


def backfill_window_start(run_date: str, lookback_years: int) -> date:
    current = parse_candidate_date(run_date)
    if not current:
        raise ValueError(f"Invalid run date: {run_date}")
    if lookback_years < 1:
        raise ValueError("lookback_years must be positive")
    return subtract_years(current, lookback_years)


def candidate_within_backfill_window(candidate: ArticleCandidate, run_date: str, lookback_years: int) -> bool:
    published = parse_candidate_date(candidate.published_date)
    current = parse_candidate_date(run_date)
    if not published or not current:
        return False
    return backfill_window_start(run_date, lookback_years) <= published <= current


def daily_window_start(run_date: str, lookback_days: int) -> date:
    current = parse_candidate_date(run_date)
    if not current:
        raise ValueError(f"Invalid run date: {run_date}")
    if lookback_days < 1:
        raise ValueError("lookback_days must be positive")
    return current - timedelta(days=lookback_days)


def candidate_within_daily_window(candidate: ArticleCandidate, run_date: str, lookback_days: int) -> bool:
    published = parse_candidate_date(candidate.published_date)
    current = parse_candidate_date(run_date)
    if not published or not current:
        return False
    return daily_window_start(run_date, lookback_days) <= published <= current


def sort_for_writing(candidates: list[ArticleCandidate]) -> list[ArticleCandidate]:
    return sorted(
        candidates,
        key=lambda item: (
            PRIORITY_ORDER.get(item.priority, 99),
            innovation_support_sort_rank(item),
            -item.score,
            -published_date_sort_value(item.published_date),
            item.institution_slug,
            item.title,
        ),
    )


def balance_limited_write_queue(candidates: list[ArticleCandidate], write_limit: int | None) -> list[ArticleCandidate]:
    ordered = sort_for_writing(candidates)
    quota = innovation_support_quota(write_limit)
    if not quota:
        return ordered

    selected: list[ArticleCandidate] = []
    selected_urls: set[str] = set()
    support_count = 0

    for item in ordered:
        if support_count >= quota:
            break
        if is_innovation_support_candidate(item):
            selected.append(item)
            selected_urls.add(item.url)
            support_count += 1

    for item in ordered:
        if item.url in selected_urls:
            continue
        selected.append(item)
        selected_urls.add(item.url)
    return selected


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
    write_periodic_brief(
        args.brief_root,
        run_date,
        candidates,
        cadence=getattr(args, "brief_cadence", "daily"),
    )


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
    profile = resolve_search_profile(getattr(args, "search_profile", None))
    selected = _select_institutions(institutions, args.batch, args.institution)
    candidates = collect_candidates(selected, args.limit, include_details=not args.no_details, backfill=args.backfill)
    scored = [
        item
        for item in [score_candidate(item, topics, priorities) for item in candidates]
        if candidate_matches_filters(item, args, profile)
    ]
    if args.backfill:
        run_date = getattr(args, "date", None) or date.today().isoformat()
        lookback_years = getattr(args, "lookback_years", DEFAULT_BACKFILL_LOOKBACK_YEARS)
        scored = [
            item
            for item in scored
            if candidate_within_backfill_window(item, run_date, lookback_years)
        ]
    if getattr(args, "unseen_only", False):
        scored = filter_unseen_candidates(scored, getattr(args, "state", "state/articles.sqlite"))
    if getattr(args, "unarchived_only", False):
        scored = filter_unarchived_candidates(scored, getattr(args, "state", "state/articles.sqlite"))
    for item in sort_for_writing(scored):
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
    profile = resolve_search_profile(getattr(args, "search_profile", None))
    selected = _select_institutions(institutions, args.batch, args.institution)
    candidates = collect_candidates(selected, args.limit, include_details=not args.no_details)
    scored = [
        item
        for item in [score_candidate(item, topics, priorities) for item in candidates]
        if candidate_matches_filters(item, args, profile)
    ]
    output = Path(args.output) if args.output else Path("reports") / f"{run_date}_source_health.csv"
    path = write_audit_report(output, scored)
    print(f"audit_date={run_date} institutions={len(selected)} candidates={len(scored)} report={path}")
    return 0


def run_daily(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    institutions, topics, priorities = _load_config()
    profile = resolve_search_profile(getattr(args, "search_profile", None))
    selected = _select_institutions(institutions, args.batch, args.institution)
    state = ArticleState(args.state)
    written: list[ArticleCandidate] = []
    try:
        candidates = collect_candidates(selected, args.limit, include_details=True)
        scored = balance_limited_write_queue(
            [
                item
                for item in [score_candidate(item, topics, priorities) for item in candidates]
                if candidate_matches_filters(item, args, profile)
            ],
            args.write_limit,
        )
        for item in scored:
            if not priority_allows(item.priority, args.min_priority):
                continue
            if candidate_is_future(item, run_date):
                continue
            if state.seen(item.url) and not args.refresh:
                continue
            if detail_fetch_failed(item):
                state.upsert(item, "")
                continue
            if not candidate_within_daily_window(
                item,
                run_date,
                getattr(args, "lookback_days", DEFAULT_DAILY_LOOKBACK_DAYS),
            ):
                continue
            if write_limit_reached(len(written), args.write_limit):
                break
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


def run_weekly(args: argparse.Namespace) -> int:
    args.brief_cadence = "weekly"
    return run_daily(args)


def prepare_weekly_comics(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    candidates = load_weekly_archive_candidates(args.archive_root, run_date, args.lookback_days)
    prompt_paths = write_weekly_comic_prompts(run_date, candidates, args.comic_root)
    print(
        f"weekly_comic_prompts={len(prompt_paths)} "
        f"run_dir={weekly_comic_run_dir(run_date, args.comic_root)}"
    )
    return 0


def render_weekly_brief(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    candidates = load_weekly_archive_candidates(args.archive_root, run_date, args.lookback_days)
    paths = write_periodic_brief(args.brief_root, run_date, candidates, cadence="weekly")
    print(f"weekly_candidates={len(candidates)}")
    for path in paths:
        print(path)
    return 0


def check_weekly_comics(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    candidates = load_weekly_archive_candidates(args.archive_root, run_date, args.lookback_days)
    stats = inspect_weekly_comic_report(run_date, candidates, args.brief_root, args.comic_root)
    failures: list[str] = []
    expected = int(stats["priority_count"])
    for key in ["prompt_count", "comic_count", "md_image_refs", "html_image_nodes", "pdf_image_count"]:
        value = int(stats[key])
        if value < expected:
            failures.append(f"{key}={value} < priority_count={expected}")
    if stats["missing_files"]:
        failures.append("missing_files=" + ";".join(str(item) for item in stats["missing_files"]))
    if stats["blocked_hits"]:
        failures.append("blocked_hits=" + ";".join(str(item) for item in stats["blocked_hits"]))
    for key, value in stats.items():
        print(f"{key}={value}")
    if failures:
        print("weekly_comic_check=failed")
        for failure in failures:
            print(f"failure={failure}")
        return 1
    print("weekly_comic_check=ok")
    return 0


def backfill(args: argparse.Namespace) -> int:
    run_date = args.date or date.today().isoformat()
    institutions, topics, priorities = _load_config()
    profile = resolve_search_profile(getattr(args, "search_profile", None))
    selected = _select_institutions(institutions, args.batch, args.institution)
    state = ArticleState(args.state)
    written: list[ArticleCandidate] = []
    try:
        candidates = collect_candidates(selected, args.limit, include_details=True, backfill=True)
        scored = balance_limited_write_queue(
            [
                item
                for item in [score_candidate(item, topics, priorities) for item in candidates]
                if candidate_matches_filters(item, args, profile)
            ],
            args.write_limit,
        )
        for item in scored:
            if not priority_allows(item.priority, args.min_priority):
                continue
            if not candidate_within_backfill_window(item, run_date, args.lookback_years):
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
    eval_parser.add_argument("--search-profile")
    eval_parser.add_argument("--date", help="Run date used for the backfill lookback window.")
    eval_parser.add_argument("--lookback-years", type=int, default=DEFAULT_BACKFILL_LOOKBACK_YEARS)
    eval_parser.add_argument("--unseen-only", action="store_true", help="Only print candidates absent from the local state database.")
    eval_parser.add_argument(
        "--unarchived-only",
        action="store_true",
        help="Only print candidates without an archive path, including prior failed state records.",
    )
    eval_parser.add_argument("--state", default="state/articles.sqlite")
    eval_parser.add_argument("--dry-run", action="store_true", help="Alias for evaluate compatibility.")
    eval_parser.set_defaults(func=evaluate)

    audit_parser = sub.add_parser("audit", help="Fetch candidates and write a source health CSV without archiving.")
    audit_parser.add_argument("--batch", type=int, default=1)
    audit_parser.add_argument("--institution")
    audit_parser.add_argument("--limit", type=int, default=5)
    audit_parser.add_argument("--date")
    audit_parser.add_argument("--no-details", action="store_true")
    audit_parser.add_argument("--include-term", dest="include_terms", action="append", default=[])
    audit_parser.add_argument("--search-profile")
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
    daily.add_argument("--lookback-days", type=int, default=DEFAULT_DAILY_LOOKBACK_DAYS)
    daily.add_argument("--brief-cadence", choices=["daily", "weekly"], default="daily")
    daily.add_argument("--include-term", dest="include_terms", action="append", default=[])
    daily.add_argument("--search-profile", default=DEFAULT_EXPANDED_SEARCH_PROFILE)
    daily.add_argument("--archive-root", default="archive")
    daily.add_argument("--brief-root", default="briefs")
    daily.add_argument("--state", default="state/articles.sqlite")
    daily.add_argument("--kb-root", default=str(Path(r"C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库")))
    daily.set_defaults(func=run_daily)

    weekly = sub.add_parser("run-weekly", help="Run weekly fetch, archive, brief, and KB index update.")
    weekly.add_argument("--batch", type=int, default=1)
    weekly.add_argument("--institution")
    weekly.add_argument("--limit", type=int, default=30)
    weekly.add_argument("--date")
    weekly.add_argument("--refresh", action="store_true")
    weekly.add_argument("--skip-kb", action="store_true")
    weekly.add_argument("--min-priority", choices=sorted(PRIORITY_ORDER), default="P3")
    weekly.add_argument("--write-limit", type=int, default=0, help="Maximum number of new allowed records to write. 0 means unlimited.")
    weekly.add_argument("--lookback-days", type=int, default=DEFAULT_WEEKLY_LOOKBACK_DAYS)
    weekly.add_argument("--include-term", dest="include_terms", action="append", default=[])
    weekly.add_argument("--search-profile", default=DEFAULT_EXPANDED_SEARCH_PROFILE)
    weekly.add_argument("--archive-root", default="archive")
    weekly.add_argument("--brief-root", default="briefs")
    weekly.add_argument("--state", default="state/articles.sqlite")
    weekly.add_argument("--kb-root", default=str(Path(r"C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库")))
    weekly.add_argument("--brief-cadence", choices=["weekly"], default="weekly")
    weekly.set_defaults(func=run_weekly)

    comic_prepare = sub.add_parser(
        "prepare-weekly-comics",
        help="Create Codex comic prompt files for weekly P0/P1 topic pages without fetching new records.",
    )
    comic_prepare.add_argument("--date")
    comic_prepare.add_argument("--lookback-days", type=int, default=DEFAULT_WEEKLY_LOOKBACK_DAYS)
    comic_prepare.add_argument("--archive-root", default="archive")
    comic_prepare.add_argument("--comic-root", default="comic")
    comic_prepare.set_defaults(func=prepare_weekly_comics)

    weekly_render = sub.add_parser(
        "render-weekly-brief",
        help="Rebuild the weekly reader brief from local archive records without fetching new records.",
    )
    weekly_render.add_argument("--date")
    weekly_render.add_argument("--lookback-days", type=int, default=DEFAULT_WEEKLY_LOOKBACK_DAYS)
    weekly_render.add_argument("--archive-root", default="archive")
    weekly_render.add_argument("--brief-root", default="briefs")
    weekly_render.set_defaults(func=render_weekly_brief)

    comic_check = sub.add_parser(
        "check-weekly-comics",
        help="Check that weekly Codex comic assets are embedded in Markdown, HTML, and PDF outputs.",
    )
    comic_check.add_argument("--date")
    comic_check.add_argument("--lookback-days", type=int, default=DEFAULT_WEEKLY_LOOKBACK_DAYS)
    comic_check.add_argument("--archive-root", default="archive")
    comic_check.add_argument("--brief-root", default="briefs")
    comic_check.add_argument("--comic-root", default="comic")
    comic_check.set_defaults(func=check_weekly_comics)

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
    backfill_parser.add_argument("--search-profile", default=DEFAULT_EXPANDED_SEARCH_PROFILE)
    backfill_parser.add_argument("--lookback-years", type=int, default=DEFAULT_BACKFILL_LOOKBACK_YEARS)
    backfill_parser.add_argument("--brief-cadence", choices=["daily", "weekly"], default="daily")
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
