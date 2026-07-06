from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date as Date, timedelta
from html import escape
from io import BytesIO
from pathlib import Path
from textwrap import wrap

from .models import ArticleCandidate
from .focus import (
    GOVERNANCE_ONLY_TAGS,
    INNOVATION_SUPPORT_TAGS,
    innovation_support_sort_rank,
    is_governance_only_candidate,
    is_innovation_support_candidate,
)
from .kb import INDEX_RELATIVE
from .restore import parse_archive_markdown
from .summary import render_summary_bullets, summary_sections


MAX_EXPANDED_PRIORITY_ITEMS = 12
MIN_EXPANDED_INNOVATION_SUPPORT_ITEMS = 8
MAX_EXPANDED_GOVERNANCE_ONLY_ITEMS = 4
MAX_INDEX_ITEMS = 100
MAX_RECENT_WRITE_ITEMS = 8
WEEKLY_EXPANDED_PRIORITY_ITEMS = 18
WEEKLY_MIN_EXPANDED_INNOVATION_SUPPORT_ITEMS = 12
WEEKLY_MAX_INDEX_ITEMS = 160
WEEKLY_TECH_ITEMS = 12
WEEKLY_GOVERNANCE_ITEMS = 8
WEEKLY_SUPPORT_ITEMS = 18
WEEKLY_CHINA_ITEMS = 12
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
BRIEF_CADENCE_LABELS = {
    "daily": "国际科技智库动态简报",
    "weekly": "国际科技智库周报",
}
BRIEF_CADENCE_DIRECTORIES = {
    "daily": "daily",
    "weekly": "weekly",
}
IMAGE_MARKDOWN_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")


def published_date_sort_value(value: str) -> int:
    if len(value or "") < 10:
        return 0
    try:
        return int(value[:10].replace("-", ""))
    except ValueError:
        return 0


def sort_brief_candidates(candidates: list[ArticleCandidate]) -> list[ArticleCandidate]:
    indexed = list(enumerate(candidates))
    return [
        item
        for _, item in sorted(
            indexed,
            key=lambda pair: (
                PRIORITY_ORDER.get(pair[1].priority, 99),
                innovation_support_sort_rank(pair[1]),
                -pair[1].score,
                -published_date_sort_value(pair[1].published_date),
                pair[0],
            ),
        )
    ]


def select_innovation_support_items(candidates: list[ArticleCandidate], limit: int = 12) -> list[ArticleCandidate]:
    support_candidates = [
        item
        for item in candidates
        if INNOVATION_SUPPORT_TAGS & set(item.topic_tags) and not is_governance_only_candidate(item)
    ]
    if not support_candidates:
        support_candidates = [item for item in candidates if INNOVATION_SUPPORT_TAGS & set(item.topic_tags)]

    selected: list[ArticleCandidate] = []
    selected_urls: set[str] = set()
    selected_institutions: set[str] = set()

    for item in support_candidates:
        if len(selected) >= limit:
            break
        if item.institution_slug in selected_institutions:
            continue
        selected.append(item)
        selected_urls.add(item.url)
        selected_institutions.add(item.institution_slug)

    def add_first_with_tag(pool: list[ArticleCandidate], tag: str) -> None:
        if len(selected) >= limit:
            return
        for item in pool:
            if tag in item.topic_tags and item.url not in selected_urls:
                selected.append(item)
                selected_urls.add(item.url)
                return

    topic_order = ["科技创新", "先进制造", "半导体", "数字经济", "科技人才", "国防AI"]
    for tag in topic_order:
        add_first_with_tag(support_candidates, tag)
    p2_support = [item for item in support_candidates if item.priority == "P2"]
    for tag in topic_order:
        add_first_with_tag(p2_support, tag)
    for item in support_candidates:
        if len(selected) >= limit:
            break
        if item.url not in selected_urls:
            selected.append(item)
            selected_urls.add(item.url)
    return selected[:limit]


def select_expanded_priority_items(
    priority_items: list[ArticleCandidate],
    limit: int = MAX_EXPANDED_PRIORITY_ITEMS,
    min_innovation_support: int = MIN_EXPANDED_INNOVATION_SUPPORT_ITEMS,
    max_governance_only: int = MAX_EXPANDED_GOVERNANCE_ONLY_ITEMS,
) -> list[ArticleCandidate]:
    selected_urls: set[str] = set()
    selected: list[ArticleCandidate] = []

    def add(item: ArticleCandidate) -> None:
        if len(selected) >= limit or item.url in selected_urls:
            return
        selected.append(item)
        selected_urls.add(item.url)

    support_items = [item for item in priority_items if is_innovation_support_candidate(item)]
    for item in support_items[:min_innovation_support]:
        add(item)

    governance_only_count = 0
    governance_cap_enabled = bool(support_items)
    for item in priority_items:
        if is_governance_only_candidate(item) and governance_cap_enabled:
            if governance_only_count >= max_governance_only:
                continue
            governance_only_count += 1
        add(item)
    return selected[:limit]


def select_recent_write_items(candidates: list[ArticleCandidate], limit: int = MAX_RECENT_WRITE_ITEMS) -> list[ArticleCandidate]:
    return list(reversed(candidates[-limit:])) if candidates else []


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _short_text(value: str, limit: int = 220) -> str:
    text = _clean_text(value)
    if len(text) <= limit:
        return text
    match = re.search(r"[。！？.!?]", text[:limit])
    if match and match.end() >= 60:
        return text[: match.end()]
    return text[:limit].rstrip() + "..."


def _markdown_link(text: str, url: str) -> str:
    title = (text or "未命名条目").replace("[", "【").replace("]", "】")
    return f"[{title}]({url})" if url else title


def _bold_first_sentence(value: str) -> str:
    text = _clean_text(value)
    if not text:
        return ""
    match = re.search(r"[。！？.!?]", text)
    if match and match.end() <= 220:
        first = text[: match.end()]
        rest = text[match.end():].strip()
        return f"**{first}**" + (f" {rest}" if rest else "")
    return f"**{_short_text(text, 180)}**" + (f" {text[180:].strip()}" if len(text) > 180 else "")


def weekly_priority_items(candidates: list[ArticleCandidate]) -> list[ArticleCandidate]:
    return [item for item in sort_brief_candidates(candidates) if item.priority in {"P0", "P1"}]


def weekly_chapter_name(candidate: ArticleCandidate) -> str:
    tags = set(candidate.topic_tags)
    if "中国与上海相关" in tags:
        return "涉华科技竞争与上海参考"
    if tags & {"半导体", "先进制造"}:
        return "产业链、制造与能源基础设施"
    if tags & {"AI治理", "数字经济", "科技治理", "国防AI"}:
        return "AI、数字基础设施与技术治理"
    if tags & {"科技人才", "科技创新"}:
        return "科研体系、人才与创新政策"
    return "其他创新支撑观察"


PDF_TOC_LINES_PER_PAGE = 44
PDF_TOC_WIDTH_CHARS = 58
WEEKLY_COMIC_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
WEEKLY_COMIC_BLOCKED_TERMS = [
    "主题机制图解",
    "Codex 漫画待生成",
    "## 新增概览",
    "## 最近写入",
    "运行审计",
    "### 漫画",
    "## 导读漫画",
    "漫画 1",
]


def _topic_anchor(index: int) -> str:
    return f"topic-{index:02d}"


def _pdf_topic_key(index: int) -> str:
    return f"topic_{index:02d}"


def weekly_topic_comic_file(date: str, index: int) -> Path | None:
    comic_dir = Path("comic") / f"weekly-topic-comics-{date}" / "pages"
    matches = sorted(
        path
        for path in comic_dir.glob(f"{index:02d}-*")
        if path.suffix.lower() in WEEKLY_COMIC_SUFFIXES
    )
    return matches[0] if matches else None


def weekly_topic_comic_markdown_src(date: str, index: int) -> str | None:
    comic_path = weekly_topic_comic_file(date, index)
    if comic_path is None:
        return None
    return "../../../" + comic_path.as_posix()


def weekly_comic_run_dir(date: str, comic_root: str | Path = "comic") -> Path:
    return Path(comic_root) / f"weekly-topic-comics-{date}"


def weekly_comic_basename(index: int, candidate: ArticleCandidate) -> str:
    source = candidate.title or candidate.chinese_title or candidate.url or f"topic-{index}"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", source.lower()).strip("-")
    if not slug:
        slug = f"{candidate.institution_slug or 'source'}-{index:02d}"
    return f"{index:02d}-topic-{slug[:64].strip('-')}"


def load_weekly_archive_candidates(
    archive_root: str | Path,
    run_date: str,
    lookback_days: int = 14,
) -> list[ArticleCandidate]:
    end = Date.fromisoformat(run_date)
    start = end - timedelta(days=max(1, lookback_days) - 1)
    items: list[ArticleCandidate] = []
    for path in sorted(Path(archive_root).rglob("*.md")):
        try:
            candidate = parse_archive_markdown(path)
        except (KeyError, ValueError, OSError):
            continue
        if len(candidate.published_date or "") < 10:
            continue
        try:
            published = Date.fromisoformat(candidate.published_date[:10])
        except ValueError:
            continue
        if start <= published <= end:
            items.append(candidate)
    items.sort(key=lambda item: (item.published_date, item.institution_slug, item.title))
    return items


def weekly_comic_prompt_text(date: str, index: int, candidate: ArticleCandidate) -> str:
    sections = _weekly_summary_sections(candidate)
    source_title = candidate.chinese_title or candidate.title
    basename = weekly_comic_basename(index, candidate)
    tags = ", ".join(candidate.topic_tags) or "待分类"
    return f"""---
date: {date}
topic_index: {index}
priority: {candidate.priority}
institution: {candidate.institution_name}
source_url: {candidate.url}
output: ../pages/{basename}.jpg
aspect_ratio: "16:9"
style: "Codex-generated explanatory viewpoint comic"
---

# 主题 {index:02d} 漫画提示词

请生成一张 16:9 横版知识漫画，用于国际科技智库周报的单篇主题页。画面必须是漫画叙事场景，不得画成流程图、PPT 示意图、仪表盘模板或纯信息图。漫画不需要完整复刻报告论证链，重点是用科普化、可视化的视角让读者快速看懂文章观点。

## 报告锚点

- 机构：{candidate.institution_name}
- 标题：{source_title}
- 原文链接：{candidate.url}
- 优先级：{candidate.priority}
- 主题标签：{tags}

## 需要表达的核心内容

- 核心观点：{_clean_text(sections["核心观点"])}
- 建议或政策含义：{_clean_text(sections["建议"])}
- 中国/上海参考：{_clean_text(sections["中国/上海参考"])}

## 分镜要求

1. 第一格呈现报告识别到的关键信号，必须让读者一眼看出研究对象。
2. 第二格把报告观点转译成可视化场景，可以使用比喻、人物行动、实验台、城市系统、产业现场、数据屏、地图、技术栈、供应链剖面或政策工具箱。
3. 第三格突出报告最重要的解释：为什么这个问题重要，影响会如何传导，哪些主体会受影响。逻辑不必求全，但必须抓住文章观点。
4. 第四格收束到报告最重要的核心判断。不要强行落到中国或上海；只有原报告、摘要或资料标签存在明确涉华、涉沪或可操作参照时，才把中国/上海作为最后一格内容。否则，最后一格应突出报告本身的中心结论。
5. 证据配图转译：如果报告正文、摘要或图注中出现图表、数据曲线、地图、技术架构图、供应链图、照片或其他证据配图线索，可将其转译为漫画中的报告页、屏幕、白板、证据卡或背景装置；后续若自动化提供真实参考图，可作为参考素材纳入，但不得凭空复制未取得的原图。

## 视觉约束

- 风格：清线条、知识科普漫画、真实场景、明确视觉焦点、适合嵌入 PDF。
- 画面文字尽量短，优先使用大标题、路标、标签和少量中文短句；不要依赖大段图中文字解释观点。
- 机构名称只作为来源标识，不作为视觉主角。
- 不要出现“主题机制图解”“示意图”“占位图”等字样。
- 最终输出为可嵌入周报的单张图片，文件名应为 `{basename}.jpg`。
"""


def write_weekly_comic_prompts(
    date: str,
    candidates: list[ArticleCandidate],
    comic_root: str | Path = "comic",
) -> list[Path]:
    priority_items = weekly_priority_items(candidates)
    run_dir = weekly_comic_run_dir(date, comic_root)
    prompt_dir = run_dir / "prompts"
    page_dir = run_dir / "pages"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    page_dir.mkdir(parents=True, exist_ok=True)
    prompt_paths: list[Path] = []
    manifest_lines = [
        f"# {date} 周报 Codex 漫画生成清单",
        "",
        "本目录用于未来周报的逐条 P0/P1 Codex 漫画生成。漫画应从科普化、可视化角度突出报告核心观点，不要求完整复刻报告论证链；最后一格不强行转向中国或上海，只有报告存在明确涉华、涉沪或可操作参照时才纳入。",
        "",
    ]
    for index, item in enumerate(priority_items, 1):
        basename = weekly_comic_basename(index, item)
        prompt_path = prompt_dir / f"{basename}.md"
        prompt_path.write_text(weekly_comic_prompt_text(date, index, item), encoding="utf-8")
        prompt_paths.append(prompt_path)
        manifest_lines.append(
            f"- {index:02d}｜{item.priority}｜{item.institution_name}｜{item.chinese_title or item.title}｜"
            f"`prompts/{basename}.md` -> `pages/{basename}.jpg`"
        )
    (run_dir / "manifest.md").write_text("\n".join(manifest_lines).rstrip() + "\n", encoding="utf-8")
    return prompt_paths


def inspect_weekly_comic_report(
    date: str,
    candidates: list[ArticleCandidate],
    brief_root: str | Path = "briefs",
    comic_root: str | Path = "comic",
) -> dict[str, int | list[str]]:
    priority_count = len(weekly_priority_items(candidates))
    run_dir = weekly_comic_run_dir(date, comic_root)
    prompt_count = len(list((run_dir / "prompts").glob("*.md"))) if (run_dir / "prompts").exists() else 0
    comic_count = len(
        [
            path
            for path in (run_dir / "pages").glob("*")
            if path.suffix.lower() in WEEKLY_COMIC_SUFFIXES
        ]
    ) if (run_dir / "pages").exists() else 0
    brief_dir = Path(brief_root) / "weekly" / date[:4]
    stem = f"{date}_{BRIEF_CADENCE_LABELS['weekly']}"
    md_path = brief_dir / f"{stem}.md"
    html_path = brief_dir / f"{stem}.html"
    pdf_path = brief_dir / f"{stem}.pdf"
    md_text = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
    html_text = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    blocked_hits = [term for term in WEEKLY_COMIC_BLOCKED_TERMS if term in md_text or term in html_text]
    pdf_images = 0
    if pdf_path.exists():
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(pdf_path))
            for page in reader.pages:
                resources = page.get("/Resources") or {}
                xobjects = resources.get("/XObject") or {}
                for xobject in xobjects.values():
                    obj = xobject.get_object()
                    if obj.get("/Subtype") == "/Image":
                        pdf_images += 1
        except Exception:
            pdf_images = -1
    return {
        "priority_count": priority_count,
        "prompt_count": prompt_count,
        "comic_count": comic_count,
        "md_image_refs": md_text.count("![主题 "),
        "html_image_nodes": html_text.count('<figure class="comic"'),
        "pdf_image_count": pdf_images,
        "blocked_hits": blocked_hits,
        "missing_files": [
            str(path)
            for path in [md_path, html_path, pdf_path]
            if not path.exists()
        ],
    }


def _weekly_pdf_toc_entry_lines(index: int, item: ArticleCandidate, page: int) -> list[str]:
    title = item.chinese_title or item.title
    text = f"P.{page:02d}  主题 {index:02d}｜[{item.priority}] {title}"
    wrapped = wrap(_clean_text(text), width=PDF_TOC_WIDTH_CHARS)
    if len(wrapped) <= 1:
        return wrapped
    return [wrapped[0], *[f"    {line}" for line in wrapped[1:]]]


def _weekly_pdf_toc_page_count(priority_items: list[ArticleCandidate]) -> int:
    if not priority_items:
        return 1
    pages = 1
    used_lines = 0
    for index, item in enumerate(priority_items, 1):
        needed = len(_weekly_pdf_toc_entry_lines(index, item, 99)) + 1
        if used_lines and used_lines + needed > PDF_TOC_LINES_PER_PAGE:
            pages += 1
            used_lines = 0
        used_lines += needed
    return pages


def weekly_pdf_page_plan(candidates: list[ArticleCandidate]) -> tuple[dict[str, int], dict[str, int]]:
    priority_items = weekly_priority_items(candidates)
    toc_pages = _weekly_pdf_toc_page_count(priority_items)
    topic_start_page = 2 + toc_pages
    topic_pages = {item.url: topic_start_page + index for index, item in enumerate(priority_items)}
    return topic_pages, topic_pages


def _comic_lines(candidate: ArticleCandidate) -> list[tuple[str, str]]:
    sections = summary_sections(candidate)
    return [
        ("报告信号", _short_text(sections["核心观点"], 300)),
        ("真正矛盾", _short_text(_comic_tension(candidate), 280)),
        ("传导链条", _short_text(_comic_transmission(candidate), 260)),
        ("中国/上海参考", _short_text(sections["中国/上海参考"], 300)),
    ]


def _comic_tension(candidate: ArticleCandidate) -> str:
    tags = set(candidate.topic_tags)
    if "中国与上海相关" in tags and tags & {"半导体", "先进制造", "科技治理"}:
        return "关键矛盾在于，技术能力、出口管制、供应链安全和产业开放同时作用，政策判断不能只看单一技术指标。"
    if tags & {"AI治理", "国防AI"}:
        return "关键矛盾在于，AI能力扩散速度快于安全评估、行业标准和责任分配，创新收益与系统性风险同步上升。"
    if tags & {"先进制造", "半导体"}:
        return "关键矛盾在于，制造能力、能源供给、关键材料和市场准入开始绑定，产业竞争转向全链条韧性。"
    if tags & {"数字经济"}:
        return "关键矛盾在于，算力、数据、云服务和平台规则成为创新底座，基础设施配置会直接影响产业化速度。"
    if tags & {"科技人才"}:
        return "关键矛盾在于，科研和产业竞争最终落到人才供给、技能结构、流动制度和长期培养能力。"
    return "关键矛盾在于，报告讨论的政策工具会改变创新资源配置，需要从能力建设、产业化和风险治理同时判断。"


def _comic_transmission(candidate: ArticleCandidate) -> str:
    tags = set(candidate.topic_tags)
    chain: list[str] = []
    if "科技创新" in tags:
        chain.append("研发体系")
    if "半导体" in tags:
        chain.append("芯片与硬件瓶颈")
    if "先进制造" in tags:
        chain.append("制造和供应链")
    if "数字经济" in tags:
        chain.append("算力、数据和平台")
    if "科技人才" in tags:
        chain.append("人才和技能")
    if "中国与上海相关" in tags:
        chain.append("中国/上海产业参照")
    if not chain:
        chain.append("政策工具")
        chain.append("产业化路径")
    return "传导链条：" + " -> ".join(chain[:5]) + "。阅读时应追问该链条中哪个环节最可能成为瓶颈或政策抓手。"


def _has_explicit_summary_label(candidate: ArticleCandidate, label: str) -> bool:
    aliases = {
        "建议": ("建议", "政策建议", "行动建议", "对策建议", "启示建议"),
        "中国/上海参考": (
            "中国/上海参考",
            "中国与上海参考",
            "中国参考",
            "上海参考",
            "涉华/涉沪参考",
            "涉华参考",
            "涉沪参考",
            "中国/上海启示",
        ),
    }.get(label, ())
    if not aliases:
        return False
    pattern = r"(?:" + "|".join(re.escape(alias) for alias in aliases) + r")\s*[:：]"
    return bool(re.search(pattern, candidate.chinese_summary or ""))


def _normalized_card_text(value: str) -> str:
    return re.sub(r"[\s，。！？、；：,.!?;:()（）《》“”\"'|]+", "", _clean_text(value)).lower()


def _needs_weekly_card_enrichment(value: str, core: str) -> bool:
    text = _clean_text(value)
    if len(text) < 90:
        return True
    normalized = _normalized_card_text(text)
    normalized_core = _normalized_card_text(core)
    if not normalized or not normalized_core:
        return False
    if normalized == normalized_core:
        return True
    return len(normalized) > 80 and (normalized in normalized_core or normalized_core in normalized)


def _thematic_weekly_advice(candidate: ArticleCandidate) -> str:
    tags = set(candidate.topic_tags)
    if "中国与上海相关" in tags and "国防AI" in tags:
        return (
            "建议把该条目作为军民两用物流、智能供应链、网络安全和模型可靠性的联动观察入口；"
            "后续应核验相关判断是否外溢到出口管制、云服务、工业软件和城市级安全评估。"
        )
    if tags & {"AI治理", "国防AI"}:
        return (
            "建议跟踪该议题如何进入测试评估、采购规则、责任划分和跨境数据安排；"
            "对本地政策研判而言，重点在于识别哪些安全要求会直接改变模型、算力和应用场景的扩散速度。"
        )
    if tags & {"半导体", "先进制造"}:
        return (
            "建议沿设备、材料、能源、关键零部件、市场准入和供应链韧性建立持续跟踪表；"
            "判断重点应放在产业链瓶颈是否会从单点技术约束转化为系统性成本和产能约束。"
        )
    if "数字经济" in tags:
        return (
            "建议关注算力、云服务、数据可得性和平台规则之间的组合效应；"
            "后续研判应把基础设施供给、场景开放和安全合规作为同一套创新条件来观察。"
        )
    if "科技人才" in tags:
        return (
            "建议把人才流动、技能结构、科研组织和长期培养机制放在同一框架下跟踪；"
            "短期政策工具需要对应到关键岗位供给、跨学科训练和产业端吸纳能力。"
        )
    return (
        "建议把该条目纳入政策工具与创新能力的关系表，继续核验其对研发投入、基础设施、"
        "产业化路径、标准监管和国际竞争工具的具体含义。"
    )


def _thematic_weekly_reference(candidate: ArticleCandidate) -> str:
    tags = set(candidate.topic_tags)
    if "中国与上海相关" in tags and "国防AI" in tags:
        return (
            "对中国/上海的参考在于，军民两用供应链、智能物流、公共算力和网络韧性可能同时进入技术竞争视野；"
            "上海可重点关注城市级场景、产业链安全测试和关键平台外溢规则。"
        )
    if "中国与上海相关" in tags and tags & {"半导体", "先进制造"}:
        return (
            "对中国/上海的参考在于，外部产业政策和安全规则会影响设备、材料、制造服务和跨国企业研发配置；"
            "上海应优先识别可替代环节、开放合作窗口和供应链压力测试场景。"
        )
    if "中国与上海相关" in tags:
        return (
            "对中国/上海的参考在于，该条目提供了外部机构观察中国科技能力、监管工具或产业竞争位置的证据；"
            "上海可据此校准产业政策、平台治理和国际合作中的风险识别口径。"
        )
    if tags & {"AI治理", "数字经济"}:
        return (
            "对上海的间接参考在于，AI治理、数据制度和算力基础设施会影响创新扩散速度；"
            "可用于比较公共算力、数据服务、场景开放和合规评估的政策组合。"
        )
    if tags & {"半导体", "先进制造"}:
        return (
            "对上海的间接参考在于，制造业创新越来越依赖供应链韧性、能源条件和关键工艺生态；"
            "可用于对照本地先进制造、集成电路和产业链协同政策。"
        )
    return "对中国/上海的参考主要是比较政策工具和创新组织方式；后续可结合本地产业链、科研平台和治理场景补充实证证据。"


def _weekly_summary_sections(candidate: ArticleCandidate) -> dict[str, str]:
    sections = dict(summary_sections(candidate))
    core = sections["核心观点"]
    if not _has_explicit_summary_label(candidate, "建议") and _needs_weekly_card_enrichment(sections["建议"], core):
        sections["建议"] = _thematic_weekly_advice(candidate)
    if not _has_explicit_summary_label(candidate, "中国/上海参考") and _needs_weekly_card_enrichment(
        sections["中国/上海参考"], core
    ):
        sections["中国/上海参考"] = _thematic_weekly_reference(candidate)
    return sections


def _tracking_question(candidate: ArticleCandidate) -> str:
    tags = set(candidate.topic_tags)
    if "中国与上海相关" in tags and tags & {"AI治理", "国防AI", "数字经济"}:
        return "后续追踪美欧对中国 AI 能力、安全议程和出口策略的判断是否转化为标准、采购、算力、模型出海或城市级治理约束。"
    if "中国与上海相关" in tags and tags & {"半导体", "先进制造", "科技治理"}:
        return "后续追踪技术管制、供应链重组和产业补贴是否改变跨国企业在华研发、制造、采购和上海产业协同空间。"
    if tags & {"半导体", "先进制造"}:
        return "后续追踪关键材料、设备、能源和制造环节中哪一项最可能成为创新扩散的硬约束。"
    if tags & {"AI治理", "数字经济", "国防AI"}:
        return "后续追踪算力、数据、模型评测和平台规则是否形成新的准入门槛，及其对应用型企业的成本影响。"
    if tags & {"科技人才", "科技创新"}:
        return "后续追踪人才、科研组织和公共平台供给是否真正改善从研发到产业化的反馈速度。"
    return "后续追踪该报告提出的政策工具是否会改变创新资源配置、产业化路径和风险承担结构。"


_WEEKLY_PDF_NON_CORE_LABEL_PATTERN = re.compile(
    r"(?:建议|政策建议|行动建议|对策建议|启示建议|中国/上海参考|中国与上海参考|中国参考|上海参考|涉华/涉沪参考|涉华参考|涉沪参考|对中国/上海的参考|中国/上海启示)\s*[:：]"
)
_WEEKLY_PDF_LABEL_PREFIX_PATTERN = re.compile(
    r"^(?:核心观点|核心判断|主要观点|核心结论|内容摘要|建议|政策建议|行动建议|对策建议|启示建议|中国/上海参考|中国与上海参考|中国参考|上海参考|涉华/涉沪参考|涉华参考|涉沪参考|对中国/上海的参考|中国/上海启示)\s*[:：]\s*"
)


def _strip_weekly_pdf_label_prefix(value: str) -> str:
    return _WEEKLY_PDF_LABEL_PREFIX_PATTERN.sub("", _clean_text(value)).strip()


def _weekly_pdf_core_text(value: str) -> str:
    core = _strip_weekly_pdf_label_prefix(value)
    return _WEEKLY_PDF_NON_CORE_LABEL_PATTERN.split(core, maxsplit=1)[0].strip()


def _weekly_pdf_article_title(candidate: ArticleCandidate) -> str:
    return _clean_text(candidate.chinese_title or candidate.title or "未命名报告")


def _strip_weekly_pdf_argument_label(value: str) -> str:
    return re.sub(r"^(?:核心矛盾|传导链条)[:：]\s*", "", _clean_text(value)).strip()


def _weekly_pdf_main_argument(candidate: ArticleCandidate, sections: dict[str, str]) -> str:
    core = _weekly_pdf_core_text(sections["核心观点"])
    source_title = _weekly_pdf_article_title(candidate)
    if core:
        lead = f"这篇报告讨论的是“{source_title}”。核心判断是：{core}"
    else:
        lead = f"这篇报告讨论的是“{source_title}”。核心判断需回到原文进一步补全，但该条目已被识别为本周 P0/P1 重点。"
    tension = _strip_weekly_pdf_argument_label(_comic_tension(candidate))
    transmission = re.sub(r"阅读时应追问.*$", "", _strip_weekly_pdf_argument_label(_comic_transmission(candidate))).strip()
    parts = [
        lead,
        f"报告的论述线索集中在：{tension}" if tension else "",
        f"影响路径可以概括为：{transmission}" if transmission else "",
    ]
    unique_parts: list[str] = []
    for part in parts:
        if not part:
            continue
        if any(part in existing or existing in part for existing in unique_parts):
            continue
        unique_parts.append(part)
    return " ".join(unique_parts)


def _weekly_pdf_implication(sections: dict[str, str]) -> str:
    advice = _strip_weekly_pdf_label_prefix(sections["建议"])
    reference = _strip_weekly_pdf_label_prefix(sections["中国/上海参考"])
    advice = re.sub(_WEEKLY_PDF_NON_CORE_LABEL_PATTERN, " ", advice).strip()
    reference = re.sub(_WEEKLY_PDF_NON_CORE_LABEL_PATTERN, " ", reference).strip()
    if reference and "未检出" not in reference and "未提供" not in reference:
        if reference in advice:
            return advice
        if advice in reference:
            return reference
        return f"{advice} {reference}" if advice else reference
    return advice or reference


def weekly_situation_summary(candidates: list[ArticleCandidate]) -> str:
    priority_items = weekly_priority_items(candidates)
    if not priority_items:
        return "本周未形成 P0/P1 重点条目，后续仅需维持低频巡检和来源健康检查。"
    chapter_counter: Counter[str] = Counter(weekly_chapter_name(item) for item in priority_items)
    top_chapters = [name for name, _ in chapter_counter.most_common(2)]
    china_count = sum(1 for item in priority_items if "中国与上海相关" in item.topic_tags)
    ai_count = sum(1 for item in priority_items if {"AI治理", "数字经济", "国防AI"} & set(item.topic_tags))
    industrial_count = sum(1 for item in priority_items if {"半导体", "先进制造"} & set(item.topic_tags))
    signals = []
    if top_chapters:
        signals.append("重点集中在" + "、".join(top_chapters))
    if china_count:
        signals.append(f"涉华与上海参考条目 {china_count} 条")
    if ai_count:
        signals.append(f"AI、数字基础设施和国防AI信号 {ai_count} 条")
    if industrial_count:
        signals.append(f"产业链、制造和能源基础设施信号 {industrial_count} 条")
    sentence = "；".join(signals)
    return (
        f"本周形成 {len(priority_items)} 条 P0/P1 重点。{sentence}。"
        "主要态势是：国际科技政策讨论正转向创新资源、供应链韧性、算力平台、产业准入和安全规则的组合竞争。"
        "上海参考应优先聚焦产业链压力测试、公共算力与场景供给、关键平台迁移能力和国际规则外溢跟踪。"
    )


def render_weekly_reader_markdown(date: str, candidates: list[ArticleCandidate]) -> str:
    priority_items = weekly_priority_items(candidates)
    topic_pages, _ = weekly_pdf_page_plan(candidates)
    chapter_groups: dict[str, list[ArticleCandidate]] = {}
    for item in priority_items:
        chapter_groups.setdefault(weekly_chapter_name(item), []).append(item)

    lines = [
        f"# 国际科技智库周报（{date}）",
        "",
        "## 目录",
        "",
    ]
    for index, item in enumerate(priority_items, 1):
        lines.append(
            f"- P.{topic_pages[item.url]:02d}｜[主题 {index:02d}｜{item.chinese_title or item.title}](#{_topic_anchor(index)})"
        )
    lines.extend(["", "## 本周态势", "", weekly_situation_summary(candidates), "", "## 主题展开", ""])
    if not priority_items:
        lines.extend(["本周无 P0/P1 重点条目。", ""])
    for index, item in enumerate(priority_items, 1):
        title = item.chinese_title or item.title
        sections = _weekly_summary_sections(item)
        lines.extend(
            [
                f'<a id="{_topic_anchor(index)}"></a>',
                f"### 主题 {index:02d}｜[{item.priority}] {_markdown_link(title, item.url)}",
                "",
                f"- **来源**：{item.institution_name}",
                f"- **主题**：{', '.join(item.topic_tags) or '待分类'}",
            ]
        )
        comic_src = weekly_topic_comic_markdown_src(date, index)
        if comic_src:
            lines.extend(["", f"![主题 {index:02d} 漫画]({comic_src})", ""])
        for label, value in _comic_lines(item):
            if label == "中国/上海参考":
                continue
            lines.append(f"- **{label}**：{_bold_first_sentence(value)}")
        lines.extend(
            [
                f"- **核心观点**：{_bold_first_sentence(sections['核心观点'])}",
                f"- **建议**：{_bold_first_sentence(sections['建议'])}",
                f"- **中国/上海参考**：{_bold_first_sentence(sections['中国/上海参考'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_weekly_audit_markdown(date: str, candidates: list[ArticleCandidate]) -> str:
    ordered_candidates = sort_brief_candidates(candidates)
    priority_items = [item for item in ordered_candidates if item.priority in {"P0", "P1"}]
    recent_write_items = select_recent_write_items(candidates)
    topic_counter: Counter[str] = Counter(tag for item in candidates for tag in item.topic_tags)
    innovation_support_count = sum(1 for item in candidates if is_innovation_support_candidate(item))
    governance_only_count = sum(1 for item in candidates if is_governance_only_candidate(item))

    lines = [
        f"# 国际科技智库周报资料索引与生成记录（{date}）",
        "",
        "## 新增概览",
        "",
        f"- 新增条目：{len(candidates)}",
        f"- P0/P1重点：{len(priority_items)}",
        f"- 创新支撑条目：{innovation_support_count}",
        f"- 纯治理条目：{governance_only_count}",
        f"- 涉及机构：{len({item.institution_slug for item in candidates})}",
        f"- 高频主题：{', '.join(name for name, _ in topic_counter.most_common(8)) or '无'}",
        "",
        "## 最近写入",
        "",
    ]
    if recent_write_items:
        for item in recent_write_items:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}｜{item.url}")
    else:
        lines.append("- 无最近写入。")
    lines.extend(["", "## 完整索引", ""])
    for item in ordered_candidates:
        lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}｜{item.url}")
    return "\n".join(lines).rstrip() + "\n"


def render_periodic_brief_markdown(
    date: str,
    candidates: list[ArticleCandidate],
    cadence: str = "daily",
    comic_paths: list[str] | None = None,
    comic_notes: list[str] | None = None,
) -> str:
    if cadence == "weekly":
        return render_weekly_reader_markdown(date, candidates)

    title = BRIEF_CADENCE_LABELS.get(cadence, BRIEF_CADENCE_LABELS["daily"])
    period_word = "本周" if cadence == "weekly" else "本日"
    expanded_limit = WEEKLY_EXPANDED_PRIORITY_ITEMS if cadence == "weekly" else MAX_EXPANDED_PRIORITY_ITEMS
    min_support = (
        WEEKLY_MIN_EXPANDED_INNOVATION_SUPPORT_ITEMS
        if cadence == "weekly"
        else MIN_EXPANDED_INNOVATION_SUPPORT_ITEMS
    )
    index_limit = WEEKLY_MAX_INDEX_ITEMS if cadence == "weekly" else MAX_INDEX_ITEMS
    tech_limit = WEEKLY_TECH_ITEMS if cadence == "weekly" else 8
    governance_limit = WEEKLY_GOVERNANCE_ITEMS if cadence == "weekly" else 5
    support_limit = WEEKLY_SUPPORT_ITEMS if cadence == "weekly" else 12
    china_limit = WEEKLY_CHINA_ITEMS if cadence == "weekly" else 8
    ordered_candidates = sort_brief_candidates(candidates)
    priority_items = [item for item in ordered_candidates if item.priority in {"P0", "P1"}]
    expanded_priority_items = select_expanded_priority_items(
        priority_items,
        limit=expanded_limit,
        min_innovation_support=min_support,
    )
    recent_write_items = select_recent_write_items(candidates)
    expanded_priority_urls = {item.url for item in expanded_priority_items}
    overflow_priority_items = [item for item in priority_items if item.url not in expanded_priority_urls]
    index_items = [*overflow_priority_items, *[item for item in ordered_candidates if item.priority not in {"P0", "P1"}]]
    topic_counter: Counter[str] = Counter(tag for item in candidates for tag in item.topic_tags)
    innovation_support_count = sum(1 for item in candidates if is_innovation_support_candidate(item))
    governance_only_count = sum(1 for item in candidates if is_governance_only_candidate(item))

    lines = [
        f"# {title}（{date}）",
        "",
    ]
    if cadence == "weekly":
        lines.extend(["## 漫画导读", ""])
        if comic_paths:
            for index, comic_path in enumerate(comic_paths, 1):
                lines.append(f"![漫画导读{index}]({comic_path})")
                if comic_notes and index <= len(comic_notes):
                    note = comic_notes[index - 1].strip()
                    if note:
                        lines.extend(["", f"读图说明{index}：{note}"])
        else:
            lines.append("本周漫画导读尚未接入自动生成图片；样式确认后应在周报正文前插入1-3页漫画导读。")
        lines.append("")

    lines.extend(
        [
        "## 新增概览",
        "",
        f"- 新增条目：{len(candidates)}",
        f"- P0/P1重点：{len(priority_items)}",
        f"- 创新支撑条目：{innovation_support_count}",
        f"- 纯治理条目：{governance_only_count}",
        f"- 涉及机构：{len({item.institution_slug for item in candidates})}",
        f"- 高频主题：{', '.join(name for name, _ in topic_counter.most_common(6)) or '无'}",
        "",
        "## 最近写入",
        "",
        ]
    )
    if recent_write_items:
        for item in recent_write_items:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}｜{item.url}")
    else:
        lines.append(f"{period_word}暂无新增写入。")
    lines.extend(
        [
            "",
            "## P0/P1重点",
            "",
        ]
    )
    if not priority_items:
        lines.extend([f"{period_word}无P0/P1新增重点。", ""])
    else:
        for item in expanded_priority_items:
            title = item.chinese_title or item.title
            lines.extend(
                [
                    f"### [{item.priority}] {title}",
                    "",
                    f"- 机构：{item.institution_name}",
                    f"- 主题：{', '.join(item.topic_tags) or '待分类'}",
                    f"- 链接：{item.url}",
                    *render_summary_bullets(item, cadence=cadence),
                    "",
                ]
            )

    lines.extend(["## 科技创新支撑重点", ""])
    tech_items = [item for item in ordered_candidates if is_innovation_support_candidate(item)]
    if tech_items:
        for item in tech_items[:tech_limit]:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}")
    else:
        lines.append(f"{period_word}未检出科技创新支撑强相关条目。")

    governance_items = [item for item in ordered_candidates if is_governance_only_candidate(item)]
    if governance_items:
        lines.extend(["", "## AI治理与科技治理观察", ""])
        for item in governance_items[:governance_limit]:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}")

    lines.extend(["", "## 广义科技创新支撑", ""])
    support_items = select_innovation_support_items(ordered_candidates)
    if support_items:
        for item in support_items[:support_limit]:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}")
    else:
        lines.append(f"{period_word}未检出区域创新、先进制造、数字基础设施、半导体或科技人才相关条目。")

    lines.extend(["", "## 涉华/涉沪判断", ""])
    china_items = [item for item in ordered_candidates if "中国与上海相关" in item.topic_tags]
    if china_items:
        for item in china_items[:china_limit]:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}｜{item.url}")
    else:
        lines.append(f"{period_word}未检出中国/上海强相关条目。")

    lines.extend(["", "## 新增索引", ""])
    for item in index_items[:index_limit]:
        lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}｜{item.url}")
    omitted = len(index_items) - index_limit
    if omitted > 0:
        lines.append(f"- 其余 {omitted} 条已写入私有归档和知识库索引。")

    lines.extend(["", "## 后续推进", "", "- 对P0/P1条目补充中文研判、页码级证据和可复用表述。"])
    return "\n".join(lines) + "\n"


def render_daily_brief_markdown(date: str, candidates: list[ArticleCandidate]) -> str:
    return render_periodic_brief_markdown(date, candidates, cadence="daily")


def render_weekly_brief_markdown(date: str, candidates: list[ArticleCandidate]) -> str:
    return render_periodic_brief_markdown(date, candidates, cadence="weekly")


def load_daily_brief_candidates(
    archive_root: str | Path,
    kb_root: str | Path,
    run_date: str,
) -> list[ArticleCandidate]:
    index_path = Path(kb_root) / INDEX_RELATIVE
    if not index_path.exists():
        return []

    urls: list[str] = []
    seen_urls: set[str] = set()
    with index_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            url = row.get("原始链接", "")
            if row.get("抓取日期") != run_date or not url or url in seen_urls:
                continue
            seen_urls.add(url)
            urls.append(url)

    if not urls:
        return []

    archived: dict[str, ArticleCandidate] = {}
    for path in sorted(Path(archive_root).rglob("*.md")):
        try:
            candidate = parse_archive_markdown(path)
        except (KeyError, ValueError, OSError):
            continue
        archived[candidate.url] = candidate
    return [archived[url] for url in urls if url in archived]


def _inline_markdown_to_html(text: str) -> str:
    escaped = escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        escaped,
    )
    return escaped


def markdown_to_html(markdown_text: str, title: str) -> str:
    body_lines: list[str] = []
    open_card = False

    def close_card() -> None:
        nonlocal open_card
        if open_card:
            body_lines.append("</section>")
            open_card = False

    for line in markdown_text.splitlines():
        image_match = IMAGE_MARKDOWN_RE.match(line.strip())
        if image_match:
            close_card()
            alt, src = image_match.groups()
            body_lines.append(
                f'<figure class="comic"><img src="{escape(src, quote=True)}" alt="{escape(alt, quote=True)}"></figure>'
            )
        elif line.startswith('<a id="topic-') and line.endswith('"></a>'):
            close_card()
            body_lines.append(line)
        elif line.startswith("# "):
            close_card()
            body_lines.append(f"<h1>{_inline_markdown_to_html(line[2:])}</h1>")
        elif line.startswith("## "):
            close_card()
            body_lines.append(f"<h2>{_inline_markdown_to_html(line[3:])}</h2>")
        elif line.startswith("### "):
            close_card()
            card_class = "topic-card" if line.startswith("### 主题") else "section-heading"
            body_lines.append(f'<section class="{card_class}"><h3>{_inline_markdown_to_html(line[4:])}</h3>')
            open_card = True
        elif line.startswith("#### "):
            close_card()
            body_lines.append(f'<section class="point-card"><h3>{_inline_markdown_to_html(line[5:])}</h3>')
            open_card = True
        elif line.startswith("- "):
            body_lines.append(f'<p class="bullet">{_inline_markdown_to_html(line[2:])}</p>')
        elif line.startswith("> "):
            close_card()
            body_lines.append(f'<p class="dek">{_inline_markdown_to_html(line[2:])}</p>')
        elif line.strip():
            body_lines.append(f"<p>{_inline_markdown_to_html(line)}</p>")
        else:
            body_lines.append("")
    close_card()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
body {{ font-family: "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif; margin: 0; color: #16202a; line-height: 1.62; background: #f3f6f8; }}
body::before {{ content: ""; display: block; height: 10px; background: linear-gradient(90deg, #1f5f8b, #b84c3d, #4f7d5a); }}
main {{ max-width: 980px; margin: 0 auto; padding: 38px 38px 70px; background: #fbfcfd; box-shadow: 0 20px 50px rgba(22,32,42,.10); }}
h1 {{ font-size: 30px; border-bottom: 3px solid #1f5f8b; padding-bottom: 14px; margin-top: 0; }}
h2 {{ font-size: 21px; margin-top: 34px; color: #1f5f8b; border-left: 6px solid #b84c3d; padding-left: 12px; }}
h3 {{ font-size: 17px; margin: 0 0 12px; }}
p {{ font-size: 13px; margin: 7px 0; }}
a {{ color: #155c91; font-weight: 700; text-decoration: none; }}
strong {{ color: #8b2f2a; font-weight: 800; }}
.dek {{ font-size: 14px; background: #eaf1f6; padding: 12px 14px; border-left: 5px solid #1f5f8b; }}
.bullet {{ padding-left: 12px; }}
.topic-card, .point-card {{ border-radius: 8px; padding: 18px 20px; margin: 18px 0; page-break-inside: avoid; }}
.topic-card {{ background: #fff7ec; border: 1px solid #e4b36e; box-shadow: inset 0 0 0 2px #f4dfbd; }}
.point-card {{ background: #f6faf6; border: 1px solid #9eb99f; box-shadow: inset 0 0 0 2px #e2efe2; }}
.section-heading {{ background: #eef3f7; border: 1px solid #c7d7e3; border-radius: 8px; padding: 14px 18px; margin: 22px 0 12px; }}
.comic {{ margin: 18px 0 22px; }}
.comic img {{ max-width: 100%; border: 1px solid #d7dee5; }}
@media print {{ .topic-card, .point-card {{ page-break-before: always; }} main {{ box-shadow: none; }} }}
</style>
</head>
<body>
<main>
{chr(10).join(body_lines)}
</main>
</body>
</html>
"""


def write_periodic_brief(
    root: str | Path,
    date: str,
    candidates: list[ArticleCandidate],
    cadence: str = "daily",
    comic_paths: list[str] | None = None,
    comic_notes: list[str] | None = None,
) -> tuple[Path, Path, Path]:
    title = BRIEF_CADENCE_LABELS.get(cadence, BRIEF_CADENCE_LABELS["daily"])
    directory_name = BRIEF_CADENCE_DIRECTORIES.get(cadence, BRIEF_CADENCE_DIRECTORIES["daily"])
    year = date[:4]
    directory = Path(root) / directory_name / year
    directory.mkdir(parents=True, exist_ok=True)
    markdown_path = directory / f"{date}_{title}.md"
    html_path = directory / f"{date}_{title}.html"
    markdown = render_periodic_brief_markdown(
        date,
        candidates,
        cadence=cadence,
        comic_paths=comic_paths,
        comic_notes=comic_notes,
    )
    markdown_path.write_text(markdown, encoding="utf-8")
    if cadence == "weekly":
        audit_path = directory / f"{date}_{title}_资料索引.md"
        audit_path.write_text(render_weekly_audit_markdown(date, candidates), encoding="utf-8")
    html_path.write_text(markdown_to_html(markdown, f"{title}（{date}）"), encoding="utf-8")
    if cadence == "weekly":
        pdf_path = write_weekly_reader_pdf(directory / f"{date}_{title}.pdf", date, candidates)
    else:
        pdf_path = write_pdf_brief(directory / f"{date}_{title}.pdf", markdown, base_dir=directory)
    return markdown_path, html_path, pdf_path


def write_daily_brief(root: str | Path, date: str, candidates: list[ArticleCandidate]) -> tuple[Path, Path, Path]:
    return write_periodic_brief(root, date, candidates, cadence="daily")


def write_weekly_brief(
    root: str | Path,
    date: str,
    candidates: list[ArticleCandidate],
    comic_paths: list[str] | None = None,
    comic_notes: list[str] | None = None,
) -> tuple[Path, Path, Path]:
    return write_periodic_brief(
        root,
        date,
        candidates,
        cadence="weekly",
        comic_paths=comic_paths,
        comic_notes=comic_notes,
    )


def _register_pdf_font() -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
    ]
    for font_path in candidates:
        if font_path.exists():
            try:
                pdfmetrics.registerFont(TTFont("ThinkTankCJK", str(font_path)))
                return "ThinkTankCJK"
            except Exception:
                continue
    return "Helvetica"


def _resolve_markdown_image(src: str, base_dir: Path) -> Path:
    clean_src = src.split("#", 1)[0].split("?", 1)[0]
    image_path = Path(clean_src)
    if image_path.is_absolute():
        return image_path
    return base_dir / image_path


def _pdf_image_reader(image_path: Path, max_width_px: int = 1200, jpeg_quality: int = 82):
    from reportlab.lib.utils import ImageReader

    try:
        from PIL import Image
    except ImportError:
        return ImageReader(str(image_path))

    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")
            if image.width > max_width_px:
                target_height = round(image.height * max_width_px / image.width)
                resampling = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
                image = image.resize((max_width_px, target_height), resampling)
            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=jpeg_quality,
                optimize=True,
                progressive=True,
            )
            buffer.seek(0)
            return ImageReader(buffer)
    except Exception:
        return ImageReader(str(image_path))


def write_pdf_brief(path: str | Path, markdown_text: str, base_dir: str | Path | None = None) -> Path:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return Path(path)

    path = Path(path)
    base_dir_path = Path(base_dir) if base_dir is not None else Path.cwd()
    path.parent.mkdir(parents=True, exist_ok=True)
    font = _register_pdf_font()
    page_width, page_height = A4
    margin = 42
    y = page_height - margin
    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.setTitle(path.stem)

    def draw_line(text: str, size: int, leading: int) -> None:
        nonlocal y
        if y < margin + leading:
            pdf.showPage()
            y = page_height - margin
        pdf.setFont(font, size)
        pdf.drawString(margin, y, text)
        y -= leading

    def draw_image(src: str) -> None:
        nonlocal y
        image_path = _resolve_markdown_image(src, base_dir_path)
        if not image_path.exists():
            draw_line(f"[图片未找到] {src}", 9, 14)
            return
        try:
            image = _pdf_image_reader(image_path)
            image_width, image_height = image.getSize()
        except Exception:
            draw_line(f"[图片无法读取] {src}", 9, 14)
            return
        if image_width <= 0 or image_height <= 0:
            draw_line(f"[图片尺寸异常] {src}", 9, 14)
            return
        max_width = page_width - 2 * margin
        max_height = page_height * 0.42
        scale = min(max_width / image_width, max_height / image_height)
        draw_width = image_width * scale
        draw_height = image_height * scale
        if y < margin + draw_height:
            pdf.showPage()
            y = page_height - margin
        pdf.drawImage(image, margin, y - draw_height, width=draw_width, height=draw_height, mask="auto")
        y -= draw_height + 12

    for raw in markdown_text.splitlines():
        line = raw.strip()
        if not line:
            y -= 6
            continue
        image_match = IMAGE_MARKDOWN_RE.match(line)
        if image_match:
            draw_image(image_match.group(2))
        elif line.startswith("# "):
            draw_line(line[2:], 17, 24)
        elif line.startswith("## "):
            draw_line(line[3:], 13, 20)
        elif line.startswith("### "):
            draw_line(line[4:], 11, 17)
        else:
            text = line[2:] if line.startswith("- ") else line
            for part in wrap(text, width=54):
                draw_line(part, 9, 14)
    pdf.save()
    return path


def write_weekly_reader_pdf(path: str | Path, run_date: str, candidates: list[ArticleCandidate]) -> Path:
    try:
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
    except ImportError:
        return Path(path)
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        Image = ImageDraw = ImageFont = None

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    font = _register_pdf_font()
    page_width, page_height = A4
    margin = 42
    content_width = page_width - 2 * margin
    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.setTitle(f"国际科技智库周报（{run_date}）")

    colors = {
        "navy": HexColor("#1f5f8b"),
        "red": HexColor("#b84c3d"),
        "green": HexColor("#4f7d5a"),
        "ink": HexColor("#172026"),
        "muted": HexColor("#5f6b75"),
        "paper": HexColor("#fbfcfd"),
        "blue_bg": HexColor("#eaf1f6"),
        "red_bg": HexColor("#f8ebe7"),
        "green_bg": HexColor("#edf5ed"),
        "gold_bg": HexColor("#fff6e7"),
    }

    page_no = 0

    def footer() -> None:
        pdf.setFont(font, 8)
        pdf.setFillColor(colors["muted"])
        pdf.drawRightString(page_width - margin, 24, f"{run_date} | {page_no}")

    def new_page() -> None:
        nonlocal page_no
        if page_no:
            footer()
            pdf.showPage()
        page_no += 1
        pdf.setFillColor(colors["paper"])
        pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
        pdf.setFillColor(colors["navy"])
        pdf.rect(0, page_height - 10, page_width * 0.42, 10, fill=1, stroke=0)
        pdf.setFillColor(colors["red"])
        pdf.rect(page_width * 0.42, page_height - 10, page_width * 0.25, 10, fill=1, stroke=0)
        pdf.setFillColor(colors["green"])
        pdf.rect(page_width * 0.67, page_height - 10, page_width * 0.33, 10, fill=1, stroke=0)

    def wrap_pdf_text(text: str, max_width: float, size: int) -> list[str]:
        clean = _clean_text(text)
        if not clean:
            return []
        lines: list[str] = []
        current = ""
        for char in clean:
            if char == " " and not current:
                continue
            candidate = current + char
            if current and pdf.stringWidth(candidate, font, size) > max_width:
                lines.append(current.rstrip())
                current = char.lstrip()
            else:
                current = candidate
        if current:
            lines.append(current.rstrip())
        return lines

    def draw_wrapped(text: str, x: float, y: float, max_width: float, size: int, leading: int, color=None) -> float:
        pdf.setFont(font, size)
        pdf.setFillColor(color or colors["ink"])
        for part in wrap_pdf_text(text, max_width, size):
            pdf.drawString(x, y, part)
            y -= leading
        return y

    def draw_link_title(text: str, url: str, x: float, y: float, size: int, max_width: float) -> float:
        pdf.setFont(font, size)
        pdf.setFillColor(colors["navy"])
        top = y + size
        first_line_bottom = y - 3
        for line_index, part in enumerate(wrap_pdf_text(text, max_width, size)):
            pdf.drawString(x, y, part)
            if line_index == 0 and url:
                link_width = min(content_width, max(80, pdf.stringWidth(part, font, size)))
                pdf.linkURL(url, (x, first_line_bottom, x + link_width, top), relative=0)
            y -= size + 5
        return y

    def draw_card(
        x: float,
        y: float,
        w: float,
        h: float,
        fill,
        stroke,
        title: str,
        body: str,
        body_size: int = 9,
        leading: int = 13,
    ) -> None:
        pdf.setFillColor(fill)
        pdf.setStrokeColor(stroke)
        pdf.roundRect(x, y - h, w, h, 8, fill=1, stroke=1)
        pdf.setFillColor(stroke)
        pdf.setFont(font, 12)
        pdf.drawString(x + 12, y - 20, title)
        max_width = w - 24
        max_lines = max(1, int((h - 52) / leading))
        size = body_size
        line_height = leading
        lines = wrap_pdf_text(body, max_width, size)
        while len(lines) > max_lines and size > 8:
            size -= 1
            line_height = max(11, line_height - 1)
            max_lines = max(1, int((h - 52) / line_height))
            lines = wrap_pdf_text(body, max_width, size)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            if lines:
                suffix = "..."
                while lines[-1] and pdf.stringWidth(lines[-1] + suffix, font, size) > max_width:
                    lines[-1] = lines[-1][:-1]
                lines[-1] = lines[-1].rstrip() + suffix
        pdf.setFont(font, size)
        pdf.setFillColor(colors["ink"])
        body_y = y - 42
        for part in lines:
            pdf.drawString(x + 12, body_y, part)
            body_y -= line_height

    priority_items = weekly_priority_items(candidates)
    topic_pages, _ = weekly_pdf_page_plan(candidates)
    chapter_groups: dict[str, list[ArticleCandidate]] = {}
    for item in priority_items:
        chapter_groups.setdefault(weekly_chapter_name(item), []).append(item)

    def chapter_note(chapter: str) -> str:
        if chapter == "涉华科技竞争与上海参考":
            return "优先观察技术管制、供应链调整与上海产业政策的外部压力。"
        if chapter == "AI、数字基础设施与技术治理":
            return "重点看算力、模型、数据和治理规则如何影响创新扩散速度。"
        if chapter == "产业链、制造与能源基础设施":
            return "关注能源、制造、关键材料和产业链韧性之间的联动。"
        if chapter == "科研体系、人才与创新政策":
            return "关注科研组织、人才供给和政策工具对长期创新能力的支撑。"
        return "作为补充信号，用于识别跨主题创新支撑线索。"

    def draw_map_card(x: float, y: float, w: float, h: float, title: str, body: str, fill, stroke) -> None:
        pdf.setFillColor(fill)
        pdf.setStrokeColor(stroke)
        pdf.roundRect(x, y - h, w, h, 8, fill=1, stroke=1)
        title_y = draw_wrapped(title, x + 12, y - 22, w - 24, 12, 16, stroke)
        draw_wrapped(body, x + 12, title_y - 8, w - 24, 10, 15, colors["ink"])

    def _pil_font(size: int):
        if ImageFont is None:
            return None
        candidates = [
            Path(r"C:\Windows\Fonts\simhei.ttf"),
            Path(r"C:\Windows\Fonts\msyh.ttc"),
            Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        ]
        for font_path in candidates:
            if font_path.exists():
                try:
                    return ImageFont.truetype(str(font_path), size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _generated_comic_path(index: int) -> Path | None:
        return weekly_topic_comic_file(run_date, index)

    def _missing_comic_reader(index: int, candidate: ArticleCandidate):
        if Image is None or ImageDraw is None or ImageFont is None:
            return None
        width_px = 1500
        height_px = 410
        image = Image.new("RGB", (width_px, height_px), "#fff6e7")
        draw = ImageDraw.Draw(image)
        title_font = _pil_font(42)
        body_font = _pil_font(30)
        small_font = _pil_font(24)
        draw.rounded_rectangle((18, 18, width_px - 18, height_px - 18), radius=28, fill="#fff6e7", outline="#b84c3d", width=5)
        draw.text((62, 70), f"主题 {index:02d}｜Codex 漫画待生成", font=title_font, fill="#1f5f8b")
        title = candidate.chinese_title or candidate.title
        draw.text((62, 150), _short_text(title, 52), font=body_font, fill="#172026")
        draw.text((62, 222), "本页禁止回退为程序化示意图；生成真实漫画 PNG 后自动嵌入周报。", font=small_font, fill="#5f6b75")
        draw.text((62, 276), "目标样式：单篇报告观点科普漫画，呈现核心观点、视觉证据和主要影响。", font=small_font, fill="#5f6b75")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return ImageReader(buffer)

    def draw_comic_illustration(index: int, candidate: ArticleCandidate, x: float, y: float, w: float, h: float) -> None:
        comic_path = _generated_comic_path(index)
        if comic_path is not None:
            pdf.drawImage(_pdf_image_reader(comic_path), x, y - h, width=w, height=h, mask="auto")
            return
        missing = _missing_comic_reader(index, candidate)
        if missing is not None:
            pdf.drawImage(missing, x, y - h, width=w, height=h, mask="auto")
            return
        pdf.setFillColor(colors["gold_bg"])
        pdf.setStrokeColor(colors["red"])
        pdf.roundRect(x, y - h, w, h, 8, fill=1, stroke=1)
        pdf.setFillColor(colors["navy"])
        pdf.setFont(font, 13)
        pdf.drawString(x + 16, y - 34, f"主题 {index:02d}｜Codex 漫画待生成")

    new_page()
    pdf.setFillColor(colors["navy"])
    pdf.setFont(font, 24)
    pdf.drawString(margin, page_height - 96, "国际科技智库周报")
    pdf.setFont(font, 13)
    pdf.setFillColor(colors["muted"])
    pdf.drawString(margin, page_height - 124, f"{run_date} | 阅读版")
    situation = weekly_situation_summary(candidates)
    situation_lines = wrap_pdf_text(situation, content_width - 32, 10)
    situation_box_top = page_height - 140
    situation_box_h = max(126, 50 + len(situation_lines) * 15)
    pdf.setFillColor(colors["blue_bg"])
    pdf.roundRect(margin, situation_box_top - situation_box_h, content_width, situation_box_h, 8, fill=1, stroke=0)
    pdf.setFillColor(colors["ink"])
    pdf.setFillColor(colors["navy"])
    pdf.setFont(font, 13)
    pdf.drawString(margin + 16, situation_box_top - 24, "本周主要态势")
    draw_wrapped(
        situation,
        margin + 16,
        situation_box_top - 50,
        content_width - 32,
        10,
        15,
        colors["ink"],
    )
    y = situation_box_top - situation_box_h - 34
    pdf.setFillColor(colors["navy"])
    pdf.setFont(font, 15)
    pdf.drawString(margin, y, "阅读地图")
    map_items = list(chapter_groups.items())[:4]
    if map_items:
        card_w = (content_width - 18) / 2
        card_h = 132
        fills = [colors["green_bg"], colors["blue_bg"], colors["gold_bg"], colors["red_bg"]]
        strokes = [colors["green"], colors["navy"], colors["red"], colors["red"]]
        top = y - 30
        for card_index, (chapter, items) in enumerate(map_items):
            col = card_index % 2
            row = card_index // 2
            x = margin + col * (card_w + 18)
            yy = top - row * (card_h + 18)
            draw_map_card(
                x,
                yy,
                card_w,
                card_h,
                chapter,
                f"{len(items)} 条。{chapter_note(chapter)}",
                fills[card_index],
                strokes[card_index],
            )
    else:
        draw_map_card(
            margin,
            y - 30,
            content_width,
            108,
            "本周无 P0/P1 重点条目",
            "资料索引仍保留全部新增条目，供后续回看。",
            colors["green_bg"],
            colors["green"],
        )

    def draw_toc_pages() -> None:
        new_page()
        y = page_height - 52
        pdf.setFillColor(colors["navy"])
        pdf.setFont(font, 18)
        pdf.drawString(margin, y, "目录")
        y -= 28
        pdf.setFillColor(colors["muted"])
        pdf.setFont(font, 9)
        pdf.drawString(margin, y, "点击标题跳转至对应主题页")
        y -= 22
        for index, item in enumerate(priority_items, 1):
            lines = _weekly_pdf_toc_entry_lines(index, item, topic_pages[item.url])
            needed_height = len(lines) * 13 + 8
            if y - needed_height < 64:
                new_page()
                y = page_height - 52
                pdf.setFillColor(colors["navy"])
                pdf.setFont(font, 18)
                pdf.drawString(margin, y, "目录（续）")
                y -= 32
            entry_top = y + 4
            for line_index, line in enumerate(lines):
                pdf.setFont(font, 9)
                pdf.setFillColor(colors["navy"] if line_index == 0 else colors["ink"])
                pdf.drawString(margin + (0 if line_index == 0 else 18), y, line)
                y -= 13
            pdf.linkRect(
                "",
                _pdf_topic_key(index),
                (margin, y - 1, page_width - margin, entry_top + 6),
                relative=0,
                thickness=0,
            )
            y -= 8

    draw_toc_pages()

    for index, item in enumerate(priority_items, 1):
        sections = _weekly_summary_sections(item)
        chapter = weekly_chapter_name(item)
        new_page()
        pdf.bookmarkPage(_pdf_topic_key(index))
        pdf.addOutlineEntry(f"主题 {index:02d} {item.chinese_title or item.title}", _pdf_topic_key(index), level=0, closed=True)
        pdf.setFillColor(colors["green"])
        pdf.setFont(font, 11)
        pdf.drawString(margin, page_height - 46, f"主题 {index:02d} / {len(priority_items):02d} | {chapter}")
        y = draw_link_title(
            f"[{item.priority}] {item.chinese_title or item.title}",
            item.url,
            margin,
            page_height - 76,
            16,
            content_width,
        )
        y = draw_wrapped(
            f"机构：{item.institution_name} | 主题：{', '.join(item.topic_tags) or '待分类'}",
            margin,
            y - 3,
            content_width,
            9,
            13,
            colors["muted"],
        )
        y -= 14
        illustration_h = 190
        draw_comic_illustration(index, item, margin, y, content_width, illustration_h)
        y -= illustration_h + 14
        draw_card(
            margin,
            y,
            content_width,
            220,
            colors["blue_bg"],
            colors["navy"],
            "核心观点与论述",
            _short_text(_weekly_pdf_main_argument(item, sections), 980),
            body_size=10,
            leading=15,
        )
        y -= 236
        draw_card(
            margin,
            y,
            content_width,
            154,
            colors["green_bg"],
            colors["green"],
            "政策含义与参考",
            _short_text(_weekly_pdf_implication(sections), 620),
            body_size=10,
            leading=14,
        )

    if not priority_items:
        new_page()
        pdf.setFillColor(colors["navy"])
        pdf.setFont(font, 15)
        pdf.drawString(margin, page_height - 72, "本周无 P0/P1 重点条目")

    footer()
    pdf.save()
    return path
