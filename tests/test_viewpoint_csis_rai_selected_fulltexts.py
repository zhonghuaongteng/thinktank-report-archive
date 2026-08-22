import unittest
from unittest.mock import patch

from scripts.extend_viewpoint_csis_rai_selected_fulltexts import SELECTED_ITEMS, browser_pdf, official_pdf_urls
from scripts.validate_viewpoint_research import expected_csis_rai_selected_ids


class CsisRaiSelectedFulltextsTests(unittest.TestCase):
    def test_selection_is_small_relative_to_the_light_catalog(self):
        self.assertEqual(len(SELECTED_ITEMS), 21)
        self.assertLess(len(SELECTED_ITEMS), 30)

    def test_selection_covers_every_actual_program_year(self):
        self.assertEqual({item["date"][:4] for item in SELECTED_ITEMS}, {"2021", "2022", "2023", "2024", "2025", "2026"})

    def test_selection_covers_science_technology_and_china_axes(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertIn("科学体系与研发投入", axes)
        self.assertIn("研发治理与科研组织", axes)
        self.assertIn("科技人才与创新生态", axes)
        self.assertIn("技术创新与产业转化", axes)
        self.assertIn("关键与通用技术", axes)
        self.assertGreaterEqual(sum(bool(item["china"]) for item in SELECTED_ITEMS), 6)

    def test_security_led_items_are_not_selected(self):
        titles = "\n".join(item["title"].lower() for item in SELECTED_ITEMS)
        self.assertNotIn("industrial espionage", titles)
        self.assertNotIn("export controls", titles)
        self.assertNotIn("national security commission", titles)

    def test_all_ids_are_program_scoped(self):
        self.assertTrue(all(item["id"].startswith("C-CSIS-RAI-") for item in SELECTED_ITEMS))
        self.assertEqual({item["id"] for item in SELECTED_ITEMS}, expected_csis_rai_selected_ids())

    def test_pdf_ranges_can_finish_without_exposed_content_range(self):
        first = b"%PDF" + b"x" * (1_500_000 - 4)
        second = b"tail"
        with patch(
            "scripts.extend_viewpoint_csis_rai_selected_fulltexts._range_fetch",
            side_effect=[(206, "", first), (206, "", second)],
        ):
            self.assertEqual(browser_pdf("target", "https://example.org/report.pdf"), first + second)

    def test_only_csis_original_attachments_are_treated_as_source_assets(self):
        urls = [
            "https://csis-website-prod.s3.amazonaws.com/s3fs-public/report.pdf?VersionId=x",
            "https://cset.georgetown.edu/wp-content/uploads/cited-report.pdf",
        ]
        self.assertEqual(official_pdf_urls(urls), [urls[0]])


if __name__ == "__main__":
    unittest.main()
