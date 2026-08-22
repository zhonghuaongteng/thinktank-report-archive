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


REPORT_TYPE = 18
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "WordPress_ID", "发布日期", "报告名称", "官方摘要", "科学技术创新主题",
    "中国关联", "官方落地页", "官方PDF入口", "附件数", "资料层级", "全文策略", "采集日期",
]

THEME_RULES = (
    ("科学体系与基础研究", re.compile(r"science|scientific|research ecosystem|basic research|fundamental research|r&d|research and development", re.I)),
    ("技术创新与关键技术", re.compile(r"artificial intelligence|\bai\b|semiconductor|chip|quantum|biotech|biosecurity|robot|space|satellite|compute|technology|technical|digital", re.I)),
    ("创新政策与研发治理", re.compile(r"innovation|r&d|research and development|funding|policy|foresight|evaluation|standards", re.I)),
    ("人才大学与科研组织", re.compile(r"talent|workforce|university|universities|researcher|scientist|engineer|doctoral|education|laboratory", re.I)),
    ("产业创新转化与区域生态", re.compile(r"commerciali[sz]|startup|industry|industrial|manufactur|technology transfer|regional|cluster|market", re.I)),
    ("国际合作开放科学与比较", re.compile(r"international|global|cooperation|collaboration|open science|allies|comparative|cross-border", re.I)),
)
SECURITY_RE = re.compile(r"security|supply chain|export control|military|defen[cs]e|cyber|governance|regulation", re.I)
CHINA_RE = re.compile(r"china|chinese|beijing|prc|中(?:国|美|欧)", re.I)
PDF_RE = re.compile(r'href=["\'](https://cset\.georgetown\.edu/wp-content/uploads/[^"\']+?\.pdf(?:\?[^"\']*)?)["\']', re.I)


@dataclass(frozen=True)
class LightReport:
    report_id: str
    wp_id: int
    published: str
    title: str
    abstract: str
    landing_url: str
    pdf_entries: tuple[str, ...]
    themes: tuple[str, ...]


def clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def normalize_title(value: str) -> str:
    return clean_html(value).replace("��", "—")


def extract_pdf_entries(rendered: str) -> list[str]:
    return list(dict.fromkeys(html.unescape(url) for url in PDF_RE.findall(rendered or "")))


def classify_science_innovation_themes(title: str, abstract: str) -> list[str]:
    text = f"{title} {abstract}"
    themes = [label for label, pattern in THEME_RULES if pattern.search(text)]
    if CHINA_RE.search(text):
        themes.append("中国科技横向维度")
    if SECURITY_RE.search(text):
        themes.append("安全供应链与治理边界（次级）")
    return themes or ["科技创新综合目录候选"]


def parse_items(items: list[dict]) -> list[LightReport]:
    reports: list[LightReport] = []
    for item in items:
        if REPORT_TYPE not in [int(value) for value in item.get("content_type", [])]:
            continue
        published = str(item.get("date", ""))[:10]
        if not ("2023-01-01" <= published <= "2024-12-31"):
            continue
        wp_id = int(item["id"])
        title = normalize_title(item.get("title", {}).get("rendered", ""))
        abstract = clean_html(item.get("excerpt", {}).get("rendered", ""))
        content = item.get("content", {}).get("rendered", "")
        reports.append(LightReport(
            report_id=f"C-CSET-{wp_id}",
            wp_id=wp_id,
            published=published,
            title=title,
            abstract=abstract,
            landing_url=str(item.get("link", "")),
            pdf_entries=tuple(extract_pdf_entries(content)),
            themes=tuple(classify_science_innovation_themes(title, abstract)),
        ))
    return sorted(reports, key=lambda item: (item.published, item.wp_id))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def stable_source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--input-json", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    items = json.loads(args.input_json.read_text(encoding="utf-8"))
    reports = parse_items(items)
    if len(reports) != 60:
        raise ValueError(f"expected 60 official CSET reports for 2023-2024; found {len(reports)}")

    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    existing = {row["报告ID"]: row for row in catalog}
    ledger_rows: list[dict[str, str]] = []
    added = 0
    for report in reports:
        themes = "；".join(report.themes)
        china = "是" if "中国科技横向维度" in report.themes else "否"
        row = {
            "报告ID": report.report_id,
            "机构ID": "cset",
            "机构英文名": "Center for Security and Emerging Technology",
            "国家或地区": "美国",
            "发布日期": report.published,
            "观察窗": "W3",
            "报告名称": report.title,
            "报告类型": "CSET正式报告轻量目录",
            "原文链接": report.landing_url,
            "本地路径": "",
            "正文完整度": "官方目录元数据与附件入口",
            "优先级": "P1-China-tech-candidate" if china == "是" else "P2-light-catalog",
            "示踪问题": themes,
            "机构观点等级": "作者/项目正式研究，正文待核",
            "样本角色": "CSET 2023—2024正式报告轻量目录",
            "编码状态": "目录待筛选",
            "预期用途": "科学体系、技术创新、研发治理、科研组织、产业转化、开放合作及中国科技专题检索",
            "本地原始资产路径": "",
            "原始资产状态": "官方目录与附件入口已保存；未下载全文",
        }
        if report.report_id in existing:
            existing[report.report_id].update(row)
        else:
            catalog.append(row)
            existing[report.report_id] = row
            added += 1
        ledger_rows.append({
            "报告ID": report.report_id,
            "WordPress_ID": str(report.wp_id),
            "发布日期": report.published,
            "报告名称": report.title,
            "官方摘要": report.abstract,
            "科学技术创新主题": themes,
            "中国关联": china,
            "官方落地页": report.landing_url,
            "官方PDF入口": "；".join(report.pdf_entries),
            "附件数": str(len(report.pdf_entries)),
            "资料层级": "官方正式报告轻量目录",
            "全文策略": "不自动下载；由机构—节点—主题覆盖缺口触发",
            "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "75_CSET_2023-2024正式报告轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    years = {year: sum(row.published.startswith(str(year)) for row in reports) for year in (2023, 2024)}
    china_count = sum("中国科技横向维度" in row.themes for row in reports)
    pdf_entries = sum(len(row.pdf_entries) for row in reports)
    result = f"""# CSET 2023—2024正式报告轻量目录增补结果

- 官方正式报告：{len(reports)}项，其中2023年{years[2023]}项、2024年{years[2024]}项。
- 中国科技横向关联：{china_count}项。
- 保存官方PDF附件入口：{pdf_entries}个；本轮未下载正文。
- 新增统一总目录记录：{added}项；源JSON SHA256：`{stable_source_hash(args.input_json)}`。

## 采集边界

直接保存CSET官方WordPress接口中2023—2024年全部正式报告元数据，不以安全关键词决定是否进入轻量目录。主题标引以科学体系、技术创新、研发治理、人才与科研组织、产业转化和开放合作为主体，中国作为横向维度；安全、供应链与治理边界只保留次级标签。

题名、摘要、落地页和附件入口可以支持关注方向及报告谱系分析。机构观点、因果解释和政策主张须在覆盖矩阵触发后回查正文，不由轻量目录直接推导。
"""
    (root / "76_CSET_2023-2024正式报告轻量目录结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(reports)} added={added} china={china_count} pdf_entries={pdf_entries} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
