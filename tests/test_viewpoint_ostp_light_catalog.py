from __future__ import annotations

import unittest

from scripts.extend_viewpoint_ostp_light_catalog import (
    BIDEN_ITEMS,
    CURRENT_ITEMS,
    OBAMA_ITEMS,
    observation_window,
    parse_trump_archive,
    theme_labels,
)


class OstpLightCatalogTests(unittest.TestCase):
    def test_parser_keeps_innovation_and_excludes_security_led_items(self) -> None:
        source = """
        <ul>
          <li><a href="/ai.pdf">National Artificial Intelligence R&amp;D Strategic Plan</a> (June 21, 2019)</li>
          <li><a href="/stem.pdf">Federal STEM Education Strategic Plan</a> (December 2019)</li>
          <li><a href="/security.pdf">Enhancing the Security and Integrity of America's Research Enterprise</a> (October 15, 2020)</li>
          <li><a href="/cyber.pdf">Federal Cybersecurity Strategic Plan</a> (December 10, 2019)</li>
          <li><a href="/nspm.pdf">Fact Sheet: National Security Presidential Memorandum on United States Research and Development National Security Policy</a> (January 16, 2021)</li>
        </ul>
        """
        items = parse_trump_archive(source)
        self.assertEqual([item.title for item in items], ["National Artificial Intelligence R&D Strategic Plan", "Federal STEM Education Strategic Plan"])

    def test_static_items_cover_three_observation_windows_with_sti_focus(self) -> None:
        self.assertEqual(len(OBAMA_ITEMS), 7)
        self.assertEqual(len(BIDEN_ITEMS), 9)
        self.assertEqual(len(CURRENT_ITEMS), 2)
        self.assertEqual({observation_window(item.published) for item in (*OBAMA_ITEMS, *BIDEN_ITEMS)}, {"W1", "W2", "W3"})
        self.assertTrue(all("安全供应链与治理边界" not in item.themes for item in (*OBAMA_ITEMS, *BIDEN_ITEMS, *CURRENT_ITEMS)))

    def test_theme_labels_do_not_add_security_axis(self) -> None:
        themes = theme_labels("National Artificial Intelligence R&D Strategic Plan")
        self.assertIn("科学体系与基础研究", themes)
        self.assertIn("技术创新与关键技术", themes)
        self.assertNotIn("安全供应链与治理边界", themes)


if __name__ == "__main__":
    unittest.main()
