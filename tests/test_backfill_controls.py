import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from thinktank_watch.cli import institution_fetch_limit, priority_allows, run_daily, sort_for_writing, write_limit_reached
from thinktank_watch.models import ArticleCandidate, Institution


class BackfillControlTests(unittest.TestCase):
    def test_priority_allows_candidate_at_or_above_minimum(self):
        self.assertTrue(priority_allows("P0", "P1"))
        self.assertTrue(priority_allows("P1", "P1"))
        self.assertFalse(priority_allows("P2", "P1"))

    def test_write_limit_zero_means_unlimited(self):
        self.assertFalse(write_limit_reached(99, 0))
        self.assertFalse(write_limit_reached(1, None))
        self.assertTrue(write_limit_reached(3, 3))

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
