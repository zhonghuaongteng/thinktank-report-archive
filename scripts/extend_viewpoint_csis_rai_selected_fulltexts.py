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
    from scripts.extend_viewpoint_csis_rai_light_catalog import CATALOG_FIELDS, CDP_PROXY, PROGRAM_URL, _proxy_json
except ModuleNotFoundError:
    from extend_viewpoint_csis_rai_light_catalog import CATALOG_FIELDS, CDP_PROXY, PROGRAM_URL, _proxy_json


SERIES_ROLE = "CSIS RAI科学技术创新机制与中国比较跨期精选全文"


def _item(report_id: str, published: str, title: str, axes: tuple[str, ...], role: str, china: bool = False) -> dict[str, object]:
    return {"id": report_id, "date": published, "title": title, "axes": axes, "role": role, "china": china}


SELECTED_ITEMS = (
    _item("C-CSIS-RAI-2021-WHY-RENEWING-AMERICAN-INNOVATION-ENDLESS-FRONTIER-ACT-AND-BIDENS-BID-MAINTAINING-US-GLOBAL", "2021-04-14", "Why Renewing American Innovation? The “Endless Frontier Act” and Biden’s Bid for Maintaining U.S. Global Competitiveness", ("科学体系与研发投入", "研发治理与科研组织"), "RAI项目发端期对科研投资、区域创新与国家创新体系的议程定义", True),
    _item("C-CSIS-RAI-2021-US-COMPETITIVENESS-WHERE-DO-WE-STAND-WHAT-DO-WE-DO-NOW", "2021-06-22", "U.S. Competitiveness: Where Do We Stand? What Do We Do Now?", ("科学体系与研发投入", "技术创新与产业转化"), "以生产率、研发、产业能力和公共投资诊断美国创新竞争力"),
    _item("C-CSIS-RAI-2021-WINNING-TECH-TALENT-COMPETITION", "2021-10-28", "Winning the Tech Talent Competition", ("科技人才与创新生态", "关键与通用技术"), "科技人才培养、吸引和留用的制度竞争节点", True),
    _item("C-CSIS-RAI-2022-WILL-AMERICA-SQUANDER-ITS-NEW-SPUTNIK-MOMENT", "2022-01-19", "Will America Squander Its New Sputnik Moment?", ("科学体系与研发投入", "研发治理与科研组织"), "CHIPS and Science语境下联邦科研投资与组织能力的转折节点", True),
    _item("C-CSIS-RAI-2022-UNTAPPED-INNOVATION", "2022-05-25", "Untapped Innovation?", ("科技人才与创新生态", "技术创新与产业转化"), "创新参与、发明者供给和包容性创新的人才基础"),
    _item("C-CSIS-RAI-2023-CHINAS-DRIVE-LEADERSHIP-GLOBAL-RESEARCH-AND-DEVELOPMENT", "2023-06-30", "China's Drive for Leadership in Global Research and Development", ("科学体系与研发投入",), "中国研发投入规模、全球占比与美国相对位置的直接比较", True),
    _item("C-CSIS-RAI-2023-IMPLEMENTING-CHIPS-ACT-SEMATECHS-LESSONS-NATIONAL-SEMICONDUCTOR-TECHNOLOGY-CENTER", "2023-05-19", "Implementing the CHIPS Act: Sematech’s Lessons for the National Semiconductor Technology Center", ("研发治理与科研组织", "关键与通用技术"), "用Sematech经验解释国家半导体技术中心的治理和产学研协同"),
    _item("C-CSIS-RAI-2023-INCLUSIVE-INNOVATION-US-ECONOMIC-GROWTH-AND-RESILIENCY", "2023-05-30", "Inclusive Innovation for U.S. Economic Growth and Resiliency", ("科技人才与创新生态", "技术创新与产业转化"), "扩大创新参与和区域扩散的制度机制"),
    _item("C-CSIS-RAI-2023-QUANTUM-CANT-BE-BUSINESS-USUAL-ISSUES-REAUTHORIZATION-NATIONAL-QUANTUM-INITIATIVE-ACT", "2023-08-17", "Quantum Can't Be Business as Usual: Issues for the Reauthorization of the National Quantum Initiative Act", ("研发治理与科研组织", "关键与通用技术"), "国家量子计划从科研投入走向组织协调和产业转化的政策节点"),
    _item("C-CSIS-RAI-2024-FRENCH-MODEL-COOPERATIVE-SEMICONDUCTOR-RESEARCH-LESSONS-CEA-LETI", "2024-02-16", "The French Model for Cooperative Semiconductor Research: Lessons from CEA-Leti", ("研发治理与科研组织", "关键与通用技术"), "合作研究机构连接基础研究、工程验证和企业应用的组织模型"),
    _item("C-CSIS-RAI-2024-INVESTING-SCIENCE-AND-TECHNOLOGY", "2024-06-18", "Investing in Science and Technology", ("科学体系与研发投入", "关键与通用技术"), "中美研发投入与科技机构能力比较的核心报告", True),
    _item("C-CSIS-RAI-2024-UNDERSTANDING-US-BIOPHARMACEUTICAL-INNOVATION-ECOSYSTEM", "2024-08-15", "Understanding the U.S. Biopharmaceutical Innovation Ecosystem", ("技术创新与产业转化", "关键与通用技术"), "生物医药从基础研究、知识产权到制造和市场的创新生态链", True),
    _item("C-CSIS-RAI-2024-IMEC-WORLD-LEADING-COOPERATIVE-RESEARCH-CENTER-MICROELECTRONICS", "2024-10-08", "Imec: A World-Leading Cooperative Research Center for Microelectronics", ("研发治理与科研组织", "关键与通用技术"), "开放合作型微电子研发平台及其公共投入和产业协作机制"),
    _item("C-CSIS-RAI-2025-ALBANY-NANOTECHS-POTENTIAL-SUPPORT-NATIONAL-SEMICONDUCTOR-TECHNOLOGY-CENTER", "2025-02-14", "Albany NanoTech’s Potential to Support the National Semiconductor Technology Center", ("研发治理与科研组织", "关键与通用技术"), "国家级共享研发基础设施与半导体技术转化平台"),
    _item("C-CSIS-RAI-2025-NETHERLANDS-INNOVATION-LANDSCAPE", "2025-08-29", "The Netherlands’ Innovation Landscape", ("科技人才与创新生态", "技术创新与产业转化"), "区域创新生态、研究机构和高技术企业协同的国际比较"),
    _item("C-CSIS-RAI-2025-INNOVATION-LIGHTBULB-EXAMINING-CHINAS-STRATEGIC-REGIONAL-INNOVATION-AND-RD-DISTRIBUTION", "2025-07-28", "Innovation Lightbulb: Examining China’s Strategic Regional Innovation and R&D Distribution", ("科学体系与研发投入", "科技人才与创新生态"), "中国区域研发空间分布和创新集群布局的直接材料", True),
    _item("C-CSIS-RAI-2025-PUBLIC-AND-PRIVATE-RD-ARE-COMPLEMENTS-NOT-SUBSTITUTES", "2025-08-20", "Public and Private R&D Are Complements—Not Substitutes", ("科学体系与研发投入", "技术创新与产业转化"), "公共研发与企业研发互补关系及其创新外溢机制", True),
    _item("C-CSIS-RAI-2025-COMPETING-CHINAS-PUBLIC-RD-MODEL-LESSONS-AND-RISKS-US-INNOVATION-STRATEGY", "2025-09-17", "Competing with China’s Public R&D Model: Lessons and Risks for U.S. Innovation Strategy", ("科学体系与研发投入", "研发治理与科研组织"), "中美公共研发模式及国家创新战略的直接比较", True),
    _item("C-CSIS-RAI-2026-UNDERSTANDING-CHINAS-QUEST-QUANTUM-ADVANCEMENT", "2026-01-29", "Understanding China’s Quest for Quantum Advancement", ("研发治理与科研组织", "关键与通用技术"), "中国量子科研、人才、平台和产业转化体系的专题分析", True),
    _item("C-CSIS-RAI-2026-LEVERAGING-SBIR-QUANTUM-COMMERCIALIZATION-AND-SUPPLY-CHAIN-GROWTH", "2026-03-30", "Leveraging SBIR for Quantum Commercialization and Supply Chain Growth", ("技术创新与产业转化", "关键与通用技术"), "用小企业创新研究机制推动量子技术商业化和供应能力"),
    _item("C-CSIS-RAI-2026-POWERING-INNOVATION-DATA-CENTERS-COMPUTE-AND-US-COMPETITIVENESS", "2026-08-11", "Powering Innovation: Data Centers, Compute, and U.S. Competitiveness", ("技术创新与产业转化", "关键与通用技术"), "算力基础设施约束、扩张机制与创新竞争力"),
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


def official_pdf_urls(urls: list[str]) -> list[str]:
    return list(dict.fromkeys(url for url in urls if url.startswith("https://csis-website-prod.s3.amazonaws.com/") and ".pdf" in url.lower()))


def page_detail(target: str, url: str) -> tuple[str, str, list[str]]:
    _proxy_json("/navigate?target=" + target + "&url=" + quote(url, safe=""))
    for _ in range(40):
        title = str(_eval(target, "document.title"))
        text_len = int(_eval(target, "document.querySelector('main')?.innerText.length||0"))
        if title and "稍候" not in title and "Just a moment" not in title and text_len >= 300:
            break
        time.sleep(0.25)
    expression = """(() => {const main=document.querySelector('main');return {title:document.title,html:main?.outerHTML||'',text:main?.innerText||'',pdfs:[...document.querySelectorAll('a[href]')].map(a=>a.href).filter(h=>h.toLowerCase().includes('.pdf'))}})()"""
    value = _eval(target, expression)
    if not isinstance(value, dict) or len(str(value.get("text", ""))) < 300:
        raise RuntimeError(f"thin or blocked CSIS page: {url}")
    return str(value.get("html", "")), str(value.get("text", "")), official_pdf_urls([str(x) for x in value.get("pdfs", [])])


def _range_fetch(target: str, url: str, start: int, end: int) -> tuple[int, str, bytes]:
    expression = """(async()=>{const r=await fetch(URL_VALUE,{headers:{Range:RANGE_VALUE}});const b=new Uint8Array(await r.arrayBuffer());let s='';for(let i=0;i<b.length;i+=32768){s+=String.fromCharCode(...b.subarray(i,i+32768))}return {status:r.status,range:r.headers.get('content-range')||'',data:btoa(s)}})()"""
    expression = expression.replace("URL_VALUE", json.dumps(url)).replace("RANGE_VALUE", json.dumps(f"bytes={start}-{end}"))
    value = _eval(target, expression)
    if not isinstance(value, dict):
        raise RuntimeError(f"unexpected CSIS PDF response: {url}")
    return int(value.get("status", 0)), str(value.get("range", "")), base64.b64decode(str(value.get("data", "")))


def browser_pdf(target: str, url: str) -> bytes:
    chunk_size = 1_500_000
    status, content_range, first = _range_fetch(target, url, 0, chunk_size - 1)
    if status == 200:
        data = first
    elif status == 206:
        total_match = re.search(r"/(\d+)$", content_range)
        chunks = [first]
        total = int(total_match.group(1)) if total_match else None
        start = chunk_size
        while total is None or start < total:
            next_status, next_range, part = _range_fetch(target, url, start, start + chunk_size - 1)
            if next_status == 416:
                break
            if next_status != 206:
                raise RuntimeError(f"unexpected PDF range status {next_status}: {url}")
            chunks.append(part)
            if total is None:
                next_total = re.search(r"/(\d+)$", next_range)
                total = int(next_total.group(1)) if next_total else None
            start += chunk_size
            if total is None and len(part) < chunk_size:
                break
        data = b"".join(chunks)
        if total is not None and len(data) != total:
            raise RuntimeError(f"incomplete PDF download: expected {total}, found {len(data)}")
    else:
        raise RuntimeError(f"CSIS PDF request failed with status {status}: {url}")
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"CSIS attachment is not a PDF: {url}")
    return data


def extract_pdf_text(data: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(data))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n", len(reader.pages)


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = (
        "science", "scientific", "research", "r&d", "innovation", "technology", "talent", "workforce",
        "commercial", "university", "laboratory", "infrastructure", "semiconductor", "quantum", "china", "chinese",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 70]
    hits = [part for part in paragraphs if any(word in part.lower() for word in keywords)][:180]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 科技创新复用角色：{item['role']}\n"
        f"- 主轴：{'；'.join(item['axes'])}\n\n## 科学技术创新与中国定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Save a selective CSIS RAI science and technology innovation full-text layer through the browser.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "178_CSIS_RAI科技创新项目轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light = read_csv(light_path)
    catalog = read_csv(catalog_path)
    light_by_id = {row["报告ID"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    missing = selected_ids - set(light_by_id)
    if missing:
        raise RuntimeError(f"selected CSIS RAI items missing from light catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        source = light_by_id[str(item["id"])]
        if source["发布日期"] != item["date"] or source["报告名称"] != item["title"]:
            raise RuntimeError(f"selected CSIS RAI metadata drift: {item['id']}")
    html_dir = root / "03_证据底稿" / "网页原文"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (html_dir, pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    opened = _proxy_json("/new?url=" + quote(PROGRAM_URL, safe=""))
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
            main_html, page_text, pdf_urls = page_detail(target, url)
            html_path.write_text(main_html, encoding="utf-8", newline="\n")
            pdf_url = pdf_urls[0] if pdf_urls else ""
            pages = 0
            if pdf_url:
                if pdf_path.exists():
                    pdf_data = pdf_path.read_bytes()
                else:
                    pdf_data = browser_pdf(target, pdf_url)
                    pdf_path.write_bytes(pdf_data)
                text, pages = extract_pdf_text(pdf_data)
                asset_path = pdf_path
                asset_data = pdf_data
                asset_type = "官方PDF"
            else:
                text = re.sub(r"\n{3,}", "\n\n", page_text).strip() + "\n"
                asset_path = html_path
                asset_data = main_html.encode("utf-8")
                asset_type = "官方网页正文"
            if len(text) < 300:
                raise RuntimeError(f"CSIS RAI selected text too short: {rid} {len(text)}")
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(selected_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            row = catalog_by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = f"{asset_type}已保存；同时保存官方页面主体HTML、清洗文本和科技创新切片"
            row["优先级"] = "P0-China-STI-node" if item["china"] else "P1-STI-node"
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = str(item["role"])
            row["本地原始资产路径"] = str(asset_path)
            row["原始资产状态"] = f"{asset_type}已获取并校验；官方页面主体HTML同步保存"
            source["中国直接信号"] = "是" if item["china"] else source["中国直接信号"]
            source["全文策略"] = "已进入精选全文；按本地官方PDF或网页正文、清洗文本和科技创新切片调用"
            ledger.append({
                "报告ID": rid, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
                "官方内容类型": source["官方内容类型"], "官方子类型": source["官方子类型"], "官方落地页": url,
                "官方PDF入口": pdf_url, "本地原始资产": str(asset_path), "本地页面HTML": str(html_path),
                "本地文本": str(text_path), "本地切片": str(slice_path), "资产类型": asset_type,
                "页数": str(pages), "字节数": str(len(asset_data)), "清洗文本字符数": str(len(text)),
                "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(asset_data).hexdigest(),
                "中国直接信号": "是" if item["china"] else "否", "科技创新主轴": "；".join(item["axes"]),
                "科技创新复用角色": str(item["role"]), "选择理由": "跨期节点；直接解释科学、技术与创新机制；安全议题仅在改变创新能力时纳入",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} asset={asset_type} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass
    marker = "CSIS RAI跨期精选已完成；其余Report/Article保留轻量目录"
    for row in catalog:
        if row.get("机构ID") == "csis-rai" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            if marker not in row.get("原始资产状态", ""):
                row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(light_path, light, list(light[0]))
    write_csv(root / "180_CSIS_RAI科学技术创新机制与中国比较跨期精选全文台账.csv", ledger, list(ledger[0]))
    totals = {
        "bytes": sum(int(row["字节数"]) for row in ledger), "chars": sum(int(row["清洗文本字符数"]) for row in ledger),
        "pages": sum(int(row["页数"]) for row in ledger), "pdfs": sum(row["资产类型"] == "官方PDF" for row in ledger),
        "china": sum(int(row["China词形命中数"]) for row in ledger), "direct": sum(row["中国直接信号"] == "是" for row in ledger),
    }
    (root / "181_CSIS_RAI科学技术创新机制与中国比较跨期精选全文结果.md").write_text(
        "# CSIS RAI科学技术创新机制与中国比较跨期精选全文结果\n\n"
        f"- 从176项Report/Article轻量目录中选择{len(ledger)}项跨期节点，保存官方原始资产、页面主体HTML、清洗文本和科技创新切片。\n"
        f"- 原始资产含PDF {totals['pdfs']}份、网页正文{len(ledger)-totals['pdfs']}份，共{totals['bytes']:,}字节、PDF {totals['pages']}页、清洗文本{totals['chars']:,}字符。\n"
        f"- 直接中国比较节点{totals['direct']}项，全文China/Chinese/PRC词形命中{totals['china']}次。\n"
        "- 机制覆盖联邦科研投入、公共与企业R&D互补、科研与产业协作平台、科技人才、包容性和区域创新、半导体与量子转化、算力基础设施。\n"
        "- 工业间谍、一般出口管制、军事技术和安全机构评论未进入精选；相关题名仅在项目轻量目录中保留。\n"
        "- 项目实际资料始于2021年，跨期分析据此建立2021—2026序列，不向2016—2020回填推定立场。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} pdfs={totals['pdfs']} pages={totals['pages']} bytes={totals['bytes']} text_chars={totals['chars']} direct_china={totals['direct']} china_hits={totals['china']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
