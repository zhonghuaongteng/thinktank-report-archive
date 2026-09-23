from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from .models import ArticleCandidate, Institution
from .interests import ResearchInterest, match_research_interests


AUDIT_FIELDS = [
    "机构slug",
    "机构",
    "来源分组",
    "候选状态",
    "候选数",
    "P0/P1数",
    "缺日期数",
    "缺摘要数",
    "缺作者数",
    "PDF线索数",
    "PDF可访问数",
    "详情成功数",
    "详情失败数",
    "近7日候选数",
    "近7日P0/P1数",
    "近7日可入选数",
]


def _within_window(value: str, run_date: date, lookback_days: int) -> bool:
    try:
        published = date.fromisoformat((value or "")[:10])
    except ValueError:
        return False
    return run_date - timedelta(days=max(1, lookback_days) - 1) <= published <= run_date


def audit_rows(
    candidates: list[ArticleCandidate],
    run_date: str | None = None,
    lookback_days: int = 7,
    institutions: list[Institution] | None = None,
) -> list[dict[str, str]]:
    current = date.fromisoformat(run_date) if run_date else date.today()
    grouped: dict[str, list[ArticleCandidate]] = defaultdict(list)
    for item in candidates:
        grouped[item.institution_slug].append(item)
    configured = {item.slug: item for item in institutions or []}
    for slug in configured:
        grouped.setdefault(slug, [])

    rows: list[dict[str, str]] = []
    for slug in sorted(grouped):
        items = grouped[slug]
        recent = [item for item in items if _within_window(item.published_date, current, lookback_days)]
        rows.append(
            {
                "机构slug": slug,
                "机构": configured[slug].name if slug in configured else items[0].institution_name,
                "来源分组": configured[slug].source_group if slug in configured else items[0].source_group,
                "候选状态": "有候选" if items else "零候选（需核验入口，不等于无发布）",
                "候选数": str(len(items)),
                "P0/P1数": str(sum(1 for item in items if item.priority in {"P0", "P1"})),
                "缺日期数": str(sum(1 for item in items if not item.published_date)),
                "缺摘要数": str(sum(1 for item in items if not item.summary and not item.chinese_summary)),
                "缺作者数": str(sum(1 for item in items if not item.authors)),
                "PDF线索数": str(sum(1 for item in items if item.pdf_url)),
                "PDF可访问数": str(sum(1 for item in items if item.pdf_status.startswith("200"))),
                "详情成功数": str(sum(1 for item in items if item.fetch_status == "detail_ok")),
                "详情失败数": str(sum(1 for item in items if item.fetch_status.startswith("detail_error"))),
                "近7日候选数": str(len(recent)),
                "近7日P0/P1数": str(sum(1 for item in recent if item.priority in {"P0", "P1"})),
                "近7日可入选数": str(
                    sum(
                        1
                        for item in recent
                        if item.priority in {"P0", "P1"}
                        and item.fetch_status == "detail_ok"
                    )
                ),
            }
        )
    return rows


def write_audit_report(
    path: str | Path,
    candidates: list[ArticleCandidate],
    run_date: str | None = None,
    lookback_days: int = 7,
    institutions: list[Institution] | None = None,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows(candidates, run_date=run_date, lookback_days=lookback_days, institutions=institutions))
    return path


def write_editorial_review_queue(
    path: str | Path, candidates: list[ArticleCandidate], run_date: str,
    lookback_days: int = 7, interests: list[ResearchInterest] | None = None,
) -> Path:
    """Keep dated and date-unverified candidates from every source before filters; never archive."""
    current = date.fromisoformat(run_date)
    fields = ["机构slug", "标题", "URL", "发布日期", "原始优先级", "原始得分", "详情状态", "公开摘要",
              "发现线索", "研究关注层级", "研究关注主题", "命中检索词", "复核状态", "采纳理由及原文定位"]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in candidates:
            matches = match_research_interests(item, interests or [])
            broad_source = item.source_group in {"innovation_economy", "enterprise_research"}
            try:
                date.fromisoformat((item.published_date or "")[:10])
                precise_date = True
            except ValueError:
                precise_date = False
            if precise_date and not _within_window(item.published_date, current, lookback_days):
                continue
            writer.writerow(dict(zip(fields, [item.institution_slug, item.title, item.url, item.published_date,
                item.priority, item.score, item.fetch_status, item.summary[:800],
                "；".join((["经济与企业来源"] if broad_source else []) + (["研究关注词待复核"] if matches else ["开放发现：未命中现有关注词"])),
                "；".join(dict.fromkeys(interest.level for interest, _ in matches)),
                "；".join(interest.name for interest, _ in matches),
                "；".join(dict.fromkeys(alias for _, hits in matches for alias in hits)),
                "待原文复核" if precise_date else "待核首次发布日期", ""])))
    return path
