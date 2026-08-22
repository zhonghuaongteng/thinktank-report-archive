from __future__ import annotations

import unittest

from scripts.review_viewpoint_ninth_batch import CANDIDATE_IDS, SELECTED


class NinthBatchReviewTests(unittest.TestCase):
    def test_selection_builds_science_and_innovation_policy_longitudinal_chain(self) -> None:
        self.assertEqual(len(CANDIDATE_IDS), 20)
        self.assertEqual(len(SELECTED), 14)
        self.assertTrue(all(report_id.startswith("C-FRAUNHOFER-ISI-DP-") for report_id in SELECTED))
        self.assertIn("C-FRAUNHOFER-ISI-DP-49", SELECTED)
        self.assertIn("C-FRAUNHOFER-ISI-DP-94", SELECTED)
        self.assertNotIn("C-FRAUNHOFER-ISI-DP-83", SELECTED)
        self.assertNotIn("S-FISI-2016-01", SELECTED)


if __name__ == "__main__":
    unittest.main()
