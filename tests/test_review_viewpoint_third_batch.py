from __future__ import annotations

import unittest

from scripts.review_viewpoint_third_batch import SELECTED


class ThirdBatchReviewTests(unittest.TestCase):
    def test_selection_is_bounded_and_innovation_centered(self) -> None:
        self.assertEqual(len(SELECTED), 12)
        self.assertEqual(sum(report_id.startswith("C-STANFORD-HAI-AI-INDEX-") for report_id in SELECTED), 4)
        self.assertEqual(sum(report_id.startswith("C-OECD-") for report_id in SELECTED), 4)
        self.assertNotIn("C-CSET-11988", SELECTED)
        self.assertNotIn("C-FRAUNHOFER-ISI-DP-86", SELECTED)


if __name__ == "__main__":
    unittest.main()
