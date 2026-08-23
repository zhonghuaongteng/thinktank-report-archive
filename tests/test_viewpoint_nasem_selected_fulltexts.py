import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from unittest.mock import patch

from scripts.extend_viewpoint_nasem_selected_fulltexts import (
    SELECTED,
    SELECTED_IDS,
    discover_chapter_urls,
    discover_chapter_count_from_markdown,
    count_archived_chapters,
    same_chapter_content,
    normalize_archive_whitespace,
    extract_main_text,
    fetch_html,
    fetch_jina_markdown,
    fetch_book,
    fetch_book_via_jina,
    selected_slice,
)


class NasemSelectedFulltextsTests(unittest.TestCase):
    def test_archive_whitespace_normalization_removes_line_end_padding(self):
        self.assertEqual(normalize_archive_whitespace("alpha  \n beta\t\n\n"), "alpha\n beta\n")

    def test_selection_covers_cross_period_science_and_innovation_mechanisms(self):
        titles = " ".join(item[1] for item in SELECTED).lower()
        for signal in (
            "academic research", "innovation system", "open science", "reproducibility",
            "nanotechnology", "commercialization", "global cooperation", "human capital",
            "international talent", "scientific discovery",
        ):
            self.assertIn(signal, titles)
        self.assertEqual(len(SELECTED_IDS), 18)

    def test_security_context_is_limited_and_requires_innovation_mechanism(self):
        titles = [item[1].lower() for item in SELECTED]
        security_led = [title for title in titles if "protecting" in title or "security" in title or "defense" in title]
        self.assertEqual(security_led, ["protecting u.s. technological advantage"])
        role = next(item[3] for item in SELECTED if item[0] == 26647)
        self.assertIn("创新生态", role)
        self.assertIn("中国", role)

    def test_chapter_discovery_and_text_extraction_use_official_read_pages(self):
        html = '''<html><body><main><h1>Science and Innovation</h1><p>Research ecosystems matter.</p>
        <a href="/read/26647/chapter/2">Next</a><a href="/read/26647/chapter/1">Current</a></main></body></html>'''
        self.assertEqual(
            discover_chapter_urls(html, 26647),
            [
                "https://www.nationalacademies.org/read/26647/chapter/1",
                "https://www.nationalacademies.org/read/26647/chapter/2",
            ],
        )
        text = extract_main_text(html)
        self.assertIn("Science and Innovation", text)
        self.assertIn("Research ecosystems matter", text)

    def test_slice_keeps_science_innovation_and_china_mechanisms(self):
        source = (
            "Federal research investment and open science infrastructure support innovation and technology transfer.\n\n"
            "China participates in international scientific collaboration and researcher mobility across universities.\n\n"
            "This administrative paragraph is deliberately unrelated and should not be selected into the reusable slice."
        )
        output = selected_slice("Science policy", source)
        self.assertIn("research investment", output)
        self.assertIn("China participates", output)
        self.assertNotIn("administrative paragraph", output)

    def test_official_read_page_retries_rate_limit(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b"<html><main>Science and innovation</main></html>"

        limited = HTTPError("https://example.test", 429, "Too Many Requests", {"Retry-After": "0"}, BytesIO())
        with patch("scripts.extend_viewpoint_nasem_selected_fulltexts.urlopen", side_effect=[limited, Response()]) as opener:
            with patch("time.sleep"):
                try:
                    result = fetch_html("https://example.test")
                except HTTPError:
                    self.fail("fetch_html did not retry an HTTP 429 response")
                self.assertIn("Science and innovation", result)
        self.assertEqual(opener.call_count, 2)

    def test_book_fetch_resumes_from_cached_chapters(self):
        first = '<html><body><main>First research chapter <a href="/read/99/chapter/2">Next</a></main></body></html>'
        second = '<html><body><main>Second innovation chapter</main></body></html>'
        with TemporaryDirectory() as tmp:
            cache = Path(tmp)
            record_cache = cache / "99"
            record_cache.mkdir()
            (record_cache / "chapter-1.html").write_text(first, encoding="utf-8")
            with patch("scripts.extend_viewpoint_nasem_selected_fulltexts.fetch_html", return_value=second) as fetcher:
                try:
                    archive, text, chapters = fetch_book(99, "Test book", cache_root=cache)
                except TypeError:
                    self.fail("fetch_book does not support resumable chapter caching")
        self.assertEqual(chapters, 2)
        self.assertIn("First research chapter", text)
        self.assertIn("Second innovation chapter", text)
        self.assertIn('data-source="https://www.nationalacademies.org/read/99/chapter/2"', archive)
        fetcher.assert_called_once()

    def test_jina_markdown_reveals_full_official_chapter_span(self):
        markdown = (
            "URL Source: https://www.nationalacademies.org/read/25116/chapter/1\n"
            "[Methods](https://www.nationalacademies.org/read/25116/chapter/10)\n"
            "[Appendix](https://www.nationalacademies.org/read/25116/chapter/14)\n"
        )
        self.assertEqual(discover_chapter_count_from_markdown(markdown, 25116), 14)

    def test_single_chapter_official_report_is_valid(self):
        markdown = (
            "URL Source: https://www.nationalacademies.org/read/24905/chapter/1\n\n"
            "Markdown Content:\n" + "Research investment and innovation system evidence. " * 30
        )
        with TemporaryDirectory() as tmp:
            cache = Path(tmp)
            record_cache = cache / "24905"
            record_cache.mkdir()
            (record_cache / "chapter-1.md").write_text(markdown, encoding="utf-8")
            with patch("scripts.extend_viewpoint_nasem_selected_fulltexts.fetch_jina_markdown", return_value=markdown):
                archive, text, chapters = fetch_book_via_jina(24905, "Innovation", cache_root=cache)
        self.assertEqual(chapters, 1)
        self.assertIn("Research investment", text)
        self.assertIn("官方在线阅读第1章", archive)

    def test_jina_book_probe_stops_when_official_reader_wraps_to_front_matter(self):
        first_body = "Front matter for science report. " * 40
        second_body = "Research investment and innovation findings. " * 40
        first = (
            "URL Source: https://www.nationalacademies.org/read/77/chapter/1\n\n"
            "Markdown Content:\n" + first_body
        )
        second = (
            "URL Source: https://www.nationalacademies.org/read/77/chapter/2\n\n"
            "Markdown Content:\n" + second_body
        )
        wrapped = (
            "URL Source: https://www.nationalacademies.org/read/77/chapter/3\n\n"
            "Markdown Content:\n" + first_body
        )
        with TemporaryDirectory() as tmp:
            cache = Path(tmp)
            record_cache = cache / "77"
            record_cache.mkdir()
            (record_cache / "chapter-1.md").write_text(first, encoding="utf-8")
            with patch("scripts.extend_viewpoint_nasem_selected_fulltexts.fetch_jina_markdown", side_effect=[second, wrapped]) as fetcher:
                archive, text, chapters = fetch_book_via_jina(77, "Science report", cache_root=cache)
        self.assertEqual(chapters, 2)
        self.assertIn("Research investment", text)
        self.assertIn("collection-complete: chapter-probe-v2", archive)
        self.assertEqual(fetcher.call_count, 2)

    def test_chapter_wrap_detection_tolerates_small_dynamic_footer_changes(self):
        original = ("Research enterprise front matter and publication navigation. " * 80).strip()
        wrapped = original + " Refreshed 2026-08-23."
        distinct = ("Innovation findings on funding, talent, and commercialization. " * 80).strip()
        self.assertTrue(same_chapter_content(original, wrapped))
        self.assertFalse(same_chapter_content(original, distinct))

    def test_archived_chapter_count_supports_markdown_and_legacy_html(self):
        self.assertEqual(count_archived_chapters("<!-- source: one -->\n<!-- source: two -->"), 2)
        self.assertEqual(count_archived_chapters('<section data-source="one"></section>'), 1)

    def test_jina_fetch_retries_transient_service_error(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b"Markdown Content:\nResearch and innovation"

        unavailable = HTTPError("https://r.jina.ai/example", 503, "Service Unavailable", {}, BytesIO())
        with patch("scripts.extend_viewpoint_nasem_selected_fulltexts.urlopen", side_effect=[unavailable, Response()]) as opener:
            with patch("time.sleep"):
                try:
                    result = fetch_jina_markdown("https://example.test")
                except HTTPError:
                    self.fail("fetch_jina_markdown did not retry a transient HTTP 503 response")
        self.assertIn("Research and innovation", result)
        self.assertEqual(opener.call_count, 2)


if __name__ == "__main__":
    unittest.main()
