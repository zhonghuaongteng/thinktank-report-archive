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
        self.assertEqual(len(SELECTED_ITEMS), 28)
        self.assertEqual({item["date"][:4] for item in SELECTED_ITEMS}, {str(year) for year in range(2016, 2027)})

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
