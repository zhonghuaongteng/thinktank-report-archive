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
except ModuleNotFoundError:
    from backfill_viewpoint_china_research_system_nodes import (
        clean_text, download_pdf, extract_pdf, make_slice, read_csv, write_csv,
    )
    from backfill_viewpoint_mission_oriented_rd_nodes import fetch_wordpress_record
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from extend_viewpoint_fas_selected_fulltexts import clean_html


SERIES_ROLE = "先进材料技术创新平台与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-US-OSTP-2016-2016-NNI-STRATEGIC-PLAN", "kind": "pdf", "institution_id": "us-ostp",
        "institution": "White House Office of Science and Technology Policy / National Science and Technology Council",
        "date": "2016-01-01", "title": "National Nanotechnology Initiative 2016 Strategic Plan",
        "landing_url": "https://obamawhitehouse.archives.gov/node/10054/",
        "asset_url": "https://www.nano.gov/sites/default/files/pub_resource/2016-nni-strategic-plan.pdf",
        "axes": "纳米技术；基础研究；跨机构研发；共享基础设施；技术转移；中国科技横向维度",
        "role": "以基础研究、跨机构协调、用户设施和商业化目标构成先进材料政策的2016早期战略节点",
    },
    {
        "id": "C-EU-JRC-JRC115968", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2019-01-01",
        "title": "Technology Transfer in Nanotechnology",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC115968",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC115968/jrc115968_jrc115968_technical_report_on_technology_transfer_in_nanotechnology.pdf",
        "axes": "纳米技术；技术转移；知识产权；中试与产业化；创新生态；中国科技横向维度",
        "role": "从实验室成果、知识产权、企业吸收和中试环节解释纳米技术商业化瓶颈的2019节点",
    },
    {
        "id": "C-OECD-DOI-BB5225F1-EN", "kind": "pdf", "institution_id": "oecd-sti",
        "institution": "Organisation for Economic Co-operation and Development", "date": "2020-12-14",
        "title": "Collaborative platforms for innovation in advanced materials",
        "landing_url": "https://www.oecd.org/en/publications/collaborative-platforms-for-innovation-in-advanced-materials_bb5225f1-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/12/collaborative-platforms-for-innovation-in-advanced-materials_9050e25f/bb5225f1-en.pdf",
        "axes": "先进材料；数字与物理协作平台；研发数据；标准；技能；产业价值链；中国科技横向维度",
        "role": "用12个案例解释共享数据设施、实验平台、知识产权和标准如何缩短材料转化周期的2020节点",
    },
    {
        "id": "C-EU-JRC-JRC126884", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2021-01-01",
        "title": "Innovation Ecosystems in the Creative Sector: The Case of Additive Manufacturing and Advanced Materials for Design.",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC126884",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC126884/JRC126884_01.pdf",
        "axes": "增材制造；先进材料；创新生态；初创企业；技术采用；区域集群",
        "role": "以430家初创企业和四类区域生态观察先进材料与增材制造扩散的2021产业化节点",
    },
    {
        "id": "C-FAS-2024-ACCELERATING-MATERIALS-SCIENCE-WITH-AI-AND-ROBOTICS", "kind": "wordpress", "wp_id": 33722,
        "institution_id": "fas", "institution": "Federation of American Scientists", "date": "2024-11-26",
        "title": "Accelerating Materials Science with AI and Robotics",
        "landing_url": "https://fas.org/publication/accelerating-materials-science-with-ai-and-robotics/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/33722?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "材料发现；科学基础模型；科研数据；机器人实验室；公共研发设施；成果转化",
        "role": "将材料数据、科学基础模型和自驱动实验室组织为公共研发能力的2024技术路线节点",
    },
    {
        "id": "C-OECD-DOI-A15874FA-EN", "kind": "pdf", "institution_id": "oecd-sti",
        "institution": "Organisation for Economic Co-operation and Development", "date": "2025-10-20",
        "title": "Steering the future of advanced materials",
        "landing_url": "https://www.oecd.org/en/publications/steering-the-future-of-advanced-materials_a15874fa-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/10/steering-the-future-of-advanced-materials_9add3995/a15874fa-en.pdf",
        "axes": "先进材料战略；技术前瞻；路线图；战略情报；研发治理；创新生态",
        "role": "把材料政策从单项研发支持推进到国家战略、路线图和前瞻治理组合的2025节点",
    },
)

SOURCE_CATALOGS = (
    "77_OECD_STI正式系列轻量目录.csv", "88_美国OSTP科学技术创新政策轻量目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv", "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
)


def update_source_catalogs(root: Path, selected_ids: set[str]) -> None:
    for filename in SOURCE_CATALOGS:
        records, fields = read_csv(root / filename)
        changed = False
        for row in records:
            rid = row.get("统一目录报告ID") or row.get("报告ID")
            if rid not in selected_ids or "全文策略" not in fields:
                continue
            row["全文策略"] = "已进入先进材料技术创新平台定点全文；按官方原始资产、净文本和科技创新切片调用"
            changed = True
        if changed:
            write_csv(root / filename, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded advanced-materials innovation evidence batch.")
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
                "本地路径": str(text_path), "正文完整度": "官方全文已保存；同时生成可检索文本和科技创新切片",
                "优先级": "P0-China-STI-node" if china_hits else "P1-STI-materials-node", "示踪问题": item["axes"],
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
                "选择理由": "补充先进材料技术路线、研发平台、技术转移、AI材料发现和中国比较；关键矿产与安全未作为选择条件",
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
    write_csv(root / "240_先进材料技术创新平台与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "241_先进材料技术创新平台与中国比较定点增补结果.md").write_text(
        "# 先进材料技术创新平台与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点保存{len(ledger)}份正式材料，覆盖OSTP/NSTC、JRC、OECD与FAS，形成2016—2025跨期节点。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger)-pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；只用于定位中国科研、技术转移和材料创新能力比较段落。\n"
        "- 技术机制覆盖纳米技术、增材制造、材料数据、科学基础模型与自驱动实验室；政策机制覆盖跨机构研发、共享设施、协作平台、技术转移、标准、技能、路线图和战略情报。\n"
        "- 本批未纳入关键矿产、供应链韧性、材料安全评估或国防应用主导材料；相关表述仅在直接解释研发与创新机制时调用。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
