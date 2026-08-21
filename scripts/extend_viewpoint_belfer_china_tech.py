from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import clean_page_text, request
from extract_viewpoint_pdf_slices import process_pdf


API_ROOT = "https://www.belfercenter.org/api/search/search"
SITE_ROOT = "https://www.belfercenter.org/"
CUTOFF = "2016-01-01"
END_DATE = "2026-08-22"
TECH_TOPICS = "691,694,698,702,703,706,710,2851,758,795,801,827,850"
CHINA_TOPICS = "806,821,724"
CONTENT_TYPES = "7,5,6"
TYPE_NAMES = {
    "Reports & Papers": "研究报告与论文",
    "Policy Briefs": "政策简报",
    "Testimonies": "政策证词",
}
PDF_HREF_RE = re.compile(r'href=["\']([^"\']+?\.pdf(?:\?[^"\']*)?)["\']', re.I)
OFFICIAL_HOSTS = {"belfercenter.org", "www.belfercenter.org"}
TECH_PATTERNS = {
    "人工智能、芯片与算力": re.compile(
        r"artificial intelligence|\bAI\b|machine learning|semiconductor|microchip|\bchips?\b|"
        r"computing power|compute infrastructure|data cent(?:er|re)", re.I
    ),
    "网络安全与数字治理": re.compile(
        r"cyber|digital|information operation|internet|data governance|surveillance|cloud|"
        r"software|social media|election security", re.I
    ),
    "技术供应链与出口管制": re.compile(
        r"supply chain|export control|critical minerals?|rare earth|battery|electric vehicle|"
        r"telecom|\b5G\b|\b6G\b|technology transfer", re.I
    ),
    "创新体系与产业政策": re.compile(
        r"innovation|industrial policy|research security|technical standards?|technology competition|"
        r"tech(?:nology)? sovereignty|science and technology|R&D", re.I
    ),
    "国防、航天与无人系统": re.compile(
        r"autonomous|drone|unmanned|robot|space technolog|satellite|hypersonic|military technolog|"
        r"command-and-control|information warfare", re.I
    ),
    "生物、量子及其他前沿技术": re.compile(
        r"biotech|biosecurity|bioconvergence|quantum|advanced materials?|carbon capture|hydrogen", re.I
    ),
}
CHINA_RE = re.compile(r"\b(?:China|Chinese|Beijing|PRC|Sino-)\b", re.I)

CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]


@dataclass(frozen=True)
class SearchCard:
    report_id: str
    published: str
    title: str
    landing_url: str
    content_type: str
    source: str
    discovered_by: frozenset[str] = frozenset()


@dataclass
class Acquisition:
    candidate: SearchCard
    page_data: bytes = b""
    page_text: str = ""
    pdf_url: str = ""
    pdf_data: bytes = b""
    status: str = ""
    error: str = ""


def clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def safe_url(url: str) -> str:
    parts = urlsplit(html.unescape(url))
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), parts.query, ""))


def canonical_url(url: str) -> str:
    parts = urlsplit(urljoin(SITE_ROOT, html.unescape(url)))
    path = re.sub(r"/+", "/", parts.path).rstrip("/") or "/"
    return urlunsplit(("https", "www.belfercenter.org", path, "", ""))


def stable_report_id(url: str) -> str:
    digest = hashlib.sha1(canonical_url(url).encode("utf-8")).hexdigest()[:10].upper()
    return f"C-BEL-{digest}"


def parse_search_cards(source: str) -> list[SearchCard]:
    cards: list[SearchCard] = []
    for match in re.finditer(r"<article\b[\s\S]*?</article>", source, re.I):
        block = match.group(0)
        link = re.search(r"<h2\b[^>]*>[\s\S]*?<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>([\s\S]*?)</a>", block, re.I)
        published = re.search(r"<time\b[^>]*datetime=[\"']([^\"']+)[\"']", block, re.I)
        material_type = re.search(r"<div\s+class=[\"']type[\"']>([\s\S]*?)</div>", block, re.I)
        source_match = re.search(r"<div\s+class=[\"']source[\"']>([\s\S]*?)</div>", block, re.I)
        if not link or not published or not material_type:
            continue
        landing_url = canonical_url(link.group(1))
        cards.append(
            SearchCard(
                report_id=stable_report_id(landing_url),
                published=published.group(1)[:10],
                title=clean_html(link.group(2)),
                landing_url=landing_url,
                content_type=clean_html(material_type.group(1)),
                source=clean_html(source_match.group(1)) if source_match else "",
            )
        )
    return cards


def extract_official_pdf_urls(source: str, landing_url: str = SITE_ROOT) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for raw in PDF_HREF_RE.findall(source):
        url = safe_url(urljoin(landing_url, html.unescape(raw)))
        if urlsplit(url).hostname not in OFFICIAL_HOSTS or "/sites/default/files/" not in url or url in seen:
            continue
        seen.add(url)
        values.append(url)
    return values


def classify_themes(title: str, text: str) -> str:
    combined = f"{title} {text}"
    themes = [label for label, pattern in TECH_PATTERNS.items() if pattern.search(combined)]
    return "；".join(themes or ["综合科技竞争"])


def is_material_relevant(title: str, page_text: str, discovered_by: set[str] | frozenset[str]) -> bool:
    if "tech_topics_with_china_keyword" in discovered_by:
        return bool(CHINA_RE.search(title)) or len(CHINA_RE.findall(page_text)) >= 5
    title_hits = sum(bool(pattern.search(title)) for pattern in TECH_PATTERNS.values())
    body_hits = sum(bool(pattern.search(page_text)) for pattern in TECH_PATTERNS.values())
    return title_hits >= 1 or body_hits >= 3


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def merge_ledger_rows(existing_rows, refreshed_rows, ordered_ids):
    by_id = {row["报告ID"]: row for row in existing_rows}
    by_id.update({row["报告ID"]: row for row in refreshed_rows})
    return [by_id[report_id] for report_id in ordered_ids if report_id in by_id]


def replace_institution_catalog_rows(catalog, refreshed_rows, report_id_prefix):
    retained = [row for row in catalog if not row.get("报告ID", "").startswith(report_id_prefix)]
    return retained + refreshed_rows


def pdf_asset_status(duplicate_path: Path, report_id: str) -> str:
    return "官方PDF已保存并校验" if duplicate_path.stem == report_id else "关联既有官方PDF"


def fetch_search(query: str) -> list[SearchCard]:
    cards: list[SearchCard] = []
    page = 1
    while True:
        url = f"{API_ROOT}?_page={page}&_limit=8&_sort=date&_order=desc&type=research_and_analysis&{query}"
        raw, _, _ = request(url, timeout=60)
        payload = __import__("json").loads(raw.decode("utf-8"))
        cards.extend(parse_search_cards(payload.get("results", "")))
        if page >= int(payload.get("meta", {}).get("totalPages", 1)):
            break
        page += 1
    return cards


def build_candidates() -> list[SearchCard]:
    streams = {
        "tech_topics_with_china_keyword": f"keywords=China&topic={TECH_TOPICS}&content-type={CONTENT_TYPES}",
        "china_topics": f"topic={CHINA_TOPICS}&content-type={CONTENT_TYPES}",
    }
    merged: dict[str, SearchCard] = {}
    for basis, query in streams.items():
        for card in fetch_search(query):
            if not (CUTOFF <= card.published <= END_DATE):
                continue
            previous = merged.get(card.landing_url)
            discovered = set(previous.discovered_by if previous else ()) | {basis}
            merged[card.landing_url] = replace(card, discovered_by=frozenset(discovered))
    return sorted(merged.values(), key=lambda item: (item.published, item.report_id))


def acquire_candidate(candidate: SearchCard) -> Acquisition:
    result = Acquisition(candidate=candidate)
    try:
        page_data, final_url, _ = request(candidate.landing_url, timeout=60)
        result.page_data = page_data
        result.page_text = clean_page_text(page_data)
        source = page_data.decode("utf-8", errors="replace")
        pdf_urls = extract_official_pdf_urls(source, final_url)
        if not pdf_urls:
            result.status = "官方网页全文已保存"
            return result
        result.pdf_url = pdf_urls[0]
        pdf_data, final_pdf_url, _ = request(result.pdf_url, referer=final_url, timeout=120)
        result.pdf_url = final_pdf_url
        if pdf_data.startswith(b"%PDF"):
            result.pdf_data = pdf_data
            result.status = "官方PDF已获取"
        else:
            result.status = "官方网页全文已保存"
            result.error = f"PDF链接返回非PDF: bytes={len(pdf_data)}"
    except Exception as exc:
        result.status = "获取失败"
        result.error = f"{type(exc).__name__}: {exc}"
    return result


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def normalize_extracted_text(path: Path) -> None:
    value = path.read_text(encoding="utf-8")
    normalized = re.sub(r"[ \t\r]+(?=\n|$)", "", value)
    if normalized != value:
        path.write_text(normalized, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    directories = {
        "pdf": root / "03_证据底稿" / "原文PDF",
        "text": root / "03_证据底稿" / "文本",
        "slice": root / "03_证据底稿" / "切片",
        "html": root / "03_证据底稿" / "网页快照",
        "web_text": root / "03_证据底稿" / "网页文本",
        "transcript": root / "03_证据底稿" / "网页转写",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)

    candidates = build_candidates()
    acquisitions: dict[str, Acquisition] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(acquire_candidate, candidate): candidate.report_id for candidate in candidates}
        for future in as_completed(futures):
            report_id = futures[future]
            try:
                acquisitions[report_id] = future.result()
            except Exception as exc:
                candidate = next(item for item in candidates if item.report_id == report_id)
                acquisitions[report_id] = Acquisition(candidate, status="获取失败", error=f"{type(exc).__name__}: {exc}")

    first_party = [
        candidate for candidate in candidates
        if candidate.report_id in acquisitions
        and acquisitions[candidate.report_id].page_text
        and (not candidate.source or "Belfer" in candidate.source)
    ]
    relevant = [
        candidate for candidate in first_party
        if is_material_relevant(candidate.title, acquisitions[candidate.report_id].page_text, candidate.discovered_by)
    ]
    catalog = read_csv(catalog_path)
    ledger_path = root / "35_Belfer涉华科技专题增补台账.csv"
    existing_ledger = read_csv(ledger_path) if ledger_path.exists() else []
    existing_hashes: dict[str, Path] = {}
    for pdf_path in directories["pdf"].glob("*.pdf"):
        existing_hashes.setdefault(hashlib.sha256(pdf_path.read_bytes()).hexdigest(), pdf_path)

    ledger_rows: list[dict[str, str]] = []
    belfer_catalog_rows: list[dict[str, str]] = []
    for candidate in relevant:
        result = acquisitions[candidate.report_id]
        local_asset = local_text = local_slice = digest = ""
        pages = chars = 0
        asset_status = result.status
        if result.pdf_data:
            digest = hashlib.sha256(result.pdf_data).hexdigest()
            duplicate = existing_hashes.get(digest)
            if duplicate:
                pdf_path = duplicate
                asset_status = pdf_asset_status(duplicate, candidate.report_id)
            else:
                pdf_path = directories["pdf"] / f"{candidate.report_id}.pdf"
                pdf_path.write_bytes(result.pdf_data)
                existing_hashes[digest] = pdf_path
                asset_status = "官方PDF已保存并校验"
            pages = len(PdfReader(str(pdf_path)).pages)
            text_path = directories["text"] / f"{pdf_path.stem}.txt"
            slice_path = directories["slice"] / f"{pdf_path.stem}.md"
            if not text_path.exists() or not slice_path.exists():
                process_pdf(pdf_path, directories["text"], directories["slice"])
            normalize_extracted_text(text_path)
            chars = len(text_path.read_text(encoding="utf-8"))
            local_asset, local_text, local_slice = map(str, (pdf_path, text_path, slice_path))
        elif result.page_data and result.page_text:
            html_path = directories["html"] / f"{candidate.report_id}.html"
            text_path = directories["web_text"] / f"{candidate.report_id}.txt"
            transcript_path = directories["transcript"] / f"{candidate.report_id}.md"
            html_path.write_bytes(result.page_data)
            text_path.write_text(result.page_text, encoding="utf-8")
            transcript_path.write_text(
                f"# {candidate.title}\n\n- 发布机构：Belfer Center for Science and International Affairs\n"
                f"- 发布日期：{candidate.published}\n- 官方页面：{candidate.landing_url}\n"
                f"- 材料类型：{candidate.content_type}\n\n{result.page_text}\n",
                encoding="utf-8",
            )
            local_asset, local_text, local_slice = map(str, (text_path, text_path, transcript_path))
            chars = len(result.page_text)
            digest = hashlib.sha256(result.page_text.encode("utf-8")).hexdigest()
            asset_status = "官方网页全文已保存"

        themes = classify_themes(candidate.title, result.page_text)
        type_cn = TYPE_NAMES.get(candidate.content_type, candidate.content_type)
        viewpoint_level = "作者/项目政策证词" if candidate.content_type == "Testimonies" else "作者/项目正式研究"
        row = {
            "报告ID": candidate.report_id, "机构ID": "belfer", "机构英文名": "Belfer Center for Science and International Affairs",
            "国家或地区": "美国", "发布日期": candidate.published, "观察窗": observation_window(candidate.published),
            "报告名称": candidate.title, "报告类型": type_cn, "原文链接": candidate.landing_url, "本地路径": "",
            "正文完整度": "本地原文已保存" if local_asset else "获取失败", "优先级": "P0-China-tech-corpus",
            "示踪问题": themes, "机构观点等级": viewpoint_level, "样本角色": "Belfer涉华科技专题库", "编码状态": "待编码",
            "预期用途": "中美科技竞争、数字安全、创新政策、能源技术及国防前沿技术专题复用",
            "本地原始资产路径": local_asset, "原始资产状态": asset_status if local_asset else "获取失败",
        }
        belfer_catalog_rows.append(row)
        ledger_rows.append({
            "报告ID": candidate.report_id, "发布日期": candidate.published, "观察窗": row["观察窗"], "材料类型": type_cn,
            "报告名称": candidate.title, "资料角色": viewpoint_level, "主题标签": themes,
            "筛选依据": "；".join(sorted(candidate.discovered_by)), "官方来源标识": candidate.source,
            "官方落地页": candidate.landing_url, "官方PDF": result.pdf_url, "本地原始资产": local_asset,
            "本地文本": local_text, "本地切片或转写": local_slice,
            "字节数": str(len(result.pdf_data) if result.pdf_data else len(result.page_data)), "SHA256": digest,
            "PDF页数": str(pages), "提取文本字符数": str(chars), "本地状态": asset_status if local_asset else "获取失败",
            "错误": result.error, "获取日期": date.today().isoformat(),
        })

    ordered_ids = [item.report_id for item in relevant]
    ledger_rows = merge_ledger_rows(existing_ledger, ledger_rows, ordered_ids)
    ledger_fields = [
        "报告ID", "发布日期", "观察窗", "材料类型", "报告名称", "资料角色", "主题标签", "筛选依据", "官方来源标识",
        "官方落地页", "官方PDF", "本地原始资产", "本地文本", "本地切片或转写", "字节数", "SHA256", "PDF页数",
        "提取文本字符数", "本地状态", "错误", "获取日期",
    ]
    write_csv(ledger_path, ledger_rows, ledger_fields)
    merged_catalog = replace_institution_catalog_rows(catalog, belfer_catalog_rows, "C-BEL-")
    merged_catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, merged_catalog, CATALOG_FIELDS)

    theme_rows = [
        {"主题标签": theme, "报告ID": row["报告ID"], "发布日期": row["发布日期"], "观察窗": row["观察窗"],
         "材料类型": row["材料类型"], "报告名称": row["报告名称"], "资料角色": row["资料角色"],
         "本地原始资产": row["本地原始资产"], "本地文本": row["本地文本"], "官方落地页": row["官方落地页"]}
        for row in ledger_rows for theme in row["主题标签"].split("；")
    ]
    theme_fields = ["主题标签", "报告ID", "发布日期", "观察窗", "材料类型", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页"]
    write_csv(root / "37_Belfer涉华科技主题索引.csv", theme_rows, theme_fields)
    counts = Counter((row["主题标签"], row["观察窗"], row["材料类型"]) for row in theme_rows)
    matrix = [{"主题标签": key[0], "观察窗": key[1], "材料类型": key[2], "材料数": str(value)} for key, value in sorted(counts.items())]
    write_csv(root / "38_Belfer涉华科技复用矩阵.csv", matrix, ["主题标签", "观察窗", "材料类型", "材料数"])

    status_counts = Counter(row["本地状态"] for row in ledger_rows)
    type_counts = Counter(row["材料类型"] for row in ledger_rows)
    lines = [
        "# Belfer近十年涉华科技专题库增补结果", "", f"- 纳入材料：{len(ledger_rows)}项。",
        f"- 官方接口候选：{len(candidates)}项；排除非Belfer发布来源{len(candidates) - len(first_party)}项、低强度涉华提及{len(first_party) - len(relevant)}项。",
        f"- 研究报告与论文：{type_counts['研究报告与论文']}项。", f"- 政策简报：{type_counts['政策简报']}项。",
        f"- 政策证词：{type_counts['政策证词']}项。",
        f"- 官方PDF保存或关联：{status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']}项。",
        f"- 官方网页全文保存：{status_counts['官方网页全文已保存']}项。", f"- 获取失败：{status_counts['获取失败']}项。",
        f"- PDF物理页数：{sum(int(row['PDF页数']) for row in ledger_rows):,}。",
        f"- 报告总目录：{len(catalog)}项扩展至{len(merged_catalog)}项。", "", "## 纳入边界", "",
        "材料来自Belfer官方研究检索接口，限定2016年1月1日至2026年8月22日。第一路要求官方科技主题与China全文检索同时命中；第二路要求官方中国主题命中，并由标题或正文中的多类核心科技证据复核。仅纳入研究报告与论文、政策简报、政策证词。", "",
        "## 资料角色边界", "", "报告、论文和简报按作者或项目正式研究处理；证词按作者或项目政策证词处理。除非材料存在明确机构署名及一致立场声明，不自动上升为Belfer统一机构观点。", "",
        "## 跨项目调用", "", "优先从`37_Belfer涉华科技主题索引.csv`按主题与观察窗检索，再回到本地逐页文本和官方原始资产。`38_Belfer涉华科技复用矩阵.csv`用于核验主题、时间窗和材料类型覆盖。", "",
    ]
    (root / "36_Belfer涉华科技专题增补结果.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"candidates={len(candidates)} relevant={len(ledger_rows)} pdf={status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']} web={status_counts['官方网页全文已保存']} failed={status_counts['获取失败']} catalog={len(merged_catalog)}")
    return 1 if any(row["本地状态"] == "获取失败" for row in ledger_rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
