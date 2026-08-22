from __future__ import annotations

import unittest

from scripts.extend_viewpoint_oecd_light_catalog import (
    classify_themes,
    canonical_title,
    parse_crossref_item,
    stable_report_id,
)


class OecdLightCatalogTests(unittest.TestCase):
    def test_stable_id_uses_doi(self) -> None:
        self.assertEqual(stable_report_id("10.1787/abc-en"), "C-OECD-DOI-ABC-EN")

    def test_parses_registered_oecd_series_metadata(self) -> None:
        item = {
            "DOI": "10.1787/abc-en",
            "title": ["Research and innovation policy"],
            "published": {"date-parts": [[2024, 6, 3]]},
            "author": [{"given": "A.", "family": "Scholar"}],
            "container-title": ["OECD Science, Technology and Industry Policy Papers"],
            "URL": "https://doi.org/10.1787/abc-en",
            "resource": {"primary": {"URL": "https://www.oecd-ilibrary.org/example"}},
            "publisher": "Organisation for Economic Co-Operation and Development (OECD)",
        }
        row = parse_crossref_item(item, "2307-4957")
        self.assertEqual(row.published, "2024-06-03")
        self.assertEqual(row.authors, "A. Scholar")
        self.assertEqual(row.official_url, "https://www.oecd-ilibrary.org/example")

    def test_science_and_innovation_themes_precede_security(self) -> None:
        themes = classify_themes("Research security for international science collaboration")
        self.assertIn("科学体系与基础研究", themes)
        self.assertIn("国际合作开放科学与比较", themes)
        self.assertEqual(themes[-1], "安全供应链与治理边界（次级）")

    def test_china_is_cross_cutting(self) -> None:
        self.assertIn("中国科技横向维度", classify_themes("Innovation policy in the People's Republic of China"))

    def test_canonical_title_normalizes_punctuation(self) -> None:
        self.assertEqual(canonical_title("AI-enabled R&D: Policy!"), "aienabledrdpolicy")


if __name__ == "__main__":
    unittest.main()
