from __future__ import annotations

import unittest

from scripts.extend_viewpoint_wipo_gii import CHINA_PROFILE, ITEMS, observation_window


class ViewpointWipoGiiTests(unittest.TestCase):
    def test_series_covers_2016_to_2025(self) -> None:
        self.assertEqual([item.year for item in ITEMS], list(range(2016, 2026)))
        self.assertTrue(all(item.pdf.startswith("https://www.wipo.int/") for item in ITEMS))

    def test_only_cross_period_nodes_are_selected(self) -> None:
        self.assertEqual({item.year for item in ITEMS if item.selected}, {2016, 2020, 2024})
        self.assertEqual(CHINA_PROFILE["id"], "C-WIPO-GII-CHINA-2025")

    def test_series_spans_all_catalog_windows(self) -> None:
        self.assertEqual({observation_window(item.year) for item in ITEMS}, {"W1", "W2", "W3"})


if __name__ == "__main__":
    unittest.main()
