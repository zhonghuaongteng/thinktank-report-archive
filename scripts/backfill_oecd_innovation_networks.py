from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import date
from pathlib import Path

import httpx
from pypdf import PdfReader

try:
    from scripts.extract_viewpoint_pdf_slices import process_pdf
except ModuleNotFoundError:  # direct execution via python scripts/<name>.py
    from extract_viewpoint_pdf_slices import process_pdf


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"
TARGETS = (
    {
        "id": "C-OECD-DOI-FA11A0E0-EN",
        "title": "Strengthening the effectiveness and sustainability of international research infrastructures",
        "landing": "https://www.oecd.org/en/publications/strengthening-the-effectiveness-and-sustainability-of-international-research-infrastructures_fa11a0e0-en.html",
        "pdf": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/12/strengthening-the-effectiveness-and-sustainability-of-international-research-infrastructures_85cfbf50/fa11a0e0-en.pdf",
        "role": "跨国科研基础设施治理、融资与长期可持续性",
    },
    {
        "id": "C-OECD-DOI-76D78FBB-EN",
        "title": "The links between global value chains and global innovation networks",
        "landing": "https://www.oecd.org/en/publications/the-links-between-global-value-chains-and-global-innovation-networks_76d78fbb-en.html",
        "pdf": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/04/the-links-between-global-value-chains-and-global-innovation-networks_03343659/76d78fbb-en.pdf",
        "role": "全球创新网络、知识流动与价值获取机制",
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    catalog_path = root / "05_报告总目录.csv"
    light_path = root / "77_OECD_STI正式系列轻量目录.csv"
    catalog = read_csv(catalog_path)
    light = read_csv(light_path)
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    light_by_id = {row["报告ID"]: row for row in light}
    ledger: list[dict[str, str]] = []
    today = date.today().isoformat()
    for target in TARGETS:
        report_id = target["id"]
        if report_id not in catalog_by_id or report_id not in light_by_id:
            raise KeyError(f"missing OECD catalog record: {report_id}")
        response = httpx.get(target["pdf"], follow_redirects=True, timeout=300, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        data = response.content
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"not a PDF: {target['pdf']}")
        pdf_path = pdf_dir / f"{report_id}.pdf"
        pdf_path.write_bytes(data)
        process_pdf(pdf_path, text_dir, slice_dir)
        text_path = text_dir / f"{report_id}.txt"
        slice_path = slice_dir / f"{report_id}.md"
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        pages = len(PdfReader(pdf_path).pages)
        row = catalog_by_id[report_id]
        row["本地路径"] = str(pdf_path)
        row["正文完整度"] = "官方PDF全文已保存"
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "官方PDF已获取；已生成逐页文本与科技创新定向切片"
        light_row = light_by_id[report_id]
        light_row["全文策略"] = "已按真实科技创新机制缺口定点下载"
        ledger.append({
            "报告ID": report_id, "报告名称": target["title"], "机制角色": target["role"],
            "官方落地页": target["landing"], "官方PDF": target["pdf"], "本地PDF": str(pdf_path),
            "本地文本": str(text_path), "本地切片": str(slice_path), "PDF页数": str(pages),
            "字节数": str(len(data)), "提取文本字符数": str(len(extracted)),
            "SHA256": hashlib.sha256(data).hexdigest(), "获取日期": today,
        })
    write_csv(catalog_path, catalog, list(catalog[0]))
    write_csv(light_path, light, list(light[0]))
    write_csv(root / "128_OECD科研基础设施与全球创新网络定点全文台账.csv", ledger, list(ledger[0]))
    pages = sum(int(row["PDF页数"]) for row in ledger)
    chars = sum(int(row["提取文本字符数"]) for row in ledger)
    (root / "129_OECD科研基础设施与全球创新网络定点全文结果.md").write_text(
        "# OECD科研基础设施与全球创新网络定点全文结果\n\n"
        f"- 新增官方PDF：{len(ledger)}份，共{pages}页、{chars:,}字符。\n"
        "- 两份材料分别补充跨国科研基础设施的长期治理与融资机制，以及全球创新网络中的知识流动和价值获取机制。\n"
        "- 均由科技创新机制缺口触发；一般全球市场、旅游和产品监管材料继续保留在轻量目录层。\n",
        encoding="utf-8",
    )
    print(f"reports={len(ledger)} pages={pages} chars={chars}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
