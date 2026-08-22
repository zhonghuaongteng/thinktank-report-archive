from __future__ import annotations

import unittest

from scripts.extend_viewpoint_eu_eis import ITEMS, observation_window


class ViewpointEuEisTests(unittest.TestCase):
    def test_series_covers_every_annual_edition(self) -> None:
        self.assertEqual([item.year for item in ITEMS], list(range(2016, 2027)))
        self.assertTrue(all(item.landing.startswith("https://op.europa.eu/") for item in ITEMS))
        self.assertTrue(all(item.doi.startswith("10.") for item in ITEMS))

    def test_only_cross_period_nodes_are_selected(self) -> None:
        self.assertEqual({item.year for item in ITEMS if item.selected}, {2016, 2020, 2024, 2026})

    def test_legacy_2016_uses_verified_official_docsroom_pdf(self) -> None:
        item = next(item for item in ITEMS if item.year == 2016)
        self.assertIn("ec.europa.eu/docsroom/documents/17822/", item.attachment)

    def test_series_spans_all_catalog_windows(self) -> None:
        self.assertEqual({observation_window(item.year) for item in ITEMS}, {"W1", "W2", "W3"})


if __name__ == "__main__":
    unittest.main()
