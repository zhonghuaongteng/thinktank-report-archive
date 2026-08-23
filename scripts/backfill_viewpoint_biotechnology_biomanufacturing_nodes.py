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
    from scripts.backfill_viewpoint_mission_oriented_rd_nodes import fetch_wordpress_record
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from scripts.extend_viewpoint_fas_selected_fulltexts import clean_html
except ModuleNotFoundError:
    from backfill_viewpoint_china_research_system_nodes import (
        clean_text,
        download_pdf,
        extract_pdf,
        make_slice,
        read_csv,
        write_csv,
    )
    from backfill_viewpoint_mission_oriented_rd_nodes import fetch_wordpress_record
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from extend_viewpoint_fas_selected_fulltexts import clean_html


SERIES_ROLE = "生物技术生物制造创新机制与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-DE-ACATECH-2750",
        "kind": "pdf",
        "institution_id": "de-acatech",
        "institution": "acatech - National Academy of Science and Engineering",
        "date": "2017-04-05",
        "title": "Innovationspotenziale der Biotechnologie",
        "landing_url": "https://www.acatech.de/publikation/innovationspotenziale-der-biotechnologie/",
        "asset_url": "https://www.acatech.de/publikation/innovationspotenziale-der-biotechnologie/download-pdf?lang=de",
        "axes": "生物技术关键能力；组学与基因编辑；技术融合；科研条件；产业转化",
        "role": "识别组学、CRISPR、生物信息学和产业应用汇合的2017早期技术潜力节点",
    },
    {
        "id": "C-OECD-DOI-E2E3D8A1-EN",
        "kind": "pdf",
        "institution_id": "oecd-sti",
        "institution": "Organisation for Economic Co-operation and Development",
        "date": "2019-09-05",
        "title": "Innovation ecosystems in the bioeconomy",
        "landing_url": "https://www.oecd.org/en/publications/innovation-ecosystems-in-the-bioeconomy_e2e3d8a1-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/09/innovation-ecosystems-in-the-bioeconomy_b77a065a/e2e3d8a1-en.pdf",
        "axes": "生物经济创新生态；价值链；需求侧工具；中小企业；技术融合；中国科技横向维度",
        "role": "从国家案例比较创新生态、政策协同和生物炼制价值链的2019机制节点",
    },
    {
        "id": "C-FAS-2020-A-NATIONAL-BIOECONOMY-MANUFACTURING-AND-INNOVATION-INITIATIVE",
        "kind": "wordpress",
        "wp_id": 17015,
        "institution_id": "fas",
        "institution": "Federation of American Scientists",
        "date": "2020-12-16",
        "title": "A National Bioeconomy Manufacturing and Innovation Initiative",
        "landing_url": "https://fas.org/publication/a-national-bioeconomy-manufacturing-and-innovation-initiative/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/17015?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "生物制造；公共研发组织；制造创新机构；技术规模化；人才；成果转化",
        "role": "将生物技术研发连接制造创新机构、规模化设施和劳动力建设的2020组织节点",
    },
    {
        "id": "C-FAS-2023-PROJECT-BOOST-A-BIOMANUFACTURING-TEST-FACILITY-NETWORK-FOR-BIOPROCESS-OPTIMIZATION-SCALING-AND-TRAINING",
        "kind": "wordpress",
        "wp_id": 17257,
        "institution_id": "fas",
        "institution": "Federation of American Scientists",
        "date": "2023-01-23",
        "title": "Project BOoST: A Biomanufacturing Test Facility Network for Bioprocess Optimization, Scaling, and Training",
        "landing_url": "https://fas.org/publication/project-boost-a-biomanufacturing-test-facility-network-for-bioprocess-optimization-scaling-and-training/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/17257?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "生物工艺优化；中试放大；测试设施网络；制造成熟度；创业与人才",
        "role": "以共享测试设施、工艺优化和制造成熟度解决生物制造放大瓶颈的2023项目设计节点",
    },
    {
        "id": "C-EU-JRC-JRC139154",
        "kind": "pdf",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01",
        "title": "Innovation trends in industrial biotechnology: a patent landscape analysis",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC139154",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC139154/JRC139154_01.pdf",
        "axes": "工业生物技术；专利格局；创新热点；机构类型；技术领域；中国科技横向维度",
        "role": "用2015—2020专利数据比较工业生物技术热点、创新主体和中国位置的2025测量节点",
    },
    {
        "id": "C-OECD-DOI-3E6510CF-EN",
        "kind": "pdf",
        "institution_id": "oecd-sti",
        "institution": "Organisation for Economic Co-operation and Development",
        "date": "2025-02-24",
        "title": "Synthetic biology in focus",
        "landing_url": "https://www.oecd.org/en/publications/synthetic-biology-in-focus_3e6510cf-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/02/synthetic-biology-in-focus_42893a6a/3e6510cf-en.pdf",
        "axes": "合成生物学；AI自动化融合；分布式制造；创新生态；研发融资；科技人才",
        "role": "连接合成生物学技术路线、AI与自动化融合、创新生态和规模化政策的2025前瞻节点",
    },
)

SOURCE_CATALOGS = (
    "77_OECD_STI正式系列轻量目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "202_acatech科学与技术创新正式成果轻量总目录.csv",
)


def update_source_catalogs(root: Path, selected_ids: set[str]) -> None:
    for filename in SOURCE_CATALOGS:
        path = root / filename
        records, fields = read_csv(path)
        changed = False
        for row in records:
            rid = row.get("统一目录报告ID") or row.get("报告ID")
            if rid not in selected_ids or "全文策略" not in fields:
                continue
            row["全文策略"] = "已进入生物技术与生物制造创新定点全文；按官方原始资产、净文本和科技创新切片调用"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded biotechnology and biomanufacturing innovation evidence batch.")
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

    opened = _proxy_json("/new?url=" + quote(SELECTED_ITEMS[0]["landing_url"], safe=""))
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
                text, units = extract_pdf(source_path)
                asset_type = "官方PDF"
                status = "官方PDF已获取并校验；已生成可检索文本和科技创新切片"
            else:
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
                "本地路径": str(text_path),
                "正文完整度": "官方全文已保存；同时生成可检索文本和科技创新切片",
                "优先级": "P0-China-STI-node" if china_hits else "P1-STI-biotech-node",
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
                "选择理由": "补充生物技术、生物制造、创新生态、试验设施和中国能力比较；生物安全未作为选择条件",
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
    write_csv(root / "238_生物技术生物制造创新机制与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "239_生物技术生物制造创新机制与中国比较定点增补结果.md").write_text(
        "# 生物技术、生物制造创新机制与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点保存{len(ledger)}份正式材料，覆盖acatech、OECD、FAS与JRC，形成2017—2025跨期节点。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger)-pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；只用于定位中国科研、专利和产业能力比较段落。\n"
        "- 技术机制覆盖组学、基因编辑、合成生物学、AI与自动化融合、工业生物技术专利和生物工艺放大；政策机制覆盖创新生态、制造创新机构、共享测试设施、研发融资、人才和成果转化。\n"
        "- 本批未纳入生物安全、军事应用或一般药品价格政策主导材料；相关表述仅在直接解释研发和创新机制时调用。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
