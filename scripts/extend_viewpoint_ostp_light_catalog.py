from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup


TRUMP_SOURCE_URL = "https://trumpwhitehouse.archives.gov/ostp/documents-and-reports/"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "发布日期", "日期精度", "报告名称", "政策节点角色",
    "科学技术创新主题", "中国关联", "官方索引或落地页", "官方PDF入口", "时期来源",
    "全文策略", "源文件SHA256", "采集日期",
]


INCLUDE = re.compile(
    r"science|technology|research(?: and| &)? development|\bR&D\b|artificial intelligence|"
    r"quantum|computing|STEM|advanced manufacturing|bioeconomy|biotechnology|nanotechnology|"
    r"citizen science|research environment|wireless communications|public access",
    re.I,
)
SECURITY_LED = re.compile(
    r"cybersecurity|nuclear defense|electromagnetic pulses|security and integrity|research security|"
    r"national security presidential memorandum.*research and development",
    re.I,
)


@dataclass(frozen=True)
class OstpItem:
    published: str
    title: str
    url: str
    source_page: str
    source_period: str
    role: str
    themes: tuple[str, ...]
    china_relation: str = "否；美国科技创新政策基线或节点样本"
    precision: str = "日"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def canonical_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(value).lower())


def canonical_url(value: str) -> str:
    return value.strip().lower().replace("http://", "https://").split("?", 1)[0].rstrip("/")


def theme_labels(title: str) -> tuple[str, ...]:
    value = clean_text(title)
    themes: list[str] = []
    if re.search(r"science|research|R&D|public access|research environment", value, re.I):
        themes.append("科学体系与基础研究")
    if re.search(r"technology|artificial intelligence|quantum|computing|manufacturing|bioeconomy|biotechnology|nanotechnology|wireless", value, re.I):
        themes.append("技术创新与关键技术")
    if re.search(r"strategy|strategic|plan|priorit|initiative|policy|implementation|leadership|innovation", value, re.I):
        themes.append("创新政策与研发治理")
    if re.search(r"STEM|workforce|education|research environment|research community", value, re.I):
        themes.append("人才大学与科研组织")
    if re.search(r"manufacturing|bioeconomy|biotechnology|innovation|industry|commercial", value, re.I):
        themes.append("产业创新转化与区域生态")
    if re.search(r"global|international|around the world|public access|open access|ocean", value, re.I):
        themes.append("国际合作开放科学与比较")
    if re.search(r"China|Chinese|PRC", value, re.I):
        themes.append("中国科技横向维度")
    if not themes:
        themes = ["创新政策与研发治理"]
    return tuple(dict.fromkeys(themes))


def parse_date(value: str) -> tuple[str, str]:
    value = clean_text(value)
    for fmt in ("%B %d, %Y", "%B %Y"):
        try:
            parsed = datetime.strptime(value, fmt)
            if fmt == "%B %Y":
                return parsed.strftime("%Y-%m-01"), "月；以当月1日作排序占位，不代表实际发布日期"
            return parsed.strftime("%Y-%m-%d"), "日"
        except ValueError:
            pass
    raise ValueError(f"unsupported official date: {value}")


def parse_trump_archive(source_html: str) -> list[OstpItem]:
    soup = BeautifulSoup(source_html, "html.parser")
    records: dict[str, OstpItem] = {}
    for item in soup.select("li"):
        anchor = item.find("a", href=True)
        if not anchor:
            continue
        title = clean_text(anchor.get_text(" ", strip=True))
        text = clean_text(item.get_text(" ", strip=True))
        match = re.search(r"\((January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{1,2},)?\s+20\d{2}\)\s*$", text)
        if not match or not INCLUDE.search(title) or SECURITY_LED.search(title):
            continue
        date_text = match.group(0).strip("()")
        published, precision = parse_date(date_text)
        if not 2017 <= int(published[:4]) <= 2021:
            continue
        url = urljoin(TRUMP_SOURCE_URL, str(anchor["href"]))
        key = canonical_url(url)
        records.setdefault(key, OstpItem(
            published, title, url, TRUMP_SOURCE_URL, "Trump OSTP/NSTC官方归档",
            "联邦科学技术战略、研发投入或创新体系节点", theme_labels(title), precision=precision,
        ))
    return sorted(records.values(), key=lambda row: (row.published, row.title))


OBAMA_ITEMS = (
    OstpItem("2016-01-01", "Principles for Promoting Access to Federal Government-Supported Scientific Data and Research Findings through International Scientific Cooperation", "https://obamawhitehouse.archives.gov/sites/default/files/microsites/ostp/NSTC/iwgodsp_principles_0.pdf", "https://obamawhitehouse.archives.gov/node/10054/", "Obama OSTP/NSTC官方归档", "开放科学与国际科研合作基线", ("科学体系与基础研究", "创新政策与研发治理", "国际合作开放科学与比较"), precision="年；以1月1日作排序占位，不代表实际发布日期"),
    OstpItem("2016-01-01", "National Nanotechnology Initiative 2016 Strategic Plan", "https://www.nano.gov/sites/default/files/pub_resource/2016-nni-strategic-plan.pdf", "https://obamawhitehouse.archives.gov/node/10054/", "Obama OSTP/NSTC官方归档", "纳米科技长期研发与产业化战略", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "产业创新转化与区域生态"), precision="年；以1月1日作排序占位，不代表实际发布日期"),
    OstpItem("2016-10-12", "Preparing for the Future of Artificial Intelligence", "https://obamawhitehouse.archives.gov/sites/default/files/whitehouse_files/microsites/ostp/NSTC/preparing_for_the_future_of_ai.pdf", "https://obamawhitehouse.archives.gov/blog/2016/10/12/administrations-report-future-artificial-intelligence", "Obama OSTP/NSTC官方归档", "AI技术应用、创新机会与政策问题基线", ("技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较")),
    OstpItem("2016-10-12", "The National Artificial Intelligence Research and Development Strategic Plan", "https://obamawhitehouse.archives.gov/sites/default/files/whitehouse_files/microsites/ostp/NSTC/national_ai_rd_strategic_plan.pdf", "https://obamawhitehouse.archives.gov/blog/2016/10/12/administrations-report-future-artificial-intelligence", "Obama OSTP/NSTC官方归档", "国家AI基础与应用研发战略基线", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态")),
    OstpItem("2016-01-01", "Sustaining a Competitive Edge in Innovation Through a World-Class Federal Science and Technology Workforce", "https://obamawhitehouse.archives.gov/sites/default/files/federal_science_and_technology_workforce_report.pdf", "https://obamawhitehouse.archives.gov/node/10054/", "Obama OSTP/NSTC官方归档", "联邦科技人才与科研组织能力", ("科学体系与基础研究", "创新政策与研发治理", "人才大学与科研组织"), precision="年；以1月1日作排序占位，不代表实际发布日期"),
    OstpItem("2016-07-22", "Advancing Quantum Information Science: National Challenges and Opportunities", "https://obamawhitehouse.archives.gov/sites/default/files/quantum_info_sci_report_2016_07_22_final.pdf", "https://obamawhitehouse.archives.gov/node/10054/", "Obama OSTP/NSTC官方归档", "量子信息科学研究议程", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织")),
    OstpItem("2016-05-01", "The Federal Big Data Research and Development Strategic Plan", "https://obamawhitehouse.archives.gov/sites/default/files/microsites/ostp/NSTC/bigdatardstrategicplan-nitrd_final-051916.pdf", "https://obamawhitehouse.archives.gov/node/10054/", "Obama OSTP/NSTC官方归档", "大数据基础研究、基础设施与应用战略", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态"), precision="月；以当月1日作排序占位，不代表实际发布日期"),
)


BIDEN_ITEMS = (
    OstpItem("2021-11-05", "2021 Public Access Congressional Report", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2022/02/2021-Public-Access-Congressional-Report_OSTP.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "联邦资助研究成果开放获取进展", ("科学体系与基础研究", "创新政策与研发治理", "国际合作开放科学与比较")),
    OstpItem("2022-02-01", "Critical and Emerging Technologies List Update", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2022/02/02-2022-Critical-and-Emerging-Technologies-List-Update.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "关键与新兴技术组合边界", ("技术创新与关键技术", "创新政策与研发治理", "产业创新转化与区域生态"), china_relation="技术清单本身不作中国判断；作为后续中美技术比较的美国政策基线", precision="月；以当月1日作排序占位，不代表实际发布日期"),
    OstpItem("2022-08-25", "Ensuring Free, Immediate, and Equitable Access to Federally Funded Research", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2022/08/08-2022-OSTP-Public-Access-Memo.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "联邦科研成果即时开放政策", ("科学体系与基础研究", "创新政策与研发治理", "国际合作开放科学与比较")),
    OstpItem("2022-08-31", "Economic Landscape of Federal Public Access Policy", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2022/08/08-2022-OSTP-Public-Access-Congressional-Report.pdf", "https://bidenwhitehouse.archives.gov/ostp/news-updates/2022/08/31/economic-landscape-of-federal-public-access-policy/", "Biden OSTP/NSTC官方归档", "开放获取政策的经济成本与科研传播机制", ("科学体系与基础研究", "创新政策与研发治理", "国际合作开放科学与比较")),
    OstpItem("2023-03-01", "Bold Goals for U.S. Biotechnology and Biomanufacturing: Harnessing Research and Development to Further Societal Goals", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2023/03/Bold-Goals-for-U.S.-Biotechnology-and-Biomanufacturing-Harnessing-Research-and-Development-To-Further-Societal-Goals-FINAL.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "生物技术从基础研究到生物制造的任务导向创新", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态"), precision="月；以当月1日作排序占位，不代表实际发布日期"),
    OstpItem("2023-05-01", "The National Artificial Intelligence Research and Development Strategic Plan: 2023 Update", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2023/05/National-Artificial-Intelligence-Research-and-Development-Strategic-Plan-2023-Update.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "国家AI研发战略更新与国际协作", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较"), precision="月；以当月1日作排序占位，不代表实际发布日期"),
    OstpItem("2024-02-01", "Biennial Report to Congress on International Science & Technology Cooperation", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/02/2024-Biennial-Report-to-Congress-on-International-Science-Technology-Cooperation.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "国际科技合作、国内创新能力与关键技术协作", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"), china_relation="是；正文涉及中国并把国内创新投入与国际科技合作联系起来", precision="月；以当月1日作排序占位，不代表实际发布日期"),
    OstpItem("2024-03-01", "National Strategy on Microelectronics Research", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/03/National-Strategy-on-Microelectronics-Research-March-2024.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "微电子基础研究、制造、人才与公私协同", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态"), precision="月；以当月1日作排序占位，不代表实际发布日期"),
    OstpItem("2024-10-01", "Quadrennial Science and Technology Review Report", "https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/10/2024-Quadrennial-Science-and-Technology-Review.pdf", "https://bidenwhitehouse.archives.gov/ostp/", "Biden OSTP/NSTC官方归档", "美国科研事业、联邦研发与国家任务的综合审视", ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较", "中国科技横向维度"), china_relation="是；正文明确讨论中国科技竞争及其对美国研发体系的影响", precision="月；以当月1日作排序占位，不代表实际发布日期"),
)


CURRENT_ITEMS = (
    OstpItem(
        "2025-06-23",
        "Agency Guidance for Implementing Gold Standard Science in the Conduct & Management of Scientific Activities",
        "https://www.whitehouse.gov/wp-content/uploads/2025/03/OSTP-Guidance-for-GSS-June-2025.pdf",
        "https://www.whitehouse.gov/ostp/information-resources/",
        "2025—2026现行OSTP官方资源",
        "联邦科学活动的研究设计、同行评议、可重复性与公开传播规范",
        ("科学体系与基础研究", "创新政策与研发治理", "人才大学与科研组织", "国际合作开放科学与比较"),
    ),
    OstpItem(
        "2026-01-01",
        "Trump Administration Science & Technology Highlights: Year One",
        "https://www.whitehouse.gov/wp-content/uploads/2026/01/WHOSTP-2025-Wins.pdf",
        "https://www.whitehouse.gov/ostp/information-resources/",
        "2025—2026现行OSTP官方资源",
        "年度科技创新政策、任务导向研发与公私协同进展",
        ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理", "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较"),
        china_relation="全球技术与创新政策背景；中国命题须回查正文",
        precision="月；以1月1日作排序占位，不代表实际发布日期",
    ),
)


def stable_report_id(item: OstpItem) -> str:
    slug = urlsplit(item.url).path.strip("/").split("/")[-1].rsplit(".", 1)[0]
    return "C-US-OSTP-" + item.published[:4] + "-" + re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-").upper()


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
    parser.add_argument("--trump-html", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    source_bytes = args.trump_html.read_bytes()
    trump_items = parse_trump_archive(source_bytes.decode("utf-8"))
    if len(trump_items) < 25:
        raise ValueError(f"expected at least 25 innovation-led Trump OSTP records; found {len(trump_items)}")
    items = sorted((*OBAMA_ITEMS, *trump_items, *BIDEN_ITEMS, *CURRENT_ITEMS), key=lambda row: (row.published, row.title))
    selected_ids = {stable_report_id(item) for item in items}

    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    catalog = [
        row for row in catalog
        if row.get("样本角色") != "OSTP联邦科技创新政策节点轻量目录" or row.get("报告ID") in selected_ids
    ]
    existing_by_id = {row["报告ID"]: row for row in catalog}
    existing_by_url = {canonical_url(row.get("原文链接", "")): row["报告ID"] for row in catalog if row.get("原文链接")}
    existing_by_title_year = {
        (canonical_title(row.get("报告名称", "")), row.get("发布日期", "")[:4]): row["报告ID"]
        for row in catalog if row.get("报告名称")
    }
    ledger_rows: list[dict[str, str]] = []
    added = linked = 0
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    for item in items:
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
                "机构ID": "us-ostp",
                "机构英文名": "White House Office of Science and Technology Policy",
                "国家或地区": "美国",
                "发布日期": item.published,
                "观察窗": observation_window(item.published),
                "报告名称": item.title,
                "报告类型": "OSTP/NSTC科学技术创新政策文件",
                "原文链接": item.url,
                "本地路径": "",
                "正文完整度": "官方索引与PDF入口元数据",
                "优先级": "P0-China-innovation-candidate" if "是；" in item.china_relation else "P1-STI-light-catalog",
                "示踪问题": themes,
                "机构观点等级": "美国政府正式科技政策文件，正文待核",
                "样本角色": "OSTP联邦科技创新政策节点轻量目录",
                "编码状态": "目录待筛选",
                "预期用途": "联邦研发、关键技术、科研组织、人才、产业转化、开放科学和国际科技合作",
                "本地原始资产路径": "",
                "原始资产状态": "官方PDF入口已保存；未下载全文" + (f"；{item.precision}" if item.precision != "日" else ""),
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
            "政策节点角色": item.role,
            "科学技术创新主题": themes,
            "中国关联": item.china_relation,
            "官方索引或落地页": item.source_page,
            "官方PDF入口": item.url,
            "时期来源": item.source_period,
            "全文策略": "不自动下载；由科学技术创新主轴缺口、政策节点价值与中国关联触发",
            "源文件SHA256": source_hash if item.source_period.startswith("Trump") else "静态核验官方入口",
            "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "88_美国OSTP科学技术创新政策轻量目录.csv", ledger_rows, LEDGER_FIELDS)
    node_counts = {window: sum(observation_window(item.published) == window for item in items) for window in ("W1", "W2", "W3")}
    china_count = sum("中国科技横向维度" in item.themes for item in items)
    result = f"""# 美国OSTP科学技术创新政策轻量目录增补结果

- 正式科技政策文件：{len(items)}项；Obama时期{len(OBAMA_ITEMS)}项、Trump第一任期{len(trump_items)}项、Biden时期{len(BIDEN_ITEMS)}项、2025—2026现行OSTP资源{len(CURRENT_ITEMS)}项。
- 观察窗分布：W1（2016—2018）{node_counts['W1']}项；W2（2019—2021）{node_counts['W2']}项；W3（2022—2026）{node_counts['W3']}项。
- 与既有统一目录关联：{linked}项；新增统一总目录：{added}项；明确中国横向关联：{china_count}项。
- Trump时期官方索引快照SHA256：`{source_hash}`；本轮未下载正文。

## 采集边界

目录围绕联邦研发投入、基础研究、AI与量子等关键技术、先进制造、生物技术、科研人才、开放科学和国际科技合作建立政策节点。纯网络安全、核防御、电磁脉冲和“研究安全/完整性”主导文件已从自动纳入条件中排除，避免安全议程抬高覆盖率。

中国关联只在官方正文已经明确涉及中国或可核验的中美比较时标注。关键与新兴技术清单等材料仅作为美国技术政策基线，不据题名推断对华立场。机构判断、政策因果和战略转向仍须由精选全文支持。
"""
    (root / "89_美国OSTP科学技术创新政策轻量目录结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(items)} obama={len(OBAMA_ITEMS)} trump={len(trump_items)} biden={len(BIDEN_ITEMS)} linked={linked} added={added} china={china_count} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
