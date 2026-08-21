from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_nbr_technology import (
    classify_china_relevance,
    classify_technology_scope,
    extract_official_pdf_urls,
    ip_commission_supplements,
    jina_request_headers,
    merge_ledger_rows,
    merge_nbr_catalog_rows,
    normalize_text_content,
    parse_program_publications,
    replace_institution_catalog_rows,
    stable_report_id,
)
from validate_viewpoint_research import expected_catalog_size


PROGRAM_SAMPLE = """
All Program Publications

Export Controls
### [Charting China’s Export Controls Predicting Impacts on Critical U.S. Supply Chains](https://www.nbr.org/publication/charting-chinas-export-controls-predicting-impacts-on-critical-u-s-supply-chains/)

 Emma M. Rafaelof and John VerWey

 Report | Jan 9, 2025

AI Governance
### [The Indo-Pacific and the Challenge of Multilateral AI Governance](https://www.nbr.org/publication/the-indo-pacific-and-the-challenge-of-multilateral-ai-governance/)

 Renan Araujo

 Brief | May 12, 2026

China's Digital Strategy
### [China’s Strategic Approach to the Digital Revolution Podcast Series](https://www.nbr.org/publication/chinas-strategic-approach-to-the-digital-revolution/)

 Doug Strub

 Podcast Series | Aug 5, 2022
"""


class NBRTechnologyCollectionTests(unittest.TestCase):
    def test_program_parser_extracts_metadata_and_excludes_audio_only_types(self) -> None:
        candidates = parse_program_publications(PROGRAM_SAMPLE)

        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].published, "2025-01-09")
        self.assertEqual(candidates[0].material_type, "Report")
        self.assertEqual(candidates[0].category, "Export Controls")
        self.assertEqual(candidates[1].authors, "Renan Araujo")

    def test_report_id_is_stable_across_query_and_fragment_variants(self) -> None:
        base = "https://www.nbr.org/publication/chinas-approach-to-ai-development-and-governance/"

        self.assertEqual(stable_report_id(base), stable_report_id(base + "?x=1#content"))
        self.assertTrue(stable_report_id(base).startswith("C-NBR-"))

    def test_china_relevance_has_direct_comparative_and_baseline_layers(self) -> None:
        self.assertEqual(
            classify_china_relevance("China’s Approach to AI Development", "", "AI Governance"),
            "直接涉华科技",
        )
        comparative = " ".join(["China and Chinese technology competition"] * 5)
        self.assertEqual(
            classify_china_relevance("Quantum Ecosystems in the Indo-Pacific", comparative, "Quantum Computing"),
            "含中国比较的印太技术材料",
        )
        self.assertEqual(
            classify_china_relevance("AI Governance in India", "India focuses on domestic regulation.", "AI Governance"),
            "区域技术基线",
        )

    def test_technology_scope_separates_core_from_geoeconomic_baseline(self) -> None:
        self.assertEqual(
            classify_technology_scope("Quantum Ecosystems", "Quantum Computing"),
            "核心科技直接材料",
        )
        self.assertEqual(
            classify_technology_scope("RCEP Negotiations", "Trade Agreements"),
            "科技地缘经济基线",
        )

    def test_pdf_extraction_keeps_only_nbr_publication_assets(self) -> None:
        text = """
        [Download](https://www.nbr.org/wp-content/uploads/pdfs/publications/sr115_report.pdf)
        [Other](https://www.nbr.org/wp-content/uploads/files/other.pdf)
        [Citation](https://example.org/citation.pdf)
        """

        self.assertEqual(
            extract_official_pdf_urls(text),
            ["https://www.nbr.org/wp-content/uploads/pdfs/publications/sr115_report.pdf"],
        )

    def test_jina_requests_do_not_reuse_browser_user_agent(self) -> None:
        headers = jina_request_headers()

        self.assertNotIn("User-Agent", headers)
        self.assertEqual(headers["Accept"], "text/markdown")

    def test_web_text_normalization_removes_line_end_whitespace(self) -> None:
        self.assertEqual(normalize_text_content("alpha  \n \nbeta\t\n\n\n"), "alpha\n\nbeta\n")

    def test_ip_commission_supplements_are_recent_first_party_assets(self) -> None:
        supplements = ip_commission_supplements()

        self.assertEqual(len(supplements), 6)
        self.assertTrue(all(item.published >= "2017-01-01" for item in supplements))
        self.assertTrue(all("nbr.org/wp-content/uploads/pdfs/publications/" in item.pdf_url for item in supplements))

    def test_rerun_preserves_existing_rows_and_replaces_refreshed_rows(self) -> None:
        existing = [
            {"报告ID": "C-NBR-A", "本地状态": "官方PDF已保存并校验"},
            {"报告ID": "C-NBR-B", "本地状态": "获取失败"},
        ]
        refreshed = [{"报告ID": "C-NBR-B", "本地状态": "官方网页全文已保存"}]

        merged = merge_ledger_rows(existing, refreshed, ["C-NBR-A", "C-NBR-B"])

        self.assertEqual([row["报告ID"] for row in merged], ["C-NBR-A", "C-NBR-B"])
        self.assertEqual(merged[1]["本地状态"], "官方网页全文已保存")

    def test_catalog_rerun_prunes_stale_nbr_rows(self) -> None:
        catalog = [{"报告ID": "BASE-1"}, {"报告ID": "C-NBR-OLD"}]
        refreshed = [{"报告ID": "C-NBR-NEW"}]

        merged = replace_institution_catalog_rows(catalog, refreshed, "C-NBR-")

        self.assertEqual([row["报告ID"] for row in merged], ["BASE-1", "C-NBR-NEW"])

    def test_catalog_rerun_preserves_current_rows_that_need_no_download(self) -> None:
        existing = [{"报告ID": "C-NBR-A"}, {"报告ID": "C-NBR-B"}]
        refreshed = [{"报告ID": "C-NBR-B", "报告名称": "refreshed"}]

        merged = merge_nbr_catalog_rows(existing, refreshed, ["C-NBR-A", "C-NBR-B"])

        self.assertEqual([row["报告ID"] for row in merged], ["C-NBR-A", "C-NBR-B"])
        self.assertEqual(merged[1]["报告名称"], "refreshed")

    def test_expected_catalog_size_includes_nbr_tranche(self) -> None:
        self.assertEqual(
            expected_catalog_size(
                seed_count=49,
                catalog_asset_count=105,
                early_asset_count=47,
                cset_asset_count=104,
                atlantic_asset_count=95,
                belfer_asset_count=29,
                nbr_asset_count=89,
            ),
            518,
        )


if __name__ == "__main__":
    unittest.main()
