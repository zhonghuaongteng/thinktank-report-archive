from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


FIELDS = ["报告ID", "机构ID", "发布日期", "报告名称", "转向节点", "战略主题", "中国关联", "官方链接", "证据增量等级", "主要增量机制", "复核结论", "全文状态", "复核理由", "复核日期"]


@dataclass(frozen=True)
class Selection:
    mechanism: str
    reason: str


SELECTED = {
    "C-KISTEP-RES0220210156": Selection("全球健康技术研发基金", "补足疫苗、治疗、诊断和数字健康的跨国研发资助及项目再评估机制"),
    "C-KISTEP-PRG0720230001": Selection("科技外交能力建设", "补足国际科技协作人才、教育训练和组织能力建设机制"),
    "C-OECD-DOI-EE847E5F-EN": Selection("量子计算商业化准备", "补足量子技术从研发走向企业采用所需的人才、设施、延伸服务和协作平台"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def deferred_reason(row: dict[str, str]) -> str:
    report_id = row["报告ID"]
    if report_id in {"C-STANFORD-HAI-AI-INDEX-2018", "C-STANFORD-HAI-AI-INDEX-2022", "C-STANFORD-HAI-AI-INDEX-2025"}:
        return "相邻AI Index年份继续以轻量目录承担趋势索引"
    if report_id == "C-KISTEP-PRG0720220002":
        return "技术霸权竞争框架会抬高安全议题权重，本轮不保存全文"
    if report_id in {"C-OECD-DOI-68058B95-EN", "C-OECD-DOI-D8B0D605-EN", "C-FRAUNHOFER-ISI-DP-86"}:
        return "内容治理、产品召回或关键性研究对科技创新机制的独立增量不足，保留目录"
    return "偏离科学发现、研发组织、科技人才、技术路线、成果转化和国际科技协作主轴，保留目录"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    output_path = root / "102_第六批定点全文候选证据增量复核台账.csv"
    queue = read_csv(root / "70_定点补源优先队列.csv")
    prior = read_csv(output_path) if output_path.exists() else []
    if set(SELECTED) <= {row["报告ID"] for row in prior}:
        queue = prior
    catalog = {row["报告ID"]: row for row in read_csv(root / "05_报告总目录.csv")}
    if not set(SELECTED) <= {row["报告ID"] for row in queue}:
        raise ValueError("selected IDs not in current queue")
    rows = []
    for item in queue:
        report_id = item["报告ID"]
        selection = SELECTED.get(report_id)
        asset = catalog[report_id].get("本地原始资产路径", "")
        rows.append({
            "报告ID": report_id, "机构ID": item["机构ID"], "发布日期": item["发布日期"], "报告名称": item["报告名称"],
            "转向节点": item["转向节点"], "战略主题": item["战略主题"], "中国关联": item["中国关联"], "官方链接": item["官方链接"],
            "证据增量等级": "高" if selection else "中或低", "主要增量机制": selection.mechanism if selection else "目录层关注方向",
            "复核结论": "第六批精选全文" if selection else "保留轻量目录", "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(item), "复核日期": date.today().isoformat(),
        })
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    selected = [row for row in rows if row["复核结论"] == "第六批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    result = f"""# 第六批定点全文候选证据增量复核结果

- 当前候选：{len(rows)}份。
- 第六批精选：{len(selected)}份；已保存本地资产：{len(acquired)}份。
- 保留轻量目录：{len(rows) - len(selected)}份。

本批补强全球健康技术研发基金、科技外交能力建设和量子计算商业化准备。技术霸权、关键性、内容治理以及相邻年度重复项保持目录级覆盖，不进入全文池。
"""
    (root / "103_第六批定点全文候选证据增量复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
