from __future__ import annotations

import argparse
import hashlib
from datetime import date
from pathlib import Path
from urllib.parse import quote

try:
    from scripts.backfill_viewpoint_china_research_system_nodes import (
        clean_text,
        download_pdf,
        extract_pdf,
        make_slice,
        read_csv,
        write_csv,
    )
    from scripts.backfill_viewpoint_cross_institution_china_innovation import navigate, sanitize_html
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _proxy_json
except ModuleNotFoundError:
    from backfill_viewpoint_china_research_system_nodes import (
        clean_text,
        download_pdf,
        extract_pdf,
        make_slice,
        read_csv,
        write_csv,
    )
    from backfill_viewpoint_cross_institution_china_innovation import navigate, sanitize_html
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json


SERIES_ROLE = "中国科技创新测量、技术生态与科研投入定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-JRC-JRC102366",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2016-01-01",
        "title": "PREDICT 2016 Country factsheets: EU Member States – Benchmarking with Non-EU Countries",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC102366",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC102366/jrc102366%20with%20identifiers.pdf",
        "asset_type": "pdf",
        "axes": "研发投入与创新政策；创新测量与政策方法；国际合作与中国比较",
        "role": "中国与欧美日等经济体ICT产业规模、研发投入和研发强度的2016比较基线",
    },
    {
        "id": "C-EU-JRC-JRC118467",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2019-01-01",
        "title": "The techno-economic segment analysis of the Earth observation ecosystem",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC118467",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC118467/jrc118467_eo_tes_report_5_dec_2019_final.pdf",
        "asset_type": "pdf",
        "axes": "研发投入与创新政策；关键与新兴技术；产业创新与成果转化；国际合作与中国比较",
        "role": "中国、欧盟和美国地球观测研发主体、专利集中度与空间数据产业化的比较材料",
    },
    {
        "id": "C-EU-JRC-JRC133609",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2023-01-01",
        "title": "Sustainable Development Goals and Digital Technologies: Mapping Scientific Research",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC133609",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC133609/JRC133609_01.pdf",
        "asset_type": "pdf",
        "axes": "科学体系与科研能力；关键与新兴技术；创新测量与政策方法；国际合作与中国比较",
        "role": "中国、美国和欧盟数字技术与可持续发展科研产出的主题映射和比较节点",
    },
    {
        "id": "C-EU-JRC-JRC141343",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01",
        "title": "Tracking country Innovation Performance: The Innovation Output Indicator 2024",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC141343",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC141343/JRC141343_01.pdf",
        "asset_type": "pdf",
        "axes": "产业创新与成果转化；创新测量与政策方法；国际合作与中国比较",
        "role": "中国创新产出、知识密集就业、技术能力与成果市场化追赶的2024指标节点",
    },
    {
        "id": "C-EU-JRC-JRC146046",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2026-01-01",
        "title": "Virtual Worlds, Real Impact",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC146046",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC146046/JRC146046_01.pdf",
        "asset_type": "pdf",
        "axes": "研发投入与创新政策；关键与新兴技术；产业创新与成果转化；国际合作与中国比较",
        "role": "中国虚拟世界研发、创新主体、风险投资和AI、XR、物联网技术生态的全球比较材料",
    },
    {
        "id": "C-CSIS-RAI-2026-INNOVATION-LIGHTBULB-FY-2027-PROPOSED-RD-CUTS",
        "institution_id": "csis-rai",
        "institution": "CSIS Renewing American Innovation",
        "date": "2026-06-10",
        "title": "Innovation Lightbulb: FY 2027 Proposed R&D Cuts",
        "landing_url": "https://www.csis.org/analysis/innovation-lightbulb-fy-2027-proposed-rd-cuts",
        "asset_url": "https://www.csis.org/analysis/innovation-lightbulb-fy-2027-proposed-rd-cuts",
        "asset_type": "web",
        "axes": "科学体系与科研能力；研发投入与创新政策；国际合作与中国比较",
        "role": "公共基础与应用研究投入、私人研发边界及中国国家支持研发扩张的2026比较节点",
    },
)


def update_measurement_catalog(path: Path, selected_ids: set[str]) -> None:
    rows, fields = read_csv(path)
    for row in rows:
        report_id = row.get("统一目录报告ID") or row.get("报告ID")
        if report_id in selected_ids:
            row["全文策略"] = "已进入中国科技创新测量与技术生态定点全文；按官方原始资产、提取文本和科技创新切片调用"
    write_csv(path, rows, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded China innovation measurement evidence batch.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    catalog, fields = read_csv(catalog_path)
    by_id = {row["报告ID"]: row for row in catalog}
    ids = {item["id"] for item in SELECTED_ITEMS}
    if missing := ids - set(by_id):
        raise RuntimeError(f"selected reports missing from catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        row = by_id[item["id"]]
        if row["发布日期"] != item["date"] or row["报告名称"] != item["title"]:
            raise RuntimeError(f"selected metadata drift: {item['id']}")

    dirs = {
        "pdf": root / "03_证据底稿" / "原文PDF",
        "html": root / "03_证据底稿" / "网页原文",
        "text": root / "03_证据底稿" / "文本",
        "slice": root / "03_证据底稿" / "切片",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)

    opened = _proxy_json("/new?url=" + quote(SELECTED_ITEMS[0]["landing_url"], safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = item["id"]
            pages = 0
            if item["asset_type"] == "pdf":
                asset_path = dirs["pdf"] / f"{rid}.pdf"
                if not asset_path.exists() or not asset_path.read_bytes().startswith(b"%PDF"):
                    asset_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
                payload = asset_path.read_bytes()
                if not payload.startswith(b"%PDF"):
                    raise RuntimeError(f"invalid official PDF: {rid}")
                text, pages = extract_pdf(asset_path)
                completeness = "官方PDF全文已保存；同时生成提取文本和科技创新切片"
                status = "官方PDF已获取并校验"
                asset_label = "官方PDF"
            else:
                page = navigate(target, item["landing_url"], minimum_text=1_000)
                if item["title"].lower() not in page["title"].lower() or len(page["text"]) < 3_000:
                    raise RuntimeError(f"thin or incorrect official web page: {rid}")
                asset_path = dirs["html"] / f"{rid}.html"
                asset_path.write_text(sanitize_html(page["html"]), encoding="utf-8", newline="\n")
                text = clean_text(page["text"])
                payload = asset_path.read_bytes()
                completeness = "官方网页正文与HTML快照已保存；同时生成科技创新切片"
                status = "官方网页正文及HTML快照已获取"
                asset_label = "官方网页HTML"
            if len(text) < 1_000:
                raise RuntimeError(f"text too short: {rid} {len(text)}")
            text_path = dirs["text"] / f"{rid}.txt"
            slice_path = dirs["slice"] / f"{rid}.md"
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(make_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            row = by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = completeness
            row["优先级"] = "P0-China-STI-node"
            row["示踪问题"] = item["axes"] + "；中国科技横向维度"
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = item["role"]
            row["本地原始资产路径"] = str(asset_path)
            row["原始资产状态"] = status
            ledger.append({
                "报告ID": rid, "机构ID": item["institution_id"], "机构": item["institution"],
                "发布日期": item["date"], "报告名称": item["title"], "官方落地页": item["landing_url"],
                "官方原始资产入口": item["asset_url"], "资产类型": asset_label,
                "本地原始资产": str(asset_path), "本地文本": str(text_path), "本地切片": str(slice_path),
                "PDF页数": str(pages), "字节数": str(len(payload)), "清洗文本字符数": str(len(text)),
                "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(payload).hexdigest(),
                "科技创新主轴": item["axes"], "科技创新复用角色": item["role"],
                "选择理由": "直接支撑科技创新测量、研发投入、技术生态或科研能力比较；安全题名不构成选择依据",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={pages} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, fields)
    update_measurement_catalog(root / "186_欧委会JRC科技创新政策近十年轻量总目录.csv", ids)
    update_measurement_catalog(root / "178_CSIS_RAI科技创新项目轻量总目录.csv", ids)
    write_csv(root / "218_中国科技创新测量与技术生态定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("PDF页数", "字节数", "清洗文本字符数", "China词形命中数")}
    (root / "219_中国科技创新测量与技术生态定点增补结果.md").write_text(
        "# 中国科技创新测量与技术生态定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：欧委会JRC 5份、CSIS RAI 1份。\n"
        f"- 保存5份官方PDF和1项官方网页正文，共{totals['PDF页数']:,}页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- China/Chinese/PRC词形共命中{totals['China词形命中数']:,}次。\n"
        "- 覆盖ICT产业研发、地球观测创新生态、数字技术科研图谱、创新产出指标、虚拟世界技术生态，以及公共基础与应用研究投入。\n"
        "- 皇家学会候选因官方防火墙阻断而保留目录级；贸易制裁、军事技术和纯安全治理材料未进入本批全文。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} pages={totals['PDF页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
