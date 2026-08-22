from __future__ import annotations

import unittest

from scripts.review_viewpoint_fourth_batch import SELECTED


class FourthBatchReviewTests(unittest.TestCase):
    def test_selection_keeps_innovation_mechanisms_and_excludes_noise(self) -> None:
        self.assertEqual(len(SELECTED), 12)
        self.assertEqual(sum(report_id.startswith("C-KISTEP-") for report_id in SELECTED), 4)
        self.assertEqual(sum(report_id.startswith("C-OECD-") for report_id in SELECTED), 5)
        self.assertNotIn("C-OECD-DOI-68058B95-EN", SELECTED)
        self.assertNotIn("C-FRAUNHOFER-ISI-DP-86", SELECTED)
        self.assertNotIn("C-CSET-18960", SELECTED)


if __name__ == "__main__":
    unittest.main()
