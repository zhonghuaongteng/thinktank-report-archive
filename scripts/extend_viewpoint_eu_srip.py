from __future__ import annotations

import argparse
import csv
import hashlib
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
SERIES_ROLE = "欧盟SRIP科研创新绩效近十年轻量目录"


@dataclass(frozen=True)
class SripItem:
    year: int
    published: str
    title: str
    landing: str
    publication_id: str
    doi: str
    selected: bool = False

    @property
    def report_id(self) -> str:
        return f"C-EU-SRIP-{self.year}"

    @property
    def attachment(self) -> str:
        return (
            "https://op.europa.eu/o/opportal-service/download-handler"
            f"?identifier={self.publication_id}&format=PDF&language=en"
            "&productionSystem=cellar&part="
        )


ITEMS = (
    SripItem(
        2016,
        "2016-03-03",
        "Science, Research and Innovation Performance of the EU 2016: A Contribution to the Open Innovation, Open Science, Open to the World Agenda",
        "https://op.europa.eu/en/publication-detail/-/publication/744d5735-e1d4-11e5-8a50-01aa75ed71a1/language-en",
        "744d5735-e1d4-11e5-8a50-01aa75ed71a1",
        "10.2777/427046",
        True,
    ),
    SripItem(
        2018,
        "2018-04-10",
        "Science, Research and Innovation Performance of the EU 2018: Strengthening the Foundations for Europe's Future",
        "https://op.europa.eu/en/publication-detail/-/publication/16907d0f-1d05-11e8-ac73-01aa75ed71a1/language-en",
        "16907d0f-1d05-11e8-ac73-01aa75ed71a1",
        "10.2777/14136",
    ),
    SripItem(
        2020,
        "2020-10-12",
        "Science, Research and Innovation Performance of the EU 2020: A Fair, Green and Digital Europe",
        "https://op.europa.eu/en/publication-detail/-/publication/932417b9-0cfc-11eb-bc07-01aa75ed71a1/language-en",
        "932417b9-0cfc-11eb-bc07-01aa75ed71a1",
        "10.2777/534046",
        True,
    ),
    SripItem(
        2022,
        "2022-08-01",
        "Science, Research and Innovation Performance of the EU 2022: Building a Sustainable Future in Uncertain Times",
        "https://op.europa.eu/en/publication-detail/-/publication/52f8a759-1c42-11ed-8fa0-01aa75ed71a1/language-en",
        "52f8a759-1c42-11ed-8fa0-01aa75ed71a1",
        "10.2777/78826",
    ),
    SripItem(
        2024,
        "2024-06-26",
        "Science, Research and Innovation Performance of the EU 2024: A Competitive Europe for a Sustainable Future",
        "https://op.europa.eu/en/publication-detail/-/publication/c683268c-3cdc-11ef-ab8f-01aa75ed71a1/language-en",
        "c683268c-3cdc-11ef-ab8f-01aa75ed71a1",
        "10.2777/965670",
        True,
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


def fetch_pdf(url: str) -> bytes:
    response = httpx.get(url, follow_redirects=True, timeout=900, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    data = response.content
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"official attachment is not a PDF: {url}")
    return data


def catalog_row(item: SripItem) -> dict[str, str]:
    return {
        "报告ID": item.report_id,
        "机构ID": "eu-srip",
        "机构英文名": "European Commission, Directorate-General for Research and Innovation",
        "国家或地区": "欧盟",
        "发布日期": item.published,
        "观察窗": observation_window(item.year),
        "报告名称": item.title,
        "报告类型": "欧盟科学研究与创新绩效双年度旗舰报告",
        "原文链接": item.landing,
        "本地路径": "",
        "正文完整度": "官方报告元数据与PDF入口",
        "优先级": "P0-China-STI-series" if item.selected else "P1-STI-light-catalog",
        "示踪问题": THEMES,
        "机构观点等级": "欧盟委员会研发总司官方绩效评估；作为欧洲科研创新证据基线",
        "样本角色": SERIES_ROLE,
        "编码状态": "目录待筛选",
        "预期用途": "欧盟科研投入、知识生产、人才、创新扩散、产业转化、区域生态及中欧美比较",
        "本地原始资产路径": "",
        "原始资产状态": "待定点下载" if item.selected else "官方入口已保存；连续系列已完成跨期抽样",
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
        raise RuntimeError("EU SRIP report ID collides with an existing non-series record")
    catalog.extend(new_rows)
    catalog_by_id = {row["报告ID"]: row for row in catalog}

    fulltext_rows: list[dict[str, str]] = []
    today = date.today().isoformat()
    for item in (candidate for candidate in ITEMS if candidate.selected):
        pdf_path = pdf_dir / f"{item.report_id}.pdf"
        text_path = text_dir / f"{item.report_id}.txt"
        slice_path = slice_dir / f"{item.report_id}.md"
        if pdf_path.exists() and text_path.exists() and slice_path.exists():
            data = pdf_path.read_bytes()
        else:
            data = fetch_pdf(item.attachment)
            pdf_path.write_bytes(data)
            process_pdf(pdf_path, text_dir, slice_dir)
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        pages = len(PdfReader(pdf_path).pages)
        if len(extracted) < 5_000:
            raise RuntimeError(f"extracted text too short: {item.report_id} {len(extracted)}")
        china_hits = extracted.lower().count("china") + extracted.lower().count("chinese")
        if china_hits < 5:
            raise RuntimeError(f"China comparison signal unexpectedly weak: {item.report_id} {china_hits}")
        row = catalog_by_id[item.report_id]
        row["本地路径"] = str(pdf_path)
        row["正文完整度"] = "官方PDF全文已保存"
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "官方PDF已获取；已生成逐页文本与科技创新定向切片"
        fulltext_rows.append(
            {
                "报告ID": item.report_id,
                "年份": str(item.year),
                "报告名称": item.title,
                "序列角色": "早期开放创新基线" if item.year == 2016 else "转型期绿色数字节点" if item.year == 2020 else "近期竞争力与科研体系节点",
                "DOI": item.doi,
                "官方落地页": item.landing,
                "官方PDF": item.attachment,
                "本地PDF": str(pdf_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "PDF页数": str(pages),
                "字节数": str(len(data)),
                "提取文本字符数": str(len(extracted)),
                "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(data).hexdigest(),
                "中国关联": "是；正文含中国科研投入、知识生产、技术能力或创新绩效比较",
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
            "DOI": item.doi,
            "官方落地页": item.landing,
            "官方PDF": item.attachment,
            "科学技术创新主题": THEMES,
            "中国关联": "是；报告在全球语境中比较中国科研与创新表现",
            "全文策略": "已定点下载" if item.selected else "保留轻量目录；连续系列已完成跨期抽样",
            "采集日期": today,
        }
        for item in ITEMS
    ]
    write_csv(root / "134_欧盟SRIP科研创新绩效近十年轻量目录.csv", light_rows, list(light_rows[0]))
    write_csv(root / "136_欧盟SRIP科研创新绩效跨期节点全文台账.csv", fulltext_rows, list(fulltext_rows[0]))
    total_pages = sum(int(row["PDF页数"]) for row in fulltext_rows)
    total_bytes = sum(int(row["字节数"]) for row in fulltext_rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in fulltext_rows)
    total_china_hits = sum(int(row["China词形命中数"]) for row in fulltext_rows)
    (root / "135_欧盟SRIP科研创新绩效近十年轻量目录结果.md").write_text(
        "# 欧盟SRIP科研创新绩效近十年轻量目录结果\n\n"
        "- 建立2016、2018、2020、2022、2024五期欧盟委员会双年度旗舰目录。\n"
        "- 目录覆盖科研投入、知识生产、人才与科研组织、创新扩散、产业转化、区域生态和国际比较。\n"
        "- 中国作为横向比较维度进入全部五期记录。\n"
        "- 精选2016、2020、2024三个跨期节点进入本地全文层；2018、2022保留发现入口。\n\n"
        "2026版截至采集日尚未发布，欧盟委员会已列出2026年10月1日发布活动。该节点等待正式报告，不把活动材料计入报告目录。\n",
        encoding="utf-8",
    )
    (root / "137_欧盟SRIP科研创新绩效跨期节点全文结果.md").write_text(
        "# 欧盟SRIP科研创新绩效跨期节点全文结果\n\n"
        f"- 新增官方PDF：{len(fulltext_rows)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次，用于定位中欧美科研投入、知识生产、技术能力与创新绩效比较。\n"
        "- 跨期节点：2016开放创新与开放科学基线、2020绿色数字转型节点、2024竞争力与科研体系重组节点。\n\n"
        "该系列属于欧盟委员会官方绩效评估和政策分析，应作为欧洲科研创新证据基线使用。自动切片只作定位；正式引用须回查正文、图表注释、统计口径与页码。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(fulltext_rows)} pages={total_pages} "
        f"bytes={total_bytes} chars={total_chars} china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
