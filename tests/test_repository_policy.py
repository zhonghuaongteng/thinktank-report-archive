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


if __name__ == "__main__":
    unittest.main()
