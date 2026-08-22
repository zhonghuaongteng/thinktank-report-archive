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
except ModuleNotFoundError:  # direct execution via python scripts/<name>.py
    from extract_viewpoint_pdf_slices import process_pdf


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
THEMES = "科学体系与基础研究；技术创新与关键技术；创新政策与研发治理；人才大学与科研组织；产业创新转化与区域生态；国际合作开放科学与比较；中国科技横向维度"
SERIES_ROLE = "NSF/NSB科学体系人才转化专题序列"


@dataclass(frozen=True)
class SeriesItem:
    cycle: int
    published: str
    topic: str
    publication_code: str
    title: str
    id_suffix: str
    reuse_role: str

    @property
    def report_id(self) -> str:
        return f"C-NSF-NSB-{self.id_suffix}-{self.cycle}"

    @property
    def landing(self) -> str:
        return f"https://ncses.nsf.gov/pubs/{self.publication_code}"

    @property
    def pdf_url(self) -> str:
        return f"{self.landing}/assets/{self.publication_code}.pdf"


ITEMS = (
    SeriesItem(2020, "2020-01-15", "Academic R&D", "nsb20202", "Academic Research and Development", "ARD", "大学基础研究投入、资助结构、科研设施、研究人才与国际比较"),
    SeriesItem(2022, "2021-09-14", "Academic R&D", "nsb20213", "Academic Research and Development", "ARD", "大学基础研究投入、资助结构、科研设施、研究人才与国际比较"),
    SeriesItem(2024, "2023-10-05", "Academic R&D", "nsb202326", "Academic Research and Development", "ARD", "大学基础研究投入、资助结构、科研设施、研究人才与国际比较"),
    SeriesItem(2020, "2019-09-26", "STEM Workforce", "nsb20198", "Science and Engineering Labor Force", "WF", "科学与工程人才规模、结构、流动、职业路径及中国出生人才关联"),
    SeriesItem(2022, "2021-08-31", "STEM Workforce", "nsb20212", "The STEM Labor Force of Today: Scientists, Engineers, and Skilled Technical Workers", "WF", "科学与工程人才规模、结构、流动、职业路径及中国出生人才关联"),
    SeriesItem(2024, "2024-05-30", "STEM Workforce", "nsb20245", "The STEM Labor Force: Scientists, Engineers, and Skilled Technical Workers", "WF", "科学与工程人才规模、结构、流动、职业路径及中国出生人才关联"),
    SeriesItem(2020, "2020-01-15", "Invention and Innovation", "nsb20204", "Invention, Knowledge Transfer, and Innovation", "INV", "专利、科学知识引用、大学与联邦技术转移、创业创新及中国位置"),
    SeriesItem(2022, "2022-03-08", "Invention and Innovation", "nsb20224", "Invention, Knowledge Transfer, and Innovation", "INV", "专利、科学知识引用、大学与联邦技术转移、创业创新及中国位置"),
    SeriesItem(2024, "2024-02-29", "Invention and Innovation", "nsb20241", "Invention, Knowledge Transfer, and Innovation", "INV", "专利、科学知识引用、大学与联邦技术转移、创业创新及中国位置"),
    SeriesItem(2020, "2020-01-23", "KTI Industries", "nsb20205", "Production and Trade of Knowledge- and Technology-Intensive Industries", "KTI", "知识技术密集产业产出、贸易、研发强度、人工智能、生物技术与中国位置"),
    SeriesItem(2022, "2022-04-19", "KTI Industries", "nsb20226", "Production and Trade of Knowledge- and Technology-Intensive Industries", "KTI", "知识技术密集产业产出、贸易、研发强度、人工智能、生物技术与中国位置"),
    SeriesItem(2024, "2024-04-22", "KTI Industries", "nsb20247", "Production and Trade of Knowledge- and Technology-Intensive Industries", "KTI", "知识技术密集产业产出、贸易、研发强度、人工智能、生物技术与中国位置"),
    SeriesItem(2026, "2025-07-23", "Discovery", "nsb20257", "Discovery: R&D Activity and Research Publications", "DISC", "研发投入、科学论文、国际合作与中国位置的2026整合节点"),
    SeriesItem(2026, "2026-02-12", "STEM Talent", "nsb20261", "STEM Talent: Education, Training, and Workforce", "TALENT", "STEM教育、博士培养、科研人才与技术劳动力的2026整合节点"),
    SeriesItem(2026, "2026-05-01", "Translation to Impact", "nsb20262", "Translation to Impact: U.S. and Global Science, Technology, and Innovation Output", "IMPACT", "知识转移、专利、创新、产业、贸易与中国位置的2026整合节点"),
)


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


def catalog_row(item: SeriesItem) -> dict[str, str]:
    return {
        "报告ID": item.report_id,
        "机构ID": "nsf-nsb-sei",
        "机构英文名": "National Science Board / National Center for Science and Engineering Statistics",
        "国家或地区": "美国",
        "发布日期": item.published,
        "观察窗": observation_window(item.published),
        "报告名称": f"{item.title} ({item.cycle} cycle)",
        "报告类型": "Science and Engineering Indicators专题报告",
        "原文链接": item.landing,
        "本地路径": "",
        "正文完整度": "官方PDF全文待保存",
        "优先级": "P0-China-STI-series",
        "示踪问题": THEMES,
        "机构观点等级": "美国联邦官方统计分析；事实性、政策中性指标材料",
        "样本角色": SERIES_ROLE,
        "编码状态": "目录待筛选",
        "预期用途": item.reuse_role,
        "本地原始资产路径": "",
        "原始资产状态": "待定点下载",
    }


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
    catalog = [row for row in read_csv(catalog_path) if row.get("样本角色") != SERIES_ROLE]
    new_rows = [catalog_row(item) for item in ITEMS]
    existing_ids = {row["报告ID"] for row in catalog}
    collisions = existing_ids & {row["报告ID"] for row in new_rows}
    if collisions:
        raise RuntimeError(f"NSF/NSB science innovation series ID collision: {sorted(collisions)}")
    catalog.extend(new_rows)
    catalog_by_id = {row["报告ID"]: row for row in catalog}

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
        if len(extracted) < 5_000:
            raise RuntimeError(f"extracted text too short: {item.report_id} {len(extracted)}")
        pages = len(PdfReader(pdf_path).pages)
        lower = extracted.lower()
        china_hits = lower.count("china") + lower.count("chinese")
        row = catalog_by_id[item.report_id]
        row["本地路径"] = str(pdf_path)
        row["正文完整度"] = "官方PDF全文已保存"
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "NCSES官方主报告PDF已获取；已生成逐页文本与科技创新定向切片"
        ledger.append({
            "报告ID": item.report_id,
            "指标周期": str(item.cycle),
            "发布日期": item.published,
            "专题": item.topic,
            "报告名称": item.title,
            "官方编号": item.publication_code.upper(),
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
            "中国与科技创新复用角色": item.reuse_role,
            "获取日期": today,
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "156_NSF_NSB科学体系人才转化跨期专题全文台账.csv", ledger, list(ledger[0]))
    total_pages = sum(int(row["PDF页数"]) for row in ledger)
    total_bytes = sum(int(row["字节数"]) for row in ledger)
    total_chars = sum(int(row["提取文本字符数"]) for row in ledger)
    total_china_hits = sum(int(row["China词形命中数"]) for row in ledger)
    (root / "157_NSF_NSB科学体系人才转化跨期专题全文结果.md").write_text(
        "# NSF/NSB科学体系、人才与创新转化跨期专题全文结果\n\n"
        f"- 定点保存NCSES官方主报告PDF：{len(ledger)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次；中国关联强度因专题而异，须结合全文语境使用。\n"
        "- 2020、2022、2024三个指标周期各保留学术研发、科技人才、发明与知识转移、知识技术密集型产业四类高复用专题。\n"
        "- 2026周期保留Discovery、STEM Talent、Translation to Impact三份重组后的综合专题，衔接研发投入、论文产出、人才、专利、技术转移、产业和贸易。\n"
        "- 本批只保存主报告PDF，不下载同页附表、图包、技术附录和全格式压缩包。\n"
        "- 该系列属于事实性、政策中性的联邦统计材料，用于科技能力、创新机制和中国位置比较，不能直接替代独立智库立场证据。\n\n"
        "跨期引用须核对指标周期、数据年份、统计分类、计价方式和2026专题重组造成的口径变化。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(ledger)} pages={total_pages} bytes={total_bytes} "
        f"chars={total_chars} china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
