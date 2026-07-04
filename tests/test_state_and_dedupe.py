import unittest

import httpx

from thinktank_watch.fetch import canonical_url, dedupe_key, make_client
from thinktank_watch.fetch import check_pdf
from thinktank_watch.models import ArticleCandidate


class StateAndDedupeTests(unittest.TestCase):
    def test_canonical_url_removes_tracking_fragment_and_duplicate_slash(self):
        url = "https://example.org//reports/ai/?utm_source=newsletter&utm_medium=email#section"

        self.assertEqual(canonical_url(url), "https://example.org/reports/ai")

    def test_dedupe_key_uses_canonical_url(self):
        first = "https://example.org/reports/ai/?utm_source=newsletter#summary"
        second = "https://example.org/reports/ai"

        self.assertEqual(dedupe_key(first), dedupe_key(second))

    def test_make_client_uses_browser_like_user_agent(self):
        with make_client() as client:
            user_agent = client.headers["User-Agent"]

        self.assertIn("Mozilla/5.0", user_agent)
        self.assertIn("thinktank-watch", user_agent)

    def test_check_pdf_uses_last_modified_as_missing_date_fallback(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers={"content-type": "application/pdf", "last-modified": "Mon, 29 Jun 2026 17:46:20 GMT"},
                request=request,
            )

        candidate = ArticleCandidate(
            institution_slug="stanford-hai",
            institution_name="Stanford HAI",
            institution_type="university_research_center",
            title="The 2026 AI Index Report",
            url="https://example.org/report",
            pdf_url="https://example.org/report.pdf",
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            checked = check_pdf(client, candidate)

        self.assertEqual(checked.pdf_status, "200 application/pdf")
        self.assertEqual(checked.published_date, "2026-06-29")


if __name__ == "__main__":
    unittest.main()
