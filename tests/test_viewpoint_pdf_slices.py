from __future__ import annotations

import unittest

from scripts.extract_viewpoint_pdf_slices import KEYWORDS


class ViewpointPdfSliceTests(unittest.TestCase):
    def test_default_slices_follow_science_and_technology_innovation_axes(self) -> None:
        self.assertEqual(
            set(KEYWORDS),
            {
                "T1_科学体系与基础研究",
                "T2_技术创新与关键技术",
                "T3_创新政策与研发治理",
                "T4_人才大学与科研组织",
                "T5_产业创新与成果转化",
                "T6_国际合作开放科学与比较",
                "T7_中国科技横向维度",
            },
        )
        self.assertFalse(any("安全" in name or "供应链" in name for name in KEYWORDS))


if __name__ == "__main__":
    unittest.main()
