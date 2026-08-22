import unittest

from scripts.extend_viewpoint_rieti_light_catalog import (
    classify_relevance,
    is_catalog_candidate,
    merge_catalog_rows,
    parse_listing_html,
)


class RietiLightCatalogTests(unittest.TestCase):
    def test_parse_listing_preserves_official_code_authors_and_links(self):
        source = """
        <ul><li><p class="date">December 2017 17-E-126</p>
        <h3><a href="/en/publications/summary/17120010.html">Innovation Responses of Japanese Firms to Chinese Import Competition</a></h3>
        <ul class="listItem"><li class="name">YAMASHITA Nobuaki / YAMAUCHI Isamu</li>
        <li class="dl"><a href="/jp/publications/dp/17e126.pdf">Download paper</a></li></ul></li></ul>
        """
        rows = parse_listing_html(source, "English Discussion Paper", "https://www.rieti.go.jp/en/publications/act_dp2017.html")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].code, "17-E-126")
        self.assertEqual(rows[0].published, "2017-12-01")
        self.assertEqual(rows[0].authors, "YAMASHITA Nobuaki / YAMAUCHI Isamu")
        self.assertEqual(rows[0].landing_url, "https://www.rieti.go.jp/en/publications/summary/17120010.html")
        self.assertEqual(rows[0].pdf_url, "https://www.rieti.go.jp/jp/publications/dp/17e126.pdf")

    def test_science_technology_and_innovation_titles_are_candidates(self):
        for title in (
            "R&D Spillovers through Buyer-supplier Networks",
            "Quantifying Innovation Processes in China, Japan and the United States",
            "Design Right Commercialization by Public Technology Transfer Organizations",
        ):
            self.assertTrue(is_catalog_candidate(title), title)

    def test_generic_diplomacy_title_is_excluded(self):
        self.assertFalse(is_catalog_candidate("Unpacking China’s Wolf Warrior Diplomacy"))

    def test_security_led_title_is_context_only(self):
        relevance, _ = classify_relevance("U.S. Semiconductor Export Restrictions on China and the WTO Security Exception")
        self.assertEqual(relevance, "语境")

    def test_china_economic_title_requires_science_technology_or_innovation_signal(self):
        self.assertFalse(is_catalog_candidate("Productivity of Firms Engaged in Service Trade with China"))
        self.assertTrue(is_catalog_candidate("Innovation and Productivity of Firms Engaged in Trade with China"))

    def test_general_security_and_economy_titles_are_excluded_without_sti_signal(self):
        self.assertFalse(is_catalog_candidate("Supply Chain Resilience and Economic Security"))
        self.assertFalse(is_catalog_candidate("China and Global Trade Patterns"))
        self.assertFalse(is_catalog_candidate("Green Growth and Energy Prices"))
        self.assertFalse(is_catalog_candidate("Tourism Productivity: Evidence from Micro Data"))
        self.assertFalse(is_catalog_candidate("Research on Fiscal System Reform in China"))

    def test_research_system_and_digital_technology_mechanisms_are_retained(self):
        self.assertTrue(is_catalog_candidate("National Research Grants and Academic Productivity"))
        self.assertTrue(is_catalog_candidate("Digital Platforms and Industrial Competitiveness"))
        self.assertTrue(is_catalog_candidate("Cross-border Data Flows and Firm Innovation"))

    def test_catalog_merge_preserves_dynamic_schema(self):
        fields = ["报告ID", "机构ID", "报告名称", "自定义字段"]
        existing = [{"报告ID": "OLD", "机构ID": "other", "报告名称": "旧记录", "自定义字段": "保留"}]
        light = [{"报告ID": "C-JP-RIETI-17-E-126", "报告名称": "Innovation", "发布日期": "2017-12-01",
                  "官方文类": "English Discussion Paper", "作者": "A", "官方落地页": "https://example.test",
                  "官方PDF入口": "https://example.test/a.pdf", "科技创新相关度": "核心",
                  "科技创新主轴": "产业创新与成果转化"}]
        merged = merge_catalog_rows(existing, light, fields)
        by_id = {row["报告ID"]: row for row in merged}
        self.assertEqual(by_id["OLD"]["自定义字段"], "保留")
        self.assertEqual(list(by_id["C-JP-RIETI-17-E-126"]), fields)


if __name__ == "__main__":
    unittest.main()
