import unittest

from scripts.extend_viewpoint_eu_jrc_light_catalog import (
    classify_relevance,
    is_catalog_candidate,
    merge_catalog_rows,
    normalize_item,
)


class EuJrcLightCatalogTests(unittest.TestCase):
    def test_innovation_growth_report_is_a_core_candidate(self):
        item = {
            "dc.title": "The EU Industrial R&D Investment Scoreboard",
            "dc.description.abstract": "Compares corporate research and development, innovation and technology investment.",
            "extra.collection.science_area": ["Innovation and growth"],
        }
        self.assertTrue(is_catalog_candidate(item))
        self.assertEqual(classify_relevance(item)[0], "核心")

    def test_generic_environment_report_without_sti_mechanism_is_excluded(self):
        item = {
            "dc.title": "Monitoring river water quality",
            "dc.description.abstract": "Measurements of nutrients in European rivers.",
            "extra.collection.science_area": ["Environment and climate change"],
        }
        self.assertFalse(is_catalog_candidate(item))

    def test_security_led_digital_report_remains_context_only(self):
        item = {
            "dc.title": "Cyber threats and law enforcement operations",
            "dc.description.abstract": "A security assessment for public authorities.",
            "extra.collection.science_area": ["Information society", "Safety and security"],
        }
        self.assertTrue(is_catalog_candidate(item))
        self.assertEqual(classify_relevance(item)[0], "语境")

    def test_official_item_normalization_preserves_provenance_and_china_signal(self):
        item = {
            "id": "JRC124597",
            "collection.year": 2021,
            "dc.date.issued": "2021",
            "dc.title": "China overtakes the EU in high-impact publications",
            "dc.description.abstract": "Compares Chinese and European scientific excellence and R&D investment.",
            "dc.contributor.author": ["AUTHOR One", "AUTHOR Two"],
            "extra.collection.group": "Science for policy",
            "extra.collection.science_area": ["Innovation and growth"],
            "resource_type.description": "Report",
            "dc.identifier.doi": "10.2760/example (online)",
            "document.42.main": "Y",
            "document.42.filename": "JRC124597_01.pdf",
            "document.42.mimetype": "application/pdf",
        }
        row = normalize_item(item, "2026-08-23")
        self.assertEqual(row["报告ID"], "C-EU-JRC-JRC124597")
        self.assertEqual(row["发布日期"], "2021-01-01")
        self.assertEqual(row["日期精度"], "年")
        self.assertEqual(row["中国直接信号"], "是")
        self.assertEqual(row["官方落地页"], "https://publications.jrc.ec.europa.eu/repository/handle/JRC124597")
        self.assertEqual(row["官方PDF入口"], "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC124597/JRC124597_01.pdf")

    def test_catalog_merge_preserves_the_existing_schema(self):
        fields = ["报告ID", "机构ID", "报告名称", "自定义字段"]
        existing = [{"报告ID": "OLD-1", "机构ID": "other", "报告名称": "旧记录", "自定义字段": "保留"}]
        light = [{"报告ID": "NEW-1", "机构名称": "JRC", "报告名称": "新记录", "发布日期": "2025-01-01",
                  "官方文类": "Report", "作者": "A", "官方落地页": "https://example.test", "科技创新相关度": "核心",
                  "科技创新主轴": "研发投入与创新政策"}]
        merged = merge_catalog_rows(existing, light, fields)
        by_id = {row["报告ID"]: row for row in merged}
        self.assertEqual(list(by_id["OLD-1"]), fields)
        self.assertEqual(by_id["OLD-1"]["自定义字段"], "保留")
        self.assertEqual(by_id["NEW-1"]["报告ID"], "NEW-1")
        self.assertEqual(list(by_id["NEW-1"]), fields)

    def test_preencoded_pdf_filename_is_not_double_encoded(self):
        item = {
            "id": "JRC100825", "collection.year": 2016, "dc.title": "Innovation report",
            "document.7.main": "Y", "document.7.filename": "innovation%20output.pdf",
            "document.7.mimetype": "application/pdf",
        }
        row = normalize_item(item, "2026-08-23")
        self.assertTrue(row["官方PDF入口"].endswith("/innovation%20output.pdf"))
        self.assertNotIn("%2520", row["官方PDF入口"])


if __name__ == "__main__":
    unittest.main()
