import unittest

from thinktank_watch.config import load_institutions, load_priority_rules, load_topics
from thinktank_watch.cli import _select_institutions
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

    def test_selecting_explicit_institution_ignores_batch_filter(self):
        institutions = load_institutions("config/institutions")
        selected = _select_institutions(institutions, batch=1, slug="csis")

        self.assertEqual([item.slug for item in selected], ["csis"])

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

    def test_china_context_alone_does_not_promote_to_priority_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="csis",
            institution_name="CSIS",
            institution_type="think_tank",
            title="Statesmen's Forum: Wang Yi, Minister of Foreign Affairs, PRC",
            url="https://example.org/event",
            summary="A foreign affairs event focused on diplomatic exchange and bilateral relations.",
            published_date="2016-02-19",
            content_type="event",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertEqual(scored.topic_tags, ["中国与上海相关"])
        self.assertEqual(scored.translation_level, "summary")

    def test_ai_index_report_is_priority_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="stanford-hai",
            institution_name="Stanford HAI",
            institution_type="university_research_center",
            title="The 2026 AI Index Report",
            url="https://example.org/ai-index/2026-ai-index-report",
            summary="Annual measurement report on artificial intelligence trends, governance, investment, and research.",
            published_date="2026-05-12",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)

    def test_ai_surveillance_is_governance_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="carnegie-tech",
            institution_name="Carnegie Technology and International Affairs Program",
            institution_type="think_tank",
            title="The Global Expansion of AI Surveillance",
            url="https://example.org/research/ai-surveillance",
            summary="A report on artificial intelligence surveillance and governance risks.",
            published_date="2019-09-17",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)

    def test_ai_standards_are_governance_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="brookings-cti",
            institution_name="Brookings Center for Technology Innovation",
            institution_type="think_tank",
            title="G7 should accept AI standards offer, but make it enforceable",
            url="https://example.org/articles/g7-ai-standards",
            summary="AI standards and enforceable governance commitments for advanced economies.",
            published_date="2026-07-01",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("AI治理", scored.topic_tags)

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
