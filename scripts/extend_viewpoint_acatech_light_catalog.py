from __future__ import annotations

import argparse
import csv
import html
import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API = "https://www.acatech.de/wp-json/wp/v2"
ARCHIVE = "https://www.acatech.de/publikationen/"
START = date(2016, 1, 1)
END = date(2026, 8, 23)
LIGHT_FIELDS = [
    "报告ID", "机构ID", "机构名称", "发布日期", "日期精度", "报告名称", "官方文类", "官方主题",
    "摘要", "官方落地页", "官方PDF入口", "来源列表页", "科技创新相关度", "科技创新主轴",
    "中国直接信号", "全文策略", "获取日期",
]

SECURITY_PATTERN = re.compile(
    r"security|sicherheit|militär|military|defen[cs]e|verteidigung|cyber|export control|"
    r"souveränität|sovereignty|resilien|lieferkette|supply chain|zivile und militärische",
    re.I,
)
CORE_PATTERN = re.compile(
    r"wissenschaft|science|forschung|research|engineering|technikwissenschaft|technolog|innovation|industrie 4\.0|"
    r"quant|biotech|kernfusion|fusion|robot|künstliche intelligenz|artificial intelligence|\bki\b|\bai\b|"
    r"halbleiter|mikroelektronik|material|produktion|manufactur|transfer|ausgründ|startup|start-up|fachkräft|kompetenz",
    re.I,
)
CHINA_PATTERN = re.compile(r"\bChina\b|chines|Volksrepublik China|Sino[- ]German|deutsch[- ]chines", re.I)
# 2786的正式PDF含独立中国章节，但WordPress摘要未列出China词形。
CHINA_DIRECT_IDS = {2786}
AXIS_PATTERNS = {
    "科学体系与基础研究": re.compile(r"wissenschaft|science|forschung|research|grundlagen|basic research|forschungsinfrastruktur", re.I),
    "技术创新与关键技术": re.compile(r"engineering|technikwissenschaft|technolog|industrie 4\.0|quant|biotech|kernfusion|robot|künstliche intelligenz|\bki\b|\bai\b|halbleiter|mikroelektronik", re.I),
    "创新政策与研发治理": re.compile(r"innovation|forschung und entwicklung|research and development|\bfu[e]?\b|\br&d\b|sprunginnovation|innovationssystem|politik|strategie", re.I),
    "人才大学与科研组织": re.compile(r"fachkräft|kompetenz|bildung|hochschul|universit|wissenschaftler|forscher|talent|workforce|skills|engineering in deutschland", re.I),
    "产业创新转化与区域生态": re.compile(r"transfer|industrie|produktion|wirtschaft|unternehmen|mittelstand|markt|ökosystem|ecosystem|ausgründ|startup|start-up|wertschöpf", re.I),
    "国际合作开放科学与比较": re.compile(r"international|global|zusammenarbeit|kooperation|vergleich|china|chines|europe|europä", re.I),
}


def clean_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def classify_relevance(title: str, excerpt: str = "") -> tuple[str, list[str]]:
    text = f"{title} {excerpt}"
    axes = [axis for axis, pattern in AXIS_PATTERNS.items() if pattern.search(text)]
    if SECURITY_PATTERN.search(title):
        return "语境", axes
    return ("核心" if CORE_PATTERN.search(text) else "支撑"), axes


def normalize_publications(
    items: list[dict[str, object]], formats: dict[int, str], topics: dict[int, str], acquired: str
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in items:
        published = datetime.fromisoformat(str(item["date"])).date()
        if not START <= published <= END:
            continue
        title = clean_html(str((item.get("title") or {}).get("rendered", "")))
        excerpt = clean_html(str((item.get("excerpt") or {}).get("rendered", "")))
        format_names = [formats.get(int(value), f"format-{value}") for value in item.get("format", [])]
        topic_names = [topics.get(int(value), f"topic-{value}") for value in item.get("topic", [])]
        relevance, axes = classify_relevance(title, excerpt)
        slug = str(item["slug"])
        landing = str(item["link"])
        rows.append({
            "报告ID": f"C-DE-ACATECH-{item['id']}", "机构ID": "de-acatech",
            "机构名称": "acatech – Deutsche Akademie der Technikwissenschaften",
            "发布日期": published.isoformat(), "日期精度": "日", "报告名称": title,
            "官方文类": "；".join(format_names) or "acatech publication", "官方主题": "；".join(topic_names),
            "摘要": excerpt, "官方落地页": landing,
            "官方PDF入口": f"https://www.acatech.de/publikation/{slug}/download-pdf?lang=de",
            "来源列表页": ARCHIVE, "科技创新相关度": relevance, "科技创新主轴": "；".join(axes),
            "中国直接信号": "是" if int(item["id"]) in CHINA_DIRECT_IDS or CHINA_PATTERN.search(f"{title} {excerpt}") else "否",
            "全文策略": "轻量目录保留；安全语境不自动触发全文，仅按科学与技术创新跨期机制精选",
            "获取日期": acquired,
        })
    return sorted(rows, key=lambda row: (row["发布日期"], row["报告ID"]))


def fetch_json(path: str, params: dict[str, object]) -> tuple[object, dict[str, str]]:
    url = f"{API}/{path}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 Codex research catalog"})
    with urlopen(request, timeout=90) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return json.loads(response.read().decode("utf-8")), headers


def fetch_taxonomy(name: str) -> dict[int, str]:
    data, _ = fetch_json(name, {"per_page": 100, "_fields": "id,name"})
    return {int(row["id"]): clean_html(str(row["name"])) for row in data}


def fetch_publications() -> list[dict[str, object]]:
    params = {
        "per_page": 100, "page": 1, "after": "2016-01-01T00:00:00", "before": "2026-08-24T00:00:00",
        "orderby": "date", "order": "desc", "_fields": "id,date,slug,link,title,excerpt,format,topic",
    }
    first, headers = fetch_json("publication", params)
    pages = int(headers.get("x-wp-totalpages", "1"))
    rows = list(first)
    for page in range(2, pages + 1):
        params["page"] = page
        batch, _ = fetch_json("publication", params)
        rows.extend(batch)
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
        "报告ID": row["报告ID"], "机构ID": "de-acatech", "机构英文名": "acatech",
        "国家或地区": "Germany", "发布日期": row["发布日期"],
        "观察窗": "W1" if year <= "2018" else "W2" if year <= "2021" else "W3",
        "报告名称": row["报告名称"], "报告类型": row["官方文类"], "原文链接": row["官方落地页"],
        "正文完整度": "官方题名、日期、文类、主题、摘要和PDF入口已保存；正文按科技创新机制精选",
        "优先级": "P3-context" if row["科技创新相关度"] == "语境" else "P1-STI-catalog" if row["科技创新相关度"] == "核心" else "P2-STI-support",
        "示踪问题": row["科技创新主轴"], "机构观点等级": "德国国家工程科学院正式出版物；合作出版物按共同机构归因",
        "样本角色": f"acatech近十年正式成果轻量目录/{row['官方文类']}", "编码状态": "轻量目录待筛选",
        "预期用途": "德国工程科学、关键技术、创新体系、科研人才、产业转化及中国技术比较",
        "原始资产状态": "acatech跨期精选已完成；其余正式成果保留轻量目录",
    })
    return {field: result.get(field, "") for field in fields}


def merge_catalog_rows(existing: list[dict[str, str]], light_rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    merged = [{field: row.get(field, "") for field in fields} for row in existing if row.get("机构ID") != "de-acatech"]
    merged.extend(to_catalog(row, fields) for row in light_rows)
    return sorted(merged, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the 2016-2026 official acatech light catalog.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    acquired = date.today().isoformat()
    raw = fetch_publications()
    rows = normalize_publications(raw, fetch_taxonomy("format"), fetch_taxonomy("topic"), acquired)
    light_path = root / "202_acatech科学与技术创新正式成果轻量总目录.csv"
    result_path = root / "203_acatech科学与技术创新正式成果轻量总目录结果.md"
    write_csv(light_path, rows, LIGHT_FIELDS)
    catalog_path = root / "05_报告总目录.csv"
    existing, fields = read_csv(catalog_path)
    write_csv(catalog_path, merge_catalog_rows(existing, rows, fields), fields)
    counts = {key: sum(row["科技创新相关度"] == key for row in rows) for key in ("核心", "支撑", "语境")}
    china = sum(row["中国直接信号"] == "是" for row in rows)
    result_path.write_text(
        "# acatech科学与技术创新正式成果轻量总目录结果\n\n"
        f"- 通过acatech官方WordPress出版接口保存2016—2026年{len(rows)}项正式出版物：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；中国直接信号{china}项。\n"
        "- 轻量目录保留官方档案的完整议题结构，关键词只承担标引；精选全文聚焦工程科学、技术研发、创新体系、人才与组织、产业转化及国际技术比较。\n"
        "- 安全、技术主权、韧性、军民融合和供应链题名保持目录级，不由关键词自动触发全文。\n",
        encoding="utf-8",
    )
    print(f"acatech_light={len(rows)} core={counts['核心']} support={counts['支撑']} context={counts['语境']} china={china}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
