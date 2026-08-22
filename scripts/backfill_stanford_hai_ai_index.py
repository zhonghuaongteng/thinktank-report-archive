from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import date
from pathlib import Path

import httpx
from pypdf import PdfReader

from extract_viewpoint_pdf_slices import process_pdf


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"
TARGETS = (
    {
        "id": "C-STANFORD-HAI-AI-INDEX-2018",
        "year": "2018",
        "title": "The 2018 AI Index Report",
        "landing": "https://hai.stanford.edu/ai-index/2018-ai-index-report",
        "pdf": "https://hai.stanford.edu/assets/files/ai_index_2018_annual_report.pdf",
        "role": "早期AI科研、技术能力、人才与全球比较基线",
    },
    {
        "id": "C-STANFORD-HAI-AI-INDEX-2022",
        "year": "2022",
        "title": "The 2022 AI Index Report",
        "landing": "https://hai.stanford.edu/ai-index/2022-ai-index-report",
        "pdf": "https://hai.stanford.edu/assets/files/2022-ai-index-report_master.pdf",
        "role": "生成式AI扩散前的科研、产业、人才与政策中期节点",
    },
    {
        "id": "C-STANFORD-HAI-AI-INDEX-2025",
        "year": "2025",
        "title": "The 2025 AI Index Report",
        "landing": "https://hai.stanford.edu/ai-index/2025-ai-index-report",
        "pdf": "https://hai.stanford.edu/assets/files/hai_ai_index_report_2025.pdf",
        "role": "前沿模型、研发投入、科学应用、人才与中国比较近期节点",
    },
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fetch_pdf(url: str) -> bytes:
    response = httpx.get(url, follow_redirects=True, timeout=300, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    data = response.content
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"official attachment is not a PDF: {url}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    catalog_path = root / "05_报告总目录.csv"
    light_path = root / "86_Stanford_HAI科学技术创新轻量目录.csv"
    catalog = read_csv(catalog_path)
    light = read_csv(light_path)
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    light_by_id = {row["报告ID"]: row for row in light}
    today = date.today().isoformat()
    ledger: list[dict[str, str]] = []

    for target in TARGETS:
        report_id = target["id"]
        if report_id not in catalog_by_id or report_id not in light_by_id:
            raise KeyError(f"missing catalog record: {report_id}")
        data = fetch_pdf(target["pdf"])
        pdf_path = pdf_dir / f"{report_id}.pdf"
        pdf_path.write_bytes(data)
        process_pdf(pdf_path, text_dir, slice_dir)
        text_path = text_dir / f"{report_id}.txt"
        slice_path = slice_dir / f"{report_id}.md"
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        pages = len(PdfReader(pdf_path).pages)
        if len(extracted) < 10_000:
            raise RuntimeError(f"extracted text too short: {report_id} {len(extracted)}")

        catalog_row = catalog_by_id[report_id]
        catalog_row["本地路径"] = str(pdf_path)
        catalog_row["正文完整度"] = "官方PDF全文已保存"
        catalog_row["本地原始资产路径"] = str(pdf_path)
        catalog_row["原始资产状态"] = "官方PDF已获取；已生成逐页文本与科技创新定向切片"
        light_row = light_by_id[report_id]
        light_row["官方PDF入口"] = target["pdf"]
        light_row["全文策略"] = "已按连续序列缺口定点下载；其余年份继续执行轻量目录策略"
        ledger.append(
            {
                "报告ID": report_id,
                "年份": target["year"],
                "报告名称": target["title"],
                "连续序列角色": target["role"],
                "官方落地页": target["landing"],
                "官方PDF": target["pdf"],
                "本地PDF": str(pdf_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "PDF页数": str(pages),
                "字节数": str(len(data)),
                "提取文本字符数": str(len(extracted)),
                "SHA256": hashlib.sha256(data).hexdigest(),
                "中国关联": "报告含中国科研、技术、人才、产业和国际比较指标；具体命题须回查相应页码",
                "获取日期": today,
            }
        )

    write_csv(catalog_path, catalog, list(catalog[0]))
    write_csv(light_path, light, list(light[0]))
    ledger_path = root / "122_Stanford_HAI_AI_Index连续序列定点全文台账.csv"
    write_csv(ledger_path, ledger, list(ledger[0]))
    total_pages = sum(int(row["PDF页数"]) for row in ledger)
    total_bytes = sum(int(row["字节数"]) for row in ledger)
    total_chars = sum(int(row["提取文本字符数"]) for row in ledger)
    years = "、".join(row["年份"] for row in ledger)
    result = f"""# Stanford HAI AI Index连续序列定点全文结果

- 定点补齐年份：{years}，共{len(ledger)}份官方全文。
- PDF共{total_pages}页，原始资产{total_bytes:,}字节，可检索文本{total_chars:,}字符。
- 本地AI Index年度全文序列现覆盖2017、2018、2019、2021、2022、2023、2024、2025、2026。

## 采集判断

三个年份分别构成早期基线、中期节点和近期节点，可支持近十年AI科研产出、技术性能、研发投入、人才、产业化、科学应用及中国比较的连续观察。本批只补齐既有序列缺口，未对Stanford HAI全部出版物进行全文扩张。

## 加工边界

自动切片按科学体系、关键技术、研发治理、人才与科研组织、产业创新、国际合作及中国科技横向维度生成。题名、指标图表和自动切片可用于检索定位；正式引用仍需核对PDF物理页码、印刷页码和当年指标口径。
"""
    (root / "123_Stanford_HAI_AI_Index连续序列定点全文结果.md").write_text(result, encoding="utf-8")
    print(f"reports={len(ledger)} pages={total_pages} bytes={total_bytes} chars={total_chars}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
