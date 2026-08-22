from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


FIELDS = ["报告ID", "机构ID", "发布日期", "报告名称", "报告类型", "官方链接", "证据增量等级", "主要增量机制", "复核结论", "全文状态", "复核理由", "复核日期"]


@dataclass(frozen=True)
class Selection:
    mechanism: str
    reason: str


SELECTED = {
    "C-FRAUNHOFER-ISI-DP-55": Selection("国有企业与创新产出", "以中国上市企业为样本检验所有制与创新产出的关系"),
    "C-FRAUNHOFER-ISI-DP-61": Selection("区域技术系统转型", "补足中国区域技术相关性和技术经济匹配的动态证据"),
    "C-FRAUNHOFER-ISI-DP-62": Selection("中国研发创新体系演进", "直接总结中国研发与创新体系十年发展"),
    "C-FRAUNHOFER-ISI-DP-63": Selection("中国研发创新政策前景", "补足中国研发创新政策未来发展判断"),
    "C-ITIF-2023-WAKE-UP-AMERICA-CHINA-IS-OVERTAKING-THE-UNITED-STATES-IN-INNOVATION-CAPACITY": Selection("中国创新能力比较", "提供中国创新能力跨指标比较及追赶判断"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-THE-ROBOTICS-INDUSTRY": Selection("机器人产业创新", "补足机器人技术、企业与产业创新能力证据"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-THE-CHEMICALS-INDUSTRY": Selection("化学工业创新", "补足化学工业研发、企业与产业创新证据"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-NUCLEAR-POWER": Selection("核能技术创新", "补足核电技术能力、产业组织与创新表现"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-THE-ELECTRIC-VEHICLE-AND-BATTERY-INDUSTRIES": Selection("电动汽车与电池创新", "补足新能源汽车和电池技术路线、企业能力与产业生态"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-BIOTECHNOLOGY": Selection("生物技术创新", "补足中国生物技术研发、企业与成果转化能力"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-SEMICONDUCTORS": Selection("半导体产业创新", "补足中国半导体研发、制造能力与创新绩效"),
    "C-ITIF-2024-CHINA-IS-RAPIDLY-BECOMING-A-LEADING-INNOVATOR-IN-ADVANCED-INDUSTRIES": Selection("先进产业综合创新", "形成中国先进产业创新能力的跨行业综合判断"),
    "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-THE-DISPLAY-INDUSTRY": Selection("显示产业创新", "补足显示技术研发、制造与企业创新能力"),
    "C-ITIF-2026-HAMILTON-INDEX-2026-CHINAS-DOMINANCE-IN-ADVANCED-INDUSTRIES-IS-GROWING": Selection("先进产业全球份额", "以Hamilton Index更新中国先进产业全球生产份额与结构"),
    "C-CSET-18346": Selection("科技人才回流", "以高华健个案观察中国高层次科技人才回流与科研组织机制"),
    "C-CSET-18319": Selection("中国生物技术企业", "补足BGI及中国生物技术企业、科研网络与技术能力证据"),
    "C-CSET-19825": Selection("中国科学院创新体系", "直接分析中国科学院在国家科技创新体系中的组织、资助与转化作用"),
    "S-CSIS-2026-01": Selection("中国高技术创新驱动", "补足中国高技术产业创新的近期综合判断并保持机构归因"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog = read_csv(root / "05_报告总目录.csv")
    candidates = [row for row in catalog if re.search(r"China|Chinese|PRC|中国|중국", row["报告名称"], re.I) and not row.get("本地原始资产路径")]
    prior_path = root / "104_第七批中国科技创新全文候选复核台账.csv"
    prior = read_csv(prior_path) if prior_path.exists() else []
    if set(SELECTED) <= {row["报告ID"] for row in prior}:
        candidates = prior
    if not set(SELECTED) <= {row["报告ID"] for row in candidates}:
        raise ValueError("selected IDs missing from China-title candidates")
    rows = []
    for item in candidates:
        report_id = item["报告ID"]
        selection = SELECTED.get(report_id)
        current = next(row for row in catalog if row["报告ID"] == report_id)
        reason = selection.reason if selection else "宏观竞争、脱钩、安全治理、资源治理或一般经济关系材料保持目录级覆盖"
        rows.append({
            "报告ID": report_id, "机构ID": item["机构ID"], "发布日期": item["发布日期"], "报告名称": item["报告名称"],
            "报告类型": item["报告类型"], "官方链接": item.get("原文链接", item.get("官方链接", "")), "证据增量等级": "高" if selection else "中或低",
            "主要增量机制": selection.mechanism if selection else "目录层中国议题", "复核结论": "第七批精选全文" if selection else "保留轻量目录",
            "全文状态": "本地资产已保存" if current.get("本地原始资产路径") else ("待获取" if selection else "不下载"),
            "复核理由": reason, "复核日期": date.today().isoformat(),
        })
    with prior_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    selected = [row for row in rows if row["复核结论"] == "第七批精选全文"]
    acquired = [row for row in selected if row["全文状态"] == "本地资产已保存"]
    result = f"""# 第七批中国科技创新全文候选复核结果

- 中国题名候选：{len(rows)}份。
- 第七批精选：{len(selected)}份；已保存本地资产：{len(acquired)}份。
- 保留轻量目录：{len(rows) - len(selected)}份。

本批以中国研发创新体系、区域技术系统、科技人才回流、中国科学院、先进产业创新能力以及机器人、化工、核能、电动汽车与电池、生物技术、半导体和显示产业为重点。宏观竞争、技术脱钩、安全治理、资源治理和一般经济关系材料继续只留目录。
"""
    (root / "105_第七批中国科技创新全文候选复核结果.md").write_text(result, encoding="utf-8")
    print(f"candidates={len(rows)} selected={len(selected)} acquired={len(acquired)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
