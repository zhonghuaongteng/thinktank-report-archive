from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


TIMELINE_URL = "https://royalsociety.org/news-resources/projects/uk-research-and-innovation/most-recent/"
JINA_PREFIX = "https://r.jina.ai/http://"
START = date(2016, 1, 1)
END = date(2026, 8, 23)
LIGHT_FIELDS = [
    "报告ID", "机构ID", "机构名称", "发布日期", "日期精度", "报告名称", "官方文类", "语言",
    "官方落地页", "官方PDF入口", "来源列表页", "科技创新相关度", "科技创新主轴", "中国直接信号",
    "全文策略", "获取日期",
]

MONTHS = {name: index for index, name in enumerate(
    ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1
)}

FORMAL_TYPES = ("Report", "Policy briefing", "Factsheet", "Factsheets", "Conference report")
TIMELINE_PATTERN = re.compile(
    r"(?m)^(\d{1,2}) (" + "|".join(MONTHS) + r") (20\d{2}) (" + "|".join(FORMAL_TYPES) +
    r")\[([^\]]+)\]\((https?://[^)]+)\)"
)
SECURITY_PATTERN = re.compile(r"security|state threats|defen[cs]e|cyber|export control|sanction|dual[- ]use", re.I)
CORE_PATTERN = re.compile(
    r"science|scientific|research|R&D|innovation|translation|technolog|machine learning|artificial intelligence|\bAI\b|"
    r"data science|workforce|skills|absorptive capacity|laborator|university|funding|economy", re.I,
)
AXIS_PATTERNS = {
    "科学体系与基础研究": re.compile(r"science|scientific|research system|research culture|research organisation|research organization|infrastructure", re.I),
    "技术创新与关键技术": re.compile(r"technolog|machine learning|artificial intelligence|\bAI\b|data science|digital|biodiversity", re.I),
    "创新政策与研发治理": re.compile(r"R&D|research and development|innovation|funding|investment|economy|policy|manifesto|science 2040", re.I),
    "人才大学与科研组织": re.compile(r"workforce|skills|talent|visa|immigration|mobility|culture|university|organisation|organization", re.I),
    "产业创新转化与区域生态": re.compile(r"translation|absorptive|cluster|region|economy|industry|commercial|innovation", re.I),
    "国际合作开放科学与比较": re.compile(r"international|China|Chinese|Horizon Europe|EU research|Ukraine|collaboration|global", re.I),
}
CHINA_PATTERN = re.compile(r"China|Chinese|CAS-RS|China-UK", re.I)


@dataclass(frozen=True)
class RoyalSocietyItem:
    published: str
    kind: str
    title: str
    url: str
    source_url: str
    pdf_url: str = ""


SUPPLEMENTAL_ITEMS = (
    RoyalSocietyItem("2017-04-25", "Report", "Machine learning: the power and promise of computers that learn by example", "https://royalsociety.org/news-resources/projects/machine-learning/", "https://royalsociety.org/news-resources/projects/machine-learning/", "https://royalsociety.org/-/media/policy/projects/machine-learning/publications/machine-learning-report.pdf"),
    RoyalSocietyItem("2019-05-08", "Report", "Dynamics of data science skills", "https://royalsociety.org/news-resources/projects/dynamics-of-data-science/", "https://royalsociety.org/news-resources/projects/dynamics-of-data-science/", "https://royalsociety.org/-/media/policy/projects/dynamics-of-data-science/dynamics-of-data-science-skills-report.pdf"),
    RoyalSocietyItem("2020-12-03", "Report", "Digital technology and the planet: harnessing computing to achieve net zero", "https://royalsociety.org/news-resources/projects/digital-technology-and-the-planet/", "https://royalsociety.org/news-resources/projects/digital-technology-and-the-planet/", "https://royalsociety.org/-/media/policy/projects/digital-technology-and-the-planet/digital-technology-and-the-planet-report.pdf"),
    RoyalSocietyItem("2023-01-23", "Report", "From privacy to partnership: the role of Privacy Enhancing Technologies in data governance and collaborative analysis", "https://royalsociety.org/news-resources/projects/privacy-enhancing-technologies/", "https://royalsociety.org/news-resources/projects/privacy-enhancing-technologies/", "https://royalsociety.org/-/media/policy/projects/privacy-enhancing-technologies/from-privacy-to-partnership.pdf"),
    RoyalSocietyItem("2024-05-28", "Report", "Science in the age of AI", "https://royalsociety.org/news-resources/projects/science-in-the-age-of-ai/", "https://royalsociety.org/news-resources/projects/science-in-the-age-of-ai/", "https://royalsociety.org/-/media/policy/projects/science-in-the-age-of-ai/science-in-the-age-of-ai-report.pdf"),
    RoyalSocietyItem("2025-06-23", "Report", "Disability technology", "https://royalsociety.org/news-resources/projects/disability-technology/", "https://royalsociety.org/news-resources/projects/disability-technology/"),
    RoyalSocietyItem("2026-06-26", "Conference report", "2026 China-UK Science Policy Dialogue on food systems and biodiversity loss", "https://royalsociety.org/news-resources/publications/2026/2026-china-uk-dialogue/", "https://royalsociety.org/news-resources/publications/", "https://royalsociety.org/-/media/policy/publications/2026/joint-statement.pdf"),
    RoyalSocietyItem("2026-07-24", "Conference report", "2026 CAS-RS AI ethics workshop: Ethical considerations in physical AI systems", "https://royalsociety.org/news-resources/publications/2026/ai-ethics-workshop-2026/", "https://royalsociety.org/news-resources/publications/"),
)


def parse_timeline_markdown(source: str, source_url: str = TIMELINE_URL) -> list[RoyalSocietyItem]:
    rows: list[RoyalSocietyItem] = []
    for day, month, year, kind, title, url in TIMELINE_PATTERN.findall(source):
        published = f"{int(year):04d}-{MONTHS[month]:02d}-{int(day):02d}"
        normalized_url = url.replace("http://royalsociety.org/", "https://royalsociety.org/")
        rows.append(RoyalSocietyItem(
            published, kind, re.sub(r"\s+", " ", title).strip(), normalized_url, source_url,
            normalized_url if urlparse(normalized_url).path.lower().endswith(".pdf") else "",
        ))
    return rows


def classify_relevance(title: str) -> tuple[str, list[str]]:
    axes = [axis for axis, pattern in AXIS_PATTERNS.items() if pattern.search(title)]
    if SECURITY_PATTERN.search(title):
        return "语境", axes
    return ("核心" if CORE_PATTERN.search(title) else "支撑"), axes


def item_id(item: RoyalSocietyItem) -> str:
    slug = re.sub(r"[^A-Z0-9]+", "-", item.title.upper()).strip("-")[:44]
    digest = hashlib.sha1(item.url.encode("utf-8")).hexdigest()[:6].upper()
    return f"C-UK-RS-{item.published[:4]}-{slug}-{digest}"


def normalize_items(items: list[RoyalSocietyItem], acquired: str) -> list[dict[str, str]]:
    found: dict[str, RoyalSocietyItem] = {}
    for item in items:
        published = datetime.strptime(item.published, "%Y-%m-%d").date()
        if START <= published <= END:
            found[item.url.rstrip("/").lower()] = item
    rows = []
    for item in found.values():
        relevance, axes = classify_relevance(item.title)
        rows.append({
            "报告ID": item_id(item), "机构ID": "uk-royal-society", "机构名称": "The Royal Society",
            "发布日期": item.published, "日期精度": "日", "报告名称": item.title, "官方文类": item.kind,
            "语言": "English", "官方落地页": item.url, "官方PDF入口": item.pdf_url,
            "来源列表页": item.source_url, "科技创新相关度": relevance, "科技创新主轴": "；".join(axes),
            "中国直接信号": "是" if CHINA_PATTERN.search(item.title) else "否",
            "全文策略": "轻量目录保留；仅按科学体系、技术创新、中国科研合作和跨期增量精选全文",
            "获取日期": acquired,
        })
    return sorted(rows, key=lambda row: (row["发布日期"], row["报告ID"]))


def fetch_markdown(url: str) -> str:
    jina_url = JINA_PREFIX + url.removeprefix("https://").removeprefix("http://")
    request = Request(jina_url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=90) as response:
        text = response.read().decode("utf-8")
    if len(text) < 1000:
        raise RuntimeError(f"Royal Society source too short: {url}")
    return text


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
    year = row["发布日期"][:4]
    result = {field: "" for field in fields}
    result.update({
        "报告ID": row["报告ID"], "机构ID": "uk-royal-society", "机构英文名": "The Royal Society",
        "国家或地区": "United Kingdom", "发布日期": row["发布日期"],
        "观察窗": "W1" if year <= "2018" else "W2" if year <= "2021" else "W3",
        "报告名称": row["报告名称"], "报告类型": row["官方文类"], "原文链接": row["官方落地页"],
        "正文完整度": "官方题名、日期、文类与入口已保存；正文按科学技术创新节点精选",
        "优先级": "P3-context" if row["科技创新相关度"] == "语境" else "P1-STI-catalog" if row["科技创新相关度"] == "核心" else "P2-STI-support",
        "示踪问题": row["科技创新主轴"], "机构观点等级": "英国国家科学院正式报告、政策简报或专题材料；联合报告按共同机构归因",
        "样本角色": f"英国皇家学会科学技术创新专题目录/{row['官方文类']}", "编码状态": "轻量目录待筛选",
        "预期用途": "科学体系、研发投入、科研人才、成果转化、AI赋能科学及中英科研合作",
        "本地原始资产路径": "", "原始资产状态": "Royal Society官方入口已保存；跨期精选完成后其余成果保留轻量目录",
    })
    return {field: result.get(field, "") for field in fields}


def merge_catalog_rows(existing: list[dict[str, str]], light_rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    merged = [{field: row.get(field, "") for field in fields} for row in existing if row.get("机构ID") != "uk-royal-society"]
    merged.extend(to_catalog(row, fields) for row in light_rows)
    return sorted(merged, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a science-and-technology-first Royal Society thematic catalog.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    timeline = fetch_markdown(TIMELINE_URL)
    rows = normalize_items(parse_timeline_markdown(timeline) + list(SUPPLEMENTAL_ITEMS), date.today().isoformat())
    light_path = root / "198_英国皇家学会科学技术创新专题轻量总目录.csv"
    result_path = root / "199_英国皇家学会科学技术创新专题轻量总目录结果.md"
    write_csv(light_path, rows, LIGHT_FIELDS)
    source_dir = root / "03_证据底稿" / "网页原文"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "C-UK-RS-SOURCE-UK-RI-TIMELINE.md").write_text(timeline, encoding="utf-8", newline="\n")
    catalog_path = root / "05_报告总目录.csv"
    existing, fields = read_csv(catalog_path)
    write_csv(catalog_path, merge_catalog_rows(existing, rows, fields), fields)
    counts = {key: sum(row["科技创新相关度"] == key for row in rows) for key in ("核心", "支撑", "语境")}
    china = sum(row["中国直接信号"] == "是" for row in rows)
    result_path.write_text(
        "# 英国皇家学会科学技术创新专题轻量总目录结果\n\n"
        f"- 收录{len(rows)}项2016—2026年官方正式成果：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；中国直接信号{china}项。\n"
        "- 范围由英国研究与创新专题官方时间线，加上机器学习、数据科学、数字技术、AI赋能科学和中英科学合作等经核验专题构成。该目录是科技创新专题目录，不宣称覆盖皇家学会全部出版物。\n"
        "- 安全议题只保留为科研与创新条件变化的语境；不单独触发全文。精选全文围绕科学体系、研发投入、人才与科研组织、技术形成、成果转化和国际科研合作。\n",
        encoding="utf-8",
    )
    print(f"royal_society_light={len(rows)} core={counts['核心']} support={counts['支撑']} context={counts['语境']} china={china}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
