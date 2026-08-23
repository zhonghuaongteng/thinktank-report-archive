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


SERIES_ROLE = "空间科学地球观测技术创新与中国比较定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-JRC-JRC118879", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2020-01-01",
        "title": "Copernicus and Earth observation in support of EU policies",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC118879",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC118879/user_uptake_report_pdf.pdf",
        "axes": "地球观测；开放数据；政策采用；用户反馈；标准；质量控制；数据集成",
        "role": "以公共投资、开放数据、用户反馈和标准质量控制解释地球观测政策采用的2020基础设施节点",
    },
    {
        "id": "C-EU-JRC-JRC121833", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2020-01-01",
        "title": "Cold atom interferometry for Earth observation",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC121833",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC121833/cold_atom_interferometry_satellite-based_gravimetry.pdf",
        "axes": "冷原子干涉；量子重力传感；卫星任务；科学需求；工程验证；跨学科协作",
        "role": "比较成熟重力测量与冷原子量子传感路线并提出在轨科学验证阶梯的2020技术评估节点",
    },
    {
        "id": "C-FAS-2020-EARTH-OBSERVATION-FOR-SENSIBLE-CLIMATE-POLICY", "kind": "wordpress", "wp_id": 17085,
        "institution_id": "fas", "institution": "Federation of American Scientists", "date": "2020-10-19",
        "title": "Earth Observation for Sensible Climate Policy",
        "landing_url": "https://fas.org/publication/earth-observation-for-sensible-climate-policy/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/17085?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "地球观测；气候测量；温室气体监测；卫星数据；公共投资；政策证据",
        "role": "把持续地球观测投资连接到温室气体直接测量和气候政策证据的2020应用节点",
    },
    {
        "id": "C-EU-JRC-JRC136730", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2024-01-01",
        "title": "Earth Observation Strategic Research and Innovation Agenda",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC136730",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC136730/JRC136730_01.pdf",
        "axes": "地球观测研发议程；Copernicus；数据基础设施；数字孪生；AI；服务演进；用户采用",
        "role": "将卫星、原位数据、计算基础设施、数字孪生和AI组织为持续服务演进的2024研发议程节点",
    },
    {
        "id": "C-EU-JRC-JRC143067", "kind": "pdf", "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre", "date": "2025-01-01",
        "title": "AI Super-Resolution of Satellite Imagery: The Evidential Paradigm Shift in CAP Monitoring",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC143067",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC143067/JRC143067_01.pdf",
        "axes": "卫星图像；AI超分辨率；性能边界；证据可靠性；认证；业务部署",
        "role": "识别AI增强卫星图像从物理记录转向生成式表征后的性能、认证和部署边界的2025节点",
    },
    {
        "id": "C-FAS-2026-TRACKING-HYPERSCALE", "kind": "wordpress", "wp_id": 42781,
        "institution_id": "fas", "institution": "Federation of American Scientists", "date": "2026-05-12",
        "title": "Tracking Hyperscale AI Data Center Growth with Satellite Imagery",
        "landing_url": "https://fas.org/publication/tracking-hyperscale/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/42781?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "卫星图像；AI数据中心；基础设施测量；开放情报方法；规模识别；中国科技横向维度",
        "role": "以卫星图像建立AI数据中心规模、建设进度和全球基础设施比较方法的2026测量节点",
    },
)

SOURCE_CATALOGS = (
    "174_FAS报告与政策备忘录近十年轻量总目录.csv",
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
            row["全文策略"] = "已进入空间科学地球观测技术创新定点全文；按官方原始资产、净文本和科技创新切片调用"
            changed = True
        if changed:
            write_csv(root / filename, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded Earth-observation technology and innovation evidence batch.")
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
                "优先级": "P0-China-STI-node" if china_hits else "P1-STI-earth-observation-node",
                "示踪问题": item["axes"], "样本角色": SERIES_ROLE, "编码状态": "全文待观点编码",
                "预期用途": item["role"], "本地原始资产路径": str(source_path), "原始资产状态": status,
            })
            ledger.append({
                "报告ID": rid, "机构ID": item["institution_id"], "机构": item["institution"], "发布日期": item["date"],
                "报告名称": item["title"], "官方落地页": item["landing_url"], "官方全文入口": item["asset_url"],
                "资产类型": asset_type, "本地原始资产": str(source_path), "本地文本": str(text_path), "本地切片": str(slice_path),
                "页数或网页数": str(units), "字节数": str(len(payload)), "清洗文本字符数": str(len(clean)),
                "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(payload).hexdigest(),
                "科技创新主轴": item["axes"], "科技创新复用角色": item["role"],
                "选择理由": "补充地球观测公共基础设施、量子传感、研发议程、AI图像增强和跨领域测量方法；安全与军事用途未作为选择条件",
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
    write_csv(root / "246_空间科学地球观测技术创新与中国比较定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "247_空间科学地球观测技术创新与中国比较定点增补结果.md").write_text(
        "# 空间科学地球观测技术创新与中国比较定点增补结果\n\n"
        f"- 从既有轻量目录定点保存{len(ledger)}份正式材料，覆盖JRC与FAS，形成2020—2026跨期节点。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger)-pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；只用于定位中国地球观测、卫星应用与AI基础设施比较段落。\n"
        "- 技术机制覆盖开放卫星数据、冷原子量子传感、温室气体直接测量、数字孪生、AI超分辨率与基础设施遥感；政策机制覆盖公共投资、用户反馈、标准质量控制、在轨验证、研发议程、服务采用和认证。\n"
        "- 本批未纳入军事航天、导弹、核设施监视、一般空间安全或轨道治理材料；相关表述仅在直接解释技术研发、测量能力和应用边界时调用。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
