from __future__ import annotations

import sqlite3
from pathlib import Path

from .fetch import dedupe_key
from .models import ArticleCandidate


SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    dedupe_key TEXT PRIMARY KEY,
    institution_slug TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    published_date TEXT,
    priority TEXT,
    score INTEGER,
    fetch_status TEXT,
    archive_path TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


class ArticleState:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def seen(self, url: str) -> bool:
        key = dedupe_key(url)
        row = self.conn.execute("SELECT 1 FROM articles WHERE dedupe_key = ?", (key,)).fetchone()
        return row is not None

    def upsert(self, candidate: ArticleCandidate, archive_path: str = "") -> None:
        self.conn.execute(
            """
            INSERT INTO articles
                (dedupe_key, institution_slug, title, url, published_date, priority, score, fetch_status, archive_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(dedupe_key) DO UPDATE SET
                title=excluded.title,
                published_date=excluded.published_date,
                priority=excluded.priority,
                score=excluded.score,
                fetch_status=excluded.fetch_status,
                archive_path=excluded.archive_path,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                dedupe_key(candidate.url),
                candidate.institution_slug,
                candidate.title,
                candidate.url,
                candidate.published_date,
                candidate.priority,
                candidate.score,
                candidate.fetch_status,
                archive_path,
            ),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
