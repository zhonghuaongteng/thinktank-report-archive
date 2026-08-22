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
    china_link: str = "比较参照"


SELECTED: dict[str, Selection] = {
    "C-CSET-13458": Selection("中国通用人工智能科研组织", "直接分析北京通用人工智能研究院的目标、技术路线、组织与人才结构", "直接"),
    "C-CSET-15022": Selection("生命科学研究版图", "以论文数据刻画功能获得与功能缺失研究的全球分布、协作网络和方法结构", "全球比较"),
    "C-CSET-20520": Selection("新兴技术趋势识别", "补足使用大数据开展技术扫描、规划和资源配置的方法证据", "方法参照"),
    "C-CSET-20613": Selection("人工智能技能形成", "补足AI扩散条件下职业培训、技能供给与人才政策的近期证据", "人才参照"),
    "C-FRAUNHOFER-ISI-DP-91": Selection("国家创新战略能力", "拆解创新战略的目标、协调和执行能力，可用于比较国家创新政策组织方式"),
    "C-FRAUNHOFER-ISI-DP-87": Selection("科学研究经济效应", "以创新研究院的分期设立识别科学研究机构的因果经济效应", "科研机构参照"),
    "C-FRAUNHOFER-ISI-DP-85": Selection("产业发展与技术能力", "比较产业发展、国际协作和技术自主之间的政策组合，保留创新机制主线", "新兴经济体参照"),
    "C-STANFORD-HAI-WHITE-PAPER-RECOMMENDATIONS-UPDATING-NATIONAL-ARTIFICIAL-INTELLIGENCE-RESEARCH-AND-DEVELOPMENT": Selection("人工智能研发体系", "提供公共AI研发预算、科研基础设施、跨学科研究和技术人才政策建议", "国际比较"),
    "S-OECD-2025-01": Selection("全球科技创新政策转型", "旗舰报告综合科学体系、技术融合、产业生态、科研合作与政策试验的最新变化", "含主要伙伴经济体"),
    "C-OECD-DOI-2B93187F-EN": Selection("大型科研基础设施", "补足大型科研设施的投资、建设、运行、开放使用和国际协作机制"),
    "C-OECD-DOI-D7917B11-EN": Selection("专业研发机构", "提供专业研发机构的部门归类、资金来源及其对国家研发绩效的贡献测量"),
    "C-OECD-DOI-BA2AAF7B-EN": Selection("变革型科技创新政策", "形成变革型STI政策议程、政策能力与工具组合的系统参照"),
    "C-OECD-DOI-1EE956A5-EN": Selection("任务导向创新组合管理", "补足任务导向创新政策的主动组合管理、项目调整与学习机制"),
    "C-OECD-DOI-D725304C-EN": Selection("韩国任务导向创新", "提供东亚科技体系中任务导向政策设计与实施的可比案例", "东亚参照"),
    "C-OECD-DOI-5E55E7AB-EN": Selection("量子技术国家战略", "比较各国量子技术战略、研发支持、基础设施、人才和产业化安排", "含中国比较"),
    "S-CSIS-2020-01": Selection("产业政策向创新战略转化", "提炼政府支持关键技术创新的历史经验和政策设计原则，并明确中国崛起语境", "中国竞争语境"),
}


CANDIDATE_IDS = list(SELECTED) + [
    "C-CSET-20366", "C-CSET-19631", "C-CSET-18992", "C-CSET-18518",
    "C-CSET-18636", "C-CSET-17919", "C-CSET-16648", "C-CSET-14591",
    "C-OECD-DOI-4154CDBF-EN", "C-OECD-DOI-0254AE07-EN",
    "C-FRAUNHOFER-ISI-DP-86", "C-US-OSTP-2025-OSTP-GUIDANCE-FOR-GSS-JUNE-2025",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def deferred_reason(report_id: str) -> str:
    if report_id.startswith("C-CSET-"):
        return "AI安全、治理、标准、风险或事故报告材料保持目录级覆盖，当前不增加科技创新机制全文"
    if report_id == "C-OECD-DOI-4154CDBF-EN":
        return "半导体价值链材料与既有产业链证据重叠，继续保留目录供定点调用"
    if report_id == "C-OECD-DOI-0254AE07-EN":
        return "综合数字政策框架范围过宽，对科学与技术创新机制的独立增量有限"
    if report_id == "C-FRAUNHOFER-ISI-DP-86":
        return "关键性与供应链语境较强，暂不以安全标签触发全文"
    return "研究规范争议与当前科技创新主轴的增量尚需进一步核验"


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
            "复核结论": "第八批精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(report_id),
            "复核日期": date.today().isoformat(),
        })

    review_path = root / "106_第八批科技创新与中国比较全文候选复核台账.csv"
    with review_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    selected = [row for row in rows if row["复核结论"] == "第八批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    result = f"""# 第八批科技创新与中国比较全文候选复核结果

- 定点复核：{len(rows)}份。
- 第八批精选：{len(selected)}份；已保存本地资产：{len(acquired)}份。
- 保留轻量目录：{len(rows) - len(selected)}份。

## 增量结构

本批围绕全球科技创新政策转型、科研基础设施与专业研发机构、创新战略能力、任务导向创新、量子技术战略、AI研发与人才、中国通用人工智能科研组织及产业政策向创新战略转化形成互补证据。

## 采集边界

AI安全、治理、标准、风险、事故报告、关键性和一般数字政策框架继续保留轻量目录。安全语境只有在改变研发投入、科研组织、技术路线、人才、成果转化或国际科技合作时进入全文证据。
"""
    (root / "107_第八批科技创新与中国比较全文候选复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
