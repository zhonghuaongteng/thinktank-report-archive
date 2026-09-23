"""Render authored report selections without fetching resources or accepting raw HTML.

Supported Markdown: headings, paragraphs, lists, blockquotes, pipe tables,
bold/italic text, source links, and standalone local raster-image references.
Chart paths are relative to the current project root. Captions, attribution,
licence and original page references remain explicit authored text.
"""
from __future__ import annotations

import base64
from html import escape
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from .models import ArticleCandidate


_IMAGE = re.compile(r'^!\[([^\]]*)\]\(<?([^>\n]+?)>?\)\s*$')
_LIST = re.compile(r"^\s*(?:(\d+)[.)]|([-+*]))\s+(.+)$")
_LINK = re.compile(r"\[([^\]]+)\]\(([^\s)]+)\)|\[([^\]]+)\]\[([^\]]*)\]")


def validated_highlights_markdown(candidate: ArticleCandidate) -> str:
    """Selections are explicit editorial input, never populated from fetched text.

    A source's metadata-only access does not restrict independently authored
    analysis. Verbatim excerpts or translations need a separately recorded
    source-licence/permission verification; do not infer it from source access
    or institution. Explicit source licences or existing user authorization
    can provide that recorded basis without repeated approval requests.
    """
    text = candidate.highlights_markdown.strip()
    if not text:
        return ""
    if candidate.highlights_usage not in {"editorial", "licensed_excerpt"}:
        raise ValueError("highlights_usage must be editorial or licensed_excerpt; source excerpts and translations require verified permission")
    if candidate.highlights_usage == "licensed_excerpt" and not (
        candidate.highlights_permission_verified and candidate.highlights_permission_note.strip()
    ):
        raise ValueError("Licensed excerpts or translations require source-licence/permission verification and its recorded basis")
    return text


def _inline(text: str, references: dict[str, str] | None = None) -> str:
    def formatted(value: str) -> str:
        value = escape(value)
        value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
        return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)

    parts: list[str] = []
    cursor = 0
    for match in _LINK.finditer(text):
        parts.append(formatted(text[cursor:match.start()]))
        label, target, reference_label, reference_id = match.groups()
        if reference_label is not None:
            label = reference_label
            target = (references or {}).get(" ".join((reference_id or label).lower().split()), "")
        parsed = urlsplit(target)
        if parsed.scheme.lower() in {"http", "https"} and parsed.netloc:
            parts.append(f'<a href="{escape(target, quote=True)}">{formatted(label)}</a>')
        else:
            parts.append(formatted(match.group(0)))
        cursor = match.end()
    parts.append(formatted(text[cursor:]))
    return "".join(parts)


def _local_chart_uri(target: str, root: Path) -> str:
    target = unquote(target.strip())
    if urlsplit(target).scheme or target.startswith(("//", "\\\\")):
        raise ValueError("Selected charts must use project-relative local image paths")
    resolved = (root / target).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Selected chart path escapes the project root")
    if resolved.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        raise ValueError("Selected charts must be local raster images")
    if not resolved.is_file():
        raise ValueError(f"Selected chart is missing: {target}")
    media_type = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}[resolved.suffix.lower()]
    encoded = base64.b64encode(resolved.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def _cells(line: str) -> list[str]:
    return [cell.strip().replace(r"\|", "|") for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _table_separator(line: str) -> bool:
    return "|" in line and all(re.fullmatch(r":?-{3,}:?", value) for value in _cells(line))


def _selection_lines(markdown: str) -> tuple[list[str], dict[str, str]]:
    references: dict[str, str] = {}
    lines: list[str] = []
    in_code = False
    for line in markdown.strip().splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        definition = re.match(r'^\s*\[([^\]]+)\]:\s*<?([^\s>]+)>?(?:\s+["\'].*["\'])?\s*$', line)
        if definition and not in_code:
            references[" ".join(definition.group(1).lower().split())] = definition.group(2)
        else:
            lines.append(line)
    return lines, references


def highlights_headings(markdown: str) -> list[str]:
    lines, _ = _selection_lines(markdown)
    headings: list[str] = []
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
        heading = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if heading and not in_code:
            headings.append(heading.group(1))
    return headings


def render_highlights_markdown(markdown: str, project_root: str | Path | None = None, heading_id_prefix: str = "") -> str:
    """Return safe HTML for an authored selection; do not summarize or truncate it."""
    root = Path(project_root or Path.cwd()).resolve()
    lines, references = _selection_lines(markdown)
    inline = lambda value: _inline(value, references)
    output: list[str] = []
    index = 0
    heading_index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("```"):
            end = index + 1
            while end < len(lines) and not lines[end].strip().startswith("```"):
                end += 1
            output.append('<pre><code>' + escape("\n".join(lines[index + 1:end])) + '</code></pre>')
            index = min(end + 1, len(lines))
            continue
        image = _IMAGE.fullmatch(line)
        if image:
            caption, target = image.groups()
            uri = _local_chart_uri(target, root)
            output.append(
                f'<figure class="selected-chart"><img src="{escape(uri, quote=True)}" alt="{escape(caption, quote=True)}">'
                + (f'<figcaption>{inline(caption)}</figcaption>' if caption else "") + '</figure>'
            )
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = min(len(heading.group(1)) + 3, 6)
            heading_index += 1
            anchor = f' id="{escape(heading_id_prefix, quote=True)}-{heading_index}"' if heading_id_prefix else ""
            output.append(f'<h{level}{anchor}>{inline(heading.group(2))}</h{level}>')
            index += 1
            continue
        if index + 1 < len(lines) and "|" in line and _table_separator(lines[index + 1]):
            headers = _cells(line)
            output.append('<table><thead><tr>' + ''.join(f'<th>{inline(value)}</th>' for value in headers) + '</tr></thead><tbody>')
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                values = _cells(lines[index])
                output.append('<tr>' + ''.join(f'<td>{inline(value)}</td>' for value in values) + '</tr>')
                index += 1
            output.append('</tbody></table>')
            continue
        listed = _LIST.match(line)
        if listed:
            tag = "ol" if listed.group(1) else "ul"
            start = f' start="{int(listed.group(1))}"' if listed.group(1) else ""
            output.append(f'<{tag}{start}>')
            while index < len(lines):
                item = _LIST.match(lines[index])
                if not item or ("ol" if item.group(1) else "ul") != tag:
                    break
                output.append(f'<li>{inline(item.group(3))}</li>')
                index += 1
            output.append(f'</{tag}>')
            continue
        quote = line.startswith("> ")
        paragraph = [line[2:] if quote else line]
        index += 1
        while index < len(lines) and lines[index].strip():
            next_line = lines[index].strip()
            if bool(next_line.startswith("> ")) != quote or re.match(r"^(?:#{1,6}\s|```|!\[)", next_line) or _LIST.match(next_line):
                break
            if index + 1 < len(lines) and _table_separator(lines[index + 1]):
                break
            paragraph.append(next_line[2:] if quote else next_line)
            index += 1
        tag = "blockquote" if quote else "p"
        output.append(f'<{tag}>{inline(" ".join(paragraph))}</{tag}>')
    return "\n".join(output)
