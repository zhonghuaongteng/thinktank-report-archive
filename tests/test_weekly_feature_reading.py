import unittest

from scripts.check_weekly_feature_reading import fingerprint, validate


class FeatureReadingTests(unittest.TestCase):
    def setUp(self):
        self.url = "https://example.org/issue"
        self.item = dict(priority="P1", url=self.url, chinese_title="学校怎样牵头",
                         chinese_summary="先认定大学，再审项目。", highlights_markdown="甲方负责合同。\n\n### 乙方的责任\n\n乙方提供人员。")
        self.review = dict(url=self.url, reviewed_sha256=fingerprint(self.item),
                           retelling="甲方签约之后，乙方按约派人。",
                           source_notes=[dict(url=self.url, locator="议程三", finding="合同和投入分别核查。")])
        self.body = "<p>甲方负责合同。</p><h3>乙方的责任</h3><p>乙方提供人员。</p>"
        self.pc = (f'<section class="topic-primary"><h3><a href="{self.url}">学校怎样牵头</a></h3>'
                   '<div class="judgment-box"><p>先认定大学，再审项目。</p></div></section>'
                   f'<section><div class="report-highlights">{self.body}</div></section>')
        self.mobile = (f'<article class="feature"><h2><a href="{self.url}">学校怎样牵头</a></h2>'
                       f'<p class="summary">先认定大学，再审项目。</p>{self.body}</article>')

    def result(self):
        return validate([self.item], [self.review], self.pc, self.mobile)

    def test_two_complete_readers(self):
        self.assertTrue(self.result()["passed"])

    def test_reordered_paragraphs_and_missing_tail(self):
        self.mobile = self.mobile.replace(self.body, "<p>乙方提供人员。</p><p>甲方负责合同。</p><h3>乙方的责任</h3>")
        self.assertFalse(self.result()["passed"])
        self.pc = self.pc.replace("<p>乙方提供人员。</p>", "")
        self.assertTrue(any("PC缺段" in error for error in self.result()["errors"]))

    def test_edited_body_requires_fresh_review(self):
        self.item["chinese_summary"] = "改过的导读。"
        self.assertTrue(any("未经本次复核" in e for e in self.result()["errors"]))

    def test_wrong_feature_or_empty_review_not_accepted(self):
        self.mobile = self.mobile.replace(self.url, "https://example.org/other")
        self.review["retelling"] = "通过"
        self.review["source_notes"] = []
        errors = self.result()["errors"]
        for clue in ("集合不一致", "具体复述", "原始资料摘记"):
            self.assertTrue(any(clue in error for error in errors))

    def test_wrong_headline_in_rendered_card(self):
        self.pc = self.pc.replace("学校怎样牵头", "旧标题")
        self.assertFalse(self.result()["passed"])
