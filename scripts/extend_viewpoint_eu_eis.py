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
THEMES = "科学体系与基础研究；创新投入与公共支持；人才与研究体系；企业研发与创新活动；知识资产与创新产出；产业转化与经济影响；国际创新绩效比较；中国科技横向维度"
SERIES_ROLE = "欧盟EIS创新记分牌近十年轻量目录"


@dataclass(frozen=True)
class EisItem:
    year: int
    published: str
    publication_id: str
    doi: str
    selected: bool = False
    attachment_override: str = ""

    @property
    def report_id(self) -> str:
        return f"C-EU-EIS-{self.year}"

    @property
    def title(self) -> str:
        return f"European Innovation Scoreboard {self.year}"

    @property
    def landing(self) -> str:
        return f"https://op.europa.eu/en/publication-detail/-/publication/{self.publication_id}/language-en"

    @property
    def attachment(self) -> str:
        if self.attachment_override:
            return self.attachment_override
        return (
            "https://op.europa.eu/o/opportal-service/download-handler"
            f"?identifier={self.publication_id}&format=PDF&language=en"
            "&productionSystem=cellar&part="
        )


ITEMS = (
    EisItem(
        2016,
        "2016-07-14",
        "6e1bc53d-de12-11e6-ad7c-01aa75ed71a1",
        "10.2873/84537",
        True,
        "https://ec.europa.eu/docsroom/documents/17822/attachments/1/translations/en/renditions/native",
    ),
    EisItem(2017, "2017-06-15", "5b916ff4-523d-11e7-a5ca-01aa75ed71a1", "10.2873/076586"),
    EisItem(2018, "2018-06-21", "8e458033-74fc-11e8-9483-01aa75ed71a1", "10.2873/66501"),
    EisItem(2019, "2019-06-19", "d156a01b-9307-11e9-9369-01aa75ed71a1", "10.2873/877069"),
    EisItem(2020, "2020-06-23", "1457a9d4-084f-11eb-a511-01aa75ed71a1", "10.2873/168", True),
    EisItem(2021, "2021-09-01", "bd128c04-0b93-11ec-adb1-01aa75ed71a1", "10.2873/725879"),
    EisItem(2022, "2022-10-20", "f0e0330d-534f-11ed-92ed-01aa75ed71a1", "10.2777/309907"),
    EisItem(2023, "2023-07-17", "04797497-25de-11ee-a2d3-01aa75ed71a1", "10.2777/119961"),
    EisItem(2024, "2024-07-09", "8a4a4a1f-3e68-11ef-ab8f-01aa75ed71a1", "10.2777/779689", True),
    EisItem(2025, "2025-07-21", "c102236e-66b2-11f0-bf4e-01aa75ed71a1", "10.2777/3239776"),
    EisItem(2026, "2026-07-09", "273fbdb3-7c07-11f1-bf5e-01aa75ed71a1", "10.2777/4615399", True),
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


def catalog_row(item: EisItem) -> dict[str, str]:
    return {
        "报告ID": item.report_id,
        "机构ID": "eu-eis",
        "机构英文名": "European Commission, Directorate-General for Research and Innovation",
        "国家或地区": "欧盟",
        "发布日期": item.published,
        "观察窗": observation_window(item.year),
        "报告名称": item.title,
        "报告类型": "欧盟创新绩效年度记分牌",
        "原文链接": item.landing,
        "本地路径": "",
        "正文完整度": "官方报告元数据与PDF入口",
        "优先级": "P0-China-STI-series" if item.selected else "P1-STI-light-catalog",
        "示踪问题": THEMES,
        "机构观点等级": "欧盟委员会年度创新绩效测量；作为国家创新体系比较证据基线",
        "样本角色": SERIES_ROLE,
        "编码状态": "目录待筛选",
        "预期用途": "创新投入、人才、研究体系、企业研发、知识资产、创新产出、经济影响及中欧美比较",
        "本地原始资产路径": "",
        "原始资产状态": "待定点下载" if item.selected else "官方入口已保存；连续系列已完成跨期抽样",
    }


def sequence_role(year: int) -> str:
    if year == 2016:
        return "早期25项指标与中国追赶基线"
    if year == 2020:
        return "疫情与绿色数字转型前后节点"
    if year == 2024:
        return "现行32项指标框架近期节点"
    return "当前全球创新绩效比较节点"


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
        raise RuntimeError("EU EIS report ID collides with an existing non-series record")
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
        if china_hits < 3:
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
                "序列角色": sequence_role(item.year),
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
                "中国关联": "是；正文将中国纳入全球创新绩效及国家创新体系比较",
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
            "中国关联": "是；年度报告包含中国等全球竞争者的创新绩效比较",
            "全文策略": "已定点下载" if item.selected else "保留轻量目录；连续系列已完成跨期抽样",
            "采集日期": today,
        }
        for item in ITEMS
    ]
    write_csv(root / "138_欧盟EIS创新记分牌近十年轻量目录.csv", light_rows, list(light_rows[0]))
    write_csv(root / "140_欧盟EIS创新记分牌跨期节点全文台账.csv", fulltext_rows, list(fulltext_rows[0]))
    total_pages = sum(int(row["PDF页数"]) for row in fulltext_rows)
    total_bytes = sum(int(row["字节数"]) for row in fulltext_rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in fulltext_rows)
    total_china_hits = sum(int(row["China词形命中数"]) for row in fulltext_rows)
    (root / "139_欧盟EIS创新记分牌近十年轻量目录结果.md").write_text(
        "# 欧盟EIS创新记分牌近十年轻量目录结果\n\n"
        "- 建立2016—2026十一期欧盟委员会年度创新记分牌目录。\n"
        "- 目录覆盖创新投入、人才与研究体系、企业研发、知识资产、创新产出、产业转化和经济影响。\n"
        "- 中国作为全球竞争者和国家创新体系比较维度进入全部十一期记录。\n"
        "- 精选2016、2020、2024、2026四个跨期节点进入本地全文层；其余七期保留发现入口。\n\n"
        "2017和2021发生重要指标框架修订，跨期比较须优先使用各版共同指标或回查方法报告，避免把测量框架变化直接解释为创新绩效变化。\n",
        encoding="utf-8",
    )
    (root / "141_欧盟EIS创新记分牌跨期节点全文结果.md").write_text(
        "# 欧盟EIS创新记分牌跨期节点全文结果\n\n"
        f"- 新增官方PDF：{len(fulltext_rows)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        f"- China/Chinese词形共命中{total_china_hits}次，用于定位中国相对欧盟、美国、日本和韩国的创新绩效变化。\n"
        "- 跨期节点：2016早期25项指标基线、2020疫情与绿色数字转型节点、2024现行32项指标近期节点、2026当前全球比较节点。\n\n"
        "该系列属于欧盟委员会年度创新绩效测量，适合作为国家创新体系和政策效果的比较证据。综合指数受指标定义、基期、缺失值处理和框架修订影响，正式引用须回查当年方法说明、图表注释与页码。\n",
        encoding="utf-8",
    )
    print(
        f"catalog_added={len(new_rows)} fulltexts={len(fulltext_rows)} pages={total_pages} "
        f"bytes={total_bytes} chars={total_chars} china_hits={total_china_hits} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
