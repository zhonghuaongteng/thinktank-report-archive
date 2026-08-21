from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_belfer_china_tech import (
    classify_themes,
    extract_official_pdf_urls,
    is_material_relevant,
    merge_ledger_rows,
    parse_search_cards,
    pdf_asset_status,
    replace_institution_catalog_rows,
    stable_report_id,
)
from validate_viewpoint_research import expected_catalog_size


SEARCH_RESULTS = """
<article class="teaser js-link-event">
  <div class="teaser-main">
    <h2 class="-sans"><a href="/research-analysis/autonomous-arsenal">The Autonomous Arsenal in Defense of Taiwan</a></h2>
    <div class="card-meta"><time datetime="2025-02-03T12:00:00Z">Feb. 3, 2025</time><span>by Gregory Allen</span></div>
  </div>
  <div class="teaser-info"><div class="teaser-info-inner">
    <div class="type">Reports &amp; Papers</div>
    <div class="source">from <strong>Belfer Center for Science and International Affairs</strong></div>
  </div></div>
</article>
<article class="teaser js-link-event">
  <div class="teaser-main">
    <h2 class="-sans"><a href="https://www.belfercenter.org/research-analysis/china-cyber">China &amp; Cyber Risk</a></h2>
    <div class="card-meta"><time datetime="2017-06-12T12:00:00Z">Jun. 12, 2017</time></div>
  </div>
  <div class="teaser-info"><div class="teaser-info-inner"><div class="type">Testimonies</div></div></div>
</article>
"""


class BelferChinaTechCollectionTests(unittest.TestCase):
    def test_search_cards_parse_official_fields_and_decode_entities(self) -> None:
        cards = parse_search_cards(SEARCH_RESULTS)

        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0].published, "2025-02-03")
        self.assertEqual(cards[0].content_type, "Reports & Papers")
        self.assertEqual(
            cards[0].landing_url,
            "https://www.belfercenter.org/research-analysis/autonomous-arsenal",
        )
        self.assertEqual(cards[1].title, "China & Cyber Risk")

    def test_report_id_is_stable_across_query_and_fragment_variants(self) -> None:
        base = "https://www.belfercenter.org/research-analysis/china-cyber"

        self.assertEqual(
            stable_report_id(base),
            stable_report_id(base + "?utm_source=test#download"),
        )
        self.assertTrue(stable_report_id(base).startswith("C-BEL-"))

    def test_material_relevance_accepts_each_authoritative_intersection(self) -> None:
        self.assertTrue(
            is_material_relevant(
                title="Competition with China in artificial intelligence",
                page_text="A formal technology assessment.",
                discovered_by={"tech_topics_with_china_keyword"},
            )
        )
        self.assertTrue(
            is_material_relevant(
                title="The Autonomous Arsenal in Defense of Taiwan",
                page_text="Autonomous systems, AI, drones, and semiconductors shape the contest.",
                discovered_by={"china_topics"},
            )
        )

    def test_material_relevance_rejects_generic_geopolitics(self) -> None:
        self.assertFalse(
            is_material_relevant(
                title="Multi-alignment as strategy",
                page_text="Diplomatic relations among Washington, Beijing, and the Global South.",
                discovered_by={"china_topics"},
            )
        )

    def test_keyword_discovery_rejects_incidental_china_mentions(self) -> None:
        self.assertFalse(
            is_material_relevant(
                title="European technology sovereignty",
                page_text="China is mentioned once in a comparison with the United States.",
                discovered_by={"tech_topics_with_china_keyword"},
            )
        )

    def test_extract_pdf_urls_keeps_only_belfer_first_party_assets(self) -> None:
        source = """
        <a class="btn -download" href="/sites/default/files/2025-02/report%20one.pdf">Download</a>
        <a href="https://www.belfercenter.org/sites/default/files/2024/report-two.pdf?x=1">PDF</a>
        <a href="https://example.org/citation.pdf">Citation</a>
        """

        self.assertEqual(
            extract_official_pdf_urls(source),
            [
                "https://www.belfercenter.org/sites/default/files/2025-02/report%20one.pdf",
                "https://www.belfercenter.org/sites/default/files/2024/report-two.pdf?x=1",
            ],
        )

    def test_theme_classification_covers_core_technology_domains(self) -> None:
        themes = classify_themes(
            "Chinese artificial intelligence and semiconductor capabilities",
            "Cyber operations, autonomous drones, and export controls.",
        )

        self.assertIn("人工智能、芯片与算力", themes)
        self.assertIn("网络安全与数字治理", themes)
        self.assertIn("技术供应链与出口管制", themes)
        self.assertIn("国防、航天与无人系统", themes)

    def test_rerun_preserves_existing_rows_and_replaces_refreshed_rows(self) -> None:
        existing = [
            {"报告ID": "C-BEL-A", "本地状态": "官方PDF已保存并校验"},
            {"报告ID": "C-BEL-B", "本地状态": "获取失败"},
        ]
        refreshed = [{"报告ID": "C-BEL-B", "本地状态": "官方网页全文已保存"}]

        merged = merge_ledger_rows(existing, refreshed, ["C-BEL-A", "C-BEL-B"])

        self.assertEqual([row["报告ID"] for row in merged], ["C-BEL-A", "C-BEL-B"])
        self.assertEqual(merged[1]["本地状态"], "官方网页全文已保存")

    def test_catalog_rerun_prunes_rows_that_no_longer_meet_scope(self) -> None:
        catalog = [
            {"报告ID": "BASE-1", "报告名称": "base"},
            {"报告ID": "C-BEL-OLD", "报告名称": "incidental mention"},
        ]
        refreshed = [{"报告ID": "C-BEL-NEW", "报告名称": "substantive China technology"}]

        merged = replace_institution_catalog_rows(catalog, refreshed, "C-BEL-")

        self.assertEqual([row["报告ID"] for row in merged], ["BASE-1", "C-BEL-NEW"])

    def test_pdf_status_distinguishes_own_file_from_cross_report_deduplication(self) -> None:
        self.assertEqual(
            pdf_asset_status(Path("C-BEL-ABC.pdf"), "C-BEL-ABC"),
            "官方PDF已保存并校验",
        )
        self.assertEqual(
            pdf_asset_status(Path("C-ATL-123.pdf"), "C-BEL-ABC"),
            "关联既有官方PDF",
        )

    def test_expected_catalog_size_includes_belfer_tranche(self) -> None:
        self.assertEqual(
            expected_catalog_size(
                seed_count=49,
                catalog_asset_count=105,
                early_asset_count=47,
                cset_asset_count=104,
                atlantic_asset_count=95,
                belfer_asset_count=42,
            ),
            442,
        )


if __name__ == "__main__":
    unittest.main()
