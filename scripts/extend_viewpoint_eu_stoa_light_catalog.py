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
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


CDP_PROXY = "http://localhost:3456"
LISTING_URL = "https://www.europarl.europa.eu/stoa/en/publications/search"
EXPECTED_TOTAL = 381
SERIES_ROLE = "欧洲议会STOA近十年科技评估轻量总目录"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
LEDGER_FIELDS = [
    "报告ID", "统一目录报告ID", "发布日期", "报告名称", "官方文类", "官方文号",
    "科技创新相关度", "中国直接信号", "官方落地页", "页面摘要", "资料层级", "全文策略", "采集日期",
]

CORE_PATTERN = re.compile(
    r"(?:science|scientific|research|innovation|technolog|artificial intelligence|\bai\b|quantum|"
    r"biotech|biomed|genom|health data|robot|automat|semiconductor|microelectronic|comput|digital twin|"
    r"data cent|space|satellite|energy system|hydrogen|battery|renewable|decarboni[sz]|climate technolog|"
    r"advanced material|nanotech|manufactur|agricultural technolog|food technolog|research infrastructure|"
    r"horizon europe|academic freedom|laborator|university|scientist|r\s*&\s*d)",
    re.I,
)
SUPPORT_PATTERN = re.compile(
    r"(?:skills|education|workforce|industrial|industry|transport|mobility|environment|climate|energy|health|"
    r"foresight|scenario|future of|intellectual property|standardi[sz]|regional development|productivity)",
    re.I,
)
CHINA_PATTERN = re.compile(r"\b(?:china|chinese|prc)\b", re.I)


@dataclass(frozen=True)
class StoaItem:
    published: str
    title: str
    url: str
    summary: str
    publication_type: str
    document_code: str


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_listing_html(source: str) -> tuple[int, list[StoaItem]]:
    soup = BeautifulSoup(source, "html.parser")
    label = normalize_space((soup.select_one("#indexDisplayedResultsLabel") or soup).get_text(" ", strip=True))
    total_match = re.search(r"\bof\s+([0-9,]+)\s+results\b", label)
    if not total_match:
        raise ValueError(f"missing STOA result count: {label[:160]!r}")
    total = int(total_match.group(1).replace(",", ""))
    items: list[StoaItem] = []
    for node in soup.select(".es_document"):
        link = node.select_one(".es_document-title a[href]")
        date_node = node.select_one(".es_document-subtitle-date")
        type_node = node.select_one(".es_document-subtitle-documenttype")
        if not link or not date_node or not type_node:
            continue
        title = normalize_space(link.get_text(" ", strip=True))
        url = urljoin(LISTING_URL, str(link.get("href", "")))
        code = url.rstrip("/").split("/")[-1]
        published = datetime.strptime(normalize_space(date_node.get_text(" ", strip=True)), "%d-%m-%Y").date().isoformat()
        summary_node = node.select_one(".es_document-body")
        summary = normalize_space(summary_node.get_text(" ", strip=True) if summary_node else "")
        publication_type = normalize_space(type_node.get_text(" ", strip=True))
        items.append(StoaItem(published, title, url, summary, publication_type, code))
    return total, items


def classify_relevance(title: str, summary: str) -> str:
    text = f"{title} | {summary}"
    if CORE_PATTERN.search(text):
        return "核心"
    if SUPPORT_PATTERN.search(text):
        return "支撑"
    return "语境"


def china_signal(title: str, summary: str) -> bool:
    return bool(CHINA_PATTERN.search(f"{title} | {summary}"))


def report_id(document_code: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", document_code.upper()).strip("-")
    return f"C-EU-STOA-{token}"


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def _proxy_json(path: str, body: str | None = None) -> object:
    request = Request(CDP_PROXY + path, data=body.encode("utf-8") if body is not None else None)
    if body is not None:
        request.add_header("Content-Type", "text/plain; charset=utf-8")
    with urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def _eval(target: str, expression: str) -> object:
    payload = _proxy_json("/eval?target=" + target, expression)
    if not isinstance(payload, dict) or "value" not in payload:
        raise RuntimeError(f"unexpected CDP evaluation response: {payload!r}")
    return payload["value"]


def collect_items() -> tuple[list[StoaItem], list[str]]:
    opened = _proxy_json("/new?url=" + quote(LISTING_URL, safe=""))
    target = str(opened["targetId"])
    try:
        for _ in range(40):
            title = str(_eval(target, "document.title"))
            if "Panel for the Future of Science and Technology" in title:
                break
            time.sleep(0.25)
        else:
            raise RuntimeError(f"STOA listing unavailable: {title!r}")
        expression = """
(async()=>{
  const output=[];
  for(let page=0;page<39;page++){
    const response=await fetch('/stoa/en/publications/search?page='+page,{credentials:'same-origin'});
    if(!response.ok) throw new Error('STOA page '+page+' HTTP '+response.status);
    const html=await response.text();
    const doc=new DOMParser().parseFromString(html,'text/html');
    const label=(doc.querySelector('#indexDisplayedResultsLabel')?.innerText||'').trim();
    const items=[...doc.querySelectorAll('.es_document')].map(node=>({
      title:(node.querySelector('.es_document-title')?.innerText||'').replace(/\\s+/g,' ').trim(),
      url:new URL(node.querySelector('.es_document-title a')?.getAttribute('href')||'',location.origin).href,
      date:(node.querySelector('.es_document-subtitle-date')?.innerText||'').trim(),
      type:(node.querySelector('.es_document-subtitle-documenttype')?.innerText||'').trim(),
      summary:(node.querySelector('.es_document-body')?.innerText||'').replace(/\\s+/g,' ').trim()
    }));
    output.push({page,label,html,items});
  }
  return JSON.stringify(output);
})()
"""
        pages = json.loads(str(_eval(target, expression)))
        items: list[StoaItem] = []
        hashes: list[str] = []
        for page in pages:
            total, parsed = parse_listing_html(str(page["html"]))
            if total != EXPECTED_TOTAL:
                raise RuntimeError(f"STOA result count changed: expected {EXPECTED_TOTAL}, found {total}")
            items.extend(parsed)
            hashes.append(hashlib.sha256(str(page["html"]).encode("utf-8")).hexdigest())
        deduped = {item.document_code: item for item in items}
        if len(deduped) != EXPECTED_TOTAL:
            raise RuntimeError(f"STOA pagination incomplete: expected {EXPECTED_TOTAL}, found {len(deduped)}")
        return sorted(deduped.values(), key=lambda item: (item.published, item.title.lower())), hashes
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
        row.get("机构ID") == "eu-stoa"
        and row.get("报告ID") in previous_ids
        and row.get("样本角色") == SERIES_ROLE
        and not row.get("本地原始资产路径")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect the official European Parliament STOA publication catalog through the browser.")
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--collection-date", default=date.today().isoformat())
    args = parser.parse_args()
    root = args.research.resolve()
    items, hashes = collect_items()
    items = [item for item in items if "2016-01-01" <= item.published <= args.collection_date]
    output_path = root / "182_欧洲议会STOA科技评估近十年轻量总目录.csv"
    result_path = root / "183_欧洲议会STOA科技评估近十年轻量总目录结果.md"
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
    types: dict[str, int] = {}
    added = linked = china_count = 0
    for item in items:
        relevance = classify_relevance(item.title, item.summary)
        china = china_signal(item.title, item.summary)
        counts[relevance] += 1
        china_count += int(china)
        years[item.published[:4]] = years.get(item.published[:4], 0) + 1
        types[item.publication_type] = types.get(item.publication_type, 0) + 1
        existing = by_url.get(item.url.rstrip("/"))
        rid = existing["报告ID"] if existing else report_id(item.document_code)
        if existing or rid in by_id:
            linked += 1
        else:
            row = {
                "报告ID": rid,
                "机构ID": "eu-stoa",
                "机构英文名": "European Parliament Panel for the Future of Science and Technology (STOA)",
                "国家或地区": "欧盟",
                "发布日期": item.published,
                "观察窗": observation_window(item.published),
                "报告名称": item.title,
                "报告类型": f"European Parliament STOA {item.publication_type}",
                "原文链接": item.url,
                "本地路径": "",
                "正文完整度": "官方出版目录元数据、摘要与正式文号入口；正文未批量落盘",
                "优先级": "P1-China-STI-candidate" if china and relevance != "语境" else "P2-light-catalog" if relevance != "语境" else "P3-context-catalog",
                "示踪问题": f"科技创新相关度={relevance}" + ("；中国科技横向维度" if china else ""),
                "机构观点等级": "欧洲议会STOA正式技术评估；研究结论与欧洲议会政治立场分层使用",
                "样本角色": SERIES_ROLE,
                "编码状态": "目录待筛选",
                "预期用途": "技术评估、科学体系、前沿技术路线、研发政策、创新应用与中国比较",
                "本地原始资产路径": "",
                "原始资产状态": "官方落地页与摘要入口已保存；未批量下载全文",
            }
            catalog.append(row)
            by_id[rid] = row
            by_url[item.url.rstrip("/")] = row
            added += 1
        ledger.append({
            "报告ID": rid,
            "统一目录报告ID": rid,
            "发布日期": item.published,
            "报告名称": item.title,
            "官方文类": item.publication_type,
            "官方文号": item.document_code,
            "科技创新相关度": relevance,
            "中国直接信号": "是" if china else "否",
            "官方落地页": item.url,
            "页面摘要": item.summary,
            "资料层级": "轻量总目录",
            "全文策略": "按科技创新机制、中国比较、跨期转向和独立方法定点精选",
            "采集日期": args.collection_date,
        })
    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("机构ID", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(output_path, ledger, LEDGER_FIELDS)
    year_text = "、".join(f"{year}年{count}项" for year, count in sorted(years.items()))
    type_text = "、".join(f"{kind}{count}项" for kind, count in sorted(types.items()))
    result_path.write_text(
        "# 欧洲议会STOA科技评估近十年轻量总目录结果\n\n"
        f"- 官方目录：{LISTING_URL}\n"
        f"- 采集日期：{args.collection_date}\n"
        f"- 官方全库规模：{EXPECTED_TOTAL}项；纳入2016—{args.collection_date[:4]}时间窗：{len(ledger)}项。\n"
        f"- 年度分布：{year_text}。\n"
        f"- 文类分布：{type_text}。\n"
        f"- 科技创新相关度：核心{counts['核心']}项、支撑{counts['支撑']}项、语境{counts['语境']}项。\n"
        f"- 中国直接信号：{china_count}项。\n"
        f"- 写入统一目录：新增{added}项、关联既有{linked}项；统一目录现为{len(catalog)}项。\n"
        f"- 分页快照摘要：{len(hashes)}页，SHA-256去重值{len(set(hashes))}个。\n\n"
        "## 使用边界\n\n"
        "STOA成果均属于欧洲议会技术评估与科学前瞻体系，轻量目录保留其完整议题结构。全文只选择能够解释科学能力、技术路线、研发组织、创新应用、方法变化或中国比较的跨期节点；一般政治参与、议会程序、纯法律治理及安全议题不自动进入全文层。\n",
        encoding="utf-8",
    )
    print(f"eu_stoa_light_catalog=ok official={EXPECTED_TOTAL} in_window={len(ledger)} added={added} linked={linked} catalog={len(catalog)} core={counts['核心']} support={counts['支撑']} context={counts['语境']} china={china_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
