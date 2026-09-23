import base64
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from bs4 import BeautifulSoup

from thinktank_watch.archive import build_markdown
from thinktank_watch.brief import (
    MAGAZINE_CSS, _find_headless_browser, _magazine_topic_card_html,
    render_weekly_reader_markdown, write_pdf_from_html, write_periodic_brief,
    weekly_chapter_name,
)
from thinktank_watch.cli import check_weekly_comics
from thinktank_watch.highlights import render_highlights_markdown
from thinktank_watch.models import ArticleCandidate
from thinktank_watch.restore import parse_archive_markdown


def candidate(**kwargs):
    return ArticleCandidate(
        "example", "Example", "think_tank", "Authored report", "https://example.org/report",
        chinese_title="研究报告", priority="P1", topic_tags=["科技创新"],
        chinese_summary="核心观点：核心判断是企业研究能力取决于持续投入。原研究卡次级正文不应重复。建议：原建议只在兼容模式展示。",
        **kwargs,
    )


class HighlightsTests(unittest.TestCase):
    def test_archive_roundtrip_preserves_selection_headings_and_layout_choice(self):
        text = "## 一个实质发现\n\n较完整的研究发现。\n\n## 第二个发现\n\n来源：报告第12页。"
        item = candidate(highlights_markdown=text, highlights_title="企业进入与退出", highlights_start_new_page=True)
        with TemporaryDirectory() as temp:
            path = Path(temp) / "report.md"
            path.write_text(build_markdown(item), encoding="utf-8")
            restored = parse_archive_markdown(path)
        self.assertEqual(restored.highlights_markdown, text)
        self.assertEqual(restored.highlights_title, "企业进入与退出")
        self.assertTrue(restored.highlights_start_new_page)
        self.assertNotIn("一个实质发现", restored.chinese_summary)

    def test_authored_selection_replaces_legacy_body_without_truncation(self):
        authored = "### 企业生命周期\n\n" + "较完整的研究解释，" * 160 + "选编结尾。"
        item = candidate(highlights_markdown=authored, highlights_title="企业动态的三个发现")
        html = _magazine_topic_card_html("2026-09-20", 1, 1, item)
        md = render_weekly_reader_markdown("2026-09-20", [item])
        self.assertIn("核心判断是企业研究能力取决于持续投入", html)
        self.assertIn("选编结尾。", html)
        self.assertIn(authored, md)
        self.assertEqual(html.count("原研究卡次级正文不应重复"), 1)
        self.assertNotIn("原建议只在兼容模式展示", html)
        self.assertNotIn('class="topic-card topic-analysis highlights-selection selection-new-page"', html)
        self.assertNotIn("论证与依据", html)

    def test_explicit_page_start_only_applies_when_selection_exists(self):
        item = candidate(highlights_start_new_page=True)
        html = _magazine_topic_card_html("2026-09-20", 1, 1, item)
        self.assertNotIn("selection-new-page", html)
        self.assertIn("原研究卡次级正文不应重复", html)
        item.highlights_markdown = "完整且已经撰写的精华选编。"
        self.assertIn("selection-new-page", _magazine_topic_card_html("2026-09-20", 1, 1, item))

    def test_tables_lists_local_chart_and_source_page_are_preserved(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "chart.png").write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg=="))
            md = """### 主要发现

这是**完整段落**，用于解释数据。

- 企业进入
- 企业退出

1. 先说明范围
2. 再解释变化

| 指标 | 结果 |
| --- | ---: |
| 企业数 | 123 |

![图1：企业退出结构](chart.png)

来源：[原报告](https://example.org/report)，第12页，图3；许可：作者授权本地摘编。

<script>alert('unsafe')</script>
[危险链接](javascript:alert)
"""
            html = render_highlights_markdown(md, root)
            soup = BeautifulSoup(html, "html.parser")
            self.assertEqual(len(soup.select("table tbody tr")), 1)
            self.assertEqual(len(soup.select("ul li")), 2)
            self.assertEqual(len(soup.select("ol li")), 2)
            image_src = soup.select_one("figure.selected-chart img")["src"]
            self.assertTrue(image_src.startswith("data:image/png;base64,"))
            self.assertEqual(base64.b64decode(image_src.split(",", 1)[1]), (root / "chart.png").read_bytes())
            self.assertNotIn(root.as_uri(), html)
            self.assertIn("第12页，图3", soup.get_text())
            self.assertIn("作者授权本地摘编", soup.get_text())
            self.assertFalse(soup.select("script"))
            self.assertEqual([a["href"] for a in soup.select("a")], ["https://example.org/report"])

    def test_chart_rejects_remote_outside_and_active_content_paths(self):
        with TemporaryDirectory() as temp:
            for path in ("https://example.org/chart.png", "../outside.png", "file:///tmp/chart.png", "//host/chart.png", "chart.svg", "missing.png"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    render_highlights_markdown(f"![图]({path})", temp)

    def test_metadata_only_source_keeps_editorial_analysis_without_archiving_source_fulltext(self):
        authored = "基于公开摘要和数据另行撰写的中文分析与编译。"
        item = candidate(highlights_markdown=authored, copyright_boundary="metadata_summary_only",
                         source_completeness="full_text", detail_text="RESTRICTED_SOURCE_FULLTEXT", summary="PUBLIC_ABSTRACT")
        archived = build_markdown(item)
        self.assertIn(authored, archived)
        self.assertIn("PUBLIC_ABSTRACT", archived)
        self.assertNotIn("RESTRICTED_SOURCE_FULLTEXT", archived)
        self.assertIn(authored, _magazine_topic_card_html("2026-09-20", 1, 1, item))
        self.assertEqual(item.detail_text, "RESTRICTED_SOURCE_FULLTEXT")
        with TemporaryDirectory() as temp:
            path = Path(temp) / "report.md"
            path.write_text(archived, encoding="utf-8")
            restored = parse_archive_markdown(path)
        self.assertEqual(restored.highlights_markdown, authored)
        self.assertEqual(restored.highlights_usage, "editorial")

    def test_excerpts_require_recorded_permission_basis_and_never_silently_disappear(self):
        for usage, verified, note in (("licensed_excerpt", False, ""), ("licensed_excerpt", True, ""), ("full_translation", True, "unclear")):
            item = candidate(highlights_markdown="RESTRICTED_EXCERPT", highlights_usage=usage,
                             highlights_permission_verified=verified, highlights_permission_note=note,
                             copyright_boundary="metadata_summary_only")
            with self.subTest(usage=usage, verified=verified):
                with self.assertRaisesRegex(ValueError, "permission"):
                    build_markdown(item)
                with self.assertRaisesRegex(ValueError, "permission"):
                    _magazine_topic_card_html("2026-09-20", 1, 1, item)
        item.highlights_usage = "licensed_excerpt"
        item.highlights_permission_note = "原报告第2页明确许可本地引用；已核验适用范围。"
        with TemporaryDirectory() as temp:
            path = Path(temp) / "report.md"
            path.write_text(build_markdown(item), encoding="utf-8")
            restored = parse_archive_markdown(path)
        self.assertEqual(restored.highlights_usage, "licensed_excerpt")
        self.assertTrue(restored.highlights_permission_verified)
        self.assertEqual(restored.highlights_permission_note, item.highlights_permission_note)
        self.assertIn("RESTRICTED_EXCERPT", _magazine_topic_card_html("2026-09-20", 1, 1, restored))

    def test_reference_style_source_links_resolve_without_unsafe_protocols(self):
        markdown = '''来源：[PDF第1页][pdf1]、[公开网页][]。

[恶意链接][bad]

[pdf1]: https://example.org/report.pdf
[公开网页]: <https://example.org/page> "说明"
[bad]: javascript:alert

```
[literal]: https://example.org/inside-code
```
'''
        soup = BeautifulSoup(render_highlights_markdown(markdown), "html.parser")
        self.assertEqual([a["href"] for a in soup.select("a")], ["https://example.org/report.pdf", "https://example.org/page"])
        self.assertNotIn("[PDF第1页][pdf1]", soup.get_text())
        self.assertNotIn("[pdf1]:", soup.get_text())
        self.assertIn("[literal]:", soup.select_one("pre").get_text())

    def test_authored_guide_preserves_all_sentences_and_does_not_derive_from_selection(self):
        item = candidate(highlights_markdown="精华正文独立事实。")
        guide = "第一句判断。第二句重要限定。第三句完整结论。"
        item.chinese_summary = f"核心观点：{guide}\n建议：另一个旧字段。"
        html = _magazine_topic_card_html("2026-09-20", 1, 1, item)
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(soup.select_one(".judgment-box p").get_text(), guide)
        self.assertEqual(soup.select_one(".judgment-box .label").get_text(), "摘要导读")
        self.assertIn(guide, render_weekly_reader_markdown("2026-09-20", [item]))
        self.assertNotIn("另一个旧字段", html)

    def test_next_page_guide_lists_real_headings_only_and_has_working_anchors(self):
        item = candidate(highlights_markdown="## 企业退出\n\n内容。\n\n```\n## 代码中标题\n```\n\n## 行业差异\n\n内容。")
        html = _magazine_topic_card_html("2026-09-20", 1, 1, item)
        self.assertNotIn('class="highlights-map"', html)
        item.highlights_start_new_page = True
        soup = BeautifulSoup(_magazine_topic_card_html("2026-09-20", 1, 1, item), "html.parser")
        self.assertTrue(soup.select_one(".topic-primary.selection-on-next-page"))
        links = soup.select(".highlights-map a")
        self.assertEqual([a.get_text() for a in links], ["企业退出", "行业差异"])
        for link in links:
            self.assertEqual(soup.select_one(link["href"]).get_text(), link.get_text())
        item.highlights_markdown = "仅有连续正文。"
        self.assertNotIn('class="highlights-map"', _magazine_topic_card_html("2026-09-20", 1, 1, item))

    def test_enterprise_economics_has_a_named_chapter(self):
        item = candidate()
        item.topic_tags = ["经济与企业创新", "科技创新"]
        self.assertEqual(weekly_chapter_name(item), "经济与企业创新")

    def test_browser_failure_cannot_silently_drop_selections_via_legacy_pdf(self):
        with TemporaryDirectory() as temp, patch("thinktank_watch.brief.write_pdf_from_html", return_value=False), patch("thinktank_watch.brief.write_weekly_reader_pdf") as fallback:
            with self.assertRaisesRegex(RuntimeError, "authored selections"):
                write_periodic_brief(temp, "2026-09-20", [candidate(highlights_markdown="完整精华正文。")], cadence="weekly")
            fallback.assert_not_called()

    def test_selected_charts_do_not_mask_missing_pdf_comics(self):
        stats = dict(priority_count=1, prompt_count=1, comic_count=1, md_image_refs=1,
                     html_image_nodes=1, selected_chart_count=1, pdf_image_count=1,
                     missing_files=[], blocked_hits=[])
        args = SimpleNamespace(date="2026-09-20", archive_root="unused", lookback_days=7,
                               brief_root="unused", comic_root="unused")
        with patch("thinktank_watch.cli.load_weekly_archive_candidates", return_value=[]), patch("thinktank_watch.cli.inspect_weekly_comic_report", return_value=stats):
            self.assertEqual(check_weekly_comics(args), 1)
            stats["pdf_image_count"] = 2
            self.assertEqual(check_weekly_comics(args), 0)

    @unittest.skipUnless(_find_headless_browser(), "A local Chromium browser is required for PDF pagination verification")
    def test_browser_keeps_long_selections_complete_and_page_start_is_optional(self):
        from pypdf import PdfReader

        long_text = "\n\n".join(
            f"段落{index}：" + "这是用于验证完整分页的测试段落，保留作者已经撰写的全部内容。" * 18
            + f" END_BLOCK_{index}" for index in range(1, 10)
        )
        with TemporaryDirectory() as temp:
            for new_page in (False, True):
                with self.subTest(new_page=new_page):
                    item = candidate(highlights_markdown=long_text, highlights_title="SELECTION_START", highlights_start_new_page=new_page)
                    html = Path(temp) / f"selection-{new_page}.html"
                    pdf = html.with_suffix(".pdf")
                    html.write_text('<html><head><meta charset="utf-8"><style>' + MAGAZINE_CSS
                                    + '</style></head><body><main>'
                                    + _magazine_topic_card_html("2000-01-01", 1, 1, item)
                                    + '</main></body></html>', encoding="utf-8")
                    self.assertTrue(write_pdf_from_html(html, pdf))
                    reader = PdfReader(pdf)
                    self.assertIn("Skia", reader.metadata.producer)
                    pages = [page.extract_text() or "" for page in reader.pages]
                    all_text = "".join(pages)
                    for index in range(1, 10):
                        self.assertIn(f"END_BLOCK_{index}", all_text)
                    selection_page = next(index for index, text in enumerate(pages) if "SELECTION_START" in text)
                    self.assertEqual(selection_page, 1 if new_page else 0)


if __name__ == "__main__":
    unittest.main()
