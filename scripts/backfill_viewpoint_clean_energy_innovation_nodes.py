from __future__ import annotations

import argparse
import hashlib
from datetime import date
from pathlib import Path
from urllib.parse import quote

try:
    from scripts.backfill_viewpoint_china_research_system_nodes import clean_text, download_pdf, extract_pdf, make_slice, read_csv, write_csv
    from scripts.backfill_viewpoint_mission_oriented_rd_nodes import fetch_wordpress_record
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from scripts.extend_viewpoint_fas_selected_fulltexts import clean_html
    from scripts.extend_viewpoint_itif_selected_fulltexts import fetch_markdown
except ModuleNotFoundError:
    from backfill_viewpoint_china_research_system_nodes import clean_text, download_pdf, extract_pdf, make_slice, read_csv, write_csv
    from backfill_viewpoint_mission_oriented_rd_nodes import fetch_wordpress_record
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from extend_viewpoint_fas_selected_fulltexts import clean_html
    from extend_viewpoint_itif_selected_fulltexts import fetch_markdown


SERIES_ROLE = "清洁能源技术路线创新政策与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-OECD-DOI-F0BB5D8C-EN", "kind": "pdf", "institution_id": "oecd-sti", "institution": "Organisation for Economic Co-operation and Development",
        "date": "2022-02-23", "title": "Innovation and industrial policies for green hydrogen",
        "landing_url": "https://www.oecd.org/en/publications/innovation-and-industrial-policies-for-green-hydrogen_f0bb5d8c-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/02/innovation-and-industrial-policies-for-green-hydrogen_4cfdd6bd/f0bb5d8c-en.pdf",
        "axes": "绿色氢能；电解槽研发与示范；创新与产业政策；标准和基础设施",
        "role": "从研发示范、成本差距、标准和基础设施解释绿色氢能规模化的2022政策机制节点",
    },
    {
        "id": "C-EU-JRC-JRC144141", "kind": "pdf", "institution_id": "eu-jrc", "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01", "title": "Clean Energy Technology Observatory: Photovoltaics in the European Union - 2025 Status Report on Technology Development, Trends, Value Chains and Markets",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC144141",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC144141/JRC144141_01.pdf",
        "axes": "光伏技术路线；效率与成本；研发创新；制造转化；中国科技横向维度",
        "role": "以效率、成本、专利创新与中国制造能力连接光伏技术和产业化的2025节点",
    },
    {
        "id": "C-EU-JRC-JRC144142", "kind": "pdf", "institution_id": "eu-jrc", "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01", "title": "Clean Energy Technology Observatory: Carbon Capture, Utilisation and Storage in the European Union - 2025 Status Report on Technology Development, Trends, Value Chains and Markets",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC144142",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC144142/JRC144142_01.pdf",
        "axes": "碳捕集利用封存；技术成熟度；科研与专利；研发投入；中国科技横向维度",
        "role": "比较CCUS技术成熟度、科研产出、专利和研发投资的2025技术路线节点",
    },
    {
        "id": "C-EU-JRC-JRC144653", "kind": "pdf", "institution_id": "eu-jrc", "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01", "title": "Clean Energy Technology Observatory: Nuclear Power in the European Union - 2025 Status Report on Technology Development, Trends, Value Chains and Markets",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC144653",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC144653/JRC144653_01.pdf",
        "axes": "核能技术；小型模块化反应堆；研发融资；科技人才；中国科技横向维度",
        "role": "比较核电机组、先进反应堆融资、人才和中国扩张速度的2025技术产业节点",
    },
    {
        "id": "C-ITIF-RB-2025-TIME-RESET-CLEAN-ENERGY-POLICY-FOCUSING-PRICE-PERFORMANCE-PARITY-P3", "kind": "markdown", "institution_id": "itif", "institution": "Information Technology and Innovation Foundation",
        "date": "2025-01-27", "title": "Mend It, Don’t End It: It’s Time to Reset Clean Energy Policy by Focusing on Price/Performance Parity (P3)",
        "landing_url": "https://itif.org/publications/2025/01/27/time-reset-clean-energy-policy-focusing-price-performance-parity-p3/",
        "asset_url": "https://itif.org/publications/2025/01/27/time-reset-clean-energy-policy-focusing-price-performance-parity-p3.md",
        "axes": "清洁能源创新；价格性能平价；研发示范；技术采用；政策组合",
        "role": "以价格性能平价重构研发、示范和市场采用关系的2025政策转向节点",
    },
    {
        "id": "C-FAS-2026-PROGRAM-DESIGN-FOR-A-CLEAN-ENERGY-FUTURE", "kind": "wordpress", "wp_id": 40988, "institution_id": "fas", "institution": "Federation of American Scientists",
        "date": "2026-01-26", "title": "DOE 4.0: Rethinking Program Design for a Clean Energy Future",
        "landing_url": "https://fas.org/publication/program-design-for-a-clean-energy-future/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/40988?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "清洁能源研发；项目设计；技术示范；创新机构；成果转化",
        "role": "将能源技术项目从拨款管理转向阶段化验证、用户需求和成果转化的2026组织机制节点",
    },
)

SOURCE_CATALOGS = (
    "77_OECD_STI正式系列轻量目录.csv",
    "170_ITIF正式报告与简报近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
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
            row["全文策略"] = "已进入清洁能源技术路线与创新政策定点全文；按官方原始资产、净文本和科技创新切片调用"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded clean-energy technology and innovation-policy evidence batch.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog, fields = read_csv(root / "05_报告总目录.csv")
    by_id = {row["报告ID"]: row for row in catalog}
    ids = {item["id"] for item in SELECTED_ITEMS}
    if missing := ids - set(by_id):
        raise RuntimeError(f"selected reports missing from catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        row = by_id[item["id"]]
        if row["发布日期"] != item["date"] or row["报告名称"] != item["title"]:
            raise RuntimeError(f"selected metadata drift: {item['id']}")
        if (row.get("本地原始资产路径") or row.get("本地路径")) and row.get("样本角色") != SERIES_ROLE:
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
            if item["kind"] == "pdf":
                source_path = pdf_dir / f"{rid}.pdf"
                if not source_path.exists() or not source_path.read_bytes().startswith(b"%PDF"):
                    source_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
                payload = source_path.read_bytes()
                text, units = extract_pdf(source_path)
                asset_type = "官方PDF"
                status = "官方PDF已获取并校验；已生成可检索文本和科技创新切片"
            elif item["kind"] == "markdown":
                source_path = web_dir / f"{rid}.md"
                content = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else fetch_markdown(item["asset_url"])
                source_path.write_text(content, encoding="utf-8", newline="\n")
                payload = content.encode("utf-8")
                text, units = content, 1
                asset_type = "官方Markdown网页正文"
                status = "官方Markdown正文已获取并校验；已生成可检索文本和科技创新切片"
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
            row = by_id[rid]
            row.update({
                "本地路径": str(text_path), "正文完整度": "官方全文已保存；同时生成可检索文本和科技创新切片",
                "优先级": "P0-China-STI-node" if china_hits else "P1-STI-energy-node", "示踪问题": item["axes"],
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
                "选择理由": "补充清洁能源具体技术路线、研发示范、创新政策与中国能力比较；安全议题未作为选择条件",
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
    update_source_catalogs(root, ids)
    write_csv(root / "236_清洁能源技术路线创新政策与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "237_清洁能源技术路线创新政策与中国比较定点增补结果.md").write_text(
        "# 清洁能源技术路线、创新政策与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点保存{len(ledger)}份正式材料，覆盖JRC、OECD、ITIF与FAS。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger)-pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；用于定位中国科研、技术和产业能力比较段落。\n"
        "- 技术对象覆盖绿色氢能、光伏、CCUS与核能；政策机制覆盖研发示范、价格性能平价、标准基础设施、项目设计和成果转化。\n"
        "- 本批未纳入能源安全、供应链韧性或地缘竞争主导材料；涉及竞争的段落仅在直接解释技术创新能力时调用。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
