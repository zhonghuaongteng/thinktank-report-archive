from __future__ import annotations

import copy
import re

from .models import ArticleCandidate, PriorityRules, TopicRule


REPORT_TYPES = {
    "report",
    "rand_report",
    "research_report",
    "policy_report",
    "brief",
    "paper",
    "external_publication",
}
TOPIC_MATCH_EXTRA_CAP = 2
CONTEXT_ONLY_TOPICS = {"中国与上海相关"}
CONTEXT_ONLY_PRIORITY_CAP = "P2"
PDF_OR_REPORT_PRIORITY_CAP_SOURCES = {"orf-america"}
PDF_OR_REPORT_PRIORITY_CAP = "P2"
STANDALONE_AI_KEYWORDS = {"AI", "A.I."}
WEAK_DEFENSE_AI_KEYWORDS = {"defense technology", "national security", "国家安全"}
STRONG_DEFENSE_AI_KEYWORDS = {
    "defense AI",
    "military AI",
    "autonomous weapons",
    "cyber operations",
    "国防人工智能",
    "军事人工智能",
    "自主武器",
}
WEAK_TECH_GOVERNANCE_KEYWORDS = {"standards", "regulation", "tariff", "tariffs", "data policy"}
STRONG_TECH_GOVERNANCE_KEYWORDS = {
    "technology governance",
    "tech governance",
    "digital governance",
    "technology policy",
    "export controls",
    "Section 232",
    "competition regulation",
    "market gatekeeping",
    "cross-border data",
    "cross-border data flow",
    "cross-border data flows",
    "data flow policy",
    "data security program",
    "supply chain security",
    "data governance",
    "techno-economic war",
    "科技治理",
    "数字治理",
    "标准治理",
    "出口管制",
}


def _contains_keyword(text: str, keyword: str) -> bool:
    if not keyword:
        return False
    needle = keyword.lower()
    haystack = text.lower()
    if re.search(r"[\u4e00-\u9fff]", keyword):
        return needle in haystack
    match = re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack)
    if not match:
        return False
    context = haystack[max(0, match.start() - 32) : match.start()]
    if re.search(r"\b(no|without|lacks|lack of|not)\b", context):
        return False
    return True


def _has_substantive_standalone_ai_context(text: str) -> bool:
    haystack = text.lower()
    return (
        re.search(
            r"(?<![a-z0-9])a\.?i\.?\s+"
            r"(?:in|for|and|policy|governance|systems?|models?|applications?|adoption|regulation|safety|risk|career)",
            haystack,
        )
        is not None
    )


def score_candidate(
    candidate: ArticleCandidate,
    topics: list[TopicRule],
    rules: PriorityRules,
) -> ArticleCandidate:
    scored = copy.deepcopy(candidate)
    text = " ".join(
        [
            scored.title,
            scored.chinese_title,
            scored.summary,
            scored.chinese_summary,
            " ".join(scored.keywords),
            " ".join(scored.subjects),
        ]
    )
    topic_scores: dict[str, int] = {}
    for topic in topics:
        matched_keywords = [keyword for keyword in topic.keywords if _contains_keyword(text, keyword)]
        if topic.name == "AI治理" and set(matched_keywords) <= STANDALONE_AI_KEYWORDS:
            title_mentions_ai = any(_contains_keyword(scored.title, keyword) for keyword in STANDALONE_AI_KEYWORDS)
            if not title_mentions_ai and not _has_substantive_standalone_ai_context(text):
                matched_keywords = []
        if topic.name == "国防AI" and set(matched_keywords) <= WEAK_DEFENSE_AI_KEYWORDS:
            has_strong_defense_ai_signal = any(_contains_keyword(text, keyword) for keyword in STRONG_DEFENSE_AI_KEYWORDS)
            if not has_strong_defense_ai_signal:
                matched_keywords = []
        if topic.name == "科技治理" and set(matched_keywords) <= WEAK_TECH_GOVERNANCE_KEYWORDS:
            has_strong_tech_governance_signal = any(
                _contains_keyword(text, keyword) for keyword in STRONG_TECH_GOVERNANCE_KEYWORDS
            )
            if not has_strong_tech_governance_signal:
                matched_keywords = []
        matches = len(matched_keywords)
        if matches:
            topic_scores[topic.name] = topic.weight + min(max(0, matches - 1), TOPIC_MATCH_EXTRA_CAP)

    total = sum(topic_scores.values())
    if topic_scores:
        if scored.content_type in REPORT_TYPES:
            total += rules.report_bonus
        total += int(rules.source_priority_bonus.get(scored.institution_slug, 0))

    if total >= rules.p0_threshold:
        priority = "P0"
    elif total >= rules.p1_threshold:
        priority = "P1"
    elif total >= rules.p2_threshold:
        priority = "P2"
    else:
        priority = "P3"

    substantive_topics = set(topic_scores) - CONTEXT_ONLY_TOPICS
    if topic_scores and not substantive_topics and priority in {"P0", "P1"}:
        priority = CONTEXT_ONLY_PRIORITY_CAP
    if (
        scored.institution_slug in PDF_OR_REPORT_PRIORITY_CAP_SOURCES
        and not scored.pdf_url
        and scored.content_type not in REPORT_TYPES
        and priority in {"P0", "P1"}
    ):
        priority = PDF_OR_REPORT_PRIORITY_CAP

    scored.score = total
    scored.priority = priority
    scored.topic_scores = topic_scores
    scored.topic_tags = sorted(topic_scores, key=lambda name: (-topic_scores[name], name))
    scored.translation_level = rules.translation_by_priority.get(priority, "index_only")
    return scored
