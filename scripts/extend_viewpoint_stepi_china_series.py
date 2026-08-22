from __future__ import annotations

import argparse
import csv
import hashlib
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from pypdf import PdfReader

try:
    from .extract_viewpoint_pdf_slices import process_pdf
except ImportError:
    from extract_viewpoint_pdf_slices import process_pdf


BASE_URL = "https://www.stepi.re.kr"

CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]

LEDGER_FIELDS = [
    "报告ID", "官方记录ID", "官方分类代码", "韩文报告类型", "发布日期", "观察窗", "韩文题名",
    "作者", "语言", "资料角色", "科技关联层级", "主题标签", "官方落地页", "官方PDF",
    "本地原始资产", "本地文本", "本地切片", "字节数", "SHA256", "PDF页数",
    "提取文本字符数", "文本质量", "本地状态", "错误", "获取日期",
]


@dataclass(frozen=True)
class SeriesItem:
    report_id: str
    record_id: str
    category: str
    year: int
    zip_file: str
    zip_key: str
    main_pdf: str


SERIES = (
    SeriesItem("C-STEPI-A0203-202", "202", "A0203", 2017, "F17-07.zip", "A0203_202", "F17-07.pdf"),
    SeriesItem("C-STEPI-A0203-218", "218", "A0203", 2018, "F18-09.zip", "A0203_218", "F18-09.pdf"),
    SeriesItem("C-STEPI-A0203-227", "227", "A0203", 2019, "F19-07.zip", "A0203_227", "F19-07.pdf"),
    SeriesItem("C-STEPI-A0201-962", "962", "A0201", 2020, "P20-26.zip", "51e1fd4a-0926-4a9a-97a4-97ab18f2758a.zip", "P20-26-01.pdf"),
    SeriesItem("C-STEPI-A0201-1021", "1021", "A0201", 2021, "P21-32.zip", "cda8a3bf-728a-4754-a8c0-a8e49c7ee79f.zip", "P21-32-01.pdf"),
)


ATTACHMENT_FIELDS = [
    "附件ID", "报告ID", "卷别", "年份", "韩文题名", "官方落地页", "官方ZIP", "ZIP内文件名",
    "本地原始资产", "本地文本", "本地切片", "字节数", "SHA256", "PDF页数", "提取文本字符数",
    "文本质量", "获取日期",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_theme_rows(ledger_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"主题标签": theme, "科技关联层级": row["科技关联层级"], "报告ID": row["报告ID"],
         "发布日期": row["发布日期"], "观察窗": row["观察窗"], "报告名称": row["报告名称"],
         "资料角色": row["资料角色"], "本地原始资产": row["本地原始资产"], "本地文本": row["本地文本"],
         "官方落地页": row["官方落地页"], "本地状态": row["本地状态"]}
        for row in ledger_rows for theme in row["主题标签"].split("；")
    ]


def classify_text_quality(chars: int, pages: int, has_asset: bool) -> str:
    if not has_asset:
        return "官方目录无PDF正文"
    if not pages or chars / pages < 200:
        return "图像型PDF，OCR待补"
    return "可检索文本"


def result_summary(statuses: Counter) -> str:
    return (
        f"官方PDF保存：{statuses['官方PDF已保存并校验']}项；"
        f"同版PDF关联：{statuses['关联既有官方PDF']}项；"
        f"官方目录无PDF：{statuses['官方目录无PDF']}项；"
        f"获取失败：{statuses['获取失败']}项。"
    )


def official_landing_url(item: SeriesItem) -> str:
    return f"{BASE_URL}/site/stepiko/report/View.do?cateCont={item.category}&reIdx={item.record_id}"


def official_zip_url(item: SeriesItem) -> str:
    return (
        f"{BASE_URL}/common/report/Download.do?reIdx={item.record_id}"
        f"&streFileNm={item.zip_key}&cateCont={item.category}&purpose=1&jobGroup=1"
    )


def choose_pdf_entries(zip_path: Path, item: SeriesItem) -> tuple[str, str]:
    with zipfile.ZipFile(zip_path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".pdf") and not name.endswith("/")]
    if len(names) != 2:
        raise ValueError(f"{item.zip_file} must contain exactly two PDFs; found {len(names)}")
    main = next((name for name in names if Path(name).name == item.main_pdf), "")
    if not main:
        raise ValueError(f"{item.zip_file} is missing expected main PDF {item.main_pdf}")
    supplement = next(name for name in names if name != main)
    return main, supplement


def extract_pdf(zip_path: Path, entry: str, destination: Path) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        data = archive.read(entry)
    if not data.startswith(b"%PDF"):
        raise ValueError(f"{entry} is not a PDF")
    destination.write_bytes(data)
    if len(PdfReader(str(destination)).pages) < 1:
        raise ValueError(f"{entry} has no pages")


def asset_metrics(path: Path, text_path: Path) -> dict[str, str]:
    data = path.read_bytes()
    chars = len(text_path.read_text(encoding="utf-8", errors="replace"))
    pages = len(PdfReader(str(path)).pages)
    return {
        "字节数": str(len(data)),
        "SHA256": hashlib.sha256(data).hexdigest(),
        "PDF页数": str(pages),
        "提取文本字符数": str(chars),
        "文本质量": classify_text_quality(chars, pages, True),
    }


def update_series(root: Path, zip_dir: Path) -> list[dict[str, str]]:
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    ledger_path = root / "60_STEPI韩文科技与中国专题增补台账.csv"
    catalog_path = root / "05_报告总目录.csv"
    ledger = read_csv(ledger_path)
    catalog = read_csv(catalog_path)
    ledger_by_id = {row["报告ID"]: row for row in ledger}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    attachments: list[dict[str, str]] = []

    for item in SERIES:
        zip_path = zip_dir / item.zip_file
        if not zip_path.exists():
            raise FileNotFoundError(zip_path)
        main_entry, supplement_entry = choose_pdf_entries(zip_path, item)
        for role, entry, suffix in (("主卷", main_entry, ""), ("附卷", supplement_entry, "-SUPP")):
            attachment_id = f"{item.report_id}{suffix}"
            pdf_path = pdf_dir / f"{attachment_id}.pdf"
            text_path = text_dir / f"{attachment_id}.txt"
            slice_path = slice_dir / f"{attachment_id}.md"
            if not pdf_path.exists():
                extract_pdf(zip_path, entry, pdf_path)
            if not text_path.exists() or not slice_path.exists():
                process_pdf(pdf_path, text_dir, slice_dir)
            metrics = asset_metrics(pdf_path, text_path)
            attachments.append({
                "附件ID": attachment_id,
                "报告ID": item.report_id,
                "卷别": role,
                "年份": str(item.year),
                "韩文题名": ledger_by_id[item.report_id]["韩文题名"],
                "官方落地页": official_landing_url(item),
                "官方ZIP": official_zip_url(item),
                "ZIP内文件名": entry,
                "本地原始资产": str(pdf_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                **metrics,
                "获取日期": date.today().isoformat(),
            })

        main = attachments[-2]
        ledger_row = ledger_by_id[item.report_id]
        ledger_row.update({
            "官方落地页": official_landing_url(item),
            "官方PDF": official_zip_url(item),
            "本地原始资产": main["本地原始资产"],
            "本地文本": main["本地文本"],
            "本地切片": main["本地切片"],
            "字节数": main["字节数"],
            "SHA256": main["SHA256"],
            "PDF页数": main["PDF页数"],
            "提取文本字符数": main["提取文本字符数"],
            "文本质量": main["文本质量"],
            "本地状态": "官方PDF已保存并校验",
            "错误": "",
            "获取日期": date.today().isoformat(),
        })
        catalog_row = catalog_by_id[item.report_id]
        catalog_row.update({
            "原文链接": official_landing_url(item),
            "正文完整度": "官方ZIP主卷全文已保存",
            "本地原始资产路径": main["本地原始资产"],
            "原始资产状态": "官方ZIP主卷已提取并校验",
        })

    write_csv(ledger_path, ledger, LEDGER_FIELDS)
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "73_STEPI中国先进技术连续序列附卷台账.csv", attachments, ATTACHMENT_FIELDS)

    theme_input = [{**row, "报告名称": row["韩文题名"]} for row in ledger]
    write_csv(
        root / "62_STEPI韩文科技与中国主题索引.csv",
        build_theme_rows(theme_input),
        ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"],
    )
    matrix_counts = Counter(
        (theme, row["科技关联层级"], row["观察窗"], row["韩文报告类型"], row["本地状态"])
        for row in ledger for theme in row["主题标签"].split("；")
    )
    write_csv(
        root / "63_STEPI韩文科技与中国复用矩阵.csv",
        [{"主题标签": key[0], "科技关联层级": key[1], "观察窗": key[2], "韩文报告类型": key[3], "本地状态": key[4], "材料数": str(value)} for key, value in sorted(matrix_counts.items())],
        ["主题标签", "科技关联层级", "观察窗", "韩文报告类型", "本地状态", "材料数"],
    )
    return attachments


def write_results(root: Path, attachments: list[dict[str, str]]) -> None:
    ledger = read_csv(root / "60_STEPI韩文科技与中国专题增补台账.csv")
    statuses = Counter(row["本地状态"] for row in ledger)
    quality = Counter(row["文本质量"] for row in ledger)
    china = sum("中国科技与国际比较" in row["主题标签"] for row in ledger)
    core = sum(row["科技关联层级"] == "核心科技直接材料" for row in ledger)
    report = f"""# STEPI近十年韩文科技与中国专题库增补结果

- 纳入2016—2026年正式研究成果：{len(ledger)}项。
- 核心科技直接材料：{core}项；中国科技与国际比较材料：{china}项。
- 可检索PDF正文：{quality['可检索文本']}项；图像型PDF、OCR待补：{quality['图像型PDF，OCR待补']}项。
- {result_summary(statuses)}
- 其中中国先进技术连续序列已补齐2017—2021年5项主卷和5项附卷，共{len(attachments)}份官方PDF。

## 纳入边界

总目录保留STEPI 2016—2026年正式研究的轻量元数据。本轮全文仅补齐直接服务科学与技术创新研究的中国先进技术连续序列，未对其余目录条目实施批量下载。

## 使用边界

科学体系、技术创新、研发治理、人才与科研组织、产业转化、开放合作构成分析主轴；中国作为横向比较维度。安全、供应链和治理边界仅在解释创新投入、组织方式、技术路线或合作条件变化时使用。机器主题标签仅作检索入口；精确引用须回查官方PDF、韩文原句与页码。
"""
    (root / "61_STEPI韩文科技与中国专题增补结果.md").write_text(report, encoding="utf-8")
    series_report = """# STEPI中国先进技术连续序列增补结果

本地已保存2017—2021年五项连续研究的主卷与附卷，共10份官方PDF，并生成全文文本与页级切片。序列覆盖航天、机器人与增材制造、无人机、智能出行、人工智能、5G、区块链、智慧教育和数字医疗，可直接支持中国技术能力、应用场景和创新体系演变的跨年度比较。

目录层仍保持轻量；后续全文补充由机构—节点—主题缺口触发，不将STEPI其余正式报告自动转为下载队列。
"""
    (root / "74_STEPI中国先进技术连续序列结果.md").write_text(series_report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--zip-dir", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    attachments = update_series(root, args.zip_dir.resolve())
    write_results(root, attachments)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
