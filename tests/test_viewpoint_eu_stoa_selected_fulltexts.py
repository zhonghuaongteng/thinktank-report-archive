import unittest
from unittest.mock import patch

from scripts.extend_viewpoint_eu_stoa_selected_fulltexts import (
    SELECTED_ITEMS,
    browser_pdf,
    inferred_official_pdf_url,
    official_pdf_url,
)


class EuStoaSelectedFulltextsTests(unittest.TestCase):
    def test_selection_remains_small_relative_to_catalog(self):
        self.assertEqual(len(SELECTED_ITEMS), 20)
        self.assertLess(len(SELECTED_ITEMS), 30)

    def test_selection_covers_each_year_and_science_innovation_axes(self):
        self.assertEqual({item["date"][:4] for item in SELECTED_ITEMS}, {str(year) for year in range(2016, 2027)})
        axes = {axis for item in SELECTED_ITEMS for axis in item["axes"]}
        self.assertIn("技术评估与前瞻方法", axes)
        self.assertIn("科研体系与研发资助", axes)
        self.assertIn("创新政策与区域能力", axes)
        self.assertIn("关键技术与产业转化", axes)
        self.assertIn("国际科研合作与开放条件", axes)

    def test_security_led_studies_are_excluded(self):
        titles = "\n".join(item["title"].lower() for item in SELECTED_ITEMS)
        self.assertNotIn("battlefield", titles)
        self.assertNotIn("hybrid threats", titles)
        self.assertNotIn("cybersecurity in the eu common security", titles)

    def test_only_official_english_regdata_pdf_is_selected(self):
        links = [
            ("EN (PDF-4 MB)", "https://www.europarl.europa.eu/RegData/etudes/STUD/2025/765780/EPRS_STU(2025)765780_EN.pdf"),
            ("FR", "https://example.org/translation.pdf"),
        ]
        self.assertEqual(official_pdf_url(links), links[0][1])

    def test_legacy_official_http_regdata_pdf_is_selected(self):
        legacy = "http://www.europarl.europa.eu/RegData/etudes/STUD/2016/563501/EPRS_STU(2016)563501_EN.pdf"
        self.assertEqual(official_pdf_url([("EN (PDF-1 MB)", legacy)]), legacy)

    def test_missing_page_link_can_be_inferred_from_official_document_code(self):
        self.assertEqual(
            inferred_official_pdf_url("https://www.europarl.europa.eu/stoa/en/document/EPRS_STU(2023)753166"),
            "https://www.europarl.europa.eu/RegData/etudes/STUD/2023/753166/EPRS_STU(2023)753166_EN.pdf",
        )

    def test_pdf_ranges_can_finish_without_content_range(self):
        first = b"%PDF" + b"x" * (1_500_000 - 4)
        second = b"tail"
        with patch(
            "scripts.extend_viewpoint_eu_stoa_selected_fulltexts._range_fetch",
            side_effect=[(206, "", first), (206, "", second)],
        ):
            self.assertEqual(browser_pdf("target", "https://example.org/report.pdf"), first + second)

    def test_pdf_download_retries_the_other_protocol_after_gateway_empty_response(self):
        pdf = b"%PDF-recovered"
        with patch(
            "scripts.extend_viewpoint_eu_stoa_selected_fulltexts._range_fetch",
            side_effect=[(202, "", b""), (200, "", pdf)],
        ) as fetch:
            self.assertEqual(
                browser_pdf("target", "http://www.europarl.europa.eu/RegData/etudes/report_EN.pdf"),
                pdf,
            )
        self.assertEqual(fetch.call_args_list[1].args[1], "https://www.europarl.europa.eu/RegData/etudes/report_EN.pdf")


if __name__ == "__main__":
    unittest.main()
