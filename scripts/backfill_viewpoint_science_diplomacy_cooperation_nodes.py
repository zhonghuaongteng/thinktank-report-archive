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
        fetch_jina_markdown,
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
        fetch_jina_markdown,
        normalize_archive_whitespace,
        selected_slice,
    )


SERIES_ROLE = "科学外交、开放科研合作与中国参与机制定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-US-OSTP-2016-IWGODSP-PRINCIPLES-0",
        "kind": "pdf",
        "institution_id": "us-ostp",
        "institution": "White House Office of Science and Technology Policy",
        "date": "2016-01-01",
        "title": "Principles for Promoting Access to Federal Government-Supported Scientific Data and Research Findings through International Scientific Cooperation",
        "landing_url": "https://obamawhitehouse.archives.gov/node/10054/",
        "asset_url": "https://obamawhitehouse.archives.gov/sites/default/files/microsites/ostp/NSTC/iwgodsp_principles_0.pdf",
        "axes": "科学体系与基础研究；科研数据开放；国际科研合作",
        "role": "政府资助科研数据与研究成果通过国际合作扩大开放获取的制度基线",
    },
    {
        "id": "C-US-NASEM-25015",
        "kind": "nasem",
        "record_id": 25015,
        "institution_id": "us-nasem",
        "institution": "National Academies of Sciences, Engineering, and Medicine",
        "date": "2018-02-05",
        "title": "International Coordination for Science Data Infrastructure",
        "landing_url": "https://www.nationalacademies.org/publications/25015",
        "asset_url": "https://www.nationalacademies.org/read/25015/chapter/1",
        "axes": "科学体系与基础研究；科研数据基础设施；国际科研合作",
        "role": "跨国科研数据基础设施的互操作、治理、资助与长期协调机制节点",
    },
    {
        "id": "C-US-NASEM-26182",
        "kind": "nasem",
        "record_id": 26182,
        "institution_id": "us-nasem",
        "institution": "National Academies of Sciences, Engineering, and Medicine",
        "date": "2021-05-14",
        "title": "Science Diplomacy to Promote and Strengthen Basic Research and International Cooperation",
        "landing_url": "https://www.nationalacademies.org/publications/26182",
        "asset_url": "https://www.nationalacademies.org/read/26182/chapter/1",
        "axes": "科学体系与基础研究；科学外交；国际科研合作",
        "role": "科学外交如何连接基础研究资助、研究网络与跨国合作的中期机制节点",
    },
    {
        "id": "C-UK-RS-2023-WHY-THE-UK-NEEDS-A-COMPREHENSIVE-INTERNATION-ACB0B5",
        "kind": "jina",
        "institution_id": "uk-royal-society",
        "institution": "The Royal Society",
        "date": "2023-12-05",
        "title": "Why the UK needs a comprehensive international science strategy",
        "landing_url": "https://royalsociety.org/news-resources/publications/2023/uk-international-science-strategy/",
        "asset_url": "https://royalsociety.org/-/media/policy/publications/2023/uk_international_science_strategy.pdf",
        "axes": "科学体系与基础研究；科技人才与科研组织；国际科研合作；中国科技横向维度",
        "role": "英国以人才、设施、欧盟框架计划和对华科研联系组织国际科学战略的近期节点",
    },
    {
        "id": "C-US-OSTP-2024-2024-BIENNIAL-REPORT-TO-CONGRESS-ON-INTERNATIONAL-SCIENCE-TECHNOLOGY-COOPERATION",
        "kind": "pdf",
        "institution_id": "us-ostp",
        "institution": "White House Office of Science and Technology Policy",
        "date": "2024-02-01",
        "title": "Biennial Report to Congress on International Science & Technology Cooperation",
        "landing_url": "https://bidenwhitehouse.archives.gov/ostp/",
        "asset_url": "https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/02/2024-Biennial-Report-to-Congress-on-International-Science-Technology-Cooperation.pdf",
        "axes": "科学体系与基础研究；关键与新兴技术；国际科研合作；中国科技横向维度",
        "role": "美国政府国际科技合作组合、伙伴网络及对华合作安排的近期官方盘点节点",
    },
)

SOURCE_CATALOGS = (
    "88_美国OSTP科学技术创新政策轻量目录.csv",
    "198_英国皇家学会科学技术创新专题轻量总目录.csv",
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
                row["全文策略"] = "已进入科学外交、开放科研合作与中国参与机制定点全文；按官方全文、净文本和科技创新切片调用"
            if "中国直接信号" in fields and china_hits_by_id[rid] > 0:
                row["中国直接信号"] = "是（全文词形定位；具体语义待编码）"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded science diplomacy and international research cooperation batch.")
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
            elif item["kind"] == "nasem":
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
            else:
                source_path = web_dir / f"{rid}.md"
                archive = fetch_jina_markdown(item["asset_url"])
                archive = normalize_archive_whitespace(archive)
                text = archive
                units = 1
                source_path.write_text(archive, encoding="utf-8", newline="\n")
                payload = archive.encode("utf-8")
                asset_type = "官方PDF的Markdown转写"
                source_status = "官方PDF入口已核验；站点拒绝自动下载原始PDF，已保存全文转写"
                completeness = "官方PDF全文经Jina转换保存；精确引用回查官方PDF页码"
                slice_text = make_slice(item, text)
            if len(text) < 1_000 or units < 1:
                raise RuntimeError(f"extracted full text too short: {rid} units={units} chars={len(text)}")
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            clean = clean_text(text)
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
                "选择理由": "补充科研开放、跨国科研基础设施和科技合作机制；仅在解释创新体系时保留中国及安全相关段落",
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
    write_csv(root / "224_科学外交开放科研合作与中国参与机制定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或章节数", "字节数", "清洗文本字符数", "China词形命中数")}
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    web_count = len(ledger) - pdf_count
    (root / "225_科学外交开放科研合作与中国参与机制定点增补结果.md").write_text(
        "# 科学外交、开放科研合作与中国参与机制定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：OSTP 2份、NASEM 2份、英国皇家学会1份。\n"
        f"- 保存{pdf_count}份官方PDF、2份NASEM官方逐章网页全文和1份英国皇家学会官方PDF全文转写，共{totals['页数或章节数']:,}页或章、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- China/Chinese/PRC/Sino-词形共命中{totals['China词形命中数']:,}次；仅用于定位中国参与和比较段落。\n"
        "- 覆盖科研数据开放、跨国科研数据基础设施、基础研究科学外交、英国国际科学战略和美国国际科技合作组合。\n"
        "- 未扩展安全类目录；安全内容仅在直接解释科研合作边界时保留。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或章节数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
