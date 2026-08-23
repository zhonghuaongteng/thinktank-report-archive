from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


INSTITUTION_LABELS = {
    "eu-jrc": "European Commission Joint Research Centre (JRC)",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _queue_count(path: Path) -> int:
    return len(read_csv(path)) if path.exists() else 0


def _has_local_asset(row: dict[str, str]) -> bool:
    return bool(row.get("本地原始资产路径", "").strip() or row.get("本地路径", "").strip())


def _china_counts(research_root: Path) -> tuple[int, int, int]:
    result_path = research_root / "71_覆盖缺口结果.md"
    if not result_path.exists():
        return 0, 0, 0
    content = result_path.read_text(encoding="utf-8")
    match = re.search(r"中国关联目录材料：(\d+)份；已有本地原文(\d+)份、可检索文本(\d+)份", content)
    return tuple(map(int, match.groups())) if match else (0, 0, 0)


def build_progress(research_root: Path) -> dict[str, object]:
    catalog = read_csv(research_root / "05_报告总目录.csv")
    institution_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"catalog": 0, "local_assets": 0})
    for row in catalog:
        institution_id = row.get("机构ID", "")
        institution = row.get("机构英文名") or INSTITUTION_LABELS.get(institution_id) or institution_id or "未标明机构"
        institution_stats[institution]["catalog"] += 1
        if _has_local_asset(row):
            institution_stats[institution]["local_assets"] += 1

    institutions = [
        {
            "institution": institution,
            "catalog": values["catalog"],
            "local_assets": values["local_assets"],
            "light_only": values["catalog"] - values["local_assets"],
        }
        for institution, values in institution_stats.items()
    ]
    institutions.sort(key=lambda row: (-row["catalog"], row["institution"]))
    local_assets = sum(1 for row in catalog if _has_local_asset(row))
    china_catalog, china_assets, china_texts = _china_counts(research_root)
    return {
        "catalog_total": len(catalog),
        "local_assets": local_assets,
        "light_only": len(catalog) - local_assets,
        "explicit_failures": sum(1 for row in catalog if row.get("原始资产状态", "").strip() == "获取失败"),
        "partial_assets": sum(
            1
            for row in catalog
            if _has_local_asset(row)
            and row.get("原始资产状态", "") in {"官方发布页摘要已保存", "官方仓储概要PDF代理文本已保存"}
        ),
        "fulltext_queue": _queue_count(research_root / "70_定点补源优先队列.csv"),
        "catalog_queue": _queue_count(research_root / "72_轻量目录扩展优先队列.csv"),
        "china_catalog": china_catalog,
        "china_assets": china_assets,
        "china_texts": china_texts,
        "institutions": institutions,
    }


def render_markdown(progress: dict[str, object], generated_at: str) -> str:
    total = int(progress["catalog_total"])
    local = int(progress["local_assets"])
    density = local / total * 100 if total else 0.0
    true_queue = int(progress["fulltext_queue"]) + int(progress["catalog_queue"])
    lines = [
        "# 国际科技智库本地资料库实时进度看板",
        "",
        f"- 生成时间：{generated_at}（Asia/Shanghai）",
        f"- 轻量总目录：{total}条。",
        f"- 已有本地原始资产或官方网页转换资产：{local}条。",
        f"- 仅目录与官方入口：{int(progress['light_only'])}条；按既定分层规则保留，不计作机械下载欠账。",
        f"- 资产密度：{density:.2f}%；该指标只反映本地落盘比例，不等同于任务完成率。",
        f"- 真实待补队列：{true_queue}；其中定点全文{int(progress['fulltext_queue'])}、轻量目录扩展{int(progress['catalog_queue'])}。",
        f"- 明确获取失败：{int(progress['explicit_failures'])}条。",
        f"- 仅摘要或概要资产：{int(progress.get('partial_assets', 0))}条；具备本地检索入口，完整全文仍按具体项目证据缺口触发。",
    ]
    china_catalog = int(progress.get("china_catalog", 0))
    if china_catalog:
        lines.append(
            f"- 中国关联目录材料：{china_catalog}条；已有本地原文{int(progress['china_assets'])}条、可检索文本{int(progress['china_texts'])}条。"
        )
    lines.extend(
        [
            "",
            "## 机构存量",
            "",
            "| 机构 | 目录 | 本地资产 | 轻量保留 |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in progress["institutions"]:
        lines.append(f"| {row['institution']} | {row['catalog']} | {row['local_assets']} | {row['light_only']} |")
    lines.extend(
        [
            "",
            "## 口径",
            "",
            "目录记录用于观察机构关注方向和议题迁移；全文只在能够补充科学体系、研发投入、科研组织、技术路线、成果转化、国际科研合作或中国比较机制时保存。安全、供应链与治理题名不单独触发全文。",
            "",
        ]
    )
    return "\n".join(lines)


def write_institution_csv(path: Path, institutions: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["institution", "catalog", "local_assets", "light_only"])
        writer.writeheader()
        writer.writerows(institutions)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    progress = build_progress(args.research)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    (args.research / "210_本地资料库实时进度看板.md").write_text(
        render_markdown(progress, timestamp), encoding="utf-8", newline="\n"
    )
    write_institution_csv(args.research / "211_机构采集进度.csv", progress["institutions"])
    print(
        f"catalog={progress['catalog_total']} local_assets={progress['local_assets']} "
        f"light_only={progress['light_only']} failures={progress['explicit_failures']} "
        f"fulltext_queue={progress['fulltext_queue']} catalog_queue={progress['catalog_queue']}"
    )


if __name__ == "__main__":
    main()
