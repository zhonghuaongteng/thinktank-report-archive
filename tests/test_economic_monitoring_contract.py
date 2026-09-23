import csv
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from thinktank_watch.archive import build_markdown
from thinktank_watch.audit import audit_rows, write_editorial_review_queue
from thinktank_watch.config import load_institutions, load_topics, load_priority_rules
from thinktank_watch.models import ArticleCandidate
from thinktank_watch.parsers.generic import extract_list_links, looks_like_detail_url, parse_generic_detail
from thinktank_watch.scoring import score_candidate
from thinktank_watch.summary import _fallback_china_shanghai_reference


class EconomicMonitoringContractTests(unittest.TestCase):
    def candidate(self, **kwargs):
        values = dict(institution_slug="zew", institution_name="ZEW", institution_type="research_institute",
                      title="Firm closures and business dynamics", url="https://www.zew.de/en/publications/example",
                      published_date="2026-09-20", content_type="report", fetch_status="detail_ok",
                      source_group="innovation_economy")
        values.update(kwargs)
        return ArticleCandidate(**values)

    def test_formal_enterprise_research_does_not_need_a_technology_word(self):
        topics, rules = load_topics("config/topics.yaml"), load_priority_rules("config/priorities.yaml")
        for title in ["Firm closures and business dynamics", "Weak demand and business investment",
                      "Management practices and workforce transformation", "Skills shortages and energy costs",
                      "Capital allocation and global value chains"]:
            scored = score_candidate(self.candidate(title=title), topics, rules)
            self.assertIn(scored.priority, {"P0", "P1"}, title)
            self.assertIn("经济与企业创新", scored.topic_tags)
        noise = score_candidate(self.candidate(title="Today's stock price forecast", content_type="article"), topics, rules)
        self.assertEqual(noise.priority, "P3")

    def test_zero_candidate_source_is_visible_and_no_details_is_not_admissible(self):
        sources = {s.slug: s for s in load_institutions("config/institutions")}
        rows = audit_rows([self.candidate(priority="P1", fetch_status="list_ok")], "2026-09-20",
                          institutions=[sources["zew"], sources["kfw-research"]])
        by_slug = {row["机构slug"]: row for row in rows}
        self.assertEqual(by_slug["kfw-research"]["候选数"], "0")
        self.assertIn("不等于无发布", by_slug["kfw-research"]["候选状态"])
        self.assertEqual(by_slug["zew"]["近7日可入选数"], "0")

    def test_keyword_misses_survive_in_read_only_review_queue(self):
        item = self.candidate(title="SMEs' international business stagnates – enterprises adapt to a changing environment",
                              summary="Export markets, foreign revenues and domestic customers.", priority="P3")
        with TemporaryDirectory() as tmp:
            path = write_editorial_review_queue(Path(tmp)/"review.csv",
                [item, replace(item, published_date="2026-09-13"), replace(item, published_date="2026-09-21")], "2026-09-20")
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["原始优先级"], "P3")
            self.assertEqual(rows[0]["复核状态"], "待原文复核")
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_limited_source_cannot_leak_detail_text_via_summary_fallback(self):
        item = self.candidate(institution_slug="nber", copyright_boundary="metadata_summary_only",
            source_completeness="full_text", summary="Public abstract.", detail_text="PRIVATE_BODY_SENTINEL " * 200)
        result = build_markdown(item)
        self.assertNotIn("PRIVATE_BODY_SENTINEL", result)
        self.assertIn("source_completeness: summary_only", result)
        self.assertIn("Public abstract.", result)
        self.assertEqual(item.source_completeness, "full_text")
        self.assertTrue(item.detail_text)

    def test_verified_publication_paths_do_not_relax_arbitrary_indexes(self):
        for url in ["https://www.bis.org/publications/working-paper-1218-bank-specialisation-and-corporate-innovation",
                    "https://cepr.org/publications/dp21016", "https://www.zew.de/publikationen/juli-2026-2"]:
            self.assertTrue(looks_like_detail_url(url), url)
        self.assertFalse(looks_like_detail_url("https://example.org/publications/research-overview"))
        self.assertFalse(looks_like_detail_url("https://www.bis.org/publications/working-paper"))

    def test_navigation_does_not_consume_candidate_budget(self):
        html = '<nav><a href="/research/old-navigation">Research</a></nav><main><a href="/reports/new-study">New study</a></main>'
        self.assertEqual(extract_list_links(html, "https://example.org", 1), ["https://example.org/reports/new-study"])

    def test_modified_only_metadata_does_not_create_a_publication_date(self):
        source = next(s for s in load_institutions("config/institutions") if s.slug == "zew")
        html = '<html><title>Enterprise Research</title><script type="application/ld+json">{"@type":"Report","dateModified":"2026-09-20"}</script><main>Enterprise Research</main></html>'
        self.assertEqual(parse_generic_detail(html, "https://www.zew.de/en/publications/example", source).published_date, "")

    def test_bibliography_is_not_a_china_policy_finding(self):
        text = "The study considers worker adjustment costs.\nReferences\nAutor: The China Syndrome: Local Labor Market Effects of Import Competition."
        item = self.candidate(summary=text)
        self.assertEqual(_fallback_china_shanghai_reference(item, text), "")


if __name__ == "__main__":
    unittest.main()
