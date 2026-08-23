import unittest

from scripts.backfill_viewpoint_cross_institution_china_innovation import (
    SELECTED_ITEMS,
    sanitize_html,
    selected_slice,
)


class CrossInstitutionChinaInnovationTests(unittest.TestCase):
    def test_batch_is_bounded_and_cross_institution(self):
        self.assertEqual(len(SELECTED_ITEMS), 5)
        self.assertEqual(len({item["institution_id"] for item in SELECTED_ITEMS}), 4)

    def test_exact_high_reuse_candidates_are_selected(self):
        self.assertEqual(
            {item["id"] for item in SELECTED_ITEMS},
            {
                "C-LIGHT-MERICS-2018-CHINAS-WAY-INNOVATION-SUPERPOWER",
                "C-EU-JRC-JRC110333",
                "C-OECD-DOI-BB222C73-EN",
                "C-EU-JRC-JRC122755",
                "C-JP-RIETI-24-E-042",
            },
        )

    def test_batch_centers_innovation_mechanisms(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertTrue(
            {
                "科学体系与科研能力",
                "研发投入与创新政策",
                "关键与新兴技术",
                "产业创新与成果转化",
                "国际合作与中国比较",
            }.issubset(axes)
        )

    def test_security_led_materials_are_absent(self):
        titles = " ".join(item["title"] for item in SELECTED_ITEMS).lower()
        for signal in (
            "military",
            "export control",
            "export restriction",
            "espionage",
            "national security",
            "trade war",
        ):
            self.assertNotIn(signal, titles)

    def test_slice_keeps_technology_and_china_evidence(self):
        item = SELECTED_ITEMS[0]
        source = (
            "China expanded public research support and trained scientific talent to accelerate innovation.\n\n"
            "This unrelated administrative sentence is long enough to pass a simple length threshold."
        )
        output = selected_slice(item, source)
        self.assertIn("科学技术创新定向摘录", output)
        self.assertIn("public research support", output)
        self.assertNotIn("unrelated administrative", output)

    def test_html_snapshot_removes_line_end_whitespace(self):
        self.assertEqual(sanitize_html("<main>  \n  <p>text</p>\t\n"), "<main>\n  <p>text</p>\n")


if __name__ == "__main__":
    unittest.main()
