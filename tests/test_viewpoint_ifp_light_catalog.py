import unittest

from scripts.extend_viewpoint_ifp_light_catalog import (
    classify_relevance,
    is_relevant_post,
    normalize_post,
    report_id,
)


class IfpLightCatalogTests(unittest.TestCase):
    def test_target_portfolios_enter_light_catalog(self):
        for category in ("Metascience", "High-Skilled Immigration", "Biotechnology", "Emerging Technology"):
            self.assertTrue(is_relevant_post((category,)))
        self.assertFalse(is_relevant_post(("Infrastructure",)))

    def test_wp_post_normalization_preserves_official_metadata(self):
        row = normalize_post(
            {
                "id": 123,
                "date": "2024-06-18T09:30:00",
                "slug": "nist-foundation",
                "link": "https://ifp.org/nist-foundation/",
                "title": {"rendered": "The Case for a NIST Foundation"},
                "excerpt": {"rendered": "<p>A new model for public-private innovation.</p>"},
                "content": {"rendered": '<a href="https://ifp.org/wp-content/uploads/report.pdf">Download PDF</a>'},
                "categories": [2, 5],
            },
            {2: "Metascience", 5: "Emerging Technology"},
        )
        self.assertEqual(row.date, "2024-06-18")
        self.assertEqual(row.title, "The Case for a NIST Foundation")
        self.assertEqual(row.categories, ("Metascience", "Emerging Technology"))
        self.assertEqual(row.pdf_urls, ("https://ifp.org/wp-content/uploads/report.pdf",))

    def test_science_funding_and_translation_are_core(self):
        self.assertEqual(classify_relevance("Science Agencies Need Metascience Units", "Metascience", ""), "核心")
        self.assertEqual(classify_relevance("Fund Organizations, Not Projects", "Metascience", "innovation ecosystem"), "核心")

    def test_stem_talent_and_applied_biotechnology_are_supporting(self):
        self.assertEqual(classify_relevance("Modernizing the H-1B Program", "High-Skilled Immigration", "STEM talent"), "支撑")
        self.assertEqual(classify_relevance("The Triple Rapid Framework", "Biotechnology", "pandemic diagnostics"), "支撑")

    def test_security_alone_stays_context(self):
        self.assertEqual(classify_relevance("A Sprint Toward Security Level 5", "Emerging Technology", "frontier model security"), "语境")
        self.assertEqual(classify_relevance("Preventing AI Sleeper Agents", "Emerging Technology", "model sabotage"), "语境")

    def test_report_id_is_stable(self):
        self.assertEqual(report_id("2024-06-18", "nist-foundation"), "C-IFP-2024-NIST-FOUNDATION")


if __name__ == "__main__":
    unittest.main()
