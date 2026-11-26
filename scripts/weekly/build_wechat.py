"""把一期周报正文（Markdown）编排成公众号“这事有研究”的多图文草稿包。

用法：uv run python scripts/weekly/build_wechat.py <issue.md> <输出目录>

产出：导读一篇（本周要点 + 全部简讯）和每篇重点解读各一篇的公众号正文 HTML（内联样式）、
图表 PNG、封面 JPG、本地预览 index.html，以及供
C:/Users/WINDOWS/.codex/automations/automation-4/helpers/wechat_stage_issue.py 上传用的 manifest.json。
重点篇的微信“阅读原文”绑定该篇第一个原文链接；导读不设原文入口，原文网址只留在 manifest 的内部清单。
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

ACCOUNT = "这事有研究"
NAVY, TEAL, GOLD, INK, MUTED = "#173448", "#176b70", "#b47721", "#293d49", "#687b86"
STYLE = {
    "section": f"font-family:system-ui,-apple-system,Microsoft YaHei,sans-serif;font-size:17px;line-height:1.85;color:{INK};word-wrap:break-word;",
    "p": "margin:16px 0;",
    "h2": f"font-size:19px;font-weight:700;color:{NAVY};margin:30px 0 10px;padding-bottom:6px;border-bottom:2px solid {GOLD};",
    "h3": f"font-size:17px;font-weight:700;color:{NAVY};margin:26px 0 6px;",
    "strong": f"font-weight:700;color:{TEAL};",
    "ul": "padding-left:1.2em;margin:12px 0;",
    "li": "margin:8px 0;",
    "meta": f"font-size:13px;line-height:1.6;color:{MUTED};margin:4px 0 12px;",
    "caption": f"font-size:13px;line-height:1.6;color:{MUTED};margin:6px 0 20px;",
    "img": "width:100%;display:block;margin:18px 0 0;",
}
MASTHEAD = (f'<section style="padding:12px 16px;margin:0 0 22px;background:{NAVY};border-top:3px solid {GOLD};">'
            f'<p style="font-size:13px;line-height:1.5;color:#fff;letter-spacing:2px;margin:0;">{ACCOUNT}'
            f'<span style="color:#a8c9ca;font-size:11px;letter-spacing:1px;"> / 国际科技智库周报</span></p></section>')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_issue(md_text: str) -> dict:
    """拆出刊期行、本周要点、各篇重点和简讯。"""
    period = md_text.split("\n\n", 2)[1].strip()
    sections = re.split(r"^## ", md_text, flags=re.M)
    lead = re.search(r'<div class="lead">.*?</div>', md_text, flags=re.S)
    found = {"period": period, "lead": lead.group(0) if lead else "", "points": "", "features": [], "briefs": ""}
    for sec in sections[1:]:
        head, _, body = sec.partition("\n")
        if head.startswith("本周要点"):
            found["points"] = body
        elif head.startswith("重点解读"):
            for part in re.split(r"^### ", body, flags=re.M)[1:]:
                title_line, _, text = part.partition("\n")
                title = re.sub(r"\s*\{#[^}]+\}\s*$", "", title_line).strip()
                found["features"].append({"title": title, "body": text})
        elif head.startswith("简讯"):
            found["briefs"] = body
    return found


def first_source(body: str) -> tuple[str, list[str]]:
    urls = re.findall(r"\]\((https?://[^)\s]+)\)", body)
    origin = re.search(r"^原文：.*?\]\((https?://[^)\s]+)\)", body, flags=re.M)
    return (origin.group(1) if origin else (urls[0] if urls else "")), list(dict.fromkeys(urls))


def to_wechat_html(md_body: str, out: Path, prefix: str, page) -> tuple[str, list[str]]:
    """Markdown 片段转公众号内联样式 HTML；内联 SVG 图转成 PNG。返回 (html, 图片相对路径)。"""
    md_body = re.sub(r"^原文：.*$", "", md_body, flags=re.M)
    md_body = re.sub(r"\s*\[详见\]\(#[^)]*\)", "", md_body)
    md_body = re.sub(r"\s*\{#[^}]+\}", "", md_body)
    soup = BeautifulSoup(markdown.markdown(md_body, extensions=["extra"]), "html.parser")
    images = []
    for n, fig in enumerate([f for f in soup.find_all("figure") if f.find("svg")], 1):
        svg = fig.find("svg")
        name = f"images/{prefix}-fig{n}.png"
        page.set_content(f'<html><body style="margin:0;background:#fff;color:{INK}">'
                         f'<div id="f" style="width:680px;padding:16px;background:#f3f6f9">{svg}</div></body></html>')
        page.locator("#f").screenshot(path=str(out / name))
        caption = fig.find("figcaption")
        new = soup.new_tag("section")
        img = soup.new_tag("img", src=name, style=STYLE["img"])
        new.append(img)
        if caption:
            cap = soup.new_tag("p", style=STYLE["caption"])
            cap.string = caption.get_text(" ", strip=True)
            new.append(cap)
        fig.replace_with(new)
        images.append(name)
    src_dir = out.parent
    for comic in soup.select("div.comic"):
        box = soup.new_tag("section", style="margin:20px 0;padding:12px 12px 6px;background:#f8f5ee;border-top:4px solid " + TEAL + ";")
        t = comic.select_one(".comic-title")
        if t:
            box.append(soup.new_tag("p", style=f"font-size:17px;font-weight:700;color:{NAVY};margin:0 0 8px;"))
            box.p.string = t.get_text()
        for k, fig in enumerate(comic.find_all("figure"), 1):
            img = fig.find("img")
            name = f"images/{prefix}-panel{k}.jpg"
            (out / name).write_bytes((src_dir / img["src"]).read_bytes())
            box.append(soup.new_tag("img", src=name, style=STYLE["img"] + "margin:8px 0 0;"))
            cap = soup.new_tag("p", style="font-size:14px;line-height:1.65;color:#2b3a44;margin:4px 0 10px;")
            cap.string = fig.figcaption.get_text() if fig.figcaption else ""
            box.append(cap)
            images.append(name)
        comic.replace_with(box)
    for ab in soup.select("div.abstract"):
        box = soup.new_tag("section", style="margin:16px 0 20px;padding:12px 16px;background:#173f63;")
        lab = soup.new_tag("p", style="font-size:12px;letter-spacing:2px;color:#b9cde0;margin:0;")
        lab.string = "摘要导读"
        txt = soup.new_tag("p", style="font-size:16px;font-weight:700;line-height:1.75;color:#fff;margin:2px 0 0;")
        txt.string = ab.p.get_text() if ab.p else ab.get_text()
        box.extend([lab, txt])
        ab.replace_with(box)
    for lead in soup.select("div.lead"):
        box = soup.new_tag("section", style=f"margin:0 0 20px;padding:4px 0 4px 14px;border-left:3px solid {TEAL};")
        t = lead.select_one(".lead-title")
        if t:
            h = soup.new_tag("p", style=f"font-size:18px;font-weight:700;color:{NAVY};line-height:1.5;margin:0 0 6px;")
            h.string = t.get_text()
            box.append(h)
        for para in lead.find_all("p"):
            if "lead-title" in (para.get("class") or []):
                continue
            q = soup.new_tag("p", style="margin:4px 0;")
            q.string = para.get_text()
            box.append(q)
        lead.replace_with(box)
    # 简讯段落形如“**标题** <span class=meta>机构·日期</span> 正文”，拆成标题、说明、正文三段。
    for p in list(soup.find_all("p")):
        kids = [k for k in p.contents if not (isinstance(k, str) and not k.strip())]
        if len(kids) > 2 and getattr(kids[0], "name", "") == "strong" and "meta" in (kids[1].get("class") or [] if hasattr(kids[1], "get") else []):
            title = soup.new_tag("p")
            title["data-role"] = "brief-title"
            title.string = kids[0].get_text()
            meta = soup.new_tag("p")
            meta["class"] = ["meta"]
            meta.string = kids[1].get_text()
            kids[0].extract()
            kids[1].extract()
            p.insert_before(title)
            p.insert_before(meta)
    for tag in soup.find_all(True):
        cls = tag.get("class") or []
        if "meta" in cls:
            tag.name = "p"
            tag["style"] = STYLE["meta"]
        elif tag.get("data-role") == "brief-title" or tag.name in ("h3", "h4"):
            tag["style"] = STYLE["h3"]
        elif tag.name == "h2":
            tag["style"] = STYLE["h2"]
        elif tag.name in STYLE and tag.name != "img" and not tag.get("style"):
            tag["style"] = STYLE[tag.name]
        for attr in ("class", "id", "data-role"):
            tag.attrs.pop(attr, None)
    return f'<section style="{STYLE["section"]}">{MASTHEAD}{soup}</section>', images


def render_cover(page, out: Path, name: str, kicker: str, title: str) -> str:
    """封面 900×383（2.35:1），标题居中，方形裁切也能看全。"""
    path = f"images/{name}.jpg"
    page.set_content(f'''<html><body style="margin:0"><div id="c" style="width:900px;height:383px;background:{NAVY};
      border-top:8px solid {GOLD};box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;
      align-items:center;font-family:'Microsoft YaHei',sans-serif;color:#fff;text-align:center;padding:0 262px">
      <div style="font-size:20px;letter-spacing:2px;color:#a8c9ca;margin-bottom:16px">{kicker}</div>
      <div style="font-size:40px;font-weight:700;line-height:1.3">{title}</div></div></body></html>''')
    page.locator("#c").screenshot(path=str(out / path), type="jpeg", quality=92)
    return path


# 3:2 插画作封面时的裁切比例（微信封面需给出 2.35:1 与 1:1 两种裁切）。
PANEL_CROP = [{"ratio": "2.35_1", "x1": "0", "y1": "0.180851", "x2": "1", "y2": "0.819149"},
              {"ratio": "1_1", "x1": "0.166667", "y1": "0", "x2": "0.833333", "y2": "1"}]


def feature_cover(page, out: Path, i: int, title: str, imgs: list[str]) -> dict:
    panel = next((x for x in imgs if "-panel1." in x), None)
    if panel:
        return {"cover_file": panel, "cover_crop_percent_list": PANEL_CROP}
    return {"cover_file": render_cover(page, out, f"cover-{i:02d}", "这事有研究 · 本周研究", title)}


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    from playwright.sync_api import sync_playwright

    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    (out / "images").mkdir(parents=True, exist_ok=True)
    date = re.match(r"\d{4}-\d{2}-\d{2}", src.name).group(0)
    issue = split_issue(src.read_text(encoding="utf-8"))
    window = re.findall(r"(\d{4})年(\d{1,2})月(\d{1,2})日—(\d{1,2})日", issue["period"])
    y, m, d1, d2 = window[0]
    label = f"{int(m)}月{int(d1)}日—{int(d2)}日"
    articles = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        guide_md = (f'<p class="meta">{label} · 重点解读{len(issue["features"])}篇 · 简讯{issue["briefs"].count('<span class="meta">')}则</p>\n\n'
                    f'{issue["lead"]}\n\n## 本周要点\n{issue["points"]}\n\n## 简讯\n{issue["briefs"]}')
        _, guide_urls = first_source(issue["briefs"])
        html, imgs = to_wechat_html(guide_md, out, "01", page)
        articles.append({"slug": "guide", "kind": "guide", "title": f"国际科技智库周报｜{label}",
                         "html": html, "images": imgs, "source_url": "", "content_source_url": "",
                         "source_urls": guide_urls,
                         "cover_file": render_cover(page, out, "cover-01", f"国际科技智库周报 · {label}", "本周要点与简讯")})
        for i, feat in enumerate(issue["features"], 2):
            source, urls = first_source(feat["body"])
            html, imgs = to_wechat_html(feat["body"], out, f"{i:02d}", page)
            articles.append({"slug": f"feature-{i:02d}", "kind": "feature", "title": feat["title"],
                             "html": html, "images": imgs, "source_url": source, "content_source_url": source,
                             "source_urls": urls,
                             **feature_cover(page, out, i, feat["title"], imgs)})
        browser.close()
    reviewed, index_parts, manifest_articles = {}, [], []
    for n, art in enumerate(articles, 1):
        if len(art["title"]) > 32:
            raise SystemExit(f"标题超过32字：{art['title']}")
        if len(art["html"]) >= 20000:
            raise SystemExit(f"正文超过公众号20000字符上限（{len(art['html'])}）：{art['title']}")
        name = f"{n:02d}-{art['slug']}.wechat.html"
        (out / name).write_text(art["html"], encoding="utf-8")
        for rel in [name, art["cover_file"], *art["images"]]:
            reviewed[rel] = sha(out / rel)
        index_parts.append(f'<h1 style="font:600 15px sans-serif;color:#888;margin:40px 0 8px">{n}. {art["title"]}</h1>'
                           f'<img src="{art["cover_file"]}" style="width:100%;max-width:420px">{art["html"]}')
        manifest_articles.append({k: art[k] for k in ("slug", "kind", "title", "images", "cover_file",
                                                     "source_url", "content_source_url", "source_urls")
                                  if k in art} | ({"cover_crop_percent_list": art["cover_crop_percent_list"]}
                                                   if "cover_crop_percent_list" in art else {})
                                 | {"order": n, "content_html_file": name})
    (out / "index.html").write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                                    '<body style="max-width:430px;margin:0 auto;padding:12px">' + "".join(index_parts),
                                    encoding="utf-8")
    manifest = {"account_name": ACCOUNT, "business_date": date, "window": [f"{y}-{int(m):02d}-{int(d1):02d}", date],
                "edition": "claude-weekly-v1", "link_policy": "original_read_more_v1",
                "draft_upload_approved": True, "publication_state": "reviewed_for_draft_only",
                "article_count": len(articles), "articles": manifest_articles, "reviewed_files_sha256": reviewed}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"articles": len(articles), "sizes": [len(a["html"]) for a in articles], "out": str(out)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
