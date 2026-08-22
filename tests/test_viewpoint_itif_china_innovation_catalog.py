from __future__ import annotations

import unittest

from scripts.extend_viewpoint_itif_china_innovation_catalog import SERIES, stable_report_id


class ItifChinaInnovationCatalogTests(unittest.TestCase):
    def test_series_has_nine_sectors_and_one_synthesis(self) -> None:
        self.assertEqual(len(SERIES), 10)
        self.assertEqual(sum(item.role == "行业研究" for item in SERIES), 9)
        self.assertEqual(sum(item.role == "综合报告" for item in SERIES), 1)

    def test_all_records_are_china_innovation_reports_from_2024(self) -> None:
        self.assertTrue(all(item.published.startswith("2024-") for item in SERIES))
        self.assertTrue(all("china" in item.title.lower() for item in SERIES))
        self.assertTrue(all(item.url.startswith("https://itif.org/publications/2024/") for item in SERIES))

    def test_talent_dimension_is_only_applied_when_official_scope_is_explicit(self) -> None:
        talent_items = [item for item in SERIES if item.includes_talent]
        self.assertEqual([item.domain for item in talent_items], ["人工智能"])

    def test_stable_id_uses_official_slug(self) -> None:
        self.assertEqual(
            stable_report_id(SERIES[0].url),
            "C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-THE-ROBOTICS-INDUSTRY",
        )


if __name__ == "__main__":
    unittest.main()
