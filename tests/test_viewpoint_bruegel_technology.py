import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_bruegel_technology import (
    classify_technology_scope,
    catalog_asset_path,
    extract_official_pdf_urls,
    in_scope_title,
    parse_report_page,
    parse_sitemap_index,
    parse_sitemap_publication_urls,
    prefer_legacy_catalog_row,
    stable_report_id,
)
from validate_viewpoint_research import expected_catalog_size


INDEX_SAMPLE = """<?xml version="1.0"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://www.bruegel.org/sitemap.xml?page=1</loc></sitemap>
  <sitemap><loc>https://www.bruegel.org/sitemap.xml?page=2</loc></sitemap>
</sitemapindex>
"""

SITEMAP_SAMPLE = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.bruegel.org/policy-brief/eu-semiconductor-strategy</loc></url>
  <url><loc>https://www.bruegel.org/working-paper/china-critical-technologies</loc></url>
  <url><loc>https://www.bruegel.org/opinion-piece/unrelated</loc></url>
</urlset>
"""

PAGE_SAMPLE = """
<html><head>
<meta property="og:title" content="Lessons for Europe from China's semiconductor self-reliance">
<meta name="description" content="The paper compares semiconductor industrial policy in China and Europe.">
</head><body><main>
<h1>Lessons for Europe from China's semiconductor self-reliance</h1>
<dl><div class="c-single-header__meta-row">
<dt class="c-single-header__meta-label">Publishing date</dt>
<dd class="c-single-header__meta-term">18 November 2022</dd>
</div></dl>
<a href="/people/alicia-garcia-herrero">Alicia García-Herrero</a>
<a href="/sites/default/files/2022-11/PB-semiconductors.pdf">Download as PDF</a>
<a href="https://example.org/citation.pdf">Citation</a>
<article><p>China's semiconductor policy has implications for European capabilities.</p></article>
</main></body></html>
"""


class BruegelTechnologyCollectionTests(unittest.TestCase):
    def test_sitemap_index_and_publication_types_are_bounded(self) -> None:
        self.assertEqual(len(parse_sitemap_index(INDEX_SAMPLE)), 2)
        self.assertEqual(
            parse_sitemap_publication_urls(SITEMAP_SAMPLE),
            [
                "https://www.bruegel.org/policy-brief/eu-semiconductor-strategy",
                "https://www.bruegel.org/working-paper/china-critical-technologies",
            ],
        )

    def test_report_page_extracts_official_metadata(self) -> None:
        candidate = parse_report_page(
            PAGE_SAMPLE,
            "https://www.bruegel.org/policy-brief/lessons-europe-china-semiconductors",
        )
        self.assertEqual(candidate.published, "2022-11-18")
        self.assertIn("semiconductor self-reliance", candidate.title)
        self.assertEqual(candidate.authors, "Alicia García-Herrero")
        self.assertIn("European capabilities", candidate.page_text)

    def test_pdf_extraction_keeps_only_first_party_download_assets(self) -> None:
        self.assertEqual(
            extract_official_pdf_urls(PAGE_SAMPLE, "https://www.bruegel.org/policy-brief/sample"),
            ["https://www.bruegel.org/sites/default/files/2022-11/PB-semiconductors.pdf"],
        )

    def test_scope_keeps_core_technology_and_tech_industrial_baselines(self) -> None:
        self.assertTrue(in_scope_title("Competition in generative artificial intelligence foundation models"))
        self.assertTrue(in_scope_title("Unpacking China's industrial policy and its implications for Europe"))
        self.assertEqual(
            classify_technology_scope("Which companies are ahead in frontier innovation on critical technologies?"),
            "核心科技直接材料",
        )
        self.assertEqual(
            classify_technology_scope("How to de-risk European economic security in a world of interdependence"),
            "科技产业与经济安全基线",
        )

    def test_scope_rejects_finance_and_generic_digital_regulation(self) -> None:
        self.assertFalse(in_scope_title("The value added of central bank digital currencies"))
        self.assertFalse(in_scope_title("Decentralised finance: good technology, bad finance"))
        self.assertFalse(in_scope_title("Compliance principles for the Digital Markets Act"))
        self.assertFalse(in_scope_title("The Digital Markets Act is about enabling rights"))

    def test_report_id_is_stable_across_url_variants(self) -> None:
        base = "https://www.bruegel.org/policy-brief/eu-semiconductor-strategy"
        self.assertEqual(stable_report_id(base), stable_report_id(base + "/?x=1#top"))
        self.assertTrue(stable_report_id(base).startswith("C-BRUEGEL-"))

    def test_legacy_anchor_wins_when_current_row_links_same_pdf(self) -> None:
        current = {"报告ID": "C-BRUEGEL-X"}
        legacy = {"报告ID": "S-BR-2021-01"}
        self.assertIs(
            prefer_legacy_catalog_row(current, "abc", {"abc": legacy}),
            legacy,
        )
        self.assertIs(prefer_legacy_catalog_row(current, "def", {"abc": legacy}), current)

    def test_catalog_asset_path_falls_back_to_legacy_local_path(self) -> None:
        self.assertEqual(
            catalog_asset_path({"本地原始资产路径": "", "本地路径": "legacy.pdf"}),
            Path("legacy.pdf"),
        )

    def test_expected_catalog_size_includes_bruegel_tranche(self) -> None:
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
                bruegel_asset_count=88,
            ),
            646,
        )


if __name__ == "__main__":
    unittest.main()
