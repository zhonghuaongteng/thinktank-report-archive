import os
from contextlib import closing
from pathlib import Path
import shutil
import sqlite3
import subprocess
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from thinktank_watch.archive import write_article
from thinktank_watch.cli import run_daily, run_weekly
from thinktank_watch.kb import append_kb_index
from thinktank_watch.models import ArticleCandidate, Institution
from thinktank_watch.state import ArticleState


class WeeklyRunContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.institution = Institution(
            "example", "Example", "示例", "United States", "think_tank",
            "P1", 1, "https://example.org", "generic", "private_archive",
        )
        self.args = SimpleNamespace(
            date="2026-09-20", batch=1, institution=None,
            state=str(self.root / "articles.sqlite"),
            archive_root=str(self.root / "archive"),
            brief_root=str(self.root / "briefs"),
            skip_kb=False, kb_root=str(self.root / "kb"),
            limit=30, min_priority="P1", write_limit=0, refresh=False,
            lookback_days=7,
        )

    def candidate(self, slug, published, status="detail_ok"):
        return ArticleCandidate(
            "example", "Example", "think_tank", "Innovation research " + slug,
            "https://example.org/" + slug, published_date=published,
            summary="Research on innovation and productivity.",
            priority="P1", score=8, fetch_status=status,
        )

    def run_candidates(self, candidates, runner=run_weekly):
        with (
            patch("thinktank_watch.cli._load_config", return_value=([self.institution], [], object())),
            patch("thinktank_watch.cli.collect_candidates", return_value=candidates),
            patch("thinktank_watch.cli.score_candidate", side_effect=lambda item, *_: item),
            patch("thinktank_watch.cli.append_kb_index") as append_kb,
            patch("thinktank_watch.cli.write_institution_table"),
            patch("thinktank_watch.cli.write_run_brief") as write_brief,
        ):
            runner(self.args)
        return append_kb.call_args.args[0], write_brief.call_args.args[2]

    def stored_urls(self):
        with closing(sqlite3.connect(self.args.state)) as connection:
            return {row[0] for row in connection.execute("SELECT url FROM articles")}

    def test_weekly_archive_state_kb_and_brief_use_the_same_seven_dates(self):
        first = self.candidate("first", "2026-09-14")
        last = self.candidate("last", "2026-09-20")
        excluded = [
            self.candidate("previous-sunday", "2026-09-13"),
            self.candidate("old-failed", "2026-09-13", "detail_error:503"),
            self.candidate("future", "2026-09-21"),
            self.candidate("undated-failed", "", "detail_error:503"),
        ]
        kb_items, brief_items = self.run_candidates([*excluded, first, last])
        expected = {first.url, last.url}
        self.assertEqual(self.stored_urls(), expected)
        self.assertEqual({item.url for item in kb_items}, expected)
        self.assertEqual({item.url for item in brief_items}, expected)
        self.assertEqual(len(list((self.root / "archive").rglob("*.md"))), 2)

    def test_transient_failure_is_not_persisted_and_can_succeed_on_retry(self):
        candidate = self.candidate("retry", "2026-09-18", "detail_error:503")
        kb_items, _ = self.run_candidates([candidate])
        self.assertEqual(self.stored_urls(), set())
        self.assertEqual(kb_items, [])
        candidate.fetch_status = "detail_ok"
        self.run_candidates([candidate])
        self.assertEqual(self.stored_urls(), {candidate.url})

    def test_actual_weekly_brief_filters_same_day_indexed_daily_items(self):
        stale = self.candidate("daily-stale", "2026-09-13")
        first = self.candidate("daily-within-week", "2026-09-14")
        latest = self.candidate("weekly-latest", "2026-09-20")
        for candidate in (stale, first):
            write_article(self.args.archive_root, candidate)
        append_kb_index([stale, first], self.args.date, self.args.kb_root)
        with (
            patch("thinktank_watch.cli._load_config", return_value=([self.institution], [], object())),
            patch("thinktank_watch.cli.collect_candidates", return_value=[latest]),
            patch("thinktank_watch.cli.score_candidate", side_effect=lambda item, *_: item),
            patch("thinktank_watch.cli.write_institution_table"),
            patch("thinktank_watch.cli.write_periodic_brief") as render,
        ):
            run_weekly(self.args)
        self.assertEqual({item.url for item in render.call_args.args[2]}, {first.url, latest.url})

    def test_daily_weekly_brief_cadence_preserves_daily_window_and_seen_semantics(self):
        self.args.brief_cadence = "weekly"
        boundary = self.candidate("daily-boundary", "2026-09-13")
        legacy_failure = self.candidate("daily-seen-failure", "2026-09-18", "detail_error:503")
        state = ArticleState(self.args.state)
        try:
            state.upsert(legacy_failure, "")
        finally:
            state.close()
        legacy_failure.fetch_status = "detail_ok"
        kb_items, _ = self.run_candidates([boundary, legacy_failure], runner=run_daily)
        self.assertEqual([item.url for item in kb_items], [boundary.url])

    def test_daily_preserves_failed_attempt_state_outside_its_date_window(self):
        stale = self.candidate("daily-stale-failure", "2026-09-12", "detail_error:503")
        undated = self.candidate("daily-undated-failure", "", "detail_error:503")
        kb_items, _ = self.run_candidates([stale, undated], runner=run_daily)
        self.assertEqual(self.stored_urls(), {stale.url, undated.url})
        self.assertEqual(kb_items, [])

    def test_legacy_failed_state_can_recover_but_archived_url_stays_deduplicated(self):
        candidate = self.candidate("legacy-failure", "2026-09-18", "detail_error:503")
        state = ArticleState(self.args.state)
        try:
            state.upsert(candidate, "")
        finally:
            state.close()
        candidate.fetch_status = "detail_ok"
        kb_items, _ = self.run_candidates([candidate])
        self.assertEqual([item.url for item in kb_items], [candidate.url])
        kb_items, brief_items = self.run_candidates([candidate])
        self.assertEqual(kb_items, [])
        self.assertEqual(brief_items, [])
        self.assertEqual(len(list((self.root / "archive").rglob("*.md"))), 1)

    def test_missing_or_invalid_run_date_stops_before_loading_sources_or_state(self):
        for run_date in (None, "2026-09-31", "20260920", "2026-9-20"):
            with self.subTest(run_date=run_date), patch("thinktank_watch.cli._load_config") as load:
                self.args.date = run_date
                with self.assertRaises(ValueError):
                    run_weekly(self.args)
                load.assert_not_called()
        self.assertFalse(Path(self.args.state).exists())


@unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "PowerShell wrapper verification requires Windows")
class WeeklyWrapperTests(unittest.TestCase):
    def invoke_wrapper(self, exit_code):
        with TemporaryDirectory(prefix="weekly wrapper ") as temp:
            fake = Path(temp) / "verified-interpreter.ps1"
            fake.write_text(
                'Write-Output ($args -join "|")\nexit ' + str(exit_code) + "\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    "powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                    "-File", str(Path("scripts/run_weekly.ps1").resolve()),
                    "-Date", "2026-09-20", "-Python", str(fake),
                ],
                capture_output=True, text=True, errors="replace", timeout=20,
            )

    def test_wrapper_passes_the_fixed_date_and_verified_interpreter_path(self):
        result = self.invoke_wrapper(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--date|2026-09-20", result.stdout)
        self.assertIn("--lookback-days|7", result.stdout)

    def test_wrapper_returns_failure_when_collection_fails(self):
        result = self.invoke_wrapper(7)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Weekly collection failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
