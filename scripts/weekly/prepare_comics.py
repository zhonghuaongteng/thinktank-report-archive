"""把生成好的插画原图统一转成网页用的 JPEG（3:2 居中裁切，宽 1200 像素）。

用法：uv run python scripts/weekly/prepare_comics.py <原图目录> <成品目录>/comics <篇号前缀>
原图目录内按 1.jpg/1.png … 4.jpg 命名；输出 <前缀>-1.jpg … 供正文 <div class="comic"> 引用。
"""
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    src, dst, prefix = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.iterdir()):
        if f.stem.isdigit() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            im = Image.open(f).convert("RGB")
            w, h = im.size
            tw, th = (w, round(w * 2 / 3)) if w * 2 / 3 <= h else (round(h * 3 / 2), h)
            im = im.crop(((w - tw) // 2, (h - th) // 2, (w - tw) // 2 + tw, (h - th) // 2 + th))
            im = im.resize((1200, 800), Image.LANCZOS)
            out = dst / f"{prefix}-{f.stem}.jpg"
            im.save(out, "JPEG", quality=84, optimize=True)
            print(out.name, out.stat().st_size // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
