import sqlite3
import tempfile
import unittest
from pathlib import Path

from thinktank_watch.cli import main
from thinktank_watch.restore import parse_archive_markdown, rebuild_state_from_archive


class RestoreStateTests(unittest.TestCase):
    def test_parse_archive_markdown_recovers_candidate_metadata(self):
        markdown = """---
institution: RAND Corporation
institution_slug: rand
institution_type: think_tank
content_type: rand_report
source_completeness: full_text
english_title: "AI and Public Governance"
chinese_title: "人工智能与公共治理"
published_date: 2026-07-01
source_url: https://www.rand.org/pubs/research_reports/RRA123-1.html
pdf_url: https://www.rand.org/example.pdf
pdf_status: 200 application/pdf
external_source_url: 
authors: ["Ada Chen", "Ben Lee"]
keywords: ["AI治理", "公共部门"]
subjects: []
topic_tags: ["AI治理", "科技治理"]
priority: P1
score: 9
translation_level: full_or_long
copyright_boundary: private_archive
fetch_status: detail_ok
---

# 人工智能与公共治理
"""

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "人工智能与公共治理_2026-07-01_RRA123-1.md"
            path.write_text(markdown, encoding="utf-8")

            candidate = parse_archive_markdown(path)

        self.assertEqual(candidate.institution_slug, "rand")
        self.assertEqual(candidate.title, "AI and Public Governance")
        self.assertEqual(candidate.chinese_title, "人工智能与公共治理")
        self.assertEqual(candidate.authors, ["Ada Chen", "Ben Lee"])
        self.assertEqual(candidate.topic_tags, ["AI治理", "科技治理"])
        self.assertEqual(candidate.priority, "P1")
        self.assertEqual(candidate.score, 9)

    def test_rebuild_state_from_archive_upserts_markdown_files(self):
        first = """---
institution: interface
institution_slug: interface
institution_type: think_tank
content_type: article
source_completeness: full_text
english_title: "Talent in, Talent out"
chinese_title: "欧洲AI人才流入与流出"
published_date: 2026-04-29
source_url: https://www.interface-eu.org/publications/talent-in-talent-out
pdf_url: 
pdf_status: none
external_source_url: 
authors: []
keywords: []
subjects: []
topic_tags: ["AI治理"]
priority: P1
score: 7
translation_level: full_or_long
copyright_boundary: private_archive
fetch_status: detail_ok
---
"""
        second = first.replace("Talent in, Talent out", "AI Governance").replace(
            "talent-in-talent-out", "ai-governance"
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive" / "interface" / "2026"
            archive_dir.mkdir(parents=True)
            (archive_dir / "欧洲AI人才流入与流出_2026-04-29_INTERFACE.md").write_text(first, encoding="utf-8")
            (archive_dir / "AI治理_2026-04-29_INTERFACE.md").write_text(second, encoding="utf-8")
            state_path = root / "state" / "articles.sqlite"

            count = rebuild_state_from_archive(archive_dir.parent.parent, state_path)

            conn = sqlite3.connect(state_path)
            try:
                rows = conn.execute(
                    "SELECT title, url, archive_path FROM articles ORDER BY title"
                ).fetchall()
            finally:
                conn.close()

        self.assertEqual(count, 2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], "AI Governance")
        self.assertTrue(rows[0][2].endswith("AI治理_2026-04-29_INTERFACE.md"))

    def test_cli_rebuild_state_command_uses_archive_root(self):
        markdown = """---
institution: GovAI
institution_slug: govai
institution_type: think_tank
content_type: report
source_completeness: full_text
english_title: "AI Risk"
chinese_title: "AI风险"
published_date: 2026-06-01
source_url: https://www.governance.ai/research-paper/ai-risk
pdf_url: 
pdf_status: none
external_source_url: 
authors: []
keywords: []
subjects: []
topic_tags: ["AI治理"]
priority: P1
score: 8
translation_level: full_or_long
copyright_boundary: private_archive
fetch_status: detail_ok
---
"""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive" / "govai" / "2026"
            archive_dir.mkdir(parents=True)
            (archive_dir / "AI风险_2026-06-01_GOVAI.md").write_text(markdown, encoding="utf-8")
            state_path = root / "state" / "articles.sqlite"

            exit_code = main(
                [
                    "rebuild-state",
                    "--archive-root",
                    str(root / "archive"),
                    "--state",
                    str(state_path),
                ]
            )

            conn = sqlite3.connect(state_path)
            try:
                row_count = conn.execute("SELECT count(*) FROM articles").fetchone()[0]
            finally:
                conn.close()

        self.assertEqual(exit_code, 0)
        self.assertEqual(row_count, 1)


if __name__ == "__main__":
    unittest.main()
