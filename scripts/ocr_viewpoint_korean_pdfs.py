from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


KOREAN_TERMS = (
    "중국", "과학기술", "과학", "기술", "연구", "혁신", "정책", "인공지능",
    "반도체", "바이오", "창업", "국제협력", "기초연구", "연구개발", "R&D",
)


def ocr_engine_kwargs() -> dict[str, object]:
    return {
        "lang": "korean",
        "ocr_version": "PP-OCRv5",
        "use_doc_orientation_classify": False,
        "use_doc_unwarping": False,
        "use_textline_orientation": False,
        "enable_mkldnn": False,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def result_lines(result: object, minimum_score: float = 0.45) -> list[str]:
    payload = getattr(result, "json", result)
    if callable(payload):
        payload = payload()
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        return []
    data = payload.get("res", payload)
    texts = data.get("rec_texts", [])
    scores = data.get("rec_scores", [])
    if not scores:
        scores = [1.0] * len(texts)
    return [
        re.sub(r"\s+", " ", str(text)).strip()
        for text, score in zip(texts, scores)
        if text and float(score) >= minimum_score
    ]


def classify_ocr_quality(text: str, pages: int) -> str:
    compact = re.sub(r"\s+", "", text)
    hangul = len(re.findall(r"[가-힣]", compact))
    if pages and len(compact) / pages >= 220 and hangul / max(1, len(compact)) >= 0.2:
        return "韩文OCR可检索文本"
    return "图像型PDF，OCR待补"


def apply_ocr_metadata(
    row: dict[str, str], text_path: str | Path, slice_path: str | Path, full_text: str
) -> None:
    row["本地文本"] = str(text_path)
    row["本地切片"] = str(slice_path)
    row["提取文本字符数"] = str(len(full_text))
    row["文本质量"] = "韩文OCR可检索文本"
    row["本地状态"] = "官方PDF已保存并完成韩文OCR"


def apply_catalog_ocr_metadata(row: dict[str, str], text_path: str | Path) -> None:
    row["本地路径"] = str(text_path)
    row["正文完整度"] = "本地韩文OCR全文已保存"
    row["原始资产状态"] = "官方PDF已保存并完成韩文OCR"


def make_slice(stem: str, pdf_path: Path, page_texts: list[str]) -> str:
    lines = [
        f"# {stem} 韩文OCR切片", "", f"- 原文：`{pdf_path}`",
        f"- PDF页数：{len(page_texts)}", "- 页码口径：PDF物理页码。",
        "- 文本来源：本地韩文OCR；精确引用须回查原始扫描页。", "", "## 开篇候选", "",
    ]
    for number, text in enumerate(page_texts[:8], start=1):
        if text.strip():
            lines.extend([f"### PDF页 {number}", "", text[:3500].strip(), ""])
    lines.extend(["## 主题命中页", ""])
    hits = 0
    for number, text in enumerate(page_texts, start=1):
        matched = [term for term in KOREAN_TERMS if term.lower() in text.lower()]
        if not matched:
            continue
        excerpt = re.sub(r"\s+", " ", text).strip()[:1800]
        lines.extend([f"- PDF页{number}；命中：{'；'.join(matched)}", "", excerpt, ""])
        hits += 1
        if hits >= 20:
            break
    if not hits:
        lines.extend(["未自动命中；需回查OCR全文。", ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--ids", required=True)
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument("--max-pages", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        import fitz
        import numpy as np
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise SystemExit(f"Korean OCR dependencies unavailable: {exc}")

    root = args.research.resolve()
    ledger_path = root / args.ledger
    rows = read_csv(ledger_path)
    catalog_path = root / "05_报告总目录.csv"
    catalog_rows = read_csv(catalog_path)
    catalog_indexed = {row["报告ID"]: row for row in catalog_rows}
    selected = {value.strip() for value in args.ids.split(",") if value.strip()}
    indexed = {row["报告ID"]: row for row in rows}
    missing = selected - set(indexed)
    if missing:
        raise ValueError(f"selected IDs missing from ledger: {sorted(missing)}")

    engine = PaddleOCR(**ocr_engine_kwargs())
    completed = 0
    for report_id in sorted(selected):
        row = indexed[report_id]
        pdf_path = Path(row["本地原始资产"])
        text_path = root / "03_证据底稿" / "文本" / f"{report_id}.txt"
        slice_path = root / "03_证据底稿" / "切片" / f"{report_id}.md"
        if not args.dry_run and text_path.exists() and slice_path.exists():
            existing_text = text_path.read_text(encoding="utf-8")
            existing_pages = existing_text.count("===== OCR_PAGE ")
            if existing_pages and classify_ocr_quality(existing_text, existing_pages) == "韩文OCR可检索文本":
                apply_ocr_metadata(row, text_path, slice_path, existing_text)
                apply_catalog_ocr_metadata(catalog_indexed[report_id], text_path)
                write_csv(ledger_path, rows)
                write_csv(catalog_path, catalog_rows)
                completed += 1
                print(f"{report_id} resumed_existing_ocr chars={len(existing_text)}", flush=True)
                continue
        document = fitz.open(pdf_path)
        limit = min(len(document), args.max_pages) if args.max_pages else len(document)
        page_texts: list[str] = []
        for index in range(limit):
            page = document[index]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), alpha=False)
            image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, pixmap.n)
            results = engine.predict(image)
            lines: list[str] = []
            for result in results:
                lines.extend(result_lines(result))
            page_texts.append("\n".join(lines))
            print(f"{report_id} page={index + 1}/{limit} lines={len(lines)}", flush=True)
        document.close()

        full_text = "".join(
            f"\n===== OCR_PAGE {number} =====\n{text}\n"
            for number, text in enumerate(page_texts, start=1)
        ).rstrip() + "\n"
        quality = classify_ocr_quality(full_text, limit)
        if args.dry_run:
            print(f"{report_id} dry_run quality={quality} chars={len(full_text)}", flush=True)
            continue
        if quality != "韩文OCR可检索文本":
            print(f"{report_id} quality_rejected chars={len(full_text)}", flush=True)
            continue

        text_path.write_text(full_text, encoding="utf-8")
        slice_path.write_text(make_slice(report_id, pdf_path, page_texts), encoding="utf-8")
        apply_ocr_metadata(row, text_path, slice_path, full_text)
        apply_catalog_ocr_metadata(catalog_indexed[report_id], text_path)
        write_csv(ledger_path, rows)
        write_csv(catalog_path, catalog_rows)
        completed += 1

    if not args.dry_run:
        write_csv(ledger_path, rows)
    print(f"selected={len(selected)} completed={completed} rejected={len(selected) - completed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
