import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from repair_viewpoint_nistep_dp242 import REPORT_ID, STATUS, repair_rows


class RepairNistepDp242Tests(unittest.TestCase):
    def test_repair_updates_only_target_across_catalog_ledger_and_theme_rows(self):
        catalog = [
            {"报告ID": REPORT_ID, "本地路径": "", "正文完整度": "获取失败", "本地原始资产路径": "", "原始资产状态": "获取失败"},
            {"报告ID": "OTHER", "本地路径": "keep", "正文完整度": "keep", "本地原始资产路径": "keep", "原始资产状态": "keep"},
        ]
        ledger = [
            {"报告ID": REPORT_ID, "官方PDF": "", "页面来源": "", "本地原始资产": "", "本地文本": "", "本地切片或转写": "", "字节数": "0", "SHA256": "", "PDF页数": "0", "提取文本字符数": "0", "本地状态": "获取失败", "错误": "old", "获取日期": "old"}
        ]
        themes = [{"报告ID": REPORT_ID, "本地原始资产": "", "本地文本": "", "本地状态": "获取失败"}]

        repair_rows(catalog, ledger, themes, "asset.txt", "text.txt", "slice.md", 123, "abc", 456, "2026-08-23")

        self.assertEqual(catalog[0]["原始资产状态"], STATUS)
        self.assertEqual(catalog[0]["本地原始资产路径"], "asset.txt")
        self.assertEqual(catalog[1]["原始资产状态"], "keep")
        self.assertEqual(ledger[0]["官方PDF"], "https://nistep.repo.nii.ac.jp/record/2000273/files/NISTEP-DP242-FullJ.pdf")
        self.assertEqual(ledger[0]["本地状态"], STATUS)
        self.assertEqual(ledger[0]["错误"], "")
        self.assertEqual(themes[0]["本地状态"], STATUS)


if __name__ == "__main__":
    unittest.main()
