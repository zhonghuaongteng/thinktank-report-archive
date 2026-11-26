"""把一期周报正文（Markdown）渲染成自包含网页和手机尺寸 PDF。

用法：uv run python scripts/weekly/render_issue.py <issue.md> <输出目录>
正文约定：首行 `# 标题`，第二段为刊期说明；`## ` 为栏目，`### ` 为单篇标题。
内联 SVG 图表可直接写在 Markdown 中（以 <figure> 包裹）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown

CSS = r"""
:root{--ink:#1d2433;--muted:#5b6474;--navy:#16325c;--teal:#0f6e74;--amber:#b7791f;
--bg:#ffffff;--soft:#f3f6f9;--line:#dde3ea;}
@media (prefers-color-scheme:dark){:root{--ink:#e4e8ee;--muted:#a3adbb;--navy:#9cc0f0;
--teal:#6cc5c9;--amber:#e3b25e;--bg:#12161d;--soft:#1b212b;--line:#2c3441;}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.85 "PingFang SC","Hiragino Sans GB",
"Microsoft YaHei","Noto Sans CJK SC",sans-serif;}
main{max-width:760px;margin:0 auto;padding:28px 20px 64px}
h1{font-size:26px;line-height:1.35;color:var(--navy);margin:8px 0 4px;letter-spacing:.02em}
h1+p{color:var(--muted);font-size:14px;margin:0 0 20px;border-bottom:2px solid var(--navy);padding-bottom:12px}
h2{font-size:21px;color:var(--navy);margin:44px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:19px;line-height:1.45;color:var(--ink);margin:34px 0 6px}
h4{font-size:17px;color:var(--teal);margin:22px 0 4px}
p{margin:10px 0}
a{color:var(--teal);text-decoration:none;border-bottom:1px solid currentColor}
strong{color:var(--navy)}
@media (prefers-color-scheme:dark){strong{color:#cfe0f7}}
.meta,p.meta{color:var(--muted);font-size:14px;margin:0 0 10px}
span.meta{display:block;margin:2px 0 4px}
blockquote{margin:14px 0;padding:10px 14px;background:var(--soft);border-left:3px solid var(--amber);border-radius:0 6px 6px 0}
blockquote p{margin:4px 0}
ul,ol{padding-left:1.3em;margin:8px 0}
li{margin:6px 0}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
table{border-collapse:collapse;width:100%;font-size:15px;margin:12px 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--soft)}
figure{margin:18px 0;padding:12px;background:var(--soft);border-radius:8px}
figure svg{width:100%;height:auto;display:block}
figcaption{font-size:13px;color:var(--muted);margin-top:6px;line-height:1.6}
.toc{background:var(--soft);border-radius:8px;padding:10px 16px;font-size:15px}
.toc ul{list-style:none;padding:0;margin:0}
@media print{body{font-size:15.5px}main{padding:0 4px}h2{break-after:avoid}h3{break-after:avoid}
figure,blockquote{break-inside:avoid}a{border:0}}
"""

HTML = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>{title}</title><style>{css}</style></head>
<body><main>{body}</main></body></html>"""


def render_html(md_text: str) -> tuple[str, str]:
    title_match = re.search(r"^# (.+)$", md_text, re.M)
    title = title_match.group(1).strip() if title_match else "国际科技智库周报"
    body = markdown.markdown(
        md_text,
        extensions=["extra", "toc", "sane_lists"],
        extension_configs={"toc": {"slugify": _slug}},
        output_format="html5",
    )
    return title, HTML.format(title=title, css=CSS, body=body)


def _slug(value: str, separator: str) -> str:
    value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value).strip("-")
    return value[:60] or "s"


def render_pdf(html_path: Path, pdf_path: Path) -> int:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 420, "height": 900}, color_scheme="light")
        page.goto(html_path.resolve().as_uri())
        page.emulate_media(media="print", color_scheme="light")
        page.pdf(path=str(pdf_path), width="420px", height="900px", print_background=True,
                 margin={"top": "28px", "bottom": "28px", "left": "16px", "right": "16px"})
        browser.close()
    from pypdf import PdfReader

    return len(PdfReader(str(pdf_path)).pages)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    title, html = render_html(src.read_text(encoding="utf-8"))
    stem = src.stem
    html_path = out_dir / f"{stem}.html"
    html_path.write_text(html, encoding="utf-8")
    pages = render_pdf(html_path, out_dir / f"{stem}.pdf")
    print(f"html={html_path} pdf_pages={pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
