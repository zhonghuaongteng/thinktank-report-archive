from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.build_viewpoint_node_theme_gap_matrix import (
    STRATEGIC_THEMES,
    china_relevance,
    candidate_priority_score,
    classify_themes,
    evidence_status,
    is_security_dominant,
    node_for_date,
    priority_score,
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

    def test_security_policy_basic_study_is_not_a_science_priority(self) -> None:
        row = {
            "报告名称": "국가R&D 보안정책 설계를 위한 기초연구",
            "示踪问题": "",
            "预期用途": "",
            "样本角色": "",
        }
        title_themes = classify_themes(row, set())
        self.assertTrue(is_security_dominant(title_themes))

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

    def test_seven_strategic_themes_are_stable(self) -> None:
        self.assertEqual(len(STRATEGIC_THEMES), 7)


if __name__ == "__main__":
    unittest.main()
