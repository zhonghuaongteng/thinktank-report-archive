from __future__ import annotations

import csv
from pathlib import Path

from .models import ArticleCandidate
from .models import Institution


KB_ROOT = Path(r"C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库")
INDEX_RELATIVE = Path("06_数据资产") / "研报_国际智库抓取索引.csv"
INSTITUTION_RELATIVE = Path("06_数据资产") / "研报_国际科技智库机构口径表.csv"


INDEX_FIELDS = [
    "抓取日期",
    "机构",
    "机构类型",
    "优先级",
    "主题标签",
    "中文题名",
    "英文题名",
    "发布日期",
    "原始链接",
    "PDF链接",
    "翻译层级",
    "版权边界",
    "抓取状态",
]
INSTITUTION_FIELDS = [
    "机构slug",
    "机构",
    "中文名",
    "国家地区",
    "机构类型",
    "优先级",
    "接入批次",
    "主页",
    "辅助域名",
    "解析器",
    "版权边界",
    "单次上限",
    "RSS",
    "列表页",
    "主题页",
    "备注",
]


def append_kb_index(
    candidates: list[ArticleCandidate],
    run_date: str,
    kb_root: str | Path = KB_ROOT,
) -> Path:
    path = Path(kb_root) / INDEX_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_urls: set[str] = set()
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                existing_urls.add(row.get("原始链接", ""))

    write_header = not path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INDEX_FIELDS)
        if write_header:
            writer.writeheader()
        for item in candidates:
            if item.url in existing_urls:
                continue
            writer.writerow(
                {
                    "抓取日期": run_date,
                    "机构": item.institution_name,
                    "机构类型": item.institution_type,
                    "优先级": item.priority,
                    "主题标签": "；".join(item.topic_tags),
                    "中文题名": item.chinese_title or item.title,
                    "英文题名": item.title,
                    "发布日期": item.published_date,
                    "原始链接": item.url,
                    "PDF链接": item.pdf_url,
                    "翻译层级": item.translation_level,
                    "版权边界": item.copyright_boundary,
                    "抓取状态": item.fetch_status,
                }
            )
    return path


def write_institution_table(
    institutions: list[Institution],
    kb_root: str | Path = KB_ROOT,
) -> Path:
    path = Path(kb_root) / INSTITUTION_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INSTITUTION_FIELDS)
        writer.writeheader()
        for item in sorted(institutions, key=lambda row: (row.batch, row.slug)):
            writer.writerow(
                {
                    "机构slug": item.slug,
                    "机构": item.name,
                    "中文名": item.chinese_name,
                    "国家地区": item.country_region,
                    "机构类型": item.institution_type,
                    "优先级": item.priority,
                    "接入批次": item.batch,
                    "主页": item.homepage,
                    "辅助域名": "；".join(item.allowed_domains),
                    "解析器": item.parser,
                    "版权边界": item.copyright_boundary,
                    "单次上限": item.run_limit,
                    "RSS": "；".join(item.feeds),
                    "列表页": "；".join(item.list_pages),
                    "主题页": "；".join(item.topic_pages),
                    "备注": item.notes,
                }
            )
    return path
