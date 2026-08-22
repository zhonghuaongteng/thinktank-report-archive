from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SERIES = {
    "1815-1965": "OECD Science, Technology and Industry Working Papers",
    "2307-4957": "OECD Science, Technology and Industry Policy Papers",
    "2071-6826": "OECD Digital Economy Papers",
    "2518-6167": "OECD Science, Technology and Innovation Outlook",
}
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "DOI", "ISSN", "系列", "发布日期", "报告名称", "作者",
    "科学技术创新主题", "中国关联", "DOI入口", "OECD落地页", "登记机构", "资料层级",
    "全文策略", "源文件SHA256", "采集日期",
]

THEME_RULES = (
    ("科学体系与基础研究", re.compile(r"science|scientific|research|r&d|r & d|fundamental|infrastructure|laborator|bibliometric|patent", re.I)),
    ("技术创新与关键技术", re.compile(r"technolog|artificial intelligence|\bai\b|digital|semiconductor|quantum|biotech|robot|space|data|internet|ict", re.I)),
    ("创新政策与研发治理", re.compile(r"innovation|policy|governance|funding|indicator|measurement|foresight|mission|evaluation|regulat", re.I)),
    ("人才大学与科研组织", re.compile(r"talent|skill|workforce|university|researcher|scientist|doctoral|education|career|mobility", re.I)),
    ("产业创新转化与区域生态", re.compile(r"firm|business|industry|industrial|manufactur|startup|entrepreneur|commerciali[sz]|cluster|regional|productivity|venture", re.I)),
    ("国际合作开放科学与比较", re.compile(r"international|global|cross-country|comparative|collaboration|co-operation|cooperation|open science|multinational", re.I)),
)
CHINA_RE = re.compile(r"china|chinese|\bprc\b|people['’]s republic of china|中国|中國", re.I)
SECURITY_RE = re.compile(r"security|supply chain|resilien|export control|strategic autonomy|cyber|defen[cs]e", re.I)


@dataclass(frozen=True)
class OecdRecord:
    report_id: str
    doi: str
    issn: str
    series: str
    published: str
    title: str
    authors: str
    doi_url: str
    official_url: str
    publisher: str
    themes: tuple[str, ...]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip().replace("��", "–")


def canonical_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(value).lower())


def stable_report_id(doi: str) -> str:
    suffix = doi.lower().removeprefix("10.1787/")
    safe = re.sub(r"[^a-z0-9]+", "-", suffix).strip("-").upper()
    return f"C-OECD-DOI-{safe}"


def published_date(item: dict) -> str:
    for key in ("published", "published-online", "published-print", "issued"):
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            values = list(parts[0]) + [1, 1]
            return f"{int(values[0]):04d}-{int(values[1]):02d}-{int(values[2]):02d}"
    return ""


def author_names(item: dict) -> str:
    names = []
    for author in item.get("author", []):
        name = clean_text(" ".join(part for part in (author.get("given", ""), author.get("family", "")) if part))
        if name:
            names.append(name)
    return "；".join(names)


def classify_themes(title: str) -> list[str]:
    themes = [label for label, pattern in THEME_RULES if pattern.search(title)]
    if CHINA_RE.search(title):
        themes.append("中国科技横向维度")
    if SECURITY_RE.search(title):
        themes.append("安全供应链与治理边界（次级）")
    return themes or ["科学技术创新综合目录"]


def parse_crossref_item(item: dict, issn: str) -> OecdRecord:
    doi = str(item.get("DOI", "")).lower()
    title = clean_text((item.get("title") or [""])[0])
    official = item.get("resource", {}).get("primary", {}).get("URL", "")
    return OecdRecord(
        report_id=stable_report_id(doi),
        doi=doi,
        issn=issn,
        series=SERIES[issn],
        published=published_date(item),
        title=title,
        authors=author_names(item),
        doi_url=str(item.get("URL", "")) or f"https://doi.org/{doi}",
        official_url=str(official) or str(item.get("URL", "")) or f"https://doi.org/{doi}",
        publisher=clean_text(str(item.get("publisher", ""))),
        themes=tuple(classify_themes(title)),
    )


def load_records(paths: list[Path]) -> tuple[list[OecdRecord], dict[str, str]]:
    unique: dict[str, OecdRecord] = {}
    hashes: dict[str, str] = {}
    for path in paths:
        match = re.search(r"(\d{4}-\d{4})", path.name)
        if not match or match.group(1) not in SERIES:
            raise ValueError(f"cannot determine OECD series ISSN from {path.name}")
        issn = match.group(1)
        data = json.loads(path.read_text(encoding="utf-8"))
        hashes[issn] = hashlib.sha256(path.read_bytes()).hexdigest()
        for item in data.get("message", {}).get("items", []):
            record = parse_crossref_item(item, issn)
            if not record.doi or not ("2016-01-01" <= record.published <= "2026-08-22"):
                continue
            if record.publisher and "OECD" not in record.publisher and "Co-Operation and Development" not in record.publisher:
                continue
            unique.setdefault(record.doi, record)
    return sorted(unique.values(), key=lambda row: (row.published, row.doi)), hashes


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--inputs", required=True, nargs="+", type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    records, source_hashes = load_records(args.inputs)
    if len(records) != 445:
        raise ValueError(f"expected 445 DOI records; found {len(records)}")

    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    existing_by_id = {row["报告ID"]: row for row in catalog}
    existing_by_title_year: dict[tuple[str, str], str] = {}
    for row in catalog:
        key = (canonical_title(row.get("报告名称", "")), row.get("发布日期", "")[:4])
        if key[0]:
            existing_by_title_year.setdefault(key, row["报告ID"])

    ledger_rows: list[dict[str, str]] = []
    added = linked = 0
    for record in records:
        key = (canonical_title(record.title), record.published[:4])
        unified_id = existing_by_title_year.get(key) or record.report_id
        if unified_id in existing_by_id:
            linked += 1
        else:
            themes = "；".join(record.themes)
            china = "中国科技横向维度" in record.themes
            row = {
                "报告ID": record.report_id,
                "机构ID": "oecd-sti",
                "机构英文名": "OECD",
                "国家或地区": "国际组织",
                "发布日期": record.published,
                "观察窗": "W1" if int(record.published[:4]) <= 2018 else "W2" if int(record.published[:4]) <= 2021 else "W3",
                "报告名称": record.title,
                "报告类型": record.series,
                "原文链接": record.official_url,
                "本地路径": "",
                "正文完整度": "DOI注册元数据与OECD落地页",
                "优先级": "P1-China-tech-candidate" if china else "P2-light-catalog",
                "示踪问题": themes,
                "机构观点等级": "OECD正式系列成果，正文待核",
                "样本角色": "OECD STI正式系列轻量目录",
                "编码状态": "目录待筛选",
                "预期用途": "科学体系、技术创新、研发治理、人才科研组织、产业转化、开放合作及中国科技专题检索",
                "本地原始资产路径": "",
                "原始资产状态": "DOI与OECD落地页已保存；未下载全文",
            }
            catalog.append(row)
            existing_by_id[record.report_id] = row
            existing_by_title_year[key] = record.report_id
            added += 1
        ledger_rows.append({
            "报告ID": record.report_id,
            "统一目录报告ID": unified_id,
            "DOI": record.doi,
            "ISSN": record.issn,
            "系列": record.series,
            "发布日期": record.published,
            "报告名称": record.title,
            "作者": record.authors,
            "科学技术创新主题": "；".join(record.themes),
            "中国关联": "是" if "中国科技横向维度" in record.themes else "否",
            "DOI入口": record.doi_url,
            "OECD落地页": record.official_url,
            "登记机构": record.publisher,
            "资料层级": "DOI注册元数据与OECD正式系列",
            "全文策略": "不自动下载；由机构—节点—主题覆盖缺口触发",
            "源文件SHA256": source_hashes[record.issn],
            "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "77_OECD_STI正式系列轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    series_counts = {issn: sum(row.issn == issn for row in records) for issn in SERIES}
    years = {year: sum(row.published.startswith(str(year)) for row in records) for year in range(2016, 2027)}
    china_count = sum("中国科技横向维度" in row.themes for row in records)
    lines = [
        "# OECD STI正式系列轻量目录增补结果", "",
        f"- DOI登记记录：{len(records)}项；与既有目录关联{linked}项，新增统一目录{added}项。",
        f"- 中国科技横向关联：{china_count}项；本轮未下载正文。",
        "- 系列分布：" + "；".join(f"{SERIES[key]} {value}项" for key, value in series_counts.items()) + "。",
        "- 年度分布：" + "；".join(f"{year}年{value}项" for year, value in years.items()) + "。", "",
        "## 采集边界", "",
        "纳入2016年1月1日至2026年8月22日四个OECD科技创新正式系列的全部DOI登记记录。系列入口本身限定了科学、技术、创新和数字经济范围，未使用安全关键词做纳入筛选。中国作为横向维度；安全、供应链与治理边界仅保留次级标签。", "",
        "Crossref元数据用于确认DOI、题名、日期、作者、系列和OECD落地页。题名可用于关注方向与系列演变分析；观点、因果判断和政策主张须回查OECD正文。", "",
    ]
    (root / "78_OECD_STI正式系列轻量目录结果.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"records={len(records)} linked={linked} added={added} china={china_count} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
