from __future__ import annotations

import argparse
import hashlib
from datetime import date
from pathlib import Path
from urllib.parse import quote

try:
    from scripts.backfill_viewpoint_china_research_system_nodes import (
        clean_text, download_pdf, extract_pdf, make_slice, read_csv, write_csv,
    )
    from scripts.backfill_viewpoint_mission_oriented_rd_nodes import fetch_wordpress_record
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from scripts.extend_viewpoint_fas_selected_fulltexts import clean_html
    from scripts.extend_viewpoint_itif_selected_fulltexts import fetch_markdown
except ModuleNotFoundError:
    from backfill_viewpoint_china_research_system_nodes import (
        clean_text, download_pdf, extract_pdf, make_slice, read_csv, write_csv,
    )
    from backfill_viewpoint_mission_oriented_rd_nodes import fetch_wordpress_record
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from extend_viewpoint_fas_selected_fulltexts import clean_html
    from extend_viewpoint_itif_selected_fulltexts import fetch_markdown


SERIES_ROLE = "先进计算科研算力基础设施与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-ITIF-RB-2016-VITAL-IMPORTANCE-HIGH-PERFORMANCE-COMPUTING-US-COMPETITIVENESS",
        "kind": "itif", "institution_id": "itif", "institution": "Information Technology and Innovation Foundation",
        "date": "2016-04-28", "title": "The Vital Importance of High-Performance Computing to U.S. Competitiveness",
        "landing_url": "https://itif.org/publications/2016/04/28/vital-importance-high-performance-computing-us-competitiveness/",
        "asset_url": "https://itif.org/publications/2016/04/28/vital-importance-high-performance-computing-us-competitiveness/.md",
        "axes": "高性能计算；科研领导力；产业竞争力；软硬件生态；人才；中国科技横向维度",
        "role": "把高性能计算界定为科学发现与产业创新共同基础设施的2016基线节点",
    },
    {
        "id": "C-US-OSTP-2019-NATIONAL-STRATEGIC-COMPUTING-INITIATIVE-UPDATE-2019",
        "kind": "pdf", "institution_id": "us-ostp",
        "institution": "White House Office of Science and Technology Policy / National Science and Technology Council",
        "date": "2019-11-14", "title": "National Strategic Computing Initiative Update 2019",
        "landing_url": "https://trumpwhitehouse.archives.gov/ostp/documents-and-reports/",
        "asset_url": "https://trumpwhitehouse.archives.gov/wp-content/uploads/2019/11/National-Strategic-Computing-Initiative-Update-2019.pdf",
        "axes": "战略计算；联邦研发；高性能计算；数据密集型科学；跨机构协调；中国科技横向维度",
        "role": "观察战略计算从极限性能扩展到数据、软件、网络和人才生态的2019政策节点",
    },
    {
        "id": "C-US-OSTP-2020-RECOMMENDATIONS-CLOUD-AI-RD-NOV2020",
        "kind": "pdf", "institution_id": "us-ostp",
        "institution": "White House Office of Science and Technology Policy / National Science and Technology Council",
        "date": "2020-11-17", "title": "Recommendations for Leveraging Cloud Computing Resources for Federally Funded Artificial Intelligence Research and Development",
        "landing_url": "https://trumpwhitehouse.archives.gov/ostp/documents-and-reports/",
        "asset_url": "https://trumpwhitehouse.archives.gov/wp-content/uploads/2020/11/Recommendations-Cloud-AI-RD-Nov2020.pdf",
        "axes": "云计算；AI研发；科研算力可及性；公共资助；数据与软件；人才",
        "role": "把商业云资源纳入公共资助AI研究条件的2020科研算力可及性节点",
    },
    {
        "id": "C-US-OSTP-2020-FUTURE-ADVANCED-COMPUTING-ECOSYSTEM-STRATEGIC-PLAN-NOV-2020",
        "kind": "pdf", "institution_id": "us-ostp",
        "institution": "White House Office of Science and Technology Policy / National Science and Technology Council",
        "date": "2020-11-18", "title": "Pioneering the Future Advanced Computing Ecosystem Strategic Plan",
        "landing_url": "https://trumpwhitehouse.archives.gov/ostp/documents-and-reports/",
        "asset_url": "https://trumpwhitehouse.archives.gov/wp-content/uploads/2020/11/Future-Advanced-Computing-Ecosystem-Strategic-Plan-Nov-2020.pdf",
        "axes": "先进计算生态；硬件架构；软件与算法；网络；研发治理；人才",
        "role": "以全栈生态而非单一峰值性能组织先进计算战略的2020转向节点",
    },
    {
        "id": "C-FAS-2021-AN-INSTITUTE-FOR-SCALABLE-HETEROGENEOUS-COMPUTING", "kind": "wordpress", "wp_id": 16832,
        "institution_id": "fas", "institution": "Federation of American Scientists", "date": "2021-07-16",
        "title": "An Institute for Scalable Heterogeneous Computing",
        "landing_url": "https://fas.org/publication/an-institute-for-scalable-heterogeneous-computing/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/16832?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "异构计算；先进封装；制造创新机构；共享研发设施；产业协作；人才",
        "role": "以制造创新机构连接芯片、封装、系统和应用研发的2021组织机制节点",
    },
    {
        "id": "C-ITIF-RB-2022-HIGH-PERFORMANCE-COMPUTING-LEADERSHIP-IN-AN-EXASCALE-ERA",
        "kind": "itif", "institution_id": "itif", "institution": "Information Technology and Innovation Foundation",
        "date": "2022-09-12", "title": "A New Frontier: Sustaining U.S. High-Performance Computing Leadership in an Exascale Era",
        "landing_url": "https://itif.org/publications/2022/09/12/high-performance-computing-leadership-in-an-exascale-era/",
        "asset_url": "https://itif.org/publications/2022/09/12/high-performance-computing-leadership-in-an-exascale-era/.md",
        "axes": "百亿亿次计算；科研应用；基础设施投资；软件生态；技能；中国科技横向维度",
        "role": "从设备领先转向应用、基础设施、软件和技能持续投入的2022百亿亿次计算节点",
    },
)

SOURCE_CATALOGS = (
    "88_美国OSTP科学技术创新政策轻量目录.csv",
    "170_ITIF正式报告与简报近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv",
)


def update_source_catalogs(root: Path, selected_ids: set[str]) -> None:
    for filename in SOURCE_CATALOGS:
        records, fields = read_csv(root / filename)
        changed = False
        for row in records:
            rid = row.get("统一目录报告ID") or row.get("报告ID")
            if rid not in selected_ids or "全文策略" not in fields:
                continue
            row["全文策略"] = "已进入先进计算科研算力基础设施定点全文；按官方原始资产、净文本和科技创新切片调用"
            changed = True
        if changed:
            write_csv(root / filename, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded advanced-computing infrastructure evidence batch.")
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
            kind = item["kind"]
            if kind == "pdf":
                source_path = pdf_dir / f"{rid}.pdf"
                if not source_path.exists() or not source_path.read_bytes().startswith(b"%PDF"):
                    source_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
                payload = source_path.read_bytes()
                text, units = extract_pdf(source_path)
                asset_type = "官方PDF"
                status = "官方PDF已获取并校验；已生成可检索文本和科技创新切片"
            elif kind == "wordpress":
                source_path = web_dir / f"{rid}.html"
                response = fetch_wordpress_record(item["asset_url"], item["wp_id"])
                content = response.get("content") or {}
                content_html = str(content.get("rendered", "")) if isinstance(content, dict) else str(content)
                content_html = "\n".join(line.rstrip() for line in content_html.splitlines()).strip() + "\n"
                source_path.write_text(content_html, encoding="utf-8", newline="\n")
                payload = source_path.read_bytes()
                text, units = clean_html(content_html), 1
                asset_type = "官方WordPress网页正文"
                status = "官方WordPress正文已获取并校验；已生成可检索文本和科技创新切片"
            else:
                source_path = web_dir / f"{rid}.md"
                content = fetch_markdown(item["asset_url"])
                source_path.write_text(content, encoding="utf-8", newline="\n")
                payload = source_path.read_bytes()
                text, units = content, 1
                asset_type = "ITIF官方Markdown全文"
                status = "ITIF官方Markdown全文已获取并校验；已生成可检索文本和科技创新切片"
            clean = clean_text(text)
            if len(clean) < 1_000 or units < 1:
                raise RuntimeError(f"extracted full text too short: {rid} units={units} chars={len(clean)}")
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            text_path.write_text(clean, encoding="utf-8", newline="\n")
            slice_path.write_text(make_slice(item, clean), encoding="utf-8", newline="\n")
            lower = clean.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc") + lower.count("sino-")
            by_id[rid].update({
                "本地路径": str(text_path), "正文完整度": "官方全文已保存；同时生成可检索文本和科技创新切片",
                "优先级": "P0-China-STI-node" if china_hits else "P1-STI-computing-node", "示踪问题": item["axes"],
                "样本角色": SERIES_ROLE, "编码状态": "全文待观点编码", "预期用途": item["role"],
                "本地原始资产路径": str(source_path), "原始资产状态": status,
            })
            ledger.append({
                "报告ID": rid, "机构ID": item["institution_id"], "机构": item["institution"], "发布日期": item["date"],
                "报告名称": item["title"], "官方落地页": item["landing_url"], "官方全文入口": item["asset_url"],
                "资产类型": asset_type, "本地原始资产": str(source_path), "本地文本": str(text_path), "本地切片": str(slice_path),
                "页数或网页数": str(units), "字节数": str(len(payload)), "清洗文本字符数": str(len(clean)),
                "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(payload).hexdigest(),
                "科技创新主轴": item["axes"], "科技创新复用角色": item["role"],
                "选择理由": "补充先进计算、科研算力可及性、全栈生态、异构计算和中国比较；出口管制与军事应用未作为选择条件",
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
    write_csv(root / "242_先进计算科研算力基础设施与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "243_先进计算科研算力基础设施与中国比较定点增补结果.md").write_text(
        "# 先进计算科研算力基础设施与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点保存{len(ledger)}份正式材料，覆盖ITIF、OSTP/NSTC与FAS，形成2016—2022跨期节点。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger)-pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；只用于定位中国先进计算能力和创新生态比较段落。\n"
        "- 技术机制覆盖高性能与百亿亿次计算、云计算、异构计算、先进封装、软件算法和网络；政策机制覆盖跨机构研发、科研算力可及性、制造创新机构、基础设施投资和技能。\n"
        "- 本批未纳入出口管制、军事计算或一般云治理材料；相关表述仅在直接解释研发能力与创新生态时调用。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
