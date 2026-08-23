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
    from scripts.extend_viewpoint_nasem_selected_fulltexts import (
        count_archived_chapters,
        fetch_book_via_jina,
        normalize_archive_whitespace,
        selected_slice,
    )
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
    from extend_viewpoint_nasem_selected_fulltexts import (
        count_archived_chapters,
        fetch_book_via_jina,
        normalize_archive_whitespace,
        selected_slice,
    )


SERIES_ROLE = "AI for Science与公共科研基础设施定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-OECD-DOI-8288D208-EN",
        "kind": "pdf",
        "institution_id": "oecd-sti",
        "institution": "OECD",
        "date": "2017-12-08",
        "title": "Digital platforms for facilitating access to research infrastructures",
        "landing_url": "https://www.oecd.org/en/publications/digital-platforms-for-facilitating-access-to-research-infrastructures_8288d208-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/12/digital-platforms-for-facilitating-access-to-research-infrastructures_936ce04e/8288d208-en.pdf",
        "axes": "科学体系与科研能力；科研数据与数字基础设施；开放科学与国际合作",
        "role": "科研设施数字平台如何降低发现和使用门槛、扩大跨机构与产业用户访问的早期机制节点",
    },
    {
        "id": "C-OECD-DOI-3FFEE43B-EN",
        "kind": "pdf",
        "institution_id": "oecd-sti",
        "institution": "OECD",
        "date": "2019-03-28",
        "title": "Reference framework for assessing the scientific and socio-economic impact of research infrastructures",
        "landing_url": "https://www.oecd.org/en/publications/reference-framework-for-assessing-the-scientific-and-socio-economic-impact-of-research-infrastructures_3ffee43b-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/03/reference-framework-for-assessing-the-scientific-and-socio-economic-impact-of-research-infrastructures_5215b703/3ffee43b-en.pdf",
        "axes": "科学体系与科研能力；研发投入与创新政策；创新测量与政策方法",
        "role": "以科研产出、开放数据、产业合作和社会经济效应衡量重大科研设施公共价值的指标框架",
    },
    {
        "id": "C-US-NASEM-26566",
        "kind": "nasem",
        "record_id": 26566,
        "institution_id": "us-nasem",
        "institution": "National Academies of Sciences, Engineering, and Medicine",
        "date": "2022-06-13",
        "title": "Machine Learning and Artificial Intelligence to Advance Earth System Science",
        "landing_url": "https://www.nationalacademies.org/publications/26566",
        "asset_url": "https://www.nationalacademies.org/read/26566/chapter/1",
        "axes": "AI for Science；科学体系与科研能力；科研数据与计算基础设施",
        "role": "AI进入地球系统科学所需的数据、模型、计算、跨学科团队与评价条件",
    },
    {
        "id": "C-EU-JRC-JRC138000",
        "kind": "pdf",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2024-01-01",
        "title": "Open access to JRC research infrastructures",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC138000",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC138000/JRC138000_01.pdf",
        "axes": "科学体系与科研能力；科技人才与技能；产业创新与成果转化",
        "role": "大型公共实验设施向外部研究人员和产业开放、形成协作与能力建设的五年运行证据",
    },
    {
        "id": "C-US-NASEM-27469",
        "kind": "nasem",
        "record_id": 27469,
        "institution_id": "us-nasem",
        "institution": "National Academies of Sciences, Engineering, and Medicine",
        "date": "2024-08-05",
        "title": "Artificial Intelligence and Automated Laboratories for Biotechnology: Leveraging Opportunities and Mitigating Risks",
        "landing_url": "https://www.nationalacademies.org/publications/27469",
        "asset_url": "https://www.nationalacademies.org/read/27469/chapter/1",
        "axes": "AI for Science；自动化实验室；生命科学与生物技术；科研治理",
        "role": "AI与自动化实验室重组生物技术研究流程、设施能力和创新扩散条件的近期节点",
    },
)

SOURCE_CATALOGS = (
    "77_OECD_STI正式系列轻量目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "206_NASEM科学技术创新政策近十年轻量总目录.csv",
)


def update_source_catalogs(root: Path, china_hits_by_id: dict[str, int]) -> None:
    for filename in SOURCE_CATALOGS:
        path = root / filename
        records, fields = read_csv(path)
        changed = False
        for row in records:
            rid = row.get("报告ID") or row.get("统一目录报告ID")
            if rid in china_hits_by_id:
                if "全文策略" in fields:
                    row["全文策略"] = "已进入AI for Science与公共科研基础设施定点全文；按官方全文、净文本和科技创新切片调用"
                if "中国直接信号" in fields and china_hits_by_id[rid] > 0:
                    row["中国直接信号"] = "是（全文词形定位；具体语义待编码）"
                changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded AI for Science and public research infrastructure evidence batch.")
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
    web_dir = root / "03_证据底稿" / "网页原文"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, web_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    first_pdf = next(item for item in SELECTED_ITEMS if item["kind"] == "pdf")
    opened = _proxy_json("/new?url=" + quote(first_pdf["landing_url"], safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = item["id"]
            pages_or_chapters = 0
            if item["kind"] == "pdf":
                source_path = pdf_dir / f"{rid}.pdf"
                if not source_path.exists() or not source_path.read_bytes().startswith(b"%PDF"):
                    source_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
                payload = source_path.read_bytes()
                if not payload.startswith(b"%PDF"):
                    raise RuntimeError(f"invalid official PDF: {rid}")
                text, pages_or_chapters = extract_pdf(source_path)
                asset_type = "官方PDF"
                source_status = "官方PDF已获取并校验"
                completeness = "官方PDF全文已保存；同时生成提取文本和科技创新切片"
                slice_text = make_slice(item, text)
            else:
                source_path = web_dir / f"{rid}.md"
                text_path = text_dir / f"{rid}.txt"
                if source_path.exists() and text_path.exists() and "collection-complete: chapter-probe-v2" in source_path.read_text(encoding="utf-8"):
                    archive = source_path.read_text(encoding="utf-8")
                    text = text_path.read_text(encoding="utf-8")
                    pages_or_chapters = count_archived_chapters(archive)
                else:
                    archive, text, pages_or_chapters = fetch_book_via_jina(item["record_id"], item["title"])
                archive = normalize_archive_whitespace(archive)
                text = normalize_archive_whitespace(text)
                source_path.write_text(archive, encoding="utf-8", newline="\n")
                payload = archive.encode("utf-8")
                asset_type = "官方逐章网页Markdown转写"
                source_status = "NASEM官方在线全文已逐章转换保存并校验；非原始PDF"
                completeness = "NASEM官方在线全文逐章经Jina转换并提取文本；精确引用回查官方章节与印刷页码"
                slice_text = selected_slice(item["title"], text)
            if len(text) < 1_000 or pages_or_chapters < 1:
                raise RuntimeError(f"extracted full text too short: {rid} units={pages_or_chapters} chars={len(text)}")
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            text_path.write_text(clean_text(text), encoding="utf-8", newline="\n")
            slice_path.write_text(slice_text, encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc") + lower.count("sino-")
            row = by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = completeness
            row["优先级"] = "P1-STI-mechanism-node"
            row["示踪问题"] = item["axes"]
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = item["role"]
            row["本地原始资产路径"] = str(source_path)
            row["原始资产状态"] = source_status
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
                "页数或章节数": str(pages_or_chapters),
                "字节数": str(len(payload)),
                "清洗文本字符数": str(len(text)),
                "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(payload).hexdigest(),
                "科技创新主轴": item["axes"],
                "科技创新复用角色": item["role"],
                "选择理由": "直接补充AI辅助科学发现、科研设施开放使用或公共科研基础设施评价机制；安全题名不构成选择依据",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} units={pages_or_chapters} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, fields)
    update_source_catalogs(root, {row["报告ID"]: int(row["China词形命中数"]) for row in ledger})
    write_csv(root / "222_AI_for_Science与公共科研基础设施定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或章节数", "字节数", "清洗文本字符数", "China词形命中数")}
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    web_count = len(ledger) - pdf_count
    (root / "223_AI_for_Science与公共科研基础设施定点增补结果.md").write_text(
        "# AI for Science与公共科研基础设施定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：OECD 2份、NASEM 2份、欧委会JRC 1份。\n"
        f"- 保存{pdf_count}份官方PDF和{web_count}份NASEM官方逐章网页全文，共{totals['页数或章节数']:,}页或章、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- China/Chinese/PRC/Sino-词形共命中{totals['China词形命中数']:,}次；仅用于定位中国比较段落。\n"
        "- 覆盖科研设施数字访问平台、科研设施科学与社会经济影响评价、AI辅助地球系统科学、JRC设施开放运行、AI与自动化生物实验室。\n"
        "- 军事、出口管制、供应链安全和一般AI治理材料未进入本批全文。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或章节数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
