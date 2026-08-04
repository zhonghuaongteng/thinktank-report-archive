from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from .models import ArticleCandidate


AUDIT_FIELDS = [
    "机构slug",
    "机构",
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
) -> list[dict[str, str]]:
    current = date.fromisoformat(run_date) if run_date else date.today()
    grouped: dict[str, list[ArticleCandidate]] = defaultdict(list)
    for item in candidates:
        grouped[item.institution_slug].append(item)

    rows: list[dict[str, str]] = []
    for slug in sorted(grouped):
        items = grouped[slug]
        recent = [item for item in items if _within_window(item.published_date, current, lookback_days)]
        rows.append(
            {
                "机构slug": slug,
                "机构": items[0].institution_name,
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
                        and not item.fetch_status.startswith("detail_error")
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
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows(candidates, run_date=run_date, lookback_days=lookback_days))
    return path
