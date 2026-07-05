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
        for slug in {"aspi", "belfer", "bruegel", "csis", "ecipe", "ida-stpi", "nistep", "orf-america", "stepi"}:
            self.assertEqual(
                {item.batch for item in institutions if item.slug == slug},
                {1},
                f"{slug} should be in the broad innovation-support daily pool",
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

        self.assertEqual(scored.priority, "P1")
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

        self.assertIn(scored.priority, {"P0", "P1", "P2"})
        self.assertIn("数字经济", scored.topic_tags)

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


if __name__ == "__main__":
    unittest.main()
