import unittest

from scripts.extend_viewpoint_rathenau_selected_fulltexts import SELECTED_ITEMS, mark_selected_light_rows
from scripts.extend_viewpoint_rathenau_light_catalog import RathenauItem, report_id
from scripts.validate_viewpoint_research import expected_rathenau_selected_ids


class RathenauSelectedFulltextsTests(unittest.TestCase):
    def test_selected_set_is_cross_period_and_small(self):
        self.assertEqual(len(SELECTED_ITEMS), 13)
        years = {item["date"][:4] for item in SELECTED_ITEMS}
        self.assertTrue({"2015", "2016", "2018", "2020", "2021", "2022", "2024", "2025", "2026"}.issubset(years))

    def test_validator_tracks_the_selected_set(self):
        self.assertEqual(expected_rathenau_selected_ids(), {item["id"] for item in SELECTED_ITEMS})

    def test_selection_covers_science_policy_innovation_and_translation(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertTrue(
            {"科学体系与基础研究", "技术创新与产业转化", "研发治理与科研组织", "开放科学与国际合作"}.issubset(axes)
        )

    def test_china_materials_are_selected_for_science_and_innovation_mechanisms(self):
        china_items = [item for item in SELECTED_ITEMS if item["china"]]
        self.assertGreaterEqual(len(china_items), 4)
        self.assertTrue(any("CHINA-SCIENTIFIC-SUPERPOWER" in item["id"] for item in china_items))
        self.assertTrue(any("RD-GOES-GLOBAL" in item["id"] for item in china_items))

    def test_security_context_does_not_create_a_selected_item(self):
        titles = " ".join(item["title"].lower() for item in SELECTED_ITEMS)
        self.assertNotIn("cyberspace without conflict", titles)
        self.assertNotIn("digital threats to democracy", titles)

    def test_each_pdf_item_has_an_official_rathenau_asset(self):
        pdf_items = [item for item in SELECTED_ITEMS if item["asset_type"] == "PDF"]
        self.assertEqual(len(pdf_items), 12)
        self.assertTrue(
            all(item["asset_url"].startswith("https://www.rathenau.nl/sites/default/files/") for item in pdf_items)
        )

    def test_china_factsheet_is_preserved_as_official_web_fulltext(self):
        web_items = [item for item in SELECTED_ITEMS if item["asset_type"] == "WEB"]
        self.assertEqual(len(web_items), 1)
        self.assertEqual(web_items[0]["id"], "C-RATHENAU-2025-CHINA-SCIENTIFIC-SUPERPOWER")

    def test_selected_ids_match_the_light_catalog_id_rule(self):
        for item in SELECTED_ITEMS:
            light_item = RathenauItem(
                date=item["date"], theme="", title=item["title"], content_type=item["asset_type"],
                url=item["landing"],
            )
            self.assertEqual(item["id"], report_id(light_item))

    def test_selected_fulltexts_upgrade_light_catalog_china_and_strategy_fields(self):
        rows = [
            {"报告ID": item["id"], "中国关联": "否", "全文策略": "总目录保留"}
            for item in SELECTED_ITEMS
        ]
        mark_selected_light_rows(rows)
        self.assertEqual(sum(row["中国关联"] == "是" for row in rows), 5)
        self.assertTrue(all(row["全文策略"].startswith("已进入精选全文") for row in rows))


if __name__ == "__main__":
    unittest.main()
