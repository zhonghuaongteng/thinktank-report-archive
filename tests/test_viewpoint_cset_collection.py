from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_cset_china_collection import (
    merge_ledger_rows,
    normalize_extracted_text,
    refresh_ledger_text_counts,
)


class CsetCollectionLedgerTests(unittest.TestCase):
    def test_rerun_preserves_existing_rows_and_replaces_refreshed_rows(self) -> None:
        existing = [
            {"报告ID": "C-CSET-1", "本地状态": "官方PDF已保存并校验"},
            {"报告ID": "C-CSET-2", "本地状态": "获取失败"},
        ]
        refreshed = [
            {"报告ID": "C-CSET-2", "本地状态": "官方PDF已保存并校验"},
        ]

        merged = merge_ledger_rows(existing, refreshed, ["C-CSET-1", "C-CSET-2"])

        self.assertEqual([row["报告ID"] for row in merged], ["C-CSET-1", "C-CSET-2"])
        self.assertEqual(merged[0]["本地状态"], "官方PDF已保存并校验")
        self.assertEqual(merged[1]["本地状态"], "官方PDF已保存并校验")

    def test_normalize_extracted_text_removes_only_line_end_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.txt"
            path.write_bytes("alpha  \r\nbeta\t\r\ngamma delta\n".encode("utf-8"))

            normalize_extracted_text(path)

            self.assertEqual(path.read_text(encoding="utf-8"), "alpha\nbeta\ngamma delta\n")

    def test_refresh_ledger_text_counts_tracks_normalized_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.txt"
            path.write_bytes("alpha  \r\nbeta\n".encode("utf-8"))
            rows = [{"本地文本": str(path), "提取文本字符数": "999"}]

            refresh_ledger_text_counts(rows)

            self.assertEqual(rows[0]["提取文本字符数"], str(len("alpha\nbeta\n")))


if __name__ == "__main__":
    unittest.main()
