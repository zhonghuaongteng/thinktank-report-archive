from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Institution:
    slug: str
    name: str
    chinese_name: str
    country_region: str
    institution_type: str
    priority: str
    batch: int
    homepage: str
    parser: str
    copyright_boundary: str
    allowed_domains: list[str] = field(default_factory=list)
    feeds: list[str] = field(default_factory=list)
    list_pages: list[str] = field(default_factory=list)
    topic_pages: list[str] = field(default_factory=list)
    sitemap_urls: list[str] = field(default_factory=list)
    sitemap_include_keywords: list[str] = field(default_factory=list)
    text_proxy_fallback: bool = False
    run_limit: int = 0
    notes: str = ""


@dataclass(slots=True)
class ArticleCandidate:
    institution_slug: str
    institution_name: str
    institution_type: str
    title: str
    url: str
    published_date: str = ""
    summary: str = ""
    content_type: str = "article"
    chinese_title: str = ""
    chinese_summary: str = ""
    authors: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    subjects: list[str] = field(default_factory=list)
    pdf_url: str = ""
    pdf_status: str = ""
    external_source_url: str = ""
    source_completeness: str = "summary_only"
    priority: str = "P3"
    topic_tags: list[str] = field(default_factory=list)
    topic_scores: dict[str, int] = field(default_factory=dict)
    score: int = 0
    translation_level: str = "index_only"
    copyright_boundary: str = ""
    fetch_status: str = "candidate"
    detail_text: str = ""


@dataclass(slots=True)
class TopicRule:
    name: str
    weight: int
    keywords: list[str]


@dataclass(slots=True)
class PriorityRules:
    p0_threshold: int
    p1_threshold: int
    p2_threshold: int
    report_bonus: int
    source_priority_bonus: dict[str, int]
    translation_by_priority: dict[str, str]


@dataclass(slots=True)
class SearchProfile:
    name: str
    description: str = ""
    include_terms: list[str] = field(default_factory=list)
    topic_tags_any: list[str] = field(default_factory=list)
    exclude_governance_only: bool = False
