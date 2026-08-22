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
    "C-CSET-11988": Selection("中国AI企业融资结构", "直接量化美国资本进入中国AI企业的规模、阶段和企业类型，用于技术商业化与跨境资本机制"),
    "C-CSET-20338": Selection("AI企业并购与创新转化", "补足AI企业并购、技术获取和创新资产整合的微观证据"),
    "C-KISTEP-PRG0720220058": Selection("中小企业数字化与研发活动", "以企业研发大数据检验数字化转型支持政策及中小企业创新行为"),
    "C-KISTEP-RES0220220146": Selection("生物铸造研发基础设施", "补足生物铸造平台的建设论证、技术开发和科研基础设施组织"),
    "C-KISTEP-RES0220220145": Selection("生物研究材料基础", "补足生物研究材料利用平台、科研资源配置和项目治理"),
    "C-KISTEP-RES0220180246": Selection("中小企业全球创新技术开发", "补足中小企业技术开发、国际化和项目评估的早期基线"),
    "C-OECD-DOI-13D38F92-EN": Selection("语言模型技术节点", "提供生成式AI跃迁初期的技术能力、经济影响与政策问题综合判断"),
    "C-OECD-DOI-876367E3-EN": Selection("国家AI算力能力", "补足算力供需测量、国家科研基础设施和资源配置框架"),
    "C-OECD-DOI-BAFCDC7B-EN": Selection("研发资助方向性测量", "以Fundstat和机器学习识别公共研发资助与社会目标的关联"),
    "C-OECD-DOI-34797721-EN": Selection("科研基础设施生态", "补足跨设施、跨学科协作及科研基础设施可持续治理机制"),
    "C-OECD-DOI-5EE60CB5-EN": Selection("创新政策范式变化", "以自然语言处理识别创新政策目标和工具的长期结构变化"),
    "C-US-OSTP-2020-TRUMP-ADMINISTRATION-ST-HIGHLIGHTS-2017-2020": Selection("美国科技政策阶段总结", "形成2017至2020年联邦研发、关键技术、人才和国际科技领导议程的综合节点"),
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
        return "相邻关键年份已有六个AI Index全文观察点，继续保留目录"
    if report_id == "C-CSET-18960":
        return "一般AI监管权限研究与当前科技创新证据主轴增量有限，保留目录"
    if report_id == "C-OECD-DOI-0FB79BB9-EN":
        return "与已保存的企业AI采用者特征和数字技术扩散材料高度重叠，保留目录"
    if report_id in {"C-OECD-DOI-68058B95-EN", "C-OECD-DOI-D8B0D605-EN"}:
        return "内容分享治理或产品召回门户不构成科学技术创新机制证据，保留目录"
    if report_id == "C-FRAUNHOFER-ISI-DP-86":
        return "关键性与供应链语境权重较高，对当前创新机制的独立增量不足，保留目录"
    return "与既有全文的机制增量不足，继续保留轻量目录"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    queue = read_csv(root / "70_定点补源优先队列.csv")
    prior_path = root / "98_第四批定点全文候选证据增量复核台账.csv"
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
            "复核结论": "第四批精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(item), "复核日期": date.today().isoformat(),
        })
    write_csv(prior_path, rows)
    selected = [row for row in rows if row["复核结论"] == "第四批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    china = [row for row in selected if row["中国关联"] == "是"]
    result = f"""# 第四批定点全文候选证据增量复核结果

- 当前候选：{len(rows)}份。
- 第四批精选：{len(selected)}份，其中中国直接关联{len(china)}份。
- 已保存本地资产：{len(acquired)}份；保留轻量目录：{len(rows) - len(selected)}份。

## 增量结构

本批补强中国AI企业融资与AI企业并购、中小企业数字化研发、生物铸造和生物研究材料基础设施、全球创新技术开发、语言模型技术节点、国家AI算力、研发资助方向性测量、科研基础设施生态、创新政策范式变化及美国科技政策阶段总结。

## 使用边界

CSET对华投资材料只用于中国AI企业融资、创新资本和技术商业化机制，安全政策主张保持作者与研究项目归因。一般AI监管、内容治理、产品召回、相邻AI Index年度和关键性议题继续只留目录。
"""
    (root / "99_第四批定点全文候选证据增量复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)} china_selected={len(china)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
