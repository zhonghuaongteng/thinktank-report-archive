from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import Institution, PriorityRules, TopicRule


def _read_yaml(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        return yaml.safe_load(handle) or {}


def load_institutions(config_dir: str | Path) -> list[Institution]:
    root = Path(config_dir)
    institutions: list[Institution] = []
    for path in sorted(root.glob("*.yaml")):
        data = _read_yaml(path)
        institutions.append(
            Institution(
                slug=data["slug"],
                name=data["name"],
                chinese_name=data.get("chinese_name", data["name"]),
                country_region=data.get("country_region", ""),
                institution_type=data.get("institution_type", "think_tank"),
                priority=data.get("priority", "P1"),
                batch=int(data.get("batch", 3)),
                homepage=data["homepage"],
                parser=data.get("parser", "generic"),
                copyright_boundary=data.get("copyright_boundary", "private_archive"),
                feeds=list(data.get("feeds") or []),
                list_pages=list(data.get("list_pages") or []),
                topic_pages=list(data.get("topic_pages") or []),
                sitemap_urls=list(data.get("sitemap_urls") or []),
                sitemap_include_keywords=list(data.get("sitemap_include_keywords") or []),
                notes=data.get("notes", ""),
            )
        )
    return institutions


def load_topics(path: str | Path) -> list[TopicRule]:
    data = _read_yaml(path)
    rules: list[TopicRule] = []
    for item in data.get("topics", []):
        rules.append(
            TopicRule(
                name=item["name"],
                weight=int(item.get("weight", 1)),
                keywords=list(item.get("keywords") or []),
            )
        )
    return rules


def load_priority_rules(path: str | Path) -> PriorityRules:
    data = _read_yaml(path)
    return PriorityRules(
        p0_threshold=int(data.get("p0_threshold", 9)),
        p1_threshold=int(data.get("p1_threshold", 5)),
        p2_threshold=int(data.get("p2_threshold", 2)),
        report_bonus=int(data.get("report_bonus", 1)),
        source_priority_bonus=dict(data.get("source_priority_bonus") or {}),
        translation_by_priority=dict(data.get("translation_by_priority") or {}),
    )
