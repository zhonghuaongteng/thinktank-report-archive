import unittest

from scripts.extend_viewpoint_efi_selected_fulltexts import SELECTED_ITEMS, selected_slice


class EfiSelectedFulltextsTests(unittest.TestCase):
    def test_selection_is_one_mechanism_node_per_year(self):
        self.assertEqual(len(SELECTED_ITEMS), 11)
        self.assertEqual({item["date"][:4] for item in SELECTED_ITEMS}, {str(year) for year in range(2016, 2027)})

    def test_selection_covers_science_technology_and_china(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertIn("科学体系与科研能力", axes)
        self.assertIn("关键与新兴技术", axes)
        self.assertIn("研发投入与创新政策", axes)
        self.assertIn("产业创新与成果转化", axes)
        self.assertIn("国际合作与中国比较", axes)
        self.assertTrue(any("China" in item["title"] for item in SELECTED_ITEMS))

    def test_security_chapter_is_not_selected(self):
        titles = "\n".join(item["title"].lower() for item in SELECTED_ITEMS)
        self.assertNotIn("security-related research", titles)
        self.assertNotIn("cybersecurity", titles)

    def test_slice_keeps_innovation_mechanism_paragraphs(self):
        item = SELECTED_ITEMS[0]
        text = "Research and innovation in SMEs depends on technology transfer and R&D investment.\n\nUnrelated appendix."
        result = selected_slice(item, text)
        self.assertIn("科学技术创新定向摘录", result)
        self.assertIn("technology transfer", result)


if __name__ == "__main__":
    unittest.main()
