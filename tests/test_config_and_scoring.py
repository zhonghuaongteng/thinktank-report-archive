import unittest

from thinktank_watch.config import load_institutions, load_priority_rules, load_search_profiles, load_topics
from thinktank_watch.cli import _select_institutions, build_parser, candidate_matches_search_profile
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
        for slug in {
            "alan-turing",
            "aspi",
            "atlantic-council-geotech",
            "belfer",
            "bruegel",
            "ceps",
            "csis",
            "ecipe",
            "hoover-tpa",
            "ida-stpi",
            "nbr",
            "nistep",
            "orf-america",
            "stepi",
        }:
            self.assertEqual(
                {item.batch for item in institutions if item.slug == slug},
                {1},
                f"{slug} should be in the broad innovation-support daily pool",
            )
        self.assertEqual(
            {item.institution_type for item in institutions if item.slug == "gartner"},
            {"commercial_research"},
        )

    def test_cset_sitemap_is_enabled_for_broad_innovation_support(self):
        institutions = load_institutions("config/institutions")
        cset = next(item for item in institutions if item.slug == "cset")

        self.assertIn("https://cset.georgetown.edu/wp-sitemap.xml", cset.sitemap_urls)
        for keyword in {"compute", "supply-chain", "talent", "innovation", "research", "technology"}:
            self.assertIn(keyword, cset.sitemap_include_keywords)

    def test_rusi_sitemap_is_enabled_for_defense_technology_backfill(self):
        institutions = load_institutions("config/institutions")
        rusi = next(item for item in institutions if item.slug == "rusi")

        self.assertIn("https://www.rusi.org/sitemap-index.xml", rusi.sitemap_urls)
        for keyword in {"artificial-intelligence", "cyber", "defence", "technology", "china"}:
            self.assertIn(keyword, rusi.sitemap_include_keywords)

    def test_hoover_uses_focused_pages_instead_of_global_feed_backfill(self):
        institutions = load_institutions("config/institutions")
        hoover = next(item for item in institutions if item.slug == "hoover-tpa")

        self.assertEqual(hoover.feeds, [])
        self.assertEqual(hoover.sitemap_urls, [])
        self.assertIn("https://www.hoover.org/research-teams/technology-policy-accelerator", hoover.list_pages)
        self.assertIn(
            "https://www.hoover.org/research-teams/technology-economics-and-governance-working-group",
            hoover.list_pages,
        )
        self.assertGreaterEqual(hoover.run_limit, 20)

    def test_text_proxy_fallback_is_limited_to_static_blocked_sources(self):
        institutions = load_institutions("config/institutions")
        ceps = next(item for item in institutions if item.slug == "ceps")
        nbr = next(item for item in institutions if item.slug == "nbr")
        rand = next(item for item in institutions if item.slug == "rand")

        self.assertTrue(ceps.text_proxy_fallback)
        self.assertTrue(nbr.text_proxy_fallback)
        self.assertFalse(rand.text_proxy_fallback)
        self.assertEqual(ceps.list_pages, [])
        self.assertGreaterEqual(nbr.run_limit, 8)

    def test_rand_sitemap_prefers_publication_paths_not_center_pages(self):
        institutions = load_institutions("config/institutions")
        rand = next(item for item in institutions if item.slug == "rand")

        self.assertIn("/pubs/research_reports/", rand.sitemap_include_keywords)
        self.assertIn("/pubs/external_publications/", rand.sitemap_include_keywords)
        self.assertNotIn("center", rand.sitemap_include_keywords)

    def test_selecting_explicit_institution_ignores_batch_filter(self):
        institutions = load_institutions("config/institutions")
        selected = _select_institutions(institutions, batch=1, slug="csis")

        self.assertEqual([item.slug for item in selected], ["csis"])

    def test_loads_broad_innovation_support_search_profile(self):
        profiles = load_search_profiles("config/search_profiles.yaml")
        profile = profiles["broad_innovation_support"]

        self.assertTrue(profile.exclude_governance_only)
        self.assertIn("科技创新", profile.topic_tags_any)
        self.assertIn("先进制造", profile.topic_tags_any)
        self.assertIn("数字经济", profile.topic_tags_any)
        self.assertIn("科技人才", profile.topic_tags_any)
        self.assertIn("国防AI", profile.topic_tags_any)
        self.assertIn("科技治理", profile.topic_tags_any)

    def test_daily_and_backfill_cli_default_to_broad_innovation_support_profile(self):
        parser = build_parser()

        evaluate_args = parser.parse_args(["evaluate", "--unarchived-only"])
        daily_args = parser.parse_args(["run-daily"])
        weekly_args = parser.parse_args(["run-weekly"])
        backfill_args = parser.parse_args(["backfill"])

        self.assertTrue(evaluate_args.unarchived_only)
        self.assertEqual(daily_args.search_profile, "broad_innovation_support")
        self.assertEqual(weekly_args.search_profile, "broad_innovation_support")
        self.assertEqual(weekly_args.lookback_days, 14)
        self.assertEqual(weekly_args.brief_cadence, "weekly")
        self.assertEqual(backfill_args.search_profile, "broad_innovation_support")

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

    def test_ai_index_economy_chapter_is_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        profile = load_search_profiles("config/search_profiles.yaml")["broad_innovation_support"]
        candidate = ArticleCandidate(
            institution_slug="stanford-hai",
            institution_name="Stanford HAI",
            institution_type="university_research_center",
            title="Economy | The 2026 AI Index Report",
            url="https://hai.stanford.edu/ai-index/2026-ai-index-report/economy",
            summary=(
                "This chapter analyzes the economic footprint of AI across the private sector and "
                "its implications for labor markets, productivity, and the future of work."
            ),
            published_date="2026-06-29",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("数字经济", scored.topic_tags)
        self.assertIn("科技人才", scored.topic_tags)
        self.assertTrue(candidate_matches_search_profile(scored, profile))

    def test_hai_llm_industry_brief_is_technology_innovation_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="stanford-hai",
            institution_name="Stanford HAI",
            institution_type="university_research_center",
            title="Human-Centered Large Language Models",
            url="https://hai.stanford.edu/industry/human-centered-large-language-models",
            summary=(
                "Large language models have moved from research laboratories into everyday "
                "infrastructure, powering developer tools, healthcare assistants, and enterprise agents."
            ),
            published_date="2026-07-01",
            content_type="brief",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)

    def test_research_culture_is_science_system_support_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="nistep",
            institution_name="NISTEP",
            institution_type="government_research_institute",
            title="Research Culture in Dialogue and Practice",
            url="https://www.nistep.go.jp/en/?p=5926",
            summary="Toward a nationwide survey of researchers on wellbeing and research culture.",
            published_date="2025-12-26",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("科技人才", scored.topic_tags)

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

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)

    def test_chinese_ai_models_are_priority_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="csis",
            institution_name="CSIS",
            institution_type="think_tank",
            title="What to Know About Chinese AI Models",
            url="https://www.csis.org/analysis/what-know-about-chinese-ai-models",
            summary="Analysis of Chinese AI models, policy, and strategic technology competition.",
            published_date="2026-07-02",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)
        self.assertIn("中国与上海相关", scored.topic_tags)

    def test_ai_risk_market_gatekeeping_is_priority_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="ecipe",
            institution_name="ECIPE",
            institution_type="think_tank",
            title="The AI Risk Nobody Is Regulating: Market Gatekeeping",
            url="https://ecipe.org/insights/ai-risk-nobody-is-regulating/",
            summary="Market gatekeeping creates AI risk and competition regulation challenges.",
            published_date="2026-06-29",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)
        self.assertIn("科技治理", scored.topic_tags)

    def test_health_ai_cross_border_data_policy_is_governance_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="atlantic-council-geotech",
            institution_name="Atlantic Council GeoTech Center and Cyber Statecraft Initiative",
            institution_type="think_tank",
            title=(
                "The US AI health data collision: Charting the future of US cross-border data "
                "flow policy, health data, and health and biopharma AI policy"
            ),
            url="https://www.atlanticcouncil.org/in-depth-research-reports/issue-brief/the-us-ai-health-data-policy/",
            summary="Issue brief on health AI, data security, and cross-border data flows.",
            published_date="2026-05-13",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)
        self.assertIn("科技治理", scored.topic_tags)

    def test_hyphenated_artificial_intelligence_title_is_ai_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="Artificial-intelligence competition in Europe: the role of DMA Article 6(7)",
            url="https://www.bruegel.org/working-paper/artificial-intelligence-competition-europe-role-dma-article-67",
            summary="Working paper on artificial intelligence competition policy and digital market regulation.",
            published_date="2026-07-02",
            content_type="paper",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)

    def test_standalone_ai_report_title_is_ai_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="ada-lovelace",
            institution_name="Ada Lovelace Institute",
            institution_type="think_tank",
            title="Navigating the future",
            url="https://www.adalovelaceinstitute.org/report/navigating-the-future/",
            summary="A landscape review of AI in career guidance for young people.",
            published_date="2026-04-13",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)

    def test_genai_usage_trends_are_ai_governance_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="oecd-ai",
            institution_name="OECD.AI Policy Observatory",
            institution_type="intergovernmental",
            title="How people are using GenAI chatbots: Evidence from web traffic data",
            url="https://oecd.ai/en/wonk/how-people-are-using-genai-chatbots-evidence-from-web-traffic-data",
            summary="Evidence from web traffic data on chatbot usage and diffusion.",
            published_date="2026-06-30",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)

    def test_gpai_policy_title_is_ai_governance_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="govai",
            institution_name="GovAI",
            institution_type="think_tank",
            title="Requirements for Model Specifications in the EU GPAI Code of Practice",
            url="https://www.governance.ai/research-paper/gpai-code-model-specifications",
            summary="Analysis of general-purpose AI model specification requirements and compliance practice.",
            published_date="2026-03-14",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)

    def test_dotted_ai_abbreviation_is_governance_focus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="China Seeks A.I. Independence, Weakening Trump’s Leverage",
            url="https://cset.georgetown.edu/article/china-seeks-a-i-independence-weakening-trumps-leverage/",
            summary="Analysis of Chinese technology policy and model development strategy.",
            published_date="2026-05-12",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)
        self.assertIn("中国与上海相关", scored.topic_tags)

    def test_data_factor_policy_is_digital_economy_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title='Three-Year Action Plan for "Data Factor of Production ×"',
            url="https://cset.georgetown.edu/publication/china-data-3-year-action-plan-2024-2026/",
            summary="Policy translation on data factor deployment and digital economic transformation.",
            published_date="2026-05-07",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1", "P2"})
        self.assertIn("数字经济", scored.topic_tags)

    def test_quantum_navigation_report_is_technology_innovation_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cnas-tech",
            institution_name="CNAS Technology and National Security",
            institution_type="think_tank",
            title="Atomic Advantage",
            url="https://www.cnas.org/publications/reports/atomic-advantage",
            summary="Report on quantum navigation and strategic technology competition.",
            published_date="2025-05-28",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)

    def test_broad_innovation_support_report_enters_p1_without_ai_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="Productivity Growth Through Technology Diffusion",
            url="https://www.bruegel.org/policy-brief/productivity-growth-through-technology-diffusion",
            summary="A policy brief on technology diffusion and productivity growth.",
            published_date="2026-06-22",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_technology_policy_report_enters_broad_profile_as_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        profile = load_search_profiles("config/search_profiles.yaml")["broad_innovation_support"]
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND Corporation",
            institution_type="think_tank",
            title="Technology Policy for National Competitiveness",
            url="https://www.rand.org/pubs/research_reports/technology-policy-national-competitiveness.html",
            summary="A report on technology policy, standards, regulatory capacity, and national competitiveness.",
            published_date="2026-06-19",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("科技治理", scored.topic_tags)
        self.assertTrue(candidate_matches_search_profile(scored, profile))

    def test_core_innovation_support_article_enters_p1_without_ai_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title="Canada's Research Budget Does Not Match Its Innovation Strategy",
            url="https://itif.org/publications/2026/06/16/canadas-research-budget/",
            summary="A short analysis of research budget choices and innovation strategy.",
            published_date="2026-06-16",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_innovation_support_system_terms_enter_p1_without_governance_language(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="ida-stpi",
            institution_name="IDA Science and Technology Policy Institute",
            institution_type="federally_funded_research_center",
            title="Innovation Support Systems and Technology Scale-Up",
            url="https://www.ida.org/research/innovation-support-systems",
            summary=(
                "A report on research and technology organizations, pre-commercial procurement, "
                "regulatory sandboxes, innovation investment, and technology accelerators."
            ),
            published_date="2026-06-17",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_substantive_innovation_report_enters_p1_without_source_bonus(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="Strengthening Regional Innovation Systems",
            url="https://www.rand.org/pubs/research_reports/innovation-systems.html",
            summary="A research report on regional innovation systems and technology diffusion.",
            published_date="2026-06-20",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_digital_transformation_report_enters_p1_without_ai_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="Digital Transformation and Public Service Productivity",
            url="https://www.rand.org/pubs/research_reports/digital-transformation.html",
            summary="A research report on digital transformation and digital infrastructure.",
            published_date="2026-06-21",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("数字经济", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_data_access_and_interoperability_are_digital_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="alan-turing",
            institution_name="The Alan Turing Institute",
            institution_type="research_institute",
            title="Data Access and Interoperability for Enterprise Digitalization",
            url="https://www.turing.ac.uk/publications/data-access-interoperability",
            summary=(
                "A report on data availability, data interoperability, digital technology adoption, "
                "and public data infrastructure."
            ),
            published_date="2026-05-14",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("数字经济", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_china_context_report_alone_remains_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="csis",
            institution_name="CSIS",
            institution_type="think_tank",
            title="China and Europe Diplomatic Dialogue",
            url="https://example.org/report/china-europe-dialogue",
            summary="A report on diplomatic relations and ministerial exchanges with PRC officials.",
            published_date="2026-06-22",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertEqual(scored.topic_tags, ["中国与上海相关"])
        self.assertEqual(scored.translation_level, "summary")

    def test_regional_innovation_support_report_enters_p1_without_governance_terms(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="belfer",
            institution_name="Harvard Belfer Center Science, Technology, and Public Policy",
            institution_type="university_research_center",
            title="Building Regional Innovation Engines",
            url="https://www.belfercenter.org/publication/regional-innovation-engines",
            summary=(
                "A report on place-based innovation, research universities, technology transfer, "
                "innovation finance, and university-industry collaboration."
            ),
            published_date="2026-06-18",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)
        self.assertNotIn("科技治理", scored.topic_tags)

    def test_biomanufacturing_and_industrial_competitiveness_are_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cnas-tech",
            institution_name="CNAS Technology and National Security",
            institution_type="think_tank",
            title="Biomanufacturing and Industrial Competitiveness",
            url="https://www.cnas.org/publications/reports/biomanufacturing-industrial-competitiveness",
            summary="Report on biotechnology leadership, innovation capacity, supply chain resilience, and public R&D.",
            published_date="2026-05-18",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("先进制造", scored.topic_tags)

    def test_industrial_upgrading_report_enters_p1_as_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="merics",
            institution_name="MERICS Industrial Policy and Technology",
            institution_type="think_tank",
            title="Industrial Upgrading and Technology Finance for Innovation Capacity",
            url="https://merics.org/en/report/industrial-upgrading-and-technology-finance-innovation-capacity",
            summary="A report on industrial upgrading, technology upgrading, technology finance, and innovation capacity.",
            published_date="2026-06-30",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_clean_energy_technology_report_enters_p1_without_governance_terms(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="orf-america",
            institution_name="ORF America Technology Policy",
            institution_type="think_tank",
            title="Green Industrial Policy and Energy Technology Scale-Up",
            url="https://orfamerica.org/newresearch/green-industrial-policy-and-energy-technology-scale-up",
            summary="A report on clean tech, energy technology, industrial competitiveness, and innovation diffusion.",
            published_date="2026-06-29",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("先进制造", scored.topic_tags)
        self.assertNotIn("科技治理", scored.topic_tags)

    def test_orf_article_without_pdf_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="orf-america",
            institution_name="ORF America Technology Policy",
            institution_type="think_tank",
            title="Why the UAE's OPEC exit signals a deeper recalibration of state autonomy",
            url="https://orfamerica.org/newresearch/uae-opec-exit-signals-a-deeper-recalibration-of-state-autonomy",
            summary="This article discusses critical minerals, technology standards, industrial policy, and cross-border finance.",
            published_date="2026-05-01",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("先进制造", scored.topic_tags)

    def test_data_centers_are_digital_infrastructure_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="brookings-cti",
            institution_name="Brookings Center for Technology Innovation",
            institution_type="think_tank",
            title="Orbital data centers' feasibility gap is a governance risk",
            url="https://www.brookings.edu/articles/orbital-data-centers-feasibility-gap-is-a-governance-risk/",
            summary="Analysis of data centers, compute infrastructure, and governance risk.",
            published_date="2026-06-25",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("数字经济", scored.topic_tags)

    def test_power_grid_resilience_article_enters_p1_as_innovation_infrastructure(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="belfer",
            institution_name="Harvard Belfer Center Science, Technology, and Public Policy",
            institution_type="university_research_center",
            title="Navigating the Grid's Perfect Storm: Building a Resilient and Reliable Power System",
            url="https://www.belfercenter.org/research-analysis/navigating-grids-perfect-storm-building-resilient-and-reliable-power-system",
            summary=(
                "A policy article on grid resilience, power systems, AI data centers, "
                "energy infrastructure, and electricity infrastructure."
            ),
            published_date="2025-11-19",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("先进制造", scored.topic_tags)
        self.assertIn("数字经济", scored.topic_tags)

    def test_non_report_book_announcement_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="belfer",
            institution_name="Harvard Belfer Center Science, Technology, and Public Policy",
            institution_type="university_research_center",
            title="Jimmy Carter and China: Multilateral Competition in the Global Cold War",
            url="https://www.belfercenter.org/research-analysis/jimmy-carter-and-china-multilateral-competition-global-cold-war",
            summary=(
                "Sheng Peng's new book highlights global supply chains for defense and dual-use "
                "technologies, technological competition, and US-China relations."
            ),
            published_date="2026-06-01",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("科技创新", scored.topic_tags)

    def test_media_mention_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="The AI arms race's sneakiest tactic",
            url="https://cset.georgetown.edu/article/the-ai-arms-races-sneakiest-tactic/",
            summary=(
                "CSET's Kyle Miller shared his expert insight in a newsletter published by Politico. "
                "The newsletter examines Chinese efforts to replicate AI capabilities and strategic technology competition."
            ),
            published_date="2026-04-29",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("AI治理", scored.topic_tags)

    def test_cset_in_the_news_media_page_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Anthropic boss rejects Pentagon demand to drop AI safeguards",
            url="https://cset.georgetown.edu/article/anthropic-boss-rejects-pentagon-demand/",
            summary=(
                "In The News. CSET's Helen Toner shared her insight in an article "
                "published by The Financial Times. Original Publisher Financial Times. "
                "Read Article. The article discusses military AI safeguards."
            ),
            published_date="2026-02-27",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("AI治理", scored.topic_tags)

    def test_cset_highlighted_external_article_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="1 big thing: AI could soon improve on its own",
            url="https://cset.georgetown.edu/article/1-big-thing-ai-could-soon-improve-on-its-own/",
            summary=(
                "A CSET workshop report was highlighted in an article published by Axios "
                "in its Axios+ newsletter. To read the newsletter, visit Axios."
            ),
            published_date="2026-01-27",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("AI治理", scored.topic_tags)

    def test_cset_external_interview_page_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Anthropic boss rejects Pentagon demand to drop AI safeguards",
            url="https://cset.georgetown.edu/article/anthropic-boss-rejects-pentagon-demand/",
            summary=(
                "CSET's Owen Daniels was featured on BBC News, where he discussed "
                "military AI safeguards and autonomous weapons systems. "
                "To learn more, visit BBC News."
            ),
            published_date="2026-02-27",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("AI治理", scored.topic_tags)

    def test_says_itif_press_release_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title=(
                "EU's Designation of AWS and Azure as Core Platform Services "
                "Escalates Weaponization of Digital Markets Act, Says ITIF"
            ),
            url="https://itif.org/publications/2026/06/25/eu-designation-aws-azure-says-itif/",
            summary="Cloud services and digital markets regulation may affect digital innovation.",
            published_date="2026-06-25",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("数字经济", scored.topic_tags)

    def test_institutional_award_update_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Georgetown's Center for Security and Emerging Technology Awarded $2M Google.org Funding",
            url="https://cset.georgetown.edu/article/google-funding-award/",
            summary="The funding will support research on technology innovation and AI policy.",
            published_date="2026-02-26",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("科技创新", scored.topic_tags)

    def test_institutional_testimony_update_is_capped_below_p1(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title=(
                "CSET Senior Fellow Testifies Before U.S.-China Economic "
                "and Security Review Commission"
            ),
            url="https://cset.georgetown.edu/article/senior-fellow-testifies-uscc/",
            summary="The testimony discussed China, science policy, and emerging technology competition.",
            published_date="2026-04-30",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("科技创新", scored.topic_tags)

    def test_advanced_compute_access_is_digital_infrastructure_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="The National Security Case for Limiting China's Access to Advanced U.S. Compute",
            url="https://cset.georgetown.edu/article/advanced-compute-access",
            summary="Evidence from PLA procurement documents about advanced compute access and AI development.",
            published_date="2026-04-20",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("数字经济", scored.topic_tags)
        self.assertIn("中国与上海相关", scored.topic_tags)

    def test_advanced_industries_are_manufacturing_and_innovation_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title="China Is Rapidly Becoming a Leading Innovator in Advanced Industries",
            url="https://itif.org/publications/advanced-industries",
            summary="Advanced industries, technology competition, and national power industries shape industrial policy.",
            published_date="2024-09-16",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("先进制造", scored.topic_tags)

    def test_defense_industrial_base_is_advanced_manufacturing_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="aspi",
            institution_name="Australian Strategic Policy Institute",
            institution_type="think_tank",
            title="Australia's defence industry needs a government investment fund",
            url="https://www.aspistrategist.org.au/australias-defence-industry-needs-a-government-investment-fund/",
            summary=(
                "Analysis of industrial depth, a self-reliant industrial base, "
                "defence industry development, sustainment, and prolonged operations."
            ),
            published_date="2026-07-03",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("先进制造", scored.topic_tags)

    def test_stem_research_policy_is_talent_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title="Mobilizing for Techno-Economic War, Part 5: Transforming STEM Research Policy",
            url="https://itif.org/publications/stem-research-policy",
            summary="STEM research policy, technology talent, and techno-economic war.",
            published_date="2026-06-17",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("科技人才", scored.topic_tags)
        self.assertIn("科技治理", scored.topic_tags)

    def test_research_funding_and_lab_talent_are_innovation_support_signals(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title="NIH Researchers and Research Funding Changes",
            url="https://itif.org/publications/2026/06/29/nih-researchers-research-funding-changes/",
            summary="Research labs lost NIH researchers after science funding and research grants changed.",
            published_date="2026-06-29",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("科技人才", scored.topic_tags)

    def test_public_trust_in_science_is_science_system_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="Public Trust in Science and Scientific Trustworthiness",
            url="https://www.rand.org/pubs/external_publications/public-trust-in-science.html",
            summary=(
                "A report on science communication, research integrity, and evidence-based policy "
                "as foundations of the research ecosystem."
            ),
            published_date="2026-06-26",
            content_type="external_publication",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_stem_pipeline_is_talent_support_without_ai_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="rand",
            institution_name="RAND",
            institution_type="think_tank",
            title="Aspire to STEM: Evaluation Report",
            url="https://www.rand.org/pubs/external_publications/stem-aspire.html",
            summary="A report on STEM outreach, STEM participation, STEM pipeline, and science literacy.",
            published_date="2026-06-26",
            content_type="external_publication",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技人才", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_government_funded_research_is_innovation_support_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Government-Funded Research Seeds Entire Industries. What Would Be Lost Without It.",
            url="https://cset.georgetown.edu/article/government-funded-research-seeds-entire-industries-what-would-be-lost-without-it/",
            summary="NIH-backed research plays a foundational role in medical innovation and biotechnology growth.",
            published_date="2026-05-05",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P1", "P2"})
        self.assertIn("科技创新", scored.topic_tags)

    def test_public_investment_and_sti_indicators_are_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="nistep",
            institution_name="National Institute of Science and Technology Policy Japan",
            institution_type="government_research_institute",
            title="Science and Technology Indicators and Strategic Public Investment",
            url="https://www.nistep.go.jp/en/publication/science-technology-indicators",
            summary=(
                "A report on STI indicators, public investment, research budgets, "
                "scientific capacity, and innovation performance."
            ),
            published_date="2026-06-08",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_metascience_and_research_productivity_are_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="ida-stpi",
            institution_name="IDA Science and Technology Policy Institute",
            institution_type="government_research_institute",
            title="Metascience, Research Productivity, and Federal R&D Evaluation",
            url="https://www.ida.org/research/metascience-research-productivity",
            summary=(
                "A report on science of science, research assessment, research productivity, "
                "and federal R&D evaluation."
            ),
            published_date="2026-05-20",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_innovation_agencies_and_spinouts_are_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="Innovation Agencies, University Spinouts, and Technology Transfer Offices",
            url="https://www.bruegel.org/policy-brief/innovation-agencies-university-spinouts",
            summary=(
                "A policy brief on innovation agencies, technology transfer offices, "
                "IP commercialization, and university spinout companies."
            ),
            published_date="2026-04-15",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_innovation_tax_incentives_and_intangible_capital_are_support_signals(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="ecipe",
            institution_name="ECIPE",
            institution_type="think_tank",
            title="R&D Tax Credits and Intangible Investment for Innovation Growth",
            url="https://ecipe.org/research/rd-tax-credits-intangible-investment/",
            summary=(
                "A report on research tax credits, innovation tax incentives, "
                "intangible capital, patent boxes, and capital markets for innovation."
            ),
            published_date="2026-04-12",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_testing_standards_and_industrial_commons_are_support_signals(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="ida-stpi",
            institution_name="IDA Science and Technology Policy Institute",
            institution_type="federally_funded_research_center",
            title="Testing Infrastructure and Industrial Commons for Scale-Up",
            url="https://www.ida.org/research/testing-infrastructure-industrial-commons",
            summary=(
                "A report on standards development, metrology, conformity assessment, "
                "testing infrastructure, demonstration plants, pilot production, "
                "and technology commons."
            ),
            published_date="2026-04-09",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_researcher_mobility_and_human_capital_are_talent_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="nistep",
            institution_name="National Institute of Science and Technology Policy Japan",
            institution_type="government_research_institute",
            title="High-Skilled Mobility and Science Human Capital",
            url="https://www.nistep.go.jp/en/publication/high-skilled-mobility",
            summary="A report on researcher mobility, scientific mobility, talent attraction, and talent retention.",
            published_date="2026-03-11",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技人才", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_ai_workforce_is_talent_support_not_only_ai_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Defining the AI Workforce",
            url="https://cset.georgetown.edu/article/defining-the-ai-workforce/",
            summary="An analysis of the AI workforce and technical workforce needed for advanced technology adoption.",
            published_date="2026-05-12",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技人才", scored.topic_tags)

    def test_ai_job_market_skills_report_is_talent_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="AI Ethics and Governance in the Job Market: Trends, Skills, and Sectoral Demand",
            url="https://cset.georgetown.edu/publication/ai-ethics-and-governance-in-the-job-market-trends-skills-and-sectoral-demand/",
            summary=(
                "Demand for an AI-literate workforce has surged to counter a growing skills gap "
                "and sectoral demand for AI ethics skills."
            ),
            published_date="2025-05-20",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("AI治理", scored.topic_tags)
        self.assertIn("科技人才", scored.topic_tags)

    def test_military_civil_fusion_is_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Pulling Back the Curtain on China's Military-Civil Fusion",
            url="https://cset.georgetown.edu/publication/pulling-back-the-curtain-on-chinas-military-civil-fusion/",
            summary="A report on China's military-civil fusion, dual-use technology, and defense technology ecosystem.",
            published_date="2025-09-02",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)

    def test_value_chain_capacity_and_skills_are_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="stepi",
            institution_name="Science and Technology Policy Institute Korea",
            institution_type="government_research_institute",
            title="Industrial Value Chains and Skills Development for Future Industries",
            url="https://www.stepi.re.kr/site/stepien/publication/value-chain-skills",
            summary=(
                "A report on industrial capacity, supply chains, value chains, "
                "skills development, reskilling, and technology development programs."
            ),
            published_date="2026-04-27",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("先进制造", scored.topic_tags)
        self.assertIn("科技人才", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_qubits_report_title_is_quantum_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cnas-tech",
            institution_name="CNAS Technology and National Security",
            institution_type="think_tank",
            title="The Quest for Qubits",
            url="https://www.cnas.org/publications/reports/the-quest-for-qubits",
            summary="A report on quantum leadership and industrial technology competition.",
            published_date="2024-05-28",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_biopower_report_title_is_biotechnology_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cnas-tech",
            institution_name="CNAS Technology and National Security",
            institution_type="think_tank",
            title="Biopower",
            url="https://www.cnas.org/publications/reports/biopower",
            summary="A report on biodata, life sciences, and biotechnology competitiveness.",
            published_date="2025-01-15",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("科技创新", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_clean_energy_supply_chains_are_advanced_manufacturing_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="orf-america",
            institution_name="ORF America Technology Policy",
            institution_type="think_tank",
            title="India's Role in Diversifying Global Clean Energy Supply Chains",
            url="https://orfamerica.org/newresearch/india-global-clean-energy-supply-chains",
            summary="A report on clean energy, solar photovoltaics, green hydrogen, and supply chain resilience.",
            published_date="2024-06-24",
            content_type="report",
            pdf_url="https://orfamerica.org/s/ORF-Full-Volume-on-India-Energy-061424.pdf",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("先进制造", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_grid_and_data_center_infrastructure_enter_broad_innovation_profile(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        profile = load_search_profiles("config/search_profiles.yaml")["broad_innovation_support"]
        candidate = ArticleCandidate(
            institution_slug="orf-america",
            institution_name="ORF America Technology Policy",
            institution_type="think_tank",
            title="Grids and Data Centers for AI-Ready Infrastructure",
            url="https://orfamerica.org/newresearch/grids-data-centers-ai-infrastructure",
            summary=(
                "A policy brief on renewable energy, smart grids, microgrids, battery storage, "
                "grid interconnection, data centers, and workforce development for AI-ready infrastructure."
            ),
            published_date="2026-01-08",
            content_type="brief",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("先进制造", scored.topic_tags)
        self.assertIn("数字经济", scored.topic_tags)
        self.assertIn("科技人才", scored.topic_tags)
        self.assertTrue(candidate_matches_search_profile(scored, profile))

    def test_cloud_services_and_dma_are_digital_technology_policy_signals(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title="Cloud Hidden, Rationale Unknown: The DMA's Foggy Attack on AWS and Azure",
            url="https://itif.org/publications/2026/07/02/cloud-hidden-rationale-unknown-dma-foggy-attack-aws-azure/",
            summary="If AWS and Azure are designated under the Digital Markets Act, cloud services may face technology policy distortions.",
            published_date="2026-07-02",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1", "P2"})
        self.assertIn("数字经济", scored.topic_tags)
        self.assertIn("科技治理", scored.topic_tags)

    def test_space_spectrum_allocation_is_digital_infrastructure_policy(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title="Rigid Space Spectrum Allocations Could Limit Productivity",
            url="https://itif.org/publications/2026/07/01/rigid-space-spectrum-allocations-could-limit-productivity/",
            summary="Restrictive spectrum allocations could hinder the orbital economy and future communications infrastructure.",
            published_date="2026-07-01",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P1", "P2"})
        self.assertIn("数字经济", scored.topic_tags)

    def test_compute_infrastructure_article_enters_p1_as_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Public Compute Infrastructure for Research Access",
            url="https://cset.georgetown.edu/article/public-compute-infrastructure-research-access/",
            summary="Public compute, sovereign compute, data access, and cloud infrastructure support applied projects.",
            published_date="2026-06-10",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P1")
        self.assertIn("数字经济", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_technology_absorption_and_rto_capacity_enter_p1_without_ai_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="ida-stpi",
            institution_name="IDA Science and Technology Policy Institute",
            institution_type="federally_funded_research_center",
            title="Research and Technology Organizations for Industrial Extension",
            url="https://www.ida.org/research/rto-industrial-extension",
            summary=(
                "A report on RTOs, technology absorption, manufacturing extension, "
                "metrology, quality infrastructure, and engineering talent."
            ),
            published_date="2026-05-18",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("科技人才", scored.topic_tags)
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_general_cybersecurity_article_does_not_enter_p1_without_infrastructure_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Cybersecurity Incident Response Lessons",
            url="https://cset.georgetown.edu/article/cybersecurity-incident-response-lessons/",
            summary="Cybersecurity risk management practices for organizations.",
            published_date="2026-06-10",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P2")
        self.assertIn("数字经济", scored.topic_tags)

    def test_chinese_technology_is_innovation_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="merics",
            institution_name="MERICS Industrial Policy and Technology",
            institution_type="think_tank",
            title="EU: Shepherded by Brussels, Europe awakens to Chinese technology",
            url="https://merics.org/en/report/eu-shepherded-brussels-europe-awakens-chinese-technology",
            summary="Europe's policy response to Chinese technology competition.",
            published_date="2026-06-30",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("中国与上海相关", scored.topic_tags)

    def test_lunar_crewed_landing_is_space_technology_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="NASA's lunar success sharpens focus on China's 2030 crewed landing goal",
            url="https://cset.georgetown.edu/article/china-2030-crewed-landing",
            summary="Analysis of space technology competition and China's lunar program.",
            published_date="2026-04-08",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("科技创新", scored.topic_tags)
        self.assertIn("中国与上海相关", scored.topic_tags)

    def test_hardware_chokepoints_are_semiconductor_and_tech_control_signals(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="Multilateral Controls on Hardware Chokepoints",
            url="https://cset.georgetown.edu/publication/multilateral-controls-on-hardware-chokepoints/",
            summary="Policy analysis on hardware chokepoints in advanced computing supply chains.",
            published_date="2026-06-09",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("半导体", scored.topic_tags)
        self.assertIn("科技治理", scored.topic_tags)

    def test_national_security_alone_does_not_create_defense_ai_tag(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="itif",
            institution_name="Information Technology and Innovation Foundation",
            institution_type="think_tank",
            title="Economic Consequences of Section 232 Tariffs on Semiconductor Imports",
            url="https://itif.org/publications/semiconductor-tariffs/",
            summary="Semiconductor tariffs imposed on national security grounds would raise ICT prices and reduce economic growth.",
            published_date="2026-06-24",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("半导体", scored.topic_tags)
        self.assertIn("科技治理", scored.topic_tags)
        self.assertNotIn("国防AI", scored.topic_tags)

    def test_defense_technology_alone_does_not_create_defense_ai_tag(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="atlantic-council-geotech",
            institution_name="Atlantic Council GeoTech Center and Cyber Statecraft Initiative",
            institution_type="think_tank",
            title="US and Germany Sign Homeland Defense Technology Sharing Agreement",
            url="https://www.atlanticcouncil.org/blogs/new-atlanticist/us-and-germany-sign-homeland-defense-technology-sharing-agreement/",
            summary="A short institutional update about homeland defense technology cooperation.",
            published_date="2009-03-16",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P3")
        self.assertNotIn("国防AI", scored.topic_tags)

    def test_defense_ai_article_enters_p1_as_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="example-source",
            institution_name="Example Source",
            institution_type="think_tank",
            title="Autonomous Weapons Integration for Defense Planning",
            url="https://example.org/autonomous-weapons-defense-planning",
            summary="An article on autonomous weapons, cyber operations, procurement pathways, and test infrastructure.",
            published_date="2026-06-18",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("国防AI", scored.topic_tags)

    def test_classified_dod_ai_work_is_defense_ai_signal(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="cset",
            institution_name="Center for Security and Emerging Technology",
            institution_type="university_research_center",
            title="DOD expands its classified AI work with technology companies",
            url="https://cset.georgetown.edu/article/dod-expands-classified-ai-work/",
            summary=(
                "The article explores the Pentagon's growing efforts to integrate "
                "classified AI capabilities into military operations through partnerships "
                "with private technology companies."
            ),
            published_date="2026-05-01",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn("国防AI", scored.topic_tags)
        self.assertIn(scored.priority, {"P0", "P1", "P2"})

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

    def test_single_incidental_technology_word_does_not_promote_report(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="Annual economic outlook with one technology reference",
            url="https://example.org/economic-outlook",
            summary="The report mentions technology once while focusing on fiscal balances and monetary policy.",
            published_date="2026-07-01",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P3")
        self.assertEqual(scored.topic_tags, [])

    def test_generic_regulation_word_does_not_create_technology_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="European Union capital requirements on megabanks",
            url="https://www.bruegel.org/working-paper/european-union-capital-requirements-megabanks",
            summary="Working paper on financial regulation, bank capital, and monetary stability.",
            published_date="2026-07-03",
            content_type="paper",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P3")
        self.assertNotIn("科技治理", scored.topic_tags)

    def test_generic_data_policy_fragment_does_not_create_technology_governance(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="bruegel",
            institution_name="Bruegel",
            institution_type="think_tank",
            title="European natural gas imports",
            url="https://www.bruegel.org/dataset/european-natural-gas-imports",
            summary="Dataset page with energy storage charts and a generic data policy footer fragment.",
            published_date="2026-07-02",
            content_type="dataset",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P3")
        self.assertNotIn("科技治理", scored.topic_tags)

    def test_single_incidental_ai_mention_does_not_promote_general_article(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="csis",
            institution_name="CSIS",
            institution_type="think_tank",
            title="Russian Blood and Treasure: The Ballooning Costs of Putin's War",
            url="https://www.csis.org/analysis/russian-blood-and-treasure-ballooning-costs-putins-war",
            summary="Ukraine conducted deep strikes into Russian territory, including with AI-enabled drones.",
            published_date="2026-07-01",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P3")
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_single_incidental_ai_mention_does_not_promote_general_report(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        candidate = ArticleCandidate(
            institution_slug="csis",
            institution_name="CSIS",
            institution_type="think_tank",
            title="Russian Blood and Treasure: The Ballooning Costs of Putin's War",
            url="https://www.csis.org/analysis/russian-blood-and-treasure-ballooning-costs-putins-war",
            summary="The report estimates casualties and notes that Ukraine has used AI-enabled drones.",
            published_date="2026-07-01",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertEqual(scored.priority, "P3")
        self.assertNotIn("AI治理", scored.topic_tags)

    def test_space_policy_and_entrepreneurship_ecosystem_enter_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        profile = load_search_profiles("config/search_profiles.yaml")["broad_innovation_support"]
        candidate = ArticleCandidate(
            institution_slug="carnegie-tech",
            institution_name="Carnegie Technology and International Affairs Program",
            institution_type="think_tank",
            title="A Review of India's 2023 Space Policy and Entrepreneurship Ecosystem",
            url="https://carnegieendowment.org/india/research/2026/05/indian-space-policy-review-entrepreneurship-and-innovation-ecosystem",
            summary="Policy review of commercial space, space startups, and the entrepreneurship ecosystem.",
            published_date="2026-06-01",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("科技创新", scored.topic_tags)
        self.assertTrue(candidate_matches_search_profile(scored, profile))

    def test_nuclear_energy_supply_for_hyperscalers_enters_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        profile = load_search_profiles("config/search_profiles.yaml")["broad_innovation_support"]
        candidate = ArticleCandidate(
            institution_slug="carnegie-tech",
            institution_name="Carnegie Technology and International Affairs Program",
            institution_type="think_tank",
            title="Beyond the Hype: Assessing Hyperscaler Nuclear Commitments Against U.S. Energy Realities",
            url="https://carnegieendowment.org/research/2026/06/beyond-the-hype-assessing-hyperscaler-nuclear-commitments-against-us-energy-realities",
            summary="Analysis of nuclear energy, advanced nuclear, and hyperscaler nuclear commitments for data center power demand.",
            published_date="2026-06-02",
            content_type="report",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("先进制造", scored.topic_tags)
        self.assertIn("数字经济", scored.topic_tags)
        self.assertTrue(candidate_matches_search_profile(scored, profile))

    def test_commercial_fusion_energy_is_innovation_support(self):
        topics = load_topics("config/topics.yaml")
        rules = load_priority_rules("config/priorities.yaml")
        profile = load_search_profiles("config/search_profiles.yaml")["broad_innovation_support"]
        candidate = ArticleCandidate(
            institution_slug="belfer",
            institution_name="Harvard Belfer Center Science, Technology, and Public Policy",
            institution_type="university_research_center",
            title="Notes on the Recent Hype about Imminence of Commercial Fusion Energy",
            url="https://www.belfercenter.org/research-analysis/notes-recent-hype-about-imminence-commercial-fusion-energy",
            summary="A research analysis on fusion energy, commercial fusion timelines, and energy technology readiness.",
            published_date="2026-04-21",
            content_type="article",
        )

        scored = score_candidate(candidate, topics, rules)

        self.assertIn(scored.priority, {"P0", "P1"})
        self.assertIn("先进制造", scored.topic_tags)
        self.assertTrue(candidate_matches_search_profile(scored, profile))


if __name__ == "__main__":
    unittest.main()
