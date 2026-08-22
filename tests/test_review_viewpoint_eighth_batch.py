from __future__ import annotations

import unittest

from scripts.review_viewpoint_eighth_batch import CANDIDATE_IDS, SELECTED


class EighthBatchReviewTests(unittest.TestCase):
    def test_selection_centres_science_technology_and_china_comparison(self) -> None:
        self.assertEqual(len(CANDIDATE_IDS), 28)
        self.assertEqual(len(SELECTED), 16)
        self.assertEqual(sum(report_id.startswith("C-CSET-") for report_id in SELECTED), 4)
        self.assertEqual(sum(report_id.startswith("C-OECD-") or report_id.startswith("S-OECD-") for report_id in SELECTED), 7)
        self.assertIn("C-CSET-13458", SELECTED)
        self.assertNotIn("C-CSET-20366", SELECTED)
        self.assertNotIn("C-FRAUNHOFER-ISI-DP-86", SELECTED)


if __name__ == "__main__":
    unittest.main()
