from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


BASE_URL = "https://ifp.org"
API_URL = BASE_URL + "/wp-json/wp/v2"
TARGET_CATEGORIES = {"Metascience", "High-Skilled Immigration", "Biotechnology", "Emerging Technology"}
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "WordPress文章ID", "发布日期", "报告名称", "官方栏目", "科技创新相关度",
    "中国关联", "官方落地页", "官方PDF入口", "页面摘要", "正文字符数", "资料层级", "全文策略", "正文SHA256", "采集日期",
]


@dataclass(frozen=True)
class IfpItem:
    post_id: int
    date: str
    slug: str
    url: str
    title: str
    excerpt: str
    content_html: str
    categories: tuple[str, ...]
    pdf_urls: tuple[str, ...]


CORE_PATTERN = re.compile(
    r"(?:science|scientific|metascience|research(?: funding| grants?| productivity| policy| ecosystem| enterprise| organisations?)|"
    r"innovation(?: ecosystem| policy| agenda)?|r\s*&\s*d|national laborator|nist|nsf|nih|darpa|arpa|"
    r"artificial intelligence|\bai\b|compute|semiconductor|fusion|materials discovery|clinical trial|drug development)", re.I,
)
SUPPORT_PATTERN = re.compile(
    r"(?:high-skilled|immigration|visa|stem talent|workforce|biotechnology|pandemic|vaccine|diagnostic|pathogen|"
    r"agricultural|bio(?:manufacturing|technology)|entrepreneur|market commitment|prizes?)", re.I,
)
CONTEXT_PATTERN = re.compile(
    r"(?:security level|sleeper agents?|sabotage|biosecurity threats?|misuse of dna|dual-use research|"
    r"export control gaps?|secure the dna supply chain)", re.I,
)
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|prc|deepseek)\b", re.I)


def clean_text(value: str) -> str:
    soup = BeautifulSoup(html.unescape(value or ""), "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def is_relevant_post(categories: tuple[str, ...]) -> bool:
    return bool(TARGET_CATEGORIES.intersection(categories))


def classify_relevance(title: str, categories: str, summary: str) -> str:
    text = " | ".join((title, categories, summary))
    if CONTEXT_PATTERN.search(title) and not re.search(r"(?:science|research|innovation|r\s*&\s*d)", title, re.I):
        return "语境"
    if CORE_PATTERN.search(text):
        return "核心"
    if SUPPORT_PATTERN.search(text):
        return "支撑"
    return "语境"


def report_id(published: str, slug: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")[:82]
    return f"C-IFP-{published[:4]}-{token}"


def normalize_post(post: dict, category_names: dict[int, str]) -> IfpItem:
    content = str(post.get("content", {}).get("rendered", ""))
    categories = tuple(category_names[cid] for cid in post.get("categories", []) if cid in category_names)
    pdfs = sorted({
        html.unescape(match)
        for match in re.findall(r'https?[^"\'\s>]+\.pdf(?:\?[^"\'\s>]*)?', content, flags=re.I)
        if re.match(r"https://ifp\.org/wp-content/uploads/", html.unescape(match), flags=re.I)
    })
    return IfpItem(
        post_id=int(post["id"]), date=str(post["date"])[:10], slug=str(post["slug"]), url=str(post["link"]),
        title=clean_text(str(post.get("title", {}).get("rendered", ""))),
        excerpt=clean_text(str(post.get("excerpt", {}).get("rendered", ""))), content_html=content,
        categories=categories, pdf_urls=tuple(pdfs),
    )


def fetch_json(path: str, params: dict[str, object]) -> tuple[object, dict[str, str]]:
    url = f"{API_URL}/{path}?{urlencode(params)}"
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 CodexResearch/1.0"})
            with urlopen(request, timeout=60) as response:
                headers = {key.lower(): value for key, value in response.headers.items()}
                return json.loads(response.read().decode("utf-8")), headers
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def collect_items() -> tuple[list[IfpItem], dict[str, str]]:
    category_rows, _ = fetch_json("categories", {"per_page": 100})
    category_names = {int(row["id"]): str(row["name"]) for row in category_rows}
    items: list[IfpItem] = []
    page_hashes: dict[str, str] = {}
    page = 1
    while True:
        rows, headers = fetch_json(
            "posts",
            {"per_page": 100, "page": page, "_fields": "id,date,slug,link,title,excerpt,content,categories"},
        )
        payload = json.dumps(rows, ensure_ascii=False, sort_keys=True)
        page_hashes[str(page)] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        for row in rows:
            item = normalize_post(row, category_names)
            if is_relevant_post(item.categories) and date(2022, 1, 1) <= date.fromisoformat(item.date) <= date.today():
                items.append(item)
        if page >= int(headers.get("x-wp-totalpages", page)):
            break
        page += 1
    by_id = {item.post_id: item for item in items}
    return sorted(by_id.values(), key=lambda item: (item.date, item.title.lower(), item.post_id)), page_hashes


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
    args = parser.parse_args()
    root = args.research.resolve()
    items, page_hashes = collect_items()
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    previous = root / "166_IFP科技创新正式成果轻量总目录.csv"
    if previous.exists():
        previous_ids = {row["报告ID"] for row in read_csv(previous)}
        catalog = [row for row in catalog if not (row.get("机构ID") == "ifp" and row.get("报告ID") in previous_ids and not row.get("本地原始资产路径"))]
    by_id = {row["报告ID"]: row for row in catalog}
    ledger: list[dict[str, str]] = []
    added = linked = china_count = 0
    counts = {"核心": 0, "支撑": 0, "语境": 0}
    for item in items:
        rid = report_id(item.date, item.slug)
        categories = "；".join(item.categories)
        body_text = clean_text(item.content_html)
        relevance = classify_relevance(item.title, categories, item.excerpt)
        counts[relevance] += 1
        is_china = bool(CHINA_PATTERN.search(" ".join((item.title, item.excerpt, body_text))))
        china_count += int(is_china)
        if rid in by_id:
            linked += 1
        else:
            catalog.append({
                "报告ID": rid, "机构ID": "ifp", "机构英文名": "Institute for Progress", "国家或地区": "美国",
                "发布日期": item.date, "观察窗": "W3", "报告名称": item.title,
                "报告类型": f"IFP official publication/{categories}", "原文链接": item.url, "本地路径": "",
                "正文完整度": "官方WordPress元数据与网页正文入口；正文未批量落盘",
                "优先级": "P1-China-STI-candidate" if is_china and relevance != "语境" else "P2-light-catalog" if relevance != "语境" else "P3-context-catalog",
                "示踪问题": f"科技创新相关度={relevance}" + ("；中国科技横向维度" if is_china else ""),
                "机构观点等级": "IFP正式出版页面；署名作者观点，连续项目需另行归因", "样本角色": "新型科技政策智库进入与议题结构轻量目录",
                "编码状态": "目录待筛选", "预期用途": "科研资助、元科学、科技人才、前沿技术、产业能力与中国比较",
                "本地原始资产路径": "", "原始资产状态": "官方网页与附件入口已保存；未批量下载正文",
            })
            by_id[rid] = catalog[-1]
            added += 1
        ledger.append({
            "报告ID": rid, "统一目录报告ID": rid, "WordPress文章ID": str(item.post_id), "发布日期": item.date,
            "报告名称": item.title, "官方栏目": categories, "科技创新相关度": relevance,
            "中国关联": "是" if is_china else "否", "官方落地页": item.url, "官方PDF入口": "；".join(item.pdf_urls),
            "页面摘要": item.excerpt, "正文字符数": str(len(body_text)), "资料层级": "IFP官方WordPress出版页轻量元数据",
            "全文策略": "总目录保留；科学创新机制、中国科技比较或高复用节点进入全文层",
            "正文SHA256": hashlib.sha256(item.content_html.encode("utf-8")).hexdigest(), "采集日期": date.today().isoformat(),
        })
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(root / "166_IFP科技创新正式成果轻量总目录.csv", ledger, LEDGER_FIELDS)
    (root / "167_IFP科技创新正式成果轻量总目录结果.md").write_text(
        "# IFP科技创新正式成果轻量总目录结果\n\n"
        f"- 官网四个科技政策栏目共{len(items)}项正式出版页面；新增统一目录{added}项，关联既有目录{linked}项。\n"
        f"- 科技创新相关度：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；正文出现中国相关词形{china_count}项。\n"
        f"- IFP成立较晚，本目录覆盖2022—{date.today().year}年，只用于观察新型科技政策智库进入及近期议程，不能承担十年机构内变化判断。\n"
        "- 安全、出口管制和生物安全题名保留作议题边界；未直接解释科研、创新或技术能力建设者不进入精选全文。\n"
        f"- WordPress API页哈希：`{';'.join(f'{key}:{value}' for key, value in page_hashes.items())}`。\n",
        encoding="utf-8",
    )
    print(f"light={len(items)} added={added} linked={linked} china={china_count} core={counts['核心']} support={counts['支撑']} context={counts['语境']} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
