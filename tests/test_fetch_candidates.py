import unittest

import httpx

from thinktank_watch.fetch import _date_from_feed
from thinktank_watch.fetch import fetch_detail
from thinktank_watch.fetch import fetch_list_candidates
from thinktank_watch.fetch import fetch_sitemap_candidates
from thinktank_watch.fetch import interleave_candidate_groups
from thinktank_watch.fetch import needs_pdf_text_fallback
from thinktank_watch.fetch import sitemap_include_keyword_matches
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
        self.assertFalse(
            source_url_allowed(
                "https://www.hoover.org/research/articles-china-ai-trade-europe-manufacturing-critical-minerals-taiwan-and-global-markets",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://www.hoover.org/commentary/multimedia", institution))
        self.assertFalse(
            source_url_allowed(
                "https://www.hoover.org/about/connect-with-us/newsletter-subscriptions",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://www.hoover.org/get-involved/subscriptions", institution))

    def test_source_url_allowed_rejects_grant_and_definition_pages(self):
        institution = Institution(
            slug="stanford-hai",
            name="Stanford HAI",
            chinese_name="斯坦福以人为本人工智能研究院",
            country_region="United States",
            institution_type="university_research_center",
            priority="P0",
            batch=1,
            homepage="https://hai.stanford.edu/ai-index",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://hai.stanford.edu/research/grant-programs/hoffman-yee-research-grants",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://hai.stanford.edu/ai-definitions/what-are-robotics", institution))
        self.assertTrue(
            source_url_allowed(
                "https://hai.stanford.edu/ai-index/2026-ai-index-report/research-and-development",
                institution,
            )
        )

        hoover = Institution(
            slug="hoover-tpa",
            name="Hoover Technology Policy Accelerator",
            chinese_name="胡佛技术政策加速器",
            country_region="United States",
            institution_type="university_research_center",
            priority="P1",
            batch=1,
            homepage="https://www.hoover.org/research-teams/technology-policy-accelerator",
            parser="generic",
            copyright_boundary="private_archive",
        )
        self.assertFalse(source_url_allowed("https://www.hoover.org/research/type/working-papers", hoover))
        self.assertFalse(
            source_url_allowed(
                "https://www.hoover.org/research/hoover-institutions-technology-policy-accelerator-awarded-25-million-grant-hewlett",
                hoover,
            )
        )

    def test_source_url_allowed_rejects_itif_canada_post_public_service_reform(self):
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

        self.assertFalse(
            source_url_allowed(
                "https://itif.org/publications/2026/04/01/reforming-canada-post-for-a-lower-volume-era/",
                institution,
            )
        )
        self.assertTrue(
            source_url_allowed(
                "https://itif.org/publications/2025/10/14/rethinking-antitrust-the-case-for-dynamic-competition-policy/",
                institution,
            )
        )

    def test_source_url_allowed_rejects_pdf_and_download_endpoints(self):
        institution = Institution(
            slug="stepi",
            name="Science and Technology Policy Institute",
            chinese_name="韩国科学技术政策研究院",
            country_region="South Korea",
            institution_type="government_research_institute",
            priority="P1",
            batch=3,
            homepage="https://www.stepi.re.kr/site/stepien/main.do",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://www.stepi.re.kr/common/report/Download.do?reIdx=140&cateCont=A0509&streFileNm=example.pdf",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://www.stepi.re.kr/common/report/example.pdf", institution))
        self.assertTrue(
            source_url_allowed(
                "https://www.stepi.re.kr/site/stepien/ex/bbs/View.do?pageIndex=1&bcIdx=42251&cbIdx=1307",
                institution,
            )
        )

    def test_source_url_allowed_rejects_rusi_publication_collection_pages(self):
        institution = Institution(
            slug="rusi",
            name="Royal United Services Institute",
            chinese_name="英国皇家联合军种研究所",
            country_region="United Kingdom",
            institution_type="think_tank",
            priority="P1",
            batch=3,
            homepage="https://www.rusi.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(source_url_allowed("https://www.rusi.org/explore-our-research/research-groups", institution))
        self.assertFalse(source_url_allowed("https://www.rusi.org/publications/research-papers", institution))
        self.assertFalse(source_url_allowed("https://www.rusi.org/publications/rusi-journal", institution))
        self.assertFalse(source_url_allowed("https://www.rusi.org/publications/whitehall-papers", institution))
        self.assertFalse(
            source_url_allowed(
                "https://www.rusi.org/news-and-comment/in-the-news/could-mythos-prompt-trump-admin-u-turn-ai-regulation",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://www.rusi.org/networks/uk-cyber-effects-network", institution))
        self.assertFalse(
            source_url_allowed(
                "https://www.rusi.org/research-event-recordings/recording-understanding-cyber-operations",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.rusi.org/rusi-combat-air-conference-2023-online-member-ticket-booking-form",
                institution,
            )
        )
        self.assertTrue(
            source_url_allowed(
                "https://www.rusi.org/explore-our-research/publications/commentary/future-ai-enabled-defence",
                institution,
            )
        )

    def test_pdf_fallback_prefers_pdf_when_html_has_related_industry_briefs(self):
        candidate = ArticleCandidate(
            institution_slug="stanford-hai",
            institution_name="Stanford HAI",
            institution_type="university_research_center",
            title="Human-Centered Large Language Models",
            url="https://hai.stanford.edu/industry/human-centered-large-language-models",
            pdf_url="https://hai.stanford.edu/assets/files/hai_industry_report_llms_2026.pdf",
            detail_text=(
                "Large language models have moved from research laboratories into everyday infrastructure. "
                "Related Industry Briefs Sustainability and AI Stanford HAI Robotics and AI Stanford HAI"
            ),
        )

        self.assertTrue(needs_pdf_text_fallback(candidate))

    def test_source_url_allowed_rejects_news_pages_before_sitemap_scoring(self):
        institution = Institution(
            slug="csis",
            name="Center for Strategic and International Studies",
            chinese_name="战略与国际研究中心",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.csis.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://www.csis.org/news/csis-schieffer-series-dialogues-securing-cyberspace-discussion-sony-hack-plus-latest-threats",
                institution,
            )
        )
        self.assertFalse(source_url_allowed("https://www.csis.org/economic-security-and-technology", institution))
        self.assertFalse(
            source_url_allowed(
                "https://www.csis.org/economic-security-and-technology/staff-and-experts",
                institution,
            )
        )
        self.assertTrue(
            source_url_allowed(
                "https://www.csis.org/analysis/old-new-making-innovation-work-everyone",
                institution,
            )
        )

    def test_source_url_allowed_rejects_belfer_news_fellowship_and_program_pages(self):
        institution = Institution(
            slug="belfer",
            name="Harvard Belfer Center Science, Technology, and Public Policy",
            chinese_name="哈佛贝尔弗中心科技与公共政策项目",
            country_region="United States",
            institution_type="university_research_center",
            priority="P1",
            batch=1,
            homepage="https://www.belfercenter.org/programs/science-technology-and-public-policy",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://www.belfercenter.org/belfer-news/belfer-center-and-cfr-launch-new-task-force-energy-security-technological-innovation",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.belfercenter.org/fellowship/energy-climate-and-technology-policy",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.belfercenter.org/programs/science-technology-and-public-policy",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.belfercenter.org/publication/david-mccord-dets-program-research-assistant-receives-award-american-astronautical",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.belfercenter.org/research-analysis/qlab-spring-2026-session-1",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.belfercenter.org/research-analysis/navigating-grids-perfect-storm-webinar-andy-sun",
                institution,
            )
        )
        self.assertFalse(
            source_url_allowed(
                "https://www.belfercenter.org/research-analysis/new-geopolitics-energy-foreign-policy-live",
                institution,
            )
        )
        self.assertTrue(
            source_url_allowed(
                "https://www.belfercenter.org/research-analysis/another-technology-race-us-china-quantum-computing-landscape",
                institution,
            )
        )

    def test_source_url_allowed_rejects_known_bruegel_ai_cold_war_false_positive(self):
        institution = Institution(
            slug="bruegel",
            name="Bruegel",
            chinese_name="布鲁盖尔研究所",
            country_region="European Union",
            institution_type="think_tank",
            priority="P1",
            batch=1,
            homepage="https://www.bruegel.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://www.bruegel.org/opinion-piece/ai-cold-war-needs-nonaligned-movement",
                institution,
            )
        )

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
        self.assertFalse(source_url_allowed("https://cset.georgetown.edu/our-research/", institution))
        self.assertFalse(source_url_allowed("https://cset.georgetown.edu/research-area/biotech/", institution))
        self.assertFalse(source_url_allowed("https://cset.georgetown.edu/research-areas/", institution))
        self.assertFalse(source_url_allowed("https://cset.georgetown.edu/job/research-analysts/", institution))
        self.assertFalse(source_url_allowed("https://cset.georgetown.edu/publication/2025-annual-report/", institution))
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
        self.assertFalse(
            source_url_allowed(
                "https://www.rand.org/education-employment-infrastructure/centers/veterans-policy-research.html",
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

    def test_source_url_allowed_rejects_known_rand_iran_external_pdf_false_positive(self):
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
            copyright_boundary="private_archive",
        )

        self.assertFalse(
            source_url_allowed(
                "https://www.rand.org/pubs/commentary/2026/04/trumps-iran-war-is-a-dilemma-not-a-debacle.html",
                institution,
            )
        )

    def test_source_url_allowed_rejects_tag_pages_and_media_post_queries(self):
        institution = Institution(
            slug="ecipe",
            name="European Centre for International Political Economy",
            chinese_name="欧洲国际政治经济中心",
            country_region="European Union",
            institution_type="think_tank",
            priority="P1",
            batch=1,
            homepage="https://ecipe.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        self.assertFalse(source_url_allowed("https://ecipe.org/publications/tag/digital-economy/", institution))
        self.assertFalse(
            source_url_allowed(
                "https://ecipe.org/?ecipemediapost=turning-regulation-into-data-digital-trade-restrictiveness-index",
                institution,
            )
        )
        self.assertTrue(source_url_allowed("https://ecipe.org/insights/dma-ai-interoperability-paradox/", institution))
        self.assertTrue(
            source_url_allowed(
                "https://ecipe.org/publications/trade-in-information-technology-goods-adapting-the-itata-to-21st-century-technological-change/",
                institution,
            )
        )

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

    def test_sitemap_short_keywords_match_url_tokens_not_substrings(self):
        self.assertTrue(sitemap_include_keyword_matches("https://example.org/research/ai-governance", "ai"))
        self.assertFalse(sitemap_include_keyword_matches("https://example.org/analysis/troubled-straits", "ai"))

    def test_sitemap_candidates_expand_sitemap_indexes(self):
        sitemap_index = """<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap><loc>https://example.org/sitemap-posts.xml</loc></sitemap>
        </sitemapindex>
        """
        child_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://example.org/publication/quantum-technology-report</loc><lastmod>2026-05-01</lastmod></url>
        </urlset>
        """

        def handler(request: httpx.Request) -> httpx.Response:
            if str(request.url) == "https://example.org/sitemap.xml":
                return httpx.Response(200, text=sitemap_index, request=request)
            if str(request.url) == "https://example.org/sitemap-posts.xml":
                return httpx.Response(200, text=child_sitemap, request=request)
            return httpx.Response(404, request=request)

        institution = Institution(
            slug="example",
            name="Example",
            chinese_name="示例",
            country_region="United States",
            institution_type="think_tank",
            priority="P1",
            batch=1,
            homepage="https://example.org/",
            parser="generic",
            copyright_boundary="private_archive",
            sitemap_urls=["https://example.org/sitemap.xml"],
            sitemap_include_keywords=["quantum"],
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            candidates = fetch_sitemap_candidates(client, institution, limit=10)

        self.assertEqual([item.url for item in candidates], ["https://example.org/publication/quantum-technology-report"])

    def test_sitemap_candidates_prefer_newer_urls_across_child_sitemaps(self):
        sitemap_index = """<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap><loc>https://example.org/sitemap-old.xml</loc></sitemap>
          <sitemap><loc>https://example.org/sitemap-new.xml</loc></sitemap>
        </sitemapindex>
        """
        old_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://example.org/publication/innovation-policy-old</loc><lastmod>2024-05-01</lastmod></url>
        </urlset>
        """
        new_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://example.org/publication/innovation-policy-new</loc><lastmod>2026-06-01</lastmod></url>
        </urlset>
        """

        def handler(request: httpx.Request) -> httpx.Response:
            pages = {
                "https://example.org/sitemap.xml": sitemap_index,
                "https://example.org/sitemap-old.xml": old_sitemap,
                "https://example.org/sitemap-new.xml": new_sitemap,
            }
            return httpx.Response(200, text=pages[str(request.url)], request=request)

        institution = Institution(
            slug="example",
            name="Example",
            chinese_name="示例",
            country_region="United States",
            institution_type="think_tank",
            priority="P1",
            batch=1,
            homepage="https://example.org/",
            parser="generic",
            copyright_boundary="private_archive",
            sitemap_urls=["https://example.org/sitemap.xml"],
            sitemap_include_keywords=["innovation"],
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            candidates = fetch_sitemap_candidates(client, institution, limit=1)

        self.assertEqual([item.url for item in candidates], ["https://example.org/publication/innovation-policy-new"])

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

    def test_list_candidates_do_not_let_navigation_noise_exhaust_limit(self):
        noisy_links = "\n".join(
            f'<a href="/commentary/topic/noise-{index}">Noise {index}</a>' for index in range(20)
        )
        pages = {
            "https://www.hoover.org/research-teams/technology-policy-accelerator": f"""
                {noisy_links}
                <div class="card-wrapper">
                    <a href="/research/deep-peek-deepseek-ais-talent-and-implications-us-innovation">.</a>
                    <h4>A Deep Peek Into DeepSeek AI's Talent And Implications For US Innovation</h4>
                    <p>Working Papers DOWNLOAD THE REPORT April 21, 2025</p>
                </div>
            """,
        }

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=pages[str(request.url)], request=request)

        institution = Institution(
            slug="hoover-tpa",
            name="Hoover Technology Policy Accelerator",
            chinese_name="胡佛技术政策加速器",
            country_region="United States",
            institution_type="university_research_center",
            priority="P1",
            batch=1,
            homepage="https://www.hoover.org/research-teams/technology-policy-accelerator",
            parser="generic",
            copyright_boundary="private_archive",
            list_pages=["https://www.hoover.org/research-teams/technology-policy-accelerator"],
        )

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            candidates = fetch_list_candidates(client, institution, limit=1)

        self.assertEqual(
            [item.url for item in candidates],
            ["https://www.hoover.org/research/deep-peek-deepseek-ais-talent-and-implications-us-innovation"],
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
