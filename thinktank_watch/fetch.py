from __future__ import annotations

import hashlib
from io import BytesIO
import math
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import feedparser
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from .models import ArticleCandidate, Institution
from .parsers.generic import (
    NON_CONTENT_LAST_SEGMENTS,
    canonical_date,
    extract_list_links,
    looks_like_detail_url,
    norm,
    parse_generic_detail,
)
from .parsers.rand import parse_rand_detail
from .parsers.stepi import extract_stepi_publication_candidates, parse_stepi_detail


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
    "thinktank-watch/0.1"
)
PDF_TEXT_MAX_PAGES = 10
PDF_TEXT_MAX_CHARS = 24000
PDF_TEXT_MIN_HTML_CHARS = 5000
SITEMAP_INDEX_MAX_CHILDREN = 20
LIST_PAGE_FETCH_CAP = 3
TOPIC_PAGE_FETCH_CAP = 8
LIST_LINK_EXTRACTION_CAP = 120
TITLE_STOP_WORDS = {
    "about",
    "after",
    "again",
    "against",
    "amid",
    "analysis",
    "and",
    "are",
    "between",
    "brief",
    "center",
    "from",
    "has",
    "how",
    "into",
    "its",
    "latest",
    "lesson",
    "new",
    "not",
    "note",
    "policy",
    "primer",
    "report",
    "research",
    "should",
    "that",
    "the",
    "their",
    "this",
    "through",
    "what",
    "when",
    "where",
    "with",
}


TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
SOURCE_PATH_DENY_SEGMENTS = {
    "about",
    "blog",
    "blogs",
    "categories",
    "careers",
    "center",
    "centers",
    "connect-with-us",
    "category",
    "cyber-statecraft-initiative",
    "events",
    "event",
    "belfer-news",
    "fellowship",
    "fellowships",
    "get-involved",
    "grant-programs",
    "issue",
    "issues",
    "ai-definitions",
    "in-the-news",
    "news",
    "news-and-comment",
    "network",
    "networks",
    "page",
    "people",
    "person",
    "podcast",
    "podcasts",
    "project",
    "projects",
    "program",
    "programs",
    "topic",
    "topics",
    "type",
    "research-teams",
    "tag",
    "video",
    "videos",
    "webinars",
    "jobs",
    "job",
    "research-area",
    "research-areas",
    "research-event-recordings",
}
SOURCE_LAST_SEGMENT_DENY = {
    "commentary",
    "analyses",
    "capacity-building-initiative",
    "focus-areas",
    "datasets",
    "index",
    "multimedia",
    "newsletter-subscriptions",
    "our-research",
    "subscriptions",
    "policy-briefs",
    "publication",
    "publications",
    "pubs",
    "research",
    "research-and-commentary",
    "staff-and-experts",
    "topic",
    "topics",
    "working-papers",
}


class ExternalSourceError(httpx.HTTPError):
    """Raised when an allowed source URL redirects to an external page."""


def _normalized_host(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = (parsed.netloc or parsed.path).lower().strip("/")
    return host[4:] if host.startswith("www.") else host


def canonical_url(url: str) -> str:
    parsed = urlparse(url.strip())
    path = re_sub_slashes(parsed.path).rstrip("/") or "/"
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMS
    ]
    query = urlencode(query_pairs, doseq=True)
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", query, ""))


def re_sub_slashes(path: str) -> str:
    while "//" in path:
        path = path.replace("//", "/")
    return path


def dedupe_key(url: str) -> str:
    return hashlib.sha256(canonical_url(url).encode("utf-8")).hexdigest()[:16]


def interleave_candidate_groups(groups: list[list[ArticleCandidate]]) -> list[ArticleCandidate]:
    candidates: list[ArticleCandidate] = []
    seen: set[str] = set()
    max_length = max((len(group) for group in groups), default=0)
    for index in range(max_length):
        for group in groups:
            if index >= len(group):
                continue
            candidate = group[index]
            key = dedupe_key(candidate.url)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(candidate)
    return candidates


def source_url_allowed(url: str, institution: Institution) -> bool:
    parsed_source = urlparse(url)
    if parsed_source.path.lower().endswith(".pdf"):
        return False
    if any(key.lower() == "ecipemediapost" for key, _ in parse_qsl(parsed_source.query, keep_blank_values=True)):
        return False
    source_host = _normalized_host(parsed_source.netloc)
    allowed_hosts = [_normalized_host(institution.homepage)]
    allowed_hosts.extend(_normalized_host(domain) for domain in institution.allowed_domains)
    if not any(source_host == host or source_host.endswith(f".{host}") for host in allowed_hosts):
        return False
    ordered_path_segments = [segment.lower() for segment in parsed_source.path.split("/") if segment]
    path_segments = set(ordered_path_segments)
    last_segment = parsed_source.path.rstrip("/").split("/")[-1].lower()
    last_stem = last_segment[:-5] if last_segment.endswith(".html") else last_segment
    if path_segments & SOURCE_PATH_DENY_SEGMENTS:
        return False
    if last_segment in NON_CONTENT_LAST_SEGMENTS or last_stem in NON_CONTENT_LAST_SEGMENTS:
        return False
    if last_stem in SOURCE_LAST_SEGMENT_DENY:
        return False
    if re.search(r"(?:^|-)annual-reports?(?:-|$)", last_stem):
        return False
    if re.search(r"(?:^|-)(awarded|receives?|wins?)-.*-grant(?:-|$)", last_stem):
        return False
    if re.search(r"(?:^|-)grant-.*-foundation(?:-|$)", last_stem):
        return False
    if last_stem.endswith("booking-form"):
        return False
    if re.search(r"(?:^|-)(receives?-award|wins?-award|award-winners?|award-recipients?)(?:-|$)", last_stem):
        return False
    if institution.slug == "hoover-tpa" and last_stem.startswith("articles-"):
        return False
    if institution.slug == "itif" and "canada-post" in last_stem:
        return False
    if institution.slug == "rand" and last_stem == "trumps-iran-war-is-a-dilemma-not-a-debacle":
        return False
    if institution.slug == "bruegel" and last_stem == "ai-cold-war-needs-nonaligned-movement":
        return False
    if institution.slug == "belfer" and re.search(r"(?:^|-)(qlab|webinar|foreign-policy-live)(?:-|$)", last_stem):
        return False
    if len(last_stem) == 4 and last_stem.isdigit():
        return False
    if len(ordered_path_segments) == 2:
        if ordered_path_segments[0] == "publications" and institution.slug != "ecipe":
            return False
    if institution.slug == "csis" and len(ordered_path_segments) == 1:
        return False
    return True


def _date_from_feed(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return canonical_date(value)


def fetch_feed_candidates(institution: Institution, limit: int = 20) -> list[ArticleCandidate]:
    candidates: list[ArticleCandidate] = []
    for feed_url in institution.feeds:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries[:limit]:
            link = getattr(entry, "link", "") or getattr(entry, "id", "")
            if not link:
                continue
            if not source_url_allowed(link, institution):
                continue
            candidates.append(
                ArticleCandidate(
                    institution_slug=institution.slug,
                    institution_name=institution.name,
                    institution_type=institution.institution_type,
                    title=norm(getattr(entry, "title", "")),
                    url=link,
                    published_date=_date_from_feed(
                        norm(getattr(entry, "published", "") or getattr(entry, "updated", ""))
                    ),
                    summary=norm(getattr(entry, "summary", "")),
                    content_type="feed_item",
                    copyright_boundary=institution.copyright_boundary,
                    fetch_status="feed_ok",
                )
            )
    return candidates


def fetch_list_candidates(
    client: httpx.Client,
    institution: Institution,
    limit: int = 10,
) -> list[ArticleCandidate]:
    candidates: list[ArticleCandidate] = []
    seen: set[str] = set()
    pages = [*institution.list_pages[:LIST_PAGE_FETCH_CAP], *institution.topic_pages[:TOPIC_PAGE_FETCH_CAP]]
    for page in pages:
        try:
            response = client.get(page, timeout=30)
            response.raise_for_status()
        except httpx.HTTPError:
            continue
        if institution.slug == "stepi":
            page_candidates = extract_stepi_publication_candidates(response.text, page, institution, limit)
            for candidate in page_candidates:
                if not source_url_allowed(candidate.url, institution):
                    continue
                key = dedupe_key(candidate.url)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(candidate)
                if len(candidates) >= limit:
                    break
            if len(candidates) >= limit:
                break
            continue
        links = extract_list_links(response.text, page, max(limit * 8, LIST_LINK_EXTRACTION_CAP))
        for link in links:
            if not source_url_allowed(link, institution):
                continue
            key = dedupe_key(link)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                ArticleCandidate(
                    institution_slug=institution.slug,
                    institution_name=institution.name,
                    institution_type=institution.institution_type,
                    title=link.rstrip("/").split("/")[-1].replace("-", " ").title(),
                    url=link,
                    content_type="list_item",
                    copyright_boundary=institution.copyright_boundary,
                    fetch_status="list_ok",
                )
            )
            if len(candidates) >= limit:
                break
        if len(candidates) >= limit:
            break
    return candidates[:limit]


def fetch_sitemap_candidates(
    client: httpx.Client,
    institution: Institution,
    limit: int = 200,
) -> list[ArticleCandidate]:
    candidates: list[ArticleCandidate] = []
    seen: set[str] = set()
    for sitemap_url in institution.sitemap_urls:
        for soup in sitemap_soups(client, sitemap_url):
            for node in soup.find_all("url"):
                loc = norm(node.loc.get_text()) if node.loc else ""
                if not loc:
                    continue
                if not source_url_allowed(loc, institution):
                    continue
                if institution.sitemap_include_keywords:
                    if not any(sitemap_include_keyword_matches(loc, keyword) for keyword in institution.sitemap_include_keywords):
                        continue
                elif not looks_like_detail_url(loc):
                    continue
                key = dedupe_key(loc)
                if key in seen:
                    continue
                seen.add(key)
                lastmod = canonical_date(node.lastmod.get_text()) if node.lastmod else ""
                candidates.append(
                    ArticleCandidate(
                        institution_slug=institution.slug,
                        institution_name=institution.name,
                        institution_type=institution.institution_type,
                        title=loc.rstrip("/").split("/")[-1].replace("-", " ").replace(".html", "").title(),
                        url=loc,
                        published_date=lastmod,
                        content_type="sitemap_item",
                        copyright_boundary=institution.copyright_boundary,
                        fetch_status="sitemap_ok",
                    )
                )
    return sorted(candidates, key=lambda item: _date_sort_key(item.published_date), reverse=True)[:limit]


def sitemap_include_keyword_matches(url: str, keyword: str) -> bool:
    needle = keyword.lower().strip()
    if not needle:
        return False
    haystack = url.lower()
    if re.fullmatch(r"[a-z0-9]{1,3}", needle):
        return re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack) is not None
    return needle in haystack


def _date_sort_key(value: str) -> int:
    if len(value or "") < 10:
        return 0
    try:
        return int(value[:10].replace("-", ""))
    except ValueError:
        return 0


def sitemap_soups(client: httpx.Client, sitemap_url: str) -> list[BeautifulSoup]:
    try:
        response = client.get(sitemap_url, timeout=30)
        response.raise_for_status()
    except httpx.HTTPError:
        return []
    soup = BeautifulSoup(response.text, "xml")
    soups = [soup]
    child_urls = [norm(node.loc.get_text()) for node in soup.find_all("sitemap") if node.loc]
    for child_url in child_urls[:SITEMAP_INDEX_MAX_CHILDREN]:
        try:
            child_response = client.get(child_url, timeout=30)
            child_response.raise_for_status()
        except httpx.HTTPError:
            continue
        soups.append(BeautifulSoup(child_response.text, "xml"))
    return soups


def fetch_detail(client: httpx.Client, institution: Institution, candidate: ArticleCandidate) -> ArticleCandidate:
    response = client.get(candidate.url, timeout=30, follow_redirects=True)
    response.raise_for_status()
    if not source_url_allowed(str(response.url), institution):
        raise ExternalSourceError(f"detail redirected outside allowed domains: {response.url}")
    if institution.parser == "rand":
        detail = parse_rand_detail(response.text, str(response.url))
    elif institution.slug == "stepi":
        detail = parse_stepi_detail(response.text, str(response.url), institution)
    else:
        detail = parse_generic_detail(response.text, str(response.url), institution)
    if not detail.title:
        detail.title = candidate.title
    if not detail.summary:
        detail.summary = candidate.summary
    if not detail.published_date:
        detail.published_date = candidate.published_date
    if not detail.authors:
        detail.authors = candidate.authors
    if not detail.keywords:
        detail.keywords = candidate.keywords
    if not detail.subjects:
        detail.subjects = candidate.subjects
    if not detail.pdf_url:
        detail.pdf_url = candidate.pdf_url
    if not detail.pdf_status:
        detail.pdf_status = candidate.pdf_status
    if not detail.external_source_url:
        detail.external_source_url = candidate.external_source_url
    if institution.slug == "stepi" and detail.pdf_url and detail.source_completeness == "summary_only":
        detail.source_completeness = "full_text"
    detail.copyright_boundary = institution.copyright_boundary
    return detail


def check_pdf(client: httpx.Client, candidate: ArticleCandidate) -> ArticleCandidate:
    if not candidate.pdf_url:
        candidate.pdf_status = "none"
        return candidate
    try:
        response = client.head(candidate.pdf_url, timeout=20, follow_redirects=True)
        candidate.pdf_status = f"{response.status_code} {response.headers.get('content-type', '')}".strip()
        if not candidate.published_date:
            candidate.published_date = _date_from_feed(response.headers.get("last-modified", ""))
    except httpx.HTTPError as exc:
        candidate.pdf_status = f"error:{exc.__class__.__name__}"
    return candidate


def _title_terms(title: str) -> list[str]:
    terms: list[str] = []
    for token in re.findall(r"[a-z0-9]+", title.lower()):
        if len(token) < 3 or token in TITLE_STOP_WORDS:
            continue
        terms.append(token)
    return list(dict.fromkeys(terms))


def detail_text_matches_title(text: str, title: str) -> bool:
    terms = _title_terms(title)
    if not terms:
        return True
    haystack = (text or "").lower()
    matches = sum(1 for term in terms if term in haystack)
    required = max(1, min(3, math.ceil(len(terms) * 0.5)))
    return matches >= required


def needs_pdf_text_fallback(candidate: ArticleCandidate) -> bool:
    if not candidate.pdf_url:
        return False
    if not candidate.detail_text:
        return True
    if "related industry briefs" in candidate.detail_text[:5000].lower():
        return True
    if len(candidate.detail_text) < PDF_TEXT_MIN_HTML_CHARS:
        return True
    return not detail_text_matches_title(candidate.detail_text[:4000], candidate.title)


def extract_pdf_text(client: httpx.Client, pdf_url: str) -> str:
    response = client.get(pdf_url, timeout=45, follow_redirects=True)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "pdf" not in content_type.lower() and not response.content.startswith(b"%PDF"):
        return ""
    reader = PdfReader(BytesIO(response.content))
    parts: list[str] = []
    for page in reader.pages[:PDF_TEXT_MAX_PAGES]:
        text = page.extract_text() or ""
        text = norm(text)
        if text:
            parts.append(text)
        if sum(len(part) for part in parts) >= PDF_TEXT_MAX_CHARS:
            break
    return norm(" ".join(parts))[:PDF_TEXT_MAX_CHARS]


def enrich_detail_text_from_pdf(client: httpx.Client, candidate: ArticleCandidate) -> ArticleCandidate:
    if not needs_pdf_text_fallback(candidate):
        return candidate
    try:
        pdf_text = extract_pdf_text(client, candidate.pdf_url)
    except Exception as exc:  # PDF text is a quality fallback; failed extraction should not block archiving.
        suffix = f"text_error:{exc.__class__.__name__}"
        candidate.pdf_status = f"{candidate.pdf_status}; {suffix}" if candidate.pdf_status else suffix
        return candidate
    if pdf_text and detail_text_matches_title(pdf_text[:4000], candidate.title):
        candidate.detail_text = pdf_text
        candidate.source_completeness = "full_text"
    return candidate


def make_client() -> httpx.Client:
    return httpx.Client(
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        follow_redirects=True,
    )
