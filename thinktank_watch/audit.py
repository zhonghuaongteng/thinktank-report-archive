from __future__ import annotations

import csv
from collections import defaultdict
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
]


def audit_rows(candidates: list[ArticleCandidate]) -> list[dict[str, str]]:
    grouped: dict[str, list[ArticleCandidate]] = defaultdict(list)
    for item in candidates:
        grouped[item.institution_slug].append(item)

    rows: list[dict[str, str]] = []
    for slug in sorted(grouped):
        items = grouped[slug]
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
            }
        )
    return rows


def write_audit_report(path: str | Path, candidates: list[ArticleCandidate]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows(candidates))
    return path
