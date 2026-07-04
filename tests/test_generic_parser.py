import unittest

from thinktank_watch.parsers.generic import extract_list_links


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


if __name__ == "__main__":
    unittest.main()
