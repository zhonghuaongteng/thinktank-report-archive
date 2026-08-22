from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import httpx
from pypdf import PdfReader

try:
    from scripts.extract_viewpoint_pdf_slices import process_pdf
except ModuleNotFoundError:  # direct script execution
    from extract_viewpoint_pdf_slices import process_pdf


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
SERIES_ROLE = "Nesta科技创新与中国比较跨期精选全文"


@dataclass(frozen=True)
class SelectedItem:
    report_id: str
    published: str
    title: str
    landing: str
    pdf_url: str
    reuse_role: str
    china_focus: bool = False

    @property
    def year(self) -> int:
        return int(self.published[:4])


ITEMS = (
    SelectedItem(
        "C-NESTA-2016-MADE-IN-CHINA-MAKERSPACES-AND-THE-SEARCH-FOR-MASS-INNOVATION",
        "2016-03-29", "Made in China: Makerspaces and the search for mass innovation",
        "https://www.nesta.org.uk/report/made-in-china-makerspaces-and-the-search-for-mass-innovation/",
        "https://www.nesta.org.uk/documents/487/made_in_china-_makerspaces_report.pdf",
        "中国创客空间、制造转型、大学企业连接与大众创新载体", True,
    ),
    SelectedItem(
        "C-NESTA-2016-INNOVATION-ANALYTICS-A-GUIDE-TO-NEW-DATA-AND-MEASUREMENT-IN-INNOVATION-P",
        "2016-04-15", "Innovation Analytics: A guide to new data and measurement in innovation policy",
        "https://www.nesta.org.uk/report/innovation-analytics-a-guide-to-new-data-and-measurement-in-innovation-policy/",
        "https://www.nesta.org.uk/documents/489/innovation_analytics_report.pdf",
        "创新政策测量、数据方法、机器学习与新产业识别",
    ),
    SelectedItem(
        "C-NESTA-2016-HOW-INNOVATION-AGENCIES-WORK", "2016-05-23", "How innovation agencies work",
        "https://www.nesta.org.uk/report/how-innovation-agencies-work/",
        "https://www.nesta.org.uk/documents/496/how_innovation_agencies_work.pdf",
        "创新政策机构设计、研发与技术项目组合、组织能力和政策评估",
    ),
    SelectedItem(
        "C-NESTA-2017-NESTA-RESPONSE-TO-BUILDING-OUR-INDUSTRIAL-STRATEGY-GREEN-PAPER-2017",
        "2017-11-20", "Nesta response to 'Building our Industrial Strategy' green paper 2017",
        "https://www.nesta.org.uk/report/nesta-response-to-building-our-industrial-strategy-green-paper-2017/",
        "https://www.nesta.org.uk/documents/595/nesta_response_to_industrial_strategy_green_paper_2017_1_1_0.pdf",
        "研发投入、技术人才、创新采购、前瞻监管与区域创新转化",
    ),
    SelectedItem(
        "C-NESTA-2018-SCIENCE-OF-USING-SCIENCE-LEARNING-REPORT", "2018-11-07",
        "Science of Using Science Learning Report",
        "https://www.nesta.org.uk/report/science-of-using-science-learning-report/",
        "https://www.nesta.org.uk/documents/2378/Alliance-Science-of-using-Science-Learning-Report.pdf",
        "科学证据进入政策过程的组织机制、知识中介与科学传播",
    ),
    SelectedItem(
        "C-NESTA-2019-INVISIBLE-DRAG-CORPORATE-INCENTIVES", "2019-08-07",
        "The Invisible Drag on UK R&D: How corporate incentives within the FTSE 350 inhibit innovation",
        "https://www.nesta.org.uk/report/invisible-drag-corporate-incentives/",
        "https://www.nesta.org.uk/documents/1485/The_invisible_drag_on_UK_RD_22.08.2019.pdf",
        "企业治理激励、研发投入不足、长期技术创新与资本市场约束",
    ),
    SelectedItem(
        "C-NESTA-2019-SEMANTIC-ANALYSIS-RECENT-EVOLUTION-AI-RESEARCH", "2019-11-15",
        "A Semantic Analysis of the Recent Evolution of AI Research",
        "https://www.nesta.org.uk/report/semantic-analysis-recent-evolution-ai-research/",
        "https://www.nesta.org.uk/documents/1643/A_Semantic_Analysis_of_the_Recent_Evolution_of_AI_Research.pdf",
        "AI科学研究主题演化、机器学习文本分析与技术前沿识别",
    ),
    SelectedItem(
        "C-NESTA-2020-INNOVATING-UK-INNOVATION-POLICY", "2020-01-22", "Innovating UK Innovation Policy",
        "https://www.nesta.org.uk/report/innovating-uk-innovation-policy/",
        "https://www.nesta.org.uk/documents/1723/Innovating_UK_Innovation_Policy.pdf",
        "ARPA型高风险研发资助、使命导向创新政策与区域技术转化",
    ),
    SelectedItem(
        "C-NESTA-2020-INTRODUCING-AI-POWERED-STATE", "2020-05-18", "Introducing the AI Powered State",
        "https://www.nesta.org.uk/report/introducing-ai-powered-state/",
        "https://www.nesta.org.uk/documents/1860/Nesta_TheAIPoweredState_2020.pdf",
        "中国AI研发、地方创新生态、技术应用扩散和公共服务规模化", True,
    ),
    SelectedItem(
        "C-NESTA-2026-HDRS-DIGITAL-ECOSYSTEM-ANALYSIS", "2026-05-19",
        "Health Data Research Service (HDRS) digital ecosystem analysis",
        "https://www.nesta.org.uk/report/hdrs-digital-ecosystem-analysis/",
        "https://www.nesta.org.uk/documents/3466/Health_Data_Research_Service_HDRS_Digital_Ecosystem_Analysis_-_Final_Report_iqW8Omo.pdf",
        "健康数据科研基础设施、技术标准、研究访问、临床试验与成果转化",
    ),
)


def expected_nesta_selected_ids() -> set[str]:
    return {item.report_id for item in ITEMS}


def related_report_ids_for_pdf(rows: list[dict[str, str]], pdf_url: str) -> set[str]:
    canonical = pdf_url.strip().lower()
    return {
        row["报告ID"]
        for row in rows
        if canonical in {part.strip().lower() for part in row.get("官方PDF入口", "").split("；") if part.strip()}
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalize_generated_file(path: Path) -> None:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        current = handle.read()
    normalized = re.sub(r"\r+\n?", "\n", current)
    if normalized != current:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(normalized)


def fetch_pdf(url: str) -> bytes:
    response = httpx.get(url, follow_redirects=True, timeout=600, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    data = response.content
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"official attachment is not a PDF: {url}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    by_id = {row["报告ID"]: row for row in catalog}
    light_ledger = read_csv(root / "158_Nesta科技创新报告近十年轻量目录.csv")
    missing = expected_nesta_selected_ids() - set(by_id)
    if missing:
        raise RuntimeError(f"selected Nesta reports missing from light catalog: {sorted(missing)}")

    ledger: list[dict[str, str]] = []
    today = date.today().isoformat()
    for item in ITEMS:
        pdf_path = pdf_dir / f"{item.report_id}.pdf"
        text_path = text_dir / f"{item.report_id}.txt"
        slice_path = slice_dir / f"{item.report_id}.md"
        if pdf_path.exists():
            data = pdf_path.read_bytes()
        else:
            data = fetch_pdf(item.pdf_url)
            part_path = pdf_path.with_suffix(".pdf.part")
            part_path.write_bytes(data)
            part_path.replace(pdf_path)
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"local asset is not a PDF: {pdf_path}")
        if not text_path.exists() or not slice_path.exists():
            process_pdf(pdf_path, text_dir, slice_dir)
        normalize_generated_file(text_path)
        normalize_generated_file(slice_path)
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        if len(extracted) < 2_000:
            raise RuntimeError(f"extracted text too short: {item.report_id} {len(extracted)}")
        pages = len(PdfReader(pdf_path).pages)
        lower = extracted.lower()
        china_hits = lower.count("china") + lower.count("chinese")
        row = by_id[item.report_id]
        row["本地路径"] = str(pdf_path)
        row["正文完整度"] = "官方PDF全文已保存"
        row["优先级"] = "P0-China-STI-node" if item.china_focus else "P1-STI-node"
        row["样本角色"] = SERIES_ROLE
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = item.reuse_role
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "Nesta官方主报告PDF已获取；已生成逐页文本与科技创新定向切片"
        for related_id in related_report_ids_for_pdf(light_ledger, item.pdf_url):
            related = by_id.get(related_id)
            if not related or related_id == item.report_id:
                continue
            related["本地路径"] = str(pdf_path)
            related["正文完整度"] = "官方合集PDF全文已保存（共享附件）"
            related["本地原始资产路径"] = str(pdf_path)
            related["原始资产状态"] = "Nesta官方合集PDF已获取；本条为合集章节入口；共享全文、文本与切片"
        ledger.append({
            "报告ID": item.report_id,
            "发布日期": item.published,
            "报告名称": item.title,
            "官方落地页": item.landing,
            "官方PDF": item.pdf_url,
            "本地PDF": str(pdf_path),
            "本地文本": str(text_path),
            "本地切片": str(slice_path),
            "PDF页数": str(pages),
            "字节数": str(len(data)),
            "提取文本字符数": str(len(extracted)),
            "China词形命中数": str(china_hits),
            "SHA256": hashlib.sha256(data).hexdigest(),
            "中国关联": "是" if item.china_focus else "否",
            "科技创新复用角色": item.reuse_role,
            "选择理由": "跨期节点；直接解释科学技术创新机制；相对既有全文具有证据增量",
            "获取日期": today,
        })

    for row in catalog:
        if row.get("机构ID") != "nesta" or row.get("报告ID") in expected_nesta_selected_ids():
            continue
        marker = "机构跨期精选已完成；低增量节点保留轻量目录"
        if marker not in row.get("原始资产状态", ""):
            row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "160_Nesta科技创新与中国比较跨期精选全文台账.csv", ledger, list(ledger[0]))
    total_pages = sum(int(row["PDF页数"]) for row in ledger)
    total_bytes = sum(int(row["字节数"]) for row in ledger)
    total_chars = sum(int(row["提取文本字符数"]) for row in ledger)
    total_china_hits = sum(int(row["China词形命中数"]) for row in ledger)
    (root / "161_Nesta科技创新与中国比较跨期精选全文结果.md").write_text(
        "# Nesta科技创新与中国比较跨期精选全文结果\n\n"
        f"- 从{len(read_csv(root / '158_Nesta科技创新报告近十年轻量目录.csv'))}项轻量目录中定点保存{len(ledger)}份官方主报告PDF，"
        f"共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次；其中两份以中国科技创新机制为直接研究对象。\n"
        "- 2016—2020节点覆盖创新机构、创新测量、产业战略、科学证据使用、企业研发激励、AI研究演化、ARPA型资助及中国AI和创客生态。\n"
        "- 2026节点补充健康数据科研基础设施、研究访问、技术标准、临床试验与成果转化。\n"
        "- 2021—2025年Nesta公开报告重心明显转向社会使命和具体公共服务应用；缺少与早期创新政策主线等价的年度旗舰报告，故保留轻量目录而未为时间连续性下载低增量全文。\n"
        "- 安全、韧性、供应链与一般治理表述不构成全文选择理由。\n\n"
        "本批适合用于分析Nesta从创新系统与政策工具研究，向使命驱动、技术应用和科研基础设施实践转移的机构轨迹。\n",
        encoding="utf-8",
    )
    print(
        f"fulltexts={len(ledger)} pages={total_pages} bytes={total_bytes} chars={total_chars} "
        f"china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
