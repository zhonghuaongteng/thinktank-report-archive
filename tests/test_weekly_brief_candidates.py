from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from thinktank_watch.archive import write_article
from thinktank_watch.cli import write_run_brief
from thinktank_watch.editorial import validate_weekly_editorial
from thinktank_watch.kb import append_kb_index
from thinktank_watch.models import ArticleCandidate


class WeeklyBriefCandidateTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.args = SimpleNamespace(
            _weekly_run=True, lookback_days=7, brief_cadence="weekly",
            archive_root=root / "archive", brief_root=root / "briefs",
            skip_kb=False, kb_root=root / "kb",
        )
        self.date = "2026-09-20"

    def candidate(self, name, published):
        return ArticleCandidate(
            "example", "Example", "think_tank", name, "https://example.org/" + name,
            published_date=published, priority="P1", fetch_status="detail_ok",
        )

    def test_weekly_rerun_keeps_prior_archives_for_current_editorial(self):
        earlier = self.candidate("earlier", "2026-09-14")
        current = self.candidate("current", self.date)
        excluded = [self.candidate("old", "2026-09-13"),
                    self.candidate("future", "2026-09-21"),
                    self.candidate("undated", "")]
        for item in [earlier, current, *excluded]:
            write_article(self.args.archive_root, item)
        append_kb_index([earlier], "2026-09-16", self.args.kb_root)
        append_kb_index([current], self.date, self.args.kb_root)
        editorial = {
            "date": self.date, "headline": "本期发现", "lead": "本期跨日期材料的发现。",
            "discoveries": [{"title": "已有材料", "text": "已核对原文的发现。",
                             "source_locator": "第1页", "source_url": earlier.url,
                             "article_url": earlier.url}],
            "connections": [{"title": "研究连接", "text": "有关企业创新。",
                             "article_urls": [earlier.url]}],
        }

        def render(_root, run_date, candidates, **_kwargs):
            validate_weekly_editorial(editorial, run_date, candidates)

        for written in ([current], []):
            with self.subTest(written=len(written)), patch(
                "thinktank_watch.cli.write_periodic_brief", side_effect=render
            ) as output:
                write_run_brief(self.args, self.date, written)
            self.assertEqual({item.url for item in output.call_args.args[2]},
                             {earlier.url, current.url})

    def test_no_archive_fallback_keeps_only_written_items_in_fixed_window(self):
        current = self.candidate("index-only", self.date)
        current.priority = "P3"
        written = [current, self.candidate("old", "2026-09-13"),
                   self.candidate("future", "2026-09-21"), self.candidate("undated", "")]
        with patch("thinktank_watch.cli.write_periodic_brief") as output:
            write_run_brief(self.args, self.date, written)
        self.assertEqual(output.call_args.args[2], [current])

    def test_daily_keeps_same_day_index_even_with_weekly_brief_cadence(self):
        self.args._weekly_run = False
        indexed = self.candidate("daily-indexed", "2026-09-13")
        other = self.candidate("other-archive", "2026-09-18")
        for item in (indexed, other):
            write_article(self.args.archive_root, item)
        append_kb_index([indexed], self.date, self.args.kb_root)
        with patch("thinktank_watch.cli.write_periodic_brief") as output, patch(
            "thinktank_watch.cli.load_weekly_archive_candidates"
        ) as weekly_loader:
            write_run_brief(self.args, self.date, [other])
        weekly_loader.assert_not_called()
        self.assertEqual([item.url for item in output.call_args.args[2]], [indexed.url])


if __name__ == "__main__":
    unittest.main()
