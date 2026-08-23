from __future__ import annotations

import argparse
import hashlib
import json
import time
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
    from scripts.extend_viewpoint_fas_light_catalog import _browser_json
    from scripts.extend_viewpoint_fas_selected_fulltexts import clean_html
    from scripts.extend_viewpoint_itif_selected_fulltexts import fetch_markdown
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
    from extend_viewpoint_fas_light_catalog import _browser_json
    from extend_viewpoint_fas_selected_fulltexts import clean_html
    from extend_viewpoint_itif_selected_fulltexts import fetch_markdown


SERIES_ROLE = "使命导向创新重大研发计划与组织机制定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-ITIF-RB-2017-ARPA-E-VERSATILE-CATALYST-US-ENERGY-INNOVATION",
        "kind": "markdown",
        "institution_id": "itif",
        "institution": "Information Technology and Innovation Foundation",
        "date": "2017-11-15",
        "title": "ARPA-E: Versatile Catalyst for U.S. Energy Innovation",
        "landing_url": "https://itif.org/publications/2017/11/15/arpa-e-versatile-catalyst-us-energy-innovation/",
        "asset_url": "https://itif.org/publications/2017/11/15/arpa-e-versatile-catalyst-us-energy-innovation.md",
        "axes": "科学体系与基础研究；使命导向研发机构；能源技术创新；成果转化",
        "role": "以ARPA-E连接高风险研发、技术验证和能源创新应用的2017组织机制基线",
    },
    {
        "id": "C-FAS-2021-HOW-TO-UNLOCK-THE-POTENTIAL-OF-THE-ADVANCED-RESEARCH-PROJECTS-AGENCY-MODEL",
        "kind": "wordpress",
        "wp_id": 16864,
        "institution_id": "fas",
        "institution": "Federation of American Scientists",
        "date": "2021-06-03",
        "title": "How to Unlock the Potential of the Advanced Research Projects Agency Model",
        "landing_url": "https://fas.org/publication/how-to-unlock-the-potential-of-the-advanced-research-projects-agency-model/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/16864?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "科学体系与基础研究；使命导向研发机构；项目经理制；高风险高回报研究",
        "role": "把ARPA模式拆解为组织授权、项目经理、期限和技术组合管理的2021机制节点",
    },
    {
        "id": "S-FISI-2022-01",
        "kind": "pdf",
        "institution_id": "fraunhofer-isi",
        "institution": "Fraunhofer Institute for Systems and Innovation Research ISI",
        "date": "2022-01-01",
        "title": "Putting Mission-Oriented Innovation Policies to Work",
        "landing_url": "https://www.isi.fraunhofer.de/en/competence-center/innovations-wissensoekonomie/publikationen/innovation-systems-policy-analysis.html",
        "asset_url": "https://www.isi.fraunhofer.de/content/dam/isi/dokumente/cci/innovation-systems-policy-analysis/2022/discussionpaper_75_2022.pdf",
        "axes": "创新政策与研发治理；使命导向创新；政策组合；德国高技术战略",
        "role": "检验使命如何从政治目标转化为政策组合和执行结构的2022欧洲节点",
    },
    {
        "id": "C-IFP-2024-HOW-TO-MAKE-THE-NSTC-A-MOONSHOT-SUCCESS",
        "kind": "wordpress",
        "wp_id": 3522,
        "institution_id": "ifp",
        "institution": "Institute for Progress",
        "date": "2024-04-22",
        "title": "How to Make the NSTC a Moonshot Success",
        "landing_url": "https://ifp.org/how-to-make-the-nstc-a-moonshot-success/",
        "asset_url": "https://ifp.org/wp-json/wp/v2/posts/3522?_fields=id,date,slug,link,title,content,excerpt,categories",
        "axes": "关键与新兴技术；半导体研发组织；技术基础设施；中国科技横向维度",
        "role": "以国家半导体技术中心组织共享设施、产业研发和中美能力竞争的2024任务型机构节点",
    },
    {
        "id": "C-OECD-DOI-5E4C3204-EN",
        "kind": "pdf",
        "institution_id": "oecd-sti",
        "institution": "Organisation for Economic Co-operation and Development",
        "date": "2024-10-28",
        "title": "Monitoring and evaluation of mission-oriented innovation policies",
        "landing_url": "https://www.oecd.org/en/publications/monitoring-and-evaluation-of-mission-oriented-innovation-policies_5e4c3204-en.html",
        "asset_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/10/monitoring-and-evaluation-of-mission-oriented-innovation-policies_228b0c83/5e4c3204-en.pdf",
        "axes": "创新政策与研发治理；使命导向创新；发展性评价；任务成熟度",
        "role": "从项目产出评价转向系统效应、行动理论和任务成熟度监测的2024评价节点",
    },
    {
        "id": "C-EU-JRC-JRC141409",
        "kind": "pdf",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2025-01-01",
        "title": "Smart Specialisation Strategies and Mission-oriented approach: Bridging Theory and Practice",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC141409",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC141409/JRC141409_01.pdf",
        "axes": "区域创新体系；使命导向创新；社会参与；政策工具组合",
        "role": "揭示区域创新战略引入使命导向时方向性、灵活性和多主体治理权衡的2025实践节点",
    },
)

SOURCE_CATALOGS = (
    "84_Fraunhofer_ISI创新系统政策分析轻量目录.csv",
    "166_IFP科技创新正式成果轻量总目录.csv",
    "170_ITIF正式报告与简报近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "77_OECD_STI正式系列轻量目录.csv",
)


def fetch_wordpress_record(url: str, expected_id: int) -> dict[str, object]:
    opened = _proxy_json("/new?url=" + quote(url, safe=""))
    target = str(opened["targetId"])
    last_text = ""
    try:
        for _ in range(100):
            value = _proxy_json("/eval?target=" + target, "document.body?.innerText||''")["value"]
            last_text = str(value).strip()
            if last_text.startswith("{"):
                try:
                    record = json.loads(last_text)
                except json.JSONDecodeError:
                    time.sleep(0.2)
                    continue
                if isinstance(record, dict) and int(record.get("id", 0)) == expected_id:
                    return record
            time.sleep(0.2)
        raise RuntimeError(f"WordPress API record did not load completely: id={expected_id} chars={len(last_text)}")
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass


def update_source_catalogs(root: Path, china_hits_by_id: dict[str, int]) -> None:
    for filename in SOURCE_CATALOGS:
        path = root / filename
        records, fields = read_csv(path)
        changed = False
        for row in records:
            rid = row.get("统一目录报告ID") or row.get("报告ID")
            if rid not in china_hits_by_id:
                continue
            if "全文策略" in fields:
                row["全文策略"] = "已进入使命导向创新与重大研发组织机制定点全文；按官方原始资产、净文本和科技创新切片调用"
            if china_hits_by_id[rid] > 0:
                if "中国直接信号" in fields:
                    row["中国直接信号"] = "是（全文词形定位；具体语义待编码）"
                if "中国关联" in fields:
                    row["中国关联"] = "是；全文词形定位，具体比较口径待编码"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded mission-oriented R&D organisation evidence batch.")
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
                text, units = extract_pdf(source_path)
                asset_type = "官方PDF"
                status = "官方PDF已获取并校验；已生成文本与科技创新切片"
            elif item["kind"] == "markdown":
                source_path = web_dir / f"{rid}.md"
                content = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else fetch_markdown(item["asset_url"])
                source_path.write_text(content, encoding="utf-8", newline="\n")
                payload = content.encode("utf-8")
                text = content
                units = 1
                asset_type = "官方Markdown网页正文"
                status = "官方Markdown正文已获取并校验；已生成文本与科技创新切片"
            else:
                source_path = web_dir / f"{rid}.html"
                if source_path.exists():
                    payload = source_path.read_bytes()
                    content_html = payload.decode("utf-8", errors="replace")
                else:
                    response = fetch_wordpress_record(item["asset_url"], item["wp_id"])
                    content = response.get("content") or {}
                    content_html = str(content.get("rendered", "")) if isinstance(content, dict) else str(content)
                    source_path.write_text(content_html, encoding="utf-8", newline="\n")
                    payload = source_path.read_bytes()
                text = clean_html(content_html)
                units = 1
                asset_type = "官方WordPress网页正文"
                status = "官方WordPress正文已获取并校验；已生成文本与科技创新切片"
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
            row["本地路径"] = str(text_path)
            row["正文完整度"] = "官方全文已保存；同时生成可检索文本和科技创新切片"
            row["优先级"] = "P0-China-STI-node" if china_hits else "P1-STI-mission-node"
            row["示踪问题"] = item["axes"]
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = item["role"]
            row["本地原始资产路径"] = str(source_path)
            row["原始资产状态"] = status
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
                "选择理由": "补充使命导向创新、重大研发机构、政策组合、评价方法与半导体任务型平台机制；安全题名不构成选择依据",
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
    write_csv(root / "232_使命导向创新重大研发计划与组织机制定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或网页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    (root / "233_使命导向创新重大研发计划与组织机制定点增补结果.md").write_text(
        "# 使命导向创新、重大研发计划与组织机制定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料，覆盖ITIF、FAS、Fraunhofer ISI、IFP、OECD与JRC。\n"
        f"- 保存{pdf_count}份官方PDF和{len(ledger) - pdf_count}项官方网页正文，共{totals['页数或网页数']:,}页或网页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；仅用于定位中国科技比较段落。\n"
        "- 覆盖ARPA型研发机构、项目经理制、使命政策组合、半导体共享研发平台、发展性评价和区域任务治理。\n"
        "- 未新增安全类目录；全文选择由科学技术创新组织机制、重大研发计划执行和中国技术能力比较触发。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或网页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
