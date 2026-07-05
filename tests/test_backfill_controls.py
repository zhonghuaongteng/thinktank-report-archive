import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from thinktank_watch.cli import (
    backfill,
    backfill_window_start,
    balance_limited_write_queue,
    candidate_is_future,
    candidate_matches_include_terms,
    candidate_within_backfill_window,
    filter_unseen_candidates,
    include_term_matches_haystack,
    institution_fetch_limit,
    innovation_support_quota,
    priority_allows,
    run_daily,
    sort_for_writing,
    write_limit_reached,
)
from thinktank_watch.models import ArticleCandidate, Institution
from thinktank_watch.state import ArticleState


class BackfillControlTests(unittest.TestCase):
    def test_priority_allows_candidate_at_or_above_minimum(self):
        self.assertTrue(priority_allows("P0", "P1"))
        self.assertTrue(priority_allows("P1", "P1"))
        self.assertFalse(priority_allows("P2", "P1"))

    def test_write_limit_zero_means_unlimited(self):
        self.assertFalse(write_limit_reached(99, 0))
        self.assertFalse(write_limit_reached(1, None))
        self.assertTrue(write_limit_reached(3, 3))

    def test_innovation_support_quota_reserves_half_of_limited_write_batch(self):
        self.assertEqual(innovation_support_quota(0), 0)
        self.assertEqual(innovation_support_quota(None), 0)
        self.assertEqual(innovation_support_quota(1), 1)
        self.assertEqual(innovation_support_quota(8), 4)

    def test_institution_fetch_limit_honors_configured_run_limit(self):
        institution = Institution(
            slug="ecipe",
            name="ECIPE",
            chinese_name="欧洲国际政治经济中心",
            country_region="European Union",
            institution_type="think_tank",
            priority="P1",
            batch=2,
            homepage="https://ecipe.org/",
            parser="generic",
            copyright_boundary="private_archive",
            run_limit=3,
        )

        self.assertEqual(institution_fetch_limit(institution, 20), 3)
        self.assertEqual(institution_fetch_limit(institution, 2), 2)

    def test_sort_for_writing_prioritizes_priority_then_score(self):
        candidates = [
            ArticleCandidate("a", "A", "think_tank", "P3 item", "https://example.org/3", priority="P3", score=9),
            ArticleCandidate("b", "B", "think_tank", "P1 item", "https://example.org/1", priority="P1", score=4),
            ArticleCandidate("c", "C", "think_tank", "P0 item", "https://example.org/0", priority="P0", score=3),
            ArticleCandidate("d", "D", "think_tank", "P1 high", "https://example.org/1h", priority="P1", score=8),
        ]

        ordered = sort_for_writing(candidates)

        self.assertEqual([item.title for item in ordered], ["P0 item", "P1 high", "P1 item", "P3 item"])

    def test_sort_for_writing_prefers_innovation_support_within_same_priority(self):
        candidates = [
            ArticleCandidate(
                "govai",
                "GovAI",
                "think_tank",
                "High-score AI governance paper",
                "https://example.org/ai-governance",
                priority="P1",
                score=8,
                topic_tags=["AI治理"],
            ),
            ArticleCandidate(
                "nistep",
                "NISTEP",
                "government_research_institute",
                "Science indicators and innovation capacity report",
                "https://example.org/innovation-support",
                priority="P1",
                score=5,
                topic_tags=["科技创新"],
            ),
        ]

        ordered = sort_for_writing(candidates)

        self.assertEqual(
            [item.title for item in ordered],
            ["Science indicators and innovation capacity report", "High-score AI governance paper"],
        )

    def test_sort_for_writing_treats_defense_ai_as_innovation_support(self):
        candidates = [
            ArticleCandidate(
                "govai",
                "GovAI",
                "think_tank",
                "High-score AI governance paper",
                "https://example.org/ai-governance",
                priority="P1",
                score=9,
                topic_tags=["AI治理"],
            ),
            ArticleCandidate(
                "cset",
                "CSET",
                "university_research_center",
                "Military AI procurement and defense innovation",
                "https://example.org/defense-ai",
                priority="P1",
                score=5,
                topic_tags=["国防AI", "AI治理"],
            ),
        ]

        ordered = sort_for_writing(candidates)

        self.assertEqual(
            [item.title for item in ordered],
            ["Military AI procurement and defense innovation", "High-score AI governance paper"],
        )

    def test_sort_for_writing_prefers_newer_items_when_priority_and_score_match(self):
        candidates = [
            ArticleCandidate(
                "oecd-ai",
                "OECD.AI",
                "intergovernmental",
                "Older AI governance item",
                "https://example.org/old",
                published_date="2024-12-03",
                priority="P1",
                score=5,
            ),
            ArticleCandidate(
                "oecd-ai",
                "OECD.AI",
                "intergovernmental",
                "Newer AI governance item",
                "https://example.org/new",
                published_date="2026-06-30",
                priority="P1",
                score=5,
            ),
        ]

        ordered = sort_for_writing(candidates)

        self.assertEqual([item.title for item in ordered], ["Newer AI governance item", "Older AI governance item"])

    def test_limited_write_queue_reserves_innovation_support_over_pure_governance(self):
        candidates = [
            ArticleCandidate(
                "govai",
                "GovAI",
                "think_tank",
                f"Pure AI governance paper {index}",
                f"https://example.org/governance-{index}",
                priority="P0",
                score=10,
                topic_tags=["AI治理"],
            )
            for index in range(6)
        ]
        candidates.extend(
            [
                ArticleCandidate(
                    "itif",
                    "ITIF",
                    "think_tank",
                    "Research infrastructure and technology diffusion",
                    "https://example.org/innovation-1",
                    priority="P1",
                    score=5,
                    topic_tags=["科技创新"],
                ),
                ArticleCandidate(
                    "stepi",
                    "STEPI",
                    "government_research_institute",
                    "Industrial capacity and skills development",
                    "https://example.org/innovation-2",
                    priority="P1",
                    score=5,
                    topic_tags=["先进制造", "科技人才"],
                ),
            ]
        )

        ordered = balance_limited_write_queue(candidates, 4)

        self.assertEqual(
            [item.title for item in ordered[:2]],
            [
                "Research infrastructure and technology diffusion",
                "Industrial capacity and skills development",
            ],
        )
        self.assertEqual(
            sum(1 for item in ordered[:4] if set(item.topic_tags) & {"科技创新", "先进制造", "数字经济", "半导体", "科技人才", "国防AI"}),
            2,
        )

    def test_candidate_is_future_only_for_valid_later_dates(self):
        candidate = ArticleCandidate(
            "govai",
            "GovAI",
            "think_tank",
            "Future AI Act analysis",
            "https://example.org/future",
            published_date="2026-08-02",
        )

        self.assertTrue(candidate_is_future(candidate, "2026-07-05"))

        candidate.published_date = "2026-07-05"
        self.assertFalse(candidate_is_future(candidate, "2026-07-05"))

        candidate.published_date = ""
        self.assertFalse(candidate_is_future(candidate, "2026-07-05"))

    def test_backfill_window_starts_three_years_before_run_date(self):
        self.assertEqual(backfill_window_start("2026-07-05", 3).isoformat(), "2023-07-05")

    def test_candidate_within_backfill_window_requires_valid_recent_date(self):
        candidate = ArticleCandidate(
            "bruegel",
            "Bruegel",
            "think_tank",
            "Artificial intelligence competition",
            "https://example.org/recent",
            published_date="2023-07-05",
        )

        self.assertTrue(candidate_within_backfill_window(candidate, "2026-07-05", 3))

        candidate.published_date = "2023-07-04"
        self.assertFalse(candidate_within_backfill_window(candidate, "2026-07-05", 3))

        candidate.published_date = ""
        self.assertFalse(candidate_within_backfill_window(candidate, "2026-07-05", 3))

    def test_candidate_matches_include_terms_uses_title_url_and_topics(self):
        candidate = ArticleCandidate(
            "carnegie-tech",
            "Carnegie",
            "think_tank",
            "Cyberspace and Geopolitics",
            "https://example.org/research/cyberspace-geopolitics",
            summary="Global cybersecurity norm processes.",
            topic_tags=["数字经济", "科技治理"],
        )

        self.assertTrue(candidate_matches_include_terms(candidate, ["cyber"]))
        self.assertTrue(candidate_matches_include_terms(candidate, ["科技治理"]))
        self.assertFalse(candidate_matches_include_terms(candidate, ["semiconductor"]))
        self.assertTrue(candidate_matches_include_terms(candidate, []))

    def test_short_include_terms_match_word_boundaries(self):
        self.assertTrue(include_term_matches_haystack("ai", "ai governance and model evaluation"))
        self.assertFalse(include_term_matches_haystack("ai", "development aid evaluation"))
        self.assertFalse(include_term_matches_haystack("ai", "shared gains and secure links"))

    def test_filter_unseen_candidates_uses_state_dedupe(self):
        seen = ArticleCandidate(
            "aspi",
            "ASPI",
            "think_tank",
            "China military AI logistics",
            "https://example.org/seen",
            published_date="2026-07-02",
            priority="P1",
        )
        unseen = ArticleCandidate(
            "aspi",
            "ASPI",
            "think_tank",
            "DeepSeek cybersecurity agent",
            "https://example.org/unseen",
            published_date="2026-07-02",
            priority="P1",
        )

        with TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.sqlite"
            article_state = ArticleState(state)
            try:
                article_state.upsert(seen, "")
            finally:
                article_state.close()

            filtered = filter_unseen_candidates([seen, unseen], state)

        self.assertEqual(filtered, [unseen])

    def test_run_daily_skips_future_dated_candidates_without_recording_state(self):
        institution = Institution(
            slug="govai",
            name="GovAI",
            chinese_name="AI治理研究所",
            country_region="United Kingdom",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.governance.ai/",
            parser="generic",
            copyright_boundary="private_archive",
        )
        candidate = ArticleCandidate(
            institution_slug="govai",
            institution_name="GovAI",
            institution_type="think_tank",
            title="Labeling of AI Agent Activity in Article 50 of the EU AI Act",
            url="https://www.governance.ai/research-paper/labeling-of-ai-agent-activity",
            published_date="2026-08-02",
            priority="P1",
            score=8,
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "state" / "articles.sqlite"
            args = SimpleNamespace(
                date="2026-07-05",
                batch=None,
                institution=None,
                state=str(state_path),
                archive_root=str(root / "archive"),
                brief_root=str(root / "briefs"),
                skip_kb=True,
                kb_root=str(root / "kb"),
                limit=5,
                min_priority="P1",
                write_limit=0,
                refresh=False,
            )
            with (
                patch("thinktank_watch.cli._load_config", return_value=([institution], [], object())),
                patch("thinktank_watch.cli.collect_candidates", return_value=[candidate]),
                patch("thinktank_watch.cli.score_candidate", side_effect=lambda item, topics, priorities: item),
            ):
                run_daily(args)

            self.assertEqual(list((root / "archive").rglob("*.md")), [])
            conn = sqlite3.connect(state_path)
            try:
                count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
            finally:
                conn.close()

            self.assertEqual(count, 0)

    def test_backfill_skips_items_outside_three_year_window(self):
        institution = Institution(
            slug="bruegel",
            name="Bruegel",
            chinese_name="布鲁盖尔研究所",
            country_region="European Union",
            institution_type="think_tank",
            priority="P1",
            batch=2,
            homepage="https://www.bruegel.org/",
            parser="generic",
            copyright_boundary="private_archive",
        )
        recent = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="Artificial intelligence competition in Europe",
            url="https://example.org/recent-ai",
            published_date="2023-07-05",
            priority="P1",
            score=8,
            fetch_status="detail_ok",
        )
        old = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="Old AI competition report",
            url="https://example.org/old-ai",
            published_date="2023-07-04",
            priority="P1",
            score=8,
            fetch_status="detail_ok",
        )
        undated = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="Undated AI report",
            url="https://example.org/undated-ai",
            priority="P1",
            score=8,
            fetch_status="detail_ok",
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "state" / "articles.sqlite"
            args = SimpleNamespace(
                date="2026-07-05",
                batch=None,
                institution=None,
                state=str(state_path),
                archive_root=str(root / "archive"),
                brief_root=str(root / "briefs"),
                skip_kb=True,
                kb_root=str(root / "kb"),
                limit=5,
                min_priority="P1",
                write_limit=0,
                refresh=False,
                lookback_years=3,
            )
            with (
                patch("thinktank_watch.cli._load_config", return_value=([institution], [], object())),
                patch("thinktank_watch.cli.collect_candidates", return_value=[old, undated, recent]),
                patch("thinktank_watch.cli.score_candidate", side_effect=lambda item, topics, priorities: item),
            ):
                backfill(args)

            self.assertEqual(len(list((root / "archive").rglob("*.md"))), 1)
            conn = sqlite3.connect(state_path)
            try:
                rows = conn.execute("SELECT url FROM articles ORDER BY url").fetchall()
            finally:
                conn.close()

            self.assertEqual(rows, [(recent.url,)])

    def test_run_daily_records_detail_error_without_archiving(self):
        institution = Institution(
            slug="hoover-tpa",
            name="Hoover Technology Policy Accelerator",
            chinese_name="胡佛技术政策加速器",
            country_region="United States",
            institution_type="think_tank",
            priority="P1",
            batch=3,
            homepage="https://www.hoover.org/research-teams/technology-policy-accelerator",
            parser="generic",
            copyright_boundary="private_archive",
        )
        candidate = ArticleCandidate(
            institution_slug="hoover-tpa",
            institution_name="Hoover Technology Policy Accelerator",
            institution_type="think_tank",
            title="China AI external story",
            url="https://www.hoover.org/research/external-ai-story",
            priority="P1",
            score=8,
            fetch_status="detail_error:ExternalSourceError",
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "state" / "articles.sqlite"
            args = SimpleNamespace(
                date="2026-07-04",
                batch=None,
                institution=None,
                state=str(state_path),
                archive_root=str(root / "archive"),
                brief_root=str(root / "briefs"),
                skip_kb=True,
                kb_root=str(root / "kb"),
                limit=5,
                min_priority="P1",
                write_limit=0,
                refresh=False,
            )
            with (
                patch("thinktank_watch.cli._load_config", return_value=([institution], [], object())),
                patch("thinktank_watch.cli.collect_candidates", return_value=[candidate]),
                patch("thinktank_watch.cli.score_candidate", side_effect=lambda item, topics, priorities: item),
            ):
                run_daily(args)

            self.assertEqual(list((root / "archive").rglob("*.md")), [])
            conn = sqlite3.connect(state_path)
            try:
                row = conn.execute(
                    "SELECT fetch_status, archive_path FROM articles WHERE url = ?",
                    (candidate.url,),
                ).fetchone()
            finally:
                conn.close()

            self.assertEqual(row, ("detail_error:ExternalSourceError", ""))


if __name__ == "__main__":
    unittest.main()
