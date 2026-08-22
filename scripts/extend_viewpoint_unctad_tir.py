from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from pypdf import PdfReader

try:
    from scripts.extract_viewpoint_pdf_slices import process_pdf
except ModuleNotFoundError:  # direct execution via python scripts/<name>.py
    from extract_viewpoint_pdf_slices import process_pdf


CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
THEMES = "科学技术创新体系；前沿技术与技术扩散；研发能力与人才；产业创新与技术追赶；绿色技术与人工智能；国际合作与技术转移；中国科技横向维度"
SERIES_ROLE = "UNCTAD技术与创新报告近十年轻量目录"


@dataclass(frozen=True)
class UnctadTirItem:
    year: int
    published: str
    title: str
    symbol: str
    landing: str
    digital_library: str
    pdf_url: str = ""
    selected: bool = False
    strategy: str = "轻量目录"

    @property
    def report_id(self) -> str:
        return f"C-UNCTAD-TIR-{self.year}"


ITEMS = (
    UnctadTirItem(
        2015,
        "2015-12-17",
        "Technology and Innovation Report 2015: Fostering Innovation Policies for Industrial Development",
        "UNCTAD/TIR/2015",
        "https://unctad.org/publication/technology-and-innovation-report-2015",
        "https://digitallibrary.un.org/record/822233",
        strategy="边界目录",
    ),
    UnctadTirItem(
        2018,
        "2018-05-15",
        "Technology and Innovation Report 2018: Harnessing Frontier Technologies for Sustainable Development",
        "UNCTAD/TIR/2018",
        "https://unctad.org/publication/technology-and-innovation-report-2018",
        "https://digitallibrary.un.org/record/3832195",
        "https://digitallibrary.un.org/record/3832195/files/UNCTAD_TIR_2018-EN.pdf",
        True,
        "前沿技术基线全文节点",
    ),
    UnctadTirItem(
        2021,
        "2021-02-25",
        "Technology and Innovation Report 2021: Catching Technological Waves, Innovation with Equity",
        "UNCTAD/TIR/2020",
        "https://unctad.org/publication/technology-and-innovation-report-2021",
        "https://digitallibrary.un.org/record/3926808",
        "https://digitallibrary.un.org/record/3926808/files/tir2020_en.pdf",
        True,
        "技术准备度与创新公平全文节点",
    ),
    UnctadTirItem(
        2023,
        "2023-03-16",
        "Technology and Innovation Report 2023: Opening Green Windows, Technological Opportunities for a Low-Carbon World",
        "UNCTAD/TIR/2022",
        "https://unctad.org/tir2023",
        "https://digitallibrary.un.org/record/4007851",
        "https://digitallibrary.un.org/record/4007851/files/UNCTAD_TIR_2022--UNCTAD_TIR_2022_and_Corr.1-EN.pdf?version=1",
        True,
        "绿色技术与产业追赶全文节点",
    ),
    UnctadTirItem(
        2025,
        "2025-04-07",
        "Technology and Innovation Report 2025: Inclusive Artificial Intelligence for Development",
        "UNCTAD/TIR/2025",
        "https://unctad.org/publication/technology-and-innovation-report-2025",
        "https://digitallibrary.un.org/record/4084949",
        "https://digitallibrary.un.org/record/4084949/files/UNCTAD_TIR_2025-EN.pdf",
        True,
        "人工智能能力与包容发展全文节点",
    ),
)


def observation_window(year: int) -> str:
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalize_generated_text(text: str) -> str:
    return re.sub(r"\r+\n?", "\n", text)


def normalize_generated_file(path: Path) -> None:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        current = handle.read()
    normalized = normalize_generated_text(current)
    if normalized != current:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(normalized)


def china_role(year: int) -> str:
    return {
        2015: "作为创新政策与产业发展前序基线，仅保留系列边界",
        2018: "含中国研发、STEM人才、专利和前沿技术能力的跨国比较",
        2021: "含中国前沿技术市场、科研产出和技术准备度指数比较",
        2023: "含中国新能源、光伏、电动汽车、绿色制造和前沿技术准备度比较",
        2025: "含中国AI论文、专利、研发企业、算力、数据与开发者能力比较",
    }[year]


def catalog_row(item: UnctadTirItem) -> dict[str, str]:
    return {
        "报告ID": item.report_id,
        "机构ID": "unctad-tir",
        "机构英文名": "United Nations Conference on Trade and Development (UNCTAD)",
        "国家或地区": "多边",
        "发布日期": item.published,
        "观察窗": observation_window(item.year),
        "报告名称": item.title,
        "报告类型": "Technology and Innovation Report",
        "原文链接": item.landing,
        "本地路径": "",
        "正文完整度": "官方出版记录与全文入口",
        "优先级": "P0-China-STI-series" if item.selected else "P2-boundary-light",
        "示踪问题": THEMES,
        "机构观点等级": "UNCTAD官方科技创新发展评估；作为发展中经济体技术能力与政策比较基线",
        "样本角色": SERIES_ROLE,
        "编码状态": "目录待筛选",
        "预期用途": f"前沿技术、创新体系、能力差距、技术扩散、产业追赶及中国位置；{china_role(item.year)}",
        "本地原始资产路径": "",
        "原始资产状态": "待处理" if item.selected else "官方入口已保存；超出严格十年窗部分不下载全文",
    }


def sequence_role(year: int) -> str:
    return {
        2018: "前沿技术与可持续发展政策基线节点",
        2021: "技术准备度、能力差距与创新公平转向节点",
        2023: "绿色技术窗口、产业政策与技术追赶节点",
        2025: "人工智能基础设施、数据、技能与全球合作节点",
    }[year]


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
    if existing_ids & {row["报告ID"] for row in new_rows}:
        raise RuntimeError("UNCTAD TIR ID collides with an existing non-series record")
    catalog.extend(new_rows)
    catalog_by_id = {row["报告ID"]: row for row in catalog}

    fulltext_rows: list[dict[str, str]] = []
    today = date.today().isoformat()
    for item in (candidate for candidate in ITEMS if candidate.selected):
        pdf_path = pdf_dir / f"{item.report_id}.pdf"
        text_path = text_dir / f"{item.report_id}.txt"
        slice_path = slice_dir / f"{item.report_id}.md"
        if not pdf_path.exists():
            raise RuntimeError(f"official PDF missing: {pdf_path}; retrieve from {item.digital_library}")
        data = pdf_path.read_bytes()
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"local asset is not a PDF: {pdf_path}")
        if not text_path.exists() or not slice_path.exists():
            process_pdf(pdf_path, text_dir, slice_dir)
        normalize_generated_file(text_path)
        normalize_generated_file(slice_path)
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        pages = len(PdfReader(pdf_path).pages)
        if len(extracted) < 5_000:
            raise RuntimeError(f"extracted text too short: {item.report_id} {len(extracted)}")
        lower = extracted.lower()
        china_hits = lower.count("china") + lower.count("chinese")
        row = catalog_by_id[item.report_id]
        row["本地路径"] = str(pdf_path)
        row["正文完整度"] = "官方PDF全文已保存"
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "联合国数字图书馆官方PDF已获取；已生成逐页文本与科技创新定向切片"
        fulltext_rows.append(
            {
                "报告ID": item.report_id,
                "年份": str(item.year),
                "报告名称": item.title,
                "文件号": item.symbol,
                "序列角色": sequence_role(item.year),
                "官方落地页": item.landing,
                "联合国数字图书馆": item.digital_library,
                "官方PDF": item.pdf_url,
                "本地PDF": str(pdf_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "PDF页数": str(pages),
                "字节数": str(len(data)),
                "提取文本字符数": str(len(extracted)),
                "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(data).hexdigest(),
                "中国关联": china_role(item.year),
                "获取日期": today,
            }
        )

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    light_rows = [
        {
            "报告ID": item.report_id,
            "发布日期": item.published,
            "报告名称": item.title,
            "文件号": item.symbol,
            "官方落地页": item.landing,
            "联合国数字图书馆": item.digital_library,
            "官方PDF": item.pdf_url,
            "科学技术创新主题": THEMES,
            "中国关联": china_role(item.year),
            "全文策略": item.strategy,
            "采集日期": today,
        }
        for item in ITEMS
    ]
    write_csv(root / "146_UNCTAD技术与创新报告近十年轻量目录.csv", light_rows, list(light_rows[0]))
    write_csv(root / "148_UNCTAD技术与创新报告跨期节点全文台账.csv", fulltext_rows, list(fulltext_rows[0]))
    total_pages = sum(int(row["PDF页数"]) for row in fulltext_rows)
    total_bytes = sum(int(row["字节数"]) for row in fulltext_rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in fulltext_rows)
    total_china_hits = sum(int(row["China词形命中数"]) for row in fulltext_rows)
    (root / "147_UNCTAD技术与创新报告近十年轻量目录结果.md").write_text(
        "# UNCTAD技术与创新报告近十年轻量目录结果\n\n"
        "- 纳入2015、2018、2021、2023、2025五期Technology and Innovation Report官方目录。\n"
        "- 2015年版略超严格十年窗，仅保留为创新政策与产业发展前序边界，不下载全文。\n"
        "- 2018、2021、2023、2025四期位于三个观察窗，进入跨期全文层；该双年度系列无需补齐更多年度。\n"
        "- 四个节点依次覆盖前沿技术、创新公平、绿色技术窗口与包容性人工智能，并持续包含中国技术能力比较。\n"
        "- UNCTAD材料作为联合国官方科技创新发展评估使用，不与独立智库立场混同。\n",
        encoding="utf-8",
    )
    (root / "149_UNCTAD技术与创新报告跨期节点全文结果.md").write_text(
        "# UNCTAD技术与创新报告跨期节点全文结果\n\n"
        f"- 新增联合国官方PDF：{len(fulltext_rows)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次，四期均可用于中国科技能力与产业位置比较。\n"
        "- 2018节点建立前沿技术、创新系统、基础设施、人才和技术扩散基线。\n"
        "- 2021节点连接技术准备度、数字鸿沟、产业能力与创新公平。\n"
        "- 2023节点连接绿色技术、产业政策、价值链升级和技术追赶。\n"
        "- 2025节点连接AI研发集中度、算力、数据、技能、产业应用和国际科技合作。\n\n"
        "精确引用须回查报告表格、指标年份和物理页码；国家准备度和市场估值跨期比较须核对各版方法变化。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(fulltext_rows)} pages={total_pages} "
        f"bytes={total_bytes} chars={total_chars} china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
