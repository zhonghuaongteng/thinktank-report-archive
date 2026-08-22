from __future__ import annotations

import unittest

from scripts.extend_viewpoint_nesta_selected_fulltexts import (
    ITEMS,
    expected_nesta_selected_ids,
    related_report_ids_for_pdf,
)
from scripts.validate_viewpoint_research import expected_nesta_selected_ids


class NestaSelectedFulltextsTests(unittest.TestCase):
    def test_cross_period_selection_is_small_and_explicit(self) -> None:
        self.assertEqual(len(ITEMS), 10)
        self.assertEqual({item.year for item in ITEMS}, {2016, 2017, 2018, 2019, 2020, 2026})
        self.assertEqual(len(expected_nesta_selected_ids()), 10)

    def test_selection_covers_science_policy_technology_and_translation(self) -> None:
        roles = " ".join(item.reuse_role for item in ITEMS)
        for concept in ("科学", "技术", "创新政策", "研发", "转化"):
            self.assertIn(concept, roles)

    def test_china_materials_are_selected_for_innovation_mechanisms(self) -> None:
        china_items = [item for item in ITEMS if item.china_focus]
        self.assertEqual(len(china_items), 2)
        roles = " ".join(item.reuse_role for item in china_items)
        self.assertIn("创客空间", roles)
        self.assertIn("AI", roles)
        self.assertNotIn("安全", roles)

    def test_every_item_points_to_an_official_pdf_and_landing_page(self) -> None:
        for item in ITEMS:
            self.assertTrue(item.landing.startswith("https://www.nesta.org.uk/report/"))
            self.assertTrue(item.pdf_url.startswith("https://www.nesta.org.uk/documents/"))
            self.assertTrue(item.pdf_url.lower().endswith(".pdf"))

    def test_shared_chapter_pdf_links_related_catalog_rows(self) -> None:
        rows = [
            {"报告ID": "parent", "官方PDF入口": "https://example.org/full.pdf"},
            {"报告ID": "chapter", "官方PDF入口": "https://example.org/full.pdf"},
            {"报告ID": "other", "官方PDF入口": "https://example.org/other.pdf"},
        ]
        self.assertEqual(
            related_report_ids_for_pdf(rows, "https://example.org/full.pdf"),
            {"parent", "chapter"},
        )

    def test_validator_tracks_the_selected_set(self) -> None:
        self.assertEqual(expected_nesta_selected_ids(), {item.report_id for item in ITEMS})


if __name__ == "__main__":
    unittest.main()
