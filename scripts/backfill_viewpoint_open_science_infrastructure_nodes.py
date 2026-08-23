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
    from scripts.extend_viewpoint_fas_light_catalog import _browser_json
    from scripts.extend_viewpoint_fas_selected_fulltexts import clean_html
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
    from extend_viewpoint_fas_light_catalog import _browser_json
    from extend_viewpoint_fas_selected_fulltexts import clean_html
    from extend_viewpoint_nasem_selected_fulltexts import (
        count_archived_chapters,
        fetch_book_via_jina,
        normalize_archive_whitespace,
        selected_slice,
    )


SERIES_ROLE = "开放科学科研基础设施与技术平台定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-EU-JRC-JRC119687",
        "kind": "pdf",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2020-01-01",
        "title": "Open Data, Open Science & Open Innovation for Smart Specialisation monitoring",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC119687",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC119687/jrc119687_final_open_data_open_science__open_innovation_for_smart_specialisation_monitoring_siris_em_feb_13.pd.pdf",
        "axes": "科学体系与科研能力；开放科学与开放数据；区域创新监测；产业创新与成果转化",
        "role": "把开放数据、开放科学和开放创新嵌入区域创新战略监测的2020机制节点",
    },
    {
        "id": "C-US-NASEM-25725",
        "kind": "nasem",
        "record_id": 25725,
        "institution_id": "us-nasem",
        "institution": "National Academies of Sciences, Engineering, and Medicine",
        "date": "2020-02-27",
        "title": "Advancing Open Science Practices: Stakeholder Perspectives on Incentives and Disincentives",
        "landing_url": "https://www.nationalacademies.org/publications/25725",
        "asset_url": "https://www.nationalacademies.org/read/25725/chapter/1",
        "axes": "科学体系与基础研究；开放科学；科研评价与激励；国际合作",
        "role": "识别开放科学实践中研究者、资助方、出版机构激励与阻碍的2020制度节点",
    },
    {
        "id": "C-EU-JRC-JRC127798",
        "kind": "pdf",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2021-01-01",
        "title": "Towards the Implementation of an EU Strategy for Technology Infrastructures",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC127798",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC127798/JRC127798_01.pdf",
        "axes": "科研与技术基础设施；技术验证与放大；产业创新与成果转化；公共研发治理",
        "role": "以开放技术设施连接概念验证、测试示范、规模放大和产业技术扩散的2021政策节点",
    },
    {
        "id": "C-US-NASEM-26308",
        "kind": "nasem",
        "record_id": 26308,
        "institution_id": "us-nasem",
        "institution": "National Academies of Sciences, Engineering, and Medicine",
        "date": "2021-09-30",
        "title": "Developing a Toolkit for Fostering Open Science Practices",
        "landing_url": "https://www.nationalacademies.org/publications/26308",
        "asset_url": "https://www.nationalacademies.org/read/26308/chapter/1",
        "axes": "科学体系与基础研究；开放科学；科研组织与实践工具；国际合作",
        "role": "将开放科学原则转化为研究机构和资助组织可执行工具的2021实践节点",
    },
    {
        "id": "C-RATHENAU-2022-MOVING-FORWARD-TOGETHER-OPEN-SCIENCE",
        "kind": "pdf",
        "institution_id": "rathenau",
        "institution": "Rathenau Instituut",
        "date": "2022-02-23",
        "title": "Moving forward together with open science",
        "landing_url": "https://www.rathenau.nl/en/how-science-system-works/moving-forward-together-open-science",
        "asset_url": "https://www.rathenau.nl/sites/default/files/2022-02/Moving_further_together_with_open%20science_Rathenau_Instituut.pdf",
        "axes": "科学体系与基础研究；开放科学；科研组织与协作；公共价值",
        "role": "从多主体协同行动推进开放科学制度化的2022欧洲科学体系节点",
    },
    {
        "id": "C-FAS-2024-BUILD-CAPACITY-FOR-AGENCY-USE-OF-OPEN-SCIENCE-HARDWARE",
        "kind": "fas",
        "wp_id": 27906,
        "institution_id": "fas",
        "institution": "Federation of American Scientists",
        "date": "2024-02-06",
        "title": "Build capacity for agency use of open science hardware",
        "landing_url": "https://fas.org/publication/build-capacity-for-agency-use-of-open-science-hardware/",
        "asset_url": "https://fas.org/wp-json/wp/v2/publications/27906?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": "开放科学；科研仪器与开放硬件；公共部门科研能力；技术扩散",
        "role": "以开放源硬件提升联邦机构科研工具复用、验证和采购能力的2024政策节点",
    },
)

SOURCE_CATALOGS = (
    "162_Rathenau英文正式报告近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv",
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
            if rid not in china_hits_by_id:
                continue
            if "全文策略" in fields:
                row["全文策略"] = "已进入开放科学、科研基础设施与技术平台定点全文；按官方原始资产、净文本和科技创新切片调用"
            if "中国直接信号" in fields and china_hits_by_id[rid] > 0:
                row["中国直接信号"] = "是（全文词形定位；具体语义待编码）"
            if "中国关联" in fields and china_hits_by_id[rid] > 0:
                row["中国关联"] = "是；全文词形定位，具体比较口径待编码"
            changed = True
        if changed:
            write_csv(path, records, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded open-science and research-infrastructure evidence batch.")
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
                source_path = web_dir / f"{rid}.html"
                if source_path.exists():
                    content_html = source_path.read_text(encoding="utf-8", errors="replace")
                else:
                    response, _ = _browser_json(item["asset_url"])
                    if not isinstance(response, dict) or int(response.get("id", 0)) != item["wp_id"]:
                        raise RuntimeError(f"unexpected FAS API record: {rid}")
                    content = response.get("content") or {}
                    content_html = str(content.get("rendered", "")) if isinstance(content, dict) else str(content)
                    source_path.write_text(content_html, encoding="utf-8", newline="\n")
                text = clean_html(content_html)
                payload = content_html.encode("utf-8")
                units = 1
                asset_type = "官方WordPress网页正文"
                source_status = "FAS官方WordPress正文原始资产已获取并校验"
                completeness = "FAS官方WordPress页面正文已保存；同时生成清洗文本和科技创新切片"
                slice_text = make_slice(item, text)
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
            row["优先级"] = "P1-STI-open-infrastructure-node"
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
                "选择理由": "补充开放科学、科研基础设施、技术验证平台与公共科研能力机制；安全题名不构成选择依据",
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
    write_csv(root / "230_开放科学科研基础设施与技术平台定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数或章节数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_reports = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    pdf_count = sum(row["资产类型"] == "官方PDF" for row in ledger)
    web_count = len(ledger) - pdf_count
    (root / "231_开放科学科研基础设施与技术平台定点增补结果.md").write_text(
        "# 开放科学、科研基础设施与技术平台定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：JRC与NASEM各2份，Rathenau与FAS各1份。\n"
        f"- 保存{pdf_count}份官方PDF和{web_count}项官方网页全文，共{totals['页数或章节数']:,}页或章、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- {china_reports}份材料含China/Chinese/PRC/Sino-词形，合计{totals['China词形命中数']:,}次；仅用于定位中国科技比较段落。\n"
        "- 覆盖开放科学激励、实践工具、开放数据与区域创新监测、技术验证设施、开放科学协同和开放硬件。\n"
        "- 未新增安全类目录；全文选择由科学体系、科研工具、技术平台和创新扩散机制触发。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} units={totals['页数或章节数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_reports={china_reports} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
