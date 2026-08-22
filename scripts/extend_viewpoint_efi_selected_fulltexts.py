from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

from pypdf import PdfReader

try:
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json
    from scripts.extend_viewpoint_eu_stoa_selected_fulltexts import browser_pdf
    from scripts.extend_viewpoint_efi_light_catalog import THEMATIC_URL
except ModuleNotFoundError:
    from extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json
    from extend_viewpoint_eu_stoa_selected_fulltexts import browser_pdf
    from extend_viewpoint_efi_light_catalog import THEMATIC_URL


SERIES_ROLE = "德国EFI研究创新跨期精选全文"


def _item(year: int, segment: str, title: str, axes: tuple[str, ...], role: str) -> dict[str, object]:
    return {"id": f"C-DE-EFI-{year}-{segment}", "date": f"{year}-01-01", "title": title, "axes": axes, "role": role}


SELECTED_ITEMS = (
    _item(2016, "B1", "The contribution of SMEs to research and innovation in Germany", ("研发投入与创新政策", "产业创新与成果转化"), "中小企业参与国家研发创新的基线"),
    _item(2017, "B2-1", "Transfer of knowledge and technology", ("产业创新与成果转化", "科学体系与科研能力"), "知识技术转移机制与产学连接节点"),
    _item(2018, "B3", "Autonomous systems", ("关键与新兴技术", "产业创新与成果转化"), "自主系统由研发走向产业应用的技术节点"),
    _item(2019, "A3", "Basic research funding structures and publications in international comparison", ("科学体系与科研能力", "研发投入与创新政策", "国际合作与中国比较"), "基础研究资助结构和科研产出的国际比较"),
    _item(2020, "B3", "Exchange of knowledge and technology between Germany and China", ("国际合作与中国比较", "产业创新与成果转化", "科技人才与技能"), "德中知识技术交流、合作与能力比较的直接材料"),
    _item(2021, "B1", "New Mission Orientation and Agility in R&I Policy", ("研发投入与创新政策", "创新测量与政策方法"), "使命导向创新政策及敏捷治理节点"),
    _item(2022, "B1", "Key Enabling Technologies and Technological Sovereignty", ("关键与新兴技术", "研发投入与创新政策"), "关键使能技术的政策组合和能力建设节点"),
    _item(2023, "B2", "Markets for Technology", ("产业创新与成果转化", "研发投入与创新政策"), "技术市场与成果转化机制节点"),
    _item(2024, "B2", "International Mobility in the Science and Innovation System", ("科技人才与技能", "国际合作与中国比较", "科学体系与科研能力"), "科研创新体系中的国际人才流动节点"),
    _item(2025, "B2", "Quantum Technologies", ("关键与新兴技术", "科学体系与科研能力", "国际合作与中国比较"), "量子科技科研、产业与国际位置的近期节点"),
    _item(2026, "B3", "Development and Application of Artificial Intelligence in Germany and Europe", ("关键与新兴技术", "产业创新与成果转化", "国际合作与中国比较"), "德国和欧洲人工智能研发与应用的最新节点"),
)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def extract_pdf_text(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n", len(reader.pages)


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = ("science", "research", "r&d", "innovation", "technology", "funding", "university", "transfer", "commercial", "industry", "talent", "mobility", "artificial intelligence", "quantum", "china", "chinese")
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 60]
    hits = [part for part in paragraphs if any(keyword in part.lower() for keyword in keywords)][:240]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 科技创新复用角色：{item['role']}\n"
        f"- 主轴：{'；'.join(item['axes'])}\n\n## 科学技术创新定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Save selected EFI R&I chapter fulltexts.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "190_德国EFI研究创新近十年轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light, light_fields = read_csv(light_path)
    catalog, catalog_fields = read_csv(catalog_path)
    light_by_id = {row["报告ID"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    missing = selected_ids - set(light_by_id)
    if missing:
        raise RuntimeError(f"selected EFI items missing from light catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        source = light_by_id[str(item["id"])]
        if source["发布日期"] != item["date"] or source["报告名称"] != item["title"]:
            raise RuntimeError(f"selected EFI metadata drift: {item['id']} {source['报告名称']!r}")
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    opened = _proxy_json("/new?url=" + quote(THEMATIC_URL, safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for _ in range(60):
            if "Thematic Overview" in str(_eval(target, "document.title")):
                break
            time.sleep(0.25)
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = str(item["id"])
            source = light_by_id[rid]
            pdf_url = source["官方PDF入口"]
            if not pdf_url.startswith("https://www.e-fi.de/fileadmin/"):
                raise RuntimeError(f"official EFI PDF missing: {rid}")
            pdf_path = pdf_dir / f"{rid}.pdf"
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            if not pdf_path.exists():
                pdf_path.write_bytes(browser_pdf(target, pdf_url))
            data = pdf_path.read_bytes()
            if not data.startswith(b"%PDF"):
                raise RuntimeError(f"invalid EFI PDF: {rid}")
            text, pages = extract_pdf_text(pdf_path)
            if len(text) < 500:
                raise RuntimeError(f"EFI text too short: {rid} {len(text)}")
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(selected_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            row = catalog_by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = "EFI官方分章PDF已保存；同时保存逐页提取文本和科技创新切片"
            row["优先级"] = "P1-STI-node"
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = str(item["role"])
            row["本地原始资产路径"] = str(pdf_path)
            row["原始资产状态"] = "EFI官方分章PDF已获取并校验"
            source["全文策略"] = "已进入精选全文；按官方PDF、提取文本和科技创新切片调用"
            ledger.append({
                "报告ID": rid, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
                "官方PDF入口": pdf_url, "本地原始PDF": str(pdf_path), "本地文本": str(text_path), "本地切片": str(slice_path),
                "页数": str(pages), "字节数": str(len(data)), "清洗文本字符数": str(len(text)),
                "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(data).hexdigest(),
                "科技创新主轴": "；".join(item["axes"]), "科技创新复用角色": str(item["role"]),
                "选择理由": "每年一个跨期科技创新机制节点；安全章节不触发全文", "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={pages} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass
    marker = "EFI跨期精选已完成；其余成果保留轻量目录"
    for row in catalog:
        if row.get("机构ID") == "de-efi" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            row["原始资产状态"] = marker
    write_csv(catalog_path, sorted(catalog, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", ""))), catalog_fields)
    write_csv(light_path, light, light_fields)
    ledger_path = root / "192_德国EFI研究创新跨期精选全文台账.csv"
    result_path = root / "193_德国EFI研究创新跨期精选全文结果.md"
    write_csv(ledger_path, ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_docs = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    result_path.write_text(
        "# 德国EFI研究创新跨期精选全文结果\n\n"
        f"- 从近十年轻量目录中按每年一个机制节点选择{len(ledger)}份官方分章PDF，共{totals['页数']:,}页、{totals['字节数']:,}字节、提取文本{totals['清洗文本字符数']:,}字符。\n"
        f"- {china_docs}份全文出现China/Chinese/PRC词形，共{totals['China词形命中数']:,}次。\n"
        "- 覆盖中小企业研发创新、知识技术转移、自主系统、基础研究资助、德中科技交流、使命导向、关键使能技术、技术市场、科研人才流动、量子科技与AI应用。\n"
        "- 安全研究章节仅保留在轻量目录，未进入精选全文。\n",
        encoding="utf-8",
    )
    print(f"efi_selected={len(ledger)} pages={totals['页数']} chars={totals['清洗文本字符数']} china_docs={china_docs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
