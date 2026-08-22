from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.extend_viewpoint_stepi_china_series import (
    SERIES,
    choose_pdf_entries,
    official_landing_url,
    official_zip_url,
)


class StepiChinaSeriesTests(unittest.TestCase):
    def test_series_is_continuous_and_science_technology_centered(self) -> None:
        self.assertEqual([item.year for item in SERIES], [2017, 2018, 2019, 2020, 2021])
        self.assertEqual(len({item.report_id for item in SERIES}), 5)
        self.assertTrue(all(item.main_pdf.lower().endswith(".pdf") for item in SERIES))

    def test_official_urls_include_required_category(self) -> None:
        item = SERIES[0]
        self.assertIn("cateCont=A0203", official_landing_url(item))
        self.assertIn("streFileNm=A0203_202", official_zip_url(item))
        self.assertIn("purpose=1", official_zip_url(item))

    def test_zip_requires_expected_main_and_one_supplement(self) -> None:
        item = SERIES[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(item.main_pdf, b"%PDF-main")
                archive.writestr("appendix.pdf", b"%PDF-supp")
            main, supplement = choose_pdf_entries(path, item)
            self.assertEqual(main, item.main_pdf)
            self.assertEqual(supplement, "appendix.pdf")

    def test_zip_rejects_ambiguous_attachments(self) -> None:
        item = SERIES[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(item.main_pdf, b"%PDF-main")
                archive.writestr("a.pdf", b"%PDF-a")
                archive.writestr("b.pdf", b"%PDF-b")
            with self.assertRaisesRegex(ValueError, "exactly two PDFs"):
                choose_pdf_entries(path, item)


if __name__ == "__main__":
    unittest.main()
