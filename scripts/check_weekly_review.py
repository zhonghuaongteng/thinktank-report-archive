"""Read-only closure check for weekly editorial decisions; not a content-quality scorer."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

DECISIONS = {"重点", "简讯", "排除", "获取受阻"}
FULLTEXT = {"已核读", "不需全文", "获取受阻", "未完成"}
FIELDS = {"URL", "最终处置", "取舍理由", "全文状态", "正文定位", "全文获取记录", "写作复核"}
EMPTY_REASONS = {"低分", "未命中", "全文待证", "待证", "待核", "本期未收录", "P3", "0分"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate(queue: list[dict[str, str]], rows: list[dict[str, str]], fields: list[str]) -> dict:
    errors: list[dict[str, str]] = []

    def fail(url: str, message: str) -> None:
        errors.append({"url": url, "error": message})

    missing_fields = sorted(FIELDS - set(fields))
    if missing_fields:
        fail("", "缺少复核列：" + "、".join(missing_fields))
    expected = {(row.get("URL") or "").strip() for row in queue}
    if not queue or "" in expected:
        fail("", "原始队列为空或存在空URL，须核实发现阶段")
    seen: set[str] = set()
    counts = dict.fromkeys(sorted(DECISIONS), 0)
    for row in rows:
        url = (row.get("URL") or "").strip()
        if not url:
            fail("", "最终复核存在空URL")
            continue
        if url in seen:
            fail(url, "最终复核URL重复")
        seen.add(url)
        decision = (row.get("最终处置") or "").strip()
        reason = (row.get("取舍理由") or "").strip()
        status = (row.get("全文状态") or "").strip()
        locator = (row.get("正文定位") or "").strip()
        attempts = (row.get("全文获取记录") or "").strip()
        if decision not in DECISIONS:
            fail(url, "没有明确最终处置")
        else:
            counts[decision] += 1
        if not reason or reason in EMPTY_REASONS:
            fail(url, "缺少具体取舍理由")
        if status not in FULLTEXT or status == "未完成":
            fail(url, "原文复核尚未完成")
        unresolved = reason + " " + (row.get("复核状态") or "")
        if decision != "获取受阻" and status != "已核读" and any(
            text in unresolved for text in ("全文待证", "全文待核", "全文未读", "全文尚未核读")
        ):
            fail(url, "仍以全文未完成作为最终处置依据")
        if decision == "重点" and status != "已核读":
            fail(url, "重点材料尚未核读原文")
        if decision in {"重点", "简讯"}:
            if not locator:
                fail(url, "收录材料缺少实际正文或摘要定位")
            if (row.get("写作复核") or "").strip() != "通过":
                fail(url, "收录材料尚未完成写作复核")
        if decision == "获取受阻" or status == "获取受阻":
            if decision != "获取受阻" or status != "获取受阻":
                fail(url, "获取受阻状态与最终处置不一致")
            if not attempts or not any(x in attempts for x in ("https://", "http://")):
                fail(url, "受阻条目缺少含URL的真实获取记录")
    for url in sorted(expected - seen - {""}):
        fail(url, "原始候选没有最终复核记录")
    return {"ok": not errors, "queue_count": len(queue), "review_count": len(rows),
            "supplement_count": len(seen - expected), "decisions": counts,
            "errors": errors, "scope": "只核对记录闭合；不替代日期、事实、内容与版面人工核验"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Never allow the result to overwrite an input ledger.
    if args.output.resolve() in {args.queue.resolve(), args.review.resolve()}:
        parser.error("输出路径不能覆盖输入复核表")
    queue_fields, queue = read_csv(args.queue)
    fields, rows = read_csv(args.review)
    result = validate(queue, rows, fields)
    if "URL" not in queue_fields:
        result["ok"] = False
        result["errors"].append({"url": "", "error": "原始候选表缺少URL列"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"weekly_review_check={'ok' if result['ok'] else 'failed'} errors={len(result['errors'])}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
