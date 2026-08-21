import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extend_viewpoint_nistep_japanese import (
    classify_report_role,
    mirror_pdf_names,
    parse_report_list,
    select_full_pdf_url,
    stable_report_id,
)
from validate_viewpoint_research import expected_catalog_size


REPORT_LIST = """
<table><tr><td>NR:212</td><td>2026年8月</td><td><a href="http://hdl.handle.net/11035/0002000309">科学技術指標2026</a></td></tr>
<tr><td>RM:343</td><td>2024年9月</td><td><a href="http://hdl.handle.net/11035/0002000160">政策文書等の未来に関する記述の調査</a></td></tr>
<tr><td>DP:129</td><td>2015年12月</td><td><a href="http://hdl.handle.net/11035/3000">旧資料</a></td></tr>
<tr><td>NN:20</td><td>2025年3月</td><td><a href="http://hdl.handle.net/11035/4000">政策ノート</a></td></tr></table>
"""

OAI_TEXT = """
https://nistep.repo.nii.ac.jp/record/2000309/files/NISTEP-NR212-AbstractJ.pdf
https://nistep.repo.nii.ac.jp/record/2000309/files/NISTEP-NR212-SummaryJ.pdf
https://nistep.repo.nii.ac.jp/record/2000309/files/NISTEP-NR212-FullJ.pdf
https://nistep.repo.nii.ac.jp/record/2000309/files/NISTEP-NR212-StatisticsJ.pdf
"""


class NistepJapaneseCollectionTests(unittest.TestCase):
    def test_report_list_keeps_four_formal_series_since_2016(self) -> None:
        rows = parse_report_list(REPORT_LIST)
        self.assertEqual([(row.report_type, row.number) for row in rows], [("RM", "343"), ("NR", "212")])

    def test_stable_id_uses_landing_url_to_survive_duplicate_series_numbers(self) -> None:
        first = stable_report_id("NR", "212", "http://hdl.handle.net/11035/0002000309")
        second = stable_report_id("NR", "212", "http://hdl.handle.net/11035/0002000313")
        self.assertNotEqual(first, second)
        self.assertTrue(first.startswith("C-NISTEP-NR212-"))

    def test_mirror_names_cover_nistep_hyphen_variants(self) -> None:
        names = mirror_pdf_names("DP", "252")
        self.assertIn("NISTEP-DP252-FullJ.pdf", names)
        self.assertIn("NISTEP-DP-252-FullJ.pdf", names)

    def test_oai_selection_prefers_full_japanese_report(self) -> None:
        self.assertTrue(select_full_pdf_url(OAI_TEXT).endswith("NISTEP-NR212-FullJ.pdf"))

    def test_report_roles_preserve_institution_and_author_boundary(self) -> None:
        self.assertEqual(classify_report_role("NR"), ("NISTEP正式报告", "机构正式研究"))
        self.assertEqual(classify_report_role("DP"), ("讨论论文", "作者讨论论文"))

    def test_expected_catalog_size_accepts_nistep_tranche(self) -> None:
        self.assertEqual(
            expected_catalog_size(49, 105, 47, 104, 95, 29, 89, 40, 88, 192, nistep_asset_count=283),
            1121,
        )


if __name__ == "__main__":
    unittest.main()
