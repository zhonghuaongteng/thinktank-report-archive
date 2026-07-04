import unittest

from thinktank_watch.cli import priority_allows, sort_for_writing, write_limit_reached
from thinktank_watch.models import ArticleCandidate


class BackfillControlTests(unittest.TestCase):
    def test_priority_allows_candidate_at_or_above_minimum(self):
        self.assertTrue(priority_allows("P0", "P1"))
        self.assertTrue(priority_allows("P1", "P1"))
        self.assertFalse(priority_allows("P2", "P1"))

    def test_write_limit_zero_means_unlimited(self):
        self.assertFalse(write_limit_reached(99, 0))
        self.assertFalse(write_limit_reached(1, None))
        self.assertTrue(write_limit_reached(3, 3))

    def test_sort_for_writing_prioritizes_priority_then_score(self):
        candidates = [
            ArticleCandidate("a", "A", "think_tank", "P3 item", "https://example.org/3", priority="P3", score=9),
            ArticleCandidate("b", "B", "think_tank", "P1 item", "https://example.org/1", priority="P1", score=4),
            ArticleCandidate("c", "C", "think_tank", "P0 item", "https://example.org/0", priority="P0", score=3),
            ArticleCandidate("d", "D", "think_tank", "P1 high", "https://example.org/1h", priority="P1", score=8),
        ]

        ordered = sort_for_writing(candidates)

        self.assertEqual([item.title for item in ordered], ["P0 item", "P1 high", "P1 item", "P3 item"])


if __name__ == "__main__":
    unittest.main()
