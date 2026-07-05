from __future__ import annotations

import html
import json
import re
from datetime import datetime
from urllib.parse import unquote, urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from ..models import ArticleCandidate, Institution


ALLOW_TERMS = (
    "publication",
    "report",
    "research",
    "analysis",
    "analyses",
    "article",
    "brief",
    "paper",
    "commentary",
    "post",
    "insight",
)
BROAD_ENDPOINTS = {
    "ai-publications",
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
    "datasets",
    "testimonies-filings",
    "topic",
    "topics",
    "working-papers",
    "policy-briefs",
}
NON_CONTENT_LAST_SEGMENTS = {
    "ai-publications",
    "analyses",
    "copyright",
    "datasets",
    "download",
    "download.do",
    "incidents",
    "insights-papers",
    "overview",
    "policy-briefs",
    "privacy",
    "privacy-policy",
    "research-groups",
    "research-papers",
    "rusi-books",
    "rusi-defence-systems",
    "rusi-journal",
    "rusi-newsbrief",
    "terms",
    "terms-of-use",
    "toolkits",
    "whitehall-papers",
    "working-papers",
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
    "wonk",
}
EXCLUDED_LAST_SEGMENT_PREFIXES = ("call-", "deadline-", "apply-", "registration")
EXCLUDED_LAST_SEGMENT_SUBSTRINGS = ("integrity-statement", "research-priorities")
EXCLUDED_LAST_SEGMENTS = {"focus-areas", "multimedia", "newsletter-subscriptions", "subscriptions"}
EXCLUDED_PATH_SEGMENTS = {
    "about",
    "blog",
    "blogs",
    "books",
    "categories",
    "category",
    "community",
    "cyber-statecraft-initiative",
    "experts",
    "get-involved",
    "how-we-work",
    "issue",
    "issues",
    "knowledge-bases",
    "our-work",
    "people",
    "programs",
    "podcasts",
    "research-teams",
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
DETAIL_TEXT_SELECTORS = (
    ".article-wrapper",
    "article",
    ".article-body",
    ".post-content",
    ".entry-content",
    ".content-body",
    "main",
)
PDF_MATCH_STOP_WORDS = {
    "about",
    "after",
    "agenda",
    "analysis",
    "and",
    "are",
    "brief",
    "comment",
    "comments",
    "for",
    "from",
    "has",
    "how",
    "into",
    "next",
    "not",
    "of",
    "on",
    "over",
    "paper",
    "policy",
    "report",
    "research",
    "should",
    "that",
    "the",
    "their",
    "this",
    "to",
    "what",
    "when",
    "where",
    "with",
}
MIN_DETAIL_TEXT_LENGTH = 500
GENERIC_SUMMARY_PATTERNS = (
    "the place to find",
    "publications, reports, and people",
    "provides decision-makers with",
    "publishes rigorous, data-driven research",
    "through our written products",
)


def norm(value: str | None) -> str:
    text = html.unescape(value or "")
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "lxml").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def canonical_date(value: str) -> str:
    value = norm(value)
    if not value:
        return ""
    if re.match(r"^\d{4}-\d{2}-\d{2}T", value):
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
    match = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", value)
    if match:
        month, day, year = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    return ""


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


def infer_content_type(url: str, json_primary: dict) -> str:
    kind = json_primary.get("@type")
    if isinstance(kind, list):
        kinds = {str(item).lower() for item in kind}
    elif kind:
        kinds = {str(kind).lower()}
    else:
        kinds = set()
    if "report" in kinds:
        return "report"
    if "scholarlyarticle" in kinds:
        return "paper"
    if "blogposting" in kinds:
        return "post"

    segments = [segment.lower() for segment in urlparse(url).path.split("/") if segment]
    if any(segment in {"report", "reports", "research_reports", "research-report", "research-reports"} for segment in segments):
        return "report"
    if any(segment.endswith("-report") or segment.endswith("-reports") for segment in segments):
        return "report"
    if any(segment in {"paper", "papers", "working-paper", "working-papers"} for segment in segments):
        return "paper"
    if any(segment in {"brief", "briefs", "policy-brief", "policy-briefs", "issue-brief", "issue-briefs"} for segment in segments):
        return "brief"
    if any(segment in {"post", "posts"} for segment in segments):
        return "post"
    return "article"


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


def _title_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def clean_detail_title(title: str, institution: Institution) -> str:
    title = norm(title)
    if not title:
        return ""
    host = _normalized_host(institution.homepage)
    host_labels = [part for part in host.split(".") if part not in {"org", "com", "net", "edu", "ai", "uk", "eu"}]
    allowed_suffixes = {
        _title_token(institution.slug),
        _title_token(institution.name),
        _title_token(institution.chinese_name),
        *(_title_token(label) for label in host_labels),
    }
    for separator in (" | ", " - ", " – ", " — "):
        if separator not in title:
            continue
        left, right = title.rsplit(separator, 1)
        right_token = _title_token(right)
        if right_token in allowed_suffixes or any(token and token in right_token for token in allowed_suffixes):
            return left.strip()
    return title


def _normalized_host(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = (parsed.netloc or parsed.path).lower().strip("/")
    return host[4:] if host.startswith("www.") else host


def _host_matches(host: str, allowed: str) -> bool:
    return host == allowed or host.endswith(f".{allowed}")


def _source_pdf_link(url: str, page_url: str, institution: Institution) -> bool:
    pdf_host = _normalized_host(url)
    page_host = _normalized_host(page_url)
    allowed_hosts = [_normalized_host(institution.homepage)]
    allowed_hosts.extend(_normalized_host(domain) for domain in institution.allowed_domains)
    return _host_matches(pdf_host, page_host) or any(_host_matches(pdf_host, host) for host in allowed_hosts)


def _download_pdf_label(text: str) -> bool:
    label = text.lower()
    if label in {"pdf", "download", "download pdf", "full report", "report pdf"}:
        return True
    return any(token in label for token in ("download pdf", "download report", "full report"))


def _match_terms(value: str) -> set[str]:
    terms = set()
    for term in re.findall(r"[a-z0-9]+", unquote(value).lower()):
        if term == "ai" or (len(term) > 2 and term not in PDF_MATCH_STOP_WORDS):
            terms.add(term)
    return terms


def _pdf_link_matches_title(pdf_url: str, link_text: str, page_url: str, title: str) -> bool:
    title_terms = _match_terms(f"{title} {urlparse(page_url).path}")
    if not title_terms:
        return False
    candidate_terms = _match_terms(f"{urlparse(pdf_url).path} {link_text}")
    matched = title_terms & candidate_terms
    required = 1 if len(title_terms) <= 2 else 2
    return len(matched) >= required


def extract_pdf_url(soup: BeautifulSoup, page_url: str, institution: Institution, title: str = "") -> str:
    for node in soup.find_all("a", href=True):
        href = node["href"]
        if ".pdf" not in href.lower():
            continue
        absolute = urljoin(page_url, href)
        text = norm(node.get_text(" "))
        if _download_pdf_label(text):
            return absolute
        if _source_pdf_link(absolute, page_url, institution) and _pdf_link_matches_title(
            absolute,
            text,
            page_url,
            title,
        ):
            return absolute
    return ""


def summary_looks_generic(value: str) -> bool:
    text = norm(value).lower()
    return any(pattern in text for pattern in GENERIC_SUMMARY_PATTERNS)


def summary_from_detail_text(value: str) -> str:
    text = norm(value)
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = " ".join(sentences[:2]).strip()
    return summary[:700].rstrip()


def extract_detail_text(soup: BeautifulSoup) -> str:
    for node in soup(["script", "style", "nav", "footer", "header", "form", "aside", "noscript", "svg"]):
        node.decompose()
    candidates: list[str] = []
    for selector in DETAIL_TEXT_SELECTORS:
        for node in soup.select(selector):
            text = norm(node.get_text(" "))
            if len(text) >= MIN_DETAIL_TEXT_LENGTH:
                return text
            if text:
                candidates.append(text)
    if candidates:
        return max(candidates, key=len)
    return norm(soup.get_text(" "))


def looks_like_detail_url(url: str, text: str = "") -> bool:
    parsed = urlparse(url)
    if parsed.path.lower().endswith(".pdf"):
        return False
    path_segments = [segment for segment in parsed.path.split("/") if segment]
    if len(path_segments) < 2 or path_segments[-1].lower() in BROAD_ENDPOINTS:
        return False
    last_segment = path_segments[-1].lower()
    if last_segment in NON_CONTENT_LAST_SEGMENTS:
        return False
    if last_segment in EXCLUDED_LAST_SEGMENTS:
        return False
    if last_segment.startswith(EXCLUDED_LAST_SEGMENT_PREFIXES):
        return False
    if any(token in last_segment for token in EXCLUDED_LAST_SEGMENT_SUBSTRINGS):
        return False
    if any(segment.lower() in EXCLUDED_PATH_SEGMENTS or segment.lower().startswith("about-") for segment in path_segments):
        return False
    if len(path_segments) == 2 and path_segments[0].lower() == "publications":
        return False
    haystack = f"{path_segments[-1]} {text}".lower()
    return any(term in haystack for term in ALLOW_TERMS) or any(
        segment.lower() in CONTENT_TYPE_SEGMENTS for segment in path_segments[:-1]
    )


def parse_generic_detail(html_text: str, url: str, institution: Institution) -> ArticleCandidate:
    soup = BeautifulSoup(html_text, "lxml")
    json_primary = json_ld_primary(json_ld_items(soup))
    title = clean_detail_title(
        first_nonempty(
            meta_values(soup, "citation_title"),
            meta_values(soup, "og:title"),
            meta_values(soup, "twitter:title"),
            json_primary.get("headline") or json_primary.get("name"),
            soup.title.get_text(" ", strip=True) if soup.title else "",
        ),
        institution,
    )
    raw_summary = first_nonempty(
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

    text = extract_detail_text(soup)
    summary = raw_summary
    if summary_looks_generic(summary):
        summary = summary_from_detail_text(text) or summary
    pdf_url = extract_pdf_url(soup, url, institution, title)
    completeness = "full_text" if pdf_url or len(text) >= MIN_DETAIL_TEXT_LENGTH else "summary_only"

    return ArticleCandidate(
        institution_slug=institution.slug,
        institution_name=institution.name,
        institution_type=institution.institution_type,
        title=title,
        url=url,
        published_date=canonical_date(published),
        summary=summary,
        content_type=infer_content_type(url, json_primary),
        authors=authors,
        keywords=keywords,
        pdf_url=pdf_url,
        source_completeness=completeness,
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
