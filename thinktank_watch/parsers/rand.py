from __future__ import annotations

import html
import json
import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import ArticleCandidate


def _norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def _meta(soup: BeautifulSoup, key: str) -> list[str]:
    values: list[str] = []
    for attr in ("name", "property", "itemprop"):
        for node in soup.find_all("meta", attrs={attr: key}):
            content = node.get("content")
            if content:
                values.append(_norm(content))
    return values


def _json_ld_items(soup: BeautifulSoup) -> list[dict]:
    items: list[dict] = []
    for node in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(node.get_text())
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and isinstance(data.get("@graph"), list):
            items.extend(item for item in data["@graph"] if isinstance(item, dict))
        elif isinstance(data, dict):
            items.append(data)
    return items


def _date(value: str) -> str:
    value = _norm(value)
    if not value:
        return ""
    for fmt in ("%Y/%m/%d", "%Y/%-m/%-d", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    match = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", value)
    if match:
        year, month, day = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    if re.fullmatch(r"\d{8}", value):
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
    return value


def _authors_from_json_ld(items: list[dict]) -> list[str]:
    for item in items:
        author = item.get("author")
        if isinstance(author, list):
            names = [_norm(node.get("name")) for node in author if isinstance(node, dict) and node.get("name")]
            if names:
                return names
        if isinstance(author, dict) and author.get("name"):
            return [_norm(author["name"])]
    return []


def _detail_text(soup: BeautifulSoup) -> str:
    clone = BeautifulSoup(str(soup), "lxml")
    for node in clone(["script", "style", "nav", "footer", "header", "form"]):
        node.decompose()
    candidates: list[str] = []
    for selector in ("main", "article", ".article-body", ".body", "#content", ".publication-page"):
        for node in clone.select(selector):
            text = _norm(node.get_text(" "))
            if len(text) > 120:
                candidates.append(text)
    return max(candidates, key=len) if candidates else _norm(clone.get_text(" "))


def parse_rand_detail(html_text: str, url: str) -> ArticleCandidate:
    soup = BeautifulSoup(html_text, "lxml")
    json_ld = _json_ld_items(soup)
    json_primary = next(
        (
            item
            for item in json_ld
            if item.get("@type") in {"Article", "Book", "Report", "ScholarlyArticle"}
        ),
        {},
    )

    title = (
        _meta(soup, "citation_title")
        or _meta(soup, "og:title")
        or [_norm(json_primary.get("headline") or json_primary.get("name"))]
    )[0]
    published = (
        _meta(soup, "citation_publication_date")
        or _meta(soup, "citation_online_date")
        or _meta(soup, "rand-teaser-date")
        or [_norm(json_primary.get("datePublished"))]
    )[0]
    authors = _meta(soup, "citation_author") or _authors_from_json_ld(json_ld)
    subjects = _meta(soup, "DC.Subject")
    keywords: list[str] = []
    for raw in _meta(soup, "keywords") or [_norm(json_primary.get("keywords"))]:
        keywords.extend([_norm(part) for part in raw.split(",") if _norm(part)])

    pdf_values = _meta(soup, "citation_pdf_url")
    pdf_url = ""
    if pdf_values:
        pdf_url = pdf_values[0] if pdf_values[0].startswith("http") else "https://" + pdf_values[0].lstrip("/")
    else:
        pdf_link = next((node.get("href") for node in soup.find_all("a", href=True) if ".pdf" in node["href"].lower()), "")
        pdf_url = urljoin(url, pdf_link) if pdf_link else ""

    external_url = ""
    if "/external_publications/" in url:
        for node in soup.find_all("a", href=True):
            href = urljoin(url, node["href"])
            if href.startswith("http") and "rand.org" not in href and "rand.edu" not in href:
                external_url = href
                break

    if "/commentary/" in url:
        content_type = "commentary"
        completeness = "full_text"
    elif "/external_publications/" in url:
        content_type = "external_publication"
        completeness = "summary_only"
    else:
        content_type = "rand_report"
        completeness = "full_text" if pdf_url else "summary_only"

    summary = (
        _meta(soup, "description")
        or _meta(soup, "og:description")
        or [_norm(json_primary.get("description"))]
    )[0]

    return ArticleCandidate(
        institution_slug="rand",
        institution_name="RAND",
        institution_type="think_tank",
        title=title,
        url=url,
        published_date=_date(published),
        summary=summary,
        content_type=content_type,
        authors=authors,
        keywords=keywords,
        subjects=subjects,
        pdf_url=pdf_url,
        external_source_url=external_url,
        source_completeness=completeness,
        detail_text=_detail_text(soup),
        fetch_status="detail_ok",
    )
