from __future__ import annotations

import unittest

from scripts.extend_viewpoint_fraunhofer_isi_light_catalog import canonical_title, parse_official_page, theme_labels


class FraunhoferIsiLightCatalogTests(unittest.TestCase):
    def test_parse_official_series_entry(self) -> None:
        source = """
        <p><b>No. 63</b><br>Rainer Frietsch<br>
        <a href="/content/dam/isi/dokumente/cci/innovation-systems-policy-analysis/2020/discussionpaper_63_2020.pdf">
        Current R&amp;I policy: The future development of China´s R&amp;I system</a><br>Karlsruhe 2020</p>
        """
        rows = parse_official_page(source)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].number, 63)
        self.assertEqual(rows[0].authors, "Rainer Frietsch")
        self.assertIn("中国科技横向维度", rows[0].themes)
        self.assertTrue(rows[0].pdf_url.startswith("https://www.isi.fraunhofer.de/"))

    def test_series_scope_supplies_innovation_policy_fallback(self) -> None:
        self.assertEqual(theme_labels("A neutral systems paper"), ("创新政策与研发治理",))

    def test_security_is_context_beside_innovation_policy(self) -> None:
        themes = theme_labels("From sustainability transitions to security: Mapping innovation policy")
        self.assertIn("创新政策与研发治理", themes)
        self.assertIn("安全供应链与治理边界", themes)

    def test_title_canonicalization(self) -> None:
        self.assertEqual(canonical_title("R&D and Innovation—Policy"), "rdandinnovationpolicy")


if __name__ == "__main__":
    unittest.main()
