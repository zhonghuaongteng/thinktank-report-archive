import sys
import unittest
from pathlib import Path

from scripts.validate_viewpoint_research import expected_catalog_size


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

try:
    import extend_viewpoint_kistep_korean as kistep
except ModuleNotFoundError:
    kistep = None


class KistepKoreanCollectionTests(unittest.TestCase):
    def test_expected_catalog_size_accepts_kistep_formal_catalog(self) -> None:
        self.assertEqual(
            expected_catalog_size(
                49, 105, 47, 104, 95, 29, 89, 40, 88, 192, 283,
                stepi_asset_count=518,
                kistep_asset_count=1174,
            ),
            2813,
        )

    def test_catalog_page_parses_identity_category_keywords_and_download(self) -> None:
        self.assertIsNotNone(kistep, "KISTEP collector module is not implemented")
        html = b"""
        <p class="page"><span class="total">\xec\xa0\x84\xec\xb2\xb4 <strong>1174\xea\xb1\xb4</strong></span>
          <span class="current">\xed\x8e\x98\xec\x9d\xb4\xec\xa7\x80 <strong>1</strong>/118</span></p>
        <div class="board_list"><ul class="list_item report_list"><li>
          <div class="group"><div class="item">
            <strong class="title"><a href="/reportAllDetail.es?mid=x&amp;rpt_no=RES0220260119"
              onclick="goViewAll('831-003', 'RES0220260119'); return false;">AI \xeb\xb0\x98\xeb\x8f\x84\xec\xb2\xb4 \xea\xb8\xb0\xec\x88\xa0\xea\xb0\x9c\xeb\xb0\x9c</a></strong>
            <span class="name">\xed\x99\x8d\xeb\xaf\xb8\xec\x98\x81</span><span class="date">2026-08-05</span>
          </div><p class="btn_icon fixed">
            <a href="/reportDownload.es?rpt_no=RES0220260119&amp;seq=res_0026P@6" class="btn_type">\xeb\x8b\xa4\xec\x9a\xb4\xeb\xa1\x9c\xeb\x93\x9c</a>
          </p></div>
          <p class="status" id="keywordBox1"><em class="spanCategory">\xec\x98\x88\xeb\xb9\x84\xed\x83\x80\xeb\x8b\xb9\xec\x84\xb1\xec\xa1\xb0\xec\x82\xac</em>
            <script>fncKeywordSplit('\xec\x98\xa8\xeb\x94\x94\xeb\xb0\x94\xec\x9d\xb4\xec\x8a\xa4, AI \xeb\xb0\x98\xeb\x8f\x84\xec\xb2\xb4', '#keywordBox1');</script>
          </p>
        </li></ul></div>
        """
        entries, total, pages = kistep.parse_catalog_page(html)
        self.assertEqual((total, pages), (1174, 118))
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry.record_id, "RES0220260119")
        self.assertEqual(entry.category_code, "831-003")
        self.assertEqual(entry.report_type, "예비타당성조사")
        self.assertEqual(entry.published, "2026-08-05")
        self.assertIn("AI 반도체", entry.keywords)
        self.assertEqual(
            entry.download_path,
            "/reportDownload.es?rpt_no=RES0220260119&seq=res_0026P@6",
        )

    def test_scope_keeps_china_and_strategic_technology_visible(self) -> None:
        self.assertIsNotNone(kistep, "KISTEP collector module is not implemented")
        title = "미중 기술패권 경쟁과 중국의 인공지능·반도체 전략"
        themes = kistep.classify_themes(title, "")
        self.assertIn("中国科技与国际比较", themes)
        self.assertIn("人工智能、数据与数字技术", themes)
        self.assertIn("半导体、量子与战略技术", themes)
        self.assertEqual(kistep.classify_technology_scope(title, ""), "核心科技直接材料")
        self.assertEqual(kistep.download_priority(title, ""), "P0-China-tech")

    def test_non_attachment_record_is_catalog_only(self) -> None:
        self.assertIsNotNone(kistep, "KISTEP collector module is not implemented")
        html = """
        <p class="page"><span class="total"><strong>1건</strong></span><span class="current"><strong>1</strong>/1</span></p>
        <div class="board_list"><ul><li><div class="group"><div class="item">
          <strong class="title"><a href="/reportAllDetail.es?rpt_no=R1" onclick="goViewAll('831-002', 'R1'); return false;">연구성과 확산</a></strong>
          <span class="name">author</span><span class="date">2020-01-02</span>
        </div></div><p class="status"><em class="spanCategory">성과확산</em></p></li></ul></div>
        """.encode()
        entries, _, _ = kistep.parse_catalog_page(html)
        self.assertEqual(entries[0].download_path, "")
        self.assertFalse(kistep.should_download(entries[0]))

    def test_stable_id_window_and_urls(self) -> None:
        self.assertIsNotNone(kistep, "KISTEP collector module is not implemented")
        self.assertEqual(kistep.stable_report_id("RES0220260119"), "C-KISTEP-RES0220260119")
        self.assertEqual(kistep.observation_window("2018-05-28"), "W1")
        self.assertEqual(kistep.observation_window("2020-01-01"), "W2")
        self.assertEqual(kistep.observation_window("2024-01-01"), "W3")
        self.assertEqual(
            kistep.catalog_url(3),
            "https://www.kistep.re.kr/reportAllList.es?mid=a10305010000&nPage=3",
        )

    def test_priority_rank_orders_china_before_core_and_baseline(self) -> None:
        self.assertIsNotNone(kistep, "KISTEP collector module is not implemented")
        self.assertLess(kistep.priority_rank("P0-China-tech"), kistep.priority_rank("P0-core-tech"))
        self.assertLess(kistep.priority_rank("P0-core-tech"), kistep.priority_rank("P1-global-STI"))
        self.assertLess(kistep.priority_rank("P1-global-STI"), kistep.priority_rank("P2-STI-baseline"))

    def test_existing_korean_ocr_quality_survives_catalog_rebuild(self) -> None:
        preserve = getattr(kistep, "preserve_ocr_quality", None)
        self.assertIsNotNone(preserve, "OCR preservation helper is not implemented")
        self.assertEqual(
            preserve("可检索文本", "官方PDF已保存并完成韩文OCR"),
            "韩文OCR可检索文本",
        )
        self.assertEqual(preserve("可检索文本", "官方PDF已保存并校验"), "可检索文本")


if __name__ == "__main__":
    unittest.main()
