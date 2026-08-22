from __future__ import annotations

import unittest

from scripts.review_viewpoint_seventh_batch import SELECTED


class SeventhBatchReviewTests(unittest.TestCase):
    def test_selection_centres_china_science_and_innovation(self) -> None:
        self.assertEqual(len(SELECTED), 18)
        self.assertEqual(sum(report_id.startswith("C-ITIF-") for report_id in SELECTED), 10)
        self.assertEqual(sum(report_id.startswith("C-FRAUNHOFER-") for report_id in SELECTED), 4)
        self.assertEqual(sum(report_id.startswith("C-CSET-") for report_id in SELECTED), 3)
        self.assertNotIn("S-CEIP-2022-01", SELECTED)
        self.assertNotIn("S-CH-2019-01", SELECTED)


if __name__ == "__main__":
    unittest.main()
