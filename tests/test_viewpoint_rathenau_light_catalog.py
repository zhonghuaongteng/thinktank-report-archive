import unittest

from scripts.extend_viewpoint_rathenau_light_catalog import (
    classify_relevance,
    is_light_catalog_item,
    parse_listing_page,
)


LISTING_HTML = """
<article class="node node--report node--view-mode-teaser teaser">
  <h3 class="teaser__heading"><a href="/en/how-science-system-works/research-programmes-mission">Research programmes with a mission</a></h3>
  <span class="theme-label theme-label--small">How the science system works</span>
  <p class="label label--small">Report</p>
  <time class="date" datetime="2022-03-22">22 March 2022</time>
</article>
"""


class RathenauLightCatalogTests(unittest.TestCase):
    def test_parse_listing_page_extracts_official_report_metadata(self):
        rows = parse_listing_page(LISTING_HTML)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Research programmes with a mission")
        self.assertEqual(rows[0]["date"], "2022-03-22")
        self.assertEqual(rows[0]["type"], "Report")
        self.assertEqual(rows[0]["theme"], "How the science system works")
        self.assertEqual(
            rows[0]["url"],
            "https://www.rathenau.nl/en/how-science-system-works/research-programmes-mission",
        )

    def test_current_window_keeps_formal_reports(self):
        self.assertTrue(
            is_light_catalog_item(
                {"date": "2016-03-08", "type": "Report", "title": "Public knowledge organisations"}
            )
        )
        self.assertFalse(
            is_light_catalog_item(
                {"date": "2015-01-01", "type": "Report", "title": "Old report"}
            )
        )

    def test_rd_goes_global_is_an_explicit_near_window_boundary(self):
        self.assertTrue(
            is_light_catalog_item(
                {"date": "2015-10-19", "type": "Report", "title": "R&D goes global"}
            )
        )

    def test_non_report_content_does_not_enter_the_report_catalog(self):
        self.assertFalse(
            is_light_catalog_item(
                {"date": "2025-06-02", "type": "Article", "title": "China profile"}
            )
        )

    def test_science_system_and_emerging_technology_are_core(self):
        self.assertEqual(
            classify_relevance("NWO programmes for curiosity-driven research", "How the science system works", ""),
            "核心",
        )
        self.assertEqual(classify_relevance("Generative AI", "Digitalisation", ""), "核心")

    def test_security_or_platform_governance_alone_is_context(self):
        self.assertEqual(classify_relevance("Cyberspace without conflict", "Digitalisation", ""), "语境")
        self.assertEqual(classify_relevance("Digital threats to democracy", "Digitalisation", ""), "语境")

    def test_applied_technology_with_innovation_mechanism_is_supporting(self):
        self.assertEqual(
            classify_relevance("Making better decisions about data centres", "Digitalisation", ""),
            "支撑",
        )


if __name__ == "__main__":
    unittest.main()
