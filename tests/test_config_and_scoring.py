import unittest

from thinktank_watch.config import load_institutions, load_priority_rules, load_topics
from thinktank_watch.models import ArticleCandidate
from thinktank_watch.scoring import score_candidate


class ConfigAndScoringTests(unittest.TestCase):
    def test_loads_all_planned_institutions_by_batch(self):
        institutions = load_institutions("config/institutions")
        names = {item.slug for item in institutions}

        self.assertGreaterEqual(len(institutions), 28)
        self.assertIn("rand", names)
        self.assertIn("cset", names)
        self.assertIn("gartner", names)
        self.assertIn("ida-stpi", names)
        self.assertEqual(
            {item.batch for item in institutions if item.slug == "rand"},
            {1},
        )
        self.assertEqual(
            {item.institution_type for item in institutions if item.slug == "gartner"},
            {"commercial_research"},
        )

    def test_scoring_promotes_ai_china_governance_items_to_p0(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Georgetown CSET",
            institution_type="think_tank",
            title="China, AI governance, advanced chips, and strategic technology competition",
            url="https://example.org/report",
            summary=(
                "Policy analysis on artificial intelligence governance, semiconductor export controls, "
                "advanced computing, and China technology strategy."
            ),
            published_date="2026-07-01",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P0")
        self.assertIn("AI治理", scored.topic_tags)
        self.assertIn("半导体", scored.topic_tags)
        self.assertIn("中国与上海相关", scored.topic_tags)
        self.assertEqual(scored.translation_level, "full_or_long")

    def test_scoring_keeps_low_relevance_items_in_index_only(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="Local education attendance patterns",
            url="https://example.org/education",
            summary="A descriptive education study with no technology or China policy signal.",
            published_date="2026-07-01",
            content_type="commentary",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P3")
        self.assertEqual(scored.translation_level, "index_only")


if __name__ == "__main__":
    unittest.main()
