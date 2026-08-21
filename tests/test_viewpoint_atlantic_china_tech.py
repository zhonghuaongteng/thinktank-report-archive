from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_atlantic_china_tech import (
    classify_themes,
    extract_official_pdf_urls,
    is_tech_relevant,
    merge_ledger_rows,
    normalize_extracted_text,
)
from validate_viewpoint_research import expected_catalog_size


class AtlanticChinaTechCollectionTests(unittest.TestCase):
    def test_expected_catalog_size_includes_each_asset_tranche(self) -> None:
        self.assertEqual(
            expected_catalog_size(
                seed_count=49,
                catalog_asset_count=105,
                early_asset_count=47,
                cset_asset_count=104,
                atlantic_asset_count=95,
            ),
            400,
        )

    def test_tech_relevance_accepts_official_technology_taxonomy(self) -> None:
        self.assertTrue(
            is_tech_relevant(
                title="China Pathfinder annual scorecard",
                abstract="Economic indicators for China.",
                issue_ids=[2226],
                program_ids=[],
            )
        )

    def test_tech_relevance_rejects_generic_china_foreign_policy(self) -> None:
        self.assertFalse(
            is_tech_relevant(
                title="Hungary's policy on China",
                abstract="A review of bilateral diplomatic relations.",
                issue_ids=[2195],
                program_ids=[59028],
            )
        )

    def test_extract_pdf_urls_keeps_only_first_party_publication_assets(self) -> None:
        source = """
        <a href="https://www.atlanticcouncil.org/wp-content/uploads/2025/01/report.pdf?x=1">PDF</a>
        <a href="https://publications.atlanticcouncil.org/report/file.pdf">Download</a>
        <a href="https://example.org/other.pdf">Other</a>
        """

        self.assertEqual(
            extract_official_pdf_urls(source),
            [
                "https://www.atlanticcouncil.org/wp-content/uploads/2025/01/report.pdf?x=1",
                "https://publications.atlanticcouncil.org/report/file.pdf",
            ],
        )

    def test_classify_themes_supports_cross_cutting_technology_topics(self) -> None:
        themes = classify_themes(
            "Securing semiconductor supply chains",
            "Export controls and industrial policy in the US-China technology competition.",
        )

        self.assertIn("人工智能、芯片与算力", themes)
        self.assertIn("技术供应链与出口管制", themes)
        self.assertIn("创新体系与产业政策", themes)

    def test_rerun_preserves_existing_rows_and_replaces_refreshed_rows(self) -> None:
        existing = [
            {"报告ID": "C-ATL-1", "本地状态": "官方PDF已保存并校验"},
            {"报告ID": "C-ATL-2", "本地状态": "获取失败"},
        ]
        refreshed = [{"报告ID": "C-ATL-2", "本地状态": "官方网页全文已保存"}]

        merged = merge_ledger_rows(existing, refreshed, ["C-ATL-1", "C-ATL-2"])

        self.assertEqual([row["报告ID"] for row in merged], ["C-ATL-1", "C-ATL-2"])
        self.assertEqual(merged[1]["本地状态"], "官方网页全文已保存")

    def test_normalize_extracted_text_removes_line_end_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.txt"
            path.write_bytes("alpha  \r\nbeta\t\r\n".encode("utf-8"))

            normalize_extracted_text(path)

            self.assertEqual(path.read_text(encoding="utf-8"), "alpha\nbeta\n")


if __name__ == "__main__":
    unittest.main()
