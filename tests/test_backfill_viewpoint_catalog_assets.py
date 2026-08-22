import csv
import tempfile
import unittest
from pathlib import Path

from scripts.backfill_viewpoint_catalog_assets import load_light_catalog_overrides


class LightCatalogOverrideTests(unittest.TestCase):
    def test_loads_pdf_and_attachment_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = (
                ("75_CSET_2023-2024正式报告轻量目录.csv", "官方PDF入口", "R-1", "https://example.org/a.pdf"),
                ("64_KISTEP韩文正式报告总目录与重点附件台账.csv", "官方附件", "R-2", "https://example.org/b.pdf"),
            )
            for name, field, report_id, url in cases:
                with (root / name).open("w", encoding="utf-8-sig", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["报告ID", "统一目录报告ID", field])
                    writer.writeheader()
                    writer.writerow({"报告ID": report_id, "统一目录报告ID": "", field: url})

            self.assertEqual(
                load_light_catalog_overrides(root),
                {"R-1": "https://example.org/a.pdf", "R-2": "https://example.org/b.pdf"},
            )


if __name__ == "__main__":
    unittest.main()
