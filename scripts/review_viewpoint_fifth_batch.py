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
    "C-KISTEP-RES0220220113": Selection("基础研究议程协调", "补足基础研究促进委员会在政策议程、跨部门协调和制度运行方面的年度证据"),
    "C-KISTEP-PRG0720210065": Selection("分学科基础研究资助", "补足基础研究支持体系按学科落地的分类方法、资助结构和现场应用指南"),
    "C-KISTEP-RES0220210142": Selection("基础研究治理连续性", "与2021年度材料形成连续观察，识别基础研究议程及协调机制的变化"),
    "C-OECD-DOI-2AE8C0DC-EN": Selection("竞争性科研资助制度", "系统比较竞争性科研资助、同行评议、成功率、风险偏好和战略目标匹配机制"),
    "C-OECD-DOI-F1A650D9-EN": Selection("早期AI创新政策", "保留机器学习跃迁初期对科研进展、创新扩散、技能与政策框架的基线判断"),
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
    report_id = row["报告ID"]
    if report_id in {"C-STANFORD-HAI-AI-INDEX-2018", "C-STANFORD-HAI-AI-INDEX-2022", "C-STANFORD-HAI-AI-INDEX-2025"}:
        return "相邻关键年份已有六个AI Index全文观察点，标题与目录继续承担趋势索引功能"
    if report_id in {"C-OECD-DOI-A978348F-EN", "C-OECD-DOI-FC426AB9-EN", "C-OECD-DOI-D7557242-EN", "C-OECD-DOI-00F7D7DB-EN"}:
        return "旅游、碳足迹、废钢或全球价值链就业研究偏离当前科学技术创新证据主轴，保留目录"
    if report_id in {"C-OECD-DOI-68058B95-EN", "C-OECD-DOI-D8B0D605-EN"}:
        return "内容治理或产品召回门户不构成科研与技术创新机制证据，保留目录"
    if report_id == "C-FRAUNHOFER-ISI-DP-86":
        return "关键性和供应链风险权重较高，对研发组织与技术路线的独立增量不足，保留目录"
    return "与既有全文的科技创新机制增量不足，继续保留轻量目录"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    queue = read_csv(root / "70_定点补源优先队列.csv")
    prior_path = root / "100_第五批定点全文候选证据增量复核台账.csv"
    prior = read_csv(prior_path) if prior_path.exists() else []
    if set(SELECTED) <= {row["报告ID"] for row in prior}:
        queue = prior
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
            "复核结论": "第五批精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(item), "复核日期": date.today().isoformat(),
        })
    write_csv(prior_path, rows)
    selected = [row for row in rows if row["复核结论"] == "第五批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    china = [row for row in selected if row["中国关联"] == "是"]
    result = f"""# 第五批定点全文候选证据增量复核结果

- 当前候选：{len(rows)}份。
- 第五批精选：{len(selected)}份，其中中国直接关联{len(china)}份。
- 已保存本地资产：{len(acquired)}份；保留轻量目录：{len(rows) - len(selected)}份。

## 增量结构

本批补强基础研究议程协调、分学科基础研究资助、基础研究治理连续性、竞争性科研资助制度和早期AI创新政策基线。

## 停止边界

当前候选中的相邻AI Index年度、旅游、碳足迹、废钢、全球价值链就业、内容治理、产品召回和关键性研究继续只保留轻量目录。后续全文获取由新的科学发现、研发组织、科技人才、技术路线、成果转化或国际科技协作问题触发，不按年份和机构全量扩张。
"""
    (root / "101_第五批定点全文候选证据增量复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)} china_selected={len(china)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
