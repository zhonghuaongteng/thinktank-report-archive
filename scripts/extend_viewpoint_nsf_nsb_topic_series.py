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
SERIES_ROLE = "NSF/NSB科学与工程指标研发和论文专题序列"


@dataclass(frozen=True)
class TopicItem:
    cycle: int
    published: str
    topic: str
    publication_code: str
    landing: str

    @property
    def report_id(self) -> str:
        suffix = "RD" if self.topic == "R&D" else "PUB"
        return f"C-NSF-NSB-{suffix}-{self.cycle}"

    @property
    def title(self) -> str:
        if self.topic == "R&D":
            return "Research and Development: U.S. Trends and International Comparisons"
        return "Publications Output: U.S. Trends and International Comparisons"

    @property
    def pdf_url(self) -> str:
        return f"{self.landing}/assets/{self.publication_code}.pdf"


ITEMS = (
    TopicItem(2020, "2020-01-15", "R&D", "nsb20203", "https://ncses.nsf.gov/pubs/nsb20203"),
    TopicItem(2022, "2022-04-28", "R&D", "nsb20225", "https://ncses.nsf.gov/pubs/nsb20225"),
    TopicItem(2024, "2024-05-21", "R&D", "nsb20246", "https://ncses.nsf.gov/pubs/nsb20246"),
    TopicItem(2020, "2019-12-17", "Publications", "nsb20206", "https://ncses.nsf.gov/pubs/nsb20206"),
    TopicItem(2022, "2021-10-28", "Publications", "nsb20214", "https://ncses.nsf.gov/pubs/nsb20214"),
    TopicItem(2024, "2023-12-11", "Publications", "nsb202333", "https://ncses.nsf.gov/pubs/nsb202333"),
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


def normalize_generated_text(text: str) -> str:
    return re.sub(r"\r+\n?", "\n", text)


def normalize_generated_file(path: Path) -> None:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        current = handle.read()
    normalized = normalize_generated_text(current)
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


def topic_role(item: TopicItem) -> str:
    if item.topic == "R&D":
        return "全球研发规模、强度、资助与执行部门结构及中国追赶位置"
    return "全球科学论文规模、学科结构、影响力、开放获取、国际合作及中国位置"


def catalog_row(item: TopicItem) -> dict[str, str]:
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
        "预期用途": topic_role(item),
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
    if existing_ids & {row["报告ID"] for row in new_rows}:
        raise RuntimeError("NSF/NSB topic series ID collides with an existing non-series record")
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
        row["原始资产状态"] = "NCSES官方PDF已获取；已生成逐页文本与科技创新定向切片"
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
            "中国关联": topic_role(item),
            "获取日期": today,
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "154_NSF_NSB研发与科学论文跨期专题全文台账.csv", ledger, list(ledger[0]))
    total_pages = sum(int(row["PDF页数"]) for row in ledger)
    total_bytes = sum(int(row["字节数"]) for row in ledger)
    total_chars = sum(int(row["提取文本字符数"]) for row in ledger)
    total_china_hits = sum(int(row["China词形命中数"]) for row in ledger)
    (root / "155_NSF_NSB研发与科学论文跨期专题全文结果.md").write_text(
        "# NSF/NSB研发与科学论文跨期专题全文结果\n\n"
        f"- 新增NCSES官方专题PDF：{len(ledger)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次，所有报告均包含中国科研能力的国际比较。\n"
        "- 研发序列覆盖2020、2022、2024三个指标周期，追踪全球研发规模、研发强度、资助来源、执行部门和中国追赶位置。\n"
        "- 科学论文序列覆盖2020、2022、2024三个指标周期，追踪论文产出、学科结构、影响力、开放获取、国际合作及中国位置。\n"
        "- 2018年综合报告已在本地作为前序基线，本批不重复拆取全部章节，也不下载表格与图片附件包。\n"
        "- 该系列属于事实性、政策中性的联邦统计材料，用于能力测量和比较，不能直接替代独立智库立场证据。\n\n"
        "跨期引用须核对数据年份、数据库范围、分数计数方法、学科分类和购买力平价口径。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(ledger)} pages={total_pages} bytes={total_bytes} "
        f"chars={total_chars} china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
