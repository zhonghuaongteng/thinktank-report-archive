import unittest
from io import BytesIO

import httpx
from reportlab.pdfgen import canvas

from thinktank_watch.fetch import canonical_url, dedupe_key, make_client
from thinktank_watch.fetch import check_pdf, enrich_detail_text_from_pdf, fetch_detail
from thinktank_watch.models import ArticleCandidate, Institution


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

    def test_pdf_text_fallback_replaces_misaligned_html_body(self):
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer)
        pdf.drawString(72, 760, "China-U.S. Cyber-Nuclear C3 Stability")
        pdf.drawString(72, 740, "This report examines cyber risks to nuclear command and control.")
        pdf.save()
        pdf_bytes = pdf_buffer.getvalue()

        html = """
        <html><head>
          <meta property="og:title" content="China-U.S. Cyber-Nuclear C3 Stability">
        </head><body>
          <main>
            <a href="/files/c3.pdf">Download PDF</a>
            <p>Unrelated site recommendation text about a different commentary.</p>
          </main>
        </body></html>
        """

        def handler(request: httpx.Request) -> httpx.Response:
            if str(request.url).endswith("/article"):
                return httpx.Response(200, text=html, request=request)
            if request.method == "HEAD":
                return httpx.Response(
                    200,
                    headers={"content-type": "application/pdf"},
                    request=request,
                )
            return httpx.Response(
                200,
                headers={"content-type": "application/pdf"},
                content=pdf_bytes,
                request=request,
            )

        institution = Institution(
            slug="carnegie-tech",
            name="Carnegie Technology and International Affairs Program",
            chinese_name="卡内基技术与国际事务项目",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=1,
            homepage="https://example.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )
        candidate = ArticleCandidate(
            institution_slug=institution.slug,
            institution_name=institution.name,
            institution_type=institution.institution_type,
            title="China-U.S. Cyber-Nuclear C3 Stability",
            url="https://example.org/article",
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            detail = fetch_detail(client, institution, candidate)
            detail = check_pdf(client, detail)
            detail = enrich_detail_text_from_pdf(client, detail)

        self.assertIn("China-U.S. Cyber-Nuclear C3 Stability", detail.detail_text)
        self.assertIn("nuclear command and control", detail.detail_text)
        self.assertNotIn("Unrelated site recommendation", detail.detail_text)


if __name__ == "__main__":
    unittest.main()
