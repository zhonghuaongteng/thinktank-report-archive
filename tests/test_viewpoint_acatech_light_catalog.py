import unittest

from scripts.extend_viewpoint_acatech_light_catalog import (
    classify_relevance,
    merge_catalog_rows,
    normalize_publications,
)


class AcatechLightCatalogTests(unittest.TestCase):
    def test_official_archive_rows_are_kept_and_normalized(self):
        items = [
            {
                "id": 2786,
                "date": "2016-11-23T10:00:00",
                "slug": "industrie-4-0-im-globalen-kontext",
                "link": "https://www.acatech.de/publikation/industrie-4-0-im-globalen-kontext/",
                "title": {"rendered": "Industrie 4.0 im globalen Kontext &#8211; Strategien"},
                "excerpt": {"rendered": "<p>Internationale Strategien im Vergleich.</p>"},
                "format": [86],
                "topic": [10],
            },
            {
                "id": 1,
                "date": "2015-12-31T10:00:00",
                "slug": "too-old",
                "link": "https://www.acatech.de/publikation/too-old/",
                "title": {"rendered": "Too old"},
                "excerpt": {"rendered": ""},
                "format": [86],
                "topic": [],
            },
        ]
        rows = normalize_publications(items, {86: "acatech STUDIE"}, {10: "Digitale Transformation"}, "2026-08-23")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["发布日期"], "2016-11-23")
        self.assertIn("–", rows[0]["报告名称"])
        self.assertEqual(rows[0]["中国直接信号"], "是")

    def test_security_words_cannot_promote_a_record_to_core(self):
        self.assertEqual(classify_relevance("Research security for the national innovation system")[0], "语境")
        self.assertEqual(classify_relevance("Innovationssystem Deutschland. Zivile und militärische Innovationen verzahnen")[0], "语境")
        self.assertEqual(classify_relevance("Engineering in Deutschland – Status quo in Wirtschaft und Wissenschaft")[0], "核心")

    def test_catalog_merge_preserves_other_institutions_and_schema(self):
        fields = ["报告ID", "机构ID", "报告名称", "自定义字段"]
        existing = [{"报告ID": "OLD", "机构ID": "other", "报告名称": "旧记录", "自定义字段": "保留"}]
        light = [{
            "报告ID": "C-DE-ACATECH-2786", "发布日期": "2016-11-23", "报告名称": "Industrie 4.0",
            "官方文类": "acatech STUDIE", "官方落地页": "https://example.test", "科技创新相关度": "核心",
            "科技创新主轴": "技术创新与关键技术", "中国直接信号": "否",
        }]
        merged = merge_catalog_rows(existing, light, fields)
        by_id = {row["报告ID"]: row for row in merged}
        self.assertEqual(by_id["OLD"]["自定义字段"], "保留")
        self.assertEqual(list(by_id["C-DE-ACATECH-2786"]), fields)


if __name__ == "__main__":
    unittest.main()
