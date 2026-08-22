from __future__ import annotations

import importlib
import importlib.util
import unittest

from scripts.validate_viewpoint_research import expected_nsf_science_innovation_ids


class ViewpointNsfNsbScienceInnovationSeriesTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.find_spec("scripts.extend_viewpoint_nsf_nsb_science_innovation_series")
        self.assertIsNotNone(spec, "NSF/NSB science innovation series collector is missing")
        if spec is None:
            return None
        return importlib.import_module("scripts.extend_viewpoint_nsf_nsb_science_innovation_series")

    def test_four_reusable_topics_have_three_cross_period_nodes_each(self) -> None:
        module = self.load_module()
        if module is None:
            return

        legacy = [item for item in module.ITEMS if item.cycle < 2026]
        by_topic = {
            topic: [item.cycle for item in legacy if item.topic == topic]
            for topic in {item.topic for item in legacy}
        }
        self.assertEqual(
            by_topic,
            {
                "Academic R&D": [2020, 2022, 2024],
                "STEM Workforce": [2020, 2022, 2024],
                "Invention and Innovation": [2020, 2022, 2024],
                "KTI Industries": [2020, 2022, 2024],
            },
        )

    def test_2026_reorganization_is_covered_by_three_integrated_reports(self) -> None:
        module = self.load_module()
        if module is None:
            return

        latest = [item for item in module.ITEMS if item.cycle == 2026]
        self.assertEqual(len(module.ITEMS), 15)
        self.assertEqual(
            {item.topic for item in latest},
            {"Discovery", "STEM Talent", "Translation to Impact"},
        )

    def test_all_sources_are_official_ncses_main_report_pdfs(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertEqual(len({item.report_id for item in module.ITEMS}), len(module.ITEMS))
        self.assertTrue(all(item.landing == f"https://ncses.nsf.gov/pubs/{item.publication_code}" for item in module.ITEMS))
        self.assertTrue(all(item.pdf_url == f"{item.landing}/assets/{item.publication_code}.pdf" for item in module.ITEMS))

    def test_collection_axes_center_science_technology_and_china(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertIn("科学体系与基础研究", module.THEMES)
        self.assertIn("技术创新与关键技术", module.THEMES)
        self.assertIn("人才大学与科研组织", module.THEMES)
        self.assertIn("产业创新转化与区域生态", module.THEMES)
        self.assertIn("中国科技横向维度", module.THEMES)
        self.assertNotIn("安全", module.THEMES)

    def test_validator_tracks_the_complete_selected_set(self) -> None:
        self.assertEqual(
            expected_nsf_science_innovation_ids(),
            {
                "C-NSF-NSB-ARD-2020", "C-NSF-NSB-ARD-2022", "C-NSF-NSB-ARD-2024",
                "C-NSF-NSB-WF-2020", "C-NSF-NSB-WF-2022", "C-NSF-NSB-WF-2024",
                "C-NSF-NSB-INV-2020", "C-NSF-NSB-INV-2022", "C-NSF-NSB-INV-2024",
                "C-NSF-NSB-KTI-2020", "C-NSF-NSB-KTI-2022", "C-NSF-NSB-KTI-2024",
                "C-NSF-NSB-DISC-2026", "C-NSF-NSB-TALENT-2026", "C-NSF-NSB-IMPACT-2026",
            },
        )


if __name__ == "__main__":
    unittest.main()
