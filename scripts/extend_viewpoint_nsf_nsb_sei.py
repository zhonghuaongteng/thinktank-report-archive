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
SERIES_ROLE = "NSF-NSB科学与工程指标近十年轻量目录"


@dataclass(frozen=True)
class SeiItem:
    year: int
    published: str
    title: str
    landing: str
    attachment: str
    selected: bool = False

    @property
    def report_id(self) -> str:
        return f"C-NSF-NSB-SEI-{self.year}"


ITEMS = (
    SeiItem(
        2016,
        "2016-02-02",
        "Science and Engineering Indicators 2016 Digest",
        "https://www.nsf.gov/reports/indicators/science-engineering-indicators-2016-digest",
        "https://nsf-gov-resources.nsf.gov/statistics/2016/nsb20161/uploads/1/2/digest.pdf",
        True,
    ),
    SeiItem(
        2018,
        "2018-01-01",
        "Science and Engineering Indicators 2018",
        "https://ncses.nsf.gov/statistics/2018/nsb20181/",
        "https://ncses.nsf.gov/statistics/2018/nsb20181/downloads",
    ),
    SeiItem(
        2020,
        "2020-01-15",
        "The State of U.S. Science and Engineering 2020",
        "https://ncses.nsf.gov/pubs/nsb20201",
        "https://ncses.nsf.gov/pubs/nsb20201/assets/nsb20201.pdf",
        True,
    ),
    SeiItem(
        2022,
        "2022-01-18",
        "The State of U.S. Science and Engineering 2022",
        "https://ncses.nsf.gov/pubs/nsb20221",
        "https://ncses.nsf.gov/pubs/nsb20221/assets/nsb20221.pdf",
    ),
    SeiItem(
        2024,
        "2024-03-13",
        "The State of U.S. Science and Engineering 2024",
        "https://ncses.nsf.gov/pubs/nsb20243",
        "https://ncses.nsf.gov/pubs/nsb20243/assets/nsb20243.pdf",
        True,
    ),
    SeiItem(
        2026,
        "2026-05-04",
        "The State of U.S. Science and Engineering 2026",
        "https://ncses.nsf.gov/pubs/nsbsep20261",
        "https://ncses.nsf.gov/pubs/nsbsep20261/assets/nsbsep20261.pdf",
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
    response = httpx.get(url, follow_redirects=True, timeout=600, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    data = response.content
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"official attachment is not a PDF: {url}")
    return data


def catalog_row(item: SeiItem) -> dict[str, str]:
    return {
        "报告ID": item.report_id,
        "机构ID": "nsf-nsb-sei",
        "机构英文名": "National Science Board / National Center for Science and Engineering Statistics",
        "国家或地区": "美国",
        "发布日期": item.published,
        "观察窗": observation_window(item.year),
        "报告名称": item.title,
        "报告类型": "Science and Engineering Indicators双年度旗舰系列",
        "原文链接": item.landing,
        "本地路径": "",
        "正文完整度": "官方报告及附件入口元数据",
        "优先级": "P0-China-STI-series" if item.selected else "P1-STI-light-catalog",
        "示踪问题": THEMES,
        "机构观点等级": "NSB指导、NCSES编制的法定科技统计旗舰成果；指标本身为政策中性证据",
        "样本角色": SERIES_ROLE,
        "编码状态": "目录待筛选",
        "预期用途": "全球科研投入、基础研究、STEM人才、论文与专利、技术转移、知识密集产业及中国比较",
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
        raise RuntimeError("NSF/NSB SEI report ID collides with an existing non-series record")
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
                "序列角色": "早期基线" if item.year == 2016 else "中期节点" if item.year == 2020 else "近期节点" if item.year == 2024 else "当前节点",
                "官方落地页": item.landing,
                "官方PDF": item.attachment,
                "本地PDF": str(pdf_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "PDF页数": str(pages),
                "字节数": str(len(data)),
                "提取文本字符数": str(len(extracted)),
                "SHA256": hashlib.sha256(data).hexdigest(),
                "中国关联": "是；含中国研发、科研产出、专利、人才或知识技术密集产业比较",
                "获取日期": today,
            }
        )

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    light_rows = [
        {
            "报告ID": item.report_id,
            "发布日期": item.published,
            "日期精度": "月" if item.year == 2018 else "日",
            "报告名称": item.title,
            "官方落地页": item.landing,
            "官方附件入口": item.attachment,
            "科学技术创新主题": THEMES,
            "中国关联": "是；双年度报告包含全球科技统计及中国比较",
            "全文策略": "已定点下载" if item.selected else "保留轻量目录；连续系列已完成跨期抽样",
            "采集日期": today,
        }
        for item in ITEMS
    ]
    write_csv(root / "130_NSF_NSB科学与工程指标近十年轻量目录.csv", light_rows, list(light_rows[0]))
    write_csv(root / "132_NSF_NSB科学与工程指标跨期节点全文台账.csv", fulltext_rows, list(fulltext_rows[0]))
    total_pages = sum(int(row["PDF页数"]) for row in fulltext_rows)
    total_bytes = sum(int(row["字节数"]) for row in fulltext_rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in fulltext_rows)
    (root / "131_NSF_NSB科学与工程指标近十年轻量目录结果.md").write_text(
        "# NSF/NSB科学与工程指标近十年轻量目录结果\n\n"
        "- 建立2016、2018、2020、2022、2024、2026六期官方双年度目录。\n"
        "- 目录覆盖科研投入、基础研究、人才、论文、专利、技术转移、创新与知识技术密集产业。\n"
        "- 中国作为独立横向维度进入全部六期记录。\n"
        "- 精选2016、2020、2024、2026四个跨期节点进入本地全文层；2018、2022保留发现入口。\n\n"
        "2016与2018为综合卷册，2020年起改为摘要报告加专题报告套系。跨期比较须处理产品结构变化和统计口径修订。\n",
        encoding="utf-8",
    )
    (root / "133_NSF_NSB科学与工程指标跨期节点全文结果.md").write_text(
        "# NSF/NSB科学与工程指标跨期节点全文结果\n\n"
        f"- 新增官方PDF：{len(fulltext_rows)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        "- 跨期节点：2016早期基线、2020产品结构转换、2024近期结构、2026当前科技创新与中国比较。\n"
        "- 可用于全球研发投入、基础研究、STEM人才、科研产出、创新转化和知识技术密集产业的跨项目检索。\n\n"
        "自动切片只作定位。指标变化可能来自数据修订、统计源更新、经济体口径和报告产品结构变化，正式引用须回查原文、图表注释与数据来源。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(fulltext_rows)} pages={total_pages} "
        f"bytes={total_bytes} chars={total_chars} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
