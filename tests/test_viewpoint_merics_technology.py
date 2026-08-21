import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_merics_technology import (
    build_theme_rows,
    classify_technology_scope,
    extract_official_pdf_urls,
    in_scope_title,
    parse_report_page,
    parse_sitemap_report_urls,
    stable_report_id,
    status_for_existing_catalog_row,
)
from validate_viewpoint_research import expected_catalog_size


SITEMAP_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://merics.org/en/report/chinas-digital-rise</loc></url>
  <url><loc>https://merics.org/en/comment/unrelated</loc></url>
  <url><loc>https://merics.org/en/report/parent/chapter</loc></url>
</urlset>
"""


PAGE_SAMPLE = """
<html><head>
<meta name="description" content="A study of China's digital and industrial strategy.">
</head><body><main>
<h1>China's Digital Rise</h1>
<section class="field-name-field-date-published"><time datetime="2019-04-08T12:00:00Z">Apr 8, 2019</time></section>
<a href="/en/team/alice">Alice</a><a href="/en/team/bob">Bob</a>
<a class="file-download file-download-pdf" href="/sites/default/files/2020-04/digital-rise.pdf">Download PDF</a>
<p>China is building digital platforms and industrial capabilities.</p>
</main></body></html>
"""


class MericsTechnologyCollectionTests(unittest.TestCase):
    def test_sitemap_keeps_only_standalone_report_pages(self) -> None:
        self.assertEqual(
            parse_sitemap_report_urls(SITEMAP_SAMPLE),
            ["https://merics.org/en/report/chinas-digital-rise"],
        )

    def test_report_page_extracts_official_metadata(self) -> None:
        candidate = parse_report_page(PAGE_SAMPLE, "https://merics.org/en/report/chinas-digital-rise")

        self.assertEqual(candidate.published, "2019-04-08")
        self.assertEqual(candidate.title, "China's Digital Rise")
        self.assertEqual(candidate.authors, "Alice；Bob")
        self.assertIn("digital platforms", candidate.page_text)

    def test_pdf_extraction_keeps_only_merics_first_party_files(self) -> None:
        html = PAGE_SAMPLE + '<a href="https://example.org/citation.pdf">Citation</a>'

        self.assertEqual(
            extract_official_pdf_urls(html, "https://merics.org/en/report/chinas-digital-rise"),
            ["https://merics.org/sites/default/files/2020-04/digital-rise.pdf"],
        )

    def test_scope_accepts_core_technology_and_geoeconomic_baselines(self) -> None:
        self.assertTrue(in_scope_title("China's rise in semiconductors and Europe"))
        self.assertTrue(in_scope_title("Keeping value chains at home"))
        self.assertEqual(classify_technology_scope("China's rise in semiconductors and Europe"), "核心科技直接材料")
        self.assertEqual(classify_technology_scope("Keeping value chains at home"), "科技产业与经济安全基线")

    def test_scope_rejects_news_roundups_and_duplicate_executive_summary(self) -> None:
        self.assertFalse(in_scope_title("Executive Summary: Fragmented Europe: Dealing with China as a technology power"))
        self.assertFalse(in_scope_title("Olaf Scholz in Beijing + Mehr Staat für die Wirtschaft + Skepsis gegenüber digitaler Währung"))
        self.assertFalse(in_scope_title("Programming China"))

    def test_report_id_is_stable_across_url_variants(self) -> None:
        base = "https://merics.org/en/report/chinas-digital-rise"
        self.assertEqual(stable_report_id(base), stable_report_id(base + "/?x=1#top"))
        self.assertTrue(stable_report_id(base).startswith("C-MERICS-"))

    def test_theme_rows_keep_asset_status_for_matrix_grouping(self) -> None:
        rows = build_theme_rows([
            {
                "主题标签": "人工智能、芯片与算力；供应链、技术管制与经济安全",
                "科技关联层级": "核心科技直接材料",
                "报告ID": "C-MERICS-A",
                "发布日期": "2024-01-01",
                "观察窗": "W3",
                "报告名称": "Sample",
                "资料角色": "作者/项目正式研究",
                "本地原始资产": "a.pdf",
                "本地文本": "a.txt",
                "官方落地页": "https://merics.org/en/report/sample",
                "本地状态": "官方PDF已保存并校验",
            }
        ])

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["本地状态"], "官方PDF已保存并校验")

    def test_existing_status_distinguishes_current_batch_from_historical_reuse(self) -> None:
        self.assertEqual(
            status_for_existing_catalog_row({"报告ID": "C-MERICS-A"}, Path("C-MERICS-A.pdf")),
            "官方PDF已保存并校验",
        )
        self.assertEqual(
            status_for_existing_catalog_row({"报告ID": "C-MERICS-A"}, Path("E-MERICS-OLD.pdf")),
            "关联既有官方PDF",
        )
        self.assertEqual(
            status_for_existing_catalog_row({"报告ID": "C-MERICS-A"}, Path("C-MERICS-A.txt")),
            "官方网页全文已保存",
        )
        self.assertEqual(
            status_for_existing_catalog_row({"报告ID": "E-MERICS-OLD"}, Path("E-MERICS-OLD.pdf")),
            "复用库内既有资产",
        )

    def test_expected_catalog_size_includes_merics_tranche(self) -> None:
        self.assertEqual(
            expected_catalog_size(
                seed_count=49,
                catalog_asset_count=105,
                early_asset_count=47,
                cset_asset_count=104,
                atlantic_asset_count=95,
                belfer_asset_count=29,
                nbr_asset_count=89,
                merics_asset_count=40,
            ),
            558,
        )


if __name__ == "__main__":
    unittest.main()
