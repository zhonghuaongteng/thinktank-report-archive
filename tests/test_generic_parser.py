import unittest

from thinktank_watch.models import Institution
from thinktank_watch.parsers.generic import extract_list_links, parse_generic_detail


class GenericParserTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
