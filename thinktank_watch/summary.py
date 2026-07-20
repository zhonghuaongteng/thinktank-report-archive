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
    r"(?:^|[\n\r\t 。，；;.!?！？])"
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
    parts = re.split(r"(?<=[。！？])\s*|(?<=[.!?])\s+", text)
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
    return ""


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
    return ""


def _normalize_overlap(value: str) -> str:
    return re.sub(
        r"[\s，。！？、；：,.!?;:()（）《》〈〉【】“”‘’\"'|·—\-]+",
        "",
        _clean(value),
    ).lower()


def dedupe_against(primary: str, secondary: str) -> str:
    """Drop sentences in ``secondary`` that already appear in ``primary``.

    Weekly briefs previously copied the same paragraph into 核心观点、建议 and
    中国/上海参考, which inflated length without adding information. This keeps
    only sentences that are genuinely new relative to ``primary``.
    """
    primary_norm = _normalize_overlap(primary)
    if not primary_norm:
        return _clean(secondary)
    kept: list[str] = []
    for sentence in _split_sentences(secondary):
        sentence_norm = _normalize_overlap(sentence)
        if not sentence_norm:
            continue
        if sentence_norm in primary_norm:
            continue
        if len(sentence_norm) > 40 and primary_norm in sentence_norm:
            continue
        kept.append(sentence)
    return " ".join(kept).strip()


MIN_DISTINCT_SECTION_CHARS = 24
PLACEHOLDER_SECTION_CUES = (
    "未检出明确政策建议",
    "未检出直接中国/上海指向",
    "未提供直接涉华",
    "未提供直接涉沪",
    "尚未拆出具体参照点",
    "需在后续精读中补充",
    "后续精读应优先核验",
    "待补充：",
)


def _is_placeholder_section(text: str) -> bool:
    """Detect boilerplate markers that carry no report-specific signal."""
    cleaned = _clean(text)
    if not cleaned:
        return True
    return len(cleaned) < 150 and any(cue in cleaned for cue in PLACEHOLDER_SECTION_CUES)


def _resolve_distinct_section(primary: str, text: str) -> str:
    """Keep ``text`` only when it adds signal beyond ``primary``.

    Sections that merely repeat the core argument, or whose deduplicated
    remainder is too thin to stand alone, are dropped entirely: a missing
    建议/中国上海参考 section is more honest than manufactured filler.
    """
    if _is_placeholder_section(text):
        return ""
    deduped = dedupe_against(primary, text)
    if _normalize_overlap(deduped) == _normalize_overlap(text):
        return _clean(text)
    if len(deduped) < MIN_DISTINCT_SECTION_CHARS:
        return ""
    return deduped


def summary_sections(candidate: ArticleCandidate) -> dict[str, str]:
    parsed = parse_structured_summary(candidate.chinese_summary)
    source = _fallback_source(candidate)
    core = parsed["核心观点"] or _fallback_core(candidate)
    advice = parsed["建议"] or _fallback_advice(candidate, source)
    reference = parsed["中国/上海参考"] or _fallback_china_shanghai_reference(candidate, source)

    advice = _resolve_distinct_section(core, advice)
    reference = _resolve_distinct_section(f"{core} {advice}", reference)

    return {
        "核心观点": core,
        "建议": advice,
        "中国/上海参考": reference,
    }


JUDGMENT_CUES = (
    "核心判断",
    "核心观点是",
    "报告认为",
    "文章认为",
    "该文认为",
    "核心结论",
    "认为",
    "主张",
    "判断",
    "持支持",
    "明确支持",
    "反对",
    "警示",
    "怀疑",
    "乐观",
    "立场",
)


def core_argument_parts(core_text: str, max_evidence: int = 4) -> tuple[str, list[str]]:
    """Split a 核心观点 block into (一句话核心判断, 主要论据 sentences).

    The judgment sentence prefers an explicit "核心判断是…" style sentence within
    the first few sentences; otherwise the first sentence is used. Remaining
    sentences become the evidence list so readers can grasp the argument
    without opening the source report.
    """
    sentences = _split_sentences(core_text)
    if not sentences:
        return "", []
    judgment_index = 0
    for index, sentence in enumerate(sentences[:4]):
        if any(cue in sentence for cue in JUDGMENT_CUES):
            judgment_index = index
            break
    judgment = sentences[judgment_index]
    evidence = [s for i, s in enumerate(sentences) if i != judgment_index]
    return judgment, evidence[:max_evidence]


def format_structured_chinese_summary(candidate: ArticleCandidate) -> str:
    sections = summary_sections(candidate)
    return "\n\n".join(
        f"### {label}\n\n{sections[label]}" for label in SUMMARY_LABELS if sections[label]
    )


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
        if not value:
            continue
        limit = limits.get(label, 520)
        lines.append(f"- {label}：{_truncate(value, limit)}")
    return lines
