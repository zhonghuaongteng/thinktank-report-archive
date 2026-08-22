from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

from pypdf import PdfReader

try:
    from scripts.extend_viewpoint_eu_stoa_light_catalog import CATALOG_FIELDS, CDP_PROXY, LISTING_URL, _proxy_json
except ModuleNotFoundError:
    from extend_viewpoint_eu_stoa_light_catalog import CATALOG_FIELDS, CDP_PROXY, LISTING_URL, _proxy_json


SERIES_ROLE = "欧洲议会STOA科技创新与技术评估跨期精选全文"


def _item(report_id: str, published: str, title: str, axes: tuple[str, ...], role: str) -> dict[str, object]:
    return {"id": report_id, "date": published, "title": title, "axes": axes, "role": role}


SELECTED_ITEMS = (
    _item("C-EU-STOA-EPRS-STU-2016-563501", "2016-06-28", "Ethical Aspects of Cyber-Physical Systems", ("技术评估与前瞻方法", "关键技术与产业转化"), "以网络物理系统为样本建立技术评估、社会影响和政策响应的前序基线"),
    _item("C-EU-STOA-EPRS-STU-2017-603183", "2017-07-05", "Horizon scanning and analysis of techno-scientific trends: Scientific Foresight Study", ("技术评估与前瞻方法", "科研体系与研发资助"), "STOA科学前瞻与技术扫描方法的核心节点"),
    _item("C-EU-STOA-EPRS-STU-2017-614531", "2017-12-20", "Achieving a sovereign and trustworthy ICT industry in the EU", ("关键技术与产业转化", "创新政策与区域能力"), "欧盟ICT产业能力、研发基础和技术主权议题的早期系统材料"),
    _item("C-EU-STOA-EPRS-STU-2018-614537", "2018-03-14", "Overcoming innovation gaps in the EU-13 Member States", ("创新政策与区域能力", "科研体系与研发资助"), "区域创新能力差距、科研投入与政策工具的比较节点"),
    _item("C-EU-STOA-EPRS-STU-2018-614546", "2018-07-04", "New technologies and regional policy:Towards the next cohesion policy framework", ("创新政策与区域能力", "关键技术与产业转化"), "新技术扩散与区域创新政策结合的机制材料"),
    _item("C-EU-STOA-EPRS-STU-2019-634444", "2019-07-24", "Internationalisation of EU research organisations", ("国际科研合作与开放条件", "科研体系与研发资助"), "科研组织国际化、合作网络和开放条件的跨国比较"),
    _item("C-EU-STOA-EPRS-STU-2019-634447", "2019-07-24", "How the General Data Protection Regulation changes the rules for scientific research", ("国际科研合作与开放条件", "科研体系与研发资助"), "数据制度改变科学研究组织方式和跨境合作条件的节点"),
    _item("C-EU-STOA-EPRS-IDA-2020-641542", "2020-06-17", "Exploring the performance gap in EU Framework Programmes between EU13 and EU15 Member States", ("科研体系与研发资助", "创新政策与区域能力"), "欧盟框架计划参与和绩效差距的定量比较"),
    _item("C-EU-STOA-EPRS-IDA-2020-641543", "2020-04-22", "Ten technologies to fight coronavirus", ("关键技术与产业转化", "技术评估与前瞻方法"), "公共危机中多技术组合从研发到应用的快速评估样本"),
    _item("C-EU-STOA-EPRS-STU-2021-690029", "2021-11-25", "A framework for foresight intelligence - Part 1: Horizon scanning tailored to STOA's needs", ("技术评估与前瞻方法",), "从专题技术评估转向持续前瞻情报体系的方法节点"),
    _item("C-EU-STOA-EPRS-STU-2021-697184", "2021-12-16", "Key enabling technologies for Europe's technological sovereignty", ("关键技术与产业转化", "创新政策与区域能力"), "关键使能技术、产业能力和技术主权的政策组合"),
    _item("C-EU-STOA-EPRS-STU-2021-697197", "2021-12-21", "European pharmaceutical research and development: Could public infrastructure overcome market failures?", ("科研体系与研发资助", "关键技术与产业转化"), "公共科研基础设施介入药物研发市场失灵的组织机制"),
    _item("C-EU-STOA-EPRS-STU-2022-697218", "2022-05-05", "A reimbursement system based on a fixed lump sum - Is it the right tool for the EU Framework Programme for research?", ("科研体系与研发资助", "创新政策与区域能力"), "欧盟科研项目资助和报销机制改革的制度评估"),
    _item("C-EU-STOA-EPRS-STU-2022-737114", "2022-10-19", "Fostering coherence in EU health research: Strengthening EU research for better health", ("科研体系与研发资助", "国际科研合作与开放条件"), "健康研究计划协调、跨层级治理与科研能力建设"),
    _item("C-EU-STOA-EPRS-STU-2023-740259", "2023-06-15", "Analysis exploring risks and opportunities linked to the use of collaborative industrial robots in Europe", ("关键技术与产业转化", "创新政策与区域能力"), "协作机器人产业应用、技术能力与劳动组织的综合评估"),
    _item("C-EU-STOA-EPRS-STU-2023-753166", "2023-11-23", "Improving public access to medicines and promoting pharmaceutical innovation", ("关键技术与产业转化", "科研体系与研发资助"), "药物可及性与制药创新激励之间的政策机制"),
    _item("C-EU-STOA-EPRS-STU-2024-757813", "2024-07-04", "The Horizon Europe Programme: A strategic assessment of selected items", ("科研体系与研发资助", "创新政策与区域能力"), "Horizon Europe执行结构、任务工具和创新绩效的战略评估"),
    _item("C-EU-STOA-EPRS-STU-2024-762848", "2024-07-17", "The role of research and innovation in ensuring a safe and sustainable supply of critical raw materials in the EU", ("关键技术与产业转化", "国际科研合作与开放条件"), "以关键原材料为对象分析研发创新、替代技术和循环利用能力"),
    _item("C-EU-STOA-EPRS-STU-2025-765780", "2025-06-19", "Evolution and/or disruption? Designing the next Framework Programme for Research and Innovation", ("科研体系与研发资助", "技术评估与前瞻方法"), "面向下一期欧盟科研创新框架计划的情景设计和制度重构"),
    _item("C-EU-STOA-EPRS-STU-2026-774682", "2026-05-22", "'Widening' Indicator: Leveraging the potential for inclusive European research and innovation", ("创新政策与区域能力", "科研体系与研发资助"), "以指标体系评估科研创新能力扩散和区域收敛的新节点"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _eval(target: str, expression: str) -> object:
    payload = _proxy_json("/eval?target=" + target, expression)
    if not isinstance(payload, dict) or "value" not in payload:
        raise RuntimeError(f"unexpected CDP evaluation response: {payload!r}")
    return payload["value"]


def official_pdf_url(links: list[tuple[str, str]]) -> str:
    for label, url in links:
        if (
            label.strip().upper().startswith("EN")
            and url.startswith((
                "https://www.europarl.europa.eu/RegData/etudes/",
                "http://www.europarl.europa.eu/RegData/etudes/",
            ))
            and url.lower().endswith("_en.pdf")
        ):
            return url
    return ""


def inferred_official_pdf_url(detail_url: str) -> str:
    match = re.fullmatch(
        r"https://www\.europarl\.europa\.eu/stoa/en/document/EPRS_(STU|IDA)\((\d{4})\)(\d+)",
        detail_url,
    )
    if not match:
        return ""
    kind, year, number = match.groups()
    folder = "STUD" if kind == "STU" else "IDAN"
    return f"https://www.europarl.europa.eu/RegData/etudes/{folder}/{year}/{number}/EPRS_{kind}({year}){number}_EN.pdf"


def page_detail(target: str, url: str) -> tuple[str, str, str]:
    _proxy_json("/navigate?target=" + target + "&url=" + quote(url, safe=""))
    for _ in range(50):
        title = str(_eval(target, "document.title"))
        text_len = int(_eval(target, "document.querySelector('main')?.innerText.length||0"))
        if "Panel for the Future of Science and Technology" in title and text_len >= 300:
            break
        time.sleep(0.25)
    expression = """(() => {const main=document.querySelector('main');return {title:document.title,html:main?.outerHTML||'',text:main?.innerText||'',links:[...document.querySelectorAll('a[href]')].map(a=>[(a.innerText||'').trim(),a.href])}})()"""
    value = _eval(target, expression)
    if not isinstance(value, dict) or len(str(value.get("text", ""))) < 300:
        raise RuntimeError(f"thin or blocked STOA page: {url}")
    links = [(str(pair[0]), str(pair[1])) for pair in value.get("links", []) if isinstance(pair, list) and len(pair) == 2]
    pdf_url = official_pdf_url(links) or inferred_official_pdf_url(url)
    if not pdf_url:
        raise RuntimeError(f"official English STOA PDF missing: {url}")
    return str(value.get("html", "")), str(value.get("text", "")), pdf_url


def _range_fetch(target: str, url: str, start: int, end: int) -> tuple[int, str, bytes]:
    expression = """(async()=>{const r=await fetch(URL_VALUE,{headers:{Range:RANGE_VALUE}});const b=new Uint8Array(await r.arrayBuffer());let s='';for(let i=0;i<b.length;i+=32768){s+=String.fromCharCode(...b.subarray(i,i+32768))}return {status:r.status,range:r.headers.get('content-range')||'',data:btoa(s)}})()"""
    expression = expression.replace("URL_VALUE", json.dumps(url)).replace("RANGE_VALUE", json.dumps(f"bytes={start}-{end}"))
    value = _eval(target, expression)
    if not isinstance(value, dict):
        raise RuntimeError(f"unexpected STOA PDF response: {url}")
    return int(value.get("status", 0)), str(value.get("range", "")), base64.b64decode(str(value.get("data", "")))


def browser_pdf(target: str, url: str) -> bytes:
    chunk_size = 1_500_000
    download_url = url
    status, content_range, first = _range_fetch(target, download_url, 0, chunk_size - 1)
    if status in (0, 202):
        alternate = url.replace("http://", "https://", 1) if url.startswith("http://") else url.replace("https://", "http://", 1)
        download_url = alternate
        status, content_range, first = _range_fetch(target, download_url, 0, chunk_size - 1)
    if status == 200:
        data = first
    elif status == 206:
        total_match = re.search(r"/(\d+)$", content_range)
        chunks = [first]
        total = int(total_match.group(1)) if total_match else None
        start = chunk_size
        while total is None or start < total:
            next_status, next_range, part = _range_fetch(target, download_url, start, start + chunk_size - 1)
            if next_status == 416:
                break
            if next_status != 206:
                raise RuntimeError(f"unexpected STOA PDF range status {next_status}: {url}")
            chunks.append(part)
            if total is None:
                next_total = re.search(r"/(\d+)$", next_range)
                total = int(next_total.group(1)) if next_total else None
            start += chunk_size
            if total is None and len(part) < chunk_size:
                break
        data = b"".join(chunks)
        if total is not None and len(data) != total:
            raise RuntimeError(f"incomplete STOA PDF download: expected {total}, found {len(data)}")
    else:
        raise RuntimeError(f"STOA PDF request failed with status {status}: {url}")
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"STOA attachment is not a PDF: {url}")
    return data


def extract_pdf_text(data: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(data))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n", len(reader.pages)


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = (
        "science", "scientific", "research", "r&d", "innovation", "technology", "foresight", "assessment",
        "framework programme", "horizon europe", "infrastructure", "laboratory", "university", "industry",
        "commercial", "regional", "international", "collaboration", "china", "chinese", "quantum", "robot",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 70]
    hits = [part for part in paragraphs if any(word in part.lower() for word in keywords)][:200]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 科技创新复用角色：{item['role']}\n"
        f"- 主轴：{'；'.join(item['axes'])}\n\n## 科学技术创新与中国定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Save a selective STOA science, technology and innovation full-text layer through the browser.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "182_欧洲议会STOA科技评估近十年轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light = read_csv(light_path)
    catalog = read_csv(catalog_path)
    light_by_id = {row["报告ID"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    missing = selected_ids - set(light_by_id)
    if missing:
        raise RuntimeError(f"selected STOA items missing from light catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        source = light_by_id[str(item["id"])]
        if source["发布日期"] != item["date"] or source["报告名称"] != item["title"]:
            raise RuntimeError(f"selected STOA metadata drift: {item['id']}")
    html_dir = root / "03_证据底稿" / "网页原文"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (html_dir, pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    opened = _proxy_json("/new?url=" + quote(LISTING_URL, safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = str(item["id"])
            source = light_by_id[rid]
            url = source["官方落地页"]
            html_path = html_dir / f"{rid}.html"
            pdf_path = pdf_dir / f"{rid}.pdf"
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            main_html, page_text, pdf_url = page_detail(target, url)
            html_path.write_text(main_html, encoding="utf-8", newline="\n")
            if pdf_path.exists():
                pdf_data = pdf_path.read_bytes()
            else:
                pdf_data = browser_pdf(target, pdf_url)
                pdf_path.write_bytes(pdf_data)
            text, pages = extract_pdf_text(pdf_data)
            if len(text) < 500:
                raise RuntimeError(f"STOA selected text too short: {rid} {len(text)}")
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(selected_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            row = catalog_by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = "官方PDF已保存；同时保存官方页面主体HTML、逐页提取文本和科技创新切片"
            row["优先级"] = "P1-STI-node"
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = str(item["role"])
            row["本地原始资产路径"] = str(pdf_path)
            row["原始资产状态"] = "欧洲议会RegData官方英文PDF已获取并校验；官方页面主体HTML同步保存"
            source["全文策略"] = "已进入精选全文；按官方PDF、页面HTML、提取文本和科技创新切片调用"
            ledger.append({
                "报告ID": rid,
                "发布日期": str(item["date"]),
                "报告名称": str(item["title"]),
                "官方文类": source["官方文类"],
                "官方文号": source["官方文号"],
                "官方落地页": url,
                "官方PDF入口": pdf_url,
                "本地原始PDF": str(pdf_path),
                "本地页面HTML": str(html_path),
                "本地文本": str(text_path),
                "本地切片": str(slice_path),
                "页数": str(pages),
                "字节数": str(len(pdf_data)),
                "清洗文本字符数": str(len(text)),
                "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(pdf_data).hexdigest(),
                "科技创新主轴": "；".join(item["axes"]),
                "科技创新复用角色": str(item["role"]),
                "选择理由": "跨期节点；解释科学体系、技术评估、研发政策或技术转化机制；安全与一般治理不单独触发",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={pages} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass
    marker = "STOA跨期精选已完成；其余成果保留轻量目录"
    for row in catalog:
        if row.get("机构ID") == "eu-stoa" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            if marker not in row.get("原始资产状态", ""):
                row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(light_path, light, list(light[0]))
    ledger_path = root / "184_欧洲议会STOA科技创新与技术评估跨期精选全文台账.csv"
    result_path = root / "185_欧洲议会STOA科技创新与技术评估跨期精选全文结果.md"
    write_csv(ledger_path, ledger, list(ledger[0]))
    totals = {
        "bytes": sum(int(row["字节数"]) for row in ledger),
        "chars": sum(int(row["清洗文本字符数"]) for row in ledger),
        "pages": sum(int(row["页数"]) for row in ledger),
        "china": sum(int(row["China词形命中数"]) for row in ledger),
        "china_docs": sum(int(row["China词形命中数"]) > 0 for row in ledger),
    }
    result_path.write_text(
        "# 欧洲议会STOA科技创新与技术评估跨期精选全文结果\n\n"
        f"- 从243项近十年轻量目录中选择{len(ledger)}项跨期节点，保存欧洲议会RegData官方英文PDF、页面主体HTML、提取文本和科技创新切片。\n"
        f"- 共{totals['bytes']:,}字节、{totals['pages']}页、提取文本{totals['chars']:,}字符。\n"
        f"- {totals['china_docs']}份全文出现China/Chinese/PRC词形，共{totals['china']}次；目录未把一般第三国举例自动标记为中国科技核心材料。\n"
        "- 机制覆盖技术评估与科学前瞻、欧盟科研框架计划、区域创新差距、科研组织国际化、公共研发基础设施、关键使能技术、健康研发、产业机器人和关键原材料创新。\n"
        "- 战场技术、混合威胁、一般政治参与和纯法律治理材料未进入精选；相关成果继续保留在轻量目录。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} pdfs={len(ledger)} pages={totals['pages']} bytes={totals['bytes']} text_chars={totals['chars']} china_docs={totals['china_docs']} china_hits={totals['china']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
