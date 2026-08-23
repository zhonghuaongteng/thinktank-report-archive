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


SERIES_ROLE = "技术前瞻公共研发优先级与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-STOA-EPRS-BRI-2017-603205",
        "institution_id": "eu-stoa",
        "institution": "European Parliament Panel for the Future of Science and Technology (STOA)",
        "date": "2017-08-31",
        "title": "Forward-looking policy-making at the European Parliament through scientific foresight",
        "landing_url": "https://www.europarl.europa.eu/stoa/en/document/EPRS_BRI(2017)603205",
        "asset_url": "https://www.europarl.europa.eu/RegData/etudes/BRIE/2017/603205/EPRS_BRI(2017)603205_EN.pdf",
        "axes": "技术前瞻与科技评估；创新政策与研发治理；参与式政策分析",
        "role": "欧洲议会将科学前瞻、情景分析和回溯法嵌入科技政策选择的2017方法节点",
    },
    {
        "id": "C-EU-STOA-EPRS-STU-2021-690031",
        "institution_id": "eu-stoa",
        "institution": "European Parliament Panel for the Future of Science and Technology (STOA)",
        "date": "2021-07-26",
        "title": "Guidelines for foresight-based policy analysis",
        "landing_url": "https://www.europarl.europa.eu/stoa/en/document/EPRS_STU(2021)690031",
        "asset_url": "https://www.europarl.europa.eu/RegData/etudes/STUD/2021/690031/EPRS_STU(2021)690031_EN.pdf",
        "axes": "技术前瞻与科技评估；创新政策与研发治理；证据与社会关切整合",
        "role": "把前瞻方法制度化为议会政策分析流程、处理复杂科技议题的2021方法节点",
    },
    {
        "id": "C-EU-JRC-JRC139022",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2024-01-01",
        "title": "(Dis)Entangling the Future - Horizon scanning for emerging technologies and breakthrough innovations in the field of quantum technologies",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC139022",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC139022/JRC139022_01.pdf",
        "axes": "技术前瞻与科技评估；量子技术路线；科技人才与创新生态；中国科技横向维度",
        "role": "以地平线扫描识别量子技术新信号、创新主体与政策介入点的2024技术路线节点",
    },
    {
        "id": "C-EU-JRC-JRC139310",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2024-01-01",
        "title": "Materialising the Future - Horizon scanning for emerging technologies and breakthrough innovations in the field of advance materials for energy",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC139310",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC139310/JRC139310_01.pdf",
        "axes": "技术前瞻与科技评估；先进材料技术路线；产业创新与成果转化；中国科技横向维度",
        "role": "以地平线扫描连接先进能源材料、突破性创新与研发优先级的2024技术路线节点",
    },
    {
        "id": "C-EU-JRC-JRC139313",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2024-01-01",
        "title": "Eyes on the Future - Signals from recent reports on emerging technologies and breakthrough innovations to support European Innovation Council strategic intelligence - Volume 2",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC139313",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC139313/JRC139313_01.pdf",
        "axes": "技术前瞻与科技评估；关键与新兴技术；创新资助优先级；中国科技横向维度",
        "role": "把跨行业技术信号转化为欧洲创新理事会资助优先级和战略情报的2024综合节点",
    },
    {
        "id": "C-EU-JRC-JRC142380",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01",
        "title": "Eyes on the Future - Signals from recent reports on emerging technologies and breakthrough innovations to support European Innovation Council strategic intelligence - Volume 3",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC142380",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC142380/JRC142380_01.pdf",
        "axes": "技术前瞻与科技评估；非欧盟前沿技术；创新资助优先级；中国科技横向维度",
        "role": "追踪非欧盟国家新兴技术并反馈欧洲研发与创新资助选择的2025比较节点",
    },
)

SOURCE_CATALOGS = (
    "182_欧洲议会STOA科技评估近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
)


def update_source_catalogs(root: Path, china_hits_by_id: dict[str, int]) -> None:
    for filename in SOURCE_CATALOGS:
        path = root / filename
        records, fields = read_csv(path)
        changed = False
        for row in records:
            rid = row.get("报告ID") or row.get("统一目录报告ID")
            if rid not in china_hits_by_id:
                continue
            if "全文策略" in fields:
                row["全文策略"] = "已进入技术前瞻、公共研发优先级与中国比较定点全文；按官方PDF、净文本和科技创新切片调用"
            if "中国直接信号" in fields and china_hits_by_id[rid] > 0:
                row["中国直接信号"] = "是（全文词形定位；具体语义待编码）"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded technology-foresight and R&D-priority evidence batch.")
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
            source_path = pdf_dir / f"{rid}.pdf"
            if not source_path.exists() or not source_path.read_bytes().startswith(b"%PDF"):
                source_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
            payload = source_path.read_bytes()
            if not payload.startswith(b"%PDF"):
                raise RuntimeError(f"invalid official PDF: {rid}")
            text, units = extract_pdf(source_path)
            if len(text) < 1_000 or units < 1:
                raise RuntimeError(f"extracted full text too short: {rid} units={units} chars={len(text)}")
            clean = clean_text(text)
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            text_path.write_text(clean, encoding="utf-8", newline="\n")
            slice_path.write_text(make_slice(item, clean), encoding="utf-8", newline="\n")
            lower = clean.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc") + lower.count("sino-")
            row = by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = "官方PDF全文已保存；同时生成提取文本和科技创新切片"
            row["优先级"] = "P1-STI-foresight-node"
            row["示踪问题"] = item["axes"]
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = item["role"]
            row["本地原始资产路径"] = str(source_path)
            row["原始资产状态"] = "官方PDF已获取并校验"
            ledger.append({
                "报告ID": rid,
                "机构ID": item["institution_id"],
                "机构": item["institution"],
                "发布日期": item["date"],
                "报告名称": item["title"],
                "官方落地页": item["landing_url"],
                "官方全文入口": item["asset_url"],
                "资产类型": "官方PDF",
                "本地原始资产": str(source_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "页数": str(units),
                "字节数": str(len(payload)),
                "清洗文本字符数": str(len(clean)),
                "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(payload).hexdigest(),
                "科技创新主轴": item["axes"],
                "科技创新复用角色": item["role"],
                "选择理由": "补充技术前瞻、科技评估、前沿技术路线与公共创新资助优先级；安全题名不构成选择依据",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={units} chars={len(clean)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, fields)
    update_source_catalogs(root, {row["报告ID"]: int(row["China词形命中数"]) for row in ledger})
    write_csv(root / "228_技术前瞻公共研发优先级与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    (root / "229_技术前瞻公共研发优先级与中国比较定点增补结果.md").write_text(
        "# 技术前瞻、公共研发优先级与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：欧洲议会STOA 2份、欧委会JRC 4份。\n"
        f"- 保存{len(ledger)}份官方PDF，共{totals['页数']:,}页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；仅用于定位中国科技比较段落。\n"
        "- 覆盖科学前瞻方法、前瞻型政策分析、量子技术、先进材料、跨行业技术信号与公共创新资助优先级。\n"
        "- 未新增安全类目录；全文选择由科学技术前瞻、技术路线和研发资助机制触发。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} pages={totals['页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
