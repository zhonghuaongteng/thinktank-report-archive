import subprocess
import sys
import unittest
from pathlib import Path

from scripts.extend_viewpoint_itif_reports_catalog import report_id
from scripts.extend_viewpoint_itif_selected_fulltexts import SELECTED_ITEMS
from scripts.build_viewpoint_node_theme_gap_matrix import COVERAGE_THEMES, china_relevance, classify_themes
from scripts.validate_viewpoint_research import expected_itif_selected_ids


class ItifSelectedFulltextsTests(unittest.TestCase):
    def test_script_can_run_directly_from_repository_root(self):
        script = Path(__file__).parents[1] / "scripts" / "extend_viewpoint_itif_selected_fulltexts.py"
        result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_selected_set_is_small_and_covers_every_year(self):
        self.assertEqual(len(SELECTED_ITEMS), 34)
        self.assertLess(len(SELECTED_ITEMS), 40)
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
        self.assertEqual(sum(bool(item["china"]) for item in SELECTED_ITEMS), 21)

    def test_china_advanced_industry_followup_is_exactly_four(self):
        expected = {
            "C-ITIF-RB-2020-HOW-CHINAS-MERCANTILIST-POLICIES-HAVE-UNDERMINED-GLOBAL-INNOVATION-TELECOM",
            "C-ITIF-RB-2021-HEADING-TRACK-IMPACT-CHINAS-MERCANTILIST-POLICIES-GLOBAL-HIGH-SPEED-RAIL",
            "C-ITIF-RB-2025-CHINA-PLANS-TO-DOMINATE-A-KEY-SEMICONDUCTOR-MATERIAL",
            "C-ITIF-RB-2026-COMAC-CHINAS-LOOMING-THREAT-TO-GLOBAL-AVIATION-INDUSTRY",
        }
        previous = expected_itif_selected_ids() - expected
        actual = {item["id"] for item in SELECTED_ITEMS}
        self.assertEqual(actual - previous, expected)
        self.assertTrue(all(item["china"] for item in SELECTED_ITEMS if item["id"] in expected))
        self.assertTrue(all("工业间谍" not in item["role"] and "出口管制" not in item["role"] for item in SELECTED_ITEMS[-4:]))

    def test_independent_thinktank_china_innovation_followup_is_exactly_six(self):
        expected = {
            "C-ITIF-RB-2019-CHINAS-BIOPHARMACEUTICAL-STRATEGY-CHALLENGE-OR-COMPLEMENT-US-INDUSTRY",
            "C-ITIF-RB-2024-HOW-EXPERTS-CHINA-UNITED-KINGDOM-VIEW-AI-RISKS-COLLABORATION",
            "C-ITIF-RB-2025-FROM-FAST-FOLLOWER-TO-INNOVATION-LEADER-RESTRUCTURING-SOUTH-KOREAS-TECHNOLOGY-REGULATION",
            "C-ITIF-RB-2026-US-TECHNOLOGY-COMPANIES-SHOULD-KEEP-OPERATING-IN-CHINA",
            "C-ITIF-RB-2026-HOW-INNOVATIVE-IS-CHINAS-SPACE-INDUSTRY",
            "C-ITIF-RB-2026-CHINAS-BURGEONING-BIOPHARMACEUTICAL-COMPETITIVENESS-DEMANDS-US-RESPONSE",
        }
        previous = expected_itif_selected_ids() - expected
        self.assertEqual({item["id"] for item in SELECTED_ITEMS} - previous, expected)

    def test_bounded_china_innovation_increment_is_present(self):
        expected_increment = {
            "C-ITIF-RB-2020-INNOVATION-DRAG-CHINAS-ECONOMIC-IMPACT-DEVELOPED-NATIONS",
            "C-ITIF-RB-2020-IMPACT-CHINAS-POLICIES-GLOBAL-BIOPHARMACEUTICAL-INDUSTRY-INNOVATION",
            "C-ITIF-RB-2020-IMPACT-CHINAS-PRODUCTION-SURGE-INNOVATION-GLOBAL-SOLAR-PHOTOVOLTAICS",
            "C-ITIF-RB-2020-CHINESE-COMPETITIVENESS-INTERNATIONAL-DIGITAL-ECONOMY",
            "C-ITIF-RB-2021-WHO-WINNING-AI-RACE-CHINA-EU-OR-UNITED-STATES-2021-UPDATE",
            "C-ITIF-RB-2023-2023-HAMILTON-INDEX",
        }
        self.assertTrue(expected_increment.issubset({item["id"] for item in SELECTED_ITEMS}))

    def test_security_antitrust_and_privacy_led_reports_are_excluded(self):
        titles = "\n".join(item["title"].lower() for item in SELECTED_ITEMS)
        self.assertNotIn("national security strategy", titles)
        self.assertNotIn("antitrust", titles)
        self.assertNotIn("privacy framework", titles)

    def test_selected_assets_use_official_markdown_interface(self):
        for item in SELECTED_ITEMS:
            if not item.get("pdf_url"):
                self.assertEqual(item["markdown_url"], item["landing"].rstrip("/") + ".md")

    def test_high_speed_rail_uses_the_official_pdf_instead_of_thin_markdown(self):
        item = next(item for item in SELECTED_ITEMS if "HIGH-SPEED-RAIL" in item["id"])
        self.assertEqual(
            item["pdf_url"],
            "https://cdn.sanity.io/files/03hnmfyj/production/50fed126d9ea61ccdbfb7a60c6e817ec5650f772.pdf",
        )

    def test_curated_axes_make_each_followup_item_visible_to_china_technology_coverage(self):
        for item in SELECTED_ITEMS[-4:]:
            row = {
                "报告名称": item["title"],
                "示踪问题": "；".join(item["axes"]) + "；中国科技横向维度",
            }
            self.assertTrue(classify_themes(row) & set(COVERAGE_THEMES), item["id"])
            self.assertTrue(china_relevance(row), item["id"])


if __name__ == "__main__":
    unittest.main()
