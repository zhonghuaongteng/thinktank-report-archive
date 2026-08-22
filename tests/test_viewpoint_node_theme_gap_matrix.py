from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.build_viewpoint_node_theme_gap_matrix import (
    COVERAGE_THEMES,
    STRATEGIC_THEMES,
    china_relevance,
    catalog_node_exempt,
    candidate_priority_score,
    catalog_minimum_for,
    classify_themes,
    evidence_status,
    fulltext_axis_eligible,
    fulltext_queue_suppressed,
    is_security_dominant,
    node_for_date,
    priority_score,
    tier_for,
)


class ViewpointNodeThemeGapMatrixTests(unittest.TestCase):
    def test_node_boundaries(self) -> None:
        self.assertEqual(node_for_date("2016-01-01"), "N1")
        self.assertEqual(node_for_date("2018-12-31"), "N1")
        self.assertEqual(node_for_date("2019-01-01"), "N2")
        self.assertEqual(node_for_date("2021-06-01"), "N3")
        self.assertEqual(node_for_date("2023-06-01"), "N4")
        self.assertEqual(node_for_date("2026-08-22"), "N5")

    def test_multilingual_theme_classification(self) -> None:
        row = {
            "报告名称": "미중 기술패권과 반도체 공급망 연구",
            "示踪问题": "",
            "预期用途": "",
            "样本角色": "",
        }
        themes = classify_themes(row, {"中国科技与国际比较"})
        self.assertTrue(china_relevance(row, {"中国科技与国际比较"}))
        self.assertIn("T2_技术创新与关键技术", themes)
        self.assertIn("T7_安全供应链与治理边界", themes)

    def test_index_tag_can_supply_theme(self) -> None:
        row = {"报告名称": "A neutral title", "示踪问题": "", "预期用途": "", "样本角色": ""}
        themes = classify_themes(row, {"科技人才、博士与职业流动"})
        self.assertIn("T4_人才大学与科研组织", themes)

    def test_collection_role_does_not_create_false_china_theme(self) -> None:
        row = {
            "报告名称": "디지털 혁신전략 추진 방향 연구",
            "示踪问题": "人工智能、数据与数字技术；产业创新、创业与区域体系",
            "预期用途": "韩国国家研发战略、核心技术、中国比较专题复用",
            "样本角色": "KISTEP韩文正式研究库/核心科技直接材料",
        }
        themes = classify_themes(row, {"人工智能、数据与数字技术"})
        self.assertFalse(china_relevance(row, {"人工智能、数据与数字技术"}))
        self.assertIn("T2_技术创新与关键技术", themes)

    def test_prc_is_a_direct_china_signal(self) -> None:
        row = {"报告名称": "The PRC research ecosystem", "示踪问题": "", "预期用途": "", "样本角色": ""}
        self.assertTrue(china_relevance(row, set()))

    def test_security_policy_basic_study_is_not_a_science_priority(self) -> None:
        row = {
            "报告名称": "국가R&D 보안정책 설계를 위한 기초연구",
            "示踪问题": "",
            "预期用途": "",
            "样本角色": "",
        }
        title_themes = classify_themes(row, set())
        self.assertFalse(is_security_dominant(title_themes))
        self.assertTrue(fulltext_axis_eligible(row["报告名称"], title_themes))

    def test_military_ai_title_stays_out_of_fulltext_queue(self) -> None:
        title = "China's Military AI Roadblocks"
        themes = classify_themes({"报告名称": title, "示踪问题": ""}, set())
        self.assertIn("T2_技术创新与关键技术", themes)
        self.assertIn("T7_安全供应链与治理边界", themes)
        self.assertFalse(fulltext_axis_eligible(title, themes))

    def test_security_context_can_enter_when_innovation_mechanism_is_explicit(self) -> None:
        title = "Research security and the national innovation system"
        themes = classify_themes({"报告名称": title, "示踪问题": ""}, set())
        self.assertTrue(fulltext_axis_eligible(title, themes))

    def test_generic_global_topics_do_not_create_innovation_fulltext_candidates(self) -> None:
        for title in (
            "Estimating the global economic impacts of international tourism",
            "Measuring greenhouse gas footprints in global production networks",
            "Unlocking potential in the global scrap steel market",
        ):
            themes = classify_themes({"报告名称": title, "示踪问题": ""}, set())
            self.assertFalse(fulltext_axis_eligible(title, themes), title)

        innovation_title = "Global research collaboration and open science"
        innovation_themes = classify_themes({"报告名称": innovation_title, "示踪问题": ""}, set())
        self.assertTrue(fulltext_axis_eligible(innovation_title, innovation_themes))

    def test_sampled_annual_series_stays_out_of_fulltext_queue(self) -> None:
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "官方入口已保存；连续系列已完成跨期抽样"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "机构跨期精选已完成；低增量节点保留轻量目录"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "IFP官方网页与附件入口已保存；机构精选已完成；其余正式成果保留轻量目录"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "ITIF跨期精选已完成；其余正式报告保留轻量目录"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "FAS跨期精选已完成；其余报告与政策备忘录保留轻量目录"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "CSIS RAI跨期精选已完成；其余Report/Article保留轻量目录"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "STOA跨期精选已完成；其余成果保留轻量目录"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "JRC跨期精选已完成；其余成果保留轻量目录"}))
        self.assertTrue(fulltext_queue_suppressed({"原始资产状态": "EFI跨期精选已完成；其余成果保留轻量目录"}))
        self.assertFalse(fulltext_queue_suppressed({"原始资产状态": "官方入口已保存；未下载全文"}))

    def test_nesta_uses_observed_publication_volume_after_complete_site_scan(self) -> None:
        self.assertEqual(catalog_minimum_for("nesta", "A"), 1)

    def test_rathenau_uses_observed_publication_volume_after_complete_archive_scan(self) -> None:
        self.assertEqual(catalog_minimum_for("rathenau", "A"), 1)

    def test_ifp_uses_observed_publication_volume_after_complete_api_scan(self) -> None:
        self.assertEqual(catalog_minimum_for("ifp", "B"), 1)
        self.assertEqual(catalog_minimum_for("oecd-sti", "A"), 5)

    def test_biennial_series_does_not_create_a_false_missing_publication_node(self) -> None:
        self.assertTrue(catalog_node_exempt("unctad-tir", "N2"))
        self.assertFalse(catalog_node_exempt("unctad-tir", "N3"))

    def test_evidence_status_distinguishes_three_layers(self) -> None:
        self.assertEqual(evidence_status(3, 0, 0, "A"), "仅目录候选")
        self.assertEqual(evidence_status(3, 1, 0, "A"), "原文待文本化")
        self.assertEqual(evidence_status(3, 1, 1, "A"), "可用")
        self.assertEqual(evidence_status(3, 3, 3, "A"), "充分")
        self.assertEqual(evidence_status(0, 0, 0, "A"), "空白")

    def test_priority_focuses_on_china_core_and_transition_nodes(self) -> None:
        science_china = priority_score("A", "N3", "T1_科学体系与基础研究", 4, 0, 0, 2)
        security_only = priority_score("A", "N3", "T7_安全供应链与治理边界", 4, 0, 0, 0)
        covered = priority_score("A", "N3", "T1_科学体系与基础研究", 4, 1, 1, 2)
        self.assertGreater(science_china, security_only)
        self.assertEqual(covered, 0)

    def test_direct_china_technology_report_survives_covered_cell(self) -> None:
        score = candidate_priority_score(
            "A",
            "N2",
            {"T2_技术创新与关键技术"},
            True,
            "P0-China-tech-corpus",
            [0],
        )
        self.assertGreaterEqual(score, 20)

    def test_security_context_is_downgraded_below_fulltext_threshold(self) -> None:
        score = candidate_priority_score(
            "A",
            "N4",
            {"T1_科学体系与基础研究", "T7_安全供应链与治理边界"},
            False,
            "P2-STI-baseline",
            [17],
            security_context=True,
        )
        self.assertEqual(score, 0)

    def test_six_science_innovation_axes_and_one_context_theme_are_stable(self) -> None:
        self.assertEqual(len(STRATEGIC_THEMES), 7)
        self.assertEqual(len(COVERAGE_THEMES), 6)
        self.assertNotIn("T7_安全供应链与治理边界", COVERAGE_THEMES)

    def test_institution_tiers_follow_science_innovation_fit(self) -> None:
        self.assertEqual(tier_for("fraunhofer-isi"), "A")
        self.assertEqual(tier_for("wipo-gii"), "A")
        self.assertEqual(tier_for("nsf-nsb-sei"), "A")
        self.assertEqual(tier_for("eu-srip"), "A")
        self.assertEqual(tier_for("eu-eis"), "A")
        self.assertEqual(tier_for("unesco-science"), "A")
        self.assertEqual(tier_for("unctad-tir"), "A")
        self.assertEqual(tier_for("wipo-wipr"), "A")
        self.assertEqual(tier_for("nesta"), "A")
        self.assertEqual(tier_for("rathenau"), "A")
        self.assertEqual(tier_for("eu-stoa"), "A")
        self.assertEqual(tier_for("eu-jrc"), "A")
        self.assertEqual(tier_for("de-efi"), "A")
        self.assertEqual(tier_for("ifp"), "B")
        self.assertEqual(tier_for("ifp"), "B")
        self.assertEqual(tier_for("stanford-hai"), "B")
        self.assertEqual(tier_for("fas"), "B")
        self.assertEqual(tier_for("csis-rai"), "B")
        self.assertEqual(tier_for("rand"), "C")
        self.assertEqual(tier_for("csis"), "C")


if __name__ == "__main__":
    unittest.main()
