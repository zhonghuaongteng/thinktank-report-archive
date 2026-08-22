import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from pypdf import PdfWriter

from scripts.extract_viewpoint_pdf_slices import clean
from scripts.validate_viewpoint_research import expected_catalog_size


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

try:
    import extend_viewpoint_stepi_korean as stepi
except ModuleNotFoundError:
    stepi = None


class StepiKoreanCollectionTests(unittest.TestCase):
    def test_expected_catalog_size_accepts_stepi_korean_tranche(self) -> None:
        self.assertEqual(
            expected_catalog_size(49, 105, 47, 104, 95, 29, 89, 40, 88, 192, 283, stepi_asset_count=518),
            1639,
        )

    def test_pdf_text_clean_removes_unencodable_surrogates(self) -> None:
        value = clean("정책\udfb3연구")
        value.encode("utf-8")
        self.assertNotIn("\udfb3", value)

    def test_catalog_page_parses_formal_report_and_pdf_identity(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")

        html = """
        <div class="boardTop"><span>총 <b>26</b>건</span><span><b>1/3</b> 페이지</span></div>
        <table class="list"><tbody><tr>
          <td>4166</td>
          <td class="title"><a href="View.do?reIdx=1420&amp;pageIndex=1">국가전략기술 확보를 위한 연구</a></td>
          <td>박찬수</td><td>2026-06-30</td>
          <td class="file"><a class="btnFile pdf" data-type="report" data-idx="1420"
            data-file="abc-1420.pdf" data-cate="A0201">pdf</a></td><td>9</td>
        </tr></tbody></table>
        """.encode()
        entries, total, pages = stepi.parse_catalog_page(html, "A0201")
        self.assertEqual((total, pages), (26, 3))
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry.record_id, "1420")
        self.assertEqual(entry.category_code, "A0201")
        self.assertEqual(entry.report_type, "정책연구")
        self.assertEqual(entry.title_ko, "국가전략기술 확보를 위한 연구")
        self.assertEqual(entry.author, "박찬수")
        self.assertEqual(entry.published, "2026-06-30")
        self.assertEqual(entry.pdf_filename, "abc-1420.pdf")

    def test_download_url_preserves_official_file_and_category(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")

        entry = stepi.Entry("1420", "A0201", "정책연구", "title", "author", "2026-06-30", "abc-1420.pdf")
        self.assertEqual(
            stepi.download_url(entry),
            "https://www.stepi.re.kr/common/report/Download.do?reIdx=1420&streFileNm=abc-1420.pdf&cateCont=A0201&purpose=&jobGroup=",
        )

    def test_formal_categories_preserve_institutional_report_roles(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")

        expected = {
            "A0201": "정책연구",
            "A0203": "조사연구",
            "A0202": "정책자료",
            "A0204": "기타연구",
        }
        self.assertEqual(stepi.FORMAL_CATEGORIES, expected)
        self.assertTrue(all(stepi.report_role(code) == "机构正式研究" for code in expected))

    def test_scope_and_themes_keep_china_and_core_technology_visible(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")

        title = "중국의 인공지능·반도체 기술패권 전략"
        self.assertEqual(stepi.classify_technology_scope(title), "核心科技直接材料")
        themes = stepi.classify_themes(title, "")
        self.assertIn("中国科技与国际比较", themes)
        self.assertIn("人工智能、数据与数字技术", themes)
        self.assertIn("半导体、量子与战略技术", themes)

    def test_text_quality_separates_image_pdf_from_searchable_text(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        classify = getattr(stepi, "classify_text_quality", None)
        self.assertIsNotNone(classify, "text quality classifier is not implemented")
        self.assertEqual(classify(199, 8, True), "图像型PDF，OCR待补")
        self.assertEqual(classify(1600, 8, True), "可检索文本")
        self.assertEqual(classify(0, 0, False), "官方目录无PDF正文")

    def test_existing_korean_ocr_quality_survives_catalog_rebuild(self) -> None:
        preserve = getattr(stepi, "preserve_ocr_quality", None)
        self.assertIsNotNone(preserve, "OCR preservation helper is not implemented")
        self.assertEqual(
            preserve("可检索文本", "官方PDF已保存并完成韩文OCR"),
            "韩文OCR可检索文本",
        )
        self.assertEqual(preserve("可检索文本", "官方PDF已保存并校验"), "可检索文本")

    def test_observation_window_and_id_are_stable(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")

        self.assertEqual(stepi.observation_window("2018-04-01"), "W1")
        self.assertEqual(stepi.observation_window("2021-12-31"), "W2")
        self.assertEqual(stepi.observation_window("2026-06-30"), "W3")
        self.assertEqual(stepi.stable_report_id("A0201", "1420"), "C-STEPI-A0201-1420")

    def test_catalog_url_keeps_year_category_and_page(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        builder = getattr(stepi, "catalog_url", lambda *_args: "")
        self.assertEqual(
            builder(2025, "A0201", 2),
            "https://www.stepi.re.kr/site/stepiko/report/List.do?cbIdx=1292&searchYear=2025&cateCont=A0201&pageIndex=2",
        )

    def test_collect_catalog_walks_pages_and_deduplicates_records(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        builder = getattr(stepi, "catalog_url", None)
        self.assertIsNotNone(builder, "catalog URL builder is not implemented")
        collector = getattr(stepi, "collect_catalog", lambda *_args, **_kwargs: [])

        def page(record_id: str, current: int, pages: int) -> bytes:
            return f"""
            <div class="boardTop"><span>총 <b>{pages * 10}</b>건</span><span><b>{current}/{pages}</b> 페이지</span></div>
            <table class="list"><tbody><tr>
              <td>1</td><td class="title"><a href="View.do?reIdx={record_id}">title {record_id}</a></td>
              <td>author</td><td>2025-01-01</td>
              <td class="file"><a class="btnFile pdf" data-file="{record_id}.pdf" data-cate="A0201">pdf</a></td><td>1</td>
            </tr></tbody></table>
            """.encode()

        pages = {
            builder(2025, "A0201", 1): page("10", 1, 2),
            builder(2025, "A0201", 2): page("11", 2, 2),
            builder(2025, "A0203", 1): page("10", 1, 1),
        }

        def fetcher(url: str, timeout: int = 60):
            return pages[url], url, "text/html"

        rows = collector(years=[2025], categories=["A0201", "A0203"], fetcher=fetcher)
        self.assertEqual([row.record_id for row in rows], ["10", "11"])

    def test_fetch_official_pdf_accepts_parseable_pdf(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        fetch_pdf = getattr(stepi, "fetch_official_pdf", None)
        self.assertIsNotNone(fetch_pdf, "official PDF fetcher is not implemented")
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        stream = BytesIO()
        writer.write(stream)
        payload = stream.getvalue()
        entry = stepi.Entry("10", "A0201", "정책연구", "title", "author", "2025-01-01", "10.pdf")

        def fetcher(url: str, referer: str = "", timeout: int = 180):
            return payload, url, "application/pdf"

        data, pages = fetch_pdf(entry, fetcher=fetcher)
        self.assertEqual(data, payload)
        self.assertEqual(pages, 1)

    def test_fetch_official_pdf_rejects_html_disguised_as_download(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        fetch_pdf = getattr(stepi, "fetch_official_pdf", None)
        self.assertIsNotNone(fetch_pdf, "official PDF fetcher is not implemented")
        entry = stepi.Entry("10", "A0201", "정책연구", "title", "author", "2025-01-01", "10.pdf")

        def fetcher(url: str, referer: str = "", timeout: int = 180):
            return b"<html>survey</html>", url, "text/html"

        with self.assertRaises(ValueError):
            fetch_pdf(entry, fetcher=fetcher)

    def test_local_pdf_discovery_supports_interrupted_run_resume(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        discover = getattr(stepi, "discover_local_assets", None)
        self.assertIsNotNone(discover, "local asset resume discovery is not implemented")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wanted = root / "C-STEPI-A0201-10.pdf"
            ignored = root / "C-NISTEP-NR1.pdf"
            wanted.write_bytes(b"%PDF-local")
            ignored.write_bytes(b"%PDF-other")
            rows = discover(root)
        self.assertEqual(list(rows), ["C-STEPI-A0201-10"])
        self.assertEqual(rows["C-STEPI-A0201-10"]["本地原始资产路径"], str(wanted))

    def test_acquire_reuses_valid_persistent_cache_without_network(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        stream = BytesIO()
        writer.write(stream)
        entry = stepi.Entry("10", "A0201", "정책연구", "title", "author", "2025-01-01", "10.pdf")
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            (cache_dir / "C-STEPI-A0201-10.pdf").write_bytes(stream.getvalue())
            with patch.object(stepi, "fetch_official_pdf", side_effect=AssertionError("network called")):
                result = stepi.acquire(entry, cache_dir)
        self.assertEqual(result.status, "官方PDF已保存并校验")
        self.assertEqual(result.pages, 1)

    def test_existing_pdf_resume_builds_missing_text_and_slice(self) -> None:
        self.assertIsNotNone(stepi, "STEPI collector module is not implemented")
        ensure = getattr(stepi, "ensure_pdf_derivatives", None)
        self.assertIsNotNone(ensure, "PDF derivative resume helper is not implemented")
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pdf_dir, text_dir, slice_dir = root / "pdf", root / "text", root / "slice"
            for directory in (pdf_dir, text_dir, slice_dir):
                directory.mkdir()
            pdf_path = pdf_dir / "C-STEPI-A0201-10.pdf"
            with pdf_path.open("wb") as handle:
                writer.write(handle)
            ensure(pdf_path, {"text": text_dir, "slice": slice_dir})
            self.assertTrue((text_dir / "C-STEPI-A0201-10.txt").exists())
            self.assertTrue((slice_dir / "C-STEPI-A0201-10.md").exists())


if __name__ == "__main__":
    unittest.main()
