from __future__ import annotations

import unittest

from scripts.extend_viewpoint_stanford_hai_light_catalog import ANNUAL_PDF_URLS, ITEMS, observation_window, stable_report_id


class StanfordHaiLightCatalogTests(unittest.TestCase):
    def test_ai_index_is_a_continuous_official_series(self) -> None:
        annual = [item for item in ITEMS if "AI Index Report" in item.title]
        self.assertEqual([int(item.published[:4]) for item in annual], [2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025, 2026])
        self.assertTrue(all(item.url.startswith("https://hai.stanford.edu/ai-index/") for item in annual))

    def test_items_are_science_innovation_led(self) -> None:
        self.assertEqual(len(ITEMS), 17)
        self.assertTrue(all("安全供应链与治理边界" not in item.themes for item in ITEMS))
        self.assertTrue(all(any(theme in item.themes for theme in ("科学体系与基础研究", "技术创新与关键技术", "创新政策与研发治理")) for item in ITEMS))

    def test_series_spans_all_observation_windows(self) -> None:
        self.assertEqual({observation_window(item.published) for item in ITEMS}, {"W1", "W2", "W3"})
        self.assertEqual(stable_report_id(ITEMS[0]), "C-STANFORD-HAI-AI-INDEX-2017")

    def test_targeted_gap_years_have_official_pdf_urls(self) -> None:
        self.assertEqual(set(ANNUAL_PDF_URLS), {2018, 2022, 2023, 2025})
        self.assertTrue(all(url.startswith("https://hai.stanford.edu/") and url.endswith(".pdf") for url in ANNUAL_PDF_URLS.values()))


if __name__ == "__main__":
    unittest.main()
