import unittest

from scripts.extend_viewpoint_royal_society_light_catalog import (
    classify_relevance,
    merge_catalog_rows,
    parse_timeline_markdown,
)


class RoyalSocietyLightCatalogTests(unittest.TestCase):
    def test_timeline_keeps_formal_science_innovation_outputs(self):
        source = """
15 May 2025 Report[Science 2040 Interim Report](https://royalsociety.org/-/media/policy/projects/science-2040/report.pdf)
31 July 2024 Policy briefing[UK science: building a more resilient and prosperous future](http://royalsociety.org/news-resources/publications/2024/uk-science/)
31 July 2024 Factsheets[UK research and Innovation, by region](http://royalsociety.org/news-resources/publications/2024/regions/)
30 October 2024 Statement[Royal Society President responds to the Budget](https://royalsociety.org/news/2024/10/budget/)
"""
        rows = parse_timeline_markdown(source, "https://royalsociety.org/example")
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0].published, "2025-05-15")
        self.assertEqual(rows[0].kind, "Report")
        self.assertTrue(rows[0].url.startswith("https://royalsociety.org/"))

    def test_security_is_context_but_science_and_technology_are_core(self):
        self.assertEqual(classify_relevance("Research security and trusted collaboration")[0], "语境")
        self.assertEqual(classify_relevance("Science in the age of AI")[0], "核心")
        self.assertEqual(classify_relevance("Transforming UK Translation - six years in")[0], "核心")

    def test_catalog_merge_preserves_dynamic_schema(self):
        fields = ["报告ID", "机构ID", "报告名称", "自定义字段"]
        existing = [{"报告ID": "OLD", "机构ID": "other", "报告名称": "旧记录", "自定义字段": "保留"}]
        light = [{"报告ID": "C-UK-RS-2024-SCIENCE-ECONOMY", "报告名称": "Science and the economy",
                  "发布日期": "2024-07-03", "官方文类": "Policy briefing", "官方落地页": "https://example.test",
                  "科技创新相关度": "核心", "科技创新主轴": "科学体系与基础研究"}]
        merged = merge_catalog_rows(existing, light, fields)
        by_id = {row["报告ID"]: row for row in merged}
        self.assertEqual(by_id["OLD"]["自定义字段"], "保留")
        self.assertEqual(list(by_id["C-UK-RS-2024-SCIENCE-ECONOMY"]), fields)


if __name__ == "__main__":
    unittest.main()
