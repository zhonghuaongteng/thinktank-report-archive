from __future__ import annotations

from .models import ArticleCandidate


INNOVATION_SUPPORT_TAGS = {"科技创新", "半导体", "先进制造", "数字经济", "科技人才"}
GOVERNANCE_ONLY_TAGS = {"AI治理", "科技治理", "国防AI"}


def is_innovation_support_candidate(candidate: ArticleCandidate) -> bool:
    return bool(INNOVATION_SUPPORT_TAGS & set(candidate.topic_tags))


def is_governance_only_candidate(candidate: ArticleCandidate) -> bool:
    tags = set(candidate.topic_tags)
    return bool(tags) and not is_innovation_support_candidate(candidate) and tags <= GOVERNANCE_ONLY_TAGS


def innovation_support_sort_rank(candidate: ArticleCandidate) -> int:
    if is_innovation_support_candidate(candidate):
        return 0
    if is_governance_only_candidate(candidate):
        return 2
    return 1
