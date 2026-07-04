import unittest
from pathlib import Path
import tempfile

from thinktank_watch.archive import build_markdown, safe_article_filename
from thinktank_watch.brief import render_daily_brief_markdown
from thinktank_watch.models import ArticleCandidate, Institution


class ArchiveAndBriefTests(unittest.TestCase):
    def test_safe_article_filename_uses_chinese_title_date_and_suffix(self):
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="AI Safety and Cyber Misuse: A Test",
            chinese_title="AI安全与网络滥用测试",
            url="https://www.rand.org/pubs/research_reports/RRA5082-1.html",
            published_date="2026-07-01",
            content_type="rand_report",
        )

        name = safe_article_filename(candidate)

        self.assertTrue(name.startswith("AI安全与网络滥用测试_2026-07-01_"))
        self.assertTrue(name.endswith(".md"))
        self.assertNotIn(":", name)

    def test_build_markdown_contains_frontmatter_and_bilingual_sections(self):
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="Supply Chain, Energy, and AI Nexus",
            chinese_title="供应链、能源与人工智能交汇",
            url="https://www.rand.org/pubs/research_reports/RRA4707-1.html",
            published_date="2026-06-25",
            content_type="rand_report",
            priority="P1",
            topic_tags=["AI治理", "科技创新"],
            keywords=["Artificial Intelligence", "Supply Chain"],
            summary="A report on AI energy supply-chain vulnerabilities.",
            chinese_summary="该报告讨论人工智能能源供应链脆弱性。",
            pdf_url="https://www.rand.org/content/dam/rand/example.pdf",
            translation_level="full_or_long",
        )

        markdown = build_markdown(candidate)

        self.assertIn("institution: RAND", markdown)
        self.assertIn("priority: P1", markdown)
        self.assertIn("# 供应链、能源与人工智能交汇", markdown)
        self.assertIn("## 中文摘要与研判", markdown)
        self.assertIn("## English Source Material", markdown)

    def test_write_article_uses_undated_directory_for_missing_dates(self):
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="ITIF",
            institution_type="think_tank",
            title="AI policy note",
            url="https://example.org/publications/2026/ai-policy-note/",
            published_date="",
            content_type="article",
            priority="P2",
        )
        from thinktank_watch.archive import write_article

        with tempfile.TemporaryDirectory() as tmp:
            path = write_article(tmp, candidate)

            self.assertEqual(Path(path).parent.name, "undated")

    def test_render_daily_brief_groups_priority_items(self):
        candidates = [
            ArticleCandidate(
                institution_slug="rand",
                institution_name="RAND",
                institution_type="think_tank",
                title="AI Safety",
                chinese_title="AI安全",
                url="https://example.org/a",
                published_date="2026-07-01",
                content_type="report",
                priority="P0",
                topic_tags=["AI治理"],
                chinese_summary="重点AI治理材料。",
            ),
            ArticleCandidate(
                institution_slug="itif",
                institution_name="ITIF",
                institution_type="think_tank",
                title="Manufacturing",
                chinese_title="制造业",
                url="https://example.org/b",
                published_date="2026-07-01",
                content_type="article",
                priority="P3",
                topic_tags=["先进制造"],
                chinese_summary="一般索引材料。",
            ),
        ]

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertIn("# 国际科技智库动态简报（2026-07-04）", brief)
        self.assertIn("P0/P1重点", brief)
        self.assertIn("AI安全", brief)
        self.assertIn("新增索引", brief)
        self.assertIn("制造业", brief)

    def test_write_daily_brief_creates_pdf_when_reportlab_is_available(self):
        try:
            import reportlab  # noqa: F401
        except ImportError:
            self.skipTest("reportlab is not installed")

        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="AI Safety",
            chinese_title="AI安全",
            url="https://example.org/a",
            published_date="2026-07-01",
            content_type="report",
            priority="P1",
            topic_tags=["AI治理"],
            chinese_summary="重点AI治理材料。",
        )
        from thinktank_watch.brief import write_daily_brief

        with tempfile.TemporaryDirectory() as tmp:
            _, _, pdf_path = write_daily_brief(tmp, "2026-07-04", [candidate])

            self.assertTrue(Path(pdf_path).exists())
            self.assertEqual(Path(pdf_path).read_bytes()[:4], b"%PDF")

    def test_write_institution_table_exports_kb_schema(self):
        from thinktank_watch.kb import write_institution_table

        institution = Institution(
            slug="rand",
            name="RAND Corporation",
            chinese_name="兰德公司",
            country_region="United States",
            institution_type="think_tank",
            priority="P0",
            batch=1,
            homepage="https://www.rand.org/",
            parser="rand",
            copyright_boundary="private_fulltext_archive",
            feeds=["https://www.rand.org/pubs/new.xml"],
            list_pages=["https://www.rand.org/pubs.html"],
            topic_pages=["https://www.rand.org/topics/artificial-intelligence.html"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_institution_table([institution], tmp)

            text = Path(path).read_text(encoding="utf-8-sig")
            self.assertIn("机构slug", text)
            self.assertIn("RAND Corporation", text)
            self.assertIn("private_fulltext_archive", text)


if __name__ == "__main__":
    unittest.main()
