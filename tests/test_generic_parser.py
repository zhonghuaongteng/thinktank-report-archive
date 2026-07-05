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
          <a href="/explore-our-research/research-groups">Research Groups</a>
          <a href="/publications/insights-papers">Insights Papers</a>
          <a href="/publications/toolkits">Toolkits</a>
          <a href="/publications/research-papers">Research Papers</a>
          <a href="/publications/rusi-newsbrief">RUSI Newsbrief</a>
          <a href="/publications/rusi-defence-systems">RUSI Defence Systems</a>
          <a href="/publications/rusi-journal">RUSI Journal</a>
          <a href="/publications/whitehall-papers">Whitehall Papers</a>
          <a href="/publications/rusi-books">RUSI Books</a>
          <a href="/common/report/Download.do?reIdx=140&streFileNm=example.pdf">Download.do?reIdx=140</a>
          <a href="/common/report/example.pdf">Report PDF</a>
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

    def test_extract_list_links_accepts_wordpress_post_query_links(self):
        html = """
        <html><body>
          <a href="/en/?page_id=3800">Reports</a>
          <a href="/en/?cat=3">News & Events</a>
          <a href="/en/?p=5827">Digest of Japanese Science and Technology Indicators 2025</a>
        </body></html>
        """

        links = extract_list_links(html, "https://www.nistep.go.jp/en/", limit=10)

        self.assertEqual(links, ["https://www.nistep.go.jp/en/?p=5827"])

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

    def test_parse_generic_detail_strips_site_suffix_from_auxiliary_domain_label(self):
        html = """
        <html><head>
          <title>Australia's defence industry needs a government investment fund | The Strategist</title>
        </head><body><main><p>Defence industry and industrial base policy text.</p></main></body></html>
        """
        institution = Institution(
            slug="aspi",
            name="Australian Strategic Policy Institute",
            chinese_name="澳大利亚战略政策研究所",
            country_region="Australia",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.aspi.org.au/",
            allowed_domains=["https://www.aspistrategist.org.au/"],
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(
            html,
            "https://www.aspistrategist.org.au/australias-defence-industry-needs-a-government-investment-fund/",
            institution,
        )

        self.assertEqual(detail.title, "Australia's defence industry needs a government investment fund")

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
        self.assertEqual(detail.content_type, "report")

    def test_parse_generic_detail_infers_content_type_from_path(self):
        html = """
        <html><head><title>AI competition</title></head>
        <body><main><time datetime="2026-02-18">February 18, 2026</time><p>AI competition policy text.</p></main></body></html>
        """
        institution = Institution(
            slug="bruegel",
            name="Bruegel",
            chinese_name="布鲁盖尔研究所",
            country_region="Europe",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.bruegel.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(
            html,
            "https://www.bruegel.org/working-paper/artificial-intelligence-competition-europe-role-dma-article-67",
            institution,
        )

        self.assertEqual(detail.content_type, "paper")

        rusi_detail = parse_generic_detail(
            html,
            "https://www.rusi.org/explore-our-research/publications/research-papers/china-and-rare-earth-supply-chains",
            institution,
        )

        self.assertEqual(rusi_detail.content_type, "paper")

    def test_parse_generic_detail_marks_external_publication_without_pdf_as_summary_only(self):
        html = """
        <html><head>
          <title>Europe urgently needs cohesion on high-risk technology vendors</title>
          <meta name="description" content="A short RUSI page linking to an external op-ed.">
        </head><body>
          <main>
            <p>A common European approach to managing risks from Chinese technology vendors is vital.</p>
            <p>Read the OpEd.</p>
            <p>Topics Cyber Security and Resilience Technology, Security and Intelligence China.</p>
          </main>
        </body></html>
        """
        institution = Institution(
            slug="rusi",
            name="RUSI Artificial Intelligence and National Security",
            chinese_name="皇家联合军种研究所人工智能与国家安全",
            country_region="United Kingdom",
            institution_type="think_tank",
            priority="P1",
            batch=3,
            homepage="https://www.rusi.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(
            html,
            "https://www.rusi.org/explore-our-research/publications/external-publications/europe-urgently-needs-cohesion-on-high-risk-technology-vendors",
            institution,
        )

        self.assertEqual(detail.content_type, "external_publication")
        self.assertEqual(detail.source_completeness, "summary_only")

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

    def test_parse_generic_detail_replaces_generic_site_description_with_body_excerpt(self):
        html = """
        <html><head>
          <title>Government-Funded Research Seeds Entire Industries. What Would Be Lost Without It.</title>
          <meta name="description" content="The place to find CSET's publications, reports, and people">
        </head><body>
          <main>
            <div class="l-sidebar__main post-content">
              <p>CSET experts examined proposed funding cuts to the National Institutes of Health.</p>
              <p>NIH-backed research plays a foundational role in driving medical innovation, biotechnology growth, and U.S. competitiveness.</p>
            </div>
          </main>
        </body></html>
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
            "https://cset.georgetown.edu/article/government-funded-research-seeds-entire-industries-what-would-be-lost-without-it/",
            institution,
        )

        self.assertIn("NIH-backed research", detail.summary)
        self.assertNotIn("publications, reports, and people", detail.summary)
        self.assertIn("medical innovation", detail.detail_text)

    def test_parse_generic_detail_treats_special_report_number_as_thin_summary(self):
        html = """
        <html><head>
          <title>Greening Steel in a Fragmented World</title>
          <meta name="description" content="Special Report No. 10 By Analyst One and Analyst Two">
        </head><body>
          <main>
            <p>Special report no. 10 BY ANALYST ONE AND ANALYST TWO.</p>
            <p>The global steel industry sits at the center of the industrial transition to a low-carbon economy.</p>
            <p>Steel supports construction, transportation, energy systems, and manufacturing.</p>
            <a href="https://orfamerica.org/s/Greening-Steel-SR10-digital.pdf">Download PDF</a>
          </main>
        </body></html>
        """
        institution = Institution(
            slug="orf-america",
            name="ORF America Technology Policy",
            chinese_name="ORF美国技术政策项目",
            country_region="United States / India",
            institution_type="think_tank",
            priority="P1",
            batch=3,
            homepage="https://orfamerica.org/technology-policy",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(
            html,
            "https://orfamerica.org/newresearch/greening-steel-in-a-fragmented-world-aligning-markets-technology-and-finance",
            institution,
        )

        self.assertEqual(detail.content_type, "report")
        self.assertIn("global steel industry", detail.summary)
        self.assertNotIn("Special Report No. 10 By", detail.summary)

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

    def test_parse_generic_detail_ignores_same_site_reference_pdf_when_title_mismatches(self):
        html = """
        <html><head><title>A Techno-Economic Agenda for the Next Administration</title></head>
        <body>
          <main>
            <p>A techno-economic agenda should support innovation, competition, and industrial capacity.</p>
            <a href="https://www2.itif.org/2017-rd-tax-credit.pdf">R&D tax credit background paper</a>
          </main>
        </body></html>
        """
        institution = Institution(
            slug="itif",
            name="Information Technology and Innovation Foundation",
            chinese_name="信息技术与创新基金会",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=1,
            homepage="https://itif.org/",
            allowed_domains=["www2.itif.org"],
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(
            html,
            "https://itif.org/publications/2024/06/10/a-techno-economic-agenda-for-the-next-administration/",
            institution,
        )

        self.assertEqual(detail.pdf_url, "")

    def test_parse_generic_detail_accepts_same_site_pdf_when_title_matches(self):
        html = """
        <html><head><title>Stack battles: the US-China artificial-intelligence rivalry is moving beyond chips alone</title></head>
        <body>
          <main>
            <p>Artificial intelligence competition increasingly concerns the whole technology stack.</p>
            <a href="https://www.bruegel.org/sites/default/files/2026-06/stack-battles-the-us-china-artificial-intelligence-rivalry-is-moving-beyond-chips-alone.pdf">Brief file</a>
          </main>
        </body></html>
        """
        institution = Institution(
            slug="bruegel",
            name="Bruegel",
            chinese_name="布鲁盖尔研究所",
            country_region="European Union",
            institution_type="think_tank",
            priority="P1",
            batch=2,
            homepage="https://www.bruegel.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )

        detail = parse_generic_detail(
            html,
            "https://www.bruegel.org/analysis/stack-battles-us-china-artificial-intelligence-rivalry-moving-beyond-chips-alone",
            institution,
        )

        self.assertEqual(
            detail.pdf_url,
            "https://www.bruegel.org/sites/default/files/2026-06/stack-battles-the-us-china-artificial-intelligence-rivalry-is-moving-beyond-chips-alone.pdf",
        )

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
