from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup

from ..models import ArticleCandidate, Institution
from .generic import canonical_date, norm


def _clean_href(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _query_value(url: str, key: str, default: str = "") -> str:
    query = dict(parse_qsl(urlparse(url).query, keep_blank_values=True))
    return query.get(key, default)


def _authors_from_text(value: str) -> list[str]:
    value = norm(value)
    if not value:
        return []
    return [norm(part) for part in re.split(r"\s*,\s*|·", value) if norm(part)]


def _info_value(text: str, label: str) -> str:
    match = re.search(rf"{re.escape(label)}\s*:\s*(.*?)(?:\bBY\s*:|\bDATE\s*:|\bHIT\s*:|$)", text)
    return norm(match.group(1)) if match else ""


def _detail_url(base_url: str, cb_idx: str, re_idx: str, cate_cont: str) -> str:
    query = urlencode(
        {
            "pageIndex": "1",
            "cbIdx": cb_idx or "1303",
            "reIdx": re_idx,
            "cateCont": cate_cont,
        }
    )
    return urljoin(base_url, f"/site/stepien/ex/bbs/publicationView.do?{query}")


def extract_stepi_publication_candidates(
    html_text: str,
    base_url: str,
    institution: Institution,
    limit: int,
) -> list[ArticleCandidate]:
    soup = BeautifulSoup(html_text, "lxml")
    cb_idx = _query_value(base_url, "cbIdx", "1303")
    candidates: list[ArticleCandidate] = []
    seen: set[str] = set()
    for row in soup.find_all("li"):
        row_text = norm(row.get_text(" "))
        if "Download PDF" not in row_text or "DATE :" not in row_text:
            continue
        title_node = row.select_one("span.title")
        title = norm(title_node.get_text(" ")) if title_node else ""
        if not title:
            continue
        pdf_node = row.find("a", href=lambda value: value and "Download.do" in value)
        if not pdf_node:
            continue
        pdf_url = urljoin(base_url, _clean_href(pdf_node.get("href", "")))
        re_idx = _query_value(pdf_url, "reIdx")
        cate_cont = _query_value(pdf_url, "cateCont")
        if not re_idx:
            continue
        url = _detail_url(base_url, cb_idx, re_idx, cate_cont)
        if url in seen:
            continue
        seen.add(url)
        category_node = row.select_one("em.cate")
        category = norm(category_node.get_text(" ")) if category_node else ""
        candidates.append(
            ArticleCandidate(
                institution_slug=institution.slug,
                institution_name=institution.name,
                institution_type=institution.institution_type,
                title=title,
                url=url,
                published_date=canonical_date(_info_value(row_text, "DATE")),
                summary=f"{category} publication." if category else "",
                content_type="report",
                authors=_authors_from_text(_info_value(row_text, "BY")),
                subjects=[category] if category else [],
                pdf_url=pdf_url,
                source_completeness="full_text",
                copyright_boundary=institution.copyright_boundary,
                fetch_status="list_ok",
            )
        )
        if len(candidates) >= limit:
            break
    return candidates


def parse_stepi_detail(html_text: str, url: str, institution: Institution) -> ArticleCandidate:
    soup = BeautifulSoup(html_text, "lxml")
    board = soup.select_one(".boardView")
    title = ""
    published = ""
    authors: list[str] = []
    detail_text = ""
    if board:
        title_node = board.select_one("h4.title")
        title = norm(title_node.get_text(" ")) if title_node else ""
        info_node = board.select_one(".info")
        info_text = norm(info_node.get_text(" ")) if info_node else ""
        published = canonical_date(_info_value(info_text, "DATE"))
        authors = _authors_from_text(_info_value(info_text, "BY"))
        view_node = board.select_one(".viewCon")
        detail_text = norm(view_node.get_text(" ")) if view_node else ""
    return ArticleCandidate(
        institution_slug=institution.slug,
        institution_name=institution.name,
        institution_type=institution.institution_type,
        title=title,
        url=url,
        published_date=published,
        summary=detail_text[:700].rstrip() if detail_text else "",
        content_type="report",
        authors=authors,
        source_completeness="full_text" if detail_text else "summary_only",
        copyright_boundary=institution.copyright_boundary,
        detail_text=detail_text,
        fetch_status="detail_ok",
    )
