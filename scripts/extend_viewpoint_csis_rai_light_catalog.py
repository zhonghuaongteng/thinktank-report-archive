from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


CDP_PROXY = "http://localhost:3456"
PROGRAM_URL = "https://www.csis.org/programs/renewing-american-innovation"
PROGRAM_NODE = "100069"
EXPECTED_COUNTS = {"report": 43, "article": 133}
SERIES_ROLE = "CSIS RAI科技创新项目轻量总目录"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "发布日期", "报告名称", "官方内容类型", "官方子类型", "作者",
    "科技创新相关度", "中国直接信号", "官方落地页", "页面摘要", "资料层级", "全文策略", "采集日期",
]

CORE_PATTERN = re.compile(
    r"(?:science|scientific|research|r\s*&\s*d|research and development|innovation|patent|intellectual property|"
    r"technology transfer|commerciali[sz]|critical technolog|emerging technolog|artificial intelligence|\bai\b|"
    r"semiconductor|microelectronic|quantum|biotech|biopharma|pharmaceutical|fusion|advanced manufacturing|"
    r"industrial policy|research infrastructure|national science foundation|\bnsf\b|\bsbir\b)", re.I,
)
SUPPORT_PATTERN = re.compile(
    r"(?:\bstem\b|talent|workforce|skills|education|regional network|regional ecosystem|cluster|startup|"
    r"entrepreneur|data center|compute|manufacturing capacity|standards|supply chain)", re.I,
)
SECURITY_ONLY_PATTERN = re.compile(
    r"(?:military|weapon|deterrence|warfare|operational planning|missile|nuclear posture|armed forces)", re.I,
)
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|prc)\b", re.I)


@dataclass(frozen=True)
class CsisRaiItem:
    published: str
    title: str
    url: str
    summary: str
    content_type: str
    subtype: str
    authors: str


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_listing_html(source: str) -> tuple[int, list[CsisRaiItem]]:
    soup = BeautifulSoup(source, "html.parser")
    result_text = normalize_space((soup.select_one(".csis-search-results-text") or soup).get_text(" ", strip=True))
    total_match = re.search(r"\bof\s+([0-9,]+)\b", result_text)
    if not total_match:
        raise ValueError(f"missing CSIS result count: {result_text[:160]!r}")
    total = int(total_match.group(1).replace(",", ""))
    items: list[CsisRaiItem] = []
    for article in soup.select(".views-row article"):
        link = article.select_one("h3 a[href]")
        if not link:
            continue
        title = normalize_space(link.get_text(" ", strip=True))
        url = urljoin(PROGRAM_URL, str(link.get("href", "")))
        summary_node = article.select_one(".search-listing--summary")
        summary = normalize_space(summary_node.get_text(" ", strip=True) if summary_node else "")
        credit_node = article.select_one(".contributors")
        credit = normalize_space(credit_node.get_text(" ", strip=True) if credit_node else "")
        date_match = re.search(r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", credit)
        if not date_match:
            raise ValueError(f"missing CSIS publication date: {title!r} {credit!r}")
        published = datetime.strptime(date_match.group(1), "%B %d, %Y").date().isoformat()
        subtype = normalize_space(re.split(r"\s+by\s+|\s+—\s+", credit, maxsplit=1)[0])
        author_match = re.search(r"\bby\s+(.+?)\s+—\s+", credit)
        authors = normalize_space(author_match.group(1)) if author_match else ""
        classes = set(article.get("class", []))
        content_type = "Report" if "report-search-listing" in classes else "Article" if "article-search-listing" in classes else ""
        if not content_type:
            raise ValueError(f"unexpected CSIS listing class for {title!r}: {sorted(classes)}")
        items.append(CsisRaiItem(published, title, url, summary, content_type, subtype, authors))
    return total, items


def classify_relevance(title: str, summary: str) -> str:
    text = f"{title} | {summary}"
    if CORE_PATTERN.search(text):
        return "核心"
    if SUPPORT_PATTERN.search(text):
        return "支撑"
    if SECURITY_ONLY_PATTERN.search(text):
        return "语境"
    return "语境"


def china_signal(title: str, summary: str) -> bool:
    return bool(CHINA_PATTERN.search(f"{title} | {summary}"))


def report_id(published: str, url: str) -> str:
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    token = re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")[:105]
    return f"C-CSIS-RAI-{published[:4]}-{token}"


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def _proxy_json(path: str, body: str | None = None) -> object:
    request = Request(CDP_PROXY + path, data=body.encode("utf-8") if body is not None else None)
    if body is not None:
        request.add_header("Content-Type", "text/plain; charset=utf-8")
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def _eval(target: str, expression: str) -> object:
    payload = _proxy_json("/eval?target=" + target, expression)
    if not isinstance(payload, dict) or "value" not in payload:
        raise RuntimeError(f"unexpected CDP evaluation response: {payload!r}")
    return payload["value"]


def _ajax_html(target: str, view: dict[str, object], query: str) -> tuple[str, str]:
    body = urlencode({
        "view_name": str(view["view_name"]), "view_display_id": str(view["view_display_id"]),
        "view_args": str(view["view_args"]), "view_path": str(view["view_path"]),
        "view_dom_id": str(view["view_dom_id"]), "pager_element": str(view["pager_element"]),
    })
    expression = (
        "(async()=>{const r=await fetch(" + json.dumps("/views/ajax?" + query) + ","
        "{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',"
        "'X-Requested-With':'XMLHttpRequest'},body:" + json.dumps(body) + "});return await r.text()})()"
    )
    raw = str(_eval(target, expression))
    commands = json.loads(raw)
    html = next((str(command.get("data", "")) for command in commands if command.get("command") == "insert"), "")
    if not html:
        raise RuntimeError(f"CSIS Views AJAX returned no listing HTML for {query}")
    return html, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def collect_items() -> tuple[list[CsisRaiItem], list[str]]:
    opened = _proxy_json("/new?url=" + quote(PROGRAM_URL, safe=""))
    target = str(opened["targetId"])
    try:
        for _ in range(30):
            title = str(_eval(target, "document.title"))
            if "Renewing American Innovation" in title:
                break
            time.sleep(0.25)
        else:
            raise RuntimeError(f"CSIS program page unavailable: {title!r}")
        view = _eval(target, "Object.values(drupalSettings.views.ajaxViews)[0]")
        if not isinstance(view, dict) or str(view.get("view_args")) != PROGRAM_NODE:
            raise RuntimeError(f"unexpected CSIS program view settings: {view!r}")
        all_items: list[CsisRaiItem] = []
        hashes: list[str] = []
        for kind, expected in EXPECTED_COUNTS.items():
            pages = math.ceil(expected / 10)
            kind_items: list[CsisRaiItem] = []
            for page in range(pages):
                query = urlencode({"f[0]": f"content_type:{kind}", "page": page})
                html, digest = _ajax_html(target, view, query)
                total, page_items = parse_listing_html(html)
                if total != expected:
                    raise RuntimeError(f"CSIS RAI {kind} count changed: expected {expected}, found {total}")
                if any(item.content_type.lower() != kind for item in page_items):
                    raise RuntimeError(f"CSIS RAI {kind} filter returned another content type")
                kind_items.extend(page_items)
                hashes.append(digest)
            deduped = {item.url.rstrip("/"): item for item in kind_items}
            if len(deduped) != expected:
                raise RuntimeError(f"CSIS RAI {kind} pagination incomplete: expected {expected}, found {len(deduped)}")
            all_items.extend(deduped.values())
        return sorted(all_items, key=lambda item: (item.published, item.title.lower())), hashes
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def should_replace_previous_light_row(row: dict[str, str], previous_ids: set[str]) -> bool:
    return (
        row.get("机构ID") == "csis-rai" and row.get("报告ID") in previous_ids
        and row.get("样本角色") == SERIES_ROLE and not row.get("本地原始资产路径")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect the CSIS Renewing American Innovation official Report and Article catalog through the browser.")
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--collection-date", default=date.today().isoformat())
    args = parser.parse_args()
    root = args.research.resolve()
    items, hashes = collect_items()
    items = [item for item in items if "2016-01-01" <= item.published <= args.collection_date]
    output_path = root / "178_CSIS_RAI科技创新项目轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    if output_path.exists():
        previous_ids = {row["报告ID"] for row in read_csv(output_path)}
        catalog = [row for row in catalog if not should_replace_previous_light_row(row, previous_ids)]
    by_id = {row["报告ID"]: row for row in catalog}
    by_url = {row["原文链接"].rstrip("/"): row for row in catalog if row.get("原文链接")}
    ledger: list[dict[str, str]] = []
    counts = {"核心": 0, "支撑": 0, "语境": 0}
    years: dict[str, int] = {}
    subtypes: dict[str, int] = {}
    added = linked = china_count = 0
    for item in items:
        relevance = classify_relevance(item.title, item.summary)
        china = china_signal(item.title, item.summary)
        counts[relevance] += 1
        china_count += int(china)
        years[item.published[:4]] = years.get(item.published[:4], 0) + 1
        subtypes[item.subtype] = subtypes.get(item.subtype, 0) + 1
        existing = by_url.get(item.url.rstrip("/"))
        rid = existing["报告ID"] if existing else report_id(item.published, item.url)
        if existing or rid in by_id:
            linked += 1
        else:
            row = {
                "报告ID": rid, "机构ID": "csis-rai", "机构英文名": "CSIS Renewing American Innovation",
                "国家或地区": "美国", "发布日期": item.published, "观察窗": observation_window(item.published),
                "报告名称": item.title, "报告类型": f"CSIS RAI official {item.content_type} / {item.subtype}",
                "原文链接": item.url, "本地路径": "", "正文完整度": "官方项目归档元数据、摘要与全文入口；正文未批量落盘",
                "优先级": "P1-China-STI-candidate" if china and relevance != "语境" else "P2-light-catalog" if relevance != "语境" else "P3-context-catalog",
                "示踪问题": f"科技创新相关度={relevance}" + ("；中国科技横向维度" if china else ""),
                "机构观点等级": "CSIS RAI项目正式研究或分析；保留作者与项目归因",
                "样本角色": SERIES_ROLE, "编码状态": "目录待筛选",
                "预期用途": "科学与R&D体系、创新生态、成果转化、科技人才、关键技术、产业能力与中国比较",
                "本地原始资产路径": "", "原始资产状态": "官方项目归档入口已登记；未批量下载正文",
            }
            catalog.append(row)
            by_id[rid] = row
            by_url[item.url.rstrip("/")] = row
            added += 1
        ledger.append({
            "报告ID": rid, "统一目录报告ID": rid, "发布日期": item.published, "报告名称": item.title,
            "官方内容类型": item.content_type, "官方子类型": item.subtype, "作者": item.authors,
            "科技创新相关度": relevance, "中国直接信号": "是" if china else "否", "官方落地页": item.url,
            "页面摘要": item.summary, "资料层级": "CSIS RAI官方项目归档Report/Article元数据",
            "全文策略": "总目录保留；科学、R&D、创新生态、成果转化、关键技术及中国科技比较节点进入全文层",
            "采集日期": args.collection_date,
        })
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(output_path, ledger, LEDGER_FIELDS)
    year_text = "、".join(f"{year}年{years[year]}项" for year in sorted(years))
    subtype_text = "、".join(f"{key}{value}项" for key, value in sorted(subtypes.items()))
    (root / "179_CSIS_RAI科技创新项目轻量总目录结果.md").write_text(
        "# CSIS RAI科技创新项目轻量总目录结果\n\n"
        f"- 官方项目归档共176项Report/Article，本次观察窗内保留{len(items)}项；新增统一目录{added}项，关联既有目录{linked}项。\n"
        f"- 官方内容类型为Report 43项、Article 133项；子类型分布：{subtype_text}。\n"
        f"- 年度分布：{year_text}；该项目资料自实际出现年份起记录，不向前推定项目立场。\n"
        f"- 科技创新相关度：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；题名或摘要直接出现中国信号{china_count}项。\n"
        "- Event、Podcast Episode、人员页和一般项目页面不进入目录；全机构安全研究不扩展为本批采集范围。\n"
        "- 全文层只选择能解释科学与R&D体系、创新生态、成果转化、人才、关键技术路线及中国科技比较的跨期节点。\n"
        f"- 官方Views AJAX响应哈希共{len(hashes)}个：`{';'.join(hashes)}`。\n",
        encoding="utf-8",
    )
    print(f"light={len(items)} added={added} linked={linked} china={china_count} core={counts['核心']} support={counts['支撑']} context={counts['语境']} catalog={len(catalog)} responses={len(hashes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
