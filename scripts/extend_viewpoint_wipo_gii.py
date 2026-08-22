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


@dataclass(frozen=True)
class GiiItem:
    year: int
    landing: str
    pdf: str
    selected: bool = False

    @property
    def report_id(self) -> str:
        return f"C-WIPO-GII-{self.year}"


ITEMS = (
    GiiItem(2016, "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2016.pdf", "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2016.pdf", True),
    GiiItem(2017, "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2017.pdf", "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2017.pdf"),
    GiiItem(2018, "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2018.pdf", "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2018.pdf"),
    GiiItem(2019, "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2019.pdf", "https://www.wipo.int/edocs/pubdocs/en/wipo_pub_gii_2019.pdf"),
    GiiItem(2020, "https://www.wipo.int/en/web/global-innovation-index/2020/index", "https://www.wipo.int/documents/d/global-innovation-index/docs-en-2020-wipo_pub_gii_2020.pdf", True),
    GiiItem(2021, "https://www.wipo.int/en/web/global-innovation-index/2021/index", "https://www.wipo.int/documents/d/global-innovation-index/docs-en-2021-wipo_pub_gii_2021.pdf"),
    GiiItem(2022, "https://www.wipo.int/en/web/global-innovation-index/2022/index", "https://www.wipo.int/documents/d/global-innovation-index/docs-en-wipo-pub-2000-2022-en-main-report-global-innovation-index-2022-15th-edition.pdf"),
    GiiItem(2023, "https://www.wipo.int/en/web/global-innovation-index/2023/index", "https://www.wipo.int/documents/d/global-innovation-index/docs-en-wipo-pub-2000-2023-en-main-report-global-innovation-index-2023-16th-edition.pdf"),
    GiiItem(2024, "https://www.wipo.int/en/web/global-innovation-index/2024/index", "https://www.wipo.int/edocs/pubdocs/en/wipo-pub-2000-2024-en-global-innovation-index-2024.pdf", True),
    GiiItem(2025, "https://www.wipo.int/en/web/global-innovation-index/2025/index", "https://www.wipo.int/web-publications/global-innovation-index-2025/assets/80937/global-innovation-index-2025-en.pdf"),
)
CHINA_PROFILE = {
    "id": "C-WIPO-GII-CHINA-2025",
    "title": "Global Innovation Index 2025: China ranking profile",
    "landing": "https://www.wipo.int/en/web/global-innovation-index/2025/index",
    "pdf": "https://www.wipo.int/edocs/gii-ranking/2025/cn.pdf",
}


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


def catalog_row(report_id: str, year: int, title: str, landing: str, pdf: str, selected: bool) -> dict[str, str]:
    return {
        "报告ID": report_id,
        "机构ID": "wipo-gii",
        "机构英文名": "World Intellectual Property Organization",
        "国家或地区": "国际组织",
        "发布日期": f"{year}-01-01",
        "观察窗": observation_window(year),
        "报告名称": title,
        "报告类型": "WIPO Global Innovation Index/国家创新画像",
        "原文链接": landing,
        "本地路径": "",
        "正文完整度": "官方PDF入口元数据",
        "优先级": "P0-China-innovation-candidate" if "CHINA" in report_id else "P1-STI-light-catalog",
        "示踪问题": THEMES,
        "机构观点等级": "WIPO正式旗舰指标成果；排名与解释须按当年方法口径使用",
        "样本角色": "WIPO全球创新指数近十年轻量目录",
        "编码状态": "目录待筛选",
        "预期用途": "国家创新体系、研发投入、知识产出、产业转化、创新集群及中国比较",
        "本地原始资产路径": "",
        "原始资产状态": "待定点下载" if selected else "官方入口已保存；连续系列已完成跨期抽样",
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
    catalog = [row for row in read_csv(catalog_path) if row.get("样本角色") != "WIPO全球创新指数近十年轻量目录"]
    new_rows = [catalog_row(item.report_id, item.year, f"Global Innovation Index {item.year}", item.landing, item.pdf, item.selected) for item in ITEMS]
    new_rows.append(catalog_row(CHINA_PROFILE["id"], 2025, CHINA_PROFILE["title"], CHINA_PROFILE["landing"], CHINA_PROFILE["pdf"], True))
    existing_ids = {row["报告ID"] for row in catalog}
    if existing_ids & {row["报告ID"] for row in new_rows}:
        raise RuntimeError("WIPO GII report ID collides with an existing non-series record")
    catalog.extend(new_rows)
    catalog_by_id = {row["报告ID"]: row for row in catalog}

    fulltext_targets = [item for item in ITEMS if item.selected]
    downloads = [(item.report_id, item.year, f"Global Innovation Index {item.year}", item.landing, item.pdf, "跨期主报告节点") for item in fulltext_targets]
    downloads.append((CHINA_PROFILE["id"], 2025, CHINA_PROFILE["title"], CHINA_PROFILE["landing"], CHINA_PROFILE["pdf"], "2025中国国家创新画像"))
    fulltext_rows: list[dict[str, str]] = []
    today = date.today().isoformat()
    for report_id, year, title, landing, pdf_url, role in downloads:
        pdf_path = pdf_dir / f"{report_id}.pdf"
        text_path = text_dir / f"{report_id}.txt"
        slice_path = slice_dir / f"{report_id}.md"
        if pdf_path.exists() and text_path.exists() and slice_path.exists():
            data = pdf_path.read_bytes()
        else:
            data = fetch_pdf(pdf_url)
            pdf_path.write_bytes(data)
            process_pdf(pdf_path, text_dir, slice_dir)
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        pages = len(PdfReader(pdf_path).pages)
        if len(extracted) < 5_000:
            raise RuntimeError(f"extracted text too short: {report_id} {len(extracted)}")
        row = catalog_by_id[report_id]
        row["本地路径"] = str(pdf_path)
        row["正文完整度"] = "官方PDF全文已保存"
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "官方PDF已获取；已生成逐页文本与科技创新定向切片"
        fulltext_rows.append({
            "报告ID": report_id, "年份": str(year), "报告名称": title, "序列角色": role,
            "官方落地页": landing, "官方PDF": pdf_url, "本地PDF": str(pdf_path),
            "本地文本": str(text_path), "本地切片": str(slice_path), "PDF页数": str(pages),
            "字节数": str(len(data)), "提取文本字符数": str(len(extracted)),
            "SHA256": hashlib.sha256(data).hexdigest(), "中国关联": "是；含中国创新投入、产出、集群或国家排名",
            "获取日期": today,
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    light_rows = []
    for item in ITEMS:
        light_rows.append({
            "报告ID": item.report_id, "发布日期": f"{item.year}-01-01", "日期精度": "年；以1月1日作排序占位",
            "报告名称": f"Global Innovation Index {item.year}", "官方落地页": item.landing, "官方PDF入口": item.pdf,
            "科学技术创新主题": THEMES, "中国关联": "是；年度排名与指标包含中国",
            "全文策略": "已定点下载" if item.selected else "保留轻量目录；连续系列已完成跨期抽样", "采集日期": today,
        })
    write_csv(root / "124_WIPO全球创新指数近十年轻量目录.csv", light_rows, list(light_rows[0]))
    write_csv(root / "126_WIPO全球创新指数跨期节点全文台账.csv", fulltext_rows, list(fulltext_rows[0]))
    total_pages = sum(int(row["PDF页数"]) for row in fulltext_rows)
    total_bytes = sum(int(row["字节数"]) for row in fulltext_rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in fulltext_rows)
    (root / "125_WIPO全球创新指数近十年轻量目录结果.md").write_text(
        "# WIPO全球创新指数近十年轻量目录结果\n\n"
        "- 建立2016—2025十期官方年度目录，全部记录官方附件入口。\n"
        "- 中国作为横向维度进入每期记录；目录用于议题、指标和版本发现。\n"
        "- 精选2016、2020、2024三期主报告及2025中国国家画像进入本地全文层。\n\n"
        "年度排名和指标口径会修订，跨年比较须回查当年方法、经济体覆盖范围和数据可得性说明。\n",
        encoding="utf-8",
    )
    (root / "127_WIPO全球创新指数跨期节点全文结果.md").write_text(
        "# WIPO全球创新指数跨期节点全文结果\n\n"
        f"- 新增官方PDF：{len(fulltext_rows)}份，共{total_pages}页、{total_bytes:,}字节、{total_chars:,}字符。\n"
        "- 主报告节点：2016、2020、2024；近期中国证据：2025中国国家画像。\n"
        "- 可用于国家创新体系、科研与人力资本、知识和技术产出、产业转化、创新集群及中国位置的跨期检索。\n\n"
        "自动切片只作定位。排名变化可能来自数据修订、指标调整和经济体覆盖变化，正式比较须同时核对方法章节。\n",
        encoding="utf-8",
    )
    print(f"catalog_added={len(new_rows)} fulltexts={len(fulltext_rows)} pages={total_pages} bytes={total_bytes} chars={total_chars} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
