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


SERIES_ROLE = "基础研究资助科研评价与创新联系定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-JRC-JRC101043",
        "kind": "pdf",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2016-01-01",
        "title": "Research Performance Based Funding Systems: a Comparative Assessment",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC101043",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC101043/kj1a27837enn.pdf",
        "axes": "科学体系与科研能力；研发投入与创新政策；科研评价",
        "role": "绩效拨款如何改变公共科研组织激励、资源集中和评价副作用的早期比较节点",
    },
    {
        "id": "C-NSF-NSB-SEI-2018",
        "kind": "pdf",
        "institution_id": "nsf-nsb-sei",
        "institution": "National Science Board / National Center for Science and Engineering Statistics",
        "date": "2018-01-01",
        "title": "Science and Engineering Indicators 2018",
        "landing_url": "https://ncses.nsf.gov/statistics/2018/nsb20181/",
        "asset_url": "https://ncses.nsf.gov/pubs/nsb20181/assets/nsb20181.pdf",
        "axes": "科学体系与基础研究；研发投入；科技人才；知识产出；产业创新；中国科技横向维度",
        "role": "全球科研投入、人才、论文、专利和知识密集产业结构及中国位置的2018统计节点",
    },
    {
        "id": "C-DE-EFI-2020-A2",
        "kind": "pdf",
        "institution_id": "de-efi",
        "institution": "Commission of Experts for Research and Innovation (EFI)",
        "date": "2020-01-01",
        "title": "Science policy",
        "landing_url": "https://www.e-fi.de/en/publications/reports/thematic-overview",
        "asset_url": "https://www.e-fi.de/fileadmin/Assets/Themenverzeichnis/Inhaltskapitel_EN_2020/EFI_Report_2020_A2.pdf",
        "axes": "科学体系与科研能力；研发投入与创新政策；科研组织",
        "role": "德国大学与非大学科研机构、卓越计划和长期科研协议的2020政策节点",
    },
    {
        "id": "C-NSF-NSB-SEI-2022",
        "kind": "pdf",
        "institution_id": "nsf-nsb-sei",
        "institution": "National Science Board / National Center for Science and Engineering Statistics",
        "date": "2022-01-18",
        "title": "The State of U.S. Science and Engineering 2022",
        "landing_url": "https://ncses.nsf.gov/pubs/nsb20221",
        "asset_url": "https://ncses.nsf.gov/pubs/nsb20221/assets/nsb20221.pdf",
        "axes": "科学体系与基础研究；研发投入；科技人才；知识产出；产业创新；中国科技横向维度",
        "role": "疫情后美国与全球科研能力、知识产出、创新活动及中国位置的2022综合节点",
    },
    {
        "id": "C-JP-RIETI-23-E-015",
        "kind": "pdf",
        "institution_id": "jp-rieti",
        "institution": "Research Institute of Economy, Trade and Industry (RIETI)",
        "date": "2023-03-01",
        "title": "Measuring Science and Innovation Linkage Using Text Mining of Research Papers and Patent Information",
        "landing_url": "https://www.rieti.go.jp/en/publications/summary/23030005.html",
        "asset_url": "https://www.rieti.go.jp/jp/publications/dp/23e015.pdf",
        "axes": "科学体系与科研能力；产业创新与成果转化；创新测量与政策方法",
        "role": "利用论文与专利文本识别科学知识进入技术创新的测量方法节点",
    },
    {
        "id": "C-US-NASEM-27244",
        "kind": "nasem",
        "record_id": 27244,
        "institution_id": "us-nasem",
        "institution": "National Academies of Sciences, Engineering, and Medicine",
        "date": "2024-03-07",
        "title": "Experimental Approaches to Improving Research Funding Programs",
        "landing_url": "https://www.nationalacademies.org/publications/27244",
        "asset_url": "https://www.nationalacademies.org/read/27244/chapter/1",
        "axes": "科学体系与基础研究；创新政策与研发治理；科研资助评价",
        "role": "用随机试验和制度实验改进科研资助项目设计、同行评审与政策学习的近期节点",
    },
)

SOURCE_CATALOGS = (
    "130_NSF_NSB科学与工程指标近十年轻量目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "190_德国EFI研究创新近十年轻量总目录.csv",
    "194_RIETI科技创新与中国近十年轻量总目录.csv",
    "206_NASEM科学技术创新政策近十年轻量总目录.csv",
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
                row["全文策略"] = "已进入基础研究资助、科研评价与创新联系定点全文；按官方全文、净文本和科技创新切片调用"
            if "中国直接信号" in fields and china_hits_by_id[rid] > 0:
                row["中国直接信号"] = "是（全文词形定位；具体语义待编码）"
            if "中国关联" in fields and china_hits_by_id[rid] > 0:
                row["中国关联"] = "是；全文词形定位，具体比较口径待编码"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded research-funding and evaluation evidence batch.")
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
            if item["kind"] == "pdf":
                source_path = pdf_dir / f"{rid}.pdf"
                if not source_path.exists() or not source_path.read_bytes().startswith(b"%PDF"):
                    source_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
                payload = source_path.read_bytes()
                if not payload.startswith(b"%PDF"):
                    raise RuntimeError(f"invalid official PDF: {rid}")
                text, units = extract_pdf(source_path)
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
                    units = count_archived_chapters(archive)
                else:
                    archive, text, units = fetch_book_via_jina(item["record_id"], item["title"])
                archive = normalize_archive_whitespace(archive)
                text = normalize_archive_whitespace(text)
                source_path.write_text(archive, encoding="utf-8", newline="\n")
                payload = archive.encode("utf-8")
                asset_type = "官方逐章网页Markdown转写"
                source_status = "NASEM官方在线全文已逐章转换保存并校验；非原始PDF"
                completeness = "NASEM官方在线全文逐章经Jina转换并提取文本；精确引用回查官方章节与印刷页码"
                slice_text = selected_slice(item["title"], text)
            if len(text) < 1_000 or units < 1:
                raise RuntimeError(f"extracted full text too short: {rid} units={units} chars={len(text)}")
            clean = clean_text(text)
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            text_path.write_text(clean, encoding="utf-8", newline="\n")
            slice_path.write_text(slice_text, encoding="utf-8", newline="\n")
            lower = clean.lower()
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
                "页数或章节数": str(units),
                "字节数": str(len(payload)),
                "清洗文本字符数": str(len(clean)),
                "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(payload).hexdigest(),
                "科技创新主轴": item["axes"],
                "科技创新复用角色": item["role"],
                "选择理由": "补充基础研究投入、科研绩效评价、知识产出与创新转化测量机制；安全题名不构成选择依据",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} units={units} chars={len(clean)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, fields)
    update_source_catalogs(root, {row["报告ID"]: int(row["China词形命中数"]) for row in ledger})
    write_csv(root / "226_基础研究资助科研评价与创新联系定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或章节数", "字节数", "清洗文本字符数", "China词形命中数")}
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    web_count = len(ledger) - pdf_count
    (root / "227_基础研究资助科研评价与创新联系定点增补结果.md").write_text(
        "# 基础研究资助、科研评价与创新联系定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：NSF/NSB 2份，JRC、EFI、RIETI、NASEM各1份。\n"
        f"- 保存{pdf_count}份官方PDF和{web_count}份NASEM官方逐章网页全文，共{totals['页数或章节数']:,}页或章、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- China/Chinese/PRC/Sino-词形共命中{totals['China词形命中数']:,}次；仅用于定位全球科技指标中的中国比较段落。\n"
        "- 覆盖科研绩效拨款、全球科学与工程指标、科学政策、论文—专利知识联系和科研资助制度实验。\n"
        "- 未新增安全类目录；全文选择由基础研究投入、科研评价和创新转化机制触发。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或章节数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
