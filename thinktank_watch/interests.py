"""Personal research interests aid discovery, never determine report priority."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml

from .models import ArticleCandidate


@dataclass(frozen=True)
class ResearchInterest:
    name: str
    level: str
    aliases: tuple[str, ...]


def load_research_interests(path: str | Path) -> list[ResearchInterest]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8-sig")) or {}
    return [ResearchInterest(item["name"], item["level"], tuple(item["aliases"]))
            for item in data.get("interests", [])]


def match_research_interests(
    candidate: ArticleCandidate, interests: list[ResearchInterest],
) -> list[tuple[ResearchInterest, list[str]]]:
    # Use discovery text, not bibliographies or inferred topic tags as evidence.
    text = "\n".join((candidate.title, candidate.chinese_title,
                      candidate.summary, candidate.chinese_summary)).casefold()
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", text)
    matches = []
    for interest in interests:
        hits = []
        for alias in interest.aliases:
            needle = alias.casefold().strip()
            if not needle:
                continue
            phrase = r"[\s-]+".join(re.escape(part) for part in re.split(r"[\s-]+", needle))
            found = (needle in text if re.search(r"[\u4e00-\u9fff]", needle)
                     else re.search(rf"(?<![a-z0-9]){phrase}(?![a-z0-9])", text))
            if found:
                hits.append(alias)
        if hits:
            matches.append((interest, hits))
    return matches
