from __future__ import annotations

import unittest

from scripts.extend_viewpoint_belfer_merics_light_gaps import ITEMS, observation_window, stable_report_id


class BelferMericsLightGapTests(unittest.TestCase):
    def test_items_fill_distinct_innovation_nodes(self) -> None:
        self.assertEqual(len(ITEMS), 3)
        self.assertEqual({item.institution_id for item in ITEMS}, {"belfer", "merics"})
        self.assertEqual({observation_window(item.published) for item in ITEMS}, {"W1", "W3"})

    def test_items_are_china_and_innovation_related(self) -> None:
        self.assertTrue(all("中国科技横向维度" in item.themes for item in ITEMS))
        self.assertTrue(all("安全供应链与治理边界" not in item.themes for item in ITEMS))
        self.assertTrue(stable_report_id(ITEMS[0]).startswith("C-LIGHT-MERICS-2016-"))


if __name__ == "__main__":
    unittest.main()
