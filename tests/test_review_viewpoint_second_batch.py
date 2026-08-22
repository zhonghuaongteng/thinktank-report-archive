import unittest

from scripts.review_viewpoint_second_batch import SELECTED


class SecondBatchReviewTests(unittest.TestCase):
    def test_second_batch_is_selective_and_mechanism_led(self) -> None:
        self.assertEqual(len(SELECTED), 12)
        self.assertTrue(all(value.mechanism and value.reason for value in SELECTED.values()))
        self.assertFalse(any("安全" in value.mechanism for value in SELECTED.values()))


if __name__ == "__main__":
    unittest.main()
