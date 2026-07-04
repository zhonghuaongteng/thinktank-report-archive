from __future__ import annotations

import html
import json
import re
from datetime import datetime
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from ..models import ArticleCandidate, Institution


ALLOW_TERMS = (
    "publication",
    "report",
    "research",
    "analysis",
    "article",
    "brief",
    "paper",
    "commentary",
    "post",
    "insight",
)
BROAD_ENDPOINTS = {
    "analysis",
    "article",
    "articles",
    "articles-multimedia",
    "books",
    "brief",
    "briefs",
    "commentary",
    "defense",
    "external",
    "fellowship-programs",
    "insight",
    "insights",
    "issue",
    "issues",
    "knowledge-bases",
    "news",
    "opinion",
    "paper",
    "papers",
    "partners",
    "podcasts",
    "post",
    "posts",
    "press-releases",
    "publication",
    "publications",
    "report",
    "reports",
    "reports-briefings",
    "research",
    "research-and-commentary",
    "research-commentary",
    "research-programs",
    "resource",
    "resources",
    "testimonies-filings",
    "topic",
    "topics",
}
CONTENT_TYPE_SEGMENTS = {
    "analysis",
    "article",
    "articles",
    "brief",
    "briefs",
    "commentary",
    "external_publications",
    "insight",
    "insights",
    "paper",
    "papers",
    "post",
    "posts",
    "publication",
    "publications",
    "report",
    "reports",
    "research_reports",
    "resource",
    "resources",
}
EXCLUDED_PATH_SEGMENTS = {"books", "knowledge-bases", "podcasts"}


def norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def canonical_date(value: str) -> str:
    value = norm(value)
    if not value:
        return ""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(value[:10], fmt).date().isoformat()
        except ValueError:
            pass
    match = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", value)
    if match:
        year, month, day = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    return value[:10]


def meta_values(soup: BeautifulSoup, key: str) -> list[str]:
    values: list[str] = []
    for attr in ("name", "property", "itemprop"):
        for node in soup.find_all("meta", attrs={attr: key}):
            content = node.get("content")
            if content:
                values.append(norm(content))
    return values


def looks_like_detail_url(url: str, text: str = "") -> bool:
    parsed = urlparse(url)
    path_segments = [segment for segment in parsed.path.split("/") if segment]
    if len(path_segments) < 2 or path_segments[-1].lower() in BROAD_ENDPOINTS:
        return False
    if any(segment.lower() in EXCLUDED_PATH_SEGMENTS for segment in path_segments):
        return False
    haystack = f"{path_segments[-1]} {text}".lower()
    return any(term in haystack for term in ALLOW_TERMS) or any(
        segment.lower() in CONTENT_TYPE_SEGMENTS for segment in path_segments[:-1]
    )


def parse_generic_detail(html_text: str, url: str, institution: Institution) -> ArticleCandidate:
    soup = BeautifulSoup(html_text, "lxml")
    title = (
        meta_values(soup, "citation_title")
        or meta_values(soup, "og:title")
        or meta_values(soup, "twitter:title")
        or [norm(soup.title.get_text(" ", strip=True)) if soup.title else ""]
    )[0]
    summary = (
        meta_values(soup, "description")
        or meta_values(soup, "og:description")
        or meta_values(soup, "twitter:description")
        or [""]
    )[0]
    published = (
        meta_values(soup, "citation_publication_date")
        or meta_values(soup, "article:published_time")
        or meta_values(soup, "date")
        or [""]
    )[0]
    authors = meta_values(soup, "citation_author") or meta_values(soup, "author")
    keywords: list[str] = []
    for raw in meta_values(soup, "keywords"):
        keywords.extend([norm(part) for part in raw.split(",") if norm(part)])

    pdf_link = next((node["href"] for node in soup.find_all("a", href=True) if ".pdf" in node["href"].lower()), "")
    pdf_url = urljoin(url, pdf_link) if pdf_link else ""

    for node in soup(["script", "style", "nav", "footer", "header", "form"]):
        node.decompose()
    text = norm(soup.get_text(" "))

    return ArticleCandidate(
        institution_slug=institution.slug,
        institution_name=institution.name,
        institution_type=institution.institution_type,
        title=title,
        url=url,
        published_date=canonical_date(published),
        summary=summary,
        content_type="article",
        authors=authors,
        keywords=keywords,
        pdf_url=pdf_url,
        source_completeness="summary_only" if not pdf_url else "full_text",
        copyright_boundary=institution.copyright_boundary,
        detail_text=text,
        fetch_status="detail_ok",
    )


def extract_list_links(html_text: str, base_url: str, limit: int) -> list[str]:
    soup = BeautifulSoup(html_text, "lxml")
    links: list[str] = []
    seen: set[str] = set()
    for node in soup.find_all("a", href=True):
        href = urldefrag(urljoin(base_url, node["href"]))[0]
        text = norm(node.get_text(" "))
        if href in seen or not href.startswith("http"):
            continue
        if looks_like_detail_url(href, text):
            seen.add(href)
            links.append(href)
        if len(links) >= limit:
            break
    return links
