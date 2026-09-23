import copy
import csv
from pathlib import Path
import tempfile
import unittest

from thinktank_watch.audit import write_editorial_review_queue
from thinktank_watch.interests import ResearchInterest, match_research_interests
from thinktank_watch.models import ArticleCandidate


class ResearchInterestReviewTests(unittest.TestCase):
    def setUp(self):
        self.interests = [
            ResearchInterest("AI4S", "明确重点", ("AI4S", "AI for Science")),
            ResearchInterest("区块链", "明确重点", ("blockchain", "区块链")),
        ]

    def candidate(self, title, date="2026-09-20", **kwargs):
        return ArticleCandidate("science", "Science", "think_tank", title,
                                "https://example.org/" + title, published_date=date, **kwargs)

    def test_review_keeps_low_score_other_sources_and_unknown_dates_without_mutation(self):
        candidates = [
            self.candidate("AI4S laboratories", priority="P3", score=0),
            self.candidate("Blockchain science", date="", fetch_status="detail_error:timeout"),
            self.candidate("AI4S month-only issue", date="2026-09"),
            self.candidate("AI for Science old issue", date="2026-09-13"),
            self.candidate("AI4S future issue", date="2026-09-21"),
            self.candidate("Demand and firms", source_group="innovation_economy"),
            self.candidate("Unrelated"),
        ]
        before = copy.deepcopy(candidates)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_editorial_review_queue(Path(tmp) / "review.csv", candidates,
                                                 "2026-09-20", interests=self.interests)
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual([row["标题"] for row in rows],
                         ["AI4S laboratories", "Blockchain science", "AI4S month-only issue", "Demand and firms"])
        self.assertEqual(rows[0]["原始优先级"], "P3")
        self.assertEqual(rows[0]["研究关注主题"], "AI4S")
        self.assertEqual(rows[1]["复核状态"], "待核首次发布日期")
        self.assertEqual(rows[2]["复核状态"], "待核首次发布日期")
        self.assertEqual(rows[3]["研究关注主题"], "")
        self.assertEqual(candidates, before)

    def test_acronym_boundaries_and_bibliography_do_not_create_matches(self):
        candidate = self.candidate("CAI4Science", detail_text="References: AI4S and blockchain")
        self.assertEqual(match_research_interests(candidate, self.interests), [])
        candidate.chinese_summary = "这项研究讨论区块链如何支持科学协作。"
        matches = match_research_interests(candidate, self.interests)
        self.assertEqual([interest.name for interest, _ in matches], ["区块链"])

    def test_multiple_aliases_keep_one_review_row_and_all_context(self):
        candidate = self.candidate("AI4S: AI for Science with blockchain")
        with tempfile.TemporaryDirectory() as tmp:
            path = write_editorial_review_queue(Path(tmp) / "review.csv", [candidate],
                                                 "2026-09-20", interests=self.interests)
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["研究关注主题"], "AI4S；区块链")
        self.assertEqual(rows[0]["研究关注层级"], "明确重点")
        self.assertEqual(candidate.score, 0)

    def test_phrase_spacing_and_dash_variants_preserve_word_boundaries(self):
        for title in ["AI-for-science", "AI for\nScience", "AI\u2011for\u2011Science"]:
            matches = match_research_interests(self.candidate(title), self.interests)
            self.assertEqual([interest.name for interest, _ in matches], ["AI4S"])
        self.assertEqual(match_research_interests(self.candidate("CAI-for-Science"), self.interests), [])
