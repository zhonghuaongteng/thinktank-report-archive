from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


BASE_URL = "https://www.rathenau.nl"
ARCHIVE_URL = BASE_URL + "/en/knowledge-base?type=report&page={}"
WINDOW_START = date(2016, 1, 1)
WINDOW_END = date(2026, 8, 23)
BOUNDARY_TITLE = "R&D goes global"
CHINA_FACTSHEET = {
    "date": "2025-06-02",
    "theme": "Science in figures",
    "title": "China: a scientific superpower in the making",
    "type": "Factsheet",
    "url": BASE_URL + "/en/science-figures/process/collaboration/china-scientific-superpower-making",
}
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "发布日期", "报告名称", "报告类型", "官方主题", "科技创新相关度",
    "中国关联", "官方落地页", "官方PDF入口", "页面摘要", "资料层级", "全文策略", "页面SHA256", "采集日期",
]


@dataclass(frozen=True)
class RathenauItem:
    date: str
    theme: str
    title: str
    content_type: str
    url: str
    pdf_urls: tuple[str, ...] = ()
    description: str = ""
    page_sha256: str = ""


CORE_PATTERN = re.compile(
    r"(?:science system|scientific|research(?:ers?| grants?| programmes?| and innovation| policy| organisations?)|"
    r"r\s*&\s*d|innovation|open science|university|universities|doctoral|doctorate|generative ai|artificial intelligence|"
    r"synthetic cells?|genome editing|bio-?manufacturing|neurotechnology|embryo|technology assessment)", re.I,
)
SUPPORT_PATTERN = re.compile(
    r"(?:digitalisation|digitisation|data centres?|virtual reality|\bvr\b|speech technology|immersive technolog|"
    r"robot|sensors?|algae oil|potatoes|radioactive waste|health technology|medical technolog)", re.I,
)
CONTEXT_PATTERN = re.compile(
    r"(?:cyberspace|cyber resilience|digital threats|digital democracy|e-democracy|harmful behaviour|deepfakes?|"
    r"human rights|ballot box|inclusive online|fair share|beyond control)", re.I,
)
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|sino[- ])", re.I)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def parse_listing_page(source_html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(source_html, "html.parser")
    rows: list[dict[str, str]] = []
    for article in soup.select("article.node--report.node--view-mode-teaser"):
        link = article.select_one("h3.teaser__heading a[href]")
        stamp = article.select_one("time[datetime]")
        if not link or not stamp:
            continue
        theme = article.select_one(".theme-label")
        content_type = article.select_one("p.label")
        rows.append({
            "date": str(stamp.get("datetime", ""))[:10],
            "theme": clean_text(theme.get_text(" ", strip=True) if theme else ""),
            "title": clean_text(link.get_text(" ", strip=True)),
            "type": clean_text(content_type.get_text(" ", strip=True) if content_type else "Report"),
            "url": urljoin(BASE_URL, str(link.get("href", ""))),
        })
    return rows


def is_light_catalog_item(item: dict[str, str]) -> bool:
    if item.get("type") != "Report":
        return False
    published = date.fromisoformat(item["date"])
    if WINDOW_START <= published <= WINDOW_END:
        return True
    return item.get("title") == BOUNDARY_TITLE and published == date(2015, 10, 19)


def classify_relevance(title: str, theme: str, summary: str) -> str:
    text = " | ".join((title, theme, summary))
    if CONTEXT_PATTERN.search(title) and not CORE_PATTERN.search(title):
        return "语境"
    if CORE_PATTERN.search(text):
        return "核心"
    if SUPPORT_PATTERN.search(text):
        return "支撑"
    return "语境"


def canonical_url(value: str) -> str:
    return value.strip().lower().replace("http://", "https://").rstrip("/")


def canonical_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(value).lower())


def report_id(item: RathenauItem) -> str:
    if item.url == CHINA_FACTSHEET["url"]:
        return "C-RATHENAU-2025-CHINA-SCIENTIFIC-SUPERPOWER"
    slug = urlparse(item.url).path.rstrip("/").split("/")[-1]
    token = re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")[:72]
    return f"C-RATHENAU-{item.date[:4]}-{token}"


def parse_detail_page(source_html: str, listed: dict[str, str]) -> RathenauItem:
    soup = BeautifulSoup(source_html, "html.parser")
    canonical = soup.select_one('link[rel="canonical"]')
    url = str(canonical.get("href")) if canonical and canonical.get("href") else listed["url"]
    description = ""
    meta = soup.select_one('meta[name="description"]')
    if meta:
        description = clean_text(str(meta.get("content", "")))
    if not description:
        summary = soup.select_one(".field--name-field-summary, .article-header__intro, main .text-long")
        description = clean_text(summary.get_text(" ", strip=True) if summary else "")[:2000]
    pdfs = {
        urljoin(BASE_URL, str(anchor.get("href")))
        for anchor in soup.select('a[href]')
        if re.search(r"\.pdf(?:$|[?#])", str(anchor.get("href", "")), re.I)
        and "/sites/default/files/" in str(anchor.get("href", ""))
    }
    return RathenauItem(
        date=listed["date"], theme=listed["theme"], title=listed["title"], content_type=listed["type"],
        url=url, pdf_urls=tuple(sorted(pdfs)), description=description,
        page_sha256=hashlib.sha256(source_html.encode("utf-8")).hexdigest(),
    )


def fetch_text(url: str, *, attempts: int = 3) -> str:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 CodexResearch/1.0"})
            with urlopen(request, timeout=45) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as error:
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
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.research.resolve()

    listed: dict[str, dict[str, str]] = {}
    archive_hashes: list[str] = []
    for page in range(6):
        source = fetch_text(ARCHIVE_URL.format(page))
        archive_hashes.append(hashlib.sha256(source.encode("utf-8")).hexdigest())
        for item in parse_listing_page(source):
            if is_light_catalog_item(item):
                listed[canonical_url(item["url"])] = item
    listed[canonical_url(CHINA_FACTSHEET["url"])] = dict(CHINA_FACTSHEET)

    reports: list[RathenauItem] = []
    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        pending = {executor.submit(fetch_text, item["url"]): item for item in listed.values()}
        for future in as_completed(pending):
            item = pending[future]
            try:
                reports.append(parse_detail_page(future.result(), item))
            except Exception as error:
                failures.append((item["url"], str(error)))
    reports.sort(key=lambda row: (row.date, row.title.lower(), row.url))

    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    previous_path = root / "162_Rathenau英文正式报告近十年轻量总目录.csv"
    if previous_path.exists():
        previous_ids = {row["报告ID"] for row in read_csv(previous_path)}
        catalog = [
            row for row in catalog
            if not (row.get("报告ID") in previous_ids and row.get("机构ID") == "rathenau" and not row.get("本地原始资产路径"))
        ]
    by_id = {row["报告ID"]: row for row in catalog}
    by_url = {canonical_url(row.get("原文链接", "")): row["报告ID"] for row in catalog if row.get("原文链接")}
    by_title_year = {
        (canonical_title(row.get("报告名称", "")), row.get("发布日期", "")[:4]): row["报告ID"]
        for row in catalog if row.get("报告名称")
    }
    ledger: list[dict[str, str]] = []
    added = linked = china_count = 0
    relevance_counts = {"核心": 0, "支撑": 0, "语境": 0}
    for item in reports:
        rid = report_id(item)
        unified = by_url.get(canonical_url(item.url)) or by_title_year.get((canonical_title(item.title), item.date[:4])) or rid
        relevance = classify_relevance(item.title, item.theme, item.description)
        relevance_counts[relevance] += 1
        is_china = bool(CHINA_PATTERN.search(" ".join((item.title, item.description)))) or item.url == CHINA_FACTSHEET["url"]
        china_count += int(is_china)
        if unified in by_id:
            linked += 1
        else:
            catalog.append({
                "报告ID": rid, "机构ID": "rathenau", "机构英文名": "Rathenau Instituut", "国家或地区": "荷兰",
                "发布日期": item.date, "观察窗": "W1" if int(item.date[:4]) <= 2018 else "W2" if int(item.date[:4]) <= 2021 else "W3",
                "报告名称": item.title, "报告类型": f"Rathenau official {item.content_type.lower()}", "原文链接": item.url,
                "本地路径": "", "正文完整度": "官方落地页元数据；正文未批量下载",
                "优先级": "P1-China-STI-candidate" if is_china else "P2-light-catalog" if relevance != "语境" else "P3-context-catalog",
                "示踪问题": f"科技创新相关度={relevance}" + ("；中国科技横向维度" if is_china else ""),
                "机构观点等级": "机构正式出版物，正文待核", "样本角色": "荷兰技术评估与科学创新政策近十年轻量总目录",
                "编码状态": "目录待筛选", "预期用途": "科学体系、技术创新、研发治理、科研组织、产业转化及中国比较",
                "本地原始资产路径": "", "原始资产状态": "官方落地页及附件入口已保存；未下载全文",
            })
            by_id[rid] = catalog[-1]
            added += 1
        ledger.append({
            "报告ID": rid, "统一目录报告ID": unified, "发布日期": item.date, "报告名称": item.title,
            "报告类型": item.content_type, "官方主题": item.theme, "科技创新相关度": relevance,
            "中国关联": "是" if is_china else "否", "官方落地页": item.url, "官方PDF入口": "；".join(item.pdf_urls),
            "页面摘要": item.description, "资料层级": "Rathenau官方英文出版页轻量元数据",
            "全文策略": "总目录保留；核心跨期节点、中国科技比较或高复用机制报告进入全文层",
            "页面SHA256": item.page_sha256, "采集日期": date.today().isoformat(),
        })

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "162_Rathenau英文正式报告近十年轻量总目录.csv", ledger, LEDGER_FIELDS)
    failure_preview = "\n".join(f"- {url}: {message}" for url, message in failures[:20]) or "- 无"
    (root / "163_Rathenau英文正式报告近十年轻量总目录结果.md").write_text(
        "# Rathenau英文正式报告近十年轻量总目录结果\n\n"
        f"- 2016—2026正式英文报告及前序边界、中国科学专题共{len(reports)}项；新增统一目录{added}项，关联既有目录{linked}项。\n"
        f"- 科技创新相关度：核心{relevance_counts['核心']}项、支撑{relevance_counts['支撑']}项、语境{relevance_counts['语境']}项；中国关联{china_count}项。\n"
        f"- 官方PDF入口合计{sum(len(item.pdf_urls) for item in reports)}个；本阶段只保存目录元数据。\n"
        "- 语境类报告保留题名以观察机构议题边界，不因安全、网络冲突、平台治理或民主议题自动进入全文层。\n"
        f"- 页面解析失败{len(failures)}项；六页归档哈希：`{'；'.join(archive_hashes)}`。\n\n"
        "## 页面解析缺口\n\n" + failure_preview + "\n",
        encoding="utf-8",
    )
    print(
        f"light={len(reports)} added={added} linked={linked} china={china_count} "
        f"core={relevance_counts['核心']} support={relevance_counts['支撑']} context={relevance_counts['语境']} "
        f"failures={len(failures)} catalog={len(catalog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
