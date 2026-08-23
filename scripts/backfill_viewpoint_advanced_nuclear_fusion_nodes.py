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


SERIES_ROLE = "先进核能聚变技术创新与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-JRC-JRC116292", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2019-01-01",
        "title": "Materials for Sustainable Nuclear Energy - The Strategic Research Agenda (SRA) of the Joint Programme on Nuclear Materials (JPNM) of the European Energy Research Alliance (EERA)",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC116292",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC116292/materials_for_sustainable_nuclear_energy_-_sra_of_the_eera-jpnm_-_web_identif.pdf",
        "axes": "先进核材料；第四代核能；材料建模；试验设施；数据共享；国际科研合作；中国科技横向维度",
        "role": "以材料寿命、辐照实验、建模、数据和共享设施组织第四代核能研发的2019战略议程节点",
    },
    {
        "id": "C-EU-JRC-JRC137540", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2024-01-01",
        "title": "Molten Salt Reactor Technologies",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC137540",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC137540/JRC137540_01.pdf",
        "axes": "熔盐堆；研发标准；科学共同体；标准缺口；技术协调；市场采用；产业转化",
        "role": "以科研共同体参与标准制定和标准缺口识别推动熔盐堆市场采用的2024转化机制节点",
    },
    {
        "id": "C-FAS-2024-FUSION-ENERGY-LEADERSHIP-TRITIUM-CAPACITY", "kind": "wordpress", "wp_id": 33926,
        "institution_id": "fas", "institution": "Federation of American Scientists", "date": "2024-11-26",
        "title": "Promoting Fusion Energy Leadership with U.S. Tritium Production Capacity",
        "landing_url": "https://fas.org/publication/fusion-energy-leadership-tritium-capacity/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/33926?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "聚变能源；氚燃料；工程验证；公共生产能力；示范设施；商业化",
        "role": "以氚供应这一工程瓶颈连接公共能力与商业聚变示范的2024政策机制节点",
    },
    {
        "id": "C-EU-JRC-JRC142326", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2025-01-01",
        "title": "An exploratory analysis of the Small Modular Reactor ecosystem",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC142326",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC142326/JRC142326_01.pdf",
        "axes": "小型模块化反应堆；技术经济生态；研发网络；企业网络；创新转化；国际合作；中国科技横向维度",
        "role": "用技术经济生态方法识别SMR研发网络、企业转化和国际协作结构的2025创新生态节点",
    },
    {
        "id": "C-ITIF-RB-2025-SMALL-MODULAR-REACTORS-A-REALIST-APPROACH-TO-THE-FUTURE-OF-NUCLEAR-POWER",
        "kind": "itif", "institution_id": "itif", "institution": "Information Technology and Innovation Foundation",
        "date": "2025-04-14", "title": "Small Modular Reactors: A Realist Approach to the Future of Nuclear Power",
        "landing_url": "https://itif.org/publications/2025/04/14/small-modular-reactors-a-realist-approach-to-the-future-of-nuclear-power/",
        "asset_url": "https://itif.org/publications/2025/04/14/small-modular-reactors-a-realist-approach-to-the-future-of-nuclear-power/.md",
        "axes": "小型模块化反应堆；价格性能平价；示范研发；规模化制造；政策组合；中国科技横向维度",
        "role": "围绕SMR成本、性能、示范和制造规模化重排公共研发资源的2025路线选择节点",
    },
    {
        "id": "C-EU-STOA-EPRS-IDA-2025-774669", "kind": "pdf", "institution_id": "eu-stoa",
        "institution": "European Parliament Panel for the Future of Science and Technology", "date": "2025-09-30",
        "title": "Fusion Energy: A paradigm shift in power generation for Europe?",
        "landing_url": "https://www.europarl.europa.eu/stoa/en/document/EPRS_IDA(2025)774669",
        "asset_url": "https://www.europarl.europa.eu/RegData/etudes/IDAN/2025/774669/EPRS_IDA(2025)774669_EN.pdf",
        "axes": "聚变能源；技术路线；私营投资；工程里程碑；技能；监管；融资；中国科技横向维度",
        "role": "综合评估聚变技术进展、私营投资、工程不确定性和商业化条件的2025前瞻节点",
    },
)

SOURCE_CATALOGS = (
    "170_ITIF正式报告与简报近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv",
    "182_欧洲议会STOA科技评估近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
)


def update_source_catalogs(root: Path, selected_ids: set[str]) -> None:
    for filename in SOURCE_CATALOGS:
        records, fields = read_csv(root / filename)
        changed = False
        for row in records:
            rid = row.get("统一目录报告ID") or row.get("报告ID")
            if rid not in selected_ids or "全文策略" not in fields:
                continue
            row["全文策略"] = "已进入先进核能聚变技术创新定点全文；按官方原始资产、净文本和科技创新切片调用"
            changed = True
        if changed:
            write_csv(root / filename, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded civilian advanced-nuclear and fusion evidence batch.")
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
                "优先级": "P0-China-STI-node" if china_hits else "P1-STI-nuclear-node", "示踪问题": item["axes"],
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
                "选择理由": "补充先进核材料、核能制氢、SMR生态与聚变工程创新机制；核武器、安全与退役未作为选择条件",
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
    write_csv(root / "244_先进核能聚变技术创新与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "245_先进核能聚变技术创新与中国比较定点增补结果.md").write_text(
        "# 先进核能聚变技术创新与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点保存{len(ledger)}份正式材料，覆盖JRC、FAS、ITIF与欧洲议会STOA，形成2019—2025跨期节点。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger)-pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；只用于定位中国先进核能、聚变研发和产业生态比较段落。\n"
        "- 技术机制覆盖先进核材料、熔盐堆、小型模块化反应堆、聚变氚燃料与工程验证；政策机制覆盖战略研发议程、共享设施、科研共同体参与标准制定、技术经济生态、示范、制造规模化、技能、监管与融资。\n"
        "- 本批未纳入核武器、军用核动力、核安全防护、退役或一般能源安全材料；相关表述仅在直接解释技术研发与商业化条件时调用。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
