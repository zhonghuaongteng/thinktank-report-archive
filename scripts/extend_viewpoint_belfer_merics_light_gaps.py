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
    "报告ID", "统一目录报告ID", "机构ID", "发布日期", "报告名称", "创新机制",
    "科学技术创新主题", "中国关联", "官方落地页", "资料层级", "全文策略", "采集日期",
]


@dataclass(frozen=True)
class GapItem:
    institution_id: str
    institution_name: str
    region: str
    published: str
    title: str
    url: str
    role: str
    themes: tuple[str, ...]
    china_relation: str
    material_type: str
    viewpoint_level: str


ITEMS = (
    GapItem(
        "merics", "Mercator Institute for China Studies", "德国", "2016-08-12",
        "Made in China 2025: The making of a high-tech superpower and consequences for industrial countries",
        "https://merics.org/en/report/made-china-2025",
        "中国高技术产业政策、研发投入、专利与产业升级基线",
        ("技术创新与关键技术", "创新政策与研发治理", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
        "是；题名及官方摘要直接分析中国高技术产业战略",
        "MERICS正式报告轻量目录",
        "机构正式报告，正文待核",
    ),
    GapItem(
        "merics", "Mercator Institute for China Studies", "德国", "2018-03-27",
        "China’s way to an innovation superpower",
        "https://merics.org/en/comment/chinas-way-innovation-superpower",
        "中国AI、5G、区块链、电动汽车与创新要素趋势研判",
        ("技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
        "是；正文直接讨论中国创新能力、研发支持、人才与前沿技术",
        "MERICS机构评论轻量目录",
        "署名作者观点；仅作趋势线索与背景证据",
    ),
    GapItem(
        "belfer", "Belfer Center for Science and International Affairs", "美国", "2024-02-20",
        "Unraveling the Political Dynamics Shaping the U.S. Strategy for Technology Leadership",
        "https://www.belfercenter.org/publication/unraveling-political-dynamics-shaping-us-strategy-technology-leadership",
        "CHIPS and Science Act、先进技术产业政策与创新战略形成机制",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "中国科技横向维度"),
        "是；官方摘要明确把中国技术能力上升列为美国战略形成背景",
        "Belfer正式研究轻量目录",
        "作者/项目正式研究，正文待核",
    ),
)


def canonical_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def canonical_url(value: str) -> str:
    return value.strip().lower().replace("http://", "https://").rstrip("/")


def stable_report_id(item: GapItem) -> str:
    slug = urlsplit(item.url).path.strip("/").split("/")[-1]
    return f"C-LIGHT-{item.institution_id.upper()}-{item.published[:4]}-" + re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-").upper()


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
    selected_ids = {stable_report_id(item) for item in ITEMS}
    catalog = [row for row in catalog if row.get("样本角色") != "Belfer与MERICS科学技术创新节点轻量目录" or row.get("报告ID") in selected_ids]
    existing_by_id = {row["报告ID"]: row for row in catalog}
    existing_by_url = {canonical_url(row.get("原文链接", "")): row["报告ID"] for row in catalog if row.get("原文链接")}
    existing_by_title_year = {(canonical_title(row.get("报告名称", "")), row.get("发布日期", "")[:4]): row["报告ID"] for row in catalog if row.get("报告名称")}
    ledger_rows: list[dict[str, str]] = []
    added = linked = 0
    for item in ITEMS:
        report_id = stable_report_id(item)
        unified_id = existing_by_url.get(canonical_url(item.url)) or existing_by_title_year.get((canonical_title(item.title), item.published[:4])) or report_id
        themes = "；".join(item.themes)
        if unified_id in existing_by_id:
            linked += 1
        else:
            row = {
                "报告ID": report_id, "机构ID": item.institution_id, "机构英文名": item.institution_name,
                "国家或地区": item.region, "发布日期": item.published, "观察窗": observation_window(item.published),
                "报告名称": item.title, "报告类型": item.material_type, "原文链接": item.url,
                "本地路径": "", "正文完整度": "官方落地页与附件入口元数据", "优先级": "P0-China-innovation-candidate",
                "示踪问题": themes, "机构观点等级": item.viewpoint_level,
                "样本角色": "Belfer与MERICS科学技术创新节点轻量目录", "编码状态": "目录待筛选",
                "预期用途": "中国技术与产业创新、美国科技领导战略及政策形成机制比较",
                "本地原始资产路径": "", "原始资产状态": "官方入口已保存；未下载全文",
            }
            catalog.append(row)
            existing_by_id[report_id] = row
            existing_by_url[canonical_url(item.url)] = report_id
            existing_by_title_year[(canonical_title(item.title), item.published[:4])] = report_id
            added += 1
        ledger_rows.append({
            "报告ID": report_id, "统一目录报告ID": unified_id, "机构ID": item.institution_id,
            "发布日期": item.published, "报告名称": item.title, "创新机制": item.role,
            "科学技术创新主题": themes, "中国关联": item.china_relation, "官方落地页": item.url,
            "资料层级": item.material_type, "全文策略": "不自动下载；由创新机制增量与中国比较价值触发",
            "采集日期": date.today().isoformat(),
        })
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "90_Belfer_MERICS科学技术创新缺口轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    result = f"""# Belfer与MERICS科学技术创新缺口轻量目录结果

- 资料共{len(ITEMS)}项，其中正式报告2项、机构官网署名评论1项；与既有目录关联{linked}项，新增统一目录{added}项。
- MERICS补入2016年《中国制造2025》研究，形成中国高技术产业政策、研发投入、专利与产业升级的早期基线。
- MERICS补入2018年创新强国趋势评论，覆盖AI、5G、区块链、电动汽车、研发支持与人才等创新要素；仅按作者观点使用。
- Belfer补入2024年美国技术领导战略形成研究，直接讨论CHIPS and Science Act、先进技术产业政策及中国技术能力上升。
- 三项均只保存官方元数据入口，本轮未下载正文。

## 采集边界

纳入依据是创新体系、技术能力和产业政策机制。竞争叙述只作为解释政策形成的背景，不生成安全主题覆盖。题名与官方摘要可用于关注方向识别；机构观点、因果机制和政策评价须回查正文。
"""
    (root / "91_Belfer_MERICS科学技术创新缺口轻量目录结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(ITEMS)} linked={linked} added={added} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
