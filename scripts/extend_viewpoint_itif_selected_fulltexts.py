from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

from pypdf import PdfReader

try:
    from scripts.extend_viewpoint_itif_reports_catalog import (
        CATALOG_FIELDS,
        CDP_PROXY,
        _proxy_json,
        report_id,
        wait_until,
    )
    from scripts.extend_viewpoint_csis_rai_selected_fulltexts import browser_pdf
except ModuleNotFoundError:
    from extend_viewpoint_itif_reports_catalog import (
        CATALOG_FIELDS,
        CDP_PROXY,
        _proxy_json,
        report_id,
        wait_until,
    )
    from extend_viewpoint_csis_rai_selected_fulltexts import browser_pdf


SERIES_ROLE = "ITIF科技创新机制与中国比较跨期精选全文"


def _item(
    published: str,
    slug: str,
    title: str,
    axes: tuple[str, ...],
    role: str,
    china: bool = False,
    pdf_url: str = "",
) -> dict[str, object]:
    landing = f"https://itif.org/publications/{published[:4]}/{published[5:7]}/{published[8:10]}/{slug}/"
    return {
        "id": report_id(published, slug), "date": published, "slug": slug, "title": title,
        "landing": landing, "markdown_url": landing.rstrip("/") + ".md", "pdf_url": pdf_url,
        "axes": axes, "role": role, "china": china,
    }


SELECTED_ITEMS = (
    _item("2016-12-07", "localizing-economic-impact-research-and-development-policy-proposals-trump", "Localizing the Economic Impact of Research and Development: Policy Proposals for the Trump Administration and Congress", ("研发治理与科研组织", "技术创新与产业转化"), "R&D地域溢出、技术转移与创新政策工具基线"),
    _item("2017-01-03", "investing-innovation-infrastructure-restore-us-growth", "Investing in “Innovation Infrastructure” to Restore U.S. Growth", ("科学体系与基础研究", "研发治理与科研组织"), "科学与工程研究作为创新基础设施的政策基线"),
    _item("2017-07-26", "across-second-valley-death-designing-successful-energy-demonstration", "Across the “Second Valley of Death”: Designing Successful Energy Demonstration Projects", ("关键与通用技术", "技术创新与产业转化"), "清洁能源示范项目、第二死亡之谷与政府组合设计"),
    _item("2018-01-08", "industry-funding-university-research-which-states-lead", "Industry Funding of University Research: Which States Lead?", ("人才大学与科研组织", "技术创新与产业转化"), "产业资助大学研究、区域技术经济活动与政策工具"),
    _item("2018-06-04", "why-us-business-rd-not-strong-it-appears", "Why U.S. Business R&D Is Not as Strong as It Appears", ("科学体系与基础研究", "技术创新与产业转化"), "企业R&D结构、基础与应用研究比重及公共支持"),
    _item("2019-09-12", "why-federal-rd-policy-needs-prioritize-productivity-drive-growth-and-reduce", "Why Federal R&D Policy Needs to Prioritize Productivity to Drive Growth and Reduce the Debt-to-GDP Ratio", ("研发治理与科研组织", "技术创新与产业转化"), "生产率导向公共R&D的目标设定与经济评价"),
    _item("2020-01-06", "innovation-drag-chinas-economic-impact-developed-nations", "Innovation Drag: China’s Economic Impact on Developed Nations", ("技术创新与产业转化", "国际合作与开放科学"), "中国经济扩张对全球创新投入、知识溢出与先进经济体创新能力的影响", True),
    _item("2020-09-08", "impact-chinas-policies-global-biopharmaceutical-industry-innovation", "The Impact of China’s Policies on Global Biopharmaceutical Industry Innovation", ("关键与通用技术", "技术创新与产业转化"), "中国生物医药政策、研发激励与全球生命科学创新的关联", True),
    _item("2020-10-05", "impact-chinas-production-surge-innovation-global-solar-photovoltaics", "The Impact of China’s Production Surge on Innovation in the Global Solar Photovoltaics Industry", ("关键与通用技术", "技术创新与产业转化"), "中国光伏制造扩张、成本下降与替代技术路径多样性的关系", True),
    _item("2020-11-02", "understanding-us-national-innovation-system-2020", "Understanding the U.S. National Innovation System, 2020", ("研发治理与科研组织", "技术创新与产业转化"), "国家创新体系结构、政策协调与国际比较", True),
    _item("2020-11-23", "chinese-competitiveness-international-digital-economy", "Chinese Competitiveness in the International Digital Economy", ("关键与通用技术", "技术创新与产业转化"), "中国数字企业创新能力、平台规模与国际竞争结构", True),
    _item("2020-12-07", "how-united-states-can-increase-access-supercomputing", "How the United States Can Increase Access to Supercomputing", ("关键与通用技术", "科学体系与基础研究"), "超级计算资源、AI研究基础设施与公共投入"),
    _item("2021-01-25", "five-free-market-myths-about-increasing-federal-research-funding", "Five Free-Market Myths About Increasing Federal Research Funding", ("科学体系与基础研究", "研发治理与科研组织"), "联邦科研资助、公私R&D分工与政策正当性"),
    _item("2021-01-25", "who-winning-ai-race-china-eu-or-united-states-2021-update", "Who Is Winning the AI Race: China, the EU, or the United States? — 2021 Update", ("关键与通用技术", "人才大学与科研组织"), "中美欧AI人才、科研、企业、硬件与应用能力比较", True),
    _item("2021-10-18", "2021-global-energy-innovation-index-national-contributions-global-clean", "The 2021 Global Energy Innovation Index: National Contributions to the Global Clean Energy Innovation System", ("关键与通用技术", "国际合作与开放科学"), "清洁能源创新系统指标、国家贡献与中国比较", True),
    _item("2022-07-19", "industry-university-partnerships-to-create-ai-universities", "Industry-University Partnerships to Create AI Universities: A Model to Spur US Innovation and Competitiveness in AI", ("人才大学与科研组织", "关键与通用技术"), "AI大学、产学合作、人才与算力设备组合"),
    _item("2022-08-02", "foundation-for-energy-security-and-innovation", "The Foundation for Energy Security and Innovation: A Flexible New Tool to Build the Economy, Strengthen Science, and Fight Climate Change", ("研发治理与科研组织", "技术创新与产业转化"), "DOE配套基金会、公私合作与能源技术转化"),
    _item("2023-07-24", "innovation-wars-how-china-is-gaining-on-the-united-states-in-corporate-rd", "Innovation Wars: How China Is Gaining on the United States in Corporate R&D", ("技术创新与产业转化", "关键与通用技术"), "中美先进产业企业R&D强度与结构比较", True),
    _item("2023-12-13", "2023-hamilton-index", "The Hamilton Index, 2023: China Is Running Away With Strategic Industries", ("技术创新与产业转化", "关键与通用技术"), "中国先进产业增加值、专业化程度与全球产业创新结构比较", True),
    _item("2024-03-13", "federal-funding-for-basic-research-spurs-clean-energy-discoveries-eight-case-studies", "How Federal Funding for Basic Research Spurs Clean Energy Discoveries the World Needs: Eight Case Studies", ("科学体系与基础研究", "关键与通用技术"), "基础研究到能源技术突破的八个机制案例"),
    _item("2025-06-30", "congress-should-fully-fund-nsf-tip-directorate", "Congress Should Fully Fund NSF’s TIP Directorate to Make America More Competitive Versus China", ("研发治理与科研组织", "技术创新与产业转化"), "NSF TIP使命导向研究、产业伙伴与中国R&D比较", True),
    _item("2025-12-15", "how-nih-funded-science-supports-us-biopharmaceutical-innovation", "How NIH-Funded Science Supports US Biopharmaceutical Innovation", ("科学体系与基础研究", "技术创新与产业转化"), "NIH资助科学、生物医药产业R&D与公私互补"),
    _item("2026-02-09", "tracking-rd-leadership-us-advantage-narrowing-as-china-gains-ground", "Tracking R&D Leadership: US Advantage Narrowing as China Gains Ground", ("技术创新与产业转化", "关键与通用技术"), "九个先进产业企业R&D与中美成本调整比较", True),
    _item("2026-07-20", "paying-for-outcomes-tying-university-funding-to-commercial-results", "Paying for Outcomes: Tying University Funding to Commercial Results", ("人才大学与科研组织", "技术创新与产业转化"), "大学资助绩效、专利企业与商业化结果激励"),
    _item("2019-08-12", "chinas-biopharmaceutical-strategy-challenge-or-complement-us-industry", "China’s Biopharmaceutical Strategy: Challenge or Complement to U.S. Industry Competitiveness?", ("关键与通用技术", "技术创新与产业转化", "国际合作与开放科学"), "中国生物医药研发、产业政策与中美创新生态互补竞争的早期节点", True),
    _item("2024-08-12", "how-experts-china-united-kingdom-view-ai-risks-collaboration", "How Experts in China and the United Kingdom View AI Risks and Collaboration", ("关键与通用技术", "人才大学与科研组织", "国际合作与开放科学"), "中英AI专家对技术风险、科研交流和国际合作条件的比较", True),
    _item("2025-03-03", "from-fast-follower-to-innovation-leader-restructuring-south-koreas-technology-regulation", "From Fast Follower to Innovation Leader: Restructuring South Korea’s Technology Regulation", ("研发治理与科研组织", "技术创新与产业转化", "国际合作与开放科学"), "韩国由技术追随转向创新引领的监管重构及中国产业竞争参照", True),
    _item("2026-05-04", "us-technology-companies-should-keep-operating-in-china", "US Technology Companies Should Keep Operating in China", ("技术创新与产业转化", "国际合作与开放科学"), "跨国科技企业在华经营与研发联系对创新、市场学习和技术生态的影响", True),
    _item("2026-06-08", "how-innovative-is-chinas-space-industry", "How Innovative Is China’s Space Industry?", ("关键与通用技术", "技术创新与产业转化"), "从科研、企业、专利和产业能力评估中国航天创新体系", True),
    _item("2026-06-29", "chinas-burgeoning-biopharmaceutical-competitiveness-demands-us-response", "China’s Burgeoning Biopharmaceutical Competitiveness Demands a US Response", ("关键与通用技术", "科学体系与基础研究", "技术创新与产业转化"), "中国生物医药科研、临床开发、企业能力和成果转化的最新比较节点", True),
    _item("2020-06-22", "how-chinas-mercantilist-policies-have-undermined-global-innovation-telecom", "How China’s Mercantilist Policies Have Undermined Global Innovation in the Telecom Equipment Industry", ("关键与通用技术", "技术创新与产业转化"), "中国电信设备企业扩张、企业R&D投入与全球技术创新反馈机制", True),
    _item("2021-04-26", "heading-track-impact-chinas-mercantilist-policies-global-high-speed-rail", "Heading Off Track: The Impact of China’s Mercantilist Policies on Global High-Speed Rail Innovation", ("关键与通用技术", "技术创新与产业转化"), "中国高铁产业政策、市场规模、企业研发与全球轨道交通创新的关系", True, "https://cdn.sanity.io/files/03hnmfyj/production/50fed126d9ea61ccdbfb7a60c6e817ec5650f772.pdf"),
    _item("2025-09-08", "china-plans-to-dominate-a-key-semiconductor-material", "China Plans to Dominate a Key Semiconductor Material", ("关键与通用技术", "技术创新与产业转化"), "半导体级多晶硅的材料能力、技术门槛、产能扩张与产业政策机制", True),
    _item("2026-06-15", "comac-chinas-looming-threat-to-global-aviation-industry", "COMAC: China’s Looming Threat to the Global Aviation Industry", ("关键与通用技术", "技术创新与产业转化"), "中国商用航空的系统集成、研发组织、适航认证与产业进入机制", True),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fetch_markdown(url: str) -> str:
    opened = _proxy_json("/new?url=" + quote(url, safe=""))
    target = str(opened["targetId"])
    try:
        wait_until(lambda: int(_proxy_json("/eval?target=" + target, "document.body?.innerText.length||0")["value"]) >= 1_000)
        text = str(_proxy_json("/eval?target=" + target, "document.body.innerText")["value"])
        if "Page not found" in text[:500]:
            raise RuntimeError(f"official markdown endpoint not found: {url}")
        return re.sub(r"\r+\n?", "\n", text).strip() + "\n"
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = ("science", "research", "innovation", "R&D", "China", "Chinese", "university", "funding", "technology", "commercial", "productivity")
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 80]
    hits = [part for part in paragraphs if any(word.lower() in part.lower() for word in keywords)][:120]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 官方页面：{item['landing']}\n"
        "- 资料类型：ITIF官方Markdown全文\n\n## 科技创新与中国定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    web_dir = root / "03_证据底稿" / "网页原文"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (web_dir, pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    catalog_path = root / "05_报告总目录.csv"
    light_path = root / "170_ITIF正式报告与简报近十年轻量总目录.csv"
    catalog = read_csv(catalog_path)
    light = read_csv(light_path)
    by_id = {row["报告ID"]: row for row in catalog}
    light_by_id = {row["报告ID"]: row for row in light}
    missing = {str(item["id"]) for item in SELECTED_ITEMS} - set(by_id)
    if missing:
        raise RuntimeError(f"selected ITIF items missing from light catalog: {sorted(missing)}")
    ledger: list[dict[str, str]] = []
    for item in SELECTED_ITEMS:
        rid = str(item["id"])
        pdf_url = str(item.get("pdf_url", ""))
        asset_type = "ITIF官方PDF全文" if pdf_url else "ITIF官方Markdown全文"
        pdf_pages = 0
        asset_path = (pdf_dir / f"{rid}.pdf") if pdf_url else (web_dir / f"{rid}.md")
        page_path = web_dir / f"{rid}.md"
        text_path = text_dir / f"{rid}.txt"
        slice_path = slice_dir / f"{rid}.md"
        if pdf_url:
            if not page_path.exists():
                page_content = fetch_markdown(str(item["markdown_url"]))
                page_path.write_text("\n".join(line.rstrip() for line in page_content.splitlines()) + "\n", encoding="utf-8", newline="\n")
            if asset_path.exists():
                payload = asset_path.read_bytes()
            else:
                opened = _proxy_json("/new?url=" + quote(str(item["landing"]), safe=""))
                target = str(opened["targetId"])
                try:
                    payload = browser_pdf(target, pdf_url)
                finally:
                    try:
                        _proxy_json("/close?target=" + target)
                    except Exception:
                        pass
                asset_path.write_bytes(payload)
            reader = PdfReader(io.BytesIO(payload))
            pdf_pages = len(reader.pages)
            content = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
            content = re.sub(r"\n{3,}", "\n\n", content).strip() + "\n"
        else:
            if asset_path.exists():
                content = asset_path.read_text(encoding="utf-8", errors="replace")
            else:
                fetched = fetch_markdown(str(item["markdown_url"]))
                content = "\n".join(line.rstrip() for line in fetched.splitlines()) + "\n"
                asset_path.write_text(content, encoding="utf-8", newline="\n")
            payload = content.encode("utf-8")
        if len(content) < 1_000:
            raise RuntimeError(f"official asset text too short: {rid} {len(content)}")
        searchable_text = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        text_path.write_text(searchable_text, encoding="utf-8", newline="\n")
        slice_path.write_text(selected_slice(item, content), encoding="utf-8", newline="\n")
        lower = content.lower()
        china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
        row = by_id[rid]
        row["本地路径"] = str(asset_path)
        row["正文完整度"] = f"{asset_type}已保存"
        row["优先级"] = "P0-China-STI-node" if item["china"] else "P1-STI-node"
        row["示踪问题"] = "；".join(item["axes"]) + ("；中国科技横向维度" if item["china"] else "")
        row["样本角色"] = SERIES_ROLE
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = str(item["role"])
        row["本地原始资产路径"] = str(asset_path)
        status_asset_type = "ITIF官方PDF全文" if pdf_url else "ITIF官方Markdown"
        row["原始资产状态"] = f"{status_asset_type}原始资产已获取；已生成文本与科技创新定向切片"
        if rid in light_by_id:
            light_by_id[rid]["中国直接信号"] = "是" if item["china"] else light_by_id[rid]["中国直接信号"]
            light_by_id[rid]["全文策略"] = "已进入精选全文；按本地原始资产、文本和切片调用"
        ledger.append({
            "报告ID": rid, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
            "官方落地页": str(item["landing"]), "官方原始资产入口": pdf_url or str(item["markdown_url"]),
            "本地原始资产": str(asset_path), "本地文本": str(text_path), "本地切片": str(slice_path),
            "本地页面概要": str(page_path) if pdf_url else "",
            "资产类型": asset_type, "PDF页数": str(pdf_pages),
            "字节数": str(len(payload)), "字符数": str(len(content)), "China词形命中数": str(china_hits),
            "SHA256": hashlib.sha256(payload).hexdigest(), "中国直接信号": "是" if item["china"] else "否",
            "科技创新主轴": "；".join(item["axes"]), "科技创新复用角色": str(item["role"]),
            "选择理由": "跨期节点；直接解释科学技术创新机制；相对既有ITIF全文具有证据增量", "获取日期": date.today().isoformat(),
        })
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    for row in catalog:
        if row.get("机构ID") == "itif" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            marker = "ITIF跨期精选已完成；其余正式报告保留轻量目录"
            if marker not in row.get("原始资产状态", ""):
                row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(light_path, light, list(light[0]))
    write_csv(root / "172_ITIF科技创新机制与中国比较跨期精选全文台账.csv", ledger, list(ledger[0]))
    totals = {
        "bytes": sum(int(row["字节数"]) for row in ledger), "chars": sum(int(row["字符数"]) for row in ledger),
        "china": sum(int(row["China词形命中数"]) for row in ledger), "direct": sum(row["中国直接信号"] == "是" for row in ledger),
    }
    (root / "173_ITIF科技创新机制与中国比较跨期精选全文结果.md").write_text(
        "# ITIF科技创新机制与中国比较跨期精选全文结果\n\n"
        f"- 从669项近十年正式报告轻量目录中精选保存{len(ledger)}项ITIF官方原始资产，其中Markdown全文{sum(not item.get('pdf_url') for item in SELECTED_ITEMS)}项、PDF全文{sum(bool(item.get('pdf_url')) for item in SELECTED_ITEMS)}项、PDF {sum(int(row['PDF页数']) for row in ledger)}页，共{totals['bytes']:,}字节、{totals['chars']:,}字符。\n"
        f"- 直接中国比较材料{totals['direct']}项，China/Chinese/PRC词形命中{totals['china']}次；中国维度覆盖国家创新体系、AI能力、清洁能源、生物医药、数字经济、先进产业与企业R&D。\n"
        "- 跨期机制主线覆盖创新基础设施、R&D溢出、技术示范、产学合作、国家创新体系、科研资助、算力设施、大学商业化、生物医药公私R&D，以及规模扩张对全球创新路径的影响。\n"
        "- 安全、反垄断、隐私和一般贸易材料未进入本批精选；其题名与摘要继续保留于轻量总目录。\n",
        encoding="utf-8",
    )
    print(f"assets={len(ledger)} bytes={totals['bytes']} chars={totals['chars']} direct_china={totals['direct']} china_hits={totals['china']} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
