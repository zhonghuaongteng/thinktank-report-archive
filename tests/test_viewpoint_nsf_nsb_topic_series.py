from __future__ import annotations

import importlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


class ViewpointNsfNsbTopicSeriesTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.find_spec("scripts.extend_viewpoint_nsf_nsb_topic_series")
        self.assertIsNotNone(spec, "NSF/NSB topic series collector is missing")
        if spec is None:
            return None
        return importlib.import_module("scripts.extend_viewpoint_nsf_nsb_topic_series")

    def test_two_topics_have_three_comparable_nodes_each(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertEqual(len(module.ITEMS), 6)
        by_topic = {topic: [item.cycle for item in module.ITEMS if item.topic == topic] for topic in {item.topic for item in module.ITEMS}}
        self.assertEqual(by_topic, {"R&D": [2020, 2022, 2024], "Publications": [2020, 2022, 2024]})

    def test_all_sources_are_official_ncses_assets(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertTrue(all(item.landing.startswith("https://ncses.nsf.gov/pubs/") for item in module.ITEMS))
        self.assertTrue(all(item.pdf_url.startswith(item.landing + "/assets/") for item in module.ITEMS))

    def test_science_and_technology_axes_exclude_security_as_a_primary_theme(self) -> None:
        module = self.load_module()
        if module is None:
            return

        self.assertIn("科学体系与基础研究", module.THEMES)
        self.assertIn("技术创新与关键技术", module.THEMES)
        self.assertIn("中国科技横向维度", module.THEMES)
        self.assertNotIn("安全", module.THEMES)

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
