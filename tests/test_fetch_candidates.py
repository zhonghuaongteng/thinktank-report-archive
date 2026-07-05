import unittest

import httpx

from thinktank_watch.fetch import _date_from_feed
from thinktank_watch.fetch import fetch_detail
from thinktank_watch.fetch import fetch_list_candidates
from thinktank_watch.fetch import fetch_sitemap_candidates
from thinktank_watch.fetch import interleave_candidate_groups
from thinktank_watch.fetch import source_url_allowed
from thinktank_watch.models import ArticleCandidate
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

    def test_source_url_allowed_rejects_policy_and_platform_index_pages(self):
        institution = Institution(
            slug="itif",
            name="Information Technology and Innovation Foundation",
            chinese_name="信息技术与创新基金会",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=1,
            homepage="https://itif.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(source_url_allowed("https://itif.org/publications/2015/01/10/privacy/", institution))
        self.assertFalse(source_url_allowed("https://itif.org/publications/2015/01/10/copyright/", institution))
        self.assertFalse(source_url_allowed("https://itif.org/en/ai-publications", institution))
        self.assertTrue(
            source_url_allowed(
                "https://itif.org/publications/2026/06/24/economic-consequences-of-section-232-tariffs-on-semiconductor-imports/",
                institution,
            )
        )

    def test_source_url_allowed_rejects_program_pages_even_when_relevant(self):
        institution = Institution(
            slug="atlantic-council-geotech",
            name="Atlantic Council GeoTech Center and Cyber Statecraft Initiative",
            chinese_name="大西洋理事会GeoTech与网络治国项目",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.atlanticcouncil.org/programs/geotech-center/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://www.atlanticcouncil.org/programs/cyber-statecraft-initiative/capacity-building-initiative/",
                institution,
            )
        )
        self.assertTrue(
            source_url_allowed(
                "https://www.atlanticcouncil.org/in-depth-research-reports/report/balancing-openness-and-control-cross-border-health-data-and-ai-governance-in-china/",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.atlanticcouncil.org/blogs/new-atlanticist/us-and-germany-sign-homeland-defense-technology-sharing-agreement/",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.atlanticcouncil.org/cyber-statecraft-initiative/capacity-building-initiative",
                institution,
            )
        )

    def test_source_url_allowed_rejects_publication_series_and_research_team_pages(self):
        institution = Institution(
            slug="hoover-tpa",
            name="Hoover Technology Policy Accelerator",
            chinese_name="胡佛技术政策加速器",
            country_region="United States",
            institution_type="think_tank",
            priority="P1",
            batch=3,
            homepage="https://www.hoover.org/research-teams/technology-policy-accelerator",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://www.hoover.org/publications/chinas-global-sharp-power-weekly-alert",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.hoover.org/research-teams/technology-policy-accelerator",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://www.hoover.org/commentary/focus-areas", institution))
        self.assertFalse(source_url_allowed("https://www.hoover.org/commentary/multimedia", institution))
        self.assertFalse(
            source_url_allowed(
                "https://www.hoover.org/about/connect-with-us/newsletter-subscriptions",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://www.hoover.org/get-involved/subscriptions", institution))

    def test_source_url_allowed_rejects_pagination_index_pages(self):
        institution = Institution(
            slug="cset",
            name="Center for Security and Emerging Technology",
            chinese_name="乔治城安全与新兴技术中心",
            country_region="United States",
            institution_type="university_research_center",
            priority="P0",
            batch=1,
            homepage="https://cset.georgetown.edu/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(source_url_allowed("https://cset.georgetown.edu/publications/page/2/", institution))
        self.assertTrue(
            source_url_allowed(
                "https://cset.georgetown.edu/article/china-seeks-a-i-independence-weakening-trumps-leverage/",
                institution,
            )
        )

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

    def test_source_url_allowed_rejects_index_topic_and_year_pages(self):
        institution = Institution(
            slug="rand",
            name="RAND Corporation",
            chinese_name="兰德公司",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=1,
            homepage="https://www.rand.org/",
            parser="rand",
            copyright_boundary="private_fulltext_archive",
        )

        self.assertFalse(source_url_allowed("https://www.rand.org/zh-hans/publications.html", institution))
        self.assertFalse(source_url_allowed("https://www.rand.org/zh-hans/publications/2016.html", institution))
        self.assertFalse(source_url_allowed("https://www.rand.org/topics/artificial-intelligence.html", institution))
        self.assertFalse(
            source_url_allowed(
                "https://www.rand.org/hsrd/projects/emerging-technologies-and-risk-analysis.html",
                institution,
            )
        )
        self.assertTrue(
            source_url_allowed(
                "https://www.rand.org/zh-hans/publications/2016/exploring-the-course-and-consequences-of-a-sino-us-war.html",
                institution,
            )
        )
        self.assertTrue(source_url_allowed("https://www.rand.org/pubs/research_reports/RRA3892-2.html", institution))

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

    def test_list_candidates_include_configured_topic_pages(self):
        pages = {
            "https://example.org/publications": """
                <a href="/publications/2026/07/digital-policy-report/">Digital policy report</a>
            """,
            "https://example.org/topics/artificial-intelligence": """
                <a href="/publications/2026/07/ai-governance-report/">AI governance report</a>
                <a href="/publications/2026/07/digital-policy-report/">Digital policy report</a>
            """,
        }

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=pages[str(request.url)], request=request)

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
            list_pages=["https://example.org/publications"],
            topic_pages=["https://example.org/topics/artificial-intelligence"],
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            candidates = fetch_list_candidates(client, institution, limit=10)

        self.assertEqual(
            [item.url for item in candidates],
            [
                "https://example.org/publications/2026/07/digital-policy-report/",
                "https://example.org/publications/2026/07/ai-governance-report/",
            ],
        )

    def test_interleave_candidate_groups_preserves_source_diversity_and_dedupes_urls(self):
        def candidate(title: str, url: str) -> ArticleCandidate:
            return ArticleCandidate("example", "Example", "think_tank", title, url)

        candidates = interleave_candidate_groups(
            [
                [
                    candidate("Feed one", "https://example.org/research/feed-one/"),
                    candidate("Feed two", "https://example.org/research/feed-two/"),
                ],
                [
                    candidate("List one", "https://example.org/research/list-one/"),
                    candidate("Duplicate feed one", "https://example.org/research/feed-one"),
                ],
                [candidate("Sitemap one", "https://example.org/research/sitemap-one/")],
            ]
        )

        self.assertEqual(
            [item.title for item in candidates],
            ["Feed one", "List one", "Sitemap one", "Feed two"],
        )

    def test_fetch_detail_rejects_external_redirects(self):
        def handler(request: httpx.Request) -> httpx.Response:
            if str(request.url) == "https://www.hoover.org/research/external-ai-story":
                return httpx.Response(
                    302,
                    headers={"Location": "https://www.cnbc.com/2026/06/17/g7-ai.html"},
                    request=request,
                )
            return httpx.Response(
                200,
                text="<html><head><title>External AI story</title></head><body>outside source</body></html>",
                request=request,
            )

        institution = Institution(
            slug="hoover-tpa",
            name="Hoover Technology Policy Accelerator",
            chinese_name="胡佛技术政策加速器",
            country_region="United States",
            institution_type="think_tank",
            priority="P1",
            batch=3,
            homepage="https://www.hoover.org/research-teams/technology-policy-accelerator",
            parser="generic",
            copyright_boundary="private_archive",
        )
        candidate = ArticleCandidate(
            institution_slug="hoover-tpa",
            institution_name="Hoover Technology Policy Accelerator",
            institution_type="think_tank",
            title="External AI story",
            url="https://www.hoover.org/research/external-ai-story",
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaises(httpx.HTTPError) as raised:
                fetch_detail(client, institution, candidate)

        self.assertIn("outside allowed domains", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
