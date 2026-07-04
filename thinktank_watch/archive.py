from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import ArticleCandidate


WINDOWS_FORBIDDEN = r'<>:"/\\|?*'


def _safe_text(value: str, fallback: str = "untitled") -> str:
    value = value.strip() or fallback
    for char in WINDOWS_FORBIDDEN:
        value = value.replace(char, " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value[:120].rstrip(". ")


def safe_article_filename(candidate: ArticleCandidate) -> str:
    title = candidate.chinese_title or candidate.title
    date = candidate.published_date or "undated"
    suffix = candidate.institution_slug.upper()
    if candidate.institution_slug == "rand":
        match = re.search(r"/([A-Z]{1,5}\d+[A-Za-z0-9-]*)\.html", candidate.url)
        if match:
            suffix = match.group(1)
    if not suffix:
        suffix = hashlib.sha256(candidate.url.encode("utf-8")).hexdigest()[:8]
    return f"{_safe_text(title)}_{date}_{_safe_text(suffix)}.md"


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join('"' + value.replace('"', '\\"') + '"' for value in values) + "]"


def build_markdown(candidate: ArticleCandidate) -> str:
    title = candidate.chinese_title or candidate.title
    english_title = candidate.title.replace('"', '\\"')
    chinese_title = title.replace('"', '\\"')
    frontmatter = [
        "---",
        f"institution: {candidate.institution_name}",
        f"institution_slug: {candidate.institution_slug}",
        f"institution_type: {candidate.institution_type}",
        f"content_type: {candidate.content_type}",
        f"source_completeness: {candidate.source_completeness}",
        f"english_title: \"{english_title}\"",
        f"chinese_title: \"{chinese_title}\"",
        f"published_date: {candidate.published_date}",
        f"source_url: {candidate.url}",
        f"pdf_url: {candidate.pdf_url}",
        f"pdf_status: {candidate.pdf_status}",
        f"external_source_url: {candidate.external_source_url}",
        f"authors: {yaml_list(candidate.authors)}",
        f"keywords: {yaml_list(candidate.keywords)}",
        f"subjects: {yaml_list(candidate.subjects)}",
        f"topic_tags: {yaml_list(candidate.topic_tags)}",
        f"priority: {candidate.priority}",
        f"score: {candidate.score}",
        f"translation_level: {candidate.translation_level}",
        f"copyright_boundary: {candidate.copyright_boundary}",
        "---",
        "",
    ]
    chinese_summary = candidate.chinese_summary or "待由 Codex 自动化补充中文摘要与研判。"
    english_material = candidate.detail_text or candidate.summary or "No source text extracted."
    parts = [
        *frontmatter,
        f"# {title}",
        "",
        "## 中文摘要与研判",
        "",
        chinese_summary,
        "",
        "## 元数据",
        "",
        f"- 原始标题：{candidate.title}",
        f"- 发布日期：{candidate.published_date or '待核验'}",
        f"- 来源链接：{candidate.url}",
        f"- PDF链接：{candidate.pdf_url or '无'}",
        f"- 关键词：{', '.join(candidate.keywords or candidate.subjects) or '待抽取'}",
        f"- 主题标签：{', '.join(candidate.topic_tags) or '待分类'}",
        f"- 优先级：{candidate.priority}",
        "",
        "## English Source Material",
        "",
        english_material,
        "",
    ]
    return "\n".join(parts)


def write_article(root: str | Path, candidate: ArticleCandidate) -> Path:
    year = candidate.published_date[:4] if re.match(r"^\d{4}", candidate.published_date or "") else "undated"
    path = Path(root) / candidate.institution_slug / year / safe_article_filename(candidate)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_markdown(candidate), encoding="utf-8")
    return path
