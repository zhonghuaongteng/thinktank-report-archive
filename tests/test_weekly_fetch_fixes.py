import csv
from dataclasses import replace
from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from thinktank_watch import cli
from thinktank_watch.audit import audit_rows, write_editorial_review_queue
from thinktank_watch.config import load_institutions
from thinktank_watch.fetch import (
    fetch_detail,
    fetch_list_candidates,
    fetch_sitemap_candidates,
    parse_text_proxy_detail,
    source_url_allowed,
)
from thinktank_watch.models import ArticleCandidate, Institution


@pytest.fixture
def institution():
    return Institution(
        slug="example", name="Example", chinese_name="示例", country_region="",
        institution_type="think_tank", priority="P1", batch=1,
        homepage="https://example.org/", parser="generic",
        copyright_boundary="private_archive",
    )


def candidate(institution, path, **kwargs):
    return ArticleCandidate(
        institution.slug, institution.name, institution.institution_type,
        "Technology research report", f"https://example.org/{path}", **kwargs,
    )


def mock_discovery(monkeypatch, handler):
    monkeypatch.setattr(cli, "make_client", lambda: httpx.Client(transport=httpx.MockTransport(handler)))
    for name in ("fetch_direct_candidates", "fetch_feed_candidates", "fetch_list_candidates"):
        monkeypatch.setattr(cli, name, lambda *args, **kwargs: [])


@pytest.mark.parametrize("backfill", [False, True])
def test_sitemap_weekly_window_and_unchanged_backfill(monkeypatch, institution, backfill):
    institution.sitemap_urls = ["https://example.org/sitemap.xml"]
    entries = [
        ("today", "2026-11-25T10:00:00Z"),
        ("boundary", "2026-11-11"),
        ("too-old", "2026-11-10"),
        ("future", "2026-11-26"),
        ("missing", ""),
        ("invalid", "2026-11-99"),
    ]
    xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
        f"<url><loc>https://example.org/publication/technology-{name}</loc>"
        + (f"<lastmod>{value}</lastmod>" if value else "") + "</url>"
        for name, value in entries
    ) + "</urlset>"
    requests = []

    def handler(request):
        requests.append(str(request.url))
        assert str(request.url) == institution.sitemap_urls[0]
        return httpx.Response(200, text=xml)

    mock_discovery(monkeypatch, handler)
    result = cli.collect_candidates(
        [institution], 10, include_details=False, backfill=backfill, run_date="2026-11-25",
    )
    expected = {name for name, _ in entries} if backfill else {"today", "boundary"}
    assert {item.url.rsplit("technology-", 1)[1] for item in result} == expected
    assert requests == institution.sitemap_urls


ANTIBOT_CASES = [
    "making sure you're not a bot", "client challenge",
    "enable javascript and cookies", "checking your browser",
    "please wait while your request is being verified", "one moment, please",
    "attention required! | cloudflare",
]
TITLE_ONLY_CASES = ["just a moment", "access denied"]


@pytest.mark.parametrize(("marker", "location"), [
    *[(m, loc) for m in ANTIBOT_CASES for loc in ("title", "body")],
    *[(m, "title") for m in TITLE_ONLY_CASES],
])
@pytest.mark.parametrize("route", ["direct", "proxy"])
def test_antibot_replaces_success_status(institution, marker, location, route):
    item = candidate(institution, "publication/technology-report", fetch_status="detail_ok")
    title = marker.upper() if location == "title" else "Technology report"
    body = marker.upper() if location == "body" else "x" * 2100
    if route == "direct":
        with httpx.Client(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text=f"<title>{title}</title><body>{body}</body>")
        )) as client:
            result = fetch_detail(client, institution, item)
    else:
        result = parse_text_proxy_detail(f"Title: {title}\nMarkdown Content:{body}", item, institution)
    assert item.fetch_status == result.fetch_status == "detail_error:antibot"
    assert result.url == item.url


@pytest.mark.parametrize("marker", TITLE_ONLY_CASES)
def test_title_only_markers_ignored_in_body(institution, marker):
    item = candidate(institution, "publication/technology-report")
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, text=f"<title>Technology report</title><body>{marker} {'x' * 300}</body>")
    )) as client:
        result = fetch_detail(client, institution, item)
    assert result.fetch_status != "detail_error:antibot"


def test_antibot_page_uses_text_proxy_fallback(institution, monkeypatch):
    import thinktank_watch.fetch as fetch_module
    proxied = replace(institution, text_proxy_fallback=True)
    item = candidate(proxied, "publication/technology-report")
    monkeypatch.setattr(fetch_module, "fetch_text_proxy", lambda client, url: "Title: Technology report\nMarkdown Content:" + "Real body. " * 50)
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(403, text="<title>Just a moment...</title><body>checking</body>")
    )) as client:
        result = fetch_detail(client, proxied, item)
    assert result.fetch_status != "detail_error:antibot"


@pytest.mark.parametrize("route", ["direct", "proxy"])
def test_antibot_does_not_scan_beyond_body_window(institution, route):
    item = candidate(institution, "publication/technology-report")
    body = "x" * 2001 + " Client challenge"
    if route == "direct":
        with httpx.Client(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text=f"<title>Technology report</title><body>{body}</body>")
        )) as client:
            result = fetch_detail(client, institution, item)
    else:
        result = parse_text_proxy_detail(f"Title: Technology report\nMarkdown Content:{body}", item, institution)
    assert result.fetch_status.startswith("detail_ok")


def test_allow_path_segments_is_scoped_to_institution(institution):
    url = "https://example.org/news/technology-report"
    allowed = replace(institution, allow_path_segments=["news"])
    assert source_url_allowed(url, allowed)
    assert not source_url_allowed(url, institution)
    assert not source_url_allowed("https://example.org/news/events/technology-report", allowed)
    allowed.list_pages = [url]
    assert not source_url_allowed(url, allowed)


def test_institution_config_loads_path_exceptions():
    sources = {item.slug: item for item in load_institutions("config/institutions")}
    jrc = sources["eu-jrc"]
    assert jrc.allow_path_segments == ["news"]
    assert source_url_allowed(jrc.homepage + "news/technology-report", jrc)
    assert source_url_allowed(jrc.homepage + "jrc-news-and-updates/technology-report_en", jrc)
    atlantic = sources["atlantic-council-geotech"]
    assert set(atlantic.allow_path_segments) == {"issue", "programs", "cyber-statecraft-initiative"}
    for page in atlantic.list_pages:
        assert not source_url_allowed(page, atlantic)
        assert source_url_allowed(page.rstrip("/") + "/technology-report/", atlantic)
    assert sources["rand"].allow_path_segments == []


@pytest.mark.parametrize("discovery", ["list", "sitemap"])
def test_path_exceptions_reach_discovery_parser(institution, discovery):
    institution.list_pages = ["https://example.org/issue/artificial-intelligence/"]
    institution.sitemap_urls = ["https://example.org/sitemap.xml"]
    url = "https://example.org/issue/artificial-intelligence/technology-report"
    content = (
        f'<a href="{url}">Technology report</a>' if discovery == "list" else
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{url}</loc><lastmod>2026-11-25</lastmod></url></urlset>'
    )
    fetch = fetch_list_candidates if discovery == "list" else fetch_sitemap_candidates
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, text=content))) as client:
        assert fetch(client, institution, limit=1) == []
        institution.allow_path_segments = ["issue"]
        assert [item.url for item in fetch(client, institution, limit=1)] == [url]


def test_filter_before_limit_preserves_slots_and_skips_seen(monkeypatch, institution):
    def no_requests(request):
        pytest.fail(f"Unexpected request: {request.url}")

    mock_discovery(monkeypatch, no_requests)
    first = candidate(institution, "publication/shared-report")
    second_institution = replace(institution, slug="second")
    invalid = [
        candidate(second_institution, "publication/shared-report"),
        candidate(second_institution, "publication/technology-report?q=ai"),
        candidate(second_institution, "publication/technology-report?search="),
        candidate(second_institution, "publication/technology-report?other=1&page=2"),
        candidate(second_institution, "news/technology-report"),
    ]
    valid = candidate(second_institution, "publication/valid-report?id=1")
    monkeypatch.setattr(
        cli, "fetch_list_candidates",
        lambda client, source, limit: [first] if source.slug == institution.slug else invalid + [valid],
    )
    result = cli.collect_candidates([institution, second_institution], 1, False, run_date="2026-11-25")
    assert result == [first, valid]


def test_antibot_remains_in_audit_and_skips_pdf_enrichment(monkeypatch, institution, tmp_path):
    mock_discovery(monkeypatch, lambda request: httpx.Response(200, text="<title>Client Challenge</title>"))
    item = candidate(
        institution, "publication/technology-report", published_date="2026-11-25",
        priority="P1", pdf_url="https://example.org/report.pdf",
    )
    monkeypatch.setattr(cli, "fetch_list_candidates", lambda *args, **kwargs: [item])
    check_pdf = Mock(side_effect=AssertionError("Blocked detail must not fetch PDF"))
    enrich_pdf = Mock(side_effect=AssertionError("Blocked detail must not enrich PDF"))
    monkeypatch.setattr(cli, "check_pdf", check_pdf)
    monkeypatch.setattr(cli, "enrich_detail_text_from_pdf", enrich_pdf)
    result = cli.collect_candidates([institution], 1, True, run_date="2026-11-25")
    assert result == [item]
    row = audit_rows(result, run_date="2026-11-25")[0]
    assert row["候选数"] == row["详情失败数"] == "1"
    assert row["详情成功数"] == row["近7日可入选数"] == "0"
    check_pdf.assert_not_called()
    enrich_pdf.assert_not_called()
    # Even an old discovery date must not hide the observed blocking status.
    for published in ("2026-11-25", "2025-01-01", ""):
        item.published_date = published
        path = write_editorial_review_queue(tmp_path / "review.csv", result, "2026-11-25")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 1
        assert rows[0]["详情状态"] == "detail_error:antibot"


@pytest.mark.parametrize("command", ["audit", "evaluate", "run_daily"])
@pytest.mark.parametrize("run_date", ["2026-11-25", None])
def test_commands_forward_run_date(monkeypatch, institution, tmp_path, command, run_date):
    args = SimpleNamespace(
        date=run_date, batch=1, institution=None, limit=1, no_details=False,
        backfill=False, output=str(tmp_path / "audit.csv"), state=str(tmp_path / "state.sqlite"),
        write_limit=1, skip_kb=True,
    )
    collect = Mock(return_value=[])
    monkeypatch.setattr(cli, "_load_config", lambda: ([institution], [], None))
    monkeypatch.setattr(cli, "collect_candidates", collect)
    monkeypatch.setattr(cli, "write_run_brief", lambda *args: None)
    monkeypatch.setattr(cli, "load_research_interests", lambda *args: [])
    assert getattr(cli, command)(args) == 0
    assert collect.call_args.kwargs["run_date"] == (run_date or date.today().isoformat())
