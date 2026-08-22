from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


SITEMAP_URL = "https://www.nesta.org.uk/sitemap.xml"
WINDOW_START = date(2016, 1, 1)
WINDOW_END = date(2026, 8, 23)
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "发布日期", "报告名称", "摘要", "官方主题", "科学技术创新主题",
    "中国关联", "官方落地页", "官方PDF入口", "资料层级", "全文策略", "页面SHA256", "采集日期",
]


@dataclass(frozen=True)
class NestaReport:
    url: str
    title: str
    description: str
    published_date: date
    categories: tuple[str, ...]
    pdf_urls: tuple[str, ...]
    page_sha256: str


THEME_PATTERNS = {
    "科学体系与基础研究": re.compile(
        r"\b(?:science|scientific research|public research|research (?:system|systems|funding|policy|policies|"
        r"infrastructure|institution|institutions|collaboration|talent)|researcher|researchers|r\s*&\s*d|"
        r"university research|laborator(?:y|ies)|arpa)\b",
        re.I,
    ),
    "技术创新与关键技术": re.compile(
        r"\b(?:technolog(?:y|ies|ical)|artificial intelligence|ai|machine learning|robot(?:s|ics)?|automation|"
        r"digital|data science|biotech(?:nology)?|synthetic biology|quantum|engineering|manufactur(?:e|ing)|"
        r"climate tech|clean tech|energy innovation|makerspace|makerspaces)\b",
        re.I,
    ),
    "创新政策与研发治理": re.compile(
        r"\b(?:innovation polic(?:y|ies)|innovation system|innovation agenc(?:y|ies)|industrial strategy|"
        r"mission[- ](?:led|oriented)|challenge prize|innovation fund|innovation investment|innovation analytics|"
        r"innovation measurement|research policy|research funding|r\s*&\s*d polic(?:y|ies))\b",
        re.I,
    ),
    "人才大学与科研组织": re.compile(
        r"\b(?:research talent|researcher|scientist|stem skills?|technology skills?|digital skills?|university|universities)\b",
        re.I,
    ),
    "产业创新转化与区域生态": re.compile(
        r"\b(?:commerciali[sz]|technology transfer|innovation diffusion|innovation adoption|scale[- ]?ups?|startup|"
        r"entrepreneurship|innovative procurement|regional innovation|innovation cluster|industrial innovation)\b",
        re.I,
    ),
    "国际合作开放科学与比较": re.compile(
        r"\b(?:open science|research collaboration|science collaboration|international (?:research|innovation)|"
        r"global (?:science|innovation)|cross-border (?:research|innovation))\b",
        re.I,
    ),
}
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|sino[- ])", re.I)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def canonical_url(value: str) -> str:
    return value.strip().lower().replace("http://", "https://").rstrip("/")


def canonical_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(value).lower())


def parse_sitemap(source_xml: str) -> list[str]:
    urls = re.findall(r"<loc>([^<]+)</loc>", source_xml, flags=re.I)
    accepted: set[str] = set()
    for raw in urls:
        url = clean_text(raw)
        parsed = urlparse(url)
        if parsed.netloc.lower() not in {"nesta.org.uk", "www.nesta.org.uk"}:
            continue
        if not re.fullmatch(r"/report/[^/]+/", parsed.path):
            continue
        accepted.add(f"https://www.nesta.org.uk{parsed.path}")
    return sorted(accepted)


def _metadata_json(soup: BeautifulSoup) -> dict[str, object]:
    for node in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(node.get_text(strip=True))
        except (json.JSONDecodeError, TypeError):
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if isinstance(item, dict) and item.get("name"):
                return item
    return {}


def parse_report_page(source_html: str, url: str) -> NestaReport:
    soup = BeautifulSoup(source_html, "html.parser")
    metadata = _metadata_json(soup)
    title = clean_text(str(metadata.get("name", "")))
    description = clean_text(str(metadata.get("description", "")))
    if not title:
        heading = soup.select_one("h1")
        title = clean_text(heading.get_text(" ", strip=True) if heading else "")
    date_match = re.search(r"['\"]publishDate['\"]\s*:\s*['\"]([0-9]{4}-[0-9]{2}-[0-9]{2})", source_html)
    if not date_match:
        raise ValueError(f"missing publishDate: {url}")
    published = date.fromisoformat(date_match.group(1))
    area_match = re.search(r"['\"]areasOfWork['\"]\s*:\s*['\"]([^'\"]*)", source_html)
    categories = tuple(
        dict.fromkeys(
            clean_text(item)
            for item in re.split(r"\s*[,;|]\s*", html.unescape(area_match.group(1) if area_match else ""))
            if clean_text(item)
        )
    )
    pdfs = {
        urljoin(url, str(anchor.get("href")))
        for anchor in soup.select('a[href]')
        if re.search(r"\.pdf(?:$|[?#])", str(anchor.get("href", "")), re.I)
        and ("download" in " ".join(anchor.get("class", [])) or "/documents/" in str(anchor.get("href", "")))
    }
    return NestaReport(
        url=url,
        title=title,
        description=description,
        published_date=published,
        categories=categories,
        pdf_urls=tuple(sorted(pdfs)),
        page_sha256=hashlib.sha256(source_html.encode("utf-8")).hexdigest(),
    )


def science_innovation_themes(title: str, description: str, categories: tuple[str, ...]) -> tuple[str, ...]:
    evidence = " | ".join((title, description, *categories))
    return tuple(name for name, pattern in THEME_PATTERNS.items() if pattern.search(evidence))


def eligible_for_science_innovation_catalog(report: NestaReport) -> bool:
    if not WINDOW_START <= report.published_date <= WINDOW_END:
        return False
    substantive_text = " | ".join((report.title, report.description))
    return any(pattern.search(substantive_text) for pattern in THEME_PATTERNS.values())


def report_id(report: NestaReport) -> str:
    slug = urlparse(report.url).path.strip("/").split("/")[-1]
    token = re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")[:72]
    return f"C-NESTA-{report.published_date.year}-{token}"


def fetch_text(url: str, *, attempts: int = 3) -> str:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 CodexResearch/1.0"})
            with urlopen(request, timeout=35) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as error:  # network boundary is recorded by caller
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    root = args.research.resolve()
    sitemap = fetch_text(SITEMAP_URL)
    urls = parse_sitemap(sitemap)
    reports: list[NestaReport] = []
    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        pending = {executor.submit(fetch_text, url): url for url in urls}
        for index, future in enumerate(as_completed(pending), start=1):
            url = pending[future]
            try:
                report = parse_report_page(future.result(), url)
                if eligible_for_science_innovation_catalog(report):
                    reports.append(report)
            except Exception as error:
                failures.append((url, str(error)))
            if index % 100 == 0:
                print(f"processed={index}/{len(urls)} eligible={len(reports)} failures={len(failures)}", flush=True)

    reports.sort(key=lambda row: (row.published_date, row.title.lower(), row.url))
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    previous_ledger_path = root / "158_Nesta科技创新报告近十年轻量目录.csv"
    if previous_ledger_path.exists():
        previous_ids = {row["报告ID"] for row in read_csv(previous_ledger_path)}
        catalog = [
            row for row in catalog
            if not (
                row.get("报告ID") in previous_ids
                and row.get("机构ID") == "nesta"
                and not row.get("本地原始资产路径")
            )
        ]
    by_id = {row["报告ID"]: row for row in catalog}
    by_url = {canonical_url(row.get("原文链接", "")): row["报告ID"] for row in catalog if row.get("原文链接")}
    by_title_year = {
        (canonical_title(row.get("报告名称", "")), row.get("发布日期", "")[:4]): row["报告ID"]
        for row in catalog if row.get("报告名称")
    }
    ledger: list[dict[str, str]] = []
    added = linked = china_count = pdf_count = 0
    for report in reports:
        rid = report_id(report)
        unified = by_url.get(canonical_url(report.url)) or by_title_year.get(
            (canonical_title(report.title), str(report.published_date.year))
        ) or rid
        themes = science_innovation_themes(report.title, report.description, report.categories)
        is_china = bool(CHINA_PATTERN.search(" ".join((report.title, report.description))))
        if is_china:
            china_count += 1
        pdf_count += len(report.pdf_urls)
        if unified in by_id:
            linked += 1
        else:
            row = {
                "报告ID": rid,
                "机构ID": "nesta",
                "机构英文名": "Nesta",
                "国家或地区": "英国",
                "发布日期": report.published_date.isoformat(),
                "观察窗": "W1" if report.published_date.year <= 2018 else "W2" if report.published_date.year <= 2021 else "W3",
                "报告名称": report.title,
                "报告类型": "Nesta official report",
                "原文链接": report.url,
                "本地路径": "",
                "正文完整度": "官方落地页元数据；正文未批量下载",
                "优先级": "P1-China-tech-candidate" if is_china else "P2-light-catalog",
                "示踪问题": "；".join(themes + (("中国科技横向维度",) if is_china else ())),
                "机构观点等级": "机构正式报告，正文待核",
                "样本角色": "英国创新基金会科技创新与创新政策近十年轻量目录",
                "编码状态": "目录待筛选",
                "预期用途": "科学体系、技术创新、研发治理、人才组织、成果转化及中国比较",
                "本地原始资产路径": "",
                "原始资产状态": "官方落地页及PDF入口已保存；未下载全文",
            }
            catalog.append(row)
            by_id[rid] = row
            by_url[canonical_url(report.url)] = rid
            by_title_year[(canonical_title(report.title), str(report.published_date.year))] = rid
            added += 1
        ledger.append({
            "报告ID": rid,
            "统一目录报告ID": unified,
            "发布日期": report.published_date.isoformat(),
            "报告名称": report.title,
            "摘要": report.description,
            "官方主题": "；".join(report.categories),
            "科学技术创新主题": "；".join(themes),
            "中国关联": "是" if is_china else "否",
            "官方落地页": report.url,
            "官方PDF入口": "；".join(report.pdf_urls),
            "资料层级": "Nesta官方报告页轻量元数据",
            "全文策略": "不自动下载；仅跨期关键节点、中国科技专题或高复用方法报告进入全文复核",
            "页面SHA256": report.page_sha256,
            "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "158_Nesta科技创新报告近十年轻量目录.csv", ledger, LEDGER_FIELDS)
    year_counts = {year: sum(row.published_date.year == year for row in reports) for year in range(2016, 2027)}
    failure_preview = "\n".join(f"- {url}: {message}" for url, message in failures[:20]) or "- 无"
    result = f"""# Nesta科技创新报告近十年轻量目录增补结果

- 官方站点报告页：{len(urls)}项；2016—2026年科技创新主题命中：{len(reports)}项。
- 与既有目录关联：{linked}项；新增统一总目录：{added}项；目录更新后共{len(catalog)}项。
- 年度分布：{'；'.join(f'{year}年{count}项' for year, count in year_counts.items())}。
- 中国科技横向关联：{china_count}项；识别官方PDF入口：{pdf_count}个；本轮未批量下载正文。
- 页面解析失败：{len(failures)}项；站点地图SHA256：`{hashlib.sha256(sitemap.encode('utf-8')).hexdigest()}`。

## 采集边界

目录只使用报告题名、官方摘要和官方主题识别科学、技术、研发、创新政策、科研人才与成果转化。安全、韧性、供应链或治理词本身不能触发收录。轻量目录用于观察关注方向；机构立场与因果判断须回查本地全文。

全文继续执行选择性策略：优先跨期可比、直接解释科研与创新机制、具有明确中国科技关联或能被其他项目复用的方法型报告。

## 页面解析缺口（最多列示20项）

{failure_preview}
"""
    (root / "159_Nesta科技创新报告近十年轻量目录结果.md").write_text(result, encoding="utf-8")
    print(
        f"pages={len(urls)} eligible={len(reports)} linked={linked} added={added} "
        f"china={china_count} pdf_links={pdf_count} failures={len(failures)} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
