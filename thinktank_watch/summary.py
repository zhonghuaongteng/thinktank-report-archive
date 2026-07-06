from __future__ import annotations

import re

from .models import ArticleCandidate


SUMMARY_LABELS = ("核心观点", "建议", "中国/上海参考")
SUMMARY_ALIASES = {
    "核心观点": (
        "核心观点",
        "核心判断",
        "主要观点",
        "核心结论",
        "内容摘要",
    ),
    "建议": (
        "建议",
        "政策建议",
        "行动建议",
        "对策建议",
        "启示建议",
    ),
    "中国/上海参考": (
        "中国/上海参考",
        "中国与上海参考",
        "中国参考",
        "上海参考",
        "涉华/涉沪参考",
        "涉华参考",
        "涉沪参考",
        "对中国/上海的参考",
        "中国/上海启示",
    ),
}
ALIAS_TO_LABEL = {alias: label for label, aliases in SUMMARY_ALIASES.items() for alias in aliases}
SECTION_PATTERN = re.compile(
    r"(?m)^\s*(?:#{2,4}\s*)?(?:[-*]\s*)?"
    r"("
    + "|".join(re.escape(alias) for alias in sorted(ALIAS_TO_LABEL, key=len, reverse=True))
    + r")"
    r"\s*(?:[:：])?\s*"
)
INLINE_SECTION_PATTERN = re.compile(
    r"(?:^|[\n\r\t ])"
    r"("
    + "|".join(re.escape(alias) for alias in sorted(ALIAS_TO_LABEL, key=len, reverse=True))
    + r")"
    r"\s*[:：]\s*"
)
ADVICE_CUES = (
    "建议",
    "应当",
    "应该",
    "应关注",
    "需关注",
    "需要",
    "需",
    "可将",
    "可作为",
    "适合",
    "后续",
    "值得",
    "启示",
    "关注",
    "补充",
    "建立",
    "完善",
)
ENGLISH_ADVICE_CUES = (
    "should",
    "must",
    "need",
    "needs",
    "recommend",
    "recommendation",
    "policy",
    "strategy",
    "strategies",
    "adapt",
    "address",
    "invest",
    "build",
    "strengthen",
    "government",
    "congress",
)
CHINA_SHANGHAI_CUES = (
    "中国",
    "上海",
    "长三角",
    "涉华",
    "涉沪",
    "对华",
    "北京",
    "China",
    "Chinese",
    "Shanghai",
    "PRC",
    "Sino",
)
WEAK_SUMMARY_CUES = (
    "download the report",
    "download report",
    "find out what",
    "learn more",
    "read more",
)
DETAIL_BOILERPLATE_CUES = (
    "source:",
    "figure ",
    "table ",
    "appendix ",
    "all data from",
    "the hoover institution",
    "tpa white paper series",
)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _split_sentences(value: str) -> list[str]:
    text = _clean(value)
    if not text:
        return []
    parts = re.split(r"(?<=[。！？.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def _split_paragraphs(value: str) -> list[str]:
    return [_clean(part) for part in re.split(r"\n\s*\n+", value or "") if _clean(part)]


def _join_limited(sentences: list[str], limit: int) -> str:
    selected: list[str] = []
    total = 0
    for sentence in sentences:
        next_total = total + len(sentence)
        if selected and next_total > limit:
            break
        selected.append(sentence)
        total = next_total
    return " ".join(selected).strip()


def _truncate(value: str, limit: int) -> str:
    text = _clean(value)
    if len(text) <= limit:
        return text
    sentence_text = _join_limited(_split_sentences(text), limit)
    if sentence_text:
        return sentence_text
    return text[:limit].rstrip() + "..."


def _summary_is_weak(value: str) -> bool:
    text = _clean(value).lower()
    if not text:
        return True
    return len(text) < 180 or any(cue in text for cue in WEAK_SUMMARY_CUES)


def _substantive_sentences(value: str) -> list[str]:
    sentences: list[str] = []
    for sentence in _split_sentences(value):
        lowered = sentence.lower()
        if len(sentence) < 45:
            continue
        if any(cue in lowered for cue in DETAIL_BOILERPLATE_CUES):
            continue
        if re.match(r"^(?:\d+\s+)?(?:figure|table|appendix)\b", lowered):
            continue
        sentences.append(sentence)
    return sentences


def _fallback_source(candidate: ArticleCandidate) -> str:
    if candidate.chinese_summary:
        return candidate.chinese_summary
    source = candidate.summary or ""
    if candidate.detail_text and _summary_is_weak(source):
        return candidate.detail_text
    return source or candidate.detail_text


def _full_text_available(candidate: ArticleCandidate) -> bool:
    return bool(candidate.detail_text and len(candidate.detail_text) >= 1200)


def parse_structured_summary(value: str) -> dict[str, str]:
    text = (value or "").strip()
    parsed = {label: "" for label in SUMMARY_LABELS}
    if not text:
        return parsed

    matches = list(SECTION_PATTERN.finditer(text))
    inline_matches = list(INLINE_SECTION_PATTERN.finditer(text))
    if len(inline_matches) > len(matches):
        matches = inline_matches
    if not matches:
        return parsed

    for index, match in enumerate(matches):
        label = ALIAS_TO_LABEL.get(match.group(1), "")
        if not label:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip(" \n\r\t:：-")
        if content:
            parsed[label] = _clean(f"{parsed[label]} {content}".strip())
    return parsed


def _fallback_core(candidate: ArticleCandidate) -> str:
    source = _fallback_source(candidate)
    if source:
        if not candidate.chinese_summary and _full_text_available(candidate):
            sentences = _substantive_sentences(source)
            if sentences:
                excerpt = _join_limited(sentences[:7], 1200)
                return (
                    "该材料可从以下要点把握："
                    f"{excerpt} "
                    "上述内容应作为后续中文精读、关键词标注和政策比较的主要证据入口。"
                )
        paragraphs = _split_paragraphs(source)
        return paragraphs[0] if paragraphs else _clean(source)
    return "待补充：尚未抽取中文摘要或可用英文公开摘要。"


def _fallback_advice(candidate: ArticleCandidate, source: str) -> str:
    sentences = _substantive_sentences(source) if _full_text_available(candidate) else _split_sentences(source)
    advice_sentences = [
        sentence
        for sentence in sentences
        if (
            any(cue in sentence for cue in ADVICE_CUES)
            or any(cue in sentence.lower() for cue in ENGLISH_ADVICE_CUES)
        )
        and not any(weak in sentence for weak in ("应对美中", "应对中美", "政策回应"))
    ]
    if advice_sentences:
        advice = _join_limited(advice_sentences[:5], 640)
        if not candidate.chinese_summary and _full_text_available(candidate):
            return "自动识别到的政策含义与建议线索包括：" + advice
        return advice
    if any(tag in candidate.topic_tags for tag in ("科技创新", "先进制造", "半导体", "数字经济", "科技人才")):
        return (
            "原文或现有摘要未检出明确政策建议；后续精读应优先核验其对研发投入、"
            "人才培养、科研基础设施、产业化通道、标准监管和国际竞争工具的具体主张。"
        )
    return "原文或现有摘要未检出明确政策建议、行动建议或机构作者的具体主张；需在后续精读中补充。"


def _fallback_china_shanghai_reference(candidate: ArticleCandidate, source: str) -> str:
    sentences = _substantive_sentences(source) if _full_text_available(candidate) else _split_sentences(source)
    shanghai_sentences = [
        sentence
        for sentence in sentences
        if any(cue in sentence for cue in ("上海", "长三角", "涉沪", "Shanghai"))
    ]
    if shanghai_sentences:
        if candidate.chinese_summary or not _full_text_available(candidate):
            return _join_limited(shanghai_sentences, 420)
        return "对上海和长三角的直接参考线索包括：" + _join_limited(shanghai_sentences[:4], 640)
    china_sentences = [
        sentence
        for sentence in sentences
        if any(cue in sentence for cue in CHINA_SHANGHAI_CUES)
    ]
    if china_sentences:
        if candidate.chinese_summary or not _full_text_available(candidate):
            return _join_limited(china_sentences, 420)
        reference = _join_limited(china_sentences[:5], 760)
        return (
            "对中国/上海研判的参考在于：该材料提供了涉华技术能力、人才流动、产业链位置或政策工具的比较证据。"
            f"关键原文线索包括：{reference}"
        )
    if "中国与上海相关" in candidate.topic_tags:
        return "已标记为中国/上海相关，但摘要尚未拆出具体参照点；后续需回到原文补充页码级证据。"
    return "未检出直接中国/上海指向；可作为同类政策工具、产业链、科研组织或治理框架的比较参照。"


def summary_sections(candidate: ArticleCandidate) -> dict[str, str]:
    parsed = parse_structured_summary(candidate.chinese_summary)
    source = _fallback_source(candidate)
    sections = {
        "核心观点": parsed["核心观点"] or _fallback_core(candidate),
        "建议": parsed["建议"] or _fallback_advice(candidate, source),
        "中国/上海参考": parsed["中国/上海参考"] or _fallback_china_shanghai_reference(candidate, source),
    }
    return sections


def format_structured_chinese_summary(candidate: ArticleCandidate) -> str:
    sections = summary_sections(candidate)
    return "\n\n".join(f"### {label}\n\n{sections[label]}" for label in SUMMARY_LABELS)


def render_summary_bullets(candidate: ArticleCandidate, cadence: str = "daily") -> list[str]:
    limits = {
        "daily": {
            "核心观点": 520,
            "建议": 300,
            "中国/上海参考": 360,
        },
        "weekly": {
            "核心观点": 820,
            "建议": 480,
            "中国/上海参考": 560,
        },
    }.get(cadence, {})
    sections = summary_sections(candidate)
    lines: list[str] = []
    for label in SUMMARY_LABELS:
        value = sections[label]
        limit = limits.get(label, 520)
        lines.append(f"- {label}：{_truncate(value, limit)}")
    return lines
