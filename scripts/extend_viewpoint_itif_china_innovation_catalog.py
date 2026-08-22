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
    "报告ID", "发布日期", "报告名称", "序列角色", "技术领域", "科学技术创新主题", "中国关联",
    "官方落地页", "资料层级", "全文策略", "采集日期",
]


@dataclass(frozen=True)
class SeriesItem:
    published: str
    title: str
    url: str
    domain: str
    role: str = "行业研究"
    includes_talent: bool = False


SERIES = (
    SeriesItem("2024-03-11", "How Innovative Is China in the Robotics Industry?", "https://itif.org/publications/2024/03/11/how-innovative-is-china-in-the-robotics-industry/", "机器人"),
    SeriesItem("2024-04-15", "How Innovative Is China in the Chemicals Industry?", "https://itif.org/publications/2024/04/15/how-innovative-is-china-in-the-chemicals-industry/", "化工与材料"),
    SeriesItem("2024-06-17", "How Innovative Is China in Nuclear Power?", "https://itif.org/publications/2024/06/17/how-innovative-is-china-in-nuclear-power/", "核能"),
    SeriesItem("2024-07-29", "How Innovative Is China in the Electric Vehicle and Battery Industries?", "https://itif.org/publications/2024/07/29/how-innovative-is-china-in-the-electric-vehicle-and-battery-industries/", "电动车与电池"),
    SeriesItem("2024-07-30", "How Innovative Is China in Biotechnology?", "https://itif.org/publications/2024/07/30/how-innovative-is-china-in-biotechnology/", "生物技术"),
    SeriesItem("2024-08-19", "How Innovative Is China in Semiconductors?", "https://itif.org/publications/2024/08/19/how-innovative-is-china-in-semiconductors/", "半导体"),
    SeriesItem("2024-08-26", "How Innovative Is China in AI?", "https://itif.org/publications/2024/08/26/how-innovative-is-china-in-ai/", "人工智能", "行业研究", True),
    SeriesItem("2024-09-09", "How Innovative Is China in Quantum?", "https://itif.org/publications/2024/09/09/how-innovative-is-china-in-quantum/", "量子技术"),
    SeriesItem("2024-09-16", "How Innovative Is China in the Display Industry?", "https://itif.org/publications/2024/09/16/how-innovative-is-china-in-the-display-industry/", "显示技术"),
    SeriesItem("2024-09-16", "China Is Rapidly Becoming a Leading Innovator in Advanced Industries", "https://itif.org/publications/2024/09/16/china-is-rapidly-becoming-a-leading-innovator-in-advanced-industries/", "先进产业综合", "综合报告"),
)


def stable_report_id(url: str) -> str:
    parts = [part for part in urlsplit(url).path.strip("/").split("/") if part]
    year = parts[1]
    slug = parts[-1]
    return "C-ITIF-" + year + "-" + re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-").upper()


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
    for item in SERIES:
        item_themes = [
            "科学体系与基础研究",
            "技术创新与关键技术",
            "创新政策与研发治理",
            "产业创新转化与区域生态",
            "国际合作开放科学与比较",
        ]
        if item.includes_talent:
            item_themes.append("人才大学与科研组织")
        item_themes.append("中国科技横向维度")
        themes = "；".join(item_themes)
        report_id = stable_report_id(item.url)
        row = {
            "报告ID": report_id,
            "机构ID": "itif",
            "机构英文名": "Information Technology and Innovation Foundation",
            "国家或地区": "美国",
            "发布日期": item.published,
            "观察窗": "W3",
            "报告名称": item.title,
            "报告类型": f"ITIF中国创新能力系列/{item.role}",
            "原文链接": item.url,
            "本地路径": "",
            "正文完整度": "官方落地页与系列元数据",
            "优先级": "P0-China-innovation-candidate",
            "示踪问题": themes,
            "机构观点等级": "作者/项目正式研究，正文待核",
            "样本角色": "ITIF中国先进产业创新能力系列轻量目录",
            "编码状态": "目录待筛选",
            "预期用途": "中国科研能力、技术创新、产业转化、人才组织和先进产业比较",
            "本地原始资产路径": "",
            "原始资产状态": "官方落地页已保存；未下载全文",
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
            "序列角色": item.role,
            "技术领域": item.domain,
            "科学技术创新主题": themes,
            "中国关联": "是",
            "官方落地页": item.url,
            "资料层级": "ITIF正式报告轻量目录",
            "全文策略": "不自动下载；由跨行业比较和覆盖缺口触发",
            "采集日期": date.today().isoformat(),
        })
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "79_ITIF中国先进产业创新系列轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    result = f"""# ITIF中国先进产业创新系列轻量目录增补结果

- 2024年正式报告：{len(SERIES)}项，其中行业研究9项、综合报告1项。
- 覆盖机器人、化工与材料、核能、电动车与电池、生物技术、半导体、人工智能、量子、显示技术及先进产业综合比较。
- 新增统一总目录记录：{added}项；本轮未下载正文。

## 采集边界

该系列以科学论文、专利、研发投入、企业创新和产业转化能力衡量中国先进产业创新表现，因此整体纳入科学技术创新主轴。人才维度只标注于官方页面明确列出人才指标的AI报告，避免以系列共性替代单篇证据。安全或竞争性政策结论仍须回查正文，不因题名中的中国或先进产业信号自动上升为机构立场。
"""
    (root / "80_ITIF中国先进产业创新系列轻量目录结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(SERIES)} added={added} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
