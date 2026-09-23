"""Explicit, date-bound editorial input for a weekly report's opening page.

Validation checks structure, declared review and links, not the truth or quality
of editorial judgments. Nothing is synthesized from topic counts here.
"""
from __future__ import annotations

from datetime import date as Date
from dataclasses import asdict
import hashlib
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

from .highlights import render_highlights_markdown, validated_highlights_markdown
from .models import ArticleCandidate


def weekly_editorial_path(root: str | Path, date: str) -> Path:
    if Date.fromisoformat(date).isoformat() != date:
        raise ValueError("Editorial date must use YYYY-MM-DD")
    return Path(root) / "weekly" / date[:4] / f"{date}_editorial.json"


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Editorial {label} must be non-empty text")
    return value.strip()


def _web_url(value: object, label: str) -> str:
    text = _text(value, label)
    parsed = urlsplit(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Editorial {label} must be an explicit HTTP(S) URL")
    return text


def validate_weekly_editorial(
    document: dict, date: str, candidates: list[ArticleCandidate], *, require_review: bool = False,
) -> dict:
    if not isinstance(document, dict):
        raise ValueError("Editorial input must be a JSON object")
    if document.get("date") != date:
        raise ValueError(f"Editorial date does not match report date {date}")
    _text(document.get("headline"), "headline")
    _text(document.get("lead"), "lead")
    article_urls = {item.url for item in candidates if item.priority in {"P0", "P1"}}
    discoveries = document.get("discoveries")
    if not isinstance(discoveries, list) or not discoveries:
        raise ValueError("Editorial discoveries must contain at least one authored finding")
    for index, discovery in enumerate(discoveries, 1):
        if not isinstance(discovery, dict):
            raise ValueError(f"Editorial discovery {index} must be an object")
        for field in ("title", "text", "source_locator"):
            _text(discovery.get(field), f"discovery {index}.{field}")
        _web_url(discovery.get("source_url"), f"discovery {index}.source_url")
        if discovery.get("article_url") not in article_urls:
            raise ValueError(f"Editorial discovery {index}.article_url is not a current P0/P1 article")
        if "metric" in discovery or "metric_label" in discovery:
            _text(discovery.get("metric"), f"discovery {index}.metric")
            _text(discovery.get("metric_label"), f"discovery {index}.metric_label")
    connections = document.get("connections")
    if not isinstance(connections, list):
        raise ValueError("Editorial connections must be a list; use an empty list when there is no supported connection")
    for index, connection in enumerate(connections, 1):
        if not isinstance(connection, dict):
            raise ValueError(f"Editorial connection {index} must be an object")
        _text(connection.get("title"), f"connection {index}.title")
        _text(connection.get("text"), f"connection {index}.text")
        urls = connection.get("article_urls")
        if not isinstance(urls, list) or any(not isinstance(url, str) or url not in article_urls for url in urls):
            raise ValueError(f"Editorial connection {index}.article_urls must refer only to current P0/P1 articles")
    if "data_markdown" in document and not isinstance(document["data_markdown"], str):
        raise ValueError("Editorial data_markdown must be text")
    review = document.get("review", {})
    if not isinstance(review, dict):
        raise ValueError("Editorial review must be an object")
    if require_review:
        if review.get("completed") is not True:
            raise ValueError("Editorial content review has not been recorded for this issue")
        _text(review.get("note"), "review.note")
    return document


def load_weekly_editorial(
    root: str | Path, date: str, candidates: list[ArticleCandidate], *,
    required: bool = False, require_review: bool = False,
) -> dict | None:
    path = weekly_editorial_path(root, date)
    if not path.exists():
        if required:
            raise ValueError(f"Weekly editorial file is missing: {path}")
        return None
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    return validate_weekly_editorial(document, date, candidates, require_review=require_review)


def editorial_fingerprint(document: dict, candidates: list[ArticleCandidate]) -> str:
    content = {"editorial": document, "articles": [asdict(item) for item in sorted(candidates, key=lambda item: (item.url, item.institution_slug))]}
    payload = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def inspect_weekly_editorial(
    root: str | Path, date: str, candidates: list[ArticleCandidate], html: str,
) -> list[str]:
    if not any(item.priority in {"P0", "P1"} for item in candidates):
        return []
    try:
        document = load_weekly_editorial(root, date, candidates, required=True, require_review=True)
        for item in candidates:
            if item.priority in {"P0", "P1"}:
                validated_highlights_markdown(item)
        fingerprint = editorial_fingerprint(document, candidates)
        marker = f'name="weekly-editorial-sha256" content="{fingerprint}"'
        if marker not in html:
            return ["Rendered HTML does not match the current editorial file; render the weekly report again"]
        directory = weekly_editorial_path(root, date).parent
        stem = f"{date}_国际科技智库周报"
        markdown_path = directory / f"{stem}.md"
        html_path = directory / f"{stem}.html"
        pdf_path = directory / f"{stem}.pdf"
        if markdown_path.exists() and f'<!-- weekly-editorial-sha256: {fingerprint} -->' not in markdown_path.read_text(encoding="utf-8"):
            return ["Rendered Markdown does not match the current editorial file"]
        inputs = [weekly_editorial_path(root, date), html_path]
        if pdf_path.exists() and any(path.exists() and path.stat().st_mtime_ns > pdf_path.stat().st_mtime_ns for path in inputs):
            return ["PDF is older than its editorial input or HTML; render the weekly report again"]
    except (OSError, ValueError, TypeError) as error:
        return [str(error)]
    return []


def render_editorial_html(document: dict, anchors: dict[str, str]) -> str:
    parts = [
        '<section class="editorial-lead">',
        f'<h2>{escape(document["headline"])}</h2>',
        render_highlights_markdown(document["lead"]),
        '</section><section class="editorial-discoveries"><h2>值得细读的发现</h2>',
    ]
    for discovery in document["discoveries"]:
        metric_class = " with-metric" if discovery.get("metric") else ""
        parts.append(f'<article class="editorial-discovery{metric_class}">')
        if discovery.get("metric"):
            parts.append(f'<div class="editorial-metric"><strong>{escape(discovery["metric"])}</strong><span>{escape(discovery["metric_label"])}</span></div>')
        parts.extend(['<div class="editorial-discovery-body">', f'<h3>{escape(discovery["title"])}</h3>'])
        parts.append(render_highlights_markdown(discovery["text"]))
        parts.append(
            f'<p class="editorial-source"><a href="{escape(discovery["source_url"], quote=True)}">'
            f'原文：{escape(discovery["source_locator"])}</a> · '
            f'<a href="#{anchors[discovery["article_url"]]}">阅读全文</a></p></div></article>'
        )
    parts.append('</section>')
    if document.get("data_markdown", "").strip():
        parts.extend(['<section class="editorial-data report-highlights">', render_highlights_markdown(document["data_markdown"]), '</section>'])
    if not document["connections"]:
        return '\n'.join(parts)
    parts.append('<section class="editorial-connections"><h2>与研究关注的连接</h2>')
    for connection in document["connections"]:
        parts.append(f'<h3>{escape(connection["title"])}</h3>')
        parts.append(render_highlights_markdown(connection["text"]))
        if connection["article_urls"]:
            links = [f'<a href="#{anchors[url]}">主题 {anchors[url].removeprefix("topic-")}</a>' for url in connection["article_urls"]]
            parts.append('<p class="editorial-source">' + ' · '.join(links) + '</p>')
    parts.append('</section>')
    return '\n'.join(parts)


def render_editorial_markdown(document: dict, anchors: dict[str, str]) -> str:
    lines = [f'## {document["headline"]}', '', document['lead'], '', '## 值得细读的发现', '']
    for discovery in document['discoveries']:
        lines.extend([f'### {discovery["title"]}', '', discovery['text'], ''])
        if discovery.get('metric'):
            lines.extend([f'**{discovery["metric"]}** {discovery["metric_label"]}', ''])
        lines.extend([f'原文：[{discovery["source_locator"]}]({discovery["source_url"]}) · [阅读全文](#{anchors[discovery["article_url"]]})', ''])
    if document.get('data_markdown'):
        lines.extend([document['data_markdown'], ''])
    if document['connections']:
        lines.extend(['## 与研究关注的连接', ''])
    for connection in document['connections']:
        lines.extend([f'### {connection["title"]}', '', connection['text'], ''])
        if connection['article_urls']:
            lines.extend([' · '.join(f'[主题 {anchors[url].removeprefix("topic-")}](#{anchors[url]})' for url in connection['article_urls']), ''])
    return '\n'.join(lines)
