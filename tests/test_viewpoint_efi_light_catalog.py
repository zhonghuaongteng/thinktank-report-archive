import unittest

from scripts.extend_viewpoint_efi_light_catalog import (
    classify_relevance,
    merge_catalog_rows,
    normalize_chapters,
    normalize_space,
)


class EfiLightCatalogTests(unittest.TestCase):
    def test_duplicate_thematic_entries_are_merged_with_all_topics(self):
        raw = [
            {"segment": "B3", "title": "Exchange of knowledge and technology between Germany and China",
             "year": "2020", "url": "https://www.e-fi.de/fileadmin/Assets/example.pdf", "topic": "China"},
            {"segment": "B3", "title": "Exchange of knowledge and technology between Germany and China",
             "year": "2020", "url": "https://www.e-fi.de/fileadmin/Assets/example.pdf", "topic": "Knowledge and Technology Transfer"},
        ]
        rows = normalize_chapters(raw, "2026-08-23")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["专题分类"], "China；Knowledge and Technology Transfer")
        self.assertEqual(rows[0]["中国直接信号"], "是")

    def test_strict_window_excludes_older_chapters(self):
        raw = [
            {"segment": "B1", "title": "Old innovation report", "year": "2015",
             "url": "https://www.e-fi.de/fileadmin/Assets/old.pdf", "topic": "Innovation"},
            {"segment": "B1", "title": "Current innovation report", "year": "2016",
             "url": "https://www.e-fi.de/fileadmin/Assets/current.pdf", "topic": "Innovation"},
        ]
        rows = normalize_chapters(raw, "2026-08-23")
        self.assertEqual([row["发布日期"] for row in rows], ["2016-01-01"])

    def test_security_led_item_is_context_only(self):
        relevance, axes = classify_relevance("Security-related Research and Innovation", "Coordination of Policies")
        self.assertEqual(relevance, "语境")
        self.assertIn("研发投入与创新政策", axes)

    def test_science_and_technology_items_are_core(self):
        relevance, axes = classify_relevance(
            "Basic research funding structures and publications in international comparison", "Research and Innovation System"
        )
        self.assertEqual(relevance, "核心")
        self.assertIn("科学体系与科研能力", axes)

    def test_mojibake_from_official_page_is_repaired(self):
        self.assertEqual(normalize_space("Artificial intelligence �C Germany��s AI Strategy"),
                         "Artificial intelligence – Germany’s AI Strategy")

    def test_catalog_merge_preserves_dynamic_master_schema(self):
        fields = ["报告ID", "机构ID", "报告名称", "自定义字段"]
        existing = [{"报告ID": "OLD", "机构ID": "other", "报告名称": "旧记录", "自定义字段": "保留"}]
        light = [{"报告ID": "C-DE-EFI-2020-B3", "报告名称": "China innovation", "发布日期": "2020-01-01",
                  "官方PDF入口": "https://www.e-fi.de/fileadmin/Assets/example.pdf", "科技创新相关度": "核心",
                  "科技创新主轴": "国际合作与中国比较", "官方文类": "年度报告分章"}]
        merged = merge_catalog_rows(existing, light, fields)
        by_id = {row["报告ID"]: row for row in merged}
        self.assertEqual(by_id["OLD"]["自定义字段"], "保留")
        self.assertEqual(list(by_id["C-DE-EFI-2020-B3"]), fields)


if __name__ == "__main__":
    unittest.main()
