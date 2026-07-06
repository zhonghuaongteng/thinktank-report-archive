import unittest
from pathlib import Path


class RepositoryPolicyTests(unittest.TestCase):
    def test_archive_and_briefs_are_not_gitignored(self):
        ignore_text = Path(".gitignore").read_text(encoding="utf-8")

        self.assertNotIn("archive/", ignore_text)
        self.assertNotIn("briefs/", ignore_text)

    def test_daily_script_defaults_to_broad_innovation_support_profile(self):
        script = Path("scripts/run_daily.ps1").read_text(encoding="utf-8")

        self.assertIn('[string]$SearchProfile = "broad_innovation_support"', script)
        self.assertIn("[int]$LookbackDays = 30", script)
        self.assertIn('"--lookback-days", $LookbackDays', script)

    def test_weekly_script_defaults_to_broad_innovation_support_profile(self):
        script = Path("scripts/run_weekly.ps1").read_text(encoding="utf-8")

        self.assertIn('[string]$SearchProfile = "broad_innovation_support"', script)
        self.assertIn("[int]$LookbackDays = 14", script)
        self.assertIn('"run-weekly"', script)
        self.assertIn('"--brief-cadence", "weekly"', script)

    def test_evaluate_sources_script_is_read_only(self):
        script = Path("scripts/run_evaluate_sources.ps1").read_text(encoding="utf-8")

        self.assertIn('"evaluate"', script)
        self.assertIn('"--backfill"', script)
        self.assertIn('"--lookback-years", $LookbackYears', script)
        self.assertIn('"--search-profile", $SearchProfile', script)
        self.assertIn('"--unarchived-only"', script)
        self.assertNotIn('"backfill"', script.replace('"--backfill"', ""))
        self.assertNotIn('"run-weekly"', script)
        self.assertNotIn('"run-daily"', script)

    def test_evaluate_sources_accepts_comma_separated_institution_lists(self):
        script = Path("scripts/run_evaluate_sources.ps1").read_text(encoding="utf-8")

        self.assertIn('$normalizedInstitutions', script)
        self.assertIn('-split ","', script)
        self.assertIn("foreach ($institution in $normalizedInstitutions)", script)

    def test_strategy_only_mode_blocks_evaluation_and_backfill(self):
        retrieval = Path("docs/retrieval_strategy.md").read_text(encoding="utf-8")
        multi_agent = Path("docs/multi_agent_execution.md").read_text(encoding="utf-8")

        for text in (retrieval, multi_agent):
            self.assertIn("策略优化模式", text)
            self.assertIn("不得运行 `evaluate`", text)
            self.assertIn("不得", text)
            self.assertIn("`backfill`", text)
            self.assertIn("scripts\\run_strategy_review.ps1", text)

        self.assertIn("暂停与回滚", multi_agent)
        self.assertIn("SQLite", multi_agent)
        self.assertIn("知识库 CSV", multi_agent)

    def test_strategy_review_script_does_not_fetch_or_write(self):
        script = Path("scripts/run_strategy_review.ps1").read_text(encoding="utf-8")

        self.assertIn("git status --porcelain -- archive briefs state", script)
        self.assertIn("git diff --check", script)
        self.assertIn("$LASTEXITCODE", script)
        self.assertIn("unittest tests.test_repository_policy", script)
        self.assertIn("archive_count=", script)
        self.assertIn("state_archived=", script)
        self.assertNotIn("thinktank_watch.cli", script)
        self.assertNotIn("run_weekly.ps1", script)
        self.assertNotIn("run_daily.ps1", script)
        self.assertNotIn("run_evaluate_sources.ps1", script)


if __name__ == "__main__":
    unittest.main()
