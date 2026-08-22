from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

try:
    from scripts.extract_viewpoint_pdf_slices import process_pdf
except ModuleNotFoundError:
    from extract_viewpoint_pdf_slices import process_pdf

try:
    from scripts.extend_viewpoint_ifp_light_catalog import CATALOG_FIELDS, report_id
except ModuleNotFoundError:
    from extend_viewpoint_ifp_light_catalog import CATALOG_FIELDS, report_id


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"
SERIES_ROLE = "IFP科技创新机制与中国比较精选全文"


def _item(published, slug, title, axes, role, china=False, asset_type="WEB", asset_url=""):
    return {
        "id": report_id(published, slug), "date": published, "slug": slug, "title": title,
        "landing": f"https://ifp.org/{slug}/", "asset_url": asset_url or f"https://ifp.org/{slug}/",
        "asset_type": asset_type, "axes": tuple(axes), "role": role, "china": china,
    }


SELECTED_ITEMS = (
    _item("2022-01-19", "fund-organizations-not-projects-diversifying-americas-innovation-ecosystem-with-a-portfolio-of-independent-research-organizations", "Fund Organizations, Not Projects: Diversifying America’s Innovation Ecosystem with a Portfolio of Independent Research Organizations", ("科学体系与基础研究", "研发治理与科研组织"), "独立聚焦研究组织、组织型资助与高风险研究组合"),
    _item("2022-02-02", "piloting-and-evaluating-nsf-science-lottery-grants", "Piloting and Evaluating NSF Science Lottery Grants: A Roadmap to Improving Research Funding Efficiencies and Proposal Diversity", ("科学体系与基础研究", "研发治理与科研组织"), "科研评审随机化、资助效率与提案多样性", False, "PDF", "https://ifp.org/wp-content/uploads/Formatted-Lottery-Text.pdf"),
    _item("2022-05-10", "semiconductor-investments-wont-pay-off-if-congress-doesnt-fix-the-talent-bottleneck", "Semiconductor Investments Won’t Pay Off If Congress Doesn’t Fix the Talent Bottleneck", ("关键与通用技术", "人才大学与科研组织"), "半导体产业能力、全球人才流动与中美技术竞争", True),
    _item("2022-11-30", "how-do-we-make-an-entrepreneurial-state", "But Seriously, How Do We Make an Entrepreneurial State?", ("研发治理与科研组织", "技术创新与产业转化"), "任务型机构、公共创业能力与创新政策执行", True),
    _item("2023-05-17", "building-a-better-nih", "Building a Better NIH", ("科学体系与基础研究", "研发治理与科研组织"), "生物医学科研资助机构改革与科学公共价值"),
    _item("2023-09-11", "to-speed-up-scientific-progress-we-need-to-understand-science-policy", "To Speed Up Scientific Progress, We Need to Understand Science Policy", ("科学体系与基础研究", "研发治理与科研组织"), "元科学证据、科研政策试验与知识转译"),
    _item("2023-10-20", "where-can-federal-ai-rd-funding-go-the-furthest", "Where Can Federal AI R&D Funding Go the Furthest?", ("关键与通用技术", "研发治理与科研组织"), "公共AI研发投入方向、市场失灵与能力建设", True),
    _item("2024-06-10", "compute-in-america", "Compute in America: Building the Next Generation of AI Infrastructure at Home", ("关键与通用技术", "技术创新与产业转化"), "AI算力基础设施、产业能力与中美比较", True),
    _item("2024-06-18", "nist-foundation", "The Case for a NIST Foundation", ("研发治理与科研组织", "技术创新与产业转化"), "国家计量标准机构、公私合作与技术商业化", True),
    _item("2024-12-02", "maximizing-the-scientific-roi-from-international-phds", "Maximizing the Scientific ROI from International PhDs", ("人才大学与科研组织", "开放科学与国际合作"), "国际博士人才、科研生产率与中美人才比较", True),
    _item("2025-06-03", "catalyzing-a-golden-age", "Catalyzing a Golden Age: A Blueprint for Strategic AI R&D Investment", ("关键与通用技术", "研发治理与科研组织"), "战略AI研发投资、公共研发组合与技术能力", True),
    _item("2025-07-24", "indirect-cost-recovery-and-american-innovation", "Indirect Cost Recovery and American Innovation: Context and Ideas for Reform", ("科学体系与基础研究", "研发治理与科研组织"), "大学间接成本、科研组织激励与创新产出"),
    _item("2025-08-11", "scaling-materials-discovery-with-self-driving-labs", "Scaling Materials Discovery with Self-Driving Labs", ("关键与通用技术", "技术创新与产业转化"), "AI驱动材料发现、自主实验室与转化基础设施"),
    _item("2025-08-29", "american-science-should-take-a-lot-more-risks", "American Science Should Take a Lot More Risks", ("科学体系与基础研究", "研发治理与科研组织"), "高风险高回报研究、资助组合与科学突破"),
    _item("2026-07-23", "science-agencies-need-metascience-units", "Science Agencies Need Metascience Units", ("科学体系与基础研究", "研发治理与科研组织"), "科研机构内部元科学单元、政策试验与项目设计"),
    _item("2026-08-06", "preparing-for-ai-research-automation", "How Should the US Prepare for Increasingly Automated AI R&D?", ("关键与通用技术", "科学体系与基础研究"), "自动化AI研发、科学能力、算力与政策准备", True),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fetch(url: str) -> bytes:
    response = httpx.get(url, follow_redirects=True, timeout=600, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.content


def normalize_generated_file(path: Path) -> None:
    current = path.read_text(encoding="utf-8", errors="replace")
    normalized = re.sub(r"\r+\n?", "\n", current)
    if normalized != current:
        path.write_text(normalized, encoding="utf-8", newline="\n")


def web_text(source_html: str) -> str:
    soup = BeautifulSoup(source_html, "html.parser")
    main = soup.select_one("main") or soup.select_one("article") or soup
    for node in main.select("nav, footer, script, style, form, picture, svg, aside"):
        node.decompose()
    lines = [re.sub(r"\s+", " ", line).strip() for line in main.get_text("\n").splitlines()]
    return "\n".join(line for line in lines if line)


def web_slice(item: dict[str, object], text: str) -> str:
    keywords = ("science", "research", "innovation", "R&D", "China", "Chinese", "talent", "funding", "technology", "compute")
    paragraphs = [line for line in text.splitlines() if len(line) >= 70]
    hits = [line for line in paragraphs if any(word.lower() in line.lower() for word in keywords)][:100]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 官方页面：{item['landing']}\n"
        "- 资料类型：IFP官方网页全文\n\n## 科技创新与中国定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def mark_selected_light_rows(rows: list[dict[str, str]]) -> None:
    selected = {str(item["id"]): item for item in SELECTED_ITEMS}
    for row in rows:
        item = selected.get(row.get("报告ID", ""))
        if item:
            row["中国关联"] = "是" if item["china"] else row.get("中国关联", "否")
            row["全文策略"] = "已进入精选全文；按本地原始资产、文本和切片调用"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    web_dir = root / "03_证据底稿" / "网页原文"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, web_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    by_id = {row["报告ID"]: row for row in catalog}
    light_path = root / "166_IFP科技创新正式成果轻量总目录.csv"
    light_rows = read_csv(light_path)
    missing = {item["id"] for item in SELECTED_ITEMS} - set(by_id)
    if missing:
        raise RuntimeError(f"selected IFP items missing from light catalog: {sorted(missing)}")
    ledger: list[dict[str, str]] = []
    for item in SELECTED_ITEMS:
        report_id_value = str(item["id"])
        text_path = text_dir / f"{report_id_value}.txt"
        slice_path = slice_dir / f"{report_id_value}.md"
        if item["asset_type"] == "PDF":
            asset_path = pdf_dir / f"{report_id_value}.pdf"
            data = asset_path.read_bytes() if asset_path.exists() else fetch(str(item["asset_url"]))
            if not data.startswith(b"%PDF"):
                raise RuntimeError(f"official attachment is not a PDF: {item['asset_url']}")
            if not asset_path.exists():
                asset_path.write_bytes(data)
            if not text_path.exists() or not slice_path.exists():
                process_pdf(asset_path, text_dir, slice_dir)
            normalize_generated_file(text_path)
            normalize_generated_file(slice_path)
            pages = len(PdfReader(asset_path).pages)
        else:
            asset_path = web_dir / f"{report_id_value}.html"
            data = asset_path.read_bytes() if asset_path.exists() else fetch(str(item["asset_url"]))
            if not asset_path.exists():
                asset_path.write_bytes(data)
            extracted = web_text(data.decode("utf-8", errors="replace"))
            text_path.write_text(extracted, encoding="utf-8", newline="\n")
            slice_path.write_text(web_slice(item, extracted), encoding="utf-8", newline="\n")
            pages = 0
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        if len(extracted) < 1_000:
            raise RuntimeError(f"extracted text too short: {report_id_value} {len(extracted)}")
        lower = extracted.lower()
        china_hits = lower.count("china") + lower.count("chinese") + lower.count("deepseek")
        row = by_id[report_id_value]
        row["本地路径"] = str(asset_path)
        row["正文完整度"] = "官方PDF全文已保存" if item["asset_type"] == "PDF" else "官方网页全文已保存"
        row["优先级"] = "P0-China-STI-node" if item["china"] else "P1-STI-node"
        row["样本角色"] = SERIES_ROLE
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = str(item["role"])
        row["本地原始资产路径"] = str(asset_path)
        row["原始资产状态"] = "IFP官方原始资产已获取；已生成文本与科技创新定向切片"
        ledger.append({
            "报告ID": report_id_value, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
            "官方落地页": str(item["landing"]), "原始资产类型": str(item["asset_type"]), "官方资产": str(item["asset_url"]),
            "本地原始资产": str(asset_path), "本地文本": str(text_path), "本地切片": str(slice_path),
            "PDF页数": str(pages), "字节数": str(len(data)), "提取文本字符数": str(len(extracted)),
            "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(data).hexdigest(),
            "中国关联": "是" if item["china"] else "否", "科技创新主轴": "；".join(item["axes"]),
            "科技创新复用角色": str(item["role"]), "选择理由": "新型科技政策智库进入节点；直接解释科学技术创新机制；相对既有全文具有证据增量",
            "获取日期": date.today().isoformat(),
        })
    selected_ids = {item["id"] for item in SELECTED_ITEMS}
    for row in catalog:
        if row.get("机构ID") == "ifp" and row.get("报告ID") not in selected_ids:
            marker = "机构精选已完成；其余正式成果保留轻量目录"
            if marker not in row.get("原始资产状态", ""):
                row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    mark_selected_light_rows(light_rows)
    write_csv(light_path, light_rows, list(light_rows[0]))
    write_csv(root / "168_IFP科技创新机制与中国比较精选全文台账.csv", ledger, list(ledger[0]))
    totals = {
        "pages": sum(int(row["PDF页数"]) for row in ledger), "bytes": sum(int(row["字节数"]) for row in ledger),
        "chars": sum(int(row["提取文本字符数"]) for row in ledger), "china": sum(int(row["China词形命中数"]) for row in ledger),
    }
    (root / "169_IFP科技创新机制与中国比较精选全文结果.md").write_text(
        "# IFP科技创新机制与中国比较精选全文结果\n\n"
        f"- 从155项轻量目录中保存{len(ledger)}项官方原始资产，其中1份PDF、15份官方网页全文，共{totals['pages']}页、{totals['bytes']:,}字节、{totals['chars']:,}字符。\n"
        f"- China/Chinese/DeepSeek词形命中{totals['china']}次；中国维度服务于半导体、科研人才、AI研发、算力、材料发现与科技能力比较。\n"
        "- 机制主线覆盖组织型科研资助、评审试验、公共创业机构、NIH与NIST改革、AI研发投入、科研间接成本、自动化实验和元科学单元。\n"
        "- IFP自2022年形成当前出版序列，本批只能作为新型科技政策智库进入与近期议程样本，不用于推断十年机构内转向。\n"
        "- AI安全、出口管制和生物安全材料只在直接解释研发能力、人才、算力或产业创新时进入目录；安全主导材料未进入精选全文。\n",
        encoding="utf-8",
    )
    print(f"assets={len(ledger)} pdfs=1 web=15 pages={totals['pages']} bytes={totals['bytes']} chars={totals['chars']} china_hits={totals['china']} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
