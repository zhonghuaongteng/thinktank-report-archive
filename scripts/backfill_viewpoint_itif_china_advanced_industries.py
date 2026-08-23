from __future__ import annotations

import argparse
import hashlib
from datetime import date
from pathlib import Path

try:
    from scripts.backfill_viewpoint_china_research_system_nodes import clean_text, make_slice, read_csv, write_csv
    from scripts.extend_viewpoint_itif_selected_fulltexts import fetch_markdown
except ModuleNotFoundError:
    from backfill_viewpoint_china_research_system_nodes import clean_text, make_slice, read_csv, write_csv
    from extend_viewpoint_itif_selected_fulltexts import fetch_markdown


SERIES_ROLE = "ITIF中国先进产业技术创新能力跨行业精选全文"

SELECTED_ITEMS = (
    ("C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-THE-ROBOTICS-INDUSTRY", "2024-03-11", "How Innovative Is China in the Robotics Industry?", "机器人", "制造能力、企业研发、专利与机器人产业创新转化"),
    ("C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-THE-ELECTRIC-VEHICLE-AND-BATTERY-INDUSTRIES", "2024-07-29", "How Innovative Is China in the Electric Vehicle and Battery Industries?", "电动车与电池", "电池技术、整车工程、规模化制造与产业创新生态"),
    ("C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-BIOTECHNOLOGY", "2024-07-30", "How Innovative Is China in Biotechnology?", "生物技术", "生命科学研究、专利、企业研发与生物技术成果转化"),
    ("C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-SEMICONDUCTORS", "2024-08-19", "How Innovative Is China in Semiconductors?", "半导体", "芯片设计制造、研发强度、专利与技术能力比较"),
    ("C-ITIF-2024-HOW-INNOVATIVE-IS-CHINA-IN-QUANTUM", "2024-09-09", "How Innovative Is China in Quantum?", "量子技术", "量子科学论文、专利、人才与产业化能力比较"),
    ("C-ITIF-2024-CHINA-IS-RAPIDLY-BECOMING-A-LEADING-INNOVATOR-IN-ADVANCED-INDUSTRIES", "2024-09-16", "China Is Rapidly Becoming a Leading Innovator in Advanced Industries", "先进产业综合", "跨行业汇总中国科研产出、企业创新和先进产业转化能力"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded ITIF China advanced-industry innovation batch.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog, fields = read_csv(root / "05_报告总目录.csv")
    light, light_fields = read_csv(root / "79_ITIF中国先进产业创新系列轻量目录.csv")
    by_id = {row["报告ID"]: row for row in catalog}
    light_by_id = {row["报告ID"]: row for row in light}
    if missing := {item[0] for item in SELECTED_ITEMS} - set(by_id):
        raise RuntimeError(f"selected reports missing from catalog: {sorted(missing)}")

    web_dir = root / "03_证据底稿" / "网页原文"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (web_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    ledger: list[dict[str, str]] = []
    for index, (rid, published, title, domain, role) in enumerate(SELECTED_ITEMS, 1):
        row = by_id[rid]
        if row["发布日期"] != published or row["报告名称"] != title:
            raise RuntimeError(f"selected metadata drift: {rid}")
        landing = row["原文链接"]
        asset_url = landing.rstrip("/") + ".md"
        pdf_path = root / "03_证据底稿" / "原文PDF" / f"{rid}.pdf"
        if not pdf_path.exists() or not pdf_path.read_bytes().startswith(b"%PDF"):
            raise RuntimeError(f"existing official PDF missing or invalid: {rid}")
        source_path = web_dir / f"{rid}.md"
        content = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else fetch_markdown(asset_url)
        clean = clean_text(content)
        if len(clean) < 1_000:
            raise RuntimeError(f"official full text too short: {rid} chars={len(clean)}")
        source_path.write_text(content, encoding="utf-8", newline="\n")
        existing_text_path = text_dir / f"{rid}.txt"
        if not existing_text_path.exists():
            raise RuntimeError(f"existing PDF-derived text missing: {rid}")
        text_path = text_dir / f"{rid}-official-web.txt"
        slice_path = slice_dir / f"{rid}-official-web.md"
        text_path.write_text(clean, encoding="utf-8", newline="\n")
        item = {
            "id": rid,
            "title": title,
            "institution": "Information Technology and Innovation Foundation",
            "date": published,
            "landing_url": landing,
            "axes": "科学体系与基础研究；技术创新与关键技术；产业创新转化与区域生态；中国科技横向维度",
            "role": role,
        }
        slice_path.write_text(make_slice(item, clean), encoding="utf-8", newline="\n")
        payload = content.encode("utf-8")
        lower = clean.lower()
        china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc") + lower.count("sino-")
        row.update({
            "本地路径": str(existing_text_path),
            "正文完整度": "ITIF官方Markdown全文已保存；同时生成可检索文本和科技创新切片",
            "优先级": "P0-China-STI-node",
            "示踪问题": item["axes"],
            "样本角色": SERIES_ROLE,
            "编码状态": "全文待观点编码",
            "预期用途": role,
            "本地原始资产路径": str(pdf_path),
            "原始资产状态": "既有ITIF官方PDF已复核；另存官方Markdown正文，并生成可检索文本与科技创新切片",
        })
        light_by_id[rid]["全文策略"] = "既有官方PDF已复核；本批另存官方Markdown、净文本和科技创新切片"
        pdf_payload = pdf_path.read_bytes()
        ledger.append({
            "报告ID": rid, "发布日期": published, "报告名称": title, "技术领域": domain,
            "官方落地页": landing, "官方全文入口": asset_url, "资产类型": "ITIF官方Markdown网页正文",
            "既有官方PDF": str(pdf_path), "既有PDF字节数": str(len(pdf_payload)),
            "既有PDF_SHA256": hashlib.sha256(pdf_payload).hexdigest(),
            "新增网页正文": str(source_path), "本地文本": str(text_path), "本地切片": str(slice_path),
            "网页数": "1", "字节数": str(len(payload)), "清洗文本字符数": str(len(clean)),
            "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(payload).hexdigest(),
            "科技创新主轴": item["axes"], "科技创新复用角色": role,
            "选择理由": "覆盖科学前沿、关键技术、产业化和跨行业比较；安全议题未作为全文选择条件",
            "获取日期": date.today().isoformat(),
        })
        print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} chars={len(clean)}", flush=True)

    selected_ids = {item[0] for item in SELECTED_ITEMS}
    for rid, light_row in light_by_id.items():
        if rid not in selected_ids:
            pdf_path = root / "03_证据底稿" / "原文PDF" / f"{rid}.pdf"
            if not pdf_path.exists() or not pdf_path.read_bytes().startswith(b"%PDF"):
                raise RuntimeError(f"light-series official PDF missing or invalid: {rid}")
            light_row["全文策略"] = "既有官方PDF已复核；保留PDF全文，不追加网页正文"
    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(root / "05_报告总目录.csv", catalog, fields)
    write_csv(root / "79_ITIF中国先进产业创新系列轻量目录.csv", light, light_fields)
    write_csv(root / "234_ITIF中国先进产业技术创新能力精选全文台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    (root / "235_ITIF中国先进产业技术创新能力精选全文结果.md").write_text(
        "# ITIF中国先进产业技术创新能力精选全文结果\n\n"
        f"- 完整性复核确认轻量目录10份均已有官方PDF，本系列未抓取全文为0份。\n"
        f"- 本批对其中{len(ledger)}份增加ITIF官方Markdown正文和定向切片，另外4份继续使用既有PDF，不追加重复格式。\n"
        f"- 共{totals['网页数']}个正式网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符；China/Chinese/PRC/Sino-词形命中{totals['China词形命中数']:,}次。\n"
        "- 全文覆盖机器人、电动车与电池、生物技术、半导体、量子技术及先进产业综合比较。\n"
        "- 化工与材料、核能、人工智能、显示技术均已有PDF；后续只在具体项目问题触发时增加网页正文或深化编码。\n"
        "- 本批选择依据为科学研究、技术能力、企业研发与产业创新转化证据增量；安全和贸易竞争表述仅作为正文中的来源立场处理。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
