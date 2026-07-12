from __future__ import annotations

import ast
import re
from pathlib import Path

from .models import ArticleCandidate
from .state import ArticleState


def _frontmatter(text: str) -> dict[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        raise ValueError("archive markdown is missing frontmatter")
    try:
        block = text.split("---", 2)[1]
    except IndexError as exc:
        raise ValueError("archive markdown frontmatter is incomplete") from exc
    data: dict[str, str] = {}
    for raw in block.splitlines():
        if ": " not in raw:
            continue
        key, value = raw.split(": ", 1)
        data[key.strip()] = value.strip()
    return data


def _scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"')
    return value


def _list(value: str) -> list[str]:
    value = value.strip()
    if not value or value == "[]":
        return []
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, list):
        raise ValueError(f"expected list frontmatter value, got {type(parsed).__name__}")
    return [str(item) for item in parsed]


def _int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    after_heading = text.split(marker, 1)[1]
    match = re.search(r"\n##\s+", after_heading)
    section = after_heading[: match.start()] if match else after_heading
    return section.strip()


def parse_archive_markdown(path: str | Path) -> ArticleCandidate:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    data = _frontmatter(text)
    return ArticleCandidate(
        institution_slug=data["institution_slug"],
        institution_name=data["institution"],
        institution_type=data["institution_type"],
        title=_scalar(data["english_title"]),
        url=data["source_url"],
        published_date=data.get("published_date", ""),
        summary="",
        chinese_summary=_section(text, "中文摘要与研判"),
        content_type=data.get("content_type", "article"),
        chinese_title=_scalar(data.get("chinese_title", "")),
        authors=_list(data.get("authors", "[]")),
        keywords=_list(data.get("keywords", "[]")),
        subjects=_list(data.get("subjects", "[]")),
        pdf_url=data.get("pdf_url", ""),
        pdf_status=data.get("pdf_status", ""),
        external_source_url=data.get("external_source_url", ""),
        source_completeness=data.get("source_completeness", "summary_only"),
        priority=data.get("priority", "P3"),
        topic_tags=_list(data.get("topic_tags", "[]")),
        score=_int(data.get("score", "0")),
        translation_level=data.get("translation_level", "index_only"),
        copyright_boundary=data.get("copyright_boundary", ""),
        fetch_status=data.get("fetch_status", "restored"),
    )


def rebuild_state_from_archive(archive_root: str | Path, state_path: str | Path) -> int:
    state = ArticleState(state_path)
    count = 0
    try:
        for path in sorted(Path(archive_root).rglob("*.md")):
            candidate = parse_archive_markdown(path)
            state.upsert(candidate, str(path))
            count += 1
    finally:
        state.close()
    return count
