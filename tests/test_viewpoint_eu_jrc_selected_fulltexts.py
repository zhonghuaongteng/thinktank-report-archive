import tempfile
import unittest
from pathlib import Path

from scripts.extend_viewpoint_eu_jrc_selected_fulltexts import (
    SELECTED_ITEMS,
    reusable_existing_row,
    sanitize_extracted_text,
    selected_slice,
)


class EuJrcSelectedFulltextsTests(unittest.TestCase):
    def test_selection_is_small_and_covers_every_year(self):
        self.assertEqual(len(SELECTED_ITEMS), 34)
        self.assertEqual({item["date"][:4] for item in SELECTED_ITEMS}, {str(year) for year in range(2016, 2027)})

    def test_science_innovation_china_followup_batch_is_exactly_six(self):
        expected = {
            "C-EU-JRC-JRC111622",
            "C-EU-JRC-JRC115449",
            "C-EU-JRC-JRC128744",
            "C-EU-JRC-JRC137550",
            "C-EU-JRC-JRC140126",
            "C-EU-JRC-JRC142609",
        }
        previous = {
            "C-EU-JRC-JRC100825", "C-EU-JRC-JRC101970", "C-EU-JRC-JRC102148", "C-EU-JRC-JRC103716",
            "C-EU-JRC-JRC107386", "C-EU-JRC-JRC108520", "C-EU-JRC-JRC113807", "C-EU-JRC-JRC113826",
            "C-EU-JRC-JRC116516", "C-EU-JRC-JRC118614", "C-EU-JRC-JRC119974", "C-EU-JRC-JRC121184",
            "C-EU-JRC-JRC121318", "C-EU-JRC-JRC124072", "C-EU-JRC-JRC125613", "C-EU-JRC-JRC129967",
            "C-EU-JRC-JRC131882", "C-EU-JRC-JRC134319", "C-EU-JRC-JRC133613", "C-EU-JRC-JRC134544",
            "C-EU-JRC-JRC137266", "C-EU-JRC-JRC137811", "C-EU-JRC-JRC138601", "C-EU-JRC-JRC142093",
            "C-EU-JRC-JRC142637", "C-EU-JRC-JRC144638", "C-EU-JRC-JRC145507", "C-EU-JRC-JRC147828",
        }
        self.assertEqual({item["id"] for item in SELECTED_ITEMS} - previous, expected)

    def test_bounded_china_innovation_increment_is_present(self):
        expected_increment = {
            "C-EU-JRC-JRC101970",
            "C-EU-JRC-JRC102148",
            "C-EU-JRC-JRC121184",
            "C-EU-JRC-JRC133613",
            "C-EU-JRC-JRC137266",
            "C-EU-JRC-JRC142637",
        }
        self.assertTrue(expected_increment.issubset({item["id"] for item in SELECTED_ITEMS}))

    def test_existing_complete_assets_are_reused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = [Path(temp_dir) / name for name in ("source.pdf", "page.html", "text.txt", "slice.md")]
            for path in paths:
                path.write_text("existing", encoding="utf-8")
            self.assertTrue(reusable_existing_row({"报告ID": "existing"}, paths))
            paths[-1].unlink()
            self.assertFalse(reusable_existing_row({"报告ID": "existing"}, paths))
            self.assertFalse(reusable_existing_row(None, paths))

    def test_selection_covers_science_technology_and_innovation_mechanisms(self):
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertIn("科学体系与科研能力", axes)
        self.assertIn("研发投入与创新政策", axes)
        self.assertIn("关键与新兴技术", axes)
        self.assertIn("产业创新与成果转化", axes)
        self.assertIn("创新测量与政策方法", axes)
        self.assertIn("国际合作与中国比较", axes)

    def test_security_led_titles_are_not_selected(self):
        titles = "\n".join(item["title"].lower() for item in SELECTED_ITEMS)
        self.assertNotIn("cyber threats", titles)
        self.assertNotIn("law enforcement", titles)
        self.assertNotIn("export controls", titles)

    def test_slice_records_the_science_technology_scope(self):
        item = SELECTED_ITEMS[0]
        text = "Research and development investment supports innovation and technology transfer.\n\nUnrelated appendix."
        result = selected_slice(item, text)
        self.assertIn("科学技术创新定向摘录", result)
        self.assertIn("Research and development investment", result)

    def test_credential_shaped_examples_are_redacted_from_extracted_text(self):
        access_key = "AKIA" + "ABCD" * 4
        secret_key = "abcd" * 10
        sample = f"example {access_key}\n{secret_key}"
        cleaned = sanitize_extracted_text(sample)
        self.assertNotIn(access_key, cleaned)
        self.assertNotIn(secret_key, cleaned)
        self.assertIn("[REDACTED_CREDENTIAL_SHAPED_EXAMPLE]", cleaned)


if __name__ == "__main__":
    unittest.main()
