import unittest

import httpx

from thinktank_watch.fetch import _date_from_feed
from thinktank_watch.fetch import fetch_sitemap_candidates
from thinktank_watch.fetch import source_url_allowed
from thinktank_watch.models import Institution


class FetchCandidateTests(unittest.TestCase):
    def test_source_url_allowed_requires_same_site_or_subdomain(self):
        institution = Institution(
            slug="brookings-cti",
            name="Brookings Center for Technology Innovation",
            chinese_name="布鲁金斯技术创新中心",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=1,
            homepage="https://www.brookings.edu/centers/center-for-technology-innovation/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertTrue(source_url_allowed("https://www.brookings.edu/articles/federal-ai-policy/", institution))
        self.assertFalse(source_url_allowed("https://www.cnbc.com/2026/06/17/g7-ai.html", institution))
        self.assertFalse(source_url_allowed("https://www.brookings.edu/podcast/ai-governance/", institution))

    def test_source_url_allowed_accepts_configured_auxiliary_domains(self):
        institution = Institution(
            slug="aspi",
            name="Australian Strategic Policy Institute",
            chinese_name="澳大利亚战略政策研究所",
            country_region="Australia",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.aspi.org.au/",
            parser="generic",
            copyright_boundary="private_archive",
            allowed_domains=["https://www.aspistrategist.org.au/"],
        )

        self.assertTrue(
            source_url_allowed(
                "https://www.aspistrategist.org.au/chinas-military-ai-logistics-peacetime-gains-wartime-vulnerabilities/",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://example.com/china-ai", institution))

    def test_date_from_feed_handles_weekday_numeric_publication_date(self):
        self.assertEqual(_date_from_feed("Fri, 07/03/2026 - 09:20"), "2026-07-03")

    def test_sitemap_candidates_honor_configured_url_keywords(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://example.org/research/2026/07/nuclear-policy</loc><lastmod>2026-07-01</lastmod></url>
          <url><loc>https://example.org/research/2026/07/ai-governance-and-cyber-risk</loc><lastmod>2026-07-02</lastmod></url>
          <url><loc>https://example.org/issue/artificial-intelligence</loc><lastmod>2026-07-03</lastmod></url>
        </urlset>
        """

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=xml, request=request)

        institution = Institution(
            slug="example",
            name="Example",
            chinese_name="示例",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=1,
            homepage="https://example.org/",
            parser="generic",
            copyright_boundary="private_archive",
            sitemap_urls=["https://example.org/sitemap.xml"],
            sitemap_include_keywords=["ai-governance", "cyber", "artificial-intelligence"],
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            candidates = fetch_sitemap_candidates(client, institution, limit=10)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].url, "https://example.org/research/2026/07/ai-governance-and-cyber-risk")
        self.assertEqual(candidates[0].published_date, "2026-07-02")


if __name__ == "__main__":
    unittest.main()
