import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import extend_viewpoint_nistep_japanese as nistep
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
    def test_indicator_html_index_maps_official_series_page(self) -> None:
        indicator_html_index_url = getattr(nistep, "indicator_html_index_url", lambda *_: "")
        self.assertEqual(
            indicator_html_index_url("科学技術指標2024", "341"),
            "https://www.nistep.go.jp/sti_indicator/2024/RM341_00.html",
        )
        self.assertEqual(indicator_html_index_url("地域科学技術指標2019", "294"), "")

    def test_indicator_html_links_stay_inside_report_directory(self) -> None:
        extract_indicator_html_links = getattr(nistep, "extract_indicator_html_links", lambda *_: [])
        html = b'''<a href="RM341_01.html">chapter</a>
        <a href="./RM341_table.html">tables</a>
        <a href="RM341_01.html#part">duplicate</a>
        <a href="../2023/RM328_00.html">other year</a>
        <a href="https://example.com/x.html">external</a>'''
        self.assertEqual(
            extract_indicator_html_links(
                html,
                "https://www.nistep.go.jp/sti_indicator/2024/RM341_00.html",
            ),
            [
                "https://www.nistep.go.jp/sti_indicator/2024/RM341_01.html",
                "https://www.nistep.go.jp/sti_indicator/2024/RM341_table.html",
            ],
        )

    def test_indicator_html_report_combines_official_pages(self) -> None:
        fetch_indicator_html_report = getattr(nistep, "fetch_indicator_html_report", lambda *_args, **_kwargs: ("", ""))
        index = "https://www.nistep.go.jp/sti_indicator/2024/RM341_00.html"
        chapter = "https://www.nistep.go.jp/sti_indicator/2024/RM341_01.html"
        pages = {
            index: b'<html><body><main>index text<a href="RM341_01.html">chapter</a></main></body></html>',
            chapter: b"<html><body><main>chapter evidence</main></body></html>",
        }

        def loader(url: str, timeout: int = 60):
            return pages[url], url, "text/html"

        text, source_url = fetch_indicator_html_report(
            nistep.Candidate("RM", "341", "2024-08-01", "科学技術指標2024", "http://hdl.handle.net/11035/x"),
            loader,
        )
        self.assertEqual(source_url, index)
        self.assertIn("index text", text)
        self.assertIn("chapter evidence", text)
        self.assertIn(chapter, text)

    def test_acquire_uses_official_indicator_html_before_repository(self) -> None:
        candidate = nistep.Candidate(
            "RM", "341", "2024-08-01", "科学技術指標2024", "http://hdl.handle.net/11035/x", "2000116"
        )
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            nistep,
            "fetch_indicator_html_report",
            return_value=("official indicator evidence " * 30, "https://www.nistep.go.jp/sti_indicator/2024/RM341_00.html"),
        ):
            result = nistep.acquire(candidate, "", Path(temp_dir))
        self.assertEqual(result.status, "官方HTML版报告已保存")
        self.assertEqual(result.source, "NISTEP官方HTML版报告")
        self.assertTrue(result.proxy_cache)

    def test_acquire_uses_repository_fulltext_before_release_summary(self) -> None:
        candidate = nistep.Candidate(
            "RM", "284", "2018-08-01", "地域科学技術指標2018", "http://hdl.handle.net/11035/x", "2000084"
        )
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            nistep, "fetch_indicator_html_report", return_value=("", "")
        ), patch.object(
            nistep,
            "fetch_official_release_page",
            return_value=(
                "## SOURCE https://www.nistep.go.jp/archives/41356/\n\n" + "official release evidence " * 20,
                "https://www.nistep.go.jp/archives/41356/",
            ),
        ), patch.object(
            nistep,
            "fetch_jina",
            side_effect=[
                "https://nistep.repo.nii.ac.jp/record/2000084/files/NISTEP-RM284-FullJ.pdf",
                "repository fulltext evidence " * 30,
            ],
        ), patch.object(nistep, "probe_mirror", return_value=""):
            result = nistep.acquire(candidate, "", Path(temp_dir))
        self.assertEqual(result.status, "官方仓储PDF代理全文已保存")
        self.assertEqual(result.source, "NISTEP官方仓储PDF的Jina代理全文")
        self.assertTrue(result.proxy_cache)
        self.assertTrue(result.oai_cache)

    def test_acquire_uses_repository_summary_when_full_pdf_proxy_is_unavailable(self) -> None:
        candidate = nistep.Candidate(
            "DP", "242", "2025-11-01", "博士人材調査", "https://nistep.repo.nii.ac.jp/records/2000273", "2000273"
        )
        oai = "https://nistep.repo.nii.ac.jp/record/2000273/files/NISTEP-DP242-FullJ.pdf"
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            nistep, "fetch_indicator_html_report", return_value=("", "")
        ), patch.object(
            nistep, "fetch_official_release_page", return_value=("", "")
        ), patch.object(
            nistep,
            "fetch_jina",
            side_effect=[oai, RuntimeError("full PDF proxy unavailable"), "official summary evidence " * 40],
        ), patch.object(nistep, "probe_mirror", return_value=""):
            result = nistep.acquire(candidate, "", Path(temp_dir))
        self.assertEqual(result.status, "官方仓储概要PDF代理文本已保存")
        self.assertIn("概要PDF", result.source)
        self.assertTrue(result.proxy_cache)
        self.assertTrue(result.pdf_url.endswith("NISTEP-DP242-FullJ.pdf"))

    def test_acquire_falls_back_to_release_summary_when_repository_has_no_pdf(self) -> None:
        candidate = nistep.Candidate(
            "RM", "284", "2018-08-01", "地域科学技術指標2018", "http://hdl.handle.net/11035/x", "2000084"
        )
        release = "## SOURCE https://www.nistep.go.jp/archives/41356/\n\n" + "official release evidence " * 20
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            nistep, "fetch_indicator_html_report", return_value=("", "")
        ), patch.object(
            nistep, "fetch_official_release_page", return_value=(release, "https://www.nistep.go.jp/archives/41356/")
        ), patch.object(nistep, "fetch_jina", return_value="metadata without pdf"):
            result = nistep.acquire(candidate, "", Path(temp_dir))
        self.assertEqual(result.status, "官方发布页摘要已保存")
        self.assertEqual(result.source, "NISTEP官方发布页摘要")

    def test_status_summary_reports_official_html_separately(self) -> None:
        formatter = getattr(nistep, "nistep_status_summary", lambda *_: "")
        summary = formatter(Counter({"官方PDF已保存并校验": 2, "官方HTML版报告已保存": 3, "官方发布页摘要已保存": 4, "官方仓储概要PDF代理文本已保存": 1, "获取失败": 1}))
        self.assertIn("官方HTML版报告：3项", summary)
        self.assertIn("官方发布页摘要：4项", summary)
        self.assertIn("仓储概要PDF代理文本：1项", summary)
        self.assertIn("失败：1项", summary)

    def test_crds_nistep_comparison_preserves_role_and_asset_boundaries(self) -> None:
        builder = getattr(nistep, "build_crds_nistep_comparison", lambda *_: [])
        crds = [{"观察窗": "W1", "科技关联层级": "核心科技直接材料", "主题标签": "人工智能；中国科技政策与能力比较", "资料角色": "CRDS机构正式研究", "本地状态": "官方PDF已保存并校验"}]
        nistep_rows = [{"观察窗": "W3", "科技关联层级": "科技创新政策与能力基线", "主题标签": "人工智能；中国科技能力与国际比较", "资料角色": "作者讨论论文", "本地状态": "获取失败"}]
        rows = builder(crds, nistep_rows)
        summaries = {row["机构"]: row for row in rows if row["对照层级"] == "机构总览"}
        self.assertIn("CRDS", summaries)
        self.assertIn("NISTEP", summaries)
        self.assertEqual(summaries["CRDS"]["机构正式研究"], "1")
        self.assertEqual(summaries["NISTEP"]["作者讨论研究"], "1")
        self.assertEqual(summaries["NISTEP"]["待补全文"], "1")
        self.assertEqual(summaries["CRDS"]["中国主题材料"], "1")

    def test_release_page_discovery_selects_matching_official_archive(self) -> None:
        finder = getattr(nistep, "fetch_official_release_page", lambda *_args, **_kwargs: ("", ""))
        search_url = "https://www.nistep.go.jp/?s="
        release_url = "https://www.nistep.go.jp/archives/55391/"
        search_html = f'''<html><body>
        <a href="https://www.nistep.go.jp/archives/11111/">unrelated event</a>
        <a href="{release_url}">「科学技術指標2023（調査資料-328）」を公開しました</a>
        </body></html>'''.encode()
        release_html = "<html><body><article><h1>科学技術指標2023</h1><p>major result evidence</p></article></body></html>".encode()

        def loader(url: str, timeout: int = 60):
            if url.startswith(search_url):
                return search_html, url, "text/html"
            if url == release_url:
                return release_html, url, "text/html"
            raise AssertionError(url)

        text, page_url = finder(
            nistep.Candidate("RM", "328", "2023-08-01", "科学技術指標2023", "http://hdl.handle.net/11035/x"),
            loader,
        )
        self.assertEqual(page_url, release_url)
        self.assertIn("major result evidence", text)

    def test_release_page_discovery_retries_with_report_number(self) -> None:
        finder = getattr(nistep, "fetch_official_release_page", lambda *_args, **_kwargs: ("", ""))
        release_url = "https://www.nistep.go.jp/archives/41356/"
        empty_html = b"<html><body>no exact-title result</body></html>"
        numbered_html = f'''<html><body>
        <a href="{release_url}">科学技術指標2019（調査資料-283）及び科学研究のベンチマーキング2019（調査資料-284）の公表</a>
        </body></html>'''.encode()
        release_html = b"<html><body><article>benchmark release evidence</article></body></html>"

        def loader(url: str, timeout: int = 60):
            if url == release_url:
                return release_html, url, "text/html"
            if "%E8%AA%BF%E6%9F%BB%E8%B3%87%E6%96%99-284" in url:
                return numbered_html, url, "text/html"
            return empty_html, url, "text/html"

        text, page_url = finder(
            nistep.Candidate("RM", "284", "2019-08-01", "科学研究のベンチマーキング2019-論文分析でみる世界の研究活動の変化と日本の状況-", "http://hdl.handle.net/11035/x"),
            loader,
        )
        self.assertEqual(page_url, release_url)
        self.assertIn("benchmark release evidence", text)

    def test_release_page_discovery_uses_wordpress_rest_index(self) -> None:
        finder = getattr(nistep, "fetch_official_release_page", lambda *_args, **_kwargs: ("", ""))
        release_url = "https://www.nistep.go.jp/archives/62352/"
        rest_json = '''[{"id":62352,"title":"プレプリントの査読論文に対する先行性の実証分析 [DISCUSSION PAPER No.248]","url":"https://www.nistep.go.jp/archives/62352/"}]'''.encode()
        release_html = b"<html><body><article>preprint release evidence</article></body></html>"

        def loader(url: str, timeout: int = 60):
            if url == release_url:
                return release_html, url, "text/html"
            if "/wp-json/wp/v2/search?" in url and "DISCUSSION%20PAPER%20No.248" in url:
                return rest_json, url, "application/json"
            if "/wp-json/wp/v2/search?" in url:
                return b"[]", url, "application/json"
            return b"<html><body>no result</body></html>", url, "text/html"

        text, page_url = finder(
            nistep.Candidate("DP", "248", "2026-03-01", "プレプリントの査読論文に対する先行性の実証分析", "http://hdl.handle.net/11035/x"),
            loader,
        )
        self.assertEqual(page_url, release_url)
        self.assertIn("preprint release evidence", text)

    def test_release_page_discovery_uses_teiten_year_hint(self) -> None:
        finder = getattr(nistep, "fetch_official_release_page", lambda *_args, **_kwargs: ("", ""))
        release_url = "https://www.nistep.go.jp/archives/52391/"
        rest_json = '''[{"id":52391,"title":"NISTEP定点調査2021 [NISTEP REPORT No.194, 195]の公表","url":"https://www.nistep.go.jp/archives/52391/"}]'''.encode()

        def loader(url: str, timeout: int = 60):
            if url == release_url:
                return b"<html><body><article>teiten 2021 release evidence</article></body></html>", url, "text/html"
            if "/wp-json/wp/v2/search?search=NISTEP%E5%AE%9A%E7%82%B9%E8%AA%BF%E6%9F%BB2021&" in url:
                return rest_json, url, "application/json"
            if "/wp-json/wp/v2/search?" in url:
                return b"[]", url, "application/json"
            return b"<html><body>no result</body></html>", url, "text/html"

        text, page_url = finder(
            nistep.Candidate("NR", "195", "2022-08-01", "科学技術の状況に係る総合的意識調査（NISTEP定点調査2021）データ集", "http://hdl.handle.net/11035/x"),
            loader,
        )
        self.assertEqual(page_url, release_url)
        self.assertIn("teiten 2021 release evidence", text)

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
