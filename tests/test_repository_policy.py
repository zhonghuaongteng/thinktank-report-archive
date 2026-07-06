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


if __name__ == "__main__":
    unittest.main()
