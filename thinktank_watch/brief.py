from __future__ import annotations

import csv
from collections import Counter
from html import escape
from pathlib import Path
from textwrap import wrap

from .models import ArticleCandidate
from .kb import INDEX_RELATIVE
from .restore import parse_archive_markdown


MAX_EXPANDED_PRIORITY_ITEMS = 12
MAX_INDEX_ITEMS = 100
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
INNOVATION_SUPPORT_TAGS = {"科技创新", "先进制造", "数字经济", "半导体", "科技人才"}


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
                -pair[1].score,
                -published_date_sort_value(pair[1].published_date),
                pair[0],
            ),
        )
    ]


def select_innovation_support_items(candidates: list[ArticleCandidate], limit: int = 12) -> list[ArticleCandidate]:
    support_candidates = [
        item for item in candidates if INNOVATION_SUPPORT_TAGS & set(item.topic_tags) and "AI治理" not in item.topic_tags
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

    topic_order = ["科技创新", "先进制造", "数字经济", "半导体", "科技人才"]
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


def render_daily_brief_markdown(date: str, candidates: list[ArticleCandidate]) -> str:
    ordered_candidates = sort_brief_candidates(candidates)
    priority_items = [item for item in ordered_candidates if item.priority in {"P0", "P1"}]
    expanded_priority_items = priority_items[:MAX_EXPANDED_PRIORITY_ITEMS]
    overflow_priority_items = priority_items[MAX_EXPANDED_PRIORITY_ITEMS:]
    index_items = [*overflow_priority_items, *[item for item in ordered_candidates if item.priority not in {"P0", "P1"}]]
    topic_counter: Counter[str] = Counter(tag for item in candidates for tag in item.topic_tags)

    lines = [
        f"# 国际科技智库动态简报（{date}）",
        "",
        "## 新增概览",
        "",
        f"- 新增条目：{len(candidates)}",
        f"- P0/P1重点：{len(priority_items)}",
        f"- 涉及机构：{len({item.institution_slug for item in candidates})}",
        f"- 高频主题：{', '.join(name for name, _ in topic_counter.most_common(6)) or '无'}",
        "",
        "## P0/P1重点",
        "",
    ]
    if not priority_items:
        lines.extend(["本日无P0/P1新增重点。", ""])
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
                    f"- 摘要：{item.chinese_summary or item.summary or '待补充'}",
                    "",
                ]
            )

    lines.extend(["## 科技创新与AI治理", ""])
    tech_items = [item for item in ordered_candidates if {"AI治理", "科技创新", "科技治理"} & set(item.topic_tags)]
    if tech_items:
        for item in tech_items[:8]:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}")
    else:
        lines.append("本日未检出科技创新与AI治理强相关条目。")

    lines.extend(["", "## 广义科技创新支撑", ""])
    support_items = select_innovation_support_items(ordered_candidates)
    if support_items:
        for item in support_items[:12]:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}")
    else:
        lines.append("本日未检出区域创新、先进制造、数字基础设施、半导体或科技人才相关条目。")

    lines.extend(["", "## 涉华/涉沪判断", ""])
    china_items = [item for item in ordered_candidates if "中国与上海相关" in item.topic_tags]
    if china_items:
        for item in china_items[:8]:
            lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}｜{item.url}")
    else:
        lines.append("本日未检出中国/上海强相关条目。")

    lines.extend(["", "## 新增索引", ""])
    for item in index_items[:MAX_INDEX_ITEMS]:
        lines.append(f"- [{item.priority}] {item.institution_name}｜{item.chinese_title or item.title}｜{item.url}")
    omitted = len(index_items) - MAX_INDEX_ITEMS
    if omitted > 0:
        lines.append(f"- 其余 {omitted} 条已写入私有归档和知识库索引。")

    lines.extend(["", "## 后续推进", "", "- 对P0/P1条目补充中文研判、页码级证据和可复用表述。"])
    return "\n".join(lines) + "\n"


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


def markdown_to_html(markdown_text: str, title: str) -> str:
    body_lines: list[str] = []
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            body_lines.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body_lines.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("### "):
            body_lines.append(f"<h3>{escape(line[4:])}</h3>")
        elif line.startswith("- "):
            body_lines.append(f"<p class=\"bullet\">{escape(line)}</p>")
        elif line.strip():
            body_lines.append(f"<p>{escape(line)}</p>")
        else:
            body_lines.append("")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
body {{ font-family: "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif; margin: 42px; color: #172026; line-height: 1.58; }}
h1 {{ font-size: 26px; border-bottom: 2px solid #1f5f8b; padding-bottom: 12px; }}
h2 {{ font-size: 19px; margin-top: 28px; color: #1f5f8b; }}
h3 {{ font-size: 16px; margin-top: 18px; }}
p {{ font-size: 12px; margin: 6px 0; }}
.bullet {{ padding-left: 12px; }}
</style>
</head>
<body>
{chr(10).join(body_lines)}
</body>
</html>
"""


def write_daily_brief(root: str | Path, date: str, candidates: list[ArticleCandidate]) -> tuple[Path, Path, Path]:
    year = date[:4]
    directory = Path(root) / "daily" / year
    directory.mkdir(parents=True, exist_ok=True)
    markdown_path = directory / f"{date}_国际科技智库动态简报.md"
    html_path = directory / f"{date}_国际科技智库动态简报.html"
    markdown = render_daily_brief_markdown(date, candidates)
    markdown_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(markdown_to_html(markdown, f"国际科技智库动态简报（{date}）"), encoding="utf-8")
    pdf_path = write_pdf_brief(directory / f"{date}_国际科技智库动态简报.pdf", markdown)
    return markdown_path, html_path, pdf_path


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


def write_pdf_brief(path: str | Path, markdown_text: str) -> Path:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return Path(path)

    path = Path(path)
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

    for raw in markdown_text.splitlines():
        line = raw.strip()
        if not line:
            y -= 6
            continue
        if line.startswith("# "):
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
