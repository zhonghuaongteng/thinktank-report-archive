from __future__ import annotations

import argparse
import csv
import hashlib
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
THEMES = "科学体系与基础研究；研发投入与公共支持；科研人才与机构；科学产出与重点技术；创新扩散与成果转化；开放科学与国际合作；中国科技横向维度"
SERIES_ROLE = "UNESCO全球科学体系近十年轻量目录"


@dataclass(frozen=True)
class UnescoScienceItem:
    year: int
    published: str
    title: str
    series: str
    landing: str
    doi: str = ""
    selected: bool = False
    strategy: str = "轻量目录"
    pdf_url: str = ""

    @property
    def report_id(self) -> str:
        return f"C-UNESCO-SCIENCE-{self.year}"


ITEMS = (
    UnescoScienceItem(
        2015,
        "2015-11-10",
        "UNESCO Science Report: Towards 2030",
        "UNESCO Science Report",
        "https://unesdoc.unesco.org/ark:/48223/pf0000235406_eng",
        strategy="边界目录",
    ),
    UnescoScienceItem(
        2020,
        "2020-12-14",
        "Global Ocean Science Report 2020: Charting Capacity for Ocean Sustainability",
        "Global Ocean Science Report",
        "https://unesdoc.unesco.org/ark:/48223/pf0000375147",
        doi="10.18356/9789216040048",
        strategy="专题科学能力目录",
        pdf_url="https://sdgs.un.org/sites/default/files/2022-01/GOSR%202020.pdf",
    ),
    UnescoScienceItem(
        2021,
        "2021-06-11",
        "UNESCO Science Report: The Race Against Time for Smarter Development",
        "UNESCO Science Report",
        "https://unesdoc.unesco.org/ark:/48223/pf0000377433",
        selected=True,
        strategy="全文节点",
        pdf_url=(
            "https://unesdoc.unesco.org/in/rest/annotationSVC/DownloadWatermarkedAttachment/"
            "attach_import_a8477af4-1d6a-442f-af2f-7e77b02e5c31?_=377433eng.pdf"
        ),
    ),
    UnescoScienceItem(
        2023,
        "2023-12-14",
        "UNESCO Open Science Outlook 1: Status and Trends Around the World",
        "UNESCO Open Science Outlook",
        "https://unesdoc.unesco.org/ark:/48223/pf0000387324",
        doi="10.54677/GIIC6829",
        selected=True,
        strategy="开放科学全文节点",
        pdf_url=(
            "https://unesdoc.unesco.org/in/rest/annotationSVC/DownloadWatermarkedAttachment/"
            "attach_import_963f189b-59ff-4092-954f-56db0b0eaf02?_=387324eng.pdf"
        ),
    ),
    UnescoScienceItem(
        2026,
        "2026-07-13",
        "Science at a Turning Point: International Decade of Sciences for Sustainable Development: Global Report",
        "IDSSD Global Report",
        "https://unesdoc.unesco.org/ark:/48223/pf0000398672_eng",
        doi="10.54677/FMXL6762",
        selected=True,
        strategy="当代桥接节点",
        pdf_url=(
            "https://unesdoc.unesco.org/in/rest/annotationSVC/DownloadWatermarkedAttachment/"
            "attach_import_846710c6-7511-4d71-acd0-afb36468931e?_=398672eng.pdf"
        ),
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


def catalog_row(item: UnescoScienceItem) -> dict[str, str]:
    if item.year == 2015:
        china_role = "含独立中国章节；仅作五年周期前序边界"
    elif item.year == 2020:
        china_role = "海洋科学投入、人才、设施、论文、蓝色专利与技术转移的专题能力基线"
    elif item.year == 2021:
        china_role = "含中国专章及全球研发投入、人才、论文与重点技术比较"
    elif item.year == 2023:
        china_role = "含中国青年研究人员与开放科学实践案例"
    else:
        china_role = "用于观察中国参与全球科学合作、基础设施与能力差距议题的当代背景"
    return {
        "报告ID": item.report_id,
        "机构ID": "unesco-science",
        "机构英文名": "United Nations Educational, Scientific and Cultural Organization (UNESCO)",
        "国家或地区": "多边",
        "发布日期": item.published,
        "观察窗": observation_window(item.year),
        "报告名称": item.title,
        "报告类型": item.series,
        "原文链接": item.landing,
        "本地路径": "",
        "正文完整度": "官方出版记录与全文入口",
        "优先级": "P0-China-STI-series" if item.selected else "P2-boundary-light",
        "示踪问题": THEMES,
        "机构观点等级": "UNESCO官方全球科学监测与倡议；作为科学体系比较证据基线",
        "样本角色": SERIES_ROLE,
        "编码状态": "目录待筛选",
        "预期用途": f"全球科研投入、科学人才、知识产出、重点技术、开放科学及中国位置；{china_role}",
        "本地原始资产路径": "",
        "原始资产状态": "待处理" if item.selected else "官方入口已保存；超出严格十年窗部分不下载全文",
    }


def sequence_role(year: int) -> str:
    if year == 2021:
        return "全球科学体系与中国专章核心节点"
    if year == 2023:
        return "开放科学制度、基础设施与中国实践桥接节点"
    return "科学十年启动后组织、融资、基础设施与科学鸿沟桥接节点"


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
        raise RuntimeError("UNESCO science report ID collides with an existing non-series record")
    catalog.extend(new_rows)
    catalog_by_id = {row["报告ID"]: row for row in catalog}

    fulltext_rows: list[dict[str, str]] = []
    today = date.today().isoformat()
    for item in (candidate for candidate in ITEMS if candidate.selected):
        pdf_path = pdf_dir / f"{item.report_id}.pdf"
        text_path = text_dir / f"{item.report_id}.txt"
        slice_path = slice_dir / f"{item.report_id}.md"
        if not pdf_path.exists():
            raise RuntimeError(
                f"official PDF missing: {pdf_path}; UNESDOC may require browser-assisted retrieval from {item.pdf_url}"
            )
        data = pdf_path.read_bytes()
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"local asset is not a PDF: {pdf_path}")
        if not text_path.exists() or not slice_path.exists():
            process_pdf(pdf_path, text_dir, slice_dir)
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
        row["原始资产状态"] = "官方PDF已获取；已生成逐页文本与科技创新定向切片"
        fulltext_rows.append(
            {
                "报告ID": item.report_id,
                "年份": str(item.year),
                "报告名称": item.title,
                "系列": item.series,
                "序列角色": sequence_role(item.year),
                "DOI": item.doi,
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
                "中国关联": catalog_by_id[item.report_id]["预期用途"],
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
            "系列": item.series,
            "DOI": item.doi,
            "官方落地页": item.landing,
            "官方PDF": item.pdf_url,
            "科学技术创新主题": THEMES,
            "中国关联": catalog_by_id[item.report_id]["预期用途"],
            "全文策略": item.strategy,
            "采集日期": today,
        }
        for item in ITEMS
    ]
    write_csv(root / "142_UNESCO全球科学体系近十年轻量目录.csv", light_rows, list(light_rows[0]))
    write_csv(root / "144_UNESCO全球科学体系跨期节点全文台账.csv", fulltext_rows, list(fulltext_rows[0]))
    total_pages = sum(int(row["PDF页数"]) for row in fulltext_rows)
    total_bytes = sum(int(row["字节数"]) for row in fulltext_rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in fulltext_rows)
    total_china_hits = sum(int(row["China词形命中数"]) for row in fulltext_rows)
    (root / "143_UNESCO全球科学体系近十年轻量目录结果.md").write_text(
        "# UNESCO全球科学体系近十年轻量目录结果\n\n"
        "- 纳入2015、2021两期UNESCO Science Report，2020年全球海洋科学能力报告、2023年开放科学展望及2026年科学十年全球报告。\n"
        "- 2015年版略超严格十年窗，仅保留为五年周期前序边界，不下载全文。\n"
        "- 2020年全球海洋科学报告补齐科研投入、设施、人才、蓝色专利和技术转移的专题入口，仅保留轻量目录。\n"
        "- 2021年科学报告、2023年开放科学展望和2026年科学十年全球报告进入全文层；分别承担全球科学体系与中国专章、开放科学制度、当代科学组织与能力差距节点。\n"
        "- 该组材料用于全球科学体系和中国位置的事实比较，不作为独立智库立场。\n",
        encoding="utf-8",
    )
    (root / "145_UNESCO全球科学体系跨期节点全文结果.md").write_text(
        "# UNESCO全球科学体系跨期节点全文结果\n\n"
        f"- 新增官方PDF：{len(fulltext_rows)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次；2021年中国专章是中国科技创新体系判断的主要入口。\n"
        "- 2021节点覆盖全球研发投入、科研人才、论文产出、重点技术、开放科学、绿色与数字转型。\n"
        "- 2023节点覆盖开放科学政策、基础设施、资金、能力建设和中国青年研究人员实践。\n"
        "- 2026节点覆盖科学十年倡议的组织方式、资金、基础设施、参与差距及科学与决策连接。\n\n"
        "UNESCO报告属于国际组织官方监测和倡议材料。正式引用指标须回查表格年份、统计口径和页码；中国章节中的解释性判断须与中国官方统计及其他独立来源交叉核验。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(fulltext_rows)} pages={total_pages} "
        f"bytes={total_bytes} chars={total_chars} china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
