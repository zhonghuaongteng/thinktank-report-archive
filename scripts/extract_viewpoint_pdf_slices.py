from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader


KEYWORDS = {
    "T1_国家研发与方向设定": [
        "government", "public investment", "public funding", "state role", "directionality",
        "mission-oriented", "industrial strategy", "industrial policy",
    ],
    "T2_市场与产业政策边界": [
        "market failure", "market forces", "business r&d", "private sector", "competition policy",
        "picking winners", "commercialisation", "commercialization",
    ],
    "T4_国际合作与开放": [
        "international cooperation", "international co-operation", "open science", "openness",
        "allies", "partnership", "multilateral", "collaboration",
    ],
    "T5_供应链与技术依赖": [
        "supply chain", "dependency", "dependence", "resilience", "self-sufficiency",
        "technological sovereignty", "strategic autonomy", "de-risk",
    ],
    "T7_管制与研究安全": [
        "export control", "investment screening", "research security", "securitisation",
        "securitization", "economic security", "technology control",
    ],
    "T8_新兴技术治理": [
        "technology governance", "responsible innovation", "responsible research", "shared values",
        "artificial intelligence", "emerging technolog", "ethics", "trust",
    ],
    "T10_预见与优先领域": [
        "foresight", "horizon scanning", "strategic intelligence", "priority setting",
        "critical technolog", "key technolog", "scenario",
    ],
}


def clean(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[\ud800-\udfff]", "\ufffd", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def excerpts(text: str, terms: list[str], limit: int = 3) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    lower = flat.lower()
    spans: list[tuple[int, int]] = []
    for term in terms:
        cursor = 0
        while len(spans) < limit * 3:
            index = lower.find(term, cursor)
            if index < 0:
                break
            start = max(0, index - 280)
            end = min(len(flat), index + len(term) + 520)
            if not any(abs(start - old_start) < 300 for old_start, _ in spans):
                spans.append((start, end))
            cursor = index + len(term)
    spans.sort()
    return [flat[start:end].strip() for start, end in spans[:limit]]


def process_pdf(path: Path, text_dir: Path, slice_dir: Path) -> None:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            value = clean(page.extract_text() or "")
        except Exception as exc:  # damaged page should not abort the batch
            value = f"[extract_error: {exc}]"
        pages.append(value)

    full = []
    for page_number, value in enumerate(pages, start=1):
        full.append(f"\n===== PDF_PAGE {page_number} =====\n{value}\n")
    (text_dir / f"{path.stem}.txt").write_text("".join(full).rstrip() + "\n", encoding="utf-8")

    hits: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for page_number, value in enumerate(pages, start=1):
        for tracer, terms in KEYWORDS.items():
            page_hits = excerpts(value, terms)
            for excerpt in page_hits:
                hits[tracer].append((page_number, excerpt))

    display_path = path.relative_to(path.parents[2])
    output = [
        f"# {path.stem} 原文切片",
        "",
        f"- 原文：`{display_path}`",
        f"- PDF页数：{len(pages)}",
        "- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。",
        "",
        "## 执行摘要与开篇候选",
        "",
    ]
    for page_number, value in enumerate(pages[:12], start=1):
        if re.search(r"executive summary|summary|key (findings|messages|takeaways)|abstract", value, re.I):
            output.extend([f"### PDF页 {page_number}", "", value[:6000].rstrip(), ""])
    for tracer in KEYWORDS:
        output.extend([f"## {tracer}", ""])
        selected = hits.get(tracer, [])[:8]
        if not selected:
            output.extend(["未自动命中；需人工按目录复核。", ""])
            continue
        for page_number, excerpt in selected:
            output.extend([f"- PDF页{page_number}：{excerpt}", ""])
    (slice_dir / f"{path.stem}.md").write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--text-dir", type=Path, required=True)
    parser.add_argument("--slice-dir", type=Path, required=True)
    args = parser.parse_args()
    args.text_dir.mkdir(parents=True, exist_ok=True)
    args.slice_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(args.input.glob("*.pdf")):
        process_pdf(path, args.text_dir, args.slice_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
