from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(args.pdf)
    for i, page in enumerate(pdf):
        image = page.render(scale=1.5).to_pil().convert("RGB")
        image.save(args.output / f"page-{i + 1:02d}.jpg", quality=92)
    print(len(pdf))


if __name__ == "__main__":
    main()
