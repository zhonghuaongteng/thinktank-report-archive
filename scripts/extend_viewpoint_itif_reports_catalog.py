from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Callable
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


LISTING_URL = "https://itif.org/publications/reports-briefings/"
CDP_PROXY = "http://localhost:3456"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "发布日期", "报告名称", "官方类型", "科技创新相关度", "中国直接信号",
    "官方落地页", "页面摘要", "资料层级", "全文策略", "采集日期",
]

CORE_PATTERN = re.compile(
    r"(?:science|scientific|research|r\s*&\s*d|research and development|innovation|technology transfer|"
    r"commerciali[sz]|artificial intelligence|\bai\b|semiconductor|quantum|robot|biotech|biopharma|"
    r"advanced manufacturing|clean energy|nuclear|battery|critical technolog|emerging technolog|patent)",
    re.I,
)
SUPPORT_PATTERN = re.compile(
    r"(?:high-tech|high skilled|high-skilled|stem|talent|skills|productivity|technology diffusion|"
    r"digital government|broadband|spectrum|data center|startup|entrepreneur|regional technolog)",
    re.I,
)
CONTEXT_PATTERN = re.compile(
    r"(?:national security|defen[cs]e|cybersecurity|cyberspace|antitrust|privacy|surveillance|"
    r"trade war|tariffs?|export controls?|geopolitic|weapon)",
    re.I,
)
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|prc)\b", re.I)


@dataclass(frozen=True)
class ItifListingItem:
    date: str
    publication_type: str
    title: str
    summary: str
    url: str
    slug: str


def normalize_listing_item(meta: str, title: str, summary: str, url: str) -> ItifListingItem:
    cleaned = re.sub(r"\s+", " ", meta).strip()
    match = re.match(r"(.+?\d{4})\s*\|\s*(.+)$", cleaned)
    date_text = match.group(1) if match else cleaned
    publication_type = match.group(2).strip() if match else "Reports & Briefings"
    published = datetime.strptime(date_text, "%B %d, %Y").date().isoformat()
    canonical = url if url.startswith("http") else "https://itif.org" + "/" + url.lstrip("/")
    slug = urlparse(canonical).path.rstrip("/").split("/")[-1]
    return ItifListingItem(
        date=published,
        publication_type=publication_type,
        title=re.sub(r"\s+", " ", title).strip(),
        summary=re.sub(r"\s+", " ", summary).strip(),
        url=canonical,
        slug=slug,
    )


def extract_listing_cards(source_html: str) -> list[ItifListingItem]:
    soup = BeautifulSoup(source_html, "html.parser")
    items: list[ItifListingItem] = []
    for card in soup.select("div.block.relative.mb-8"):
        anchor = card.select_one('a[href*="/publications/20"]')
        meta = card.select_one("p.block.mb-2")
        if not anchor or not meta:
            continue
        meta_text = meta.get_text("|", strip=True).replace("|||", "|").replace("||", "|")
        if "|" in meta_text and "Reports & Briefings" not in meta_text:
            continue
        heading = anchor.select_one("h2")
        paragraphs = card.select("div p")
        summary = paragraphs[-1].get_text(" ", strip=True) if paragraphs else ""
        items.append(normalize_listing_item(meta_text, heading.get_text(" ", strip=True) if heading else anchor.get_text(" ", strip=True), summary, anchor.get("href", "")))
    return items


def page_signature(source_html: str) -> str:
    items = extract_listing_cards(source_html)
    if not items:
        return ""
    return f"{len(items)}|{items[0].url}|{items[-1].url}"


def in_research_window(published: str, collection_date: str) -> bool:
    return date(2016, 1, 1) <= date.fromisoformat(published) <= date.fromisoformat(collection_date)


def classify_relevance(title: str, summary: str) -> str:
    text = f"{title} | {summary}"
    if CONTEXT_PATTERN.search(text) and not CORE_PATTERN.search(text):
        return "语境"
    if CORE_PATTERN.search(text):
        return "核心"
    if SUPPORT_PATTERN.search(text):
        return "支撑"
    return "语境"


def direct_china_signal(title: str, summary: str) -> bool:
    return bool(CHINA_PATTERN.search(f"{title} | {summary}"))


def report_id(published: str, slug: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")[:100]
    return f"C-ITIF-RB-{published[:4]}-{token}"


def wait_until(check: Callable[[], object], attempts: int = 40, interval: float = 0.25) -> bool:
    for _ in range(attempts):
        if check():
            return True
        time.sleep(interval)
    raise TimeoutError("dynamic ITIF page did not reach the required state")


def listing_state_script() -> str:
    return '({page:document.querySelector(`a[aria-current="page"]`)?.textContent||"1",html:document.documentElement.outerHTML,nextDisabled:document.querySelector(`a[aria-label="Next page"]`)?.getAttribute("aria-disabled")})'


def next_page_script() -> str:
    return '(()=>{const a=document.querySelector(`a[aria-label="Next page"]`);if(!a)return false;a.click();return true})()'


def _proxy_json(path: str, body: str | None = None) -> object:
    request = Request(CDP_PROXY + path, data=body.encode("utf-8") if body is not None else None)
    if body is not None:
        request.add_header("Content-Type", "text/plain; charset=utf-8")
    with urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def collect_items(collection_date: str) -> tuple[list[ItifListingItem], list[str]]:
    opened = _proxy_json("/new?url=" + quote(LISTING_URL, safe=""))
    target = str(opened["targetId"])
    page_hashes: list[str] = []
    collected: dict[str, ItifListingItem] = {}
    try:
        wait_until(
            lambda: bool(_proxy_json(
                "/eval?target=" + target,
                'Boolean(document.getElementById("items-per-page"))',
            )["value"])
        )
        _proxy_json(
            "/eval?target=" + target,
            '(()=>{const s=document.getElementById("items-per-page");s.value="50";s.dispatchEvent(new Event("change",{bubbles:true}));return true})()',
        )
        wait_until(
            lambda: int(_proxy_json(
                "/eval?target=" + target,
                'document.querySelectorAll("div.block.relative.mb-8").length',
            )["value"]) >= 25
        )
        while True:
            current_data = _proxy_json(
                "/eval?target=" + target,
                listing_state_script(),
            )["value"]
            html_text = str(current_data["html"])
            page_hashes.append(hashlib.sha256(html_text.encode("utf-8")).hexdigest())
            for item in extract_listing_cards(html_text):
                if in_research_window(item.date, collection_date):
                    collected[item.url.rstrip("/")] = item
            if str(current_data.get("nextDisabled", "false")).lower() == "true":
                break
            old_signature = page_signature(html_text)
            _proxy_json(
                "/eval?target=" + target,
                next_page_script(),
            )
            def cards_advanced() -> bool:
                html_now = _proxy_json(
                    "/eval?target=" + target,
                    'document.documentElement.outerHTML',
                )["value"]
                return page_signature(str(html_now)) not in {"", old_signature}

            wait_until(cards_advanced)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass
    return sorted(collected.values(), key=lambda item: (item.date, item.title.lower())), page_hashes


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def observation_window(published: str) -> str:
    year = int(published[:4])
    if year <= 2018:
        return "W1"
    if year <= 2021:
        return "W2"
    return "W3"


def should_replace_previous_light_row(row: dict[str, str], previous_ids: set[str]) -> bool:
    return (
        row.get("机构ID") == "itif"
        and row.get("报告ID") in previous_ids
        and row.get("样本角色") == "ITIF近十年正式研究轻量总目录"
        and not row.get("本地原始资产路径")
    )


def restore_missing_itif_seeds(
    catalog: list[dict[str, str]],
    seeds: list[dict[str, str]],
    convert: Callable[[dict[str, str]], dict[str, str]],
) -> list[dict[str, str]]:
    restored = list(catalog)
    existing_ids = {row.get("报告ID", "") for row in restored}
    for seed in seeds:
        seed_id = seed.get("种子ID", "")
        if seed.get("机构ID") != "itif" or seed_id in existing_ids:
            continue
        url = seed.get("官方页面或PDF", "").rstrip("/")
        restored = [
            row for row in restored
            if not (
                row.get("机构ID") == "itif"
                and row.get("原文链接", "").rstrip("/") == url
                and row.get("样本角色") == "ITIF近十年正式研究轻量总目录"
            )
        ]
        restored.append(convert(seed))
        existing_ids.add(seed_id)
    return restored


def seed_catalog_row(seed: dict[str, str], root: Path) -> dict[str, str]:
    pdf_path = root / "03_证据底稿" / "原文PDF" / f"{seed['种子ID']}.pdf"
    return {
        "报告ID": seed["种子ID"], "机构ID": seed["机构ID"], "机构英文名": seed["机构英文名"],
        "国家或地区": seed["国家或地区"], "发布日期": seed["日期"], "观察窗": seed["观察窗"],
        "报告名称": seed["报告名称"], "报告类型": seed["报告类型"], "原文链接": seed["官方页面或PDF"],
        "本地路径": str(pdf_path) if pdf_path.exists() else "", "正文完整度": seed["获取状态"],
        "优先级": "P0-anchor", "示踪问题": seed["示踪问题"], "机构观点等级": seed["机构观点等级"],
        "样本角色": "官方锚点", "编码状态": "待编码", "预期用途": seed["预期用途"],
        "本地原始资产路径": "", "原始资产状态": "",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--collection-date", default=date.today().isoformat())
    args = parser.parse_args()
    root = args.research.resolve()
    items, page_hashes = collect_items(args.collection_date)
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    catalog = restore_missing_itif_seeds(
        catalog,
        read_csv(root / "05_官方锚点种子.csv"),
        lambda seed: seed_catalog_row(seed, root),
    )
    previous = root / "170_ITIF正式报告与简报近十年轻量总目录.csv"
    if previous.exists():
        previous_ids = {row["报告ID"] for row in read_csv(previous)}
        catalog = [row for row in catalog if not should_replace_previous_light_row(row, previous_ids)]
    by_id = {row["报告ID"]: row for row in catalog}
    by_url = {row["原文链接"].rstrip("/"): row for row in catalog if row.get("原文链接")}
    ledger: list[dict[str, str]] = []
    counts = {"核心": 0, "支撑": 0, "语境": 0}
    added = linked = china_count = 0
    for item in items:
        relevance = classify_relevance(item.title, item.summary)
        china = direct_china_signal(item.title, item.summary)
        counts[relevance] += 1
        china_count += int(china)
        existing = by_url.get(item.url.rstrip("/"))
        rid = existing["报告ID"] if existing else report_id(item.date, item.slug)
        if existing or rid in by_id:
            linked += 1
        else:
            row = {
                "报告ID": rid, "机构ID": "itif", "机构英文名": "Information Technology and Innovation Foundation",
                "国家或地区": "美国", "发布日期": item.date, "观察窗": observation_window(item.date), "报告名称": item.title,
                "报告类型": "ITIF Reports & Briefings正式研究", "原文链接": item.url, "本地路径": "",
                "正文完整度": "官方目录元数据、摘要与Markdown全文入口；正文未批量落盘",
                "优先级": "P1-China-STI-candidate" if china and relevance != "语境" else "P2-light-catalog" if relevance != "语境" else "P3-context-catalog",
                "示踪问题": f"科技创新相关度={relevance}" + ("；中国科技横向维度" if china else ""),
                "机构观点等级": "ITIF正式报告或简报；署名作者观点，系列与机构立场需另行归因",
                "样本角色": "ITIF近十年正式研究轻量总目录", "编码状态": "目录待筛选",
                "预期用途": "科学体系、R&D投入、关键技术、创新政策、人才、成果转化与中国比较",
                "本地原始资产路径": "", "原始资产状态": "官方落地页与Markdown入口已登记；未批量下载正文",
            }
            catalog.append(row)
            by_id[rid] = row
            by_url[item.url.rstrip("/")] = row
            added += 1
        ledger.append({
            "报告ID": rid, "统一目录报告ID": rid, "发布日期": item.date, "报告名称": item.title,
            "官方类型": item.publication_type, "科技创新相关度": relevance, "中国直接信号": "是" if china else "否",
            "官方落地页": item.url, "页面摘要": item.summary, "资料层级": "ITIF官方Reports & Briefings目录元数据",
            "全文策略": "总目录保留；科技创新机制、中国比较或跨期节点进入全文层", "采集日期": args.collection_date,
        })
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(previous, ledger, LEDGER_FIELDS)
    (root / "171_ITIF正式报告与简报近十年轻量总目录结果.md").write_text(
        "# ITIF正式报告与简报近十年轻量总目录结果\n\n"
        f"- 官网Reports & Briefings近十年共{len(items)}项；新增统一目录{added}项，关联既有目录{linked}项。\n"
        f"- 科技创新相关度：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；题名或摘要直接出现中国信号{china_count}项。\n"
        "- 轻量目录保留正式研究的题名、日期、摘要和落地页；全文只按科研机制、关键技术、创新转化、中国比较及跨期节点筛选。\n"
        "- 网络安全、国家安全、反垄断和隐私材料保留为语境层；未直接改变R&D、科研组织、技术路线或产业创新者不进入精选全文。\n"
        f"- 官网分页哈希共{len(page_hashes)}页：`{';'.join(page_hashes)}`。\n",
        encoding="utf-8",
    )
    print(f"light={len(items)} added={added} linked={linked} china={china_count} core={counts['核心']} support={counts['支撑']} context={counts['语境']} catalog={len(catalog)} pages={len(page_hashes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
