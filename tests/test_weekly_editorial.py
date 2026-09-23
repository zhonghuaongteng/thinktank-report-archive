import base64
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from thinktank_watch.brief import (
    _find_headless_browser, _weekly_pdf_toc_entry_lines, inspect_weekly_comic_report,
    render_weekly_magazine_html, render_weekly_reader_markdown, weekly_thin_core_items, write_periodic_brief,
)
from thinktank_watch.cli import check_weekly_comics
from thinktank_watch.editorial import (
    inspect_weekly_editorial, load_weekly_editorial, validate_weekly_editorial,
    weekly_editorial_path,
)
from thinktank_watch.models import ArticleCandidate


DATE = "2000-01-01"


def articles():
    return [ArticleCandidate(
        "example", "Example", "think_tank", "Enterprise investment", "https://example.org/report",
        chinese_title="企业投资研究", priority="P1", topic_tags=["经济与企业创新"],
        chinese_summary="核心观点：企业持续研发需要稳定条件。调查显示投入与短期经济周期并不同步。",
    )]


def editorial():
    return {
        "date": DATE,
        "headline": "编辑明确撰写的本期判断",
        "lead": "这段导读基于已经核对的研究材料，不由议题数量生成。",
        "discoveries": [{
            "title": "企业投入的具体发现",
            "text": "完整解释研究所呈现的机制与证据限制。",
            "source_url": "https://example.org/report.pdf",
            "source_locator": "第12页，表3",
            "article_url": articles()[0].url,
            "metric": "12%", "metric_label": "示例指标，仅供测试",
        }],
        "connections": [{
            "title": "与企业基础研究问题的连接",
            "text": "明确说明可参考的机制与尚不能推断的边界。",
            "article_urls": [articles()[0].url],
        }],
        "review": {"completed": True, "note": "本轮已核对原文、数字、研究连接及表述边界。"},
    }


def save_editorial(root, value=None):
    path = weekly_editorial_path(root, DATE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value if value is not None else editorial(), ensure_ascii=False), encoding="utf-8")
    return path


class WeeklyEditorialTests(unittest.TestCase):
    def test_explicit_content_is_complete_and_navigation_uses_real_anchors(self):
        document = editorial()
        document["lead"] += "保留完整句子。" * 70 + "导读终点。"
        html = render_weekly_magazine_html(DATE, articles(), editorial=document)
        markdown = render_weekly_reader_markdown(DATE, articles(), editorial=document)
        soup = BeautifulSoup(html, "html.parser")
        self.assertIn(document["lead"], soup.get_text())
        self.assertIn(document["lead"], markdown)
        self.assertEqual(len(soup.select(".issue-opening")), 1)
        self.assertFalse(soup.select(".pagebreak, .top-reads-page, .viewpoints"))
        self.assertEqual(len(soup.select(".editorial-discovery")), 1)
        for link in soup.select('.issue-opening a[href^="#"]'):
            self.assertIsNotNone(soup.select_one(link["href"]))
        self.assertNotIn("本周态势", soup.get_text())
        self.assertNotIn("P.05", html)

    def test_empty_connections_do_not_create_an_empty_section_or_filler(self):
        document = editorial()
        document["connections"] = []
        html = render_weekly_magazine_html(DATE, articles(), editorial=document)
        markdown = render_weekly_reader_markdown(DATE, articles(), editorial=document)
        self.assertNotIn("与研究关注的连接", html)
        self.assertNotIn("与研究关注的连接", markdown)

    def test_missing_editorial_preview_is_honest_and_has_only_one_navigation(self):
        html = render_weekly_magazine_html(DATE, articles())
        self.assertIn("首页编选待完成", html)
        self.assertNotIn("本周形成", html)
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(len(soup.select(".reading-navigation")), 1)
        self.assertFalse(soup.select(".editorial-lead, .editorial-discovery"))

    def test_opening_shows_inclusive_seven_day_window_and_honest_empty_issue(self):
        for rendered in (render_weekly_magazine_html(DATE, []), render_weekly_reader_markdown(DATE, [])):
            self.assertIn("1999-12-26 至 2000-01-01", rendered)
            self.assertIn("本期没有 P0/P1 重点条目", rendered)
            self.assertNotIn("首页编选待完成", rendered)

    def test_date_links_and_review_are_validated_without_inventing_destinations(self):
        mutations = [
            lambda d: d.update(date="2026-09-13"),
            lambda d: d["discoveries"][0].update(article_url="https://example.org/unknown"),
            lambda d: d["discoveries"][0].update(source_url="javascript:alert(1)"),
            lambda d: d["connections"][0].update(article_urls=["https://example.org/unknown"]),
            lambda d: d["review"].update(completed="true"),
            lambda d: d["review"].update(note=""),
        ]
        for mutate in mutations:
            document = editorial()
            mutate(document)
            with self.subTest(document=document), self.assertRaises(ValueError):
                validate_weekly_editorial(document, DATE, articles(), require_review=True)
        nonpriority = articles()
        nonpriority[0].priority = "P2"
        with self.assertRaisesRegex(ValueError, "P0/P1"):
            validate_weekly_editorial(editorial(), DATE, nonpriority)
        draft = editorial()
        del draft["review"]
        self.assertIs(validate_weekly_editorial(draft, DATE, articles()), draft)

    def test_file_loading_uses_supplied_brief_root_and_invalid_input_prevents_writes(self):
        with TemporaryDirectory() as temp:
            self.assertIsNone(load_weekly_editorial(temp, DATE, articles()))
            path = save_editorial(temp)
            self.assertEqual(load_weekly_editorial(temp, DATE, articles()), editorial())
            path.write_text('{"date": "2026-09-13"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                write_periodic_brief(temp, DATE, articles(), cadence="weekly")
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_final_gate_requires_file_review_and_current_rendered_inputs(self):
        with TemporaryDirectory() as temp:
            self.assertIn("missing", inspect_weekly_editorial(temp, DATE, articles(), "")[0])
            self.assertEqual(inspect_weekly_editorial(temp, DATE, [], ""), [])
            draft = editorial()
            draft["review"]["completed"] = False
            path = save_editorial(temp, draft)
            self.assertIn("review", inspect_weekly_editorial(temp, DATE, articles(), "")[0])
            save_editorial(temp)
            html = render_weekly_magazine_html(DATE, articles(), editorial=editorial())
            self.assertEqual(inspect_weekly_editorial(temp, DATE, articles(), html), [])
            self.assertIn("does not match", inspect_weekly_editorial(temp, DATE, articles(), "old html")[0])
            stem = f"{DATE}_国际科技智库周报"
            md_path = path.parent / f"{stem}.md"
            md_path.write_text("old markdown", encoding="utf-8")
            self.assertIn("Markdown", inspect_weekly_editorial(temp, DATE, articles(), html)[0])
            md_path.write_text(render_weekly_reader_markdown(DATE, articles(), editorial=editorial()), encoding="utf-8")
            pdf_path = path.parent / f"{stem}.pdf"
            pdf_path.touch()
            os.utime(pdf_path, ns=(1, 1))
            self.assertIn("older", inspect_weekly_editorial(temp, DATE, articles(), html)[0])

    def test_cli_reports_editorial_gate_failures_without_crashing(self):
        args = SimpleNamespace(date=DATE, archive_root="unused", lookback_days=7, brief_root="unused", comic_root="unused")
        stats = dict(priority_count=1, prompt_count=1, comic_count=1, md_image_refs=1,
                     html_image_nodes=1, pdf_image_count=1, missing_files=[], blocked_hits=[],
                     editorial_failures=["Editorial content review has not been recorded"])
        with patch("thinktank_watch.cli.load_weekly_archive_candidates", return_value=articles()), patch("thinktank_watch.cli.inspect_weekly_comic_report", return_value=stats):
            self.assertEqual(check_weekly_comics(args), 1)

    def test_changed_archive_content_or_revoked_excerpt_permission_invalidates_old_output(self):
        with TemporaryDirectory() as temp:
            save_editorial(temp)
            items = articles()
            html = render_weekly_magazine_html(DATE, items, editorial=editorial())
            items[0].chinese_summary += "新增核对后的重要内容。"
            self.assertIn("does not match", inspect_weekly_editorial(temp, DATE, items, html)[0])
            items[0].highlights_markdown = "需要许可的原文选编。"
            items[0].highlights_usage = "licensed_excerpt"
            self.assertIn("permission", inspect_weekly_editorial(temp, DATE, items, html)[0])

    def test_local_editorial_charts_are_embedded_and_counted_separately_from_comics(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            image = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==")
            (root / "chart.png").write_bytes(image)
            document = editorial()
            document["data_markdown"] = "![图表说明](chart.png)\n\n来源：报告第12页；许可：测试自制图。"
            with patch("thinktank_watch.highlights.Path.cwd", return_value=root):
                html = render_weekly_magazine_html(DATE, articles(), editorial=document)
            soup = BeautifulSoup(html, "html.parser")
            source = soup.select_one(".selected-chart img")["src"]
            self.assertEqual(base64.b64decode(source.split(",", 1)[1]), image)
            self.assertFalse(soup.select("figure.comic"))
            path = save_editorial(temp, document)
            (path.parent / f"{DATE}_国际科技智库周报.html").write_text(html, encoding="utf-8")
            stats = inspect_weekly_comic_report(DATE, articles(), temp, root / "comics")
            self.assertEqual(stats["selected_chart_count"], 1)
            self.assertEqual(stats["html_image_nodes"], 0)
            document["data_markdown"] = "![外部图](https://example.org/chart.png)"
            with self.assertRaises(ValueError):
                render_weekly_magazine_html(DATE, articles(), editorial=document)

    def test_browser_failure_cannot_fallback_and_lose_editorial(self):
        with TemporaryDirectory() as temp, patch("thinktank_watch.brief.write_pdf_from_html", return_value=False), patch("thinktank_watch.brief.write_weekly_reader_pdf") as fallback:
            save_editorial(temp)
            with self.assertRaisesRegex(RuntimeError, "editorial"):
                write_periodic_brief(temp, DATE, articles(), cadence="weekly")
            fallback.assert_not_called()

    def test_legacy_pdf_navigation_no_longer_prints_estimated_page_numbers(self):
        lines = _weekly_pdf_toc_entry_lines(1, articles()[0], 999)
        self.assertNotIn("999", "".join(lines))
        self.assertIn("主题 01", "".join(lines))

    @unittest.skipUnless(_find_headless_browser(), "A local Chromium browser is required")
    def test_actual_pdf_contains_editorial_without_four_fixed_front_pages(self):
        from pypdf import PdfReader

        with TemporaryDirectory() as temp:
            document = editorial()
            save_editorial(temp, document)
            md, html, pdf = write_periodic_brief(temp, DATE, articles(), cadence="weekly")
            reader = PdfReader(pdf)
            self.assertIn("Skia", reader.metadata.producer)
            self.assertLess(len(reader.pages), 5)
            text = "".join(page.extract_text() or "" for page in reader.pages)
            text = "".join(text.split())
            self.assertIn("".join(document["headline"].split()), text)
            self.assertIn("".join(document["discoveries"][0]["title"].split()), text)
            self.assertIn("".join(document["connections"][0]["title"].split()), text)
            self.assertEqual(inspect_weekly_editorial(temp, DATE, articles(), html.read_text(encoding="utf-8")), [])

    def test_short_readable_guide_with_substantive_selections_is_not_rejected_as_thin(self):
        item = articles()[0]
        item.chinese_summary = "核心观点：企业研究投入受组织条件影响。"
        item.highlights_markdown = "## 完整选编\n\n" + "企业研究投入受组织条件影响，跨期研究需要持续投入和稳定协作。" * 7
        self.assertEqual(weekly_thin_core_items([item]), [])
        item.highlights_markdown = "仅有一句短文。"
        self.assertEqual(weekly_thin_core_items([item]), [item])
        item.highlights_markdown = ""  # Historical cards retain their existing thin-core check.
        self.assertEqual(weekly_thin_core_items([item]), [item])
        item.highlights_markdown = "企业研究投入受组织条件影响，跨期研究需要持续投入和稳定协作。" * 7
        item.chinese_summary = "核心观点：This is an untranslated extraction with no readable Chinese guide."
        self.assertEqual(weekly_thin_core_items([item]), [item])


if __name__ == "__main__":
    unittest.main()
