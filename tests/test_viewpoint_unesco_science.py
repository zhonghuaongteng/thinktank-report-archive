from __future__ import annotations

import importlib
import importlib.util
import unittest


class ViewpointUnescoScienceTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.find_spec("scripts.extend_viewpoint_unesco_science")
        self.assertIsNotNone(spec, "UNESCO science series collector is missing")
        if spec is None:
            return None
        return importlib.import_module("scripts.extend_viewpoint_unesco_science")

    def test_series_keeps_2015_as_boundary_and_selects_recent_fulltexts(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertEqual([item.year for item in module.ITEMS], [2015, 2020, 2021, 2023, 2026])
        self.assertEqual({item.year for item in module.ITEMS if item.selected}, {2021, 2023, 2026})
        self.assertEqual(next(item for item in module.ITEMS if item.year == 2015).strategy, "边界目录")

    def test_sources_are_official_and_roles_are_not_conflated(self) -> None:
        module = self.load_module()
        if module is None:
            return

        by_year = {item.year: item for item in module.ITEMS}
        self.assertEqual(set(by_year), {2015, 2020, 2021, 2023, 2026})
        self.assertTrue(all("unesco.org" in item.landing for item in module.ITEMS))
        if set(by_year) != {2015, 2020, 2021, 2023, 2026}:
            return
        self.assertEqual(by_year[2021].series, "UNESCO Science Report")
        self.assertEqual(by_year[2020].series, "Global Ocean Science Report")
        self.assertEqual(by_year[2023].series, "UNESCO Open Science Outlook")
        self.assertEqual(by_year[2026].series, "IDSSD Global Report")

    def test_series_spans_all_observation_windows(self) -> None:
        module = self.load_module()
        if module is None:
            return
        self.assertEqual({module.observation_window(item.year) for item in module.ITEMS}, {"W1", "W2", "W3"})


if __name__ == "__main__":
    unittest.main()
