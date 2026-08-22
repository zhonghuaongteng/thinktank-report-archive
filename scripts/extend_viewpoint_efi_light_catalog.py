from __future__ import annotations

import argparse
import csv
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

try:
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json
except ModuleNotFoundError:
    from extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json


REPORTS_URL = "https://www.e-fi.de/en/publications/reports"
THEMATIC_URL = "https://www.e-fi.de/en/publications/reports/thematic-overview"
YEARS = set(range(2016, 2027))
LIGHT_FIELDS = [
    "报告ID", "机构ID", "机构名称", "发布日期", "日期精度", "报告名称", "章节编号", "官方文类",
    "专题分类", "官方落地页", "官方PDF入口", "科技创新相关度", "科技创新主轴", "中国直接信号",
    "全文策略", "获取日期",
]

CORE_PATTERN = re.compile(
    r"science|scientific|research|innovation|technolog|r\s*&\s*i|r\s*&\s*d|basic research|university|"
    r"artificial intelligence|\bai\b|quantum|robot|biotech|gene edit|digital|patent|knowledge transfer|"
    r"Forschung|Innovation|Technolog|Hochschul|Robotik|Fachpublikation|Patente|FuE", re.I,
)
SECURITY_PATTERN = re.compile(r"security-related|cybersecurity|military|defen[cs]e|export control", re.I)
CHINA_PATTERN = re.compile(r"\bChina\b|\bChinese\b|\bPRC\b|Germany and China", re.I)
AXIS_PATTERNS = {
    "科学体系与科研能力": re.compile(r"science|scientific|basic research|publication|university|higher education|research system|Hochschul|Fachpublikation", re.I),
    "研发投入与创新政策": re.compile(r"r\s*&\s*i|r\s*&\s*d|research and innovation|research funding|innovation policy|mission|Forschung|FuE|Finanzierung", re.I),
    "关键与新兴技术": re.compile(r"technolog|artificial intelligence|\bai\b|quantum|robot|biotech|gene edit|digital|autonomous", re.I),
    "产业创新与成果转化": re.compile(r"industry|industrial|business|enterprise|SME|start-up|market|transfer|commercial|cluster|Mittelstand|Unternehmen|Wirtschaft|Patente", re.I),
    "科技人才与技能": re.compile(r"talent|skill|education|mobility|researcher|scientist|qualification|Bildung|Qualifikation", re.I),
    "创新测量与政策方法": re.compile(r"indicator|evaluation|performance|productivity|publication|patent|evidence|causal|forecast|Fachpublikation", re.I),
    "国际合作与中国比较": re.compile(r"international|European|Europe|global|China|Chinese|mobility", re.I),
}


def normalize_space(value: str) -> str:
    value = (value or "").replace("�C", "–").replace("��", "’").replace("�", "")
    return re.sub(r"\s+", " ", value).strip()


def classify_relevance(title: str, topics: str) -> tuple[str, list[str]]:
    text = normalize_space(f"{title} {topics}")
    axes = [axis for axis, pattern in AXIS_PATTERNS.items() if pattern.search(text)]
    if SECURITY_PATTERN.search(title):
        return "语境", axes
    if CORE_PATTERN.search(title):
        return "核心", axes
    return "支撑", axes


def report_id(year: int, segment: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", segment.upper()).strip("-")
    return f"C-DE-EFI-{year}-{token}"


def normalize_chapters(raw: list[dict[str, str]], acquired: str) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, object]] = {}
    for item in raw:
        try:
            year = int(normalize_space(item.get("year", "")))
        except ValueError:
            continue
        url = normalize_space(item.get("url", ""))
        if year not in YEARS or not url.startswith("https://www.e-fi.de/fileadmin/") or ".pdf" not in url.lower():
            continue
        segment = normalize_space(item.get("segment", ""))
        key = url.lower()
        current = grouped.setdefault(key, {"year": year, "segment": segment, "title": normalize_space(item.get("title", "")), "url": url, "topics": set()})
        topic = normalize_space(item.get("topic", ""))
        if topic:
            current["topics"].add(topic)
    rows: list[dict[str, str]] = []
    for item in grouped.values():
        topics = "；".join(sorted(item["topics"]))
        title = str(item["title"])
        relevance, axes = classify_relevance(title, topics)
        year = int(item["year"])
        rows.append({
            "报告ID": report_id(year, str(item["segment"])), "机构ID": "de-efi",
            "机构名称": "Commission of Experts for Research and Innovation (EFI)",
            "发布日期": f"{year}-01-01", "日期精度": "年", "报告名称": title,
            "章节编号": str(item["segment"]), "官方文类": "EFI年度报告分章", "专题分类": topics,
            "官方落地页": THEMATIC_URL, "官方PDF入口": str(item["url"]),
            "科技创新相关度": relevance, "科技创新主轴": "；".join(axes),
            "中国直接信号": "是" if CHINA_PATTERN.search(f"{title} {topics}") else "否",
            "全文策略": "轻量目录保留；仅在跨期科技创新机制节点触发全文", "获取日期": acquired,
        })
    rows.sort(key=lambda row: (row["发布日期"], row["章节编号"], row["报告名称"]))
    ids = [row["报告ID"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("EFI chapter IDs are not unique; inspect official segment metadata")
    return rows


def normalize_annual_reports(raw: list[dict[str, str]], acquired: str) -> list[dict[str, str]]:
    rows = []
    for item in raw:
        match = re.search(r"(?:/|_)(20\d{2})(?:/|_|\.)", item.get("url", ""))
        if not match or int(match.group(1)) not in YEARS:
            continue
        year = int(match.group(1))
        rows.append({
            "报告ID": f"C-DE-EFI-{year}-REPORT", "机构ID": "de-efi",
            "机构名称": "Commission of Experts for Research and Innovation (EFI)",
            "发布日期": f"{year}-01-01", "日期精度": "年", "报告名称": f"EFI Report {year}",
            "章节编号": "REPORT", "官方文类": "EFI年度总报告", "专题分类": "年度综合评估",
            "官方落地页": REPORTS_URL, "官方PDF入口": normalize_space(item.get("url", "")),
            "科技创新相关度": "核心",
            "科技创新主轴": "科学体系与科研能力；研发投入与创新政策；关键与新兴技术；产业创新与成果转化",
            "中国直接信号": "否", "全文策略": "旗舰总报告目录保留；优先调用已精选的分章全文", "获取日期": acquired,
        })
    return sorted({row["报告ID"]: row for row in rows}.values(), key=lambda row: row["发布日期"])


def collect_official_records() -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
    opened = _proxy_json("/new?url=" + quote(THEMATIC_URL, safe=""))
    target = str(opened["targetId"])
    try:
        for _ in range(60):
            if int(_eval(target, "document.documentElement.outerHTML.length||0")) > 200000:
                break
            time.sleep(0.25)
        chapter_expr = """JSON.stringify([...document.querySelectorAll('.topic')].map(n=>({segment:n.querySelector('.segment')?.innerText||'',title:n.querySelector('.title')?.innerText||'',year:n.querySelector('.year')?.innerText||'',url:n.querySelector('a[href*=fileadmin]')?.href||'',topic:n.closest('.card')?.querySelector('.card-header')?.innerText||''})))"""
        chapters = json.loads(str(_eval(target, chapter_expr)))
        thematic_html = str(_eval(target, "document.documentElement.outerHTML"))
        _proxy_json("/navigate?target=" + target + "&url=" + quote(REPORTS_URL, safe=""))
        for _ in range(60):
            if "Report 2026" in str(_eval(target, "document.body?.innerText||''")):
                break
            time.sleep(0.25)
        annual_expr = r"""JSON.stringify([...document.querySelectorAll('a[href]')].filter(a=>{const h=a.href.toLowerCase();const t=(a.innerText||'').replace(/\s+/g,' ').trim().toLowerCase();return h.includes('/fileadmin/assets/gutachten/')&&h.includes('.pdf')&&t.startsWith('english')&&!t.includes('short version')}).map(a=>({url:a.href,label:(a.innerText||'').replace(/\s+/g,' ').trim()})))"""
        annual = json.loads(str(_eval(target, annual_expr)))
        return chapters, annual, thematic_html
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def to_catalog(row: dict[str, str], fields: list[str]) -> dict[str, str]:
    result = {field: "" for field in fields}
    result.update({
        "报告ID": row["报告ID"], "机构ID": "de-efi", "机构英文名": row.get("机构名称", "Commission of Experts for Research and Innovation (EFI)"), "国家或地区": "Germany",
        "发布日期": row["发布日期"], "观察窗": "W1" if row["发布日期"][:4] <= "2018" else "W2" if row["发布日期"][:4] <= "2021" else "W3",
        "报告名称": row["报告名称"], "报告类型": row["官方文类"], "原文链接": row["官方PDF入口"],
        "正文完整度": "官方题名、年份、专题分类与PDF入口已保存；正文按节点精选",
        "优先级": "P1-STI-catalog" if row["科技创新相关度"] == "核心" else "P3-context" if row["科技创新相关度"] == "语境" else "P2-STI-support",
        "示踪问题": row["科技创新主轴"], "机构观点等级": "EFI委员会年度报告正式判断",
        "样本角色": f"EFI近十年轻量总目录/{row['官方文类']}", "编码状态": "轻量目录待筛选",
        "预期用途": "德国国家创新体系、科研资助、技术发展、人才组织、成果转化及中国比较",
        "本地原始资产路径": "", "原始资产状态": "EFI官方PDF入口已核验；等待精选全文触发",
    })
    return {field: result.get(field, "") for field in fields}


def merge_catalog_rows(existing: list[dict[str, str]], light_rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    if not fields:
        raise ValueError("The master catalog has no header")
    rows = [{field: row.get(field, "") for field in fields} for row in existing if row.get("机构ID") != "de-efi"]
    rows.extend(to_catalog(row, fields) for row in light_rows)
    rows.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Build EFI 2016-2026 R&I light catalog.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    acquired = date.today().isoformat()
    chapters, annual, html = collect_official_records()
    rows = normalize_annual_reports(annual, acquired) + normalize_chapters(chapters, acquired)
    rows.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    light_path = root / "190_德国EFI研究创新近十年轻量总目录.csv"
    result_path = root / "191_德国EFI研究创新近十年轻量总目录结果.md"
    write_csv(light_path, rows, LIGHT_FIELDS)
    source_path = root / "03_证据底稿" / "网页原文" / "C-DE-EFI-THEMATIC-OVERVIEW.html"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(html, encoding="utf-8", newline="\n")
    catalog_path = root / "05_报告总目录.csv"
    existing, fields = read_csv(catalog_path)
    write_csv(catalog_path, merge_catalog_rows(existing, rows, fields), fields)
    chapters_count = sum(row["官方文类"] == "EFI年度报告分章" for row in rows)
    annual_count = sum(row["官方文类"] == "EFI年度总报告" for row in rows)
    context = sum(row["科技创新相关度"] == "语境" for row in rows)
    china = sum(row["中国直接信号"] == "是" for row in rows)
    result_path.write_text(
        "# 德国EFI研究创新近十年轻量总目录结果\n\n"
        f"- 保存2016—2026年{annual_count}份年度总报告与{chapters_count}个去重分章，共{len(rows)}项目录。\n"
        f"- {china}项具有中国直接信号；{context}项安全或相关边界材料仅保留为语境。\n"
        "- 目录用于识别德国科研体系、研发政策、关键技术、人才流动和成果转化议程；全文只选择跨期机制节点。\n",
        encoding="utf-8",
    )
    print(f"efi_light={len(rows)} annual={annual_count} chapters={chapters_count} china={china} context={context}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
