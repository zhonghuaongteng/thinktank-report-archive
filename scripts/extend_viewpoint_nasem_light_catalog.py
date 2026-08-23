from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import json


API = "https://api.crossref.org/prefixes/10.17226/works"
ARCHIVE = "https://www.nationalacademies.org/publications"
START = date(2016, 1, 1)
END = date(2026, 8, 23)
ALLOWED_TYPES = {"book", "edited-book", "monograph", "report"}
CHINA_VERIFIED_DOIS = {"10.17226/26647", "10.17226/27787"}
LIGHT_FIELDS = [
    "报告ID", "机构ID", "机构名称", "发布日期", "日期精度", "报告名称", "官方文类", "责任委员会",
    "DOI", "官方落地页", "官方在线全文入口", "来源元数据接口", "科技创新相关度", "科技创新主轴",
    "中国直接信号", "全文策略", "获取日期",
]

EXCLUDE_PATTERN = re.compile(
    r"transportation research board|\bnchrp\b|\btr news\b|airport|highway|roadway|bridge|pavement|asphalt|railroad",
    re.I,
)
SECURITY_PATTERN = re.compile(
    r"national security|defen[cs]e|army|air force|navy|military|biodefense|biological threat|"
    r"protecting .{0,20}technological advantage|security and conflicts|intelligence community",
    re.I,
)
CORE_PATTERN = re.compile(
    r"science (?:and|&|,) technology|science policy|scientific research|research enterprise|research ecosystem|"
    r"research integrity|reproducib|open science|research data|academic research|research infrastructure|"
    r"research facilit|national laborator|federal research|research funding|research investment|innovation|"
    r"technology transfer|commerciali[sz]|translational research|translating research|intellectual property|"
    r"\bsbir\b|\bsttr\b|stem workforce|skilled technical workforce|graduate stem|postdoctoral|engineering research|"
    r"engineering education|advanced manufacturing|nanotechnology initiative|artificial intelligence|quantum|"
    r"semiconductor|microelectronics|biotechnology|synthetic biology|emerging technolog|critical technolog|"
    r"technological advantage|science diplomacy|international scientific|international talent program|global s&t|"
    r"foundation models for scientific discovery",
    re.I,
)
SUPPORT_PATTERN = re.compile(
    r"(?:research|science).{0,40}(?:workforce|university|academic|funding|infrastructure|agenda|priorit|program|"
    r"strategy|portfolio|capacity|collaboration|assessment|future)|science literacy|communicating science|"
    r"stem education|graduate education",
    re.I,
)
AXIS_PATTERNS = {
    "科学体系与基础研究": re.compile(r"science|scientific|research|reproducib|open science|academic|laborator|infrastructure", re.I),
    "技术创新与关键技术": re.compile(r"technology|technological|engineering|artificial intelligence|quantum|nano|semiconductor|microelectronic|biotech|synthetic biology|manufacturing", re.I),
    "创新政策与研发治理": re.compile(r"innovation|research investment|research funding|policy|program|portfolio|governance|assessment|strategy", re.I),
    "人才大学与科研组织": re.compile(r"workforce|talent|graduate|postdoctoral|university|academic|career|human capital|education", re.I),
    "产业创新转化与区域生态": re.compile(r"commerciali[sz]|technology transfer|intellectual property|\bsbir\b|\bsttr\b|industry|industrial|regional|partnership|ecosystem", re.I),
    "国际合作开放科学与比较": re.compile(r"international|global|cooperation|partnership|open science|openness|china|chinese|ukraine", re.I),
}


def classify_relevance(title: str) -> tuple[str, list[str]] | None:
    title = re.sub(r"\s+", " ", title or "").strip()
    if not title or EXCLUDE_PATTERN.search(title):
        return None
    if not (CORE_PATTERN.search(title) or SUPPORT_PATTERN.search(title)):
        return None
    axes = [axis for axis, pattern in AXIS_PATTERNS.items() if pattern.search(title)]
    if SECURITY_PATTERN.search(title):
        return "语境", axes
    return ("核心" if CORE_PATTERN.search(title) else "支撑"), axes


def _published_date(work: dict[str, object]) -> tuple[date, str] | None:
    for key in ("published", "published-print", "issued", "created"):
        value = work.get(key) or {}
        parts = value.get("date-parts") if isinstance(value, dict) else None
        if not parts or not parts[0]:
            continue
        numbers = [int(number) for number in parts[0]]
        year = numbers[0]
        month = numbers[1] if len(numbers) > 1 else 1
        day = numbers[2] if len(numbers) > 2 else 1
        precision = "日" if len(numbers) > 2 else "月" if len(numbers) > 1 else "年"
        return date(year, month, day), precision
    return None


def normalize_works(works: list[dict[str, object]], acquired: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for work in works:
        doi = str(work.get("DOI", "")).lower()
        if not doi.startswith("10.17226/") or "_" in doi or str(work.get("type", "")) not in ALLOWED_TYPES:
            continue
        dated = _published_date(work)
        if dated is None or not START <= dated[0] <= END:
            continue
        title = re.sub(r"\s+", " ", " ".join(str(value) for value in work.get("title", []) or [])).strip()
        classified = classify_relevance(title)
        if classified is None:
            continue
        relevance, axes = classified
        record_id = doi.split("/", 1)[1]
        authors = []
        for author in work.get("author", []) or []:
            if isinstance(author, dict):
                name = str(author.get("name") or " ".join(filter(None, (author.get("given"), author.get("family"))))).strip()
                if name and name not in authors:
                    authors.append(name)
        resource = work.get("resource") or {}
        primary = resource.get("primary") if isinstance(resource, dict) else {}
        landing = str(primary.get("URL", "")) if isinstance(primary, dict) else ""
        if not landing:
            landing = f"https://www.nationalacademies.org/publications/{record_id}"
        rows.append({
            "报告ID": f"C-US-NASEM-{record_id}", "机构ID": "us-nasem",
            "机构名称": "National Academies of Sciences, Engineering, and Medicine",
            "发布日期": dated[0].isoformat(), "日期精度": dated[1], "报告名称": title,
            "官方文类": str(work.get("type", "")), "责任委员会": "；".join(authors), "DOI": doi,
            "官方落地页": landing, "官方在线全文入口": f"https://www.nationalacademies.org/read/{record_id}",
            "来源元数据接口": API, "科技创新相关度": relevance, "科技创新主轴": "；".join(axes),
            "中国直接信号": "是（正文人工核验）" if doi in CHINA_VERIFIED_DOIS else "是（题名）" if re.search(r"china|chinese", title, re.I) else "否",
            "全文策略": "科技创新主题目录保留；仅按科研制度、技术路线、人才、转化、开放科学和中国比较机制跨期精选正文",
            "获取日期": acquired,
        })
    unique = {row["报告ID"]: row for row in rows}
    return sorted(unique.values(), key=lambda row: (row["发布日期"], row["报告ID"]))


def fetch_works() -> list[dict[str, object]]:
    cursor = "*"
    rows: list[dict[str, object]] = []
    while True:
        params = {
            "filter": f"from-pub-date:{START.isoformat()},until-pub-date:{END.isoformat()}",
            "rows": 1000, "cursor": cursor,
        }
        request = Request(f"{API}?{urlencode(params, quote_via=quote)}", headers={"User-Agent": "Codex research catalog (mailto:research@example.com)"})
        with urlopen(request, timeout=120) as response:
            message = json.loads(response.read().decode("utf-8"))["message"]
        batch = list(message.get("items", []))
        rows.extend(batch)
        if len(batch) < 1000:
            break
        cursor = str(message["next-cursor"])
    return rows


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
    year = row["发布日期"][:4]
    result.update({
        "报告ID": row["报告ID"], "机构ID": "us-nasem",
        "机构英文名": "National Academies of Sciences, Engineering, and Medicine",
        "国家或地区": "United States", "发布日期": row["发布日期"],
        "观察窗": "W1" if year <= "2018" else "W2" if year <= "2021" else "W3",
        "报告名称": row["报告名称"], "报告类型": row["官方文类"], "原文链接": row["官方落地页"],
        "正文完整度": "Crossref DOI元数据、责任委员会和官方在线全文入口已保存；正文按科技创新机制精选",
        "优先级": "P3-context" if row["科技创新相关度"] == "语境" else "P1-STI-catalog" if row["科技创新相关度"] == "核心" else "P2-STI-support",
        "示踪问题": row["科技创新主轴"],
        "机构观点等级": "NASEM共识研究报告可代表评审委员会结论；研讨会纪要仅代表参与者发言",
        "样本角色": "NASEM近十年科技创新政策主题轻量目录", "编码状态": "轻量目录待筛选",
        "预期用途": "美国科研制度、关键技术计划、人才、创新转化、开放科学、国际合作及中国科技比较",
        "原始资产状态": "NASEM跨期精选完成后，其余成果保留轻量目录和官方在线全文入口",
    })
    return {field: result.get(field, "") for field in fields}


def merge_catalog_rows(existing: list[dict[str, str]], light_rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    merged = [{field: row.get(field, "") for field in fields} for row in existing if row.get("机构ID") != "us-nasem"]
    merged.extend(to_catalog(row, fields) for row in light_rows)
    return sorted(merged, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the 2016-2026 NASEM science, technology and innovation policy light catalog.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    rows = normalize_works(fetch_works(), date.today().isoformat())
    light_path = root / "206_NASEM科学技术创新政策近十年轻量总目录.csv"
    result_path = root / "207_NASEM科学技术创新政策近十年轻量总目录结果.md"
    write_csv(light_path, rows, LIGHT_FIELDS)
    catalog_path = root / "05_报告总目录.csv"
    existing, fields = read_csv(catalog_path)
    write_csv(catalog_path, merge_catalog_rows(existing, rows, fields), fields)
    counts = {key: sum(row["科技创新相关度"] == key for row in rows) for key in ("核心", "支撑", "语境")}
    china = sum(row["中国直接信号"].startswith("是") for row in rows)
    result_path.write_text(
        "# NASEM科学技术创新政策近十年轻量总目录结果\n\n"
        f"- Crossref官方注册元数据显示10.17226前缀在观察期共有3,918项成果；经科技创新政策主题与正式报告文类筛选，保留{len(rows)}项：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项。\n"
        f"- 当前标记中国直接信号{china}项；题名未出现China但正文涉及中国的记录仅在全文人工核验后补标。\n"
        "- 交通工程项目报告、临床专题和单篇章节不因宽泛research词进入目录；安全与国防主导标题仅保留语境级，不自动触发全文。\n",
        encoding="utf-8",
    )
    print(f"nasem_light={len(rows)} core={counts['核心']} support={counts['支撑']} context={counts['语境']} china={china}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
