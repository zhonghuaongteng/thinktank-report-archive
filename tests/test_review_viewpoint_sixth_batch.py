from __future__ import annotations

import unittest

from scripts.review_viewpoint_sixth_batch import SELECTED


class SixthBatchReviewTests(unittest.TestCase):
    def test_selection_excludes_security_weighted_candidate(self) -> None:
        self.assertEqual(len(SELECTED), 3)
        self.assertIn("C-OECD-DOI-EE847E5F-EN", SELECTED)
        self.assertNotIn("C-KISTEP-PRG0720220002", SELECTED)
        self.assertNotIn("C-FRAUNHOFER-ISI-DP-86", SELECTED)


if __name__ == "__main__":
    unittest.main()
