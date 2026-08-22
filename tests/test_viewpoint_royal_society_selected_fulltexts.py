import unittest

from scripts.extend_viewpoint_royal_society_selected_fulltexts import (
    SELECTED_TITLES,
    first_official_pdf,
    selected_slice,
)


class RoyalSocietySelectedFulltextsTests(unittest.TestCase):
    def test_selection_covers_science_system_and_technology_chain(self):
        joined = " ".join(SELECTED_TITLES).lower()
        for signal in ("science", "research", "workforce", "translation", "ai", "china-uk"):
            self.assertIn(signal, joined)
        self.assertTrue("technology" in joined or "technical" in joined)
        self.assertEqual(len(SELECTED_TITLES), 11)

    def test_security_led_titles_are_absent(self):
        joined = " ".join(SELECTED_TITLES).lower()
        for signal in ("national security", "export control", "state threats", "cybersecurity"):
            self.assertNotIn(signal, joined)

    def test_first_official_pdf_prefers_report_over_summary(self):
        source = """
[summary](http://royalsociety.org/-/media/project/report-summary.pdf)
[full report](http://royalsociety.org/-/media/project/main-report.pdf)
"""
        self.assertEqual(first_official_pdf(source), "https://royalsociety.org/-/media/project/main-report.pdf")

    def test_slice_keeps_science_innovation_mechanisms(self):
        source = (
            "Scientific research organisations connect long-term funding, technical talent and industrial innovation.\n\n"
            "This unrelated administrative paragraph is deliberately long enough to pass the length threshold but has no relevant concept."
        )
        output = selected_slice("Science report", source)
        self.assertIn("科学技术创新定向摘录", output)
        self.assertIn("Scientific research organisations", output)
        self.assertNotIn("unrelated administrative", output)


if __name__ == "__main__":
    unittest.main()
