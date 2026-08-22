from __future__ import annotations

import unittest

from scripts.review_viewpoint_tenth_batch import CANDIDATE_IDS, SELECTED


class TenthBatchReviewTests(unittest.TestCase):
    def test_selection_centres_science_system_and_research_mechanisms(self) -> None:
        self.assertEqual(len(CANDIDATE_IDS), 28)
        self.assertEqual(len(SELECTED), 16)
        self.assertEqual(sum(report_id.startswith("S-OECD-") for report_id in SELECTED), 3)
        self.assertIn("C-OECD-DOI-06913B3B-EN", SELECTED)
        self.assertIn("C-OECD-DOI-DC21227A-EN", SELECTED)
        self.assertNotIn("C-OECD-DOI-1C416F43-EN", SELECTED)
        self.assertNotIn("C-OECD-DOI-3F6C76A4-EN", SELECTED)
        self.assertNotIn("C-OECD-DOI-A1CFB1A8-EN", SELECTED)


if __name__ == "__main__":
    unittest.main()
