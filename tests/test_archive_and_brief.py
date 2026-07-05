import unittest
import csv
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
            fetch_status="detail_ok",
        )

        markdown = build_markdown(candidate)

        self.assertIn("institution: RAND", markdown)
        self.assertIn("priority: P1", markdown)
        self.assertIn("fetch_status: detail_ok", markdown)
        self.assertIn("# 供应链、能源与人工智能交汇", markdown)
        self.assertIn("## 中文摘要与研判", markdown)
        self.assertIn("## English Source Material", markdown)

    def test_build_markdown_uses_topic_tags_as_keyword_fallback(self):
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="ITIF",
            institution_type="think_tank",
            title="AI policy note",
            chinese_title="AI政策笔记",
            url="https://example.org/publications/2026/ai-policy-note/",
            published_date="2026-07-01",
            priority="P1",
            topic_tags=["AI治理", "科技创新"],
        )

        markdown = build_markdown(candidate)

        self.assertIn('keywords: ["AI治理", "科技创新"]', markdown)
        self.assertIn("- 关键词：AI治理, 科技创新", markdown)
        self.assertIn("\npdf_url:\n", markdown)
        self.assertNotIn("pdf_url: \n", markdown)

    def test_build_markdown_uses_summary_for_summary_only_sources(self):
        candidate = ArticleCandidate(
            institution_slug="iiss",
            institution_name="IISS",
            institution_type="think_tank",
            title="Critical minerals analysis",
            chinese_title="关键矿产分析",
            url="https://example.org/critical-minerals",
            summary="Official public abstract about critical minerals and industrial strategy.",
            detail_text="Critical minerals analysis",
            source_completeness="summary_only",
        )

        markdown = build_markdown(candidate)

        english_section = markdown.split("## English Source Material", 1)[1]
        self.assertIn("Official public abstract about critical minerals and industrial strategy.", english_section)
        self.assertNotIn("\nCritical minerals analysis\n\n", english_section)

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
        self.assertIn("科技创新支撑与AI治理", brief)
        self.assertIn("AI安全", brief)
        self.assertIn("新增索引", brief)
        self.assertIn("制造业", brief)

    def test_render_daily_brief_limits_expanded_priority_items(self):
        candidates = [
            ArticleCandidate(
                institution_slug="govai",
                institution_name="GovAI",
                institution_type="think_tank",
                title=f"AI governance report {index}",
                chinese_title=f"AI治理报告{index}",
                url=f"https://example.org/{index}",
                published_date="2026-07-01",
                content_type="report",
                priority="P1",
                topic_tags=["AI治理"],
                chinese_summary=f"摘要{index}",
            )
            for index in range(1, 15)
        ]

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertEqual(brief.count("### [P1]"), 12)
        self.assertIn("### [P1] AI治理报告12", brief)
        self.assertNotIn("### [P1] AI治理报告13", brief)
        self.assertIn("- [P1] GovAI｜AI治理报告13｜https://example.org/13", brief)

    def test_render_daily_brief_keeps_large_backfill_index_visible(self):
        candidates = [
            ArticleCandidate(
                institution_slug="source",
                institution_name="Source",
                institution_type="think_tank",
                title=f"Index item {index}",
                chinese_title=f"索引条目{index}",
                url=f"https://example.org/index/{index}",
                published_date="2026-07-01",
                content_type="article",
                priority="P2",
                topic_tags=["科技治理"],
            )
            for index in range(1, 104)
        ]

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertIn("- [P2] Source｜索引条目100｜https://example.org/index/100", brief)
        self.assertNotIn("- [P2] Source｜索引条目101｜https://example.org/index/101", brief)
        self.assertIn("其余 3 条已写入私有归档和知识库索引", brief)

    def test_render_daily_brief_keeps_innovation_support_items_visible_when_priority_overflows(self):
        candidates = [
            ArticleCandidate(
                institution_slug="govai",
                institution_name="GovAI",
                institution_type="think_tank",
                title=f"AI governance report {index}",
                chinese_title=f"AI治理报告{index}",
                url=f"https://example.org/ai/{index}",
                published_date="2026-07-01",
                content_type="report",
                priority="P1",
                topic_tags=["AI治理"],
            )
            for index in range(1, 75)
        ]
        candidates.append(
            ArticleCandidate(
                institution_slug="brookings-cti",
                institution_name="Brookings CTI",
                institution_type="think_tank",
                title="NSF Engines",
                chinese_title="NSF区域创新引擎",
                url="https://example.org/nsf-engines",
                published_date="2026-05-18",
                content_type="article",
                priority="P2",
                topic_tags=["科技创新"],
            )
        )

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertIn("广义科技创新支撑", brief)
        self.assertIn("- [P2] Brookings CTI｜NSF区域创新引擎", brief)

    def test_render_daily_brief_reserves_priority_slots_for_innovation_support(self):
        candidates = [
            ArticleCandidate(
                institution_slug="govai",
                institution_name="GovAI",
                institution_type="think_tank",
                title=f"AI governance report {index}",
                chinese_title=f"AI治理报告{index}",
                url=f"https://example.org/ai/{index}",
                published_date="2026-07-01",
                content_type="report",
                priority="P0",
                score=9,
                topic_tags=["AI治理"],
            )
            for index in range(1, 15)
        ]
        candidates.append(
            ArticleCandidate(
                institution_slug="ida-stpi",
                institution_name="IDA STPI",
                institution_type="federally_funded_research_center",
                title="Innovation Support Systems",
                chinese_title="创新支撑体系",
                url="https://example.org/innovation-support",
                published_date="2026-06-20",
                content_type="report",
                priority="P1",
                score=5,
                topic_tags=["科技创新"],
            )
        )

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertEqual(brief.count("### ["), 12)
        self.assertIn("### [P1] 创新支撑体系", brief)
        self.assertIn("- 创新支撑条目：1", brief)
        self.assertIn("- 纯治理条目：14", brief)

    def test_render_daily_brief_orders_priority_items_by_priority_and_score(self):
        candidates = [
            ArticleCandidate(
                institution_slug="old",
                institution_name="Old Source",
                institution_type="think_tank",
                title="Lower score",
                chinese_title="低分条目",
                url="https://example.org/low",
                published_date="2026-07-01",
                content_type="article",
                priority="P1",
                score=5,
                topic_tags=["AI治理"],
            ),
            ArticleCandidate(
                institution_slug="cset",
                institution_name="CSET",
                institution_type="university_research_center",
                title="Higher score",
                chinese_title="高分条目",
                url="https://example.org/high",
                published_date="2026-07-02",
                content_type="report",
                priority="P0",
                score=11,
                topic_tags=["AI治理"],
            ),
        ]

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertLess(brief.index("### [P0] 高分条目"), brief.index("### [P1] 低分条目"))

    def test_render_daily_brief_prefers_innovation_support_within_same_priority(self):
        candidates = [
            ArticleCandidate(
                institution_slug="govai",
                institution_name="GovAI",
                institution_type="think_tank",
                title="High-score AI governance paper",
                chinese_title="高分AI治理论文",
                url="https://example.org/ai-governance",
                published_date="2026-07-01",
                content_type="report",
                priority="P1",
                score=10,
                topic_tags=["AI治理"],
            ),
            ArticleCandidate(
                institution_slug="nistep",
                institution_name="NISTEP",
                institution_type="government_research_institute",
                title="Science indicators and innovation capacity",
                chinese_title="科技指标与创新能力",
                url="https://example.org/innovation-capacity",
                published_date="2026-06-30",
                content_type="report",
                priority="P1",
                score=5,
                topic_tags=["科技创新"],
            ),
        ]

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertLess(brief.index("### [P1] 科技指标与创新能力"), brief.index("### [P1] 高分AI治理论文"))

    def test_render_daily_brief_treats_defense_ai_as_innovation_support(self):
        candidates = [
            ArticleCandidate(
                institution_slug="govai",
                institution_name="GovAI",
                institution_type="think_tank",
                title="AI governance",
                chinese_title="AI治理",
                url="https://example.org/ai-governance",
                published_date="2026-07-01",
                content_type="report",
                priority="P1",
                score=9,
                topic_tags=["AI治理"],
            ),
            ArticleCandidate(
                institution_slug="cset",
                institution_name="CSET",
                institution_type="university_research_center",
                title="China's Military AI Wish List",
                chinese_title="中国军方AI需求清单",
                url="https://example.org/defense-ai",
                published_date="2026-07-02",
                content_type="report",
                priority="P1",
                score=5,
                topic_tags=["国防AI", "AI治理"],
            ),
        ]

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertLess(brief.index("### [P1] 中国军方AI需求清单"), brief.index("### [P1] AI治理"))
        self.assertIn("- 创新支撑条目：1", brief)
        self.assertIn("- 纯治理条目：1", brief)
        self.assertIn("- [P1] CSET｜中国军方AI需求清单", brief)

    def test_render_daily_brief_prefers_newer_items_when_priority_and_score_match(self):
        candidates = [
            ArticleCandidate(
                institution_slug="oecd-ai",
                institution_name="OECD.AI",
                institution_type="intergovernmental",
                title="Older governance item",
                chinese_title="较旧治理材料",
                url="https://example.org/old",
                published_date="2024-12-03",
                content_type="article",
                priority="P1",
                score=5,
                topic_tags=["AI治理"],
            ),
            ArticleCandidate(
                institution_slug="oecd-ai",
                institution_name="OECD.AI",
                institution_type="intergovernmental",
                title="Newer governance item",
                chinese_title="较新治理材料",
                url="https://example.org/new",
                published_date="2026-06-30",
                content_type="article",
                priority="P1",
                score=5,
                topic_tags=["AI治理"],
            ),
        ]

        brief = render_daily_brief_markdown("2026-07-04", candidates)

        self.assertLess(brief.index("### [P1] 较新治理材料"), brief.index("### [P1] 较旧治理材料"))

    def test_load_daily_brief_candidates_uses_kb_run_date_and_archive_summaries(self):
        from thinktank_watch.archive import write_article
        from thinktank_watch.brief import load_daily_brief_candidates
        from thinktank_watch.kb import INDEX_FIELDS, INDEX_RELATIVE

        first = ArticleCandidate(
            institution_slug="cset",
            institution_name="CSET",
            institution_type="university_research_center",
            title="AI safety standard",
            chinese_title="生成式AI安全基本要求",
            url="https://cset.georgetown.edu/publication/china-gen-ai-safety-standard-final/",
            published_date="2026-05-28",
            content_type="report",
            priority="P0",
            topic_tags=["AI治理", "中国与上海相关"],
            chinese_summary="该标准材料涉及生成式AI服务安全要求。",
            fetch_status="detail_ok",
        )
        second = ArticleCandidate(
            institution_slug="itif",
            institution_name="ITIF",
            institution_type="think_tank",
            title="AI jobs",
            chinese_title="AI就业影响新证据",
            url="https://itif.org/publications/2026/06/30/ai-jobs/",
            published_date="2026-06-30",
            content_type="article",
            priority="P1",
            topic_tags=["AI治理"],
            chinese_summary="该文讨论AI对就业的实证影响。",
            fetch_status="detail_ok",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_root = root / "archive"
            kb_root = root / "kb"
            write_article(archive_root, first)
            write_article(archive_root, second)
            index_path = kb_root / INDEX_RELATIVE
            index_path.parent.mkdir(parents=True)
            with index_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=INDEX_FIELDS)
                writer.writeheader()
                writer.writerow(
                    {
                        "抓取日期": "2026-07-04",
                        "机构": first.institution_name,
                        "机构类型": first.institution_type,
                        "优先级": first.priority,
                        "主题标签": "；".join(first.topic_tags),
                        "中文题名": first.chinese_title,
                        "英文题名": first.title,
                        "发布日期": first.published_date,
                        "原始链接": first.url,
                        "PDF链接": "",
                        "翻译层级": "full_or_long",
                        "版权边界": "private_archive",
                        "抓取状态": "detail_ok",
                    }
                )
                writer.writerow(
                    {
                        "抓取日期": "2026-07-03",
                        "机构": second.institution_name,
                        "机构类型": second.institution_type,
                        "优先级": second.priority,
                        "主题标签": "；".join(second.topic_tags),
                        "中文题名": second.chinese_title,
                        "英文题名": second.title,
                        "发布日期": second.published_date,
                        "原始链接": second.url,
                        "PDF链接": "",
                        "翻译层级": "full_or_long",
                        "版权边界": "private_archive",
                        "抓取状态": "detail_ok",
                    }
                )

            candidates = load_daily_brief_candidates(archive_root, kb_root, "2026-07-04")

        self.assertEqual([item.url for item in candidates], [first.url])
        self.assertEqual(candidates[0].chinese_title, "生成式AI安全基本要求")
        self.assertEqual(candidates[0].chinese_summary, "该标准材料涉及生成式AI服务安全要求。")

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
