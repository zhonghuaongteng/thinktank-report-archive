from __future__ import annotations

import hashlib
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import feedparser
import httpx
from bs4 import BeautifulSoup

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


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
    "thinktank-watch/0.1"
)


TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
SOURCE_PATH_DENY_SEGMENTS = {
    "categories",
    "category",
    "events",
    "event",
    "issue",
    "issues",
    "people",
    "person",
    "podcast",
    "podcasts",
    "video",
    "videos",
    "webinars",
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


def source_url_allowed(url: str, institution: Institution) -> bool:
    parsed_source = urlparse(url)
    source_host = _normalized_host(parsed_source.netloc)
    allowed_hosts = [_normalized_host(institution.homepage)]
    allowed_hosts.extend(_normalized_host(domain) for domain in institution.allowed_domains)
    if not any(source_host == host or source_host.endswith(f".{host}") for host in allowed_hosts):
        return False
    path_segments = {segment.lower() for segment in parsed_source.path.split("/") if segment}
    last_segment = parsed_source.path.rstrip("/").split("/")[-1].lower()
    return not (path_segments & SOURCE_PATH_DENY_SEGMENTS) and last_segment not in NON_CONTENT_LAST_SEGMENTS


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
    for page in institution.list_pages[:3]:
        try:
            response = client.get(page, timeout=30)
            response.raise_for_status()
        except httpx.HTTPError:
            continue
        links = extract_list_links(response.text, page, limit)
        for link in links:
            if not source_url_allowed(link, institution):
                continue
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
    return candidates[:limit]


def fetch_sitemap_candidates(
    client: httpx.Client,
    institution: Institution,
    limit: int = 200,
) -> list[ArticleCandidate]:
    candidates: list[ArticleCandidate] = []
    for sitemap_url in institution.sitemap_urls:
        try:
            response = client.get(sitemap_url, timeout=30)
            response.raise_for_status()
        except httpx.HTTPError:
            continue
        soup = BeautifulSoup(response.text, "xml")
        for node in soup.find_all("url"):
            loc = norm(node.loc.get_text()) if node.loc else ""
            if not loc:
                continue
            if not source_url_allowed(loc, institution):
                continue
            if institution.sitemap_include_keywords:
                if not any(keyword.lower() in loc.lower() for keyword in institution.sitemap_include_keywords):
                    continue
            elif not looks_like_detail_url(loc):
                continue
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
            if len(candidates) >= limit:
                break
    return candidates[:limit]


def fetch_detail(client: httpx.Client, institution: Institution, candidate: ArticleCandidate) -> ArticleCandidate:
    response = client.get(candidate.url, timeout=30, follow_redirects=True)
    response.raise_for_status()
    if not source_url_allowed(str(response.url), institution):
        raise ExternalSourceError(f"detail redirected outside allowed domains: {response.url}")
    if institution.parser == "rand":
        detail = parse_rand_detail(response.text, str(response.url))
    else:
        detail = parse_generic_detail(response.text, str(response.url), institution)
    if not detail.title:
        detail.title = candidate.title
    if not detail.summary:
        detail.summary = candidate.summary
    if not detail.published_date:
        detail.published_date = candidate.published_date
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


def make_client() -> httpx.Client:
    return httpx.Client(
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        follow_redirects=True,
    )
