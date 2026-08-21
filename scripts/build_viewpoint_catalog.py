from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


FORMAL_TYPES = {"report", "rand_report", "paper", "brief", "official_strategy", "research_report"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    result: dict[str, str] = {}
    for line in parts[1].splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
        if match:
            key, value = match.groups()
            result[key] = value.strip().strip("\"").strip("'")
    return result


def short_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:10].upper()}"


def window(date_value: str) -> str:
    match = re.match(r"^(\d{4})", date_value)
    if not match:
        return ""
    year = int(match.group(1))
    if 2016 <= year <= 2018:
        return "W1"
    if 2019 <= year <= 2021:
        return "W2"
    if 2022 <= year <= 2026:
        return "W3"
    return "OUT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    research = args.research.resolve()

    rows: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for seed in read_csv(research / "05_官方锚点种子.csv"):
        url = seed["官方页面或PDF"]
        seen_urls.add(url)
        rows.append(
            {
                "报告ID": seed["种子ID"],
                "机构ID": seed["机构ID"],
                "机构英文名": seed["机构英文名"],
                "国家或地区": seed["国家或地区"],
                "发布日期": seed["日期"],
                "观察窗": seed["观察窗"],
                "报告名称": seed["报告名称"],
                "报告类型": seed["报告类型"],
                "原文链接": url,
                "本地路径": "",
                "正文完整度": seed["获取状态"],
                "优先级": "P0-anchor",
                "示踪问题": seed["示踪问题"],
                "机构观点等级": seed["机构观点等级"],
                "样本角色": "官方锚点",
                "编码状态": "待编码",
                "预期用途": seed["预期用途"],
            }
        )

    for path in sorted((repo / "archive").rglob("*.md")):
        meta = parse_frontmatter(path)
        if meta.get("content_type", "") not in FORMAL_TYPES:
            continue
        date_value = meta.get("published_date", "")
        if window(date_value) == "OUT" or not date_value:
            continue
        url = meta.get("source_url", "")
        if url and url in seen_urls:
            continue
        rows.append(
            {
                "报告ID": short_id("L", str(path)),
                "机构ID": meta.get("institution_slug", ""),
                "机构英文名": meta.get("institution", ""),
                "国家或地区": "待回填",
                "发布日期": date_value,
                "观察窗": window(date_value),
                "报告名称": meta.get("english_title", ""),
                "报告类型": meta.get("content_type", ""),
                "原文链接": url,
                "本地路径": str(path),
                "正文完整度": meta.get("source_completeness", ""),
                "优先级": meta.get("priority", ""),
                "示踪问题": "待编码",
                "机构观点等级": "待编码",
                "样本角色": "本地近期候选",
                "编码状态": "待筛选",
                "预期用途": "W3近期观点与反证候选",
            }
        )

    fields = list(rows[0].keys())
    output = research / "05_报告总目录.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
