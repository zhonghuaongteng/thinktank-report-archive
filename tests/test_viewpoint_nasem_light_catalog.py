import unittest

from scripts.extend_viewpoint_nasem_light_catalog import (
    classify_relevance,
    merge_catalog_rows,
    normalize_works,
)


class NasemLightCatalogTests(unittest.TestCase):
    def test_science_policy_work_is_normalized_from_crossref(self):
        works = [{
            "DOI": "10.17226/25116",
            "title": ["Open Science by Design"],
            "published": {"date-parts": [[2018, 7, 17]]},
            "type": "edited-book",
            "author": [{"name": "National Academies of Sciences, Engineering, and Medicine"}],
            "URL": "https://doi.org/10.17226/25116",
        }]
        rows = normalize_works(works, "2026-08-23")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["报告ID"], "C-US-NASEM-25116")
        self.assertEqual(rows[0]["发布日期"], "2018-07-17")
        self.assertEqual(rows[0]["科技创新相关度"], "核心")
        self.assertIn("科学体系与基础研究", rows[0]["科技创新主轴"])

    def test_transport_only_record_is_excluded_and_security_context_is_not_promoted(self):
        self.assertIsNone(classify_relevance("Highway Pavement Research Report"))
        relevance, axes = classify_relevance("Protecting U.S. Technological Advantage")
        self.assertEqual(relevance, "语境")
        self.assertIn("技术创新与关键技术", axes)
        self.assertEqual(classify_relevance("Returns to Federal Investments in the Innovation System")[0], "核心")

    def test_manually_verified_china_reports_are_flagged(self):
        works = [{
            "DOI": "10.17226/26647",
            "title": ["Protecting U.S. Technological Advantage"],
            "published": {"date-parts": [[2022, 12, 19]]},
            "type": "edited-book",
            "author": [],
            "URL": "https://doi.org/10.17226/26647",
        }]
        rows = normalize_works(works, "2026-08-23")
        self.assertEqual(rows[0]["中国直接信号"], "是（正文人工核验）")

    def test_international_scientific_talent_programs_are_in_scope(self):
        relevance, axes = classify_relevance("International Talent Programs in the Changing Global Environment")
        self.assertEqual(relevance, "核心")
        self.assertIn("人才大学与科研组织", axes)
        self.assertIn("国际合作开放科学与比较", axes)

    def test_catalog_merge_preserves_other_institutions_and_schema(self):
        fields = ["报告ID", "机构ID", "报告名称", "自定义字段"]
        existing = [{"报告ID": "OLD", "机构ID": "other", "报告名称": "旧记录", "自定义字段": "保留"}]
        light = [{
            "报告ID": "C-US-NASEM-25116", "发布日期": "2018-07-17", "报告名称": "Open Science by Design",
            "官方文类": "edited-book", "官方落地页": "https://www.nationalacademies.org/publications/25116",
            "科技创新相关度": "核心", "科技创新主轴": "科学体系与基础研究", "中国直接信号": "否",
        }]
        merged = merge_catalog_rows(existing, light, fields)
        by_id = {row["报告ID"]: row for row in merged}
        self.assertEqual(by_id["OLD"]["自定义字段"], "保留")
        self.assertEqual(list(by_id["C-US-NASEM-25116"]), fields)


if __name__ == "__main__":
    unittest.main()
