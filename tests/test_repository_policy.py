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
        self.assertIn("[int]$LookbackDays = 7", script)
        self.assertIn('"run-weekly"', script)
        self.assertIn('"--brief-cadence", "weekly"', script)

    def test_weekly_comic_scripts_route_through_explicit_cli_commands(self):
        expected = {
            "scripts/prepare_weekly_comics.ps1": "prepare-weekly-comics",
            "scripts/render_weekly_brief.ps1": "render-weekly-brief",
            "scripts/check_weekly_comics.ps1": "check-weekly-comics",
        }

        for script_path, command in expected.items():
            script = Path(script_path).read_text(encoding="utf-8")
            self.assertIn(command, script)
            self.assertIn("$LASTEXITCODE", script)
            self.assertIn("Python313", script)

        cli = Path("thinktank_watch/cli.py").read_text(encoding="utf-8")
        for command in expected.values():
            self.assertIn(command, cli)

    def test_weekly_comic_mode_requires_codex_images_without_forced_shanghai(self):
        strategy = Path("docs/retrieval_strategy.md").read_text(encoding="utf-8")
        comic_doc = Path("docs/weekly_comic_generation.md").read_text(encoding="utf-8")
        comic_pref = Path(".baoyu-skills/baoyu-comic/EXTEND.md").read_text(encoding="utf-8")
        image_pref = Path(".baoyu-skills/baoyu-image-gen/EXTEND.md").read_text(encoding="utf-8")

        for text in (strategy, comic_doc, comic_pref, image_pref):
            self.assertIn("Codex", text)
            self.assertIn("不强行", text)
            self.assertIn("中国", text)
            self.assertIn("上海", text)
        self.assertIn("不得回退为程序化示意图", comic_doc)
        for text in (strategy, comic_doc, comic_pref):
            self.assertIn("科普化", text)
            self.assertIn("可视化", text)
            self.assertIn("证据配图", text)
        self.assertIn("不读原报告", comic_doc)
        self.assertIn("报告对象 -> 中心判断 -> 论述线索 -> 影响路径", strategy)
        self.assertIn("check_weekly_comics.ps1", strategy)

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

    def test_strategy_optimization_round_has_finite_stop_boundary(self):
        retrieval = Path("docs/retrieval_strategy.md").read_text(encoding="utf-8")
        multi_agent = Path("docs/multi_agent_execution.md").read_text(encoding="utf-8")

        self.assertIn("本轮优化停止机制", retrieval)
        self.assertIn("不再新增智库源", retrieval)
        self.assertIn("不再扩展检索词", retrieval)
        self.assertIn("不再启动来源评估agent", retrieval)
        self.assertIn("最多允许一次", retrieval)
        self.assertIn("第二次仍失败时停止", retrieval)
        self.assertIn("archive_count", retrieval)
        self.assertIn("state_total", retrieval)
        self.assertIn("知识库索引行数", retrieval)
        self.assertIn("策略优化轮次必须有停止边界", multi_agent)

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
