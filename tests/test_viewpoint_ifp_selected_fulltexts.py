import subprocess
import sys
import unittest
from pathlib import Path

from scripts.extend_viewpoint_ifp_light_catalog import report_id
from scripts.extend_viewpoint_ifp_selected_fulltexts import SELECTED_ITEMS
from scripts.validate_viewpoint_research import expected_ifp_selected_ids


class IfpSelectedFulltextsTests(unittest.TestCase):
    def test_script_can_run_directly_from_repository_root(self):
        script = Path(__file__).parents[1] / "scripts" / "extend_viewpoint_ifp_selected_fulltexts.py"
        result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_selected_set_is_small_and_cross_period(self):
        self.assertEqual(len(SELECTED_ITEMS), 16)
        years = {int(item["date"][:4]) for item in SELECTED_ITEMS}
        self.assertEqual(years, {2022, 2023, 2024, 2025, 2026})

    def test_selected_ids_follow_light_catalog_rule(self):
        for item in SELECTED_ITEMS:
            self.assertEqual(item["id"], report_id(item["date"], item["slug"]))

    def test_selection_covers_science_innovation_and_china_comparison(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertIn("科学体系与基础研究", axes)
        self.assertIn("研发治理与科研组织", axes)
        self.assertIn("技术创新与产业转化", axes)
        self.assertIn("关键与通用技术", axes)
        self.assertGreaterEqual(sum(bool(item["china"]) for item in SELECTED_ITEMS), 6)

    def test_incidental_china_mentions_do_not_become_direct_china_evidence(self):
        by_slug = {item["slug"]: item for item in SELECTED_ITEMS}
        self.assertFalse(by_slug["piloting-and-evaluating-nsf-science-lottery-grants"]["china"])
        self.assertFalse(by_slug["scaling-materials-discovery-with-self-driving-labs"]["china"])

    def test_security_led_items_do_not_enter_selected_set(self):
        titles = {item["title"] for item in SELECTED_ITEMS}
        self.assertNotIn("A Sprint Toward Security Level 5", titles)
        self.assertNotIn("Preventing AI Sleeper Agents", titles)

    def test_only_one_selected_asset_is_pdf(self):
        self.assertEqual(sum(item["asset_type"] == "PDF" for item in SELECTED_ITEMS), 1)

    def test_validator_tracks_selected_set(self):
        self.assertEqual(expected_ifp_selected_ids(), {item["id"] for item in SELECTED_ITEMS})


if __name__ == "__main__":
    unittest.main()
