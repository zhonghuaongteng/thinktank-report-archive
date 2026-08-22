import unittest
import json
import subprocess

from scripts.extend_viewpoint_itif_reports_catalog import (
    classify_relevance,
    direct_china_signal,
    extract_listing_cards,
    in_research_window,
    listing_state_script,
    next_page_script,
    page_signature,
    normalize_listing_item,
    report_id,
    restore_missing_itif_seeds,
    should_replace_previous_light_row,
    wait_until,
)


class ItifReportsCatalogTests(unittest.TestCase):
    def test_normalizes_official_report_listing_metadata(self):
        item = normalize_listing_item(
            "July 20, 2026 | Reports & Briefings",
            "Paying for Outcomes: Tying University Funding to Commercial Results",
            "Canada funds university research and should reward commercialization outcomes.",
            "https://itif.org/publications/2026/07/20/paying-for-outcomes-tying-university-funding-to-commercial-results/",
        )
        self.assertEqual(item.date, "2026-07-20")
        self.assertEqual(item.publication_type, "Reports & Briefings")
        self.assertEqual(item.slug, "paying-for-outcomes-tying-university-funding-to-commercial-results")

    def test_extracts_only_report_cards_from_listing_html(self):
        html = """
        <div class="block relative mb-8">
          <p class="block mb-2">July 20, 2026<span>|</span>Reports &amp; Briefings</p>
          <a href="/publications/2026/07/20/research-commercialization/"><h2>Research Commercialization</h2></a>
          <div><p>Turning university research into firms and technologies.</p></div>
        </div>
        <div class="block relative mb-8">
          <p class="block mb-2">July 19, 2026<span>|</span>Blogs</p>
          <a href="/publications/2026/07/19/a-blog/"><h2>A Blog</h2></a>
          <div><p>Commentary only.</p></div>
        </div>
        """
        rows = extract_listing_cards(html)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].title, "Research Commercialization")
        self.assertEqual(rows[0].summary, "Turning university research into firms and technologies.")

    def test_type_specific_archive_cards_may_contain_date_only(self):
        html = """
        <div class="block relative mb-8">
          <p class="block mb-2">July 20, 2026</p>
          <a href="/publications/2026/07/20/research-commercialization/"><h2>Research Commercialization</h2></a>
          <div><p>Turning university research into firms and technologies.</p></div>
        </div>
        """
        rows = extract_listing_cards(html)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].publication_type, "Reports & Briefings")

    def test_research_window_starts_in_2016_and_ends_on_collection_date(self):
        self.assertTrue(in_research_window("2016-01-01", "2026-08-23"))
        self.assertTrue(in_research_window("2026-08-23", "2026-08-23"))
        self.assertFalse(in_research_window("2015-12-31", "2026-08-23"))
        self.assertFalse(in_research_window("2026-08-24", "2026-08-23"))

    def test_science_rd_and_technology_translation_are_core(self):
        self.assertEqual(classify_relevance("Transforming STEM Research Policy", "federal R&D funding"), "核心")
        self.assertEqual(classify_relevance("Commercializing Canadian Health Research", "technology transfer"), "核心")
        self.assertEqual(classify_relevance("Innovation Wars", "corporate R&D in advanced industries"), "核心")

    def test_talent_diffusion_and_productivity_are_supporting(self):
        self.assertEqual(classify_relevance("High-Tech Nation", "regional technology activity and skills"), "支撑")
        self.assertEqual(classify_relevance("Technology Diffusion", "firm productivity"), "支撑")

    def test_security_antitrust_and_privacy_alone_stay_context(self):
        self.assertEqual(classify_relevance("A National Security Strategy for Cyberspace", "defense and cyber threats"), "语境")
        self.assertEqual(classify_relevance("Rethinking Antitrust", "competition enforcement"), "语境")
        self.assertEqual(classify_relevance("A New Privacy Framework", "consumer data rules"), "语境")

    def test_direct_china_signal_requires_explicit_reference(self):
        self.assertTrue(direct_china_signal("China Is Catching Up in Corporate R&D", ""))
        self.assertTrue(direct_china_signal("National Innovation Systems", "comparison with Chinese firms"))
        self.assertFalse(direct_china_signal("Tracking Global R&D", "Asian economies are expanding"))

    def test_report_id_is_stable(self):
        self.assertEqual(
            report_id("2023-07-24", "innovation-wars-how-china-is-gaining-on-the-united-states-in-corporate-rd"),
            "C-ITIF-RB-2023-INNOVATION-WARS-HOW-CHINA-IS-GAINING-ON-THE-UNITED-STATES-IN-CORPORATE-RD",
        )

    def test_wait_until_retries_until_dynamic_page_is_ready(self):
        states = iter([False, False, True])
        self.assertTrue(wait_until(lambda: next(states), attempts=3, interval=0))

    def test_wait_until_fails_after_bounded_attempts(self):
        with self.assertRaises(TimeoutError):
            wait_until(lambda: False, attempts=2, interval=0)

    def test_browser_scripts_are_valid_javascript(self):
        for script in (listing_state_script(), next_page_script()):
            check = subprocess.run(
                ["node", "-e", f"new Function('return ' + {json.dumps(script)})"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_page_signature_changes_with_report_cards_not_pager_number(self):
        first = '<div class="block relative mb-8"><p class="block mb-2">July 20, 2026</p><a href="/publications/2026/07/20/a/"><h2>A</h2></a></div>'
        second = '<div class="block relative mb-8"><p class="block mb-2">July 19, 2026</p><a href="/publications/2026/07/19/b/"><h2>B</h2></a></div>'
        self.assertNotEqual(page_signature(first), page_signature(second))

    def test_rerun_replaces_only_rows_created_by_this_light_catalog(self):
        previous_ids = {"C-ITIF-RB-2026-X", "S-ITIF-2026-01"}
        generated = {"报告ID": "C-ITIF-RB-2026-X", "机构ID": "itif", "样本角色": "ITIF近十年正式研究轻量总目录", "本地原始资产路径": ""}
        anchor = {"报告ID": "S-ITIF-2026-01", "机构ID": "itif", "样本角色": "官方锚点", "本地原始资产路径": ""}
        self.assertTrue(should_replace_previous_light_row(generated, previous_ids))
        self.assertFalse(should_replace_previous_light_row(anchor, previous_ids))

    def test_missing_itif_seed_replaces_same_url_generated_row(self):
        catalog = [{"报告ID": "C-ITIF-RB-2026-X", "机构ID": "itif", "原文链接": "https://itif.org/x/", "样本角色": "ITIF近十年正式研究轻量总目录"}]
        seeds = [{"种子ID": "S-ITIF-2026-01", "机构ID": "itif", "官方页面或PDF": "https://itif.org/x/"}]
        restored = restore_missing_itif_seeds(catalog, seeds, lambda seed: {"报告ID": seed["种子ID"], "机构ID": seed["机构ID"], "原文链接": seed["官方页面或PDF"], "样本角色": "官方锚点"})
        self.assertEqual([row["报告ID"] for row in restored], ["S-ITIF-2026-01"])


if __name__ == "__main__":
    unittest.main()
