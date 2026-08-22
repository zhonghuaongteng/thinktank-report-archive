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
SERIES_ROLE = "WIPO世界知识产权报告近十年轻量目录"


@dataclass(frozen=True)
class WiprItem:
    year: int
    title: str
    landing: str
    pdf_url: str
    selected: bool = False
    strategy: str = "轻量目录"

    @property
    def report_id(self) -> str:
        return f"C-WIPO-WIPR-{self.year}"


ITEMS = (
    WiprItem(
        2015,
        "World Intellectual Property Report 2015: Breakthrough Innovation and Economic Growth",
        "https://www.wipo.int/publications/en/details.jsp?id=3995&plang=EN",
        "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_944_2015.pdf",
        strategy="边界目录",
    ),
    WiprItem(
        2017,
        "World Intellectual Property Report 2017: Intangible Capital in Global Value Chains",
        "https://www.wipo.int/publications/en/series/index.jsp?id=38",
        "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_944_2017.pdf",
        True,
        "无形资本与全球价值链全文节点",
    ),
    WiprItem(
        2019,
        "World Intellectual Property Report 2019: The Geography of Innovation: Local Hotspots, Global Networks",
        "https://www.wipo.int/en/web/world-ip-report/2019/index",
        "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_944_2019.pdf",
        True,
        "创新地理与全球网络全文节点",
    ),
    WiprItem(
        2022,
        "World Intellectual Property Report 2022: The Direction of Innovation",
        "https://www.wipo.int/publications/en/details.jsp?id=4594&plang=EN",
        "https://www.wipo.int/edocs/pubdocs/en/wipo-pub-944-2022-en-world-intellectual-property-report-2022-the-direction-of-innovation.pdf",
        True,
        "创新方向与公共任务全文节点",
    ),
    WiprItem(
        2024,
        "World Intellectual Property Report 2024: Making Innovation Policy Work for Development",
        "https://www.wipo.int/publications/en/details.jsp?id=4724&plang=EN",
        "https://www.wipo.int/edocs/pubdocs/en/wipo-pub-944-2024-en-world-intellectual-property-report-2024.pdf",
        True,
        "创新能力与产业政策全文节点",
    ),
    WiprItem(
        2026,
        "World Intellectual Property Report 2026: Technology on the Move",
        "https://www.wipo.int/publications/en/details.jsp?id=4833&plang=EN",
        "https://www.wipo.int/edocs/pubdocs/en/wipo-pub-944-2026-en-the-world-intellectual-property-report-2026-technology-on-the-move.pdf",
        True,
        "技术扩散与吸收能力全文节点",
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
        2015: "突破性创新、半导体等技术的长期增长机制前序边界",
        2017: "智能手机与光伏价值链可用于识别中国制造、无形资本和技术收益分配",
        2019: "以专利和科学论文刻画创新热点，中国进入全球主要创新集聚地比较",
        2022: "可检索数字技术、健康与低碳创新方向中的中国研发和政策位置",
        2024: "可比较中国科学、技术和生产能力的相关性、复杂度及产业多元化路径",
        2026: "直接讨论中国作为深科技知识吸收者、来源国和技术扩散节点的变化",
    }[year]


def sequence_role(year: int) -> str:
    return {
        2017: "无形资本、技术收益与全球价值链基线节点",
        2019: "科学与专利活动集聚、跨国协作和创新地理节点",
        2022: "危机、公共任务与创新方向选择节点",
        2024: "本地科学技术能力、相关多元化与创新政策节点",
        2026: "技术采用、知识扩散、吸收能力与创新生态节点",
    }[year]


def catalog_row(item: WiprItem) -> dict[str, str]:
    return {
        "报告ID": item.report_id,
        "机构ID": "wipo-wipr",
        "机构英文名": "World Intellectual Property Organization",
        "国家或地区": "国际组织",
        "发布日期": f"{item.year}-01-01",
        "观察窗": observation_window(item.year),
        "报告名称": item.title,
        "报告类型": "World Intellectual Property Report/创新机制专题",
        "原文链接": item.landing,
        "本地路径": "",
        "正文完整度": "官方出版记录与全文入口",
        "优先级": "P0-China-STI-series" if item.selected else "P2-boundary-light",
        "示踪问题": THEMES,
        "机构观点等级": "WIPO官方创新机制研究；与独立智库政策立场分层使用",
        "样本角色": SERIES_ROLE,
        "编码状态": "目录待筛选",
        "预期用途": f"科学发现到技术采用的机制链；{china_role(item.year)}",
        "本地原始资产路径": "",
        "原始资产状态": "待定点下载" if item.selected else "官方入口已保存；超出严格十年窗部分不下载全文",
    }


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
    catalog = [row for row in read_csv(catalog_path) if row.get("样本角色") != SERIES_ROLE]
    new_rows = [catalog_row(item) for item in ITEMS]
    existing_ids = {row["报告ID"] for row in catalog}
    if existing_ids & {row["报告ID"] for row in new_rows}:
        raise RuntimeError("WIPO WIPR ID collides with an existing non-series record")
    catalog.extend(new_rows)
    catalog_by_id = {row["报告ID"]: row for row in catalog}

    fulltext_rows: list[dict[str, str]] = []
    today = date.today().isoformat()
    for item in (candidate for candidate in ITEMS if candidate.selected):
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
        pages = len(PdfReader(pdf_path).pages)
        if len(extracted) < 5_000:
            raise RuntimeError(f"extracted text too short: {item.report_id} {len(extracted)}")
        lower = extracted.lower()
        china_hits = lower.count("china") + lower.count("chinese")
        row = catalog_by_id[item.report_id]
        row["本地路径"] = str(pdf_path)
        row["正文完整度"] = "官方PDF全文已保存"
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "WIPO官方PDF已获取；已生成逐页文本与科技创新定向切片"
        fulltext_rows.append({
            "报告ID": item.report_id,
            "年份": str(item.year),
            "报告名称": item.title,
            "序列角色": sequence_role(item.year),
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
            "中国关联": china_role(item.year),
            "获取日期": today,
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    light_rows = [{
        "报告ID": item.report_id,
        "发布日期": f"{item.year}-01-01",
        "日期精度": "年；以1月1日作排序占位",
        "报告名称": item.title,
        "官方落地页": item.landing,
        "官方PDF": item.pdf_url,
        "科学技术创新主题": THEMES,
        "中国关联": china_role(item.year),
        "全文策略": item.strategy,
        "采集日期": today,
    } for item in ITEMS]
    write_csv(root / "150_WIPO世界知识产权报告近十年轻量目录.csv", light_rows, list(light_rows[0]))
    write_csv(root / "152_WIPO世界知识产权报告跨期节点全文台账.csv", fulltext_rows, list(fulltext_rows[0]))
    total_pages = sum(int(row["PDF页数"]) for row in fulltext_rows)
    total_bytes = sum(int(row["字节数"]) for row in fulltext_rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in fulltext_rows)
    total_china_hits = sum(int(row["China词形命中数"]) for row in fulltext_rows)
    (root / "151_WIPO世界知识产权报告近十年轻量目录结果.md").write_text(
        "# WIPO世界知识产权报告近十年轻量目录结果\n\n"
        "- 纳入2015、2017、2019、2022、2024、2026六期官方目录；2015年版仅作边界记录。\n"
        "- 2017—2026五期双年度报告进入全文层，覆盖全部观察窗，无需逐年扩张。\n"
        "- 主轴限定为科学知识、技术创新、创新能力、扩散采用、产业转化、人才与国际合作。\n"
        "- 安全、供应链和治理仅在直接改变研发、技术路线或创新协作机制时进入切片。\n"
        "- WIPO材料作为国际组织官方机制研究使用，不与独立智库立场混同。\n",
        encoding="utf-8",
    )
    (root / "153_WIPO世界知识产权报告跨期节点全文结果.md").write_text(
        "# WIPO世界知识产权报告跨期节点全文结果\n\n"
        f"- 新增WIPO官方PDF：{len(fulltext_rows)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次，可支持中国创新能力、创新地理和知识扩散比较。\n"
        "- 跨期链条：无形资本与价值链（2017）—创新地理与全球网络（2019）—创新方向（2022）—本地能力与政策设计（2024）—技术扩散与吸收能力（2026）。\n"
        "- 该系列补充GII的机制解释层，避免将指标排名直接等同于创新能力变化。\n\n"
        "精确引用须回查报告表格、指标年份和物理页码；跨期比较须核对各版问题意识与方法差异。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(fulltext_rows)} pages={total_pages} "
        f"bytes={total_bytes} chars={total_chars} china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
