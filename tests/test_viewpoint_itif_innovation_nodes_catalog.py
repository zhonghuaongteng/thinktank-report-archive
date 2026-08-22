from __future__ import annotations

import unittest

from scripts.extend_viewpoint_itif_innovation_nodes_catalog import ITEMS, observation_window, stable_report_id


class ItifInnovationNodesCatalogTests(unittest.TestCase):
    def test_items_cover_transition_nodes_and_china(self) -> None:
        self.assertEqual(len(ITEMS), 5)
        self.assertEqual({observation_window(item.published) for item in ITEMS}, {"W3"})
        self.assertTrue(all("中国科技横向维度" in item.themes for item in ITEMS))

    def test_items_are_science_innovation_led(self) -> None:
        allowed = {
            "科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理",
            "人才大学与科研组织", "产业创新转化与区域生态", "国际合作开放科学与比较",
            "中国科技横向维度",
        }
        self.assertTrue(all(set(item.themes) <= allowed for item in ITEMS))
        self.assertTrue(all("安全供应链与治理边界" not in item.themes for item in ITEMS))

    def test_stable_id_uses_official_slug(self) -> None:
        self.assertEqual(
            stable_report_id(ITEMS[0].url),
            "C-ITIF-2022-THE-HAMILTON-INDEX-ASSESSING-NATIONAL-PERFORMANCE-IN-THE-COMPETITION-FOR-ADVANCED-INDUSTRIES",
        )


if __name__ == "__main__":
    unittest.main()
