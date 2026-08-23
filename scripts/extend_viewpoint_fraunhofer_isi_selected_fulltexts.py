from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path

import httpx
from pypdf import PdfReader

try:
    from scripts.extract_viewpoint_pdf_slices import process_pdf
except ModuleNotFoundError:  # direct execution via python scripts/<name>.py
    from extract_viewpoint_pdf_slices import process_pdf


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|prc|sino[- ]?)\b", re.I)

SELECTED_ITEMS: tuple[dict[str, str], ...] = (
    {
        "id": "C-FRAUNHOFER-ISI-DP-51",
        "title": "Measuring policy-driven innovation in energy efficiency",
        "axis": "研发投入与创新政策；产业创新与成果转化；创新测量与政策方法",
        "role": "能源效率政策驱动创新的识别与测量",
        "reason": "补充政策工具如何转化为节能技术创新产出的可复用测量框架",
    },
    {
        "id": "C-FRAUNHOFER-ISI-DP-53",
        "title": "Societal Grand Challenges from a technological perspective – Methods and identification of classes of the International Patent Classification IPC",
        "axis": "关键与新兴技术；创新测量与政策方法",
        "role": "以专利分类识别重大社会挑战相关技术",
        "reason": "补充从社会挑战反向映射技术领域和专利分类的研究方法",
    },
    {
        "id": "C-FRAUNHOFER-ISI-DP-65",
        "title": "The Roles of the State in the Governance of Socio-Technical Systems' Transformation",
        "axis": "研发投入与创新政策；产业创新与成果转化",
        "role": "社会—技术系统转型中的国家作用",
        "reason": "补充国家在方向设定、协调、能力建设与转型治理中的机制分析",
    },
    {
        "id": "C-FRAUNHOFER-ISI-DP-83",
        "title": "Innovation without growth? Exploring the (in)dependency of innovation on economic growth",
        "axis": "产业创新与成果转化；创新测量与政策方法",
        "role": "创新活动与经济增长关系的边界检验",
        "reason": "补充创新政策目标从单一增长导向向多目标转型的理论与经验边界",
    },
)

LEDGER_FIELDS = [
    "报告ID", "发布日期", "报告名称", "官方PDF入口", "本地原始PDF", "本地文本", "本地切片",
    "页数", "字节数", "清洗文本字符数", "China词形命中数", "SHA256", "科技创新主轴",
    "科技创新复用角色", "选择理由", "获取日期",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def selected_ids() -> set[str]:
    return {item["id"] for item in SELECTED_ITEMS}


def _existing_row(previous: dict[str, dict[str, str]], report_id: str, paths: tuple[Path, Path, Path]) -> dict[str, str] | None:
    row = previous.get(report_id)
    return row if row and all(path.exists() for path in paths) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    light_path = root / "84_Fraunhofer_ISI创新系统政策分析轻量目录.csv"
    ledger_path = root / "212_Fraunhofer_ISI科技创新机制跨期增补全文台账.csv"
    result_path = root / "213_Fraunhofer_ISI科技创新机制跨期增补全文结果.md"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"

    catalog = read_csv(catalog_path)
    light = read_csv(light_path)
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    light_by_id = {row["报告ID"]: row for row in light}
    previous_rows = read_csv(ledger_path) if ledger_path.exists() else []
    previous = {row["报告ID"]: row for row in previous_rows}
    ledger: list[dict[str, str]] = []
    reused = acquired = 0

    for item in SELECTED_ITEMS:
        report_id = item["id"]
        if report_id not in catalog_by_id or report_id not in light_by_id:
            raise KeyError(f"missing Fraunhofer ISI catalog record: {report_id}")
        catalog_row = catalog_by_id[report_id]
        light_row = light_by_id[report_id]
        pdf_path = pdf_dir / f"{report_id}.pdf"
        text_path = text_dir / f"{report_id}.txt"
        slice_path = slice_dir / f"{report_id}.md"
        saved = _existing_row(previous, report_id, (pdf_path, text_path, slice_path))
        if saved:
            ledger.append(saved)
            reused += 1
        else:
            pdf_url = light_row["官方PDF入口"]
            response = httpx.get(pdf_url, follow_redirects=True, timeout=300, headers={"User-Agent": USER_AGENT})
            response.raise_for_status()
            data = response.content
            if not data.startswith(b"%PDF"):
                raise RuntimeError(f"not a PDF: {pdf_url}")
            pdf_path.write_bytes(data)
            process_pdf(pdf_path, text_dir, slice_dir)
            extracted = text_path.read_text(encoding="utf-8", errors="replace")
            ledger.append({
                "报告ID": report_id,
                "发布日期": light_row["发布日期"],
                "报告名称": item["title"],
                "官方PDF入口": pdf_url,
                "本地原始PDF": str(pdf_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "页数": str(len(PdfReader(pdf_path).pages)),
                "字节数": str(len(data)),
                "清洗文本字符数": str(len(extracted)),
                "China词形命中数": str(len(CHINA_PATTERN.findall(extracted))),
                "SHA256": hashlib.sha256(data).hexdigest(),
                "科技创新主轴": item["axis"],
                "科技创新复用角色": item["role"],
                "选择理由": item["reason"],
                "获取日期": date.today().isoformat(),
            })
            acquired += 1

        catalog_row["本地路径"] = str(text_path)
        catalog_row["正文完整度"] = "官方PDF全文已保存"
        catalog_row["样本角色"] = "Fraunhofer ISI科技创新机制跨期精选全文"
        catalog_row["编码状态"] = "全文待观点编码"
        catalog_row["预期用途"] = item["role"]
        catalog_row["本地原始资产路径"] = str(pdf_path)
        catalog_row["原始资产状态"] = "Fraunhofer ISI官方PDF已获取；已生成文本与科技创新定向切片"
        light_row["全文策略"] = "已按科技创新机制跨期增量定点下载"

    write_csv(catalog_path, catalog, list(catalog[0]))
    write_csv(light_path, light, list(light[0]))
    write_csv(ledger_path, ledger, LEDGER_FIELDS)
    pages = sum(int(row["页数"]) for row in ledger)
    size = sum(int(row["字节数"]) for row in ledger)
    chars = sum(int(row["清洗文本字符数"]) for row in ledger)
    china_hits = sum(int(row["China词形命中数"]) for row in ledger)
    result_path.write_text(
        "# Fraunhofer ISI科技创新机制跨期增补全文结果\n\n"
        f"- 定点全文：{len(ledger)}份；本次新获取{acquired}份、复用{reused}份。\n"
        f"- 合计：{pages}页、{size:,}字节、{chars:,}个提取文本字符。\n"
        f"- China/Chinese/PRC词形命中：{china_hits}次；仅作跨国比较线索，不作为纳入门槛。\n"
        "- 主题覆盖政策驱动创新测量、重大挑战技术识别、国家转型治理和创新—增长关系，安全、供应链、出口管制与军事议题未触发本批全文。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} acquired={acquired} reused={reused} pages={pages} bytes={size} chars={chars} china_hits={china_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
