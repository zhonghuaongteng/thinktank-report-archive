from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import time
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


CDP_PROXY = "http://localhost:3456"
API_ROOT = "https://fas.org/wp-json/wp/v2/publications"
PUBLICATION_TYPES = {12: "Report", 770: "Policy Memo"}
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "WordPress记录ID", "发布日期", "报告名称", "官方类型",
    "科技创新相关度", "中国直接信号", "官方落地页", "页面摘要", "资料层级", "全文策略", "采集日期",
]

CORE_PATTERN = re.compile(
    r"(?:science|scientific|research|r\s*&\s*d|research and development|innovation|metascience|"
    r"technology transfer|commerciali[sz]|bioeconomy|biotech|artificial intelligence|\bai\b|"
    r"semiconductor|microelectronic|quantum|robot|advanced manufacturing|clean energy|battery|"
    r"critical technolog|emerging technolog|arpa-|patent|technology policy)", re.I,
)
SUPPORT_PATTERN = re.compile(
    r"(?:\bstem\b|talent|workforce|skills|research capacity|innovation capacity|technology diffusion|"
    r"infrastructure|laborator|education|procurement|regional innovation|entrepreneur|startup|"
    r"digital government|data center)", re.I,
)
SECURITY_PATTERN = re.compile(
    r"(?:nuclear|missile|deterrence|weapon|warhead|arms control|command and control|military|"
    r"national security|defen[cs]e|nonproliferation|pre-launch)", re.I,
)
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|prc)\b", re.I)


@dataclass(frozen=True)
class FasItem:
    post_id: int
    date: str
    slug: str
    url: str
    title: str
    summary: str
    publication_types: tuple[str, ...]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", BeautifulSoup(html.unescape(value or ""), "html.parser").get_text(" ", strip=True)).strip()


def normalize_post(post: dict[str, object]) -> FasItem:
    type_ids = post.get("_fas_types") or post.get("publication-type") or post.get("publication_type") or []
    names = tuple(PUBLICATION_TYPES[type_id] for type_id in PUBLICATION_TYPES if type_id in {int(x) for x in type_ids})
    title = post.get("title") or {}
    excerpt = post.get("excerpt") or {}
    return FasItem(
        post_id=int(post["id"]),
        date=str(post["date"])[:10],
        slug=str(post["slug"]),
        url=str(post["link"]),
        title=clean_text(str(title.get("rendered", ""))) if isinstance(title, dict) else clean_text(str(title)),
        summary=clean_text(str(excerpt.get("rendered", ""))) if isinstance(excerpt, dict) else clean_text(str(excerpt)),
        publication_types=names,
    )


def classify_relevance(title: str, summary: str) -> str:
    text = f"{title} | {summary}"
    if SECURITY_PATTERN.search(text):
        return "语境"
    if SUPPORT_PATTERN.search(text):
        return "支撑"
    if CORE_PATTERN.search(text):
        return "核心"
    return "语境"


def china_signal(title: str, summary: str) -> bool:
    return bool(CHINA_PATTERN.search(f"{title} | {summary}"))


def report_id(published: str, slug: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")[:105]
    return f"C-FAS-{published[:4]}-{token}"


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def api_url(year: int, publication_type: int, page: int = 1, collection_date: str = "2026-08-23") -> str:
    end = min(date(year + 1, 1, 1), date.fromisoformat(collection_date) + timedelta(days=1))
    params = {
        "after": f"{year}-01-01T00:00:00",
        "before": f"{end.isoformat()}T00:00:00",
        "publication-type": publication_type,
        "per_page": 100,
        "page": page,
        "orderby": "date",
        "order": "asc",
        "_fields": "id,date,slug,link,title,excerpt,publication-type",
    }
    return API_ROOT + "?" + urlencode(params)


def _proxy_json(path: str, body: str | None = None) -> object:
    request = Request(CDP_PROXY + path, data=body.encode("utf-8") if body is not None else None)
    if body is not None:
        request.add_header("Content-Type", "text/plain; charset=utf-8")
    with urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def _browser_json(url: str) -> tuple[object, str]:
    opened = _proxy_json("/new?url=" + quote(url, safe=""))
    target = str(opened["targetId"])
    try:
        for _ in range(60):
            value = _proxy_json("/eval?target=" + target, "document.body?.innerText||''")["value"]
            text = str(value).strip()
            if text.startswith("[") or text.startswith("{"):
                return json.loads(text), hashlib.sha256(text.encode("utf-8")).hexdigest()
            time.sleep(0.2)
        raise TimeoutError(f"FAS API response did not load: {url}")
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass


def collect_items(collection_date: str) -> tuple[list[FasItem], list[str]]:
    posts: dict[int, dict[str, object]] = {}
    hashes: list[str] = []
    for year in range(2016, int(collection_date[:4]) + 1):
        for type_id in PUBLICATION_TYPES:
            page = 1
            while True:
                payload, digest = _browser_json(api_url(year, type_id, page, collection_date))
                hashes.append(digest)
                if not isinstance(payload, list):
                    raise ValueError(f"unexpected FAS API payload for {year}/{type_id}")
                for raw in payload:
                    post = dict(raw)
                    post_id = int(post["id"])
                    merged = posts.setdefault(post_id, post)
                    types = {int(x) for x in merged.get("_fas_types", [])}
                    types.add(type_id)
                    types.update(int(x) for x in post.get("publication-type", []))
                    merged["_fas_types"] = sorted(types)
                if len(payload) < 100:
                    break
                page += 1
    return sorted((normalize_post(post) for post in posts.values()), key=lambda item: (item.date, item.title.lower())), hashes


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
        row.get("机构ID") == "fas"
        and row.get("报告ID") in previous_ids
        and row.get("样本角色") == "FAS报告与政策备忘录近十年轻量总目录"
        and not row.get("本地原始资产路径")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect the official FAS Report and Policy Memo lightweight catalog through the browser CDP proxy.")
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--collection-date", default=date.today().isoformat())
    args = parser.parse_args()
    root = args.research.resolve()
    items, page_hashes = collect_items(args.collection_date)
    catalog_path = root / "05_报告总目录.csv"
    output_path = root / "174_FAS报告与政策备忘录近十年轻量总目录.csv"
    catalog = read_csv(catalog_path)
    if output_path.exists():
        previous_ids = {row["报告ID"] for row in read_csv(output_path)}
        catalog = [row for row in catalog if not should_replace_previous_light_row(row, previous_ids)]
    by_id = {row["报告ID"]: row for row in catalog}
    by_url = {row["原文链接"].rstrip("/"): row for row in catalog if row.get("原文链接")}
    ledger: list[dict[str, str]] = []
    counts = {"核心": 0, "支撑": 0, "语境": 0}
    years: dict[str, int] = {}
    types = {"Report": 0, "Policy Memo": 0, "Report + Policy Memo": 0}
    added = linked = china_count = 0
    for item in items:
        relevance = classify_relevance(item.title, item.summary)
        china = china_signal(item.title, item.summary)
        type_label = " + ".join(item.publication_types)
        counts[relevance] += 1
        years[item.date[:4]] = years.get(item.date[:4], 0) + 1
        types[type_label] = types.get(type_label, 0) + 1
        china_count += int(china)
        existing = by_url.get(item.url.rstrip("/"))
        rid = existing["报告ID"] if existing else report_id(item.date, item.slug)
        if existing or rid in by_id:
            linked += 1
        else:
            row = {
                "报告ID": rid, "机构ID": "fas", "机构英文名": "Federation of American Scientists",
                "国家或地区": "美国", "发布日期": item.date, "观察窗": observation_window(item.date), "报告名称": item.title,
                "报告类型": f"FAS official {type_label}", "原文链接": item.url, "本地路径": "",
                "正文完整度": "官方WordPress元数据、摘要与全文入口；正文未批量落盘",
                "优先级": "P1-China-STI-candidate" if china and relevance != "语境" else "P2-light-catalog" if relevance != "语境" else "P3-context-catalog",
                "示踪问题": f"科技创新相关度={relevance}" + ("；中国科技横向维度" if china else ""),
                "机构观点等级": "FAS正式报告或政策备忘录；署名作者观点，机构立场需另行归因",
                "样本角色": "FAS报告与政策备忘录近十年轻量总目录", "编码状态": "目录待筛选",
                "预期用途": "科学体系、R&D投入、创新机构、科技人才、成果转化、关键技术与中国比较",
                "本地原始资产路径": "", "原始资产状态": "官方落地页与WordPress正文入口已登记；未批量下载正文",
            }
            catalog.append(row)
            by_id[rid] = row
            by_url[item.url.rstrip("/")] = row
            added += 1
        ledger.append({
            "报告ID": rid, "统一目录报告ID": rid, "WordPress记录ID": str(item.post_id), "发布日期": item.date,
            "报告名称": item.title, "官方类型": type_label, "科技创新相关度": relevance,
            "中国直接信号": "是" if china else "否", "官方落地页": item.url, "页面摘要": item.summary,
            "资料层级": "FAS官方WordPress Reports/Policy Memos元数据",
            "全文策略": "总目录保留；科研机制、创新制度、关键技术、中国科技比较或跨期节点进入全文层",
            "采集日期": args.collection_date,
        })
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(output_path, ledger, LEDGER_FIELDS)
    year_text = "、".join(f"{year}年{years[year]}项" for year in sorted(years))
    type_text = "、".join(f"{key}{value}项" for key, value in types.items() if value)
    (root / "175_FAS报告与政策备忘录近十年轻量总目录结果.md").write_text(
        "# FAS报告与政策备忘录近十年轻量总目录结果\n\n"
        f"- 官网WordPress正式出版接口去重后共{len(items)}项；新增统一目录{added}项，关联既有目录{linked}项。\n"
        f"- 类型分布：{type_text}。\n"
        f"- 年度分布：{year_text}；2018年官方接口无Report或Policy Memo记录，保留真实空档。\n"
        f"- 科技创新相关度：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项；题名或摘要直接出现中国信号{china_count}项。\n"
        "- 全目录仅保存题名、日期、摘要、类型和官方入口；全文严格限于科研投入与组织、人才、成果转化、关键技术及中国科技比较。\n"
        "- 核武、导弹、军控和一般国家安全材料只保留目录语境，不进入科技创新证据主干。\n"
        f"- 官方接口响应哈希共{len(page_hashes)}个：`{';'.join(page_hashes)}`。\n",
        encoding="utf-8",
    )
    print(f"light={len(items)} added={added} linked={linked} china={china_count} core={counts['核心']} support={counts['支撑']} context={counts['语境']} catalog={len(catalog)} responses={len(page_hashes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
