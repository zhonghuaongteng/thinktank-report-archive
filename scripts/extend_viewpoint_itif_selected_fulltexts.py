from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

try:
    from scripts.extend_viewpoint_itif_reports_catalog import (
        CATALOG_FIELDS,
        CDP_PROXY,
        _proxy_json,
        report_id,
        wait_until,
    )
except ModuleNotFoundError:
    from extend_viewpoint_itif_reports_catalog import (
        CATALOG_FIELDS,
        CDP_PROXY,
        _proxy_json,
        report_id,
        wait_until,
    )


SERIES_ROLE = "ITIF科技创新机制与中国比较跨期精选全文"


def _item(published: str, slug: str, title: str, axes: tuple[str, ...], role: str, china: bool = False) -> dict[str, object]:
    landing = f"https://itif.org/publications/{published[:4]}/{published[5:7]}/{published[8:10]}/{slug}/"
    return {
        "id": report_id(published, slug), "date": published, "slug": slug, "title": title,
        "landing": landing, "markdown_url": landing.rstrip("/") + ".md", "axes": axes, "role": role, "china": china,
    }


SELECTED_ITEMS = (
    _item("2016-12-07", "localizing-economic-impact-research-and-development-policy-proposals-trump", "Localizing the Economic Impact of Research and Development: Policy Proposals for the Trump Administration and Congress", ("研发治理与科研组织", "技术创新与产业转化"), "R&D地域溢出、技术转移与创新政策工具基线"),
    _item("2017-01-03", "investing-innovation-infrastructure-restore-us-growth", "Investing in “Innovation Infrastructure” to Restore U.S. Growth", ("科学体系与基础研究", "研发治理与科研组织"), "科学与工程研究作为创新基础设施的政策基线"),
    _item("2017-07-26", "across-second-valley-death-designing-successful-energy-demonstration", "Across the “Second Valley of Death”: Designing Successful Energy Demonstration Projects", ("关键与通用技术", "技术创新与产业转化"), "清洁能源示范项目、第二死亡之谷与政府组合设计"),
    _item("2018-01-08", "industry-funding-university-research-which-states-lead", "Industry Funding of University Research: Which States Lead?", ("人才大学与科研组织", "技术创新与产业转化"), "产业资助大学研究、区域技术经济活动与政策工具"),
    _item("2018-06-04", "why-us-business-rd-not-strong-it-appears", "Why U.S. Business R&D Is Not as Strong as It Appears", ("科学体系与基础研究", "技术创新与产业转化"), "企业R&D结构、基础与应用研究比重及公共支持"),
    _item("2019-09-12", "why-federal-rd-policy-needs-prioritize-productivity-drive-growth-and-reduce", "Why Federal R&D Policy Needs to Prioritize Productivity to Drive Growth and Reduce the Debt-to-GDP Ratio", ("研发治理与科研组织", "技术创新与产业转化"), "生产率导向公共R&D的目标设定与经济评价"),
    _item("2020-11-02", "understanding-us-national-innovation-system-2020", "Understanding the U.S. National Innovation System, 2020", ("研发治理与科研组织", "技术创新与产业转化"), "国家创新体系结构、政策协调与国际比较", True),
    _item("2020-12-07", "how-united-states-can-increase-access-supercomputing", "How the United States Can Increase Access to Supercomputing", ("关键与通用技术", "科学体系与基础研究"), "超级计算资源、AI研究基础设施与公共投入"),
    _item("2021-01-25", "five-free-market-myths-about-increasing-federal-research-funding", "Five Free-Market Myths About Increasing Federal Research Funding", ("科学体系与基础研究", "研发治理与科研组织"), "联邦科研资助、公私R&D分工与政策正当性"),
    _item("2021-10-18", "2021-global-energy-innovation-index-national-contributions-global-clean", "The 2021 Global Energy Innovation Index: National Contributions to the Global Clean Energy Innovation System", ("关键与通用技术", "国际合作与开放科学"), "清洁能源创新系统指标、国家贡献与中国比较", True),
    _item("2022-07-19", "industry-university-partnerships-to-create-ai-universities", "Industry-University Partnerships to Create AI Universities: A Model to Spur US Innovation and Competitiveness in AI", ("人才大学与科研组织", "关键与通用技术"), "AI大学、产学合作、人才与算力设备组合"),
    _item("2022-08-02", "foundation-for-energy-security-and-innovation", "The Foundation for Energy Security and Innovation: A Flexible New Tool to Build the Economy, Strengthen Science, and Fight Climate Change", ("研发治理与科研组织", "技术创新与产业转化"), "DOE配套基金会、公私合作与能源技术转化"),
    _item("2023-07-24", "innovation-wars-how-china-is-gaining-on-the-united-states-in-corporate-rd", "Innovation Wars: How China Is Gaining on the United States in Corporate R&D", ("技术创新与产业转化", "关键与通用技术"), "中美先进产业企业R&D强度与结构比较", True),
    _item("2024-03-13", "federal-funding-for-basic-research-spurs-clean-energy-discoveries-eight-case-studies", "How Federal Funding for Basic Research Spurs Clean Energy Discoveries the World Needs: Eight Case Studies", ("科学体系与基础研究", "关键与通用技术"), "基础研究到能源技术突破的八个机制案例"),
    _item("2025-06-30", "congress-should-fully-fund-nsf-tip-directorate", "Congress Should Fully Fund NSF’s TIP Directorate to Make America More Competitive Versus China", ("研发治理与科研组织", "技术创新与产业转化"), "NSF TIP使命导向研究、产业伙伴与中国R&D比较", True),
    _item("2025-12-15", "how-nih-funded-science-supports-us-biopharmaceutical-innovation", "How NIH-Funded Science Supports US Biopharmaceutical Innovation", ("科学体系与基础研究", "技术创新与产业转化"), "NIH资助科学、生物医药产业R&D与公私互补"),
    _item("2026-02-09", "tracking-rd-leadership-us-advantage-narrowing-as-china-gains-ground", "Tracking R&D Leadership: US Advantage Narrowing as China Gains Ground", ("技术创新与产业转化", "关键与通用技术"), "九个先进产业企业R&D与中美成本调整比较", True),
    _item("2026-07-20", "paying-for-outcomes-tying-university-funding-to-commercial-results", "Paying for Outcomes: Tying University Funding to Commercial Results", ("人才大学与科研组织", "技术创新与产业转化"), "大学资助绩效、专利企业与商业化结果激励"),
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
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (web_dir, text_dir, slice_dir):
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
        asset_path = web_dir / f"{rid}.md"
        text_path = text_dir / f"{rid}.txt"
        slice_path = slice_dir / f"{rid}.md"
        content = asset_path.read_text(encoding="utf-8", errors="replace") if asset_path.exists() else fetch_markdown(str(item["markdown_url"]))
        if len(content) < 1_000:
            raise RuntimeError(f"official markdown too short: {rid} {len(content)}")
        if not asset_path.exists():
            asset_path.write_text(content, encoding="utf-8", newline="\n")
        searchable_text = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        text_path.write_text(searchable_text, encoding="utf-8", newline="\n")
        slice_path.write_text(selected_slice(item, content), encoding="utf-8", newline="\n")
        payload = content.encode("utf-8")
        lower = content.lower()
        china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
        row = by_id[rid]
        row["本地路径"] = str(asset_path)
        row["正文完整度"] = "ITIF官方Markdown全文已保存"
        row["优先级"] = "P0-China-STI-node" if item["china"] else "P1-STI-node"
        row["样本角色"] = SERIES_ROLE
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = str(item["role"])
        row["本地原始资产路径"] = str(asset_path)
        row["原始资产状态"] = "ITIF官方Markdown原始资产已获取；已生成文本与科技创新定向切片"
        if rid in light_by_id:
            light_by_id[rid]["中国直接信号"] = "是" if item["china"] else light_by_id[rid]["中国直接信号"]
            light_by_id[rid]["全文策略"] = "已进入精选全文；按本地原始资产、文本和切片调用"
        ledger.append({
            "报告ID": rid, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
            "官方落地页": str(item["landing"]), "官方Markdown入口": str(item["markdown_url"]),
            "本地原始资产": str(asset_path), "本地文本": str(text_path), "本地切片": str(slice_path),
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
        f"- 从669项近十年正式报告轻量目录中新增保存{len(ledger)}项ITIF官方Markdown全文，共{totals['bytes']:,}字节、{totals['chars']:,}字符。\n"
        f"- 直接中国比较材料{totals['direct']}项，China/Chinese/PRC词形命中{totals['china']}次；中国维度主要用于国家创新体系、清洁能源创新、企业R&D和NSF TIP比较。\n"
        "- 跨期机制主线覆盖创新基础设施、R&D溢出、技术示范、产学合作、国家创新体系、科研资助、算力设施、大学商业化和生物医药公私R&D。\n"
        "- 安全、反垄断、隐私和一般贸易材料未进入本批精选；其题名与摘要继续保留于轻量总目录。\n",
        encoding="utf-8",
    )
    print(f"assets={len(ledger)} bytes={totals['bytes']} chars={totals['chars']} direct_china={totals['direct']} china_hits={totals['china']} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
