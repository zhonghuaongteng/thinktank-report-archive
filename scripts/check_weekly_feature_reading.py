"""Check that reviewed weekly features and their complete prose reach both reader editions."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thinktank_watch.highlights import render_highlights_markdown


def fingerprint(item):
    parts = [item.get(key, "").replace("\r\n", "\n").strip()
             for key in ("chinese_title", "chinese_summary", "highlights_markdown")]
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()


def normalized(value):
    return re.sub(r"\s+", "", value).replace("\u00ad", "")


def reader_articles(markup, mobile):
    soup = BeautifulSoup(markup, "html.parser")
    articles = {}
    for card in soup.select("article.feature" if mobile else ".topic-primary"):
        link = card.select_one("h2 a[href]" if mobile else "h3 a[href]")
        if not link:
            raise ValueError("专题没有原文链接")
        url = link["href"]
        if url in articles:
            raise ValueError(f"阅读版专题重复 {url}")
        title = normalized(link.get_text())
        lead = card.select_one(".summary" if mobile else ".judgment-box p")
        summary = normalized(lead.get_text()) if lead else ""
        if mobile:
            body = card
            for extra in body.select("h2, .meta, .kicker, .summary"):
                extra.decompose()
        else:
            wrapper = card.find_next_sibling()
            body = wrapper.select_one(".report-highlights") if wrapper else None
        if body is None:
            raise ValueError(f"阅读版缺少专题正文 {url}")
        articles[url] = (title, summary, normalized(body.get_text()))
    return articles


def body_blocks(item):
    dom = BeautifulSoup(render_highlights_markdown(item["highlights_markdown"]), "html.parser")
    blocks = dom.find_all(["p", "h4", "h5", "h6", "li", "tr", "figcaption", "pre"])
    for idx, block in enumerate(blocks):
        # The phone renderer removes the repeated terminal link to the title's original URL.
        if idx == len(blocks) - 1 and block.name == "p" and block.get_text().startswith("来源：") and block.find("a", href=item["url"]):
            continue
        text = normalized(block.get_text())
        if text:
            yield text


def validate(items, reviews, pc, mobile):
    errors = []
    features = [item for item in items if item.get("priority") in ("P0", "P1")]
    urls = {item["url"] for item in features}
    if not features or len(features) != len(urls):
        errors.append("重点清单为空或有重复原文")
    records = {row["url"]: row for row in reviews}
    if len(records) != len(reviews) or set(records) != urls:
        errors.append("复核与重点原文未逐篇对应")
    readers = {"PC": reader_articles(pc, False), "手机": reader_articles(mobile, True)}
    for edition, articles in readers.items():
        if set(articles) != urls:
            errors.append(f"{edition}版与重点原文集合不一致")
    count = 0
    for item in features:
        url = item["url"]
        record = records.get(url, {})
        if record.get("reviewed_sha256") != fingerprint(item):
            errors.append(f"{url} 的标题、导语或正文未经本次复核")
        retelling = record.get("retelling", "")
        if not retelling.strip() or retelling.strip() in {"通过", "已复核", "已完成"}:
            errors.append(f"{url} 缺少具体复述")
        notes = record.get("source_notes", [])
        if not notes or any(not note.get("locator", "").strip() or not note.get("finding", "").strip()
                            or urlsplit(note.get("url", "")).scheme not in ("http", "https")
                            or not urlsplit(note.get("url", "")).netloc for note in notes):
            errors.append(f"{url} 缺少带定位的原始资料摘记")
        if not any(note.get("url") in {url, item.get("pdf_url")} - {None, ""} for note in notes):
            errors.append(f"{url} 缺少本篇原文或其PDF的定位")
        blocks = list(body_blocks(item))
        count += len(blocks)
        if not blocks:
            errors.append(f"{url} 正文为空")
        for edition, articles in readers.items():
            title, summary, body = articles.get(url, ("", "", ""))
            if title != normalized(item["chinese_title"]) or summary != normalized(item["chinese_summary"]):
                errors.append(f"{edition}版标题或导语与核准稿不一致 {url}")
            pos = 0
            for block in blocks:
                found = body.find(block, pos)
                if found < 0:
                    errors.append(f"{edition}缺段或顺序不符 {url} {block[:32]}")
                    break
                pos = found + len(block)
    return {"passed": not errors, "features": len(features), "blocks_per_edition": count, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("items", "review", "pc", "mobile", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        items = json.loads(args.items.read_text(encoding="utf-8-sig"))
        items = items["items"] if isinstance(items, dict) else items
        reviews = json.loads(args.review.read_text(encoding="utf-8-sig"))["features"]
        result = validate(items, reviews, args.pc.read_text(encoding="utf-8"),
                          args.mobile.read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"passed": False, "errors": [str(exc)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
