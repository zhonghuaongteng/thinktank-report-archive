from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen


API = "https://publications.jrc.ec.europa.eu/repository/data/search/query"
LANDING = "https://publications.jrc.ec.europa.eu/repository/handle/"
BITSTREAM = "https://publications.jrc.ec.europa.eu/repository/bitstream/"
GROUPS = {"G001": "Science for policy", "G003": "Technical reports"}
YEARS = tuple(range(2016, 2027))
PAGE_SIZE = 500

LIGHT_FIELDS = [
    "报告ID", "机构ID", "机构名称", "发布日期", "日期精度", "报告名称", "官方文类", "官方出版组",
    "官方科学领域", "作者", "摘要", "DOI", "官方落地页", "官方PDF入口", "科技创新相关度",
    "科技创新主轴", "中国直接信号", "全文策略", "获取日期",
]

SCIENCE_AREAS = {"Innovation and growth", "Information society"}
STI_PATTERN = re.compile(
    r"\bscience|scientific|research|\bR&D\b|research and development|innovation|innovativeness|"
    r"technology|technological|digital transformation|artificial intelligence|\bAI\b|quantum|semiconductor|"
    r"biotechnology|robotics|advanced materials|patent|intellectual property|knowledge transfer|technology transfer|"
    r"university|universities|research infrastructure|laborator|skills intelligence|scientific excellence",
    re.I,
)
CORE_TITLE_PATTERN = re.compile(
    r"science|scientific|research|\bR&D\b|innovation|technology|technological|artificial intelligence|\bAI\b|"
    r"quantum|semiconductor|biotechnology|robot|advanced material|patent|knowledge transfer|technology transfer|"
    r"research infrastructure|industrial .*scoreboard|skills intelligence",
    re.I,
)
SECURITY_TITLE_PATTERN = re.compile(
    r"cyber.?threat|law enforcement|terroris|military|defen[cs]e|hybrid threat|border security|crime|"
    r"nuclear safeguards|security operation|surveillance",
    re.I,
)
CHINA_PATTERN = re.compile(r"\bChina\b|\bChinese\b|\bPRC\b|People['’]s Republic of China", re.I)

AXIS_PATTERNS = {
    "科学体系与科研能力": re.compile(r"science|scientific|research system|scientific excellence|research infrastructure|laborator|university", re.I),
    "研发投入与创新政策": re.compile(r"\bR&D\b|research and development|innovation policy|funding|investment scoreboard|framework programme", re.I),
    "关键与新兴技术": re.compile(r"technology|artificial intelligence|\bAI\b|quantum|semiconductor|biotechnology|robot|advanced material", re.I),
    "产业创新与成果转化": re.compile(r"industrial|industry|competitiveness|commerciali[sz]|technology transfer|knowledge transfer|startup|scale.?up", re.I),
    "科技人才与技能": re.compile(r"talent|skill|researcher|doctoral|career|mobility", re.I),
    "创新测量与政策方法": re.compile(r"indicator|scoreboard|foresight|horizon scanning|monitoring|evaluation|impact assessment|benchmark", re.I),
    "国际合作与中国比较": re.compile(r"international collaboration|global research|science diplomacy|\bChina\b|\bChinese\b|\bPRC\b", re.I),
}


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(part) for part in value]
    return [str(value)]


def _plain(value: object) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def item_text(item: dict[str, object]) -> str:
    return _plain(f"{item.get('dc.title', '')} {item.get('dc.description.abstract', '')}")


def science_areas(item: dict[str, object]) -> list[str]:
    return [_plain(value) for value in _as_list(item.get("extra.collection.science_area"))]


def is_catalog_candidate(item: dict[str, object]) -> bool:
    return bool(set(science_areas(item)) & SCIENCE_AREAS or STI_PATTERN.search(item_text(item)))


def classify_relevance(item: dict[str, object]) -> tuple[str, list[str]]:
    title = _plain(item.get("dc.title", ""))
    text = item_text(item)
    areas = set(science_areas(item))
    axes = [axis for axis, pattern in AXIS_PATTERNS.items() if pattern.search(text)]
    if SECURITY_TITLE_PATTERN.search(title) and not CORE_TITLE_PATTERN.search(title):
        return "语境", axes
    if CORE_TITLE_PATTERN.search(title) or "Innovation and growth" in areas:
        return "核心", axes
    if STI_PATTERN.search(text) or "Information society" in areas:
        return "支撑", axes
    return "语境", axes


def official_pdf_url(item: dict[str, object]) -> str:
    report_id = str(item.get("id", ""))
    candidates: list[tuple[bool, str]] = []
    for key, value in item.items():
        match = re.fullmatch(r"document\.(\d+)\.filename", key)
        if not match or not str(value).lower().endswith(".pdf"):
            continue
        document_id = match.group(1)
        main = str(item.get(f"document.{document_id}.main", "")) == "Y"
        mime = str(item.get(f"document.{document_id}.mimetype", ""))
        if mime and mime != "application/pdf":
            continue
        candidates.append((main, str(value)))
    if not candidates:
        return ""
    filename = unquote(sorted(candidates, key=lambda pair: (not pair[0], pair[1]))[0][1])
    return f"{BITSTREAM}{report_id}/{quote(filename)}"


def publication_date(item: dict[str, object]) -> tuple[str, str]:
    year = int(item.get("collection.year") or str(item.get("dc.date.issued", ""))[:4])
    issued = _plain(item.get("dc.date.issued", ""))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", issued):
        return issued, "日"
    return f"{year:04d}-01-01", "年"


def normalize_item(item: dict[str, object], acquired: str) -> dict[str, str]:
    report_id = str(item["id"])
    published, precision = publication_date(item)
    relevance, axes = classify_relevance(item)
    text = item_text(item)
    doi = _plain(item.get("dc.identifier.doi", ""))
    doi = re.sub(r"\s*\([^)]*\)\s*$", "", doi)
    return {
        "报告ID": f"C-EU-JRC-{report_id}",
        "机构ID": "eu-jrc",
        "机构名称": "European Commission Joint Research Centre",
        "发布日期": published,
        "日期精度": precision,
        "报告名称": _plain(item.get("dc.title", "")),
        "官方文类": _plain(item.get("resource_type.description", "")),
        "官方出版组": _plain(item.get("extra.collection.group", "")),
        "官方科学领域": "；".join(science_areas(item)),
        "作者": "；".join(_plain(value) for value in _as_list(item.get("dc.contributor.author"))),
        "摘要": _plain(item.get("dc.description.abstract", "")),
        "DOI": doi,
        "官方落地页": f"{LANDING}{report_id}",
        "官方PDF入口": official_pdf_url(item),
        "科技创新相关度": relevance,
        "科技创新主轴": "；".join(axes),
        "中国直接信号": "是" if CHINA_PATTERN.search(text) else "否",
        "全文策略": "总目录保留；等待科技创新机制增量与跨期节点筛选",
        "获取日期": acquired,
    }


def query_page(group: str, year: int, page: int) -> dict[str, object]:
    query = {
        "criteria": {"GROUP": group, "YEAR": str(year)},
        "sort": "date-desc", "page": page, "pageSize": PAGE_SIZE,
    }
    url = API + "?q=" + quote(json.dumps(query, separators=(",", ":"))) + "&count=false"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 CodexResearch/1.0"})
    for attempt in range(4):
        try:
            with urlopen(request, timeout=60) as response:
                payload = json.load(response)
            if payload.get("exitCode") != "SUCCESS":
                raise RuntimeError(f"JRC API failure: {payload.get('exitCode')}")
            return payload
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def collect_official_items() -> list[dict[str, object]]:
    found: dict[str, dict[str, object]] = {}
    for year in YEARS:
        for group in GROUPS:
            first = query_page(group, year, 1)
            total = int(first.get("totalItems", 0))
            pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            payloads = [first] + [query_page(group, year, page) for page in range(2, pages + 1)]
            for payload in payloads:
                for item in payload.get("items", []):
                    if isinstance(item, dict) and item.get("id"):
                        found[str(item["id"])] = item
            print(f"jrc_official year={year} group={group} total={total}", flush=True)
    return list(found.values())


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def to_catalog(row: dict[str, str], fields: list[str]) -> dict[str, str]:
    relevance = row["科技创新相关度"]
    priority = {"核心": "P1-STI-catalog", "支撑": "P2-STI-support", "语境": "P3-context"}[relevance]
    result = {field: "" for field in fields}
    result.update({
        "报告ID": row["报告ID"], "机构ID": "eu-jrc", "机构名称": row["机构名称"],
        "国家或地区": "European Union", "机构类型": "government_research_body",
        "报告名称": row["报告名称"], "发布日期": row["发布日期"], "观察窗": "W3",
        "报告类型": row["官方文类"] or row["官方出版组"], "作者": row["作者"],
        "官方链接": row["官方落地页"], "语言": "English", "来源类型": "JRC官方出版库",
        "来源入口": "JRC Publications Repository API", "机构观点等级": "机构正式研究；不必然代表欧委会政策立场",
        "优先级": priority, "主题": row["科技创新主轴"], "示踪问题": row["科技创新主轴"],
        "样本角色": f"JRC科技创新轻量目录/{relevance}", "编码状态": "轻量目录待筛选",
        "正文完整度": "官方元数据、摘要与附件入口已保存；正文未自动下载",
        "预期用途": "科学体系、技术创新、研发政策、产业转化与中国比较跨项目检索",
        "本地原始资产路径": "", "原始资产状态": "JRC官方元数据与PDF入口已核验；等待精选全文触发",
    })
    return {field: result.get(field, "") for field in fields}


def merge_catalog_rows(
    existing: list[dict[str, str]], light_rows: list[dict[str, str]], fields: list[str]
) -> list[dict[str, str]]:
    if not fields:
        raise ValueError("The master catalog has no header")
    kept = [
        {field: row.get(field, "") for field in fields}
        for row in existing
        if row.get("机构ID") != "eu-jrc"
    ]
    kept.extend(to_catalog(row, fields) for row in light_rows)
    kept.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    return kept


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a selective JRC science, technology and innovation light catalog.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    acquired = date.today().isoformat()
    official = collect_official_items()
    rows = [normalize_item(item, acquired) for item in official if is_catalog_candidate(item)]
    rows.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    light_path = root / "186_欧委会JRC科技创新政策近十年轻量总目录.csv"
    result_path = root / "187_欧委会JRC科技创新政策近十年轻量总目录结果.md"
    write_csv(light_path, rows, LIGHT_FIELDS)
    catalog_path = root / "05_报告总目录.csv"
    existing_catalog, catalog_fields = read_csv(catalog_path)
    catalog = merge_catalog_rows(existing_catalog, rows, catalog_fields)
    write_csv(catalog_path, catalog, catalog_fields)
    counts = {key: sum(row["科技创新相关度"] == key for row in rows) for key in ("核心", "支撑", "语境")}
    china = sum(row["中国直接信号"] == "是" for row in rows)
    pdfs = sum(bool(row["官方PDF入口"]) for row in rows)
    result_path.write_text(
        "# 欧委会JRC科技创新政策近十年轻量总目录结果\n\n"
        f"- 核验JRC官方出版库2016—2026年Science for policy与Technical reports共{len(official)}项，形成科技创新轻量目录{len(rows)}项。\n"
        f"- 科技创新核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；{china}项题名或摘要出现直接中国信号。\n"
        f"- {pdfs}项具有官方PDF入口。目录保留官方题名、摘要、作者、科学领域、DOI、落地页和附件入口。\n"
        "- 创新与增长、信息社会是主要官方领域；其他领域只有明确涉及科研体系、R&D、技术路线、人才、转化或创新测量时纳入。\n"
        "- 一般安全、执法、军事和纯风险治理材料最多标为语境，不因安全词形进入精选全文。\n",
        encoding="utf-8",
    )
    print(f"eu_jrc_light=ok official={len(official)} selected={len(rows)} core={counts['核心']} support={counts['支撑']} context={counts['语境']} china={china} pdf_links={pdfs} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
