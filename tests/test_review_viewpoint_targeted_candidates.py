import unittest

from scripts.review_viewpoint_targeted_candidates import SELECTED


class TargetedCandidateReviewTests(unittest.TestCase):
    def test_selected_batch_is_small_and_mechanism_led(self) -> None:
        self.assertEqual(len(SELECTED), 18)
        self.assertTrue(all(value.mechanism and value.reason for value in SELECTED.values()))
        self.assertTrue(any("CHINA" in report_id for report_id in SELECTED))

    def test_security_does_not_define_a_selection_mechanism(self) -> None:
        self.assertFalse(any("安全" in value.mechanism for value in SELECTED.values()))


if __name__ == "__main__":
    unittest.main()
