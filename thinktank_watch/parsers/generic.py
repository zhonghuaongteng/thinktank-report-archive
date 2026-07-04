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
EXCLUDED_LAST_SEGMENT_PREFIXES = ("call-", "deadline-", "apply-", "registration")
EXCLUDED_PATH_SEGMENTS = {
    "about",
    "books",
    "community",
    "experts",
    "knowledge-bases",
    "people",
    "podcasts",
    "staff",
    "working-group-data-governance",
    "working-group-future-of-work",
    "working-group-innovation-and-commercialisation",
    "working-group-responsible-ai",
}
VISIBLE_DATE_RE = re.compile(
    r"\b("
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+20\d{2}"
    r"|"
    r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+20\d{2}"
    r")\b",
    re.IGNORECASE,
)


def norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def canonical_date(value: str) -> str:
    value = norm(value)
    if not value:
        return ""
    if "T" in value:
        value = value.split("T", 1)[0]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            parse_value = value[:10] if fmt in {"%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"} else value.replace(".", "")
            return datetime.strptime(parse_value, fmt).date().isoformat()
        except ValueError:
            pass
    match = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", value)
    if match:
        year, month, day = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    return value[:10]


def visible_date(text: str) -> str:
    match = VISIBLE_DATE_RE.search(norm(text))
    return canonical_date(match.group(1)) if match else ""


def meta_values(soup: BeautifulSoup, key: str) -> list[str]:
    values: list[str] = []
    for attr in ("name", "property", "itemprop"):
        for node in soup.find_all("meta", attrs={attr: key}):
            content = node.get("content")
            if content:
                values.append(norm(content))
    return values


def json_ld_items(soup: BeautifulSoup) -> list[dict]:
    items: list[dict] = []
    for node in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(node.get_text())
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and isinstance(data.get("@graph"), list):
            items.extend(item for item in data["@graph"] if isinstance(item, dict))
        elif isinstance(data, list):
            items.extend(item for item in data if isinstance(item, dict))
        elif isinstance(data, dict):
            items.append(data)
    return items


def json_ld_primary(items: list[dict]) -> dict:
    for item in items:
        kind = item.get("@type")
        if isinstance(kind, list):
            kinds = set(kind)
        else:
            kinds = {kind}
        if kinds & {"Article", "NewsArticle", "Report", "ScholarlyArticle", "BlogPosting"}:
            return item
    return items[0] if items else {}


def authors_from_json_ld(item: dict) -> list[str]:
    author = item.get("author")
    if isinstance(author, list):
        return [norm(node.get("name")) for node in author if isinstance(node, dict) and node.get("name")]
    if isinstance(author, dict) and author.get("name"):
        return [norm(author["name"])]
    if isinstance(author, str):
        return [norm(author)]
    return []


def first_nonempty(*values: list[str] | str | None) -> str:
    for value in values:
        if isinstance(value, list):
            for item in value:
                cleaned = norm(item)
                if cleaned:
                    return cleaned
        else:
            cleaned = norm(value)
            if cleaned:
                return cleaned
    return ""


def looks_like_detail_url(url: str, text: str = "") -> bool:
    parsed = urlparse(url)
    path_segments = [segment for segment in parsed.path.split("/") if segment]
    if len(path_segments) < 2 or path_segments[-1].lower() in BROAD_ENDPOINTS:
        return False
    if path_segments[-1].lower().startswith(EXCLUDED_LAST_SEGMENT_PREFIXES):
        return False
    if any(segment.lower() in EXCLUDED_PATH_SEGMENTS for segment in path_segments):
        return False
    haystack = f"{path_segments[-1]} {text}".lower()
    return any(term in haystack for term in ALLOW_TERMS) or any(
        segment.lower() in CONTENT_TYPE_SEGMENTS for segment in path_segments[:-1]
    )


def parse_generic_detail(html_text: str, url: str, institution: Institution) -> ArticleCandidate:
    soup = BeautifulSoup(html_text, "lxml")
    json_primary = json_ld_primary(json_ld_items(soup))
    title = first_nonempty(
        meta_values(soup, "citation_title"),
        meta_values(soup, "og:title"),
        meta_values(soup, "twitter:title"),
        json_primary.get("headline") or json_primary.get("name"),
        soup.title.get_text(" ", strip=True) if soup.title else "",
    )
    summary = first_nonempty(
        meta_values(soup, "description"),
        meta_values(soup, "og:description"),
        meta_values(soup, "twitter:description"),
        json_primary.get("description"),
    )
    time_date = ""
    time_node = soup.find("time")
    if time_node:
        time_date = norm(time_node.get("datetime") or time_node.get_text(" "))
    body_text = norm(soup.get_text(" "))
    published = first_nonempty(
        meta_values(soup, "citation_publication_date"),
        meta_values(soup, "article:published_time"),
        meta_values(soup, "date"),
        json_primary.get("datePublished") or json_primary.get("dateCreated") or json_primary.get("dateModified"),
        time_date,
        visible_date(body_text),
    )
    authors = meta_values(soup, "citation_author") or meta_values(soup, "author") or authors_from_json_ld(json_primary)
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
