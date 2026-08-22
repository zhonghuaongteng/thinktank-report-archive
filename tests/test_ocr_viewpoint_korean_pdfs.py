from __future__ import annotations

import unittest

from scripts.ocr_viewpoint_korean_pdfs import (
    apply_catalog_ocr_metadata,
    apply_ocr_metadata,
    classify_ocr_quality,
    ocr_engine_kwargs,
    result_lines,
)


class FakeResult:
    json = {"res": {"rec_texts": ["과학기술 정책", "noise"], "rec_scores": [0.91, 0.2]}}


class KoreanOcrTests(unittest.TestCase):
    def test_applies_ocr_paths_to_light_catalog_row(self) -> None:
        row = {"本地路径": "", "正文完整度": "", "原始资产状态": ""}
        apply_catalog_ocr_metadata(row, "text.txt")
        self.assertEqual(row["本地路径"], "text.txt")
        self.assertEqual(row["正文完整度"], "本地韩文OCR全文已保存")
        self.assertEqual(row["原始资产状态"], "官方PDF已保存并完成韩文OCR")

    def test_applies_recoverable_ocr_metadata_to_ledger_row(self) -> None:
        row = {"本地文本": "", "本地切片": "", "提取文本字符数": "0", "文本质量": "", "本地状态": ""}
        apply_ocr_metadata(row, "text.txt", "slice.md", "과학기술정책")
        self.assertEqual(row["本地文本"], "text.txt")
        self.assertEqual(row["本地切片"], "slice.md")
        self.assertEqual(row["提取文本字符数"], str(len("과학기술정책")))
        self.assertEqual(row["文本质量"], "韩文OCR可检索文本")
        self.assertEqual(row["本地状态"], "官方PDF已保存并完成韩文OCR")

    def test_disables_mkldnn_for_paddle_331_windows_inference(self) -> None:
        self.assertIs(ocr_engine_kwargs()["enable_mkldnn"], False)

    def test_filters_low_confidence_lines(self) -> None:
        self.assertEqual(result_lines(FakeResult()), ["과학기술 정책"])

    def test_quality_requires_density_and_hangul(self) -> None:
        self.assertEqual(classify_ocr_quality("과학기술정책" * 50, 1), "韩文OCR可检索文本")
        self.assertEqual(classify_ocr_quality("english text " * 100, 1), "图像型PDF，OCR待补")
        self.assertEqual(classify_ocr_quality("과학기술정책" * 5, 10), "图像型PDF，OCR待补")


if __name__ == "__main__":
    unittest.main()
