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
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json


SERIES_ROLE = "科研人才、知识转移与创新商业化定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-JRC-JRC102534",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2016-01-01",
        "title": "Intersectoral mobility and knowledge transfer. Preliminary evidence of the impact of intersectoral mobility policy instruments",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC102534",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC102534/jrc102534_ism_report_final.pdf",
        "axes": "研发投入与创新政策；产业创新与成果转化；科技人才与技能；创新测量与政策方法",
        "role": "跨部门科研人才流动政策、产业博士及知识转移效果的2016评估基线",
    },
    {
        "id": "C-JP-RIETI-18-E-070",
        "institution_id": "jp-rieti",
        "institution": "Research Institute of Economy, Trade and Industry (RIETI)",
        "date": "2018-10-01",
        "title": "How Does the Global Network of Research Collaboration Affect the Quality of Innovation?",
        "landing_url": "https://www.rieti.go.jp/en/publications/summary/18100009.html",
        "asset_url": "https://www.rieti.go.jp/jp/publications/dp/18e070.pdf",
        "axes": "科学体系与科研能力；产业创新与成果转化；国际合作与中国比较",
        "role": "全球科研合作网络、跨境知识流动与创新质量关系的微观证据",
    },
    {
        "id": "C-JP-RIETI-20-J-001",
        "institution_id": "jp-rieti",
        "institution": "Research Institute of Economy, Trade and Industry (RIETI)",
        "date": "2020-01-01",
        "title": "Contributions of Corporate Basic Research and Research Collaboration with Academia to Innovation and Spillover Performance in Japan",
        "landing_url": "https://www.rieti.go.jp/en/publications/summary/20010007.html",
        "asset_url": "https://www.rieti.go.jp/jp/publications/dp/20j001.pdf",
        "axes": "科学体系与科研能力；研发投入与创新政策；产业创新与成果转化",
        "role": "企业基础研究、产学研合作、创新产出与技术溢出的量化机制证据",
    },
    {
        "id": "C-EU-JRC-JRC124354",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2021-01-01",
        "title": "Technology Transfer and Commercialisation for the European Green Deal",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC124354",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC124354/kjna30694enn.pdf",
        "axes": "科学体系与科研能力；关键与新兴技术；产业创新与成果转化",
        "role": "氢能、电池、碳捕集和AI绿色技术从实验室到市场的知识产权、融资与政策障碍",
    },
    {
        "id": "C-EU-JRC-JRC134598",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2023-01-01",
        "title": "Putting knowledge and technology to work: A look at EU innovation output",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC134598",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC134598/JRC134598_01.pdf",
        "axes": "关键与新兴技术；产业创新与成果转化；创新测量与政策方法；国际合作与中国比较",
        "role": "知识、技术、高技能就业与产品市场化构成创新产出的跨国测量及中国比较节点",
    },
    {
        "id": "C-EU-JRC-JRC141091",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01",
        "title": "R&D productivity: are ideas harder to find or does Europe suffer from a commercialization gap?",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC141091",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC141091/JRC141091_01.pdf",
        "axes": "研发投入与创新政策；产业创新与成果转化；创新测量与政策方法",
        "role": "全球研发生产率下降与欧洲商业化缺口的2025测量节点",
    },
)

SOURCE_CATALOGS = (
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "194_RIETI科技创新与中国近十年轻量总目录.csv",
)


def update_source_catalogs(root: Path, selected_ids: set[str]) -> None:
    for filename in SOURCE_CATALOGS:
        path = root / filename
        records, fields = read_csv(path)
        changed = False
        for row in records:
            if row.get("报告ID") in selected_ids:
                row["全文策略"] = "已进入科研人才、知识转移与创新商业化定点全文；按官方PDF、提取文本和科技创新切片调用"
                changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded science mobility, transfer, and commercialization evidence batch.")
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

    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    opened = _proxy_json("/new?url=" + quote(SELECTED_ITEMS[0]["landing_url"], safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = item["id"]
            pdf_path = pdf_dir / f"{rid}.pdf"
            if not pdf_path.exists() or not pdf_path.read_bytes().startswith(b"%PDF"):
                pdf_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
            payload = pdf_path.read_bytes()
            if not payload.startswith(b"%PDF"):
                raise RuntimeError(f"invalid official PDF: {rid}")
            text, pages = extract_pdf(pdf_path)
            if len(text) < 1_000:
                raise RuntimeError(f"extracted PDF text too short: {rid} {len(text)}")
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            text_path.write_text(clean_text(text), encoding="utf-8", newline="\n")
            slice_path.write_text(make_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            row = by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = "官方PDF全文已保存；同时生成提取文本和科技创新切片"
            row["优先级"] = "P1-STI-mechanism-node"
            row["示踪问题"] = item["axes"]
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = item["role"]
            row["本地原始资产路径"] = str(pdf_path)
            row["原始资产状态"] = "官方PDF已获取并校验"
            ledger.append({
                "报告ID": rid, "机构ID": item["institution_id"], "机构": item["institution"],
                "发布日期": item["date"], "报告名称": item["title"], "官方落地页": item["landing_url"],
                "官方PDF入口": item["asset_url"], "本地原始PDF": str(pdf_path),
                "本地文本": str(text_path), "本地切片": str(slice_path), "PDF页数": str(pages),
                "字节数": str(len(payload)), "清洗文本字符数": str(len(text)), "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(payload).hexdigest(), "科技创新主轴": item["axes"],
                "科技创新复用角色": item["role"],
                "选择理由": "直接补充科研人才流动、知识转移、产学研合作或创新商业化机制；安全题名不构成选择依据",
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
    update_source_catalogs(root, ids)
    write_csv(root / "220_科研人才知识转移与创新商业化定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("PDF页数", "字节数", "清洗文本字符数", "China词形命中数")}
    (root / "221_科研人才知识转移与创新商业化定点增补结果.md").write_text(
        "# 科研人才、知识转移与创新商业化定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：欧委会JRC 4份、RIETI 2份。\n"
        f"- 保存6份官方PDF，共{totals['PDF页数']:,}页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- China/Chinese/PRC词形共命中{totals['China词形命中数']:,}次；词形仅用于定位中国比较段落。\n"
        "- 覆盖跨部门人才流动、全球科研合作网络、企业基础研究与产学合作、绿色技术转移、创新产出测量与研发生产率。\n"
        "- 军事、出口管制、供应链安全和一般贸易材料未进入本批全文。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} pages={totals['PDF页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
