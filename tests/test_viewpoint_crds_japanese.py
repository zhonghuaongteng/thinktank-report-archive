import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_crds_japanese import (
    classify_report_role,
    extract_crds_report_links,
    extract_official_pdf_urls,
    parse_report_page,
    stable_report_id,
    status_for_existing_catalog_row,
)
from validate_viewpoint_research import expected_catalog_size

YEAR_PAGE = """
<a href="../../CRDS-FY2024-FR-01.html">研究開発の俯瞰報告書</a>
<a href="../../CRDS-FY2024-SP-02.html">AI戦略プロポーザル</a>
<a href="../../CRDS-FY2024-WR-03.html">ワークショップ報告</a>
"""

DETAIL_PAGE = """
<html><body><main>
<a class="download" href="/crds/pdf/2024/FR/CRDS-FY2024-FR-01.pdf">PDFをダウンロード</a>
<h1>研究開発の俯瞰報告書　システム・情報科学技術分野（2024年）</h1>
<p>2025年2月</p><p>CRDS-FY2024-FR-01</p>
<p>人工知能、半導体、量子技術について中国、米国、欧州と比較する。</p>
<a href="/crds/pdf/2024/FR/CRDS-FY2024-FR-01_01.pdf">第1章</a>
</main></body></html>
"""


class CrdsJapaneseCollectionTests(unittest.TestCase):
    def test_year_page_keeps_four_formal_report_types(self) -> None:
        links = extract_crds_report_links(YEAR_PAGE, "https://www.jst.go.jp/crds/report/by-year/fy2024/index.html")
        self.assertEqual(len(links), 2)
        self.assertTrue(all("-WR-" not in url for url in links))

    def test_detail_page_extracts_japanese_metadata(self) -> None:
        candidate = parse_report_page(DETAIL_PAGE, "https://www.jst.go.jp/crds/report/CRDS-FY2024-FR-01.html")
        self.assertEqual(candidate.published, "2025-02-01")
        self.assertEqual(candidate.report_code, "CRDS-FY2024-FR-01")
        self.assertIn("システム・情報科学技術", candidate.title_ja)
        self.assertIn("中国", candidate.page_text)

    def test_pdf_extraction_prefers_whole_report_download(self) -> None:
        self.assertEqual(
            extract_official_pdf_urls(DETAIL_PAGE, "https://www.jst.go.jp/crds/report/CRDS-FY2024-FR-01.html"),
            ["https://www.jst.go.jp/crds/pdf/2024/FR/CRDS-FY2024-FR-01.pdf"],
        )

    def test_report_role_uses_official_series_code(self) -> None:
        self.assertEqual(classify_report_role("FR"), "研究开发全景报告")
        self.assertEqual(classify_report_role("SP"), "研究推进战略建议")
        self.assertEqual(classify_report_role("RR"), "调查分析报告")
        self.assertEqual(classify_report_role("XR"), "海外科技政策调查")

    def test_report_id_is_stable_from_report_code(self) -> None:
        self.assertEqual(stable_report_id("CRDS-FY2024-SP-02"), "C-CRDS-FY2024-SP-02")

    def test_expected_catalog_size_includes_crds_tranche(self) -> None:
        self.assertEqual(
            expected_catalog_size(49, 105, 47, 104, 95, 29, 89, 40, 88, crds_asset_count=192),
            838,
        )

    def test_existing_crds_rows_keep_original_storage_status(self) -> None:
        self.assertEqual(
            status_for_existing_catalog_row({"报告ID": "C-CRDS-FY2024-SP-02"}, Path("C-CRDS-FY2024-SP-02.pdf")),
            "官方PDF已保存并校验",
        )
        self.assertEqual(
            status_for_existing_catalog_row({"报告ID": "S-CRDS-2024-01"}, Path("S-CRDS-2024-01.pdf")),
            "复用库内既有资产",
        )


if __name__ == "__main__":
    unittest.main()
