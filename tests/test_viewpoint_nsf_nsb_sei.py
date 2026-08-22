from __future__ import annotations

import unittest

from scripts.extend_viewpoint_nsf_nsb_sei import ITEMS, observation_window


class ViewpointNsfNsbSeiTests(unittest.TestCase):
    def test_series_covers_every_biennial_edition(self) -> None:
        self.assertEqual([item.year for item in ITEMS], [2016, 2018, 2020, 2022, 2024, 2026])
        self.assertTrue(all(item.landing.startswith("https://") for item in ITEMS))

    def test_only_cross_period_nodes_are_selected(self) -> None:
        self.assertEqual({item.year for item in ITEMS if item.selected}, {2016, 2020, 2024, 2026})

    def test_series_spans_all_catalog_windows(self) -> None:
        self.assertEqual({observation_window(item.year) for item in ITEMS}, {"W1", "W2", "W3"})


if __name__ == "__main__":
    unittest.main()
