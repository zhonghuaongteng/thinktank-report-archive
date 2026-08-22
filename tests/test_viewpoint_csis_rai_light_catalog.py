import unittest

from scripts.extend_viewpoint_csis_rai_light_catalog import (
    classify_relevance,
    parse_listing_html,
    report_id,
    should_replace_previous_light_row,
)


SAMPLE_HTML = """
<div class="csis-search-results-text">1 - 2 of 43 results</div>
<div class="views-row">
  <article class="report-search-listing">
    <h3><a href="/analysis/understanding-chinas-quest-quantum-advancement">Understanding China’s Quest for Quantum Advancement</a></h3>
    <div class="search-listing--summary">China is investing in quantum research, talent, and commercialization.</div>
    <div class="contributors"><p>Report by A. Scholar — January 29, 2026</p></div>
  </article>
</div>
<div class="views-row">
  <article class="article-search-listing">
    <h3><a href="/analysis/innovation-lightbulb">Innovation Lightbulb</a></h3>
    <div class="search-listing--summary">Federal R&amp;D and basic science support the innovation ecosystem.</div>
    <div class="contributors"><p>Newsletter by B. Scholar — June 10, 2025</p></div>
  </article>
</div>
"""


class CsisRaiLightCatalogTests(unittest.TestCase):
    def test_parses_official_program_view_rows(self):
        total, items = parse_listing_html(SAMPLE_HTML)
        self.assertEqual(total, 43)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].published, "2026-01-29")
        self.assertEqual(items[0].content_type, "Report")
        self.assertEqual(items[0].authors, "A. Scholar")
        self.assertEqual(items[1].content_type, "Article")
        self.assertEqual(items[1].subtype, "Newsletter")

    def test_science_and_technology_mechanisms_take_priority(self):
        self.assertEqual(classify_relevance("Federal R&D", "basic science funding and research infrastructure"), "核心")
        self.assertEqual(classify_relevance("Quantum Commercialization", "technology transfer and regional innovation"), "核心")
        self.assertEqual(classify_relevance("Building the Workforce", "STEM skills for technical occupations"), "支撑")

    def test_security_only_material_remains_context(self):
        self.assertEqual(classify_relevance("Military Deterrence", "weapons posture and operational planning"), "语境")

    def test_report_id_is_program_scoped_and_stable(self):
        self.assertEqual(
            report_id("2026-01-29", "https://www.csis.org/analysis/understanding-chinas-quest-quantum-advancement"),
            "C-CSIS-RAI-2026-UNDERSTANDING-CHINAS-QUEST-QUANTUM-ADVANCEMENT",
        )

    def test_rerun_only_replaces_generated_assetless_rows(self):
        previous = {"C-CSIS-RAI-2026-X"}
        generated = {"报告ID": "C-CSIS-RAI-2026-X", "机构ID": "csis-rai", "样本角色": "CSIS RAI科技创新项目轻量总目录", "本地原始资产路径": ""}
        selected = {"报告ID": "C-CSIS-RAI-2026-X", "机构ID": "csis-rai", "样本角色": "CSIS RAI科技创新精选全文", "本地原始资产路径": "x.html"}
        existing_csis = {"报告ID": "S-CSIS-2026-01", "机构ID": "csis", "样本角色": "官方锚点", "本地原始资产路径": ""}
        self.assertTrue(should_replace_previous_light_row(generated, previous))
        self.assertFalse(should_replace_previous_light_row(selected, previous))
        self.assertFalse(should_replace_previous_light_row(existing_csis, previous))


if __name__ == "__main__":
    unittest.main()
