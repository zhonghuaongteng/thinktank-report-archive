from __future__ import annotations

import importlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


class ViewpointWipoWiprTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.find_spec("scripts.extend_viewpoint_wipo_wipr")
        self.assertIsNotNone(spec, "WIPO WIPR series collector is missing")
        if spec is None:
            return None
        return importlib.import_module("scripts.extend_viewpoint_wipo_wipr")

    def test_series_keeps_2015_as_boundary_and_selects_five_recent_fulltexts(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertEqual([item.year for item in module.ITEMS], [2015, 2017, 2019, 2022, 2024, 2026])
        self.assertEqual({item.year for item in module.ITEMS if item.selected}, {2017, 2019, 2022, 2024, 2026})
        self.assertEqual(next(item for item in module.ITEMS if item.year == 2015).strategy, "边界目录")

    def test_sources_are_official_and_science_technology_innovation_is_primary(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertTrue(all("wipo.int" in item.landing for item in module.ITEMS))
        self.assertTrue(all("wipo.int" in item.pdf_url for item in module.ITEMS if item.selected))
        self.assertIn("科学体系与基础研究", module.THEMES)
        self.assertIn("技术创新与关键技术", module.THEMES)
        self.assertNotIn("安全", module.THEMES)

    def test_series_spans_all_observation_windows(self) -> None:
        module = self.load_module()
        if module is None:
            return
        self.assertEqual({module.observation_window(item.year) for item in module.ITEMS}, {"W1", "W2", "W3"})

    def test_generated_text_normalization_removes_embedded_carriage_returns(self) -> None:
        module = self.load_module()
        if module is None:
            return
        self.assertEqual(module.normalize_generated_text("alpha\r\r\nbeta\r\ngamma\r"), "alpha\nbeta\ngamma\n")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_bytes(b"alpha\r\r\nbeta\r\n")
            module.normalize_generated_file(path)
            self.assertEqual(path.read_bytes(), b"alpha\nbeta\n")


if __name__ == "__main__":
    unittest.main()
