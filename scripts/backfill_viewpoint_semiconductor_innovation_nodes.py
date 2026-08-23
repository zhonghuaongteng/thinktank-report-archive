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


SERIES_ROLE = "半导体微电子研发创新生态与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-JRC-JRC129035",
        "kind": "pdf",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2022-01-01",
        "title": "The position of the EU in the semiconductor value chain: evidence on trade, foreign acquisitions, and ownership",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC129035",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC129035/JRC129035_01.pdf",
        "axes": "半导体价值链；企业所有权；研发与设计；制造装备；国际能力比较；中国科技横向维度",
        "role": "以企业、贸易和所有权数据拆解EDA、装备材料、设计、制造与封测位置的2022测量节点",
    },
    {
        "id": "C-DE-ACATECH-44300",
        "kind": "pdf",
        "institution_id": "de-acatech",
        "institution": "acatech - National Academy of Science and Engineering",
        "date": "2023-11-08",
        "title": "RISC-V: Potenziale eines offenen Standards für Chipentwicklung",
        "landing_url": "https://www.acatech.de/publikation/risc-v/",
        "asset_url": "https://www.acatech.de/publikation/risc-v/download-pdf?lang=de",
        "axes": "RISC-V；开放指令集；芯片设计；人才；开源生态；中国科技横向维度",
        "role": "评估开放指令集、工具链成熟度、人才供给和中国参与格局的2023技术路线节点",
    },
    {
        "id": "C-US-OSTP-2024-NATIONAL-STRATEGY-ON-MICROELECTRONICS-RESEARCH-MARCH-2024",
        "kind": "pdf",
        "institution_id": "us-ostp",
        "institution": "White House Office of Science and Technology Policy",
        "date": "2024-03-01",
        "title": "National Strategy on Microelectronics Research",
        "landing_url": "https://bidenwhitehouse.archives.gov/ostp/",
        "asset_url": "https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/03/National-Strategy-on-Microelectronics-Research-March-2024.pdf",
        "axes": "微电子基础研究；先进材料；设计工具；异构集成；计量；科研设施；人才；成果转化",
        "role": "连接基础研究、共享设施、原型制造、技术人才与商业转化的2024国家研发战略节点",
    },
    {
        "id": "C-CSIS-RAI-2024-UNDERSTANDING-IMEC-GLOBAL-CENTER-COOPERATIVE-RESEARCH-SEMICONDUCTORS",
        "kind": "web",
        "institution_id": "csis-rai",
        "institution": "CSIS Renewing American Innovation",
        "date": "2024-03-19",
        "title": "Understanding imec: The Global Center for Cooperative Research in Semiconductors",
        "landing_url": "https://www.csis.org/analysis/understanding-imec-global-center-cooperative-research-semiconductors",
        "asset_url": "https://www.csis.org/analysis/understanding-imec-global-center-cooperative-research-semiconductors",
        "axes": "协同研发平台；中试线；公共投入；企业会员；知识产权；人才；成果产业化",
        "role": "解释imec如何组织跨国预竞争研发、共享中试设施和企业协作的2024机构机制节点",
    },
    {
        "id": "C-DE-ACATECH-54812",
        "kind": "pdf",
        "institution_id": "de-acatech",
        "institution": "acatech - National Academy of Science and Engineering",
        "date": "2025-05-13",
        "title": "Quelloffene Designinstrumente für souveräne Chipentwicklung",
        "landing_url": "https://www.acatech.de/publikation/quelloffene-designinstrumente-fuer-souveraene-chipentwicklung/",
        "asset_url": "https://www.acatech.de/publikation/quelloffene-designinstrumente-fuer-souveraene-chipentwicklung/download-pdf?lang=de",
        "axes": "开源EDA；开放PDK；芯片设计；标准接口；初创企业；技术成熟度；科研产业协作",
        "role": "评估开源EDA与开放PDK的适用边界、成熟度和创新生态条件的2025工具链节点",
    },
    {
        "id": "C-OECD-DOI-4154CDBF-EN",
        "kind": "pdf",
        "institution_id": "oecd-sti",
        "institution": "Organisation for Economic Co-operation and Development",
        "date": "2025-06-24",
        "title": "Mapping the semiconductor value chain",
        "landing_url": "https://www.oecd.org/en/publications/mapping-the-semiconductor-value-chain_4154cdbf-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/mapping-the-semiconductor-value-chain_5ba52971/4154cdbf-en.pdf",
        "axes": "半导体价值链；投入产出；制造环节；数据方法；国际分工；中国科技横向维度",
        "role": "以产品分类、贸易和投入产出数据建立全球价值链与中国位置的2025测量节点",
    },
)

SOURCE_CATALOGS = (
    "77_OECD_STI正式系列轻量目录.csv",
    "88_美国OSTP科学技术创新政策轻量目录.csv",
    "178_CSIS_RAI科技创新项目轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "202_acatech科学与技术创新正式成果轻量总目录.csv",
)


def update_source_catalogs(root: Path, selected_ids: set[str]) -> None:
    for filename in SOURCE_CATALOGS:
        path = root / filename
        records, fields = read_csv(path)
        changed = False
        for row in records:
            report_id = row.get("统一目录报告ID") or row.get("报告ID")
            if report_id not in selected_ids or "全文策略" not in fields:
                continue
            row["全文策略"] = "已进入半导体微电子研发创新定点全文；按官方原始资产、净文本和科技创新切片调用"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded semiconductor and microelectronics innovation evidence batch.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog, fields = read_csv(root / "05_报告总目录.csv")
    by_id = {row["报告ID"]: row for row in catalog}
    selected_ids = {item["id"] for item in SELECTED_ITEMS}
    if missing := selected_ids - set(by_id):
        raise RuntimeError(f"selected reports missing from catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        row = by_id[item["id"]]
        if row["发布日期"] != item["date"] or row["报告名称"] != item["title"]:
            raise RuntimeError(f"selected metadata drift: {item['id']}")
        if row.get("本地原始资产路径") or row.get("本地路径"):
            raise RuntimeError(f"selected report already has a local asset: {item['id']}")

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
            if item["kind"] == "pdf":
                source_path = dirs["pdf"] / f"{rid}.pdf"
                if not source_path.exists() or not source_path.read_bytes().startswith(b"%PDF"):
                    source_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
                payload = source_path.read_bytes()
                text, units = extract_pdf(source_path)
                asset_type = "官方PDF"
                completeness = "官方PDF全文已保存；同时生成可检索文本和科技创新切片"
                status = "官方PDF已获取并校验；已生成可检索文本和科技创新切片"
            else:
                page = navigate(target, item["landing_url"], minimum_text=1_000)
                if len(page["text"]) < 3_000 or "imec" not in page["text"].lower():
                    raise RuntimeError(f"thin or incorrect official web page: {rid}")
                source_path = dirs["html"] / f"{rid}.html"
                source_path.write_text(sanitize_html(page["html"]), encoding="utf-8", newline="\n")
                payload = source_path.read_bytes()
                text, units = clean_text(page["text"]), 1
                asset_type = "官方网页HTML"
                completeness = "官方网页正文与HTML快照已保存；同时生成可检索文本和科技创新切片"
                status = "官方网页正文及HTML快照已获取并校验；已生成可检索文本和科技创新切片"
            clean = clean_text(text)
            if len(clean) < 1_000 or units < 1:
                raise RuntimeError(f"extracted full text too short: {rid} units={units} chars={len(clean)}")
            text_path = dirs["text"] / f"{rid}.txt"
            slice_path = dirs["slice"] / f"{rid}.md"
            text_path.write_text(clean, encoding="utf-8", newline="\n")
            slice_path.write_text(make_slice(item, clean), encoding="utf-8", newline="\n")
            lower = clean.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc") + lower.count("sino-")
            by_id[rid].update({
                "本地路径": str(text_path),
                "正文完整度": completeness,
                "优先级": "P0-China-STI-node" if china_hits else "P1-STI-semiconductor-node",
                "示踪问题": item["axes"],
                "样本角色": SERIES_ROLE,
                "编码状态": "全文待观点编码",
                "预期用途": item["role"],
                "本地原始资产路径": str(source_path),
                "原始资产状态": status,
            })
            ledger.append({
                "报告ID": rid,
                "机构ID": item["institution_id"],
                "机构": item["institution"],
                "发布日期": item["date"],
                "报告名称": item["title"],
                "官方落地页": item["landing_url"],
                "官方全文入口": item["asset_url"],
                "资产类型": asset_type,
                "本地原始资产": str(source_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "页数或网页数": str(units),
                "字节数": str(len(payload)),
                "清洗文本字符数": str(len(clean)),
                "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(payload).hexdigest(),
                "科技创新主轴": item["axes"],
                "科技创新复用角色": item["role"],
                "选择理由": "补充半导体基础研究、开放设计、协同研发平台、科研设施、人才和价值链测量；安全与管制议题未作为选择条件",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} units={units} chars={len(clean)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(root / "05_报告总目录.csv", catalog, fields)
    update_source_catalogs(root, selected_ids)
    write_csv(root / "248_半导体微电子研发创新生态与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "249_半导体微电子研发创新生态与中国比较定点增补结果.md").write_text(
        "# 半导体、微电子研发创新生态与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点保存{len(ledger)}份正式材料，覆盖JRC、acatech、OSTP、CSIS RAI与OECD，形成2022—2025跨期节点。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger)-pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；只用于定位中国研发、制造、设计生态和价值链位置。\n"
        "- 技术机制覆盖先进材料、设计工具、RISC-V、开放PDK、异构集成、先进封装与计量；创新机制覆盖共享科研设施、预竞争研发平台、人才、初创企业、成果转化和价值链测量。\n"
        "- 本批未纳入出口管制、关税、军事芯片保障或一般供应链安全主导材料；相关表述仅在直接解释研发和创新能力时调用。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
