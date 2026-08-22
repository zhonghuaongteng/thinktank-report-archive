import json
import subprocess
import unittest

from scripts.extend_viewpoint_fas_light_catalog import (
    api_url,
    china_signal,
    classify_relevance,
    normalize_post,
    report_id,
    should_replace_previous_light_row,
)


class FasLightCatalogTests(unittest.TestCase):
    def test_normalizes_official_wordpress_publication(self):
        post = {
            "id": 42007,
            "date": "2026-06-18T09:00:00",
            "slug": "the-civic-research-agenda",
            "link": "https://fas.org/publication/the-civic-research-agenda/",
            "title": {"rendered": "The Civic Research Agenda"},
            "excerpt": {"rendered": "<p>Research priorities for civic innovation.</p>"},
            "publication-type": [12, 770],
        }
        item = normalize_post(post)
        self.assertEqual(item.post_id, 42007)
        self.assertEqual(item.date, "2026-06-18")
        self.assertEqual(item.title, "The Civic Research Agenda")
        self.assertEqual(item.summary, "Research priorities for civic innovation.")
        self.assertEqual(item.publication_types, ("Report", "Policy Memo"))

    def test_research_and_innovation_mechanisms_are_core(self):
        self.assertEqual(classify_relevance("Estimating Government ROI on Scientific R&D", "science funding"), "核心")
        self.assertEqual(classify_relevance("A National Institute for High-Reward Research", "new research institutions"), "核心")
        self.assertEqual(classify_relevance("Fueling the Bioeconomy", "biotechnology innovation"), "核心")

    def test_talent_infrastructure_and_diffusion_are_supporting(self):
        self.assertEqual(classify_relevance("The Federal STEM Workforce", "skills and research capacity"), "支撑")
        self.assertEqual(classify_relevance("Regional Innovation Capacity", "technology diffusion and infrastructure"), "支撑")

    def test_security_only_publications_remain_context(self):
        self.assertEqual(classify_relevance("Nuclear Command and Control", "deterrence and missile forces"), "语境")
        self.assertEqual(classify_relevance("A Missile Pre-Launch Agreement", "nuclear risk reduction"), "语境")
        self.assertEqual(classify_relevance("Artificial Intelligence and Nuclear Security", "weapons and deterrence"), "语境")

    def test_explicit_china_signal_only(self):
        self.assertTrue(china_signal("Emerging Tech and Competitiveness", "competition with China"))
        self.assertTrue(china_signal("Industrial Policy", "Chinese legacy chips"))
        self.assertFalse(china_signal("Global Technology Competition", "Asian economies"))

    def test_report_id_is_stable(self):
        self.assertEqual(report_id("2026-04-07", "roi-of-rd"), "C-FAS-2026-ROI-OF-RD")

    def test_api_url_is_official_and_type_scoped(self):
        url = api_url(2025, 770, page=2)
        self.assertTrue(url.startswith("https://fas.org/wp-json/wp/v2/publications?"))
        self.assertIn("publication-type=770", url)
        self.assertIn("page=2", url)
        self.assertIn("per_page=100", url)

    def test_rerun_replaces_only_generated_assetless_fas_rows(self):
        previous = {"C-FAS-2026-X"}
        generated = {"报告ID": "C-FAS-2026-X", "机构ID": "fas", "样本角色": "FAS报告与政策备忘录近十年轻量总目录", "本地原始资产路径": ""}
        selected = {"报告ID": "C-FAS-2026-X", "机构ID": "fas", "样本角色": "FAS科技创新精选全文", "本地原始资产路径": "网页原文/x.html"}
        seed = {"报告ID": "S-FAS-2026-01", "机构ID": "fas", "样本角色": "官方锚点", "本地原始资产路径": ""}
        self.assertTrue(should_replace_previous_light_row(generated, previous))
        self.assertFalse(should_replace_previous_light_row(selected, previous))
        self.assertFalse(should_replace_previous_light_row(seed, previous))

    def test_collection_javascript_is_valid(self):
        script = "fetch('https://fas.org/wp-json/wp/v2/publications').then(r=>r.json())"
        check = subprocess.run(["node", "-e", f"new Function({json.dumps(script)})"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)


if __name__ == "__main__":
    unittest.main()
