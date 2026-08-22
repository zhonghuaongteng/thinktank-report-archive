from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

try:
    from scripts.build_viewpoint_node_theme_gap_matrix import CHINA_PATTERN, STRATEGIC_THEMES
except ModuleNotFoundError:  # direct script execution
    from build_viewpoint_node_theme_gap_matrix import CHINA_PATTERN, STRATEGIC_THEMES


SOURCE_URL = "https://www.isi.fraunhofer.de/en/competence-center/innovations-wissensoekonomie/publikationen/innovation-systems-policy-analysis.html"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "系列编号", "发布日期", "日期精度", "报告名称", "作者",
    "科学技术创新主题", "中国关联", "官方系列页", "官方PDF入口", "资料层级", "全文策略",
    "源文件SHA256", "采集日期",
]


@dataclass(frozen=True)
class DiscussionPaper:
    report_id: str
    number: int
    year: int
    title: str
    authors: str
    pdf_url: str
    themes: tuple[str, ...]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def canonical_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(value).lower())


def canonical_url(value: str) -> str:
    return value.strip().lower().replace("http://", "https://").rstrip("/")


def theme_labels(title: str) -> tuple[str, ...]:
    matched = [name.split("_", 1)[1] for name, pattern in STRATEGIC_THEMES.items() if pattern.search(title)]
    if re.search(r"\bsecurity\b|supply chain|export control|research security", title, re.I):
        matched.append("安全供应链与治理边界")
    if not matched:
        matched = ["创新政策与研发治理"]
    if CHINA_PATTERN.search(title):
        matched.append("中国科技横向维度")
    return tuple(dict.fromkeys(matched))


def extract_authors(paragraph, anchor, title: str) -> str:
    text = clean_text(paragraph.get_text(" ", strip=True))
    before_title = text.split(title, 1)[0] if title in text else text
    before_title = re.sub(r"^(?:No\.?|Nr\.?)\s*\d+\s*", "", before_title, flags=re.I)
    return before_title.strip(" -")


def parse_official_page(source_html: str) -> list[DiscussionPaper]:
    soup = BeautifulSoup(source_html, "html.parser")
    records: dict[int, DiscussionPaper] = {}
    for anchor in soup.select('a[href*="discussionpaper_"][href$=".pdf"]'):
        href = str(anchor.get("href", ""))
        match = re.search(r"discussionpaper_(\d+)_([0-9]{4})\.pdf", href, re.I)
        if not match:
            continue
        number, year = int(match.group(1)), int(match.group(2))
        if not 2016 <= year <= 2026:
            continue
        title = clean_text(anchor.get_text(" ", strip=True))
        paragraph = anchor.find_parent("p")
        authors = extract_authors(paragraph, anchor, title) if paragraph else ""
        records.setdefault(number, DiscussionPaper(
            report_id=f"C-FRAUNHOFER-ISI-DP-{number}",
            number=number,
            year=year,
            title=title,
            authors=authors,
            pdf_url=urljoin(SOURCE_URL, href),
            themes=theme_labels(title),
        ))
    return sorted(records.values(), key=lambda row: (row.year, row.number))


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
    parser.add_argument("--input-html", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    source_bytes = args.input_html.read_bytes()
    records = parse_official_page(source_bytes.decode("utf-8"))
    if len(records) != 47:
        raise ValueError(f"expected 47 official discussion papers for 2016-2026; found {len(records)}")

    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    existing_by_id = {row["报告ID"]: row for row in catalog}
    existing_by_url = {canonical_url(row.get("原文链接", "")): row["报告ID"] for row in catalog if row.get("原文链接")}
    existing_by_title_year = {
        (canonical_title(row.get("报告名称", "")), row.get("发布日期", "")[:4]): row["报告ID"]
        for row in catalog if row.get("报告名称")
    }
    ledger_rows: list[dict[str, str]] = []
    added = linked = 0
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    for record in records:
        title_key = (canonical_title(record.title), str(record.year))
        unified_id = existing_by_url.get(canonical_url(record.pdf_url)) or existing_by_title_year.get(title_key) or record.report_id
        themes = "；".join(record.themes)
        china = "中国科技横向维度" in record.themes
        if unified_id in existing_by_id:
            linked += 1
        else:
            row = {
                "报告ID": record.report_id,
                "机构ID": "fraunhofer-isi",
                "机构英文名": "Fraunhofer Institute for Systems and Innovation Research ISI",
                "国家或地区": "德国",
                "发布日期": f"{record.year:04d}-01-01",
                "观察窗": "W1" if record.year <= 2018 else "W2" if record.year <= 2021 else "W3",
                "报告名称": record.title,
                "报告类型": "Fraunhofer ISI Innovation Systems and Policy Analysis Discussion Paper",
                "原文链接": record.pdf_url,
                "本地路径": "",
                "正文完整度": "官方系列元数据与PDF入口；日期精度为年",
                "优先级": "P1-China-tech-candidate" if china else "P2-light-catalog",
                "示踪问题": themes,
                "机构观点等级": "机构正式讨论论文，正文待核",
                "样本角色": "Fraunhofer ISI创新系统与政策分析连续系列轻量目录",
                "编码状态": "目录待筛选",
                "预期用途": "科学体系、创新政策、研发治理、技术转化、德国及中国创新系统比较",
                "本地原始资产路径": "",
                "原始资产状态": "官方PDF入口已保存；未下载全文；发布日期仅精确到年",
            }
            catalog.append(row)
            existing_by_id[record.report_id] = row
            existing_by_url[canonical_url(record.pdf_url)] = record.report_id
            existing_by_title_year[title_key] = record.report_id
            added += 1
        ledger_rows.append({
            "报告ID": record.report_id,
            "统一目录报告ID": unified_id,
            "系列编号": str(record.number),
            "发布日期": f"{record.year:04d}-01-01",
            "日期精度": "年；统一目录以1月1日作排序占位，不代表实际出版日",
            "报告名称": record.title,
            "作者": record.authors,
            "科学技术创新主题": themes,
            "中国关联": "是" if china else "否",
            "官方系列页": SOURCE_URL,
            "官方PDF入口": record.pdf_url,
            "资料层级": "Fraunhofer ISI官方连续讨论论文系列",
            "全文策略": "不自动下载；由科学技术创新主轴缺口与纵向比较价值触发",
            "源文件SHA256": source_hash,
            "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "84_Fraunhofer_ISI创新系统政策分析轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    year_counts = {year: sum(row.year == year for row in records) for year in range(2016, 2027)}
    china_count = sum("中国科技横向维度" in row.themes for row in records)
    result = f"""# Fraunhofer ISI创新系统与政策分析轻量目录增补结果

- 官方连续讨论论文：{len(records)}项；与既有目录关联{linked}项，新增统一总目录{added}项。
- 年度分布：{'；'.join(f'{year}年{count}项' for year, count in year_counts.items())}。
- 中国科技横向关联：{china_count}项；保存47个官方PDF入口，本轮未下载正文。
- 官方系列页快照SHA256：`{source_hash}`。

## 采集边界

本批完整保留Fraunhofer ISI“Innovation Systems and Policy Analysis”讨论论文系列2016—2026年元数据。该系列本身属于创新系统与创新政策研究，不以安全关键词筛选纳入。安全或技术主权相关题名只保留次级语境标签，不能单独触发全文补取。

官方系列页只提供出版年份。统一总目录以当年1月1日作为排序占位，台账明确记录日期精度，不能将其引用为实际出版日。题名、作者、系列编号和官方PDF入口可用于关注方向与连续序列识别；机构观点和政策主张须回查正文。
"""
    (root / "85_Fraunhofer_ISI创新系统政策分析轻量目录结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(records)} linked={linked} added={added} china={china_count} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
