from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


FIELDS = [
    "报告ID", "机构ID", "发布日期", "报告名称", "报告类型", "中国关联",
    "官方链接", "证据增量等级", "主要增量机制", "复核结论", "全文状态", "复核理由", "复核日期",
]


@dataclass(frozen=True)
class Selection:
    mechanism: str
    reason: str
    china_link: str = "国际比较参照"


SELECTED: dict[str, Selection] = {
    "S-OECD-2016-01": Selection("全球科技创新体系基线", "提供十年观察窗起点的研发投入、科研体系、技术趋势和创新政策综合基线", "含中国统计与比较"),
    "S-OECD-2021-01": Selection("危机条件下的科技体系", "记录疫情冲击下科研动员、协作、资助与政策能力变化", "含中国统计与比较"),
    "S-OECD-2023-01": Selection("转型时期的科技政策", "连接气候、产业与社会转型对科技创新政策的新要求", "含中国统计与比较"),
    "C-OECD-DOI-235C9806-EN": Selection("国家研究政策组织", "比较OECD国家研究政策的组织结构、职责配置和协调方式"),
    "C-OECD-DOI-0D057DA7-EN": Selection("公共研究与创新创业", "连接公共科研成果、研究人员创业和创新企业形成机制"),
    "C-OECD-DOI-66A3BD38-EN": Selection("科学产业知识交换", "补足大学、科研机构与企业之间知识流动和合作机制"),
    "C-OECD-DOI-A4C9197A-EN": Selection("公共研究影响政策", "比较增强公共研究经济社会影响的政策工具与实施安排"),
    "C-OECD-DOI-18D3BF19-EN": Selection("全球科研人员结构", "以科学作者调查刻画科研职业、流动、协作与数字工具使用"),
    "C-OECD-DOI-1B06C47C-EN": Selection("科学数字化转型", "系统描述数据、计算和数字协作平台改变科学研究过程的机制"),
    "C-OECD-DOI-0CA0CA45-EN": Selection("跨学科研究组织", "补足面向社会挑战的跨学科研究资助、组织和评价机制"),
    "C-OECD-DOI-E08AA3BB-EN": Selection("数据密集型科研人才", "分析数据密集型科学所需技能、职业能力和机构建设"),
    "C-OECD-DOI-06913B3B-EN": Selection("高风险高回报研究资助", "比较支持突破性研究的项目设计、遴选、管理和容错机制"),
    "C-OECD-DOI-0F8BD468-EN": Selection("科研职业稳定性", "识别学术研究职业不稳定的制度来源及政策应对"),
    "C-OECD-DOI-4D787B35-EN": Selection("科学商业知识转移", "以西班牙为案例分析科学与企业协作和知识转移体系改革"),
    "C-OECD-DOI-9EB9A85B-EN": Selection("公共科研资助治理", "以瑞典为案例比较公共科研资助结构、绩效与政策协调"),
    "C-OECD-DOI-DC21227A-EN": Selection("博士后职业路径", "补足博士与博士后研究人员多元职业发展及人才流动政策"),
}


CANDIDATE_IDS = list(SELECTED) + [
    "S-OECD-2018-01",
    "C-OECD-DOI-5JLR2Z70K0BX-EN",
    "C-OECD-DOI-A1CFB1A8-EN",
    "C-OECD-DOI-0C685800-EN",
    "C-OECD-DOI-5JLN7VNPXS32-EN",
    "C-OECD-DOI-A09A3A5D-EN",
    "C-OECD-DOI-8A306011-EN",
    "C-OECD-DOI-302B12BB-EN",
    "C-OECD-DOI-FA11A0E0-EN",
    "C-OECD-DOI-EADD1094-EN",
    "C-OECD-DOI-1C416F43-EN",
    "C-OECD-DOI-3F6C76A4-EN",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def deferred_reason(report_id: str) -> str:
    reasons = {
        "S-OECD-2018-01": "官方页面保留目录；当前未确认可稳定取得的OECD官方PDF直链",
        "C-OECD-DOI-5JLR2Z70K0BX-EN": "开放获取论文保留目录；旧版官方附件当前不可稳定取得",
        "C-OECD-DOI-A1CFB1A8-EN": "公民科学材料保留目录；官方PDF直链待后续核验",
        "C-OECD-DOI-0C685800-EN": "科学体系新期待材料保留目录；官方PDF直链待后续核验",
        "C-OECD-DOI-5JLN7VNPXS32-EN": "研究伦理材料保留目录，待数据治理专题出现独立缺口后调用",
        "C-OECD-DOI-A09A3A5D-EN": "包容性创新范围较宽，与当前科学体系纵向主链的直接增量较低",
        "C-OECD-DOI-8A306011-EN": "社会科学角色议题保留目录，后续科研结构专题定点调用",
        "C-OECD-DOI-302B12BB-EN": "研究数据仓储商业模式属于基础设施细分议题，现有证据已可覆盖",
        "C-OECD-DOI-FA11A0E0-EN": "国际科研基础设施可持续性与既有大型科研设施材料重叠",
        "C-OECD-DOI-EADD1094-EN": "数字时代创新政策范围较宽，优先保留更直接的科学数字化机制材料",
        "C-OECD-DOI-1C416F43-EN": "研究安全主题保留轻量目录，不以安全标签单独触发全文",
        "C-OECD-DOI-3F6C76A4-EN": "任务导向政策设计与既有OECD、Fraunhofer材料重叠",
    }
    return reasons[report_id]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_rows = read_csv(root / "05_报告总目录.csv")
    catalog = {row["报告ID"]: row for row in catalog_rows}
    missing = set(CANDIDATE_IDS) - set(catalog)
    if missing:
        raise ValueError(f"candidate IDs missing from catalog: {sorted(missing)}")

    rows: list[dict[str, str]] = []
    for report_id in CANDIDATE_IDS:
        item = catalog[report_id]
        selection = SELECTED.get(report_id)
        asset = item.get("本地原始资产路径", "")
        rows.append({
            "报告ID": report_id,
            "机构ID": item["机构ID"],
            "发布日期": item["发布日期"],
            "报告名称": item["报告名称"],
            "报告类型": item["报告类型"],
            "中国关联": selection.china_link if selection else "目录语境",
            "官方链接": item["原文链接"],
            "证据增量等级": "高" if selection else "中或低",
            "主要增量机制": selection.mechanism if selection else "目录层关注方向",
            "复核结论": "第十批精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(report_id),
            "复核日期": date.today().isoformat(),
        })

    path = root / "110_第十批OECD科学体系与科研机制纵向全文候选复核台账.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    selected = [row for row in rows if row["复核结论"] == "第十批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    result = f"""# 第十批OECD科学体系与科研机制纵向全文候选复核结果

- 定点复核：{len(rows)}份。
- 第十批精选：{len(selected)}份；已保存本地资产：{len(acquired)}份。
- 保留轻量目录：{len(rows) - len(selected)}份。

## 增量结构

本批以2016、2021、2023三个OECD STI Outlook旗舰节点为纵向骨架，补充研究政策组织、公共研究与创业、科学产业知识交换、科研影响、科研人员结构、科学数字化、跨学科研究、数据密集型科研人才、高风险高回报资助、科研职业与知识转移。2018旗舰、开放获取、公民科学及科学体系新期待材料保留目录，待官方附件入口可稳定核验后再补。

## 采集边界

研究安全材料保留轻量目录。一般数字政策、任务导向政策和科研基础设施重复材料不再下载；全文选择继续由科学体系、研发资助、科研组织、人才与知识转移机制触发。
"""
    (root / "111_第十批OECD科学体系与科研机制纵向全文候选复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
