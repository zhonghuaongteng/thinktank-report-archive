import unittest

from scripts.extend_viewpoint_eu_stoa_light_catalog import (
    classify_relevance,
    parse_listing_html,
    report_id,
    should_replace_previous_light_row,
)


SAMPLE_HTML = """
<div id="indexDisplayedResultsLabel">Showing 20 of 381 results</div>
<div class="es_document">
  <h3 class="es_document-title"><a href="/stoa/en/document/EPRS_STU(2026)774682">'Widening' Indicator: Leveraging the potential for inclusive European research and innovation</a></h3>
  <div class="es_document-subtitle">
    <span class="es_document-subtitle-documenttype">Study</span>
    <span class="es_document-subtitle-date">22-05-2026</span>
  </div>
  <div class="es_document-body"><p>Horizon Europe supports research capacity and innovation performance.</p></div>
</div>
<div class="es_document">
  <h3 class="es_document-title"><a href="/stoa/en/document/EPRS_BRI(2026)774707">Quantum technologies: Can they boost Europe's decarbonisation?</a></h3>
  <div class="es_document-subtitle">
    <span class="es_document-subtitle-documenttype">Briefing</span>
    <span class="es_document-subtitle-date">16-02-2026</span>
  </div>
  <div class="es_document-body"><p>Quantum research, industrial applications and the EU innovation ecosystem.</p></div>
</div>
"""


class EuStoaLightCatalogTests(unittest.TestCase):
    def test_parses_official_listing_rows(self):
        total, items = parse_listing_html(SAMPLE_HTML)
        self.assertEqual(total, 381)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].published, "2026-05-22")
        self.assertEqual(items[0].publication_type, "Study")
        self.assertEqual(items[1].document_code, "EPRS_BRI(2026)774707")

    def test_science_and_technology_innovation_takes_priority(self):
        self.assertEqual(
            classify_relevance("Research and innovation capacity", "Horizon Europe, laboratories and scientific infrastructure"),
            "核心",
        )
        self.assertEqual(
            classify_relevance("Quantum technologies", "industrial applications and technology assessment"),
            "核心",
        )

    def test_security_or_general_governance_only_material_is_context(self):
        self.assertEqual(classify_relevance("Security threats", "military operations and border control"), "语境")
        self.assertEqual(classify_relevance("Citizen participation", "digital voting and parliamentary procedure"), "语境")

    def test_report_id_uses_official_document_code(self):
        self.assertEqual(report_id("EPRS_STU(2026)774682"), "C-EU-STOA-EPRS-STU-2026-774682")

    def test_rerun_only_replaces_generated_assetless_rows(self):
        previous = {"C-EU-STOA-EPRS-STU-2026-774682"}
        generated = {
            "报告ID": "C-EU-STOA-EPRS-STU-2026-774682",
            "机构ID": "eu-stoa",
            "样本角色": "欧洲议会STOA近十年科技评估轻量总目录",
            "本地原始资产路径": "",
        }
        selected = dict(generated, 样本角色="欧洲议会STOA科技创新精选全文", 本地原始资产路径="x.pdf")
        self.assertTrue(should_replace_previous_light_row(generated, previous))
        self.assertFalse(should_replace_previous_light_row(selected, previous))


if __name__ == "__main__":
    unittest.main()
