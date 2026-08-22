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


SELECTED: dict[str, Selection] = {
    "C-FRAUNHOFER-ISI-DP-49": Selection("创新系统边界扩展", "补足创新系统从传统主体向新型行动者与制度开放的早期理论节点"),
    "C-FRAUNHOFER-ISI-DP-52": Selection("创新政策方向性", "解释创新系统中的方向失灵及反思性治理，为任务导向转型提供前置机制"),
    "C-FRAUNHOFER-ISI-DP-54": Selection("企业研发集中度", "以企业数据检验研发与创新是否向少数企业集中，补足创新能力结构证据"),
    "C-FRAUNHOFER-ISI-DP-57": Selection("国家高技术战略绩效", "以专利活动评估德国高技术战略十年表现，形成战略实施与技术产出的纵向节点"),
    "C-FRAUNHOFER-ISI-DP-66": Selection("科学知识进入政策", "分析科学知识影响政策概念框架的条件，连接科学体系与政策学习"),
    "C-FRAUNHOFER-ISI-DP-67": Selection("创新系统转型", "集中讨论转型目标对创新政策提出的新要求，构成政策范式变化节点"),
    "C-FRAUNHOFER-ISI-DP-71": Selection("任务导向政策实施", "把任务定义到执行刻画为多阶段翻译过程，补足政策落地机制"),
    "C-FRAUNHOFER-ISI-DP-72": Selection("公共科研经济效应", "量化公共研究机构的宏观经济影响，补足科研投入与经济产出的连接机制"),
    "C-FRAUNHOFER-ISI-DP-79": Selection("创新需求与公共采购", "分析需求侧政策和公共采购如何驱动技术与社会转型"),
    "C-FRAUNHOFER-ISI-DP-80": Selection("公共科研组织转型", "提供公共部门组织成为转型行动者的结构分析框架"),
    "C-FRAUNHOFER-ISI-DP-88": Selection("人工智能研发质量", "界定AI研究创新领域及质量判断方法，补足技术领域识别与科研评价证据"),
    "C-FRAUNHOFER-ISI-DP-90": Selection("大型组织变革能力", "讨论大型公共与私人组织参与转型的治理条件和行动能力"),
    "C-FRAUNHOFER-ISI-DP-93": Selection("变革型政策国家能力", "比较不同政体配置下国家干预的表现条件，深化变革型创新政策机制"),
    "C-FRAUNHOFER-ISI-DP-94": Selection("高技术战略议程演进", "直接连接德国高技术战略与高技术议程，形成2016—2026纵向政策节点"),
}


CANDIDATE_IDS = list(SELECTED) + [
    "C-FRAUNHOFER-ISI-DP-53",
    "C-FRAUNHOFER-ISI-DP-59",
    "C-FRAUNHOFER-ISI-DP-65",
    "C-FRAUNHOFER-ISI-DP-74",
    "C-FRAUNHOFER-ISI-DP-83",
    "S-FISI-2016-01",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def deferred_reason(report_id: str) -> str:
    reasons = {
        "C-FRAUNHOFER-ISI-DP-53": "专利分类方法价值较窄，保留目录供技术识别方法专题调用",
        "C-FRAUNHOFER-ISI-DP-59": "一般性战略实施讨论与已选任务导向政策材料重叠",
        "C-FRAUNHOFER-ISI-DP-65": "国家角色框架与已选创新系统转型和国家干预材料重叠",
        "C-FRAUNHOFER-ISI-DP-74": "社会影响测量属于补充方法材料，当前纵向主链增量较低",
        "C-FRAUNHOFER-ISI-DP-83": "创新与增长关系具有理论价值，但对科研组织和技术政策主链的直接增量有限",
        "S-FISI-2016-01": "已作为正式锚点保存全文，无需重复下载",
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
            "中国关联": "比较参照",
            "官方链接": item["原文链接"],
            "证据增量等级": "高" if selection else "中或低",
            "主要增量机制": selection.mechanism if selection else "目录层关注方向",
            "复核结论": "第九批精选全文" if selection else "保留轻量目录或既有锚点",
            "全文状态": "本地资产已保存" if asset else ("待获取" if selection else "不下载"),
            "复核理由": selection.reason if selection else deferred_reason(report_id),
            "复核日期": date.today().isoformat(),
        })

    review_path = root / "108_第九批科学体系与创新政策纵向全文候选复核台账.csv"
    with review_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    selected = [row for row in rows if row["复核结论"] == "第九批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    result = f"""# 第九批科学体系与创新政策纵向全文候选复核结果

- 定点复核：{len(rows)}份。
- 第九批精选：{len(selected)}份；已保存本地资产：{len(acquired)}份。
- 保留轻量目录或既有锚点：{len(rows) - len(selected)}份。

## 增量结构

本批以Fraunhofer ISI连续讨论论文构造2016—2026纵向证据链，覆盖创新系统边界与方向性、企业研发结构、高技术战略绩效、科学知识进入政策、任务导向实施、公共科研经济效应、需求侧创新、科研组织转型、AI研发质量及变革型政策国家能力。

## 采集边界

全文选择由科学体系、研发组织、创新政策、技术识别与成果机制触发。一般安全、供应链与治理标签不触发补取；中国维度在后续编码中作为国际比较坐标处理。
"""
    (root / "109_第九批科学体系与创新政策纵向全文候选复核结果.md").write_text(result, encoding="utf-8")
    print(f"reviewed={len(rows)} selected={len(selected)} acquired={len(acquired)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
