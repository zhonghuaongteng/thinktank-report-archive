"""把一期周报正文（Markdown）渲染成电脑版格式的自包含网页（手机上也能读）。

用法：uv run python scripts/weekly/render_issue.py <issue.md> <输出目录>

正文约定（见 briefs/weekly/2026/2026-11-25 样刊）：
- 首行 `# 标题`，第二段为刊期说明；随后可有 `<div class="lead">` 导语块。
- `## 本周要点` 下的列表渲染为“值得细读的发现”；`## 重点解读` 下每个 `### 标题 {#锚点}` 为一篇，
  可含 `<div class="comic">` 四格插画（图片路径相对正文所在目录）和 `<div class="abstract">` 摘要导读；
  `## 简讯` 下用 `###` 分组。
本地图片以内嵌方式写入网页，附件脱离目录也能完整显示。
"""
from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

CSS = r"""
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#eef1f4;color:#172026;font:16px/1.85 "Microsoft YaHei","PingFang SC","Noto Sans CJK SC",sans-serif}
main{max-width:760px;margin:28px auto;background:#fff;box-shadow:0 18px 48px rgba(23,32,38,.14);padding:0 0 40px}
.brandbar{display:flex;height:7px}.brandbar span:nth-child(1){flex:4;background:#1f5f8b}
.brandbar span:nth-child(2){flex:2;background:#b84c3d}.brandbar span:nth-child(3){flex:3;background:#4f7d5a}
.inner{padding:0 40px}
h1,h2,h3,.lead-title,.comic-title{font-family:"Source Han Serif SC","Noto Serif CJK SC","SimSun",serif}
.kicker{letter-spacing:.32em;font-size:12px;color:#b84c3d;font-weight:700;margin:26px 0 8px}
h1{font-size:34px;line-height:1.25;color:#14456e;margin:0 0 12px}
.issue-meta{color:#5f6b75;font-size:14px;border-top:1.5px solid #172026;border-bottom:1px solid #c7d0d8;padding:9px 0;margin:0 0 18px}
.lead{border-left:3px solid #1f5f8b;padding:2px 0 2px 16px;margin:0 0 10px}
.lead-title{font-size:21px;font-weight:700;color:#14456e;line-height:1.45;margin:0 0 6px}
.lead p{margin:4px 0}
h2{font-size:20px;color:#14456e;margin:34px 0 10px}
.finds{list-style:none;padding:0;margin:0}
.finds li{border-bottom:1px solid #e1e6eb;padding:12px 0}
.finds .find-title{display:block;font-weight:700;font-size:16.5px;color:#172026;font-family:"Source Han Serif SC","Noto Serif CJK SC",serif}
.finds a{font-size:13px}
.nav{border-top:1px solid #c7d0d8;margin-top:22px;padding-top:4px}
.nav ol{columns:2;column-gap:28px;list-style:none;padding:0;margin:0}
.nav li{font-size:14px;line-height:1.6;margin:0 0 8px;break-inside:avoid}
a{color:#14456e;text-decoration:none}a:hover{text-decoration:underline}
.topic{border-top:1px solid #d7dee5;margin-top:36px;padding-top:18px}
.topic-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
.chip{font-size:12px;font-weight:700;padding:2px 12px;border-radius:999px;background:#f3dcd8;color:#8f3528}
.counter{font-size:12px;color:#8a96a0}
.topic h3{font-size:23px;line-height:1.4;color:#14456e;margin:6px 0 4px}
.meta{color:#5f6b75;font-size:13px;margin:0 0 14px}
.comic{background:#f8f5ee;border:1px solid #e6dfd0;border-top:5px solid #176b70;border-radius:3px;padding:12px 16px 8px;margin:14px 0}
.comic-title{font-size:19px;font-weight:700;color:#173448;margin:0 0 10px}
.panels{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.panels figure{margin:0;background:#fffdf8;border:1px solid #ddd6c6}
.panels img{width:100%;display:block;aspect-ratio:3/2;object-fit:cover}
.panels figcaption{font-size:13.5px;line-height:1.6;padding:6px 8px 8px;color:#2b3a44;margin:0}
.comic-src{font-size:12px;color:#6f7a83;margin:8px 0 0}
.abstract{background:#173f63;color:#fff;border-radius:3px;padding:12px 18px;margin:14px 0 18px}
.abstract span{display:block;font-size:12px;letter-spacing:.2em;color:#b9cde0;margin-bottom:2px}
.abstract p{margin:0;font-weight:700;line-height:1.75}
.topic p{margin:12px 0}
.topic strong{color:#14456e}
figure.chart{margin:16px 0;padding:12px;background:#f3f6f9;border-radius:4px}
figure.chart svg{width:100%;max-width:520px;height:auto;display:block;margin:0 auto}
figcaption{font-size:12.5px;color:#5f6b75;line-height:1.6;margin-top:6px}
.briefs h3{font-size:16px;color:#fff;background:#14456e;display:inline-block;padding:2px 12px;border-radius:2px;margin:22px 0 4px}
.briefs p{margin:10px 0;padding-left:12px;border-left:2px solid #d8e0e7}
.briefs p strong{color:#b84c3d}
span.meta{display:block;margin:2px 0}
@media (max-width:760px){main{margin:0;box-shadow:none}.inner{padding:0 18px}h1{font-size:28px}
.panels{grid-template-columns:1fr}.nav ol{columns:1}}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head>
<body><main><div class="brandbar"><span></span><span></span><span></span></div><div class="inner">{body}</div></main></body></html>"""


def _slug(value: str, separator: str) -> str:
    return re.sub(r"[^\w一-鿿-]+", "-", value).strip("-")[:60] or "s"


def embed(soup: BeautifulSoup, base: Path) -> None:
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith(("http:", "https:", "data:")):
            continue
        path = (base / src).resolve()
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        img["src"] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def section_after(h2) -> list:
    nodes, node = [], h2.next_sibling
    while node is not None and getattr(node, "name", None) != "h2":
        nodes.append(node)
        node = node.next_sibling
    return nodes


def new(soup, tag, cls=None, text=None, **attrs):
    el = soup.new_tag(tag, attrs={**({"class": cls} if cls else {}), **attrs})
    if text is not None:
        el.string = text
    return el


def build(md_text: str, base: Path) -> tuple[str, str]:
    html = markdown.markdown(md_text, extensions=["extra", "toc"], extension_configs={"toc": {"slugify": _slug}})
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    title = h1.get_text(strip=True)
    h1.insert_before(new(soup, "p", "kicker", "GLOBAL TECH THINK TANK WATCH · 每周研究"))
    h1.find_next_sibling("p")["class"] = ["issue-meta"]

    features, groups = [], []
    for h2 in soup.find_all("h2"):
        name = h2.get_text(strip=True)
        nodes = section_after(h2)
        if name.startswith("本周要点"):
            h2.string = "值得细读的发现"
            ul = next((n for n in nodes if getattr(n, "name", None) == "ul"), None)
            if ul:
                ul["class"] = ["finds"]
                for li in ul.find_all("li", recursive=False):
                    strong = li.find("strong")
                    if strong:
                        strong.name = "span"
                        strong["class"] = ["find-title"]
                        nxt = strong.next_sibling
                        if isinstance(nxt, str):
                            nxt.replace_with(nxt.lstrip("：: "))
                    for a in li.find_all("a"):
                        a.string = "阅读全文"
        elif name.startswith("重点解读"):
            h3s = [n for n in nodes if getattr(n, "name", None) == "h3"]
            for i, h3 in enumerate(h3s, 1):
                body, node = [], h3.next_sibling
                while node is not None and getattr(node, "name", None) not in ("h3", "h2"):
                    body.append(node)
                    node = node.next_sibling
                wrap = new(soup, "section", "topic", id=h3.get("id", f"t{i}"))
                h3.attrs.pop("id", None)
                h3.insert_before(wrap)
                head = new(soup, "div", "topic-head")
                head.extend([new(soup, "span", "chip", "重点"),
                             new(soup, "span", "counter", f"重点 {i:02d} / {len(h3s):02d}")])
                wrap.append(head)
                wrap.append(h3.extract())
                for n in body:
                    wrap.append(n.extract())
                for fig in wrap.find_all("figure"):
                    if fig.find("svg"):
                        fig["class"] = ["chart"]
                features.append((wrap["id"], h3.get_text(strip=True)))
        elif name.startswith("简讯"):
            box = new(soup, "section", "briefs", id=h2.get("id", "briefs"))
            h2.attrs.pop("id", None)
            h2.insert_after(box)
            for n in nodes:
                box.append(n.extract())
            groups = [(g.get("id", ""), g.get_text(strip=True)) for g in box.find_all("h3")]

    nav = new(soup, "div", "nav")
    ol = soup.new_tag("ol")
    items = [(a, f"{i:02d} | {t}") for i, (a, t) in enumerate(features, 1)] + [(a, f"简讯 | {t}") for a, t in groups]
    for anchor, text in items:
        li = soup.new_tag("li")
        li.append(new(soup, "a", None, text, href=f"#{anchor}"))
        ol.append(li)
    nav.extend([new(soup, "h2", None, "阅读导航"), ol])
    topics_h2 = next((h for h in soup.find_all("h2") if h.get_text(strip=True).startswith("重点解读")), None)
    if topics_h2:
        topics_h2.insert_before(nav)
    embed(soup, base)
    return title, PAGE.format(title=title, css=CSS, body=str(soup))


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    _, html = build(src.read_text(encoding="utf-8"), src.parent)
    html_path = out_dir / f"{src.stem}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"html={html_path} size={len(html.encode()) // 1024}KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
