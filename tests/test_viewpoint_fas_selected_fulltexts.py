import subprocess
import sys
import unittest
from pathlib import Path

from scripts.extend_viewpoint_fas_light_catalog import report_id
from scripts.extend_viewpoint_fas_selected_fulltexts import SELECTED_ITEMS
from scripts.validate_viewpoint_research import expected_fas_selected_ids


class FasSelectedFulltextsTests(unittest.TestCase):
    def test_script_can_run_from_repository_root(self):
        script = Path(__file__).parents[1] / "scripts" / "extend_viewpoint_fas_selected_fulltexts.py"
        result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_selection_is_small_and_covers_current_publication_sequence(self):
        self.assertEqual(len(SELECTED_ITEMS), 26)
        self.assertEqual({int(item["date"][:4]) for item in SELECTED_ITEMS}, set(range(2020, 2027)))

    def test_selected_ids_follow_light_catalog_rule(self):
        for item in SELECTED_ITEMS:
            slug = str(item["landing"]).rstrip("/").split("/")[-1]
            self.assertEqual(item["id"], report_id(str(item["date"]), slug))

    def test_validator_uses_an_independent_expected_selection(self):
        self.assertEqual({str(item["id"]) for item in SELECTED_ITEMS}, expected_fas_selected_ids())

    def test_selection_covers_science_technology_talent_translation_and_china(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertIn("科学体系与基础研究", axes)
        self.assertIn("研发治理与科研组织", axes)
        self.assertIn("科技人才与科研职业", axes)
        self.assertIn("技术创新与产业转化", axes)
        self.assertIn("关键与通用技术", axes)
        self.assertGreaterEqual(sum(bool(item["china"]) for item in SELECTED_ITEMS), 3)

    def test_security_led_material_is_excluded(self):
        titles = "\n".join(str(item["title"]).lower() for item in SELECTED_ITEMS)
        self.assertNotIn("nuclear", titles)
        self.assertNotIn("missile", titles)
        self.assertNotIn("deterrence", titles)

    def test_selected_source_is_official_wordpress_record(self):
        for item in SELECTED_ITEMS:
            self.assertTrue(str(item["api_url"]).startswith("https://fas.org/wp-json/wp/v2/publications/"))
            self.assertTrue(str(item["landing"]).startswith("https://fas.org/publication/"))


if __name__ == "__main__":
    unittest.main()
