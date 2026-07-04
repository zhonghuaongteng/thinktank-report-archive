import unittest
from pathlib import Path


class RepositoryPolicyTests(unittest.TestCase):
    def test_archive_and_briefs_are_not_gitignored(self):
        ignore_text = Path(".gitignore").read_text(encoding="utf-8")

        self.assertNotIn("archive/", ignore_text)
        self.assertNotIn("briefs/", ignore_text)


if __name__ == "__main__":
    unittest.main()
