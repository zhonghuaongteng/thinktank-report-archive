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
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-QUANTUM": Selection("中国量子创新能力与产业转化", "中国直接关联，补足量子技术从科研能力到产业化的比较证据"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-AI": Selection("中国AI创新体系与产业能力", "中国直接关联，覆盖研发、人才、企业与产业化的综合机制"),
    "C-ITIF-2025-HOW-REDUCING-FEDERAL-RD-REDUCES-GDP-GROWTH": Selection("公共R&D投入与经济增长", "补足基础研究投入收缩如何传导至生产率和增长的机制证据"),
    "C-ITIF-2025-UNDERSTANDING-COMPARING-NATIONAL-INNOVATION-SYSTEMS-US-KOREA-CHINA-JAPAN-TAIWAN": Selection("国家创新体系跨国比较", "同时覆盖中国、美国、日本、韩国与台湾，具有跨项目复用价值"),
    "C-CSET-18600": Selection("中国医疗AI与生物数据转化", "连接科学数据、医疗AI、监管条件与生物经济转化"),
    "C-CSET-17987": Selection("中国脑机接口科研能力", "以文献计量证据识别中国非治疗性脑机接口科研布局"),
    "C-CSET-16526": Selection("中国AI人才与科研组织", "补足人才规模、培养结构和科研组织能力证据"),
    "C-STANFORD-HAI-BEYOND-DEEPSEEK-CHINAS-DIVERSE-OPEN-WEIGHT-AI-ECOSYSTEM-AND-ITS-POLICY-IMPLICATIONS": Selection("中国开放权重AI生态", "补足模型路线、开放生态、企业结构与政策含义的近期节点"),
    "C-STANFORD-HAI-AI-INDEX-2023": Selection("生成式AI跃迁前的全球基线", "从年度系列中只选一个结构转折前基线，避免重复下载整套指数"),
    "C-FRAUNHOFER-ISI-DP-64": Selection("使命导向创新政策类型", "提供创新政策目标、工具组合和治理结构的可比较分类"),
    "C-FRAUNHOFER-ISI-DP-73": Selection("中国在全球科学创新体系中的角色", "直接分析中国科研产出、合作网络和创新体系位置变化"),
    "C-OECD-DOI-7CC876F7-EN": Selection("国家科研基础设施运行机制", "补足大型科研设施治理、开放使用和绩效机制"),
    "C-OECD-DOI-0002217C-EN": Selection("产业政策工具框架", "提供产业创新政策目标、工具与评估的通用比较框架"),
    "C-KISTEP-RES0220240068": Selection("研究者主导基础研究与战略技术", "检验基础研究自主性与战略方向设定之间的组织张力"),
    "C-KISTEP-PRG0720240044": Selection("基础研究预算政策", "补足基础研究投入结构、预算配置与政策优先序证据"),
    "C-US-OSTP-2018-ADVANCED-MANUFACTURING-STRATEGIC-PLAN-2018": Selection("先进制造研发与产业转化", "形成2018年制造创新、人才和公私协作政策基线"),
    "C-US-OSTP-2020-ARTIFICIAL-INTELLIGENCE-QUANTUM-INFORMATION-SCIENCE-R-D-SUMMARY-AUGUST-2020": Selection("AI与量子联邦研发投入", "保留研发计划与预算工具材料，压缩同年峰会和愿景文件"),
    "C-US-OSTP-2023-BOLD-GOALS-FOR-U-S-BIOTECHNOLOGY-AND-BIOMANUFACTURING-HARNESSING-RESEARCH-AND-DEVELOPMENT-TO-FURTHER-SOCIETAL-GOALS-FINAL": Selection("生物技术研发与生物制造转化", "连接基础研发、工程平台、社会目标和规模化制造"),
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
    institution = row["机构ID"]
    title = row["报告名称"]
    if institution == "stanford-hai" and "AI Index" in title:
        return "年度指数重复度较高；保留目录并以2023年结构转折前基线代表本轮全文"
    if institution == "oecd-sti":
        return "与本轮已选科研基础设施或产业政策框架处于同一政策工具族；保留目录待具体项目触发"
    if institution == "kistep":
        return "与已选基础研究战略及预算材料存在机制重叠；韩文正式目录继续保留"
    if institution == "us-ostp":
        return "同一技术领域已有研发计划或正式战略锚点；峰会摘要、愿景和综合政绩材料暂不补全文"
    if institution == "fraunhofer-isi":
        return "本轮跨国创新体系与使命导向材料已覆盖主要增量；其余专题保留目录"
    return "正式目录保留；与已选材料相比跨期或机制增量不足"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    queue = read_csv(root / "70_定点补源优先队列.csv")
    catalog = {row["报告ID"]: row for row in read_csv(root / "05_报告总目录.csv")}
    rows: list[dict[str, str]] = []
    for item in queue:
        report_id = item["报告ID"]
        selection = SELECTED.get(report_id)
        asset = catalog[report_id].get("本地原始资产路径", "")
        rows.append({
            "报告ID": report_id,
            "机构ID": item["机构ID"],
            "发布日期": item["发布日期"],
            "报告名称": item["报告名称"],
            "转向节点": item["转向节点"],
            "战略主题": item["战略主题"],
            "中国关联": item["中国关联"],
            "官方链接": item["官方链接"],
            "证据增量等级": "高" if selection else "中或低",
            "主要增量机制": selection.mechanism if selection else "目录层关注方向",
            "复核结论": "本轮精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(item),
            "复核日期": date.today().isoformat(),
        })
    write_csv(root / "92_定点全文候选证据增量复核台账.csv", rows)
    selected = [row for row in rows if row["复核结论"] == "本轮精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    china = [row for row in selected if row["中国关联"] == "是"]
    result = f"""# 定点全文候选证据增量复核结果

- 下载前候选：{len(rows)}份。
- 本轮精选：{len(selected)}份，其中中国直接关联{len(china)}份。
- 已保存本地资产：{len(acquired)}份；其余精选项仍须核验官方附件或网页正文。
- 保留轻量目录：{len(rows) - len(selected)}份，不自动下载。

## 选择口径

全文选择同时考察跨期锚点、六条科学技术创新机制、中国直接关联、正式性和与本地证据的重复度。年度指数只选结构节点，峰会摘要、愿景性材料和同一政策工具族的重复报告继续保留目录。安全、供应链与竞争措辞不形成独立加分。

## 使用边界

本台账记录下载决策和证据角色，不等同于观点编码。机构立场、因果机制和政策评价仍须回查正文、原句与页码；网页材料保持作者或项目归因。
"""
    (root / "93_定点全文候选证据增量复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)} china_selected={len(china)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
