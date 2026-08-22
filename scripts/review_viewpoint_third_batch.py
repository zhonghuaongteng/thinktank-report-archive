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
    "C-STANFORD-HAI-AI-INDEX-2017": Selection("全球AI创新起点基线", "形成近十年AI科研、人才、产业和国家比较的序列起点"),
    "C-STANFORD-HAI-AI-INDEX-2021": Selection("规模化前夜的AI创新体系", "补足大模型跃迁前科研产出、人才流动、算力和产业投入结构"),
    "C-STANFORD-HAI-AI-INDEX-2024": Selection("生成式AI扩散节点", "补足生成式AI对研发投入、模型能力、产业采用和全球竞争格局的改变"),
    "C-STANFORD-HAI-AI-INDEX-2026": Selection("AI创新最新观察点", "提供十年观察窗末端的科研、技术、人才、产业与中国比较基线"),
    "C-OECD-DOI-65234003-EN": Selection("研发税收激励政策组合", "补足研发税收激励与直接资助之间的互补、替代和企业响应机制"),
    "C-OECD-DOI-7B43B038-EN": Selection("政府资助AI研发测量", "补足如何识别公共研发项目中的AI内容及其政策组合"),
    "C-OECD-DOI-4805D3F5-EN": Selection("企业研发绩效与资金结构", "提供企业微观数据层面的研发执行、资金来源和结构变化证据"),
    "C-OECD-DOI-4889F5F2-EN": Selection("危机条件下政府研发投入", "补足疫情冲击下各国研发资助响应和科学政策优先序变化"),
    "C-KISTEP-PRG0720190004": Selection("大学研发管理组织", "补足大学科研管理、产学合作组织和制度改进的韩国经验"),
    "C-KISTEP-RES0220200140": Selection("基础研究协调机制", "补足基础研究促进委员会、政策协调和投入治理的组织材料；官方附件为图像型PDF，列入OCR待补"),
    "C-US-OSTP-2020-A-STRATEGIC-VISION-FOR-AMERICAS-QUANTUM-NETWORKS-FEB-2020": Selection("量子网络技术路线", "与量子信息科学早期基线衔接，观察从科学机会到网络基础设施的路线推进"),
    "C-US-OSTP-2019-AI-RESEARCH-AND-DEVELOPMENT-PROGRESS-REPORT-2016-2019": Selection("国家AI研发进展", "补足2016至2019年美国AI研发计划、机构分工和项目推进的阶段总结"),
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
    if row["报告ID"] in {"C-STANFORD-HAI-AI-INDEX-2018", "C-STANFORD-HAI-AI-INDEX-2022", "C-STANFORD-HAI-AI-INDEX-2025"}:
        return "相邻年度已由2017、2019、2021、2023、2024和2026节点覆盖，保留目录"
    if institution == "cset":
        return "资本审查、并购追踪或一般治理的安全和监管权重较高，本轮不扩张全文"
    if institution == "fraunhofer-isi":
        return "关键性与供应链议题的科技创新机制增量有限，保留目录"
    if institution == "oecd-sti":
        return "与已选研发资助、企业研发或政策组合材料机制重叠，保留目录待专题触发"
    if institution == "kistep":
        return "与已保存项目评估、基础研究或企业创新材料重叠，保留韩文正式目录"
    if institution == "us-ostp":
        return "综合政绩材料与具体研发计划相比证据粒度较低，保留目录"
    return f"{title}与前三批已选材料的机制增量不足，继续保留目录"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    queue = read_csv(root / "70_定点补源优先队列.csv")
    prior_path = root / "96_第三批定点全文候选证据增量复核台账.csv"
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
            "复核结论": "第三批精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(item), "复核日期": date.today().isoformat(),
        })
    write_csv(root / "96_第三批定点全文候选证据增量复核台账.csv", rows)
    selected = [row for row in rows if row["复核结论"] == "第三批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    china = [row for row in selected if row["中国关联"] == "是"]
    result = f"""# 第三批定点全文候选证据增量复核结果

- 当前候选：{len(rows)}份。
- 第三批精选：{len(selected)}份，其中中国关联{len(china)}份。
- 已保存本地资产：{len(acquired)}份；保留轻量目录：{len(rows) - len(selected)}份。

## 增量结构

本批建立2017—2026年AI创新指标的关键节点序列，并补强政府资助研发测量、企业研发投入、研发税收激励、危机条件下科研资助、大学科研管理、基础研究协调、量子网络技术路线和国家AI研发进展。相邻年度指数只保留目录，避免年度报告全量堆积。KISTEP基础研究协调报告为图像型PDF，列入OCR待补。

## 使用边界

AI指数中的中国数据用于跨期和跨国比较，引用时回查对应年度的口径、样本和修订说明。安全、资本审查和关键性议题不构成独立全文触发条件。
"""
    (root / "97_第三批定点全文候选证据增量复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)} china_selected={len(china)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
