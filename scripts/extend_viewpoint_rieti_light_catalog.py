from __future__ import annotations

import argparse
import csv
import json
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup

try:
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json
except ModuleNotFoundError:
    from extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json


BASE = "https://www.rieti.go.jp"
START = date(2016, 1, 1)
END = date(2026, 8, 23)
MONTHS = {name: index for index, name in enumerate(
          ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}
LIGHT_FIELDS = [
    "报告ID", "机构ID", "机构名称", "发布日期", "日期精度", "报告编号", "报告名称", "官方文类", "语言",
    "作者", "官方落地页", "官方PDF入口", "来源列表页", "科技创新相关度", "科技创新主轴", "中国直接信号",
    "全文策略", "获取日期",
]

CORE_PATTERN = re.compile(
    r"\bR\s*&\s*D\b|research and development|research spillover|science|scientific|innovation|innovativeness|"
    r"technolog|artificial intelligence|\bAI\b|robot|semiconductor|chip|patent|intellectual propert|"
    r"knowledge transfer|technology transfer|commerciali[sz]|digital transformation|digitization|digitali[sz]|"
    r"startup|start-up|entrepreneur|university.industry|research collaboration|science park|research infrastructure|"
    r"research grant|academic productivity|laborator|\bSTEM\b|researcher|scientist|digital platform|data flow", re.I,
)
SUPPORT_PATTERN = re.compile(
    r"productivity|intangible|manufactur|firm dynamics|business dynamism|industrial cluster|science park|"
    r"human capital|skill|workforce|green|decarbon|energy|data flow|data economy|platform|supply chain|value chain", re.I,
)
INNOVATION_BRIDGE_PATTERN = re.compile(
    r"scientific research|research grant|research collaboration|academic research|science|R\s*&\s*D|innovation|"
    r"technolog|patent|knowledge|digital|data flow|artificial intelligence|\bAI\b|robot|semiconductor|chip|"
    r"startup|start-up|entrepreneur|university|laborator|\bSTEM\b", re.I,
)
CHINA_PATTERN = re.compile(r"\bChina\b|\bChinese\b|\bPRC\b", re.I)
CHINA_MECHANISM_PATTERN = re.compile(
    r"science|scientific research|research collaboration|technolog|innovation|R\s*&\s*D|digital|data flow|artificial intelligence|\bAI\b|"
    r"semiconductor|chip|patent|robot|startup|university|scientist|researcher", re.I,
)
SECURITY_PATTERN = re.compile(
    r"security exception|economic security|export restriction|export control|sanction|geopolitical|trade war|"
    r"decoupl|embargo|economic statecraft|wolf warrior", re.I,
)
AXIS_PATTERNS = {
    "科学体系与科研能力": re.compile(r"science|scientific|research system|research collaboration|university|publication", re.I),
    "研发投入与创新政策": re.compile(r"R\s*&\s*D|research and development|innovation policy|industrial policy|subsid|public support|funding", re.I),
    "关键与新兴技术": re.compile(r"technolog|artificial intelligence|\bAI\b|robot|semiconductor|chip|biotech|digital|data", re.I),
    "产业创新与成果转化": re.compile(r"innovation|patent|commerciali[sz]|technology transfer|knowledge transfer|industr|manufactur|firm|startup|entrepreneur|productivity", re.I),
    "科技人才与技能": re.compile(r"talent|skill|human capital|workforce|researcher|scientist|education", re.I),
    "创新测量与政策方法": re.compile(r"measure|quantif|indicator|evaluation|impact|productivity|patent|evidence", re.I),
    "国际合作与中国比较": re.compile(r"international|global|cross-border|China|Chinese|Japan and|United States|Europe|Taiwan", re.I),
}


@dataclass(frozen=True)
class RietiItem:
    code: str
    published: str
    title: str
    authors: str
    landing_url: str
    pdf_url: str
    series: str
    source_url: str


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_listing_html(source: str, series: str, source_url: str) -> list[RietiItem]:
    soup = BeautifulSoup(source, "html.parser")
    items: list[RietiItem] = []
    for heading in soup.select("h3"):
        container = heading.parent
        date_node = container.select_one(":scope > p.date") if container else None
        title_link = heading.select_one("a[href]")
        pdf_link = container.select_one("li.dl a[href*=\".pdf\"]") if container else None
        author_node = container.select_one("li.name") if container else None
        if not date_node or not title_link or not pdf_link:
            continue
        date_text = normalize_space(date_node.get_text(" ", strip=True))
        match = re.search(r"(" + "|".join(MONTHS) + r")\s+(20\d{2})\s+(\d{2}-[EJP]-\d{3})\b", date_text)
        if not match:
            continue
        month, year, code = match.groups()
        published = f"{int(year):04d}-{MONTHS[month]:02d}-01"
        items.append(RietiItem(
            code=code, published=published, title=normalize_space(title_link.get_text(" ", strip=True)),
            authors=normalize_space(author_node.get_text(" ", strip=True) if author_node else ""),
            landing_url=urljoin(source_url, str(title_link.get("href", ""))),
            pdf_url=urljoin(source_url, str(pdf_link.get("href", ""))), series=series, source_url=source_url,
        ))
    return items


def is_catalog_candidate(title: str) -> bool:
    if CORE_PATTERN.search(title):
        return True
    if SUPPORT_PATTERN.search(title) and INNOVATION_BRIDGE_PATTERN.search(title):
        return True
    return bool(CHINA_PATTERN.search(title) and CHINA_MECHANISM_PATTERN.search(title))


def classify_relevance(title: str) -> tuple[str, list[str]]:
    axes = [axis for axis, pattern in AXIS_PATTERNS.items() if pattern.search(title)]
    if SECURITY_PATTERN.search(title):
        return "语境", axes
    if CORE_PATTERN.search(title):
        return "核心", axes
    return "支撑", axes


def source_specs() -> list[tuple[str, str, str]]:
    specs: list[tuple[str, str, str]] = []
    for fiscal_year in range(2015, 2026):
        specs.append((f"https://www.rieti.go.jp/en/publications/act_dp{fiscal_year}.html", "English Discussion Paper", f"dp_en_{fiscal_year}"))
        specs.append((f"https://www.rieti.go.jp/en/publications/act_dp_jp{fiscal_year}.html", "Japanese Discussion Paper", f"dp_ja_{fiscal_year}"))
    specs.extend([
        ("https://www.rieti.go.jp/en/publications/act_pdp.html", "English Policy Discussion Paper", "pdp_en"),
        ("https://www.rieti.go.jp/en/publications/act_pdp_jp.html", "Japanese Policy Discussion Paper", "pdp_ja"),
    ])
    return specs


def collect_official_pages() -> tuple[list[RietiItem], dict[str, str]]:
    entry = source_specs()[0][0]
    opened = _proxy_json("/new?url=" + quote(entry, safe=""))
    target = str(opened["targetId"])
    pages: dict[str, str] = {}
    items: list[RietiItem] = []
    try:
        for url, series, slug in source_specs():
            expression = """(async()=>{const r=await fetch(URL_VALUE,{credentials:'same-origin'});return JSON.stringify({status:r.status,html:await r.text()})})()""".replace("URL_VALUE", json.dumps(url))
            payload = json.loads(str(_eval(target, expression)))
            if int(payload["status"]) != 200:
                raise RuntimeError(f"RIETI listing HTTP {payload['status']}: {url}")
            html = str(payload["html"])
            parsed = parse_listing_html(html, series, url)
            if not parsed:
                raise RuntimeError(f"RIETI listing parsed no records: {url}")
            pages[slug] = html
            items.extend(parsed)
            print(f"rieti_source={slug} items={len(parsed)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass
    return items, pages


def normalize_items(items: list[RietiItem], acquired: str) -> list[dict[str, str]]:
    found: dict[str, RietiItem] = {}
    for item in items:
        published = datetime.strptime(item.published, "%Y-%m-%d").date()
        if START <= published <= END and is_catalog_candidate(item.title):
            found[item.code] = item
    rows: list[dict[str, str]] = []
    for item in found.values():
        relevance, axes = classify_relevance(item.title)
        rows.append({
            "报告ID": "C-JP-RIETI-" + item.code, "机构ID": "jp-rieti",
            "机构名称": "Research Institute of Economy, Trade and Industry (RIETI)",
            "发布日期": item.published, "日期精度": "月", "报告编号": item.code, "报告名称": item.title,
            "官方文类": item.series, "语言": "Japanese" if "Japanese" in item.series else "English",
            "作者": item.authors, "官方落地页": item.landing_url, "官方PDF入口": item.pdf_url,
            "来源列表页": item.source_url, "科技创新相关度": relevance, "科技创新主轴": "；".join(axes),
            "中国直接信号": "是" if CHINA_PATTERN.search(item.title) else "否",
            "全文策略": "轻量目录保留；按科技创新机制、中国比较和跨期增量精选全文", "获取日期": acquired,
        })
    return sorted(rows, key=lambda row: (row["发布日期"], row["报告ID"]))


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
        "报告ID": row["报告ID"], "机构ID": "jp-rieti", "机构英文名": row.get("机构名称", "RIETI"), "国家或地区": "Japan",
        "发布日期": row["发布日期"], "观察窗": "W1" if row["发布日期"][:4] <= "2018" else "W2" if row["发布日期"][:4] <= "2021" else "W3",
        "报告名称": row["报告名称"], "报告类型": row["官方文类"], "原文链接": row["官方落地页"],
        "正文完整度": "官方题名、作者、月份、摘要页与PDF入口已保存；正文按节点精选",
        "优先级": "P1-STI-catalog" if row["科技创新相关度"] == "核心" else "P3-context" if row["科技创新相关度"] == "语境" else "P2-STI-support",
        "示踪问题": row["科技创新主轴"], "机构观点等级": "RIETI讨论论文；观点按作者归因，不自动上升为机构立场",
        "样本角色": f"RIETI科技创新轻量目录/{row['官方文类']}", "编码状态": "轻量目录待筛选",
        "预期用途": "日本创新经济、研发投入、生产率、产业政策、技术扩散及中国比较",
        "本地原始资产路径": "", "原始资产状态": "RIETI官方摘要页与PDF入口已核验；等待精选全文触发",
    })
    return {field: result.get(field, "") for field in fields}


def merge_catalog_rows(existing: list[dict[str, str]], light_rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    if not fields:
        raise ValueError("The master catalog has no header")
    merged = [{field: row.get(field, "") for field in fields} for row in existing if row.get("机构ID") != "jp-rieti"]
    merged.extend(to_catalog(row, fields) for row in light_rows)
    merged.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Build RIETI technology innovation and China light catalog.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    acquired = date.today().isoformat()
    items, pages = collect_official_pages()
    rows = normalize_items(items, acquired)
    light_path = root / "194_RIETI科技创新与中国近十年轻量总目录.csv"
    result_path = root / "195_RIETI科技创新与中国近十年轻量总目录结果.md"
    write_csv(light_path, rows, LIGHT_FIELDS)
    html_dir = root / "03_证据底稿" / "网页原文"
    html_dir.mkdir(parents=True, exist_ok=True)
    for slug, html in pages.items():
        (html_dir / f"C-JP-RIETI-SOURCE-{slug.upper()}.html").write_text(html, encoding="utf-8", newline="\n")
    catalog_path = root / "05_报告总目录.csv"
    existing, fields = read_csv(catalog_path)
    write_csv(catalog_path, merge_catalog_rows(existing, rows, fields), fields)
    counts = {key: sum(row["科技创新相关度"] == key for row in rows) for key in ("核心", "支撑", "语境")}
    china = sum(row["中国直接信号"] == "是" for row in rows)
    languages = {key: sum(row["语言"] == key for row in rows) for key in ("English", "Japanese")}
    result_path.write_text(
        "# RIETI科技创新与中国近十年轻量总目录结果\n\n"
        f"- 扫描24个官方出版列表，保留2016—2026年科技创新或中国产业机制相关讨论论文{len(rows)}项。\n"
        f"- 核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；英文{languages['English']}项、日文{languages['Japanese']}项。\n"
        f"- {china}项题名具有中国直接信号。安全、制裁、出口限制与纯地缘政治题名降为语境或排除。\n"
        "- 讨论论文观点按作者归因；目录用于发现创新经济、研发、技术扩散、产业政策和中国比较方向。\n",
        encoding="utf-8",
    )
    print(f"rieti_light={len(rows)} core={counts['核心']} support={counts['支撑']} context={counts['语境']} china={china}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
