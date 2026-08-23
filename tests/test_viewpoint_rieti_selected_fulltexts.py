import unittest

from scripts.extend_viewpoint_rieti_selected_fulltexts import (
    SELECTED_ITEMS,
    sanitize_extracted_text,
    sanitize_html_snapshot,
    selected_slice,
)


class RietiSelectedFulltextsTests(unittest.TestCase):
    def test_selection_keeps_one_primary_node_per_year_and_bounded_china_mechanism_supplements(self):
        years = [int(str(item["date"])[:4]) for item in SELECTED_ITEMS]
        self.assertEqual(set(years), set(range(2016, 2027)))
        self.assertEqual(len(SELECTED_ITEMS), 19)
        self.assertEqual(len(years) - len(set(years)), 8)

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
        self.assertEqual(
            {item["id"] for item in china_items},
            {
                "C-JP-RIETI-17-E-111", "C-JP-RIETI-17-E-126", "C-JP-RIETI-18-P-012",
                "C-JP-RIETI-20-E-045", "C-JP-RIETI-21-J-052", "C-JP-RIETI-23-J-015",
                "C-JP-RIETI-23-J-020", "C-JP-RIETI-24-E-075", "C-JP-RIETI-25-J-005",
            },
        )
        joined = " ".join(str(item["title"]) for item in china_items).lower()
        self.assertIn("china", joined)
        for signal in ("productivity", "innovation", "robot", "artificial intelligence"):
            self.assertIn(signal, joined)

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

    def test_extracted_text_removes_line_end_whitespace(self):
        self.assertEqual(sanitize_extracted_text("alpha  \nbeta\t\n"), "alpha\nbeta\n")

    def test_html_snapshot_removes_line_end_whitespace(self):
        self.assertEqual(
            sanitize_html_snapshot("<p>alpha</p>  \n    \t<dl>\n"),
            "<p>alpha</p>\n\t<dl>\n",
        )


if __name__ == "__main__":
    unittest.main()
