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
CONTEXT_ONLY_TOPICS = {"中国与上海相关"}
CONTEXT_ONLY_PRIORITY_CAP = "P2"


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
        matches = sum(1 for keyword in topic.keywords if _contains_keyword(text, keyword))
        if matches:
            topic_scores[topic.name] = topic.weight + max(0, matches - 1)

    total = sum(topic_scores.values())
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

    scored.score = total
    scored.priority = priority
    scored.topic_scores = topic_scores
    scored.topic_tags = sorted(topic_scores, key=lambda name: (-topic_scores[name], name))
    scored.translation_level = rules.translation_by_priority.get(priority, "index_only")
    return scored
