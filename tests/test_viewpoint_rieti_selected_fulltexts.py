import unittest

from scripts.extend_viewpoint_rieti_selected_fulltexts import SELECTED_ITEMS, selected_slice


class RietiSelectedFulltextsTests(unittest.TestCase):
    def test_selection_keeps_one_primary_node_per_year_and_only_two_china_supplements(self):
        years = [int(str(item["date"])[:4]) for item in SELECTED_ITEMS]
        self.assertEqual(set(years), set(range(2016, 2027)))
        self.assertEqual(len(SELECTED_ITEMS), 13)
        self.assertEqual(len(years) - len(set(years)), 2)

    def test_selection_centers_science_technology_and_innovation(self):
        titles = " ".join(str(item["title"]) for item in SELECTED_ITEMS).lower()
        for signal in ("research", "science", "technology", "innovation", "commercialization", "patent"):
            self.assertIn(signal, titles)
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertTrue({
            "科学体系与科研能力", "研发投入与创新政策", "关键与新兴技术",
            "产业创新与成果转化", "创新测量与政策方法", "国际合作与中国比较",
        }.issubset(axes))

    def test_security_led_titles_are_absent(self):
        titles = " ".join(str(item["title"]) for item in SELECTED_ITEMS).lower()
        for signal in ("security exception", "export restriction", "export control", "decoupling", "trade war"):
            self.assertNotIn(signal, titles)

    def test_china_supplements_are_innovation_system_or_technology_comparisons(self):
        china_items = [item for item in SELECTED_ITEMS if item.get("china_supplement")]
        self.assertEqual(len(china_items), 2)
        joined = " ".join(str(item["title"]) for item in china_items).lower()
        self.assertIn("china", joined)
        self.assertTrue("patent" in joined or "technological" in joined)

    def test_slice_is_labeled_as_science_technology_innovation_evidence(self):
        item = SELECTED_ITEMS[0]
        source = (
            "Public research institutes connect scientific capabilities with industrial innovation.\n\n"
            "This paragraph concerns unrelated administrative history and contains enough words to be retained otherwise."
        )
        output = selected_slice(item, source)
        self.assertIn("科学技术创新定向摘录", output)
        self.assertIn("Public research institutes", output)
        self.assertNotIn("unrelated administrative history", output)


if __name__ == "__main__":
    unittest.main()
