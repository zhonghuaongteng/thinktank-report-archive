import subprocess
import sys
import unittest
from pathlib import Path

from scripts.extend_viewpoint_itif_reports_catalog import report_id
from scripts.extend_viewpoint_itif_selected_fulltexts import SELECTED_ITEMS
from scripts.validate_viewpoint_research import expected_itif_selected_ids


class ItifSelectedFulltextsTests(unittest.TestCase):
    def test_script_can_run_directly_from_repository_root(self):
        script = Path(__file__).parents[1] / "scripts" / "extend_viewpoint_itif_selected_fulltexts.py"
        result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_selected_set_is_small_and_covers_every_year(self):
        self.assertEqual(len(SELECTED_ITEMS), 18)
        self.assertEqual({int(item["date"][:4]) for item in SELECTED_ITEMS}, set(range(2016, 2027)))

    def test_selected_ids_follow_light_catalog_rule(self):
        for item in SELECTED_ITEMS:
            self.assertEqual(item["id"], report_id(item["date"], item["slug"]))

    def test_validator_uses_the_independent_expected_selection(self):
        self.assertEqual({item["id"] for item in SELECTED_ITEMS}, expected_itif_selected_ids())

    def test_selection_covers_science_technology_translation_and_china(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertIn("科学体系与基础研究", axes)
        self.assertIn("研发治理与科研组织", axes)
        self.assertIn("技术创新与产业转化", axes)
        self.assertIn("关键与通用技术", axes)
        self.assertGreaterEqual(sum(bool(item["china"]) for item in SELECTED_ITEMS), 4)

    def test_security_antitrust_and_privacy_led_reports_are_excluded(self):
        titles = "\n".join(item["title"].lower() for item in SELECTED_ITEMS)
        self.assertNotIn("national security strategy", titles)
        self.assertNotIn("antitrust", titles)
        self.assertNotIn("privacy framework", titles)

    def test_selected_assets_use_official_markdown_interface(self):
        for item in SELECTED_ITEMS:
            self.assertEqual(item["markdown_url"], item["landing"].rstrip("/") + ".md")


if __name__ == "__main__":
    unittest.main()
