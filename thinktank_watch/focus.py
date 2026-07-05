from __future__ import annotations

from .models import ArticleCandidate


INNOVATION_SUPPORT_TAGS = {"科技创新", "半导体", "先进制造", "数字经济", "科技人才"}


def is_innovation_support_candidate(candidate: ArticleCandidate) -> bool:
    return bool(INNOVATION_SUPPORT_TAGS & set(candidate.topic_tags))


def innovation_support_sort_rank(candidate: ArticleCandidate) -> int:
    return 0 if is_innovation_support_candidate(candidate) else 1
