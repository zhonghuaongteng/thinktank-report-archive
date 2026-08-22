from __future__ import annotations

import unittest

from scripts.review_viewpoint_fifth_batch import SELECTED


class FifthBatchReviewTests(unittest.TestCase):
    def test_selection_prioritises_science_and_innovation_mechanisms(self) -> None:
        self.assertEqual(len(SELECTED), 5)
        self.assertEqual(sum(report_id.startswith("C-KISTEP-") for report_id in SELECTED), 3)
        self.assertEqual(sum(report_id.startswith("C-OECD-") for report_id in SELECTED), 2)
        self.assertIn("C-OECD-DOI-2AE8C0DC-EN", SELECTED)
        self.assertNotIn("C-OECD-DOI-68058B95-EN", SELECTED)
        self.assertNotIn("C-FRAUNHOFER-ISI-DP-86", SELECTED)


if __name__ == "__main__":
    unittest.main()
