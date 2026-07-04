import tempfile
import unittest
from pathlib import Path

from thinktank_watch.audit import audit_rows, write_audit_report
from thinktank_watch.models import ArticleCandidate


class AuditTests(unittest.TestCase):
    def test_audit_rows_group_by_institution_and_field_completeness(self):
        candidates = [
            ArticleCandidate(
                institution_slug="rand",
                institution_name="RAND",
                institution_type="think_tank",
                title="AI safety",
                url="https://example.org/a",
                published_date="2026-07-01",
                summary="summary",
                authors=["Ada"],
                pdf_url="https://example.org/a.pdf",
                pdf_status="200 application/pdf",
                priority="P1",
                fetch_status="detail_ok",
            ),
            ArticleCandidate(
                institution_slug="rand",
                institution_name="RAND",
                institution_type="think_tank",
                title="Untimed",
                url="https://example.org/b",
                priority="P3",
                fetch_status="detail_error:ReadTimeout",
            ),
            ArticleCandidate(
                institution_slug="itif",
                institution_name="ITIF",
                institution_type="think_tank",
                title="Cloud policy",
                url="https://example.org/c",
                published_date="2026-07-02",
                priority="P2",
            ),
        ]

        rows = audit_rows(candidates)

        self.assertEqual(rows[0]["机构slug"], "itif")
        self.assertEqual(rows[0]["候选数"], "1")
        self.assertEqual(rows[1]["机构slug"], "rand")
        self.assertEqual(rows[1]["候选数"], "2")
        self.assertEqual(rows[1]["P0/P1数"], "1")
        self.assertEqual(rows[1]["缺日期数"], "1")
        self.assertEqual(rows[1]["PDF线索数"], "1")
        self.assertEqual(rows[1]["详情成功数"], "1")
        self.assertEqual(rows[1]["详情失败数"], "1")

    def test_write_audit_report_creates_csv(self):
        candidates = [
            ArticleCandidate(
                institution_slug="rand",
                institution_name="RAND",
                institution_type="think_tank",
                title="AI safety",
                url="https://example.org/a",
                published_date="2026-07-01",
                priority="P1",
            )
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = write_audit_report(Path(tmp) / "audit.csv", candidates)

            text = Path(path).read_text(encoding="utf-8-sig")
            self.assertIn("机构slug", text)
            self.assertIn("rand", text)


if __name__ == "__main__":
    unittest.main()
