from __future__ import annotations

from .models import ArticleCandidate


INNOVATION_SUPPORT_TAGS = {"科技创新", "半导体", "先进制造", "数字经济", "科技人才", "国防AI"}
GOVERNANCE_ONLY_TAGS = {"AI治理", "科技治理"}
INNOVATION_ENABLING_GOVERNANCE_TERMS = {
    "technology policy",
    "tech policy",
    "digital policy",
    "pro-innovation regulation",
    "innovation-friendly regulation",
    "enabling regulation",
    "innovation policy instrument",
    "innovation policy instruments",
    "regulatory sandbox",
    "regulatory sandboxes",
    "public procurement",
    "procurement for innovation",
    "innovation-oriented procurement",
    "pre-commercial procurement",
    "standards infrastructure",
    "standards development",
    "standard-setting",
    "open standards",
    "quality infrastructure",
    "conformity assessment",
    "metrology",
    "measurement science",
    "testing infrastructure",
    "test and evaluation",
    "data interoperability",
    "data sharing",
    "public compute",
    "compute access",
    "technology transfer",
    "technology diffusion",
    "technology adoption",
    "科技创新政策",
    "创新政策工具",
    "促进创新",
    "监管沙盒",
    "创新采购",
    "标准基础设施",
    "标准制定",
    "开放标准",
    "质量基础设施",
    "合格评定",
    "计量科学",
    "测试验证",
    "数据互操作",
    "数据共享",
    "公共算力",
    "技术转移",
    "技术扩散",
    "技术采用",
}


def candidate_focus_text(candidate: ArticleCandidate) -> str:
    return " ".join(
        [
            candidate.title,
            candidate.chinese_title,
            candidate.summary,
            candidate.chinese_summary,
            " ".join(candidate.keywords),
            " ".join(candidate.subjects),
        ]
    ).lower()


def has_innovation_enabling_governance_signal(candidate: ArticleCandidate) -> bool:
    text = candidate_focus_text(candidate)
    return any(term.lower() in text for term in INNOVATION_ENABLING_GOVERNANCE_TERMS)


def is_innovation_support_candidate(candidate: ArticleCandidate) -> bool:
    tags = set(candidate.topic_tags)
    if INNOVATION_SUPPORT_TAGS & tags:
        return True
    if "科技治理" in tags and has_innovation_enabling_governance_signal(candidate):
        return True
    return False


def is_governance_only_candidate(candidate: ArticleCandidate) -> bool:
    tags = set(candidate.topic_tags)
    return bool(tags) and not is_innovation_support_candidate(candidate) and tags <= GOVERNANCE_ONLY_TAGS


def innovation_support_sort_rank(candidate: ArticleCandidate) -> int:
    if is_innovation_support_candidate(candidate):
        return 0
    if is_governance_only_candidate(candidate):
        return 2
    return 1
