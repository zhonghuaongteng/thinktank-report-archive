from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "发布日期", "日期精度", "报告名称", "序列角色",
    "科学技术创新主题", "中国关联", "官方落地页", "官方PDF入口", "资料层级",
    "全文策略", "采集日期",
]


@dataclass(frozen=True)
class HaiItem:
    published: str
    title: str
    url: str
    role: str
    themes: tuple[str, ...]
    china_relation: str
    precision: str = "日"
    pdf_url: str = ""


CORE = (
    "科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理",
    "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较",
)


def annual(year: int) -> HaiItem:
    return HaiItem(
        f"{year}-01-01",
        f"The {year} AI Index Report",
        f"https://hai.stanford.edu/ai-index/{year}-ai-index-report",
        "AI技术、研发、人才、产业与政策全球指标连续序列",
        CORE + ("中国科技横向维度",),
        "全球指标体系含中国及中美比较；具体数值与命题须回查当年正文",
        "年；统一目录以1月1日作排序占位，不代表实际发布日期",
        "https://hai.stanford.edu/assets/files/hai_ai-index-report_2023.pdf" if year == 2023 else "",
    )


ITEMS = tuple(annual(year) for year in (2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025, 2026)) + (
    HaiItem(
        "2020-01-01", "Stanford HAI 2019–2020 Annual Report",
        "https://hai.stanford.edu/sites/default/files/2021-02/hai-2020-annual-report_1.pdf",
        "机构早期研究计划、跨学科组织与公共算力活动记录",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较"),
        "含全球AI研究和机构活动；具体中国内容须回查正文",
        "学年；统一目录以2020年1月1日作排序占位，不代表实际发布日期",
        "https://hai.stanford.edu/sites/default/files/2021-02/hai-2020-annual-report_1.pdf",
    ),
    HaiItem(
        "2020-09-01", "AI's Promise and Peril for the U.S. Government",
        "https://hai.stanford.edu/policy/policy-brief-ais-promise-and-peril-us-government",
        "公共部门AI应用、内部技术能力与政府创新",
        ("技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态"),
        "否；美国公共部门技术创新样本",
    ),
    HaiItem(
        "2021-05-01", "Policy Strategies for Harnessing the Productivity Potential of AI in the U.S.",
        "https://hai.stanford.edu/policy/policy-brief-policy-strategies-harnessing-productivity-potential-ai-us",
        "AI通用技术、互补创新与生产率机制",
        ("技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态"),
        "否；美国创新政策机制样本",
        pdf_url="https://hai.stanford.edu/sites/default/files/2021-05/Policy-Brief_Policy-Strategies-for-Harnessing-AI-Productivity-Potential.pdf",
    ),
    HaiItem(
        "2021-10-01", "Building a National AI Research Resource: A Blueprint for the National Research Cloud",
        "https://hai.stanford.edu/policy/white-paper-building-national-ai-research-resource",
        "公共算力、数据与学术AI研究基础设施",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态"),
        "否；美国公共科研基础设施样本",
    ),
    HaiItem(
        "2022-03-09", "Recommendations on Updating the National Artificial Intelligence Research and Development Strategic Plan",
        "https://hai.stanford.edu/policy/white-paper-recommendations-updating-national-artificial-intelligence-research-and-development",
        "国家AI研发投入与组织机制建议",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "国际合作开放科学与比较"),
        "否；美国国家AI研发战略样本",
        pdf_url="https://hai.stanford.edu/sites/default/files/2022-03/HAI%20Policy%20White%20Paper%20-%20Recommendations%20on%20Updating%20the%20National%20AI%20R%26D%20Strategy.pdf",
    ),
    HaiItem(
        "2024-12-04", "Expanding Academia’s Role in Public Sector AI",
        "https://hai.stanford.edu/policy/expanding-academias-role-in-public-sector-ai",
        "大学与企业在前沿AI研究中的能力分化",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织"),
        "含全球前沿AI科研组织比较；中国命题待正文核实",
        pdf_url="https://hai.stanford.edu/assets/files/hai-issue-brief-expanding-academia-role-public-sector.pdf",
    ),
    HaiItem(
        "2025-12-16", "Beyond DeepSeek: China's Diverse Open-Weight AI Ecosystem and Its Policy Implications",
        "https://hai.stanford.edu/policy/beyond-deepseek-chinas-diverse-open-weight-ai-ecosystem-and-its-policy-implications",
        "中国开放权重模型技术与产业生态",
        ("技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"),
        "是；题名与官方摘要直接讨论中国模型生态",
    ),
    HaiItem(
        "2025-12-26", "Response to OSTP's Request for Information on Accelerating the American Scientific Enterprise",
        "https://hai.stanford.edu/policy/response-to-ostps-request-for-information-on-accelerating-the-american-scientific-enterprise",
        "AI赋能科学发现、团队科学与开放研究生态",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "国际合作开放科学与比较"),
        "否；美国科学事业组织模式样本",
    ),
)


def canonical_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def canonical_url(value: str) -> str:
    return value.strip().lower().replace("http://", "https://").rstrip("/")


def stable_report_id(item: HaiItem) -> str:
    if "ai-index" in item.url and re.fullmatch(r"The \d{4} AI Index Report", item.title):
        return f"C-STANFORD-HAI-AI-INDEX-{item.published[:4]}"
    slug = urlsplit(item.url).path.strip("/").split("/")[-1]
    return "C-STANFORD-HAI-" + re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-").upper()


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    selected_ids = {stable_report_id(item) for item in ITEMS}
    catalog = [
        row for row in catalog
        if row.get("样本角色") != "Stanford HAI科学技术创新连续序列轻量目录" or row.get("报告ID") in selected_ids
    ]
    existing_by_id = {row["报告ID"]: row for row in catalog}
    existing_by_url = {canonical_url(row.get("原文链接", "")): row["报告ID"] for row in catalog if row.get("原文链接")}
    existing_by_title_year = {
        (canonical_title(row.get("报告名称", "")), row.get("发布日期", "")[:4]): row["报告ID"]
        for row in catalog if row.get("报告名称")
    }
    ledger_rows: list[dict[str, str]] = []
    added = linked = 0
    for item in ITEMS:
        report_id = stable_report_id(item)
        unified_id = existing_by_url.get(canonical_url(item.url)) or existing_by_title_year.get(
            (canonical_title(item.title), item.published[:4])
        ) or report_id
        themes = "；".join(item.themes)
        if unified_id in existing_by_id:
            linked += 1
        else:
            row = {
                "报告ID": report_id,
                "机构ID": "stanford-hai",
                "机构英文名": "Stanford Institute for Human-Centered Artificial Intelligence",
                "国家或地区": "美国",
                "发布日期": item.published,
                "观察窗": observation_window(item.published),
                "报告名称": item.title,
                "报告类型": "Stanford HAI AI Index/科技创新政策研究",
                "原文链接": item.url,
                "本地路径": "",
                "正文完整度": "官方落地页与PDF入口元数据" if item.pdf_url else "官方落地页元数据",
                "优先级": "P0-China-innovation-candidate" if "是；" in item.china_relation else "P1-STI-light-catalog",
                "示踪问题": themes,
                "机构观点等级": "机构正式报告或政策研究，正文待核",
                "样本角色": "Stanford HAI科学技术创新连续序列轻量目录",
                "编码状态": "目录待筛选",
                "预期用途": "AI技术进展、科研组织、公共算力、人才、产业化、政策及中国比较",
                "本地原始资产路径": "",
                "原始资产状态": "官方入口已保存；未下载全文" + (f"；{item.precision}" if item.precision != "日" else ""),
            }
            catalog.append(row)
            existing_by_id[report_id] = row
            existing_by_url[canonical_url(item.url)] = report_id
            existing_by_title_year[(canonical_title(item.title), item.published[:4])] = report_id
            added += 1
        ledger_rows.append({
            "报告ID": report_id,
            "统一目录报告ID": unified_id,
            "发布日期": item.published,
            "日期精度": item.precision,
            "报告名称": item.title,
            "序列角色": item.role,
            "科学技术创新主题": themes,
            "中国关联": item.china_relation,
            "官方落地页": item.url,
            "官方PDF入口": item.pdf_url,
            "资料层级": "Stanford HAI正式年度报告或政策研究",
            "全文策略": "不自动下载；由科学技术创新主轴缺口、连续比较与中国关联触发",
            "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "86_Stanford_HAI科学技术创新轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    annual_count = sum("AI Index Report" in item.title for item in ITEMS)
    china_count = sum("中国科技横向维度" in item.themes for item in ITEMS)
    result = f"""# Stanford HAI科学技术创新轻量目录增补结果

- 正式年度报告或政策研究：{len(ITEMS)}项；其中AI Index连续年度报告{annual_count}项，另含2019—2020机构年度报告与公共部门AI政策简报。
- 与既有统一目录关联：{linked}项；新增统一总目录：{added}项。
- 中国横向维度：{china_count}项；本轮未下载正文。

## 采集边界

AI Index用于观察AI论文、专利、技术性能、科研组织、人才、投资、产业采用和政策的连续变化。政策研究只保留公共科研基础设施、国家研发战略、大学科研能力、AI生产率、科学发现及中国开放模型生态等创新机制明确的材料。

年度报告落地页仅以年份标识时，统一目录以当年1月1日作排序占位，不能据此引用实际发布日期。全球指标报告的“中国关联”表示系列包含中国或中美比较维度，不代表每一章都提出中国命题；机构立场、数据口径和因果解释须回查当年正文。
"""
    (root / "87_Stanford_HAI科学技术创新轻量目录结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(ITEMS)} annual={annual_count} linked={linked} added={added} china={china_count} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
