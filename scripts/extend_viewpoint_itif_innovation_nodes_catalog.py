from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "发布日期", "报告名称", "节点角色", "科学技术创新主题", "中国关联",
    "官方落地页", "官方PDF入口", "资料层级", "全文策略", "采集日期",
]


@dataclass(frozen=True)
class InnovationNodeItem:
    published: str
    title: str
    url: str
    role: str
    themes: tuple[str, ...]
    pdf_url: str = ""


ITEMS = (
    InnovationNodeItem(
        "2022-06-08",
        "The Hamilton Index: Assessing National Performance in the Competition for Advanced Industries",
        "https://itif.org/publications/2022/06/08/the-hamilton-index-assessing-national-performance-in-the-competition-for-advanced-industries/",
        "先进产业创新能力比较基线",
        ("技术创新与关键技术", "创新政策与研发治理", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
    ),
    InnovationNodeItem(
        "2023-01-23",
        "Wake Up, America: China Is Overtaking the United States in Innovation Capacity",
        "https://itif.org/publications/2023/01/23/wake-up-america-china-is-overtaking-the-united-states-in-innovation-capacity/",
        "国家创新能力比较",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
    ),
    InnovationNodeItem(
        "2025-02-20",
        "Understanding and Comparing National Innovation Systems: The U.S., Korea, China, Japan, and Taiwan",
        "https://itif.org/publications/2025/02/20/understanding-comparing-national-innovation-systems-us-korea-china-japan-taiwan/",
        "国家创新体系比较",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
        "https://www2.itif.org/2025-itif-chey-national-innovation-systems.pdf",
    ),
    InnovationNodeItem(
        "2025-09-15",
        "How Reducing Federal R&D Reduces GDP Growth",
        "https://itif.org/publications/2025/09/15/how-reducing-federal-rd-reduces-gdp-growth/",
        "公共R&D投入机制",
        ("科学体系与基础研究", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
        "https://www2.itif.org/2025-reducing-federal-rd.pdf",
    ),
    InnovationNodeItem(
        "2026-05-06",
        "The Hamilton Index, 2026: China’s Dominance in Advanced Industries Is Growing",
        "https://itif.org/publications/2026/05/06/hamilton-index-2026-chinas-dominance-in-advanced-industries-is-growing/",
        "先进产业创新能力更新",
        ("技术创新与关键技术", "创新政策与研发治理", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
    ),
)


def stable_report_id(url: str) -> str:
    parts = [part for part in urlsplit(url).path.strip("/").split("/") if part]
    year = parts[1]
    slug = parts[-1]
    return "C-ITIF-" + year + "-" + re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-").upper()


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


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
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    existing = {row["报告ID"]: row for row in catalog}
    ledger_rows: list[dict[str, str]] = []
    added = 0
    for item in ITEMS:
        report_id = stable_report_id(item.url)
        themes = "；".join(item.themes)
        row = {
            "报告ID": report_id,
            "机构ID": "itif",
            "机构英文名": "Information Technology and Innovation Foundation",
            "国家或地区": "美国",
            "发布日期": item.published,
            "观察窗": observation_window(item.published),
            "报告名称": item.title,
            "报告类型": f"ITIF科学技术创新节点/{item.role}",
            "原文链接": item.url,
            "本地路径": "",
            "正文完整度": "官方落地页与PDF入口元数据" if item.pdf_url else "官方落地页元数据",
            "优先级": "P0-China-innovation-candidate",
            "示踪问题": themes,
            "机构观点等级": "作者/项目正式研究，正文待核",
            "样本角色": "ITIF科学技术创新节点轻量目录",
            "编码状态": "目录待筛选",
            "预期用途": "中国与主要经济体科学能力、国家创新体系、公共R&D及先进产业创新能力比较",
            "本地原始资产路径": "",
            "原始资产状态": "官方入口已保存；未下载全文",
        }
        if report_id in existing:
            existing[report_id].update(row)
        else:
            catalog.append(row)
            existing[report_id] = row
            added += 1
        ledger_rows.append({
            "报告ID": report_id,
            "发布日期": item.published,
            "报告名称": item.title,
            "节点角色": item.role,
            "科学技术创新主题": themes,
            "中国关联": "是",
            "官方落地页": item.url,
            "官方PDF入口": item.pdf_url,
            "资料层级": "ITIF正式报告轻量目录",
            "全文策略": "不自动下载；由科学技术创新主轴缺口与纵向比较价值触发",
            "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "82_ITIF科学技术创新节点轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    result = f"""# ITIF科学技术创新节点轻量目录增补结果

- 正式报告：{len(ITEMS)}项；新增统一总目录记录：{added}项。
- 节点分布：2022年1项、2023年1项、2025年2项、2026年1项。
- 主题集中于国家创新体系、公共R&D投入、先进产业创新能力及中国比较；本轮未下载正文。

## 采集边界

本批只选择能够补充科学技术创新时间节点的正式报告。安全和国家竞争叙述可能出现在正文中，但不构成纳入依据；目录标引落在科研投入、创新体系、技术能力、人才组织、产业转化和跨国比较。题名与官方落地页用于目录定位，机构观点仍须在精选全文阶段回查原文。
"""
    (root / "83_ITIF科学技术创新节点轻量目录结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(ITEMS)} added={added} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
