from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


FIELDS = [
    "报告ID", "机构ID", "发布日期", "报告名称", "转向节点", "战略主题", "中国关联",
    "官方链接", "证据增量等级", "主要增量机制", "复核结论", "全文状态", "复核理由", "复核日期",
]


@dataclass(frozen=True)
class Selection:
    mechanism: str
    reason: str


SELECTED: dict[str, Selection] = {
    "C-CSET-14366": Selection("中国认知AI科研路径", "直接分析中国科学论文、研究机构与通用人工智能前置技术"),
    "C-CSET-12229": Selection("中国AI企业国际扩散", "补足中国AI企业在东南亚的投资、商业联系和技术扩散机制"),
    "C-STANFORD-HAI-WHITE-PAPER-BUILDING-NATIONAL-AI-RESEARCH-RESOURCE": Selection("国家AI科研基础设施", "补足算力、数据与公共研究资源如何改变大学和企业研究能力"),
    "C-STANFORD-HAI-AI-INDEX-2019": Selection("全球AI科研早期基线", "与已保存2023年指数构成生成式AI跃迁前后的跨期对照"),
    "C-FRAUNHOFER-ISI-DP-84": Selection("科研管理与人才吸引", "检验新公共管理工具对科研人员组织选择和人才配置的影响"),
    "C-FRAUNHOFER-ISI-DP-58": Selection("制造业数字化与创新绩效", "补足自动化、数字化、生产效率和企业创新绩效之间的经验关系"),
    "C-OECD-DOI-154981D7-EN": Selection("企业AI采用者特征", "提供技术采用、人才、企业生产率和区域集聚的微观数据证据"),
    "C-OECD-DOI-EBC2DEBE-EN": Selection("AI时代数字技术扩散", "形成2017—2023年跨国企业技术扩散、互补资产与生产率比较"),
    "C-KISTEP-PRG0720180121": Selection("生物医疗R&D投资方向", "补足早期生物医疗研发投入、创新政策和技术路线选择"),
    "C-KISTEP-RES0220180215": Selection("量子信息长期技术开发", "补足量子技术早期项目论证、研发组织和长期投资机制"),
    "C-STANFORD-HAI-POLICY-BRIEF-AIS-PROMISE-AND-PERIL-US-GOVERNMENT": Selection("公共部门AI采用与内部创新能力", "补足政府机构采用AI时的技术能力、内部研发和组织实施机制"),
    "C-US-OSTP-2016-QUANTUM-INFO-SCI-REPORT-2016-07-22-FINAL": Selection("量子信息科学早期国家战略", "形成2016年国家挑战、科研基础与技术机会基线，可与2020年研发计划对照"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def deferred_reason(row: dict[str, str]) -> str:
    title = row["报告名称"]
    institution = row["机构ID"]
    if row["报告ID"] == "C-KISTEP-RES0220200166":
        return "官方PDF为112160241字节，超过当前单文件版本化阈值；保留目录、入口和体量核验记录"
    if "AI Index" in title:
        return "2019与2023年已构成跨期基线，其余年度继续保留目录"
    if institution == "cset":
        return "外向投资审查侧重资本管制和安全政策，本轮不以此扩张全文"
    if institution == "us-ostp":
        return "峰会摘要、愿景或综合政绩材料与已保存正式战略和研发计划重复"
    if institution == "oecd-sti":
        return "税收激励或同类数字政策工具已有较充分本地证据，保留目录待专题触发"
    if institution == "kistep":
        return "与已选基础研究、生物医疗或量子项目机制重叠，保留韩文正式目录"
    return "与前两批已选材料的跨期或机制增量不足，继续保留目录"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    queue = read_csv(root / "70_定点补源优先队列.csv")
    catalog = {row["报告ID"]: row for row in read_csv(root / "05_报告总目录.csv")}
    queue_ids = {row["报告ID"] for row in queue}
    if not set(SELECTED) <= queue_ids:
        raise ValueError(f"selected IDs not in current queue: {sorted(set(SELECTED) - queue_ids)}")
    rows: list[dict[str, str]] = []
    for item in queue:
        report_id = item["报告ID"]
        selection = SELECTED.get(report_id)
        asset = catalog[report_id].get("本地原始资产路径", "")
        rows.append({
            "报告ID": report_id, "机构ID": item["机构ID"], "发布日期": item["发布日期"],
            "报告名称": item["报告名称"], "转向节点": item["转向节点"], "战略主题": item["战略主题"],
            "中国关联": item["中国关联"], "官方链接": item["官方链接"],
            "证据增量等级": "高" if selection else "中或低",
            "主要增量机制": selection.mechanism if selection else "目录层关注方向",
            "复核结论": "第二批精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(item), "复核日期": date.today().isoformat(),
        })
    write_csv(root / "94_第二批定点全文候选证据增量复核台账.csv", rows)
    selected = [row for row in rows if row["复核结论"] == "第二批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    china = [row for row in selected if row["中国关联"] == "是"]
    result = f"""# 第二批定点全文候选证据增量复核结果

- 当前候选：{len(rows)}份。
- 第二批精选：{len(selected)}份，其中中国直接关联{len(china)}份。
- 已保存本地资产：{len(acquired)}份；保留轻量目录：{len(rows) - len(selected)}份。

## 增量结构

本批补强早期AI与量子基线、国家AI科研基础设施、科研管理与人才、制造业数字化、企业AI采用与技术扩散、基础科学R&D生产率，以及中国认知AI科研和东南亚商业扩散。外向投资审查、峰会摘要、综合政绩和同系列年度指数未进入全文批次。

## 使用边界

中国认知AI和海外商业活动材料按作者或项目研究归因；相关竞争性判断需与报告使用的数据、方法和限定条件同时引用。安全措辞不构成独立纳入依据。
"""
    (root / "95_第二批定点全文候选证据增量复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)} china_selected={len(china)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
