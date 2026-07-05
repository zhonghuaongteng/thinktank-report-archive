import unittest

from thinktank_watch.models import Institution
from thinktank_watch.parsers.generic import extract_list_links, norm, parse_generic_detail


class GenericParserTests(unittest.TestCase):
    def test_norm_strips_html_from_feed_titles(self):
        value = '<a href="https://www.hoover.org/research/china-ai" hreflang="en">China AI Policy</a>'

        self.assertEqual(norm(value), "China AI Policy")

    def test_extract_list_links_skips_navigation_and_category_pages(self):
        html = """
        <html><body>
          <a href="/publications/">Publications</a>
          <a href="/reports">Reports</a>
          <a href="/articles-multimedia">Articles & Multimedia</a>
          <a href="/publications/press-releases/">Press Releases</a>
          <a href="/publications/reports-briefings/">Reports & Briefings</a>
          <a href="/centers/center-for-technology-innovation/research-and-commentary/">Research and commentary</a>
          <a href="/research/defense">Defense</a>
          <a href="/research/fellowship-programs">Fellowship Programs</a>
          <a href="/publications/commentary/">Commentary</a>
          <a href="/publications/testimonies-filings/">Testimonies & Filings</a>
          <a href="/publications/books/">Books & Edited Volumes</a>
          <a href="/publications/knowledge-bases/">Knowledge Bases</a>
          <a href="/publications/podcasts/">Podcasts</a>
          <a href="/publications/knowledge-bases/to-do-list/">Tech Policy To-Do List</a>
          <a href="/publications/knowledge-bases/attack-tracker/">Non-Tariff Attack Tracker</a>
          <a href="/research/partners">Research Partners</a>
          <a href="/blogs/new-atlanticist/homeland-defense-technology-sharing-agreement/">Old blog update</a>
          <a href="/cyber-statecraft-initiative/capacity-building-initiative">Cyber capacity initiative</a>
          <a href="/publications/chinas-global-sharp-power-weekly-alert">China weekly publication series</a>
          <a href="/research-teams/technology-policy-accelerator">Technology Policy Accelerator</a>
          <a href="/commentary/focus-areas">Commentary key focus areas</a>
          <a href="/commentary/multimedia">Videos and podcasts</a>
          <a href="/about/connect-with-us/newsletter-subscriptions">Newsletter subscriptions</a>
          <a href="/get-involved/subscriptions">Subscriptions</a>
          <a href="/ceps-publications/ceps-research-priorities-2024-2025/">Research Priorities 2024-2025</a>
          <a href="/about-ceps/ceps-integrity-statement/">CEPS Integrity Statement</a>
          <a href="/our-work/how-we-work/public-participation-research/">Public Participation Research</a>
          <a href="/en/community/hector-de-rivoire">See all posts</a>
          <a href="/en/working-group-innovation-and-commercialisation">Working Group on Innovation and Commercialisation</a>
          <a href="/people/jon-bateman">Jon Bateman commentary</a>
          <a href="/en/wonk/call-ai-in-gov">Deadline extension: Global call for AI in government</a>
          <a href="/research/defense/resourcing-and-building-the-future-force">Resourcing and Building the Future Force</a>
          <a href="/publications/2026/ai-governance-export-controls/">AI governance report</a>
          <a href="/article/china-semiconductor-policy/">China semiconductor policy article</a>
          <a href="/research/2026/advanced-manufacturing-report">Advanced manufacturing report</a>
        </body></html>
        """

        links = extract_list_links(html, "https://example.org/research", limit=10)

        self.assertEqual(
            links,
            [
                "https://example.org/publications/2026/ai-governance-export-controls/",
                "https://example.org/article/china-semiconductor-policy/",
                "https://example.org/research/2026/advanced-manufacturing-report",
            ],
        )

    def test_extract_list_links_rejects_category_pages_even_when_anchor_mentions_reports(self):
        html = """
        <html><body>
          <a href="/issue/artificial-intelligence/">Reports and research on artificial intelligence</a>
          <a href="/programs/cyber-statecraft-initiative/">Cyber research program</a>
          <a href="/in-depth-research-reports/report/commission-on-ai/">Commission on AI report</a>
        </body></html>
        """

        links = extract_list_links(html, "https://www.atlanticcouncil.org/issue/artificial-intelligence/", limit=5)

        self.assertEqual(
            links,
            ["https://www.atlanticcouncil.org/in-depth-research-reports/report/commission-on-ai/"],
        )

    def test_extract_list_links_skips_platform_index_and_policy_pages(self):
        html = """
        <html><body>
          <a href="/en/ai-publications">Papers & Publications</a>
          <a href="/en/incidents">OECD AI Incidents Monitor</a>
          <a href="/en/transparency/overview">HAIP Reporting Framework</a>
          <a href="/publications/2015/01/10/copyright/">Copyright Notice</a>
          <a href="/publications/2015/01/10/privacy/">Privacy Policy</a>
          <a href="/en/wonk/sandboxes-matter-responsible-innovation-public-trust">Why AI Sandboxes matter for responsible innovation and public trust</a>
        </body></html>
        """

        links = extract_list_links(html, "https://oecd.ai/en/wonk", limit=10)

        self.assertEqual(
            links,
            ["https://oecd.ai/en/wonk/sandboxes-matter-responsible-innovation-public-trust"],
        )

    def test_extract_list_links_skips_publication_collection_pages(self):
        html = """
        <html><body>
          <a href="/publications/working-papers">Working Papers</a>
          <a href="/publications/policy-briefs">Policy Briefs</a>
          <a href="/publications/analyses">Analyses</a>
          <a href="/dataset/european-natural-gas-imports">European natural gas imports</a>
          <a href="/working-paper/artificial-intelligence-competition-europe-role-dma-article-67">Artificial-intelligence competition in Europe</a>
        </body></html>
        """

        links = extract_list_links(html, "https://www.bruegel.org/publications", limit=10)

        self.assertEqual(
            links,
            ["https://www.bruegel.org/working-paper/artificial-intelligence-competition-europe-role-dma-article-67"],
        )

    def test_parse_generic_detail_uses_json_ld_date_and_authors(self):
        html = """
        <html><head>
          <meta property="og:title" content="AI Governance and Export Controls">
          <script type="application/ld+json">
          {"@type":"Article","datePublished":"2026-07-03T09:30:00Z","author":[{"name":"Ada Chen"}],"description":"A governance note."}
          </script>
        </head><body><article><p>Artificial intelligence governance detail text.</p></article></body></html>
        """
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
        )

        detail = parse_generic_detail(html, "https://example.org/articles/ai-governance", institution)

        self.assertEqual(detail.published_date, "2026-07-03")
        self.assertEqual(detail.authors, ["Ada Chen"])
        self.assertEqual(detail.summary, "A governance note.")

    def test_parse_generic_detail_strips_matching_site_title_suffix(self):
        html = """
        <html><head>
          <meta property="og:title" content="Measuring AI R&amp;D Automation | GovAI">
        </head><body><main><p>AI R&D automation and governance.</p></main></body></html>
        """
        institution = Institution(
            slug="govai",
            name="Institute for AI Policy and Strategy",
            chinese_name="AI治理研究所",
            country_region="International",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.governance.ai/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(html, "https://www.governance.ai/research-paper/measuring-ai-r-d-automation", institution)

        self.assertEqual(detail.title, "Measuring AI R&D Automation")

    def test_parse_generic_detail_strips_extended_site_title_suffix(self):
        html = """
        <html><head>
          <title>Beyond P(doom) for AI Risk: Quantifying Uncertainty Without Probability | Center for Security and Emerging Technology Georgetown AI</title>
        </head><body><main><p>AI risk uncertainty and governance.</p></main></body></html>
        """
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

        detail = parse_generic_detail(
            html,
            "https://cset.georgetown.edu/publication/beyond-pdoom-for-ai-risk-quantifying-uncertainty-without-probability/",
            institution,
        )

        self.assertEqual(detail.title, "Beyond P(doom) for AI Risk: Quantifying Uncertainty Without Probability")

    def test_parse_generic_detail_falls_back_to_time_datetime(self):
        html = """
        <html><head><title>Semiconductor policy</title></head>
        <body><main><time datetime="2026-07-02">July 2, 2026</time><p>Semiconductor policy text.</p></main></body></html>
        """
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
        )

        detail = parse_generic_detail(html, "https://example.org/reports/semiconductor-policy", institution)

        self.assertEqual(detail.published_date, "2026-07-02")
        self.assertEqual(detail.title, "Semiconductor policy")

    def test_parse_generic_detail_falls_back_to_visible_month_date(self):
        html = """
        <html><head><title>AI sandbox policy</title></head>
        <body><main><p class="meta">March 18, 2026 — 8 minute read</p><p>AI governance sandbox text.</p></main></body></html>
        """
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
        )

        detail = parse_generic_detail(html, "https://example.org/wonk/ai-sandbox-policy", institution)

        self.assertEqual(detail.published_date, "2026-03-18")

    def test_parse_generic_detail_handles_weekday_numeric_publication_date(self):
        html = """
        <html><head>
          <title>Chinese AI Models</title>
          <meta name="citation_publication_date" content="Thu, 07/02/2026 - 12:00">
        </head><body><main><p>Chinese AI models and governance.</p></main></body></html>
        """
        institution = Institution(
            slug="csis",
            name="CSIS",
            chinese_name="战略与国际研究中心",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.csis.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(html, "https://www.csis.org/analysis/what-know-about-chinese-ai-models", institution)

        self.assertEqual(detail.published_date, "2026-07-02")

    def test_parse_generic_detail_prefers_article_body_container(self):
        html = """
        <html><head>
          <title>Responsible AI guidance</title>
          <meta name="description" content="Responsible AI guidance summary.">
        </head><body>
          <div class="policy-menu">AI Incidents Policy areas Papers & Publications</div>
          <main>
            <div class="article-wrapper">
              <p>Companies need trustworthy AI systems.</p>
              <p>The guidance helps businesses manage AI risks across value chains.</p>
            </div>
          </main>
          <aside>Related posts and navigation links</aside>
        </body></html>
        """
        institution = Institution(
            slug="oecd-ai",
            name="OECD.AI Policy Observatory",
            chinese_name="经合组织人工智能政策观察站",
            country_region="International",
            institution_type="intergovernmental",
            priority="P0",
            batch=1,
            homepage="https://oecd.ai/",
            parser="generic",
            copyright_boundary="metadata_summary_archive",
        )

        detail = parse_generic_detail(html, "https://oecd.ai/en/wonk/responsible-ai-guidance", institution)

        self.assertEqual(
            detail.detail_text,
            "Companies need trustworthy AI systems. The guidance helps businesses manage AI risks across value chains.",
        )

    def test_parse_generic_detail_skips_short_article_shell_for_main_body(self):
        html = """
        <html><head>
          <title>AI Has a Memory Problem</title>
          <meta name="description" content="Memory capacity is a constraint for AI deployment.">
        </head><body>
          <article><h1>AI Has a Memory Problem</h1><p>Photo: Stock image</p></article>
          <main>
            <p>AI data centers increasingly depend on high-bandwidth memory supply.</p>
            <p>Advanced memory chips and packaging capacity are becoming a bottleneck for AI deployment.</p>
            <p>Policy responses should expand manufacturing capacity, improve supply-chain visibility, and support industrial competitiveness.</p>
            <p>Public strategy should treat memory as part of the AI infrastructure stack rather than a generic semiconductor input.</p>
            <p>These constraints affect data centers, cloud providers, and national AI strategies across advanced economies.</p>
            <p>Without a resilient memory supply base, AI diffusion could slow even when compute investment remains strong.</p>
          </main>
        </body></html>
        """
        institution = Institution(
            slug="csis",
            name="CSIS",
            chinese_name="战略与国际研究中心",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.csis.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(html, "https://www.csis.org/analysis/ai-has-memory-problem", institution)

        self.assertIn("high-bandwidth memory supply", detail.detail_text)
        self.assertIn("AI infrastructure stack", detail.detail_text)
        self.assertNotEqual(detail.detail_text, "AI Has a Memory Problem Photo: Stock image")
        self.assertEqual(detail.source_completeness, "full_text")

    def test_parse_generic_detail_ignores_external_reference_pdfs(self):
        html = """
        <html><head><title>AI governance brief</title></head>
        <body>
          <main>
            <p>AI governance brief text.</p>
            <a href="https://example.org/reports/source.pdf">Cited source report</a>
          </main>
        </body></html>
        """
        institution = Institution(
            slug="interface",
            name="interface",
            chinese_name="interface欧洲科技政策智库",
            country_region="European Union",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.interface-eu.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(html, "https://www.interface-eu.org/publications/ai-governance-brief", institution)

        self.assertEqual(detail.pdf_url, "")

    def test_parse_generic_detail_accepts_download_pdf_links(self):
        html = """
        <html><head><title>AI governance brief</title></head>
        <body>
          <main>
            <p>AI governance brief text.</p>
            <a href="https://cdn.example.org/brief.pdf">Download PDF</a>
          </main>
        </body></html>
        """
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
        )

        detail = parse_generic_detail(html, "https://example.org/publications/ai-governance-brief", institution)

        self.assertEqual(detail.pdf_url, "https://cdn.example.org/brief.pdf")


if __name__ == "__main__":
    unittest.main()
