from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


WINDOWS = (
    ("W1", 2016, 2018),
    ("W2", 2019, 2021),
    ("W3", 2022, 2026),
)


@dataclass(frozen=True)
class ArchiveRecord:
    institution: str
    slug: str
    published_date: str
    year: int
    content_type: str
    completeness: str
    priority: str
    source_url: str
    path: str


def parse_scalar_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        values[key] = value.strip().strip("\"").strip("'")
    return values


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    values: dict[str, str] = {}
    for line in parts[1].splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
        if match:
            key, value = match.groups()
            values[key] = value.strip().strip("\"").strip("'")
    return values


def load_archive(repo: Path) -> list[ArchiveRecord]:
    records: list[ArchiveRecord] = []
    for path in sorted((repo / "archive").rglob("*.md")):
        meta = parse_frontmatter(path)
        published = meta.get("published_date", "")
        match = re.match(r"^(\d{4})", published)
        if not match:
            continue
        records.append(
            ArchiveRecord(
                institution=meta.get("institution", ""),
                slug=meta.get("institution_slug", path.parts[-3]),
                published_date=published,
                year=int(match.group(1)),
                content_type=meta.get("content_type", ""),
                completeness=meta.get("source_completeness", ""),
                priority=meta.get("priority", ""),
                source_url=meta.get("source_url", ""),
                path=str(path),
            )
        )
    return records


def window_for_year(year: int) -> str:
    for label, start, end in WINDOWS:
        if start <= year <= end:
            return label
    return "OUT"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the local baseline for the 2016-2026 think-tank viewpoint study.")
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()

    repo = args.repo.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    configs: list[dict[str, str]] = []
    for path in sorted((repo / "config" / "institutions").glob("*.yaml")):
        item = parse_scalar_yaml(path)
        item["config_path"] = str(path)
        configs.append(item)

    archive = load_archive(repo)
    by_slug: dict[str, list[ArchiveRecord]] = defaultdict(list)
    for record in archive:
        by_slug[record.slug].append(record)

    candidate_rows: list[dict[str, object]] = []
    coverage_rows: list[dict[str, object]] = []
    for item in configs:
        slug = item.get("slug", "")
        records = by_slug.get(slug, [])
        years = sorted({record.year for record in records})
        counts = Counter(window_for_year(record.year) for record in records)
        candidate_rows.append(
            {
                "机构ID": slug,
                "机构英文名": item.get("name", ""),
                "机构中文名": item.get("chinese_name", ""),
                "国家或地区": item.get("country_region", ""),
                "配置机构类型": item.get("institution_type", ""),
                "来源组": item.get("source_group", ""),
                "当前优先级": item.get("priority", ""),
                "本地归档数": len(records),
                "本地最早年份": min(years) if years else "",
                "本地最晚年份": max(years) if years else "",
                "成立年份": "待核验",
                "科技政策业务起始年": "待核验",
                "官网存档最早年份": "待核验",
                "Wayback最早年份": "待核验",
                "主要出版语言": "待核验",
                "研究分层": "待筛选",
                "备注": item.get("notes", ""),
            }
        )
        coverage_rows.append(
            {
                "机构ID": slug,
                "机构英文名": item.get("name", ""),
                "W1_2016_2018": counts.get("W1", 0),
                "W2_2019_2021": counts.get("W2", 0),
                "W3_2022_2026": counts.get("W3", 0),
                "窗覆盖数": sum(1 for label in ("W1", "W2", "W3") if counts.get(label, 0)),
                "本地最早年份": min(years) if years else "",
                "缺口判断": "；".join(
                    label for label in ("W1", "W2", "W3") if counts.get(label, 0) == 0
                ) or "本地三窗均有记录",
            }
        )

    write_csv(
        out / "02_机构候选池.csv",
        list(candidate_rows[0].keys()),
        candidate_rows,
    )
    write_csv(
        out / "06_时间覆盖与缺口矩阵.csv",
        list(coverage_rows[0].keys()),
        coverage_rows,
    )

    audit_rows = [
        {
            "机构ID": slug,
            "归档数": len(records),
            "W1_2016_2018": sum(record.year <= 2018 for record in records),
            "W2_2019_2021": sum(2019 <= record.year <= 2021 for record in records),
            "W3_2022_2026": sum(record.year >= 2022 for record in records),
            "全文数": sum(record.completeness == "full_text" for record in records),
            "摘要数": sum(record.completeness == "summary_only" for record in records),
            "最早日期": min((record.published_date for record in records), default=""),
            "最晚日期": max((record.published_date for record in records), default=""),
        }
        for slug, records in sorted(by_slug.items(), key=lambda pair: (-len(pair[1]), pair[0]))
    ]
    write_csv(out / "04_既有资料覆盖审计.csv", list(audit_rows[0].keys()), audit_rows)

    years = Counter(record.year for record in archive)
    pre_2022 = sum(count for year, count in years.items() if year < 2022)
    markdown = [
        "# 既有资料覆盖审计",
        "",
        f"数据截止：{args.as_of}。本审计只读取本地配置与归档，未把搜索摘要视为研究证据。",
        "",
        "## 基线判断",
        "",
        f"- 机构配置：{len(configs)}家。",
        f"- 本地归档：{len(archive)}篇，覆盖{len(by_slug)}家机构。",
        f"- 2016—2021年归档：{pre_2022}篇；2022—2026年归档：{len(archive) - pre_2022}篇。",
        f"- 2026年归档：{years.get(2026, 0)}篇，占{years.get(2026, 0) / len(archive):.1%}。",
        "- 既有库可用于近期议题发现，无法单独支持近十年机构内观点比较。",
        "",
        "## 年度分布",
        "",
        "| 年份 | 归档数 |",
        "|---:|---:|",
    ]
    markdown.extend(f"| {year} | {years[year]} |" for year in sorted(years))
    markdown.extend(
        [
            "",
            "## 采集优先级",
            "",
            "1. 先补W1、W2的同系列旗舰报告和正式研究报告。",
            "2. 先形成元数据总目录，再对变化候选做页码级深读。",
            "3. 2022—2026年仅补能够与早期报告构成同题比较的锚点，不扩大短篇动态。",
            "4. 新设机构只进入机构群体构成变化轨道，不作为在位机构转向证据。",
            "",
            "机构明细见 `04_既有资料覆盖审计.csv`，缺窗见 `06_时间覆盖与缺口矩阵.csv`。",
        ]
    )
    (out / "04_既有资料覆盖审计.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
