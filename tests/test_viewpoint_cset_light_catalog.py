from __future__ import annotations

import unittest

from scripts.extend_viewpoint_cset_light_catalog import (
    classify_science_innovation_themes,
    extract_pdf_entries,
    normalize_title,
    parse_items,
)


class CsetLightCatalogTests(unittest.TestCase):
    def test_parse_items_keeps_formal_reports_without_keyword_filter(self) -> None:
        data = [{
            "id": 321,
            "date": "2023-03-04T12:00:00",
            "link": "https://cset.georgetown.edu/publication/example/",
            "title": {"rendered": "A neutral formal report"},
            "excerpt": {"rendered": "<p>Official abstract.</p>"},
            "content": {"rendered": ""},
            "content_type": [18],
        }]
        rows = parse_items(data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].report_id, "C-CSET-321")

    def test_parser_rejects_non_report_content_type(self) -> None:
        data = [{
            "id": 322, "date": "2023-03-04T12:00:00", "link": "https://example.test/",
            "title": {"rendered": "Article"}, "excerpt": {"rendered": ""},
            "content": {"rendered": ""}, "content_type": [22],
        }]
        self.assertEqual(parse_items(data), [])

    def test_themes_prioritize_science_and_innovation(self) -> None:
        themes = classify_science_innovation_themes(
            "China's AI Research Ecosystem",
            "Universities, researchers, R&D funding, and commercialisation",
        )
        self.assertIn("科学体系与基础研究", themes)
        self.assertIn("技术创新与关键技术", themes)
        self.assertIn("人才大学与科研组织", themes)
        self.assertIn("产业创新转化与区域生态", themes)
        self.assertIn("中国科技横向维度", themes)

    def test_security_is_secondary_label(self) -> None:
        themes = classify_science_innovation_themes(
            "Research security and export controls", "",
        )
        self.assertEqual(themes, ["安全供应链与治理边界（次级）"])

    def test_extracts_first_party_pdf_entries_without_download(self) -> None:
        html = (
            '<a href="https://cset.georgetown.edu/wp-content/uploads/report.pdf">PDF</a>'
            '<a href="https://other.test/file.pdf">Other</a>'
        )
        self.assertEqual(
            extract_pdf_entries(html),
            ["https://cset.georgetown.edu/wp-content/uploads/report.pdf"],
        )

    def test_normalizes_broken_dash_and_html(self) -> None:
        self.assertEqual(normalize_title("Science��and &amp; technology"), "Science—and & technology")


if __name__ == "__main__":
    unittest.main()
