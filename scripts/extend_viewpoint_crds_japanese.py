from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import io
import re
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import request
from extract_viewpoint_pdf_slices import process_pdf
from extend_viewpoint_bruegel_technology import bruegel_asset_details, catalog_asset_path
from extend_viewpoint_merics_technology import CATALOG_FIELDS, build_theme_rows, normalize_text_content, read_csv, write_csv


SITE_ROOT = "https://www.jst.go.jp/crds/"
CUTOFF = "2016-01-01"
END_DATE = "2026-08-22"
FORMAL_TYPES = {"FR", "SP", "RR", "XR"}
TYPE_ROLES = {
    "FR": "研究开发全景报告", "SP": "研究推进战略建议", "RR": "调查分析报告", "XR": "海外科技政策调查",
}
CORE_TECH_RE = re.compile(
    r"人工知能|\bAI\b|量子|半導体|コンピュ|デジタル|情報|システム|サイバー|ロボット|通信|"
    r"ナノ|材料|デバイス|バイオ|ライフ|医療|創薬|ゲノム|エネルギー|環境|気候|カーボン|"
    r"原子力|核融合|宇宙|モビリティ|電池|水素|光|センシング|データ|計算|技術",
    re.I,
)
THEME_PATTERNS = {
    "人工智能、机器人与计算系统": re.compile(r"人工知能|\bAI\b|ロボット|コンピュ|計算|システム|データ", re.I),
    "芯片、量子、通信与网络安全": re.compile(r"半導体|量子|通信|ネットワーク|サイバー|セキュリティ|光", re.I),
    "先进材料、纳米与制造技术": re.compile(r"材料|ナノ|デバイス|製造|ものづくり|センシング", re.I),
    "生命科学、生物技术与医疗": re.compile(r"バイオ|ライフ|医療|創薬|ゲノム|細胞|健康", re.I),
    "能源、环境与绿色转型": re.compile(r"エネルギー|環境|気候|カーボン|原子力|核融合|電池|水素", re.I),
    "科技创新政策、科研体系与人才": re.compile(r"科学技術|イノベーション|研究開発|研究人材|研究基盤|産学|知的財産|評価", re.I),
    "研究安全、科技外交与国际比较": re.compile(r"研究セキュリティ|安全保障|外交|海外|国際|主要国|米国|欧州|韓国|インド", re.I),
    "中国科技政策与能力比较": re.compile(r"中国|五カ年計画|中華", re.I),
}


@dataclass(frozen=True)
class Candidate:
    landing_url: str
    report_code: str
    report_type: str
    published: str
    title_ja: str
    page_html: str
    page_text: str
    pdf_urls: tuple[str, ...]


def stable_report_id(report_code: str) -> str:
    return f"C-{report_code.replace('CRDS-', 'CRDS-')}"


def canonical_url(url: str) -> str:
    parts = urlsplit(urljoin(SITE_ROOT, html_lib.unescape(url)))
    return urlunsplit(("https", "www.jst.go.jp", re.sub(r"/+", "/", parts.path), "", ""))


def safe_url(url: str) -> str:
    parts = urlsplit(html_lib.unescape(url))
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), parts.query, ""))


def extract_crds_report_links(html_text: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html_text, "html.parser")
    urls = []
    for link in soup.select("a[href]"):
        match = re.search(r"(CRDS-FY\d{4}-([A-Z]+)-\d+(?:_[A-Z]+)?)\.html", link.get("href", ""))
        if match and match.group(2) in FORMAL_TYPES:
            urls.append(f"https://www.jst.go.jp/crds/report/{match.group(1)}.html")
    return sorted(dict.fromkeys(urls))


def extract_official_pdf_urls(html_text: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html_text, "html.parser")
    main = soup.find("main") or soup
    code_match = re.search(r"CRDS-FY\d{4}-[A-Z]+-\d+(?:_[A-Z]+)?", page_url)
    code = code_match.group(0) if code_match else ""
    candidates = []
    for index, link in enumerate(main.select('a[href*=".pdf"], a[href*=".PDF"]')):
        url = urljoin(page_url, html_lib.unescape(link.get("href", "")))
        parts = urlsplit(url)
        if parts.hostname not in {"jst.go.jp", "www.jst.go.jp"} or "/crds/pdf/" not in parts.path:
            continue
        label = link.get_text(" ", strip=True)
        exact = bool(code and re.search(rf"/{re.escape(code)}\.pdf$", parts.path, re.I))
        whole = "PDFをダウンロード" in label or "一括" in label or exact
        candidates.append((0 if whole else 1, index, urlunsplit(("https", "www.jst.go.jp", parts.path, parts.query, ""))))
    if not candidates:
        return []
    candidates.sort()
    best_priority = candidates[0][0]
    return [url for priority, _, url in candidates if priority == best_priority][:1]


def parse_report_page(html_text: str, page_url: str) -> Candidate:
    soup = BeautifulSoup(html_text, "html.parser")
    main = soup.find("main") or soup
    heading = main.find("h1") or soup.find("h1")
    title = heading.get_text(" ", strip=True) if heading else ""
    text = normalize_text_content(main.get_text("\n", strip=True))
    code_match = re.search(r"CRDS-FY\d{4}-([A-Z]+)-\d+(?:_[A-Z]+)?", f"{page_url} {text}")
    report_code = code_match.group(0) if code_match else ""
    report_type = code_match.group(1) if code_match else ""
    date_match = re.search(r"(20\d{2})年\s*(\d{1,2})月", text)
    published = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-01" if date_match else ""
    return Candidate(
        landing_url=canonical_url(page_url), report_code=report_code, report_type=report_type,
        published=published, title_ja=title, page_html=html_text, page_text=text,
        pdf_urls=tuple(extract_official_pdf_urls(html_text, page_url)),
    )


def classify_report_role(report_type: str) -> str:
    return TYPE_ROLES[report_type]


def classify_technology_scope(candidate: Candidate) -> str:
    return "核心科技直接材料" if CORE_TECH_RE.search(f"{candidate.title_ja} {candidate.page_text[:3000]}") else "科技创新政策与国际比较基线"


def classify_themes(candidate: Candidate) -> str:
    text = f"{candidate.title_ja} {candidate.page_text[:5000]}"
    themes = [label for label, pattern in THEME_PATTERNS.items() if pattern.search(text)]
    return "；".join(themes or ["科技战略与研究开发政策"])


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def fetch_candidate(url: str) -> Candidate:
    data, final_url, _ = request(url, timeout=60)
    return parse_report_page(data.decode("utf-8", errors="replace"), final_url)


def load_candidates() -> list[Candidate]:
    detail_urls = []
    for fiscal_year in range(2016, 2026):
        year_url = f"https://www.jst.go.jp/crds/report/by-year/fy{fiscal_year}/index.html"
        data, final_url, _ = request(year_url, timeout=60)
        detail_urls.extend(extract_crds_report_links(data.decode("utf-8", errors="replace"), final_url))
    candidates, errors = [], []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(fetch_candidate, url): url for url in sorted(set(detail_urls))}
        for future in as_completed(futures):
            try:
                candidate = future.result()
                if candidate.title_ja and candidate.pdf_urls and CUTOFF <= candidate.published <= END_DATE:
                    candidates.append(candidate)
            except Exception as exc:
                errors.append(f"{futures[future]}: {exc}")
    if errors:
        raise RuntimeError(f"CRDS discovery failed for {len(errors)} pages; first={errors[0]}")
    return sorted(candidates, key=lambda item: (item.published, item.report_code))


def download_pdf(candidate: Candidate) -> tuple[bytes, str, int]:
    for url in candidate.pdf_urls:
        data, final_url, _ = request(safe_url(url), referer=candidate.landing_url, timeout=120)
        if data[:4] == b"%PDF":
            return data, final_url, len(PdfReader(io.BytesIO(data)).pages)
    return b"", "", 0


def cache_candidate_pdf(candidate: Candidate, pdf_dir: Path, cache_dir: Path) -> tuple[Path, str, int]:
    existing = pdf_dir / f"{stable_report_id(candidate.report_code)}.pdf"
    if existing.exists():
        return existing, candidate.pdf_urls[0], len(PdfReader(str(existing)).pages)
    data, final_url, pages = download_pdf(candidate)
    cached = cache_dir / f"{candidate.report_code}.pdf"
    if data:
        cached.write_bytes(data)
    return cached, final_url, pages


def status_for_existing_catalog_row(row: dict[str, str], asset: Path) -> str:
    """Preserve the provenance semantics of a previous successful CRDS run."""
    if not row.get("报告ID", "").startswith("C-CRDS-FY"):
        return "复用库内既有资产"
    if asset.stem == row["报告ID"]:
        return "官方PDF已保存并校验"
    return "关联既有官方PDF"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    directories = {
        "pdf": root / "03_证据底稿" / "原文PDF", "text": root / "03_证据底稿" / "文本",
        "slice": root / "03_证据底稿" / "切片", "html": root / "03_证据底稿" / "网页快照",
        "web_text": root / "03_证据底稿" / "网页文本", "transcript": root / "03_证据底稿" / "网页转写",
    }
    candidates = load_candidates()
    catalog = read_csv(root / "05_报告总目录.csv")
    existing_by_url = {canonical_url(row["原文链接"]): row for row in catalog if row.get("机构ID") == "jst-crds"}
    prior_ledger = root / "51_CRDS日文科技与中国专题增补台账.csv"
    if prior_ledger.exists():
        catalog_by_id = {row["报告ID"]: row for row in catalog}
        for item in read_csv(prior_ledger):
            if item.get("报告ID") in catalog_by_id and item.get("官方落地页"):
                existing_by_url[canonical_url(item["官方落地页"])] = catalog_by_id[item["报告ID"]]
    existing_hashes = {}
    for pdf_path in directories["pdf"].glob("*.pdf"):
        existing_hashes.setdefault(hashlib.sha256(pdf_path.read_bytes()).hexdigest(), pdf_path)
    legacy_by_hash = {}
    for row in catalog:
        if row.get("机构ID") != "jst-crds" or row.get("报告ID", "").startswith("C-CRDS-FY"):
            continue
        asset = catalog_asset_path(row)
        if asset.exists() and asset.suffix.lower() == ".pdf":
            legacy_by_hash.setdefault(hashlib.sha256(asset.read_bytes()).hexdigest(), row)
    cache_manager = tempfile.TemporaryDirectory(prefix="crds-pdf-cache-")
    cache_dir = Path(cache_manager.name)
    download_cache = {}
    pending = [candidate for candidate in candidates if canonical_url(candidate.landing_url) not in existing_by_url]
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(cache_candidate_pdf, candidate, directories["pdf"], cache_dir): candidate for candidate in pending}
        for completed, future in enumerate(as_completed(futures), 1):
            candidate = futures[future]
            download_cache[candidate.report_code] = future.result()
            print(f"downloaded={completed}/{len(pending)} code={candidate.report_code}", flush=True)
    ledger_rows, new_catalog = [], []
    failed = 0
    for index, candidate in enumerate(candidates, 1):
        existing = existing_by_url.get(canonical_url(candidate.landing_url))
        report_id = existing["报告ID"] if existing else stable_report_id(candidate.report_code)
        local_asset = local_text = local_slice = digest = error = ""
        pages = chars = byte_count = 0
        status = ""
        if existing:
            try:
                local_asset, local_text, local_slice, pages, chars, digest, byte_count = bruegel_asset_details(existing, directories)
                status = status_for_existing_catalog_row(existing, Path(local_asset))
            except Exception as exc:
                error = str(exc)
        if not local_asset:
            try:
                cached_path, pdf_url, pages = download_cache[candidate.report_code]
                data = cached_path.read_bytes() if cached_path.exists() else b""
                digest = hashlib.sha256(data).hexdigest() if data else ""
                if digest in legacy_by_hash:
                    existing = legacy_by_hash[digest]; report_id = existing["报告ID"]
                    local_asset, local_text, local_slice, pages, chars, digest, byte_count = bruegel_asset_details(existing, directories)
                    status = "复用库内既有资产"
                elif data:
                    duplicate = existing_hashes.get(digest)
                    if duplicate:
                        pdf_path = duplicate
                        status = "官方PDF已保存并校验" if duplicate.stem == report_id else "关联既有官方PDF"
                    else:
                        pdf_path = directories["pdf"] / f"{report_id}.pdf"
                        pdf_path.write_bytes(data); existing_hashes[digest] = pdf_path
                        status = "官方PDF已保存并校验"
                    text_path = directories["text"] / f"{pdf_path.stem}.txt"
                    slice_path = directories["slice"] / f"{pdf_path.stem}.md"
                    if not text_path.exists() or not slice_path.exists():
                        process_pdf(pdf_path, directories["text"], directories["slice"])
                    chars = len(text_path.read_text(encoding="utf-8")); byte_count = len(data)
                    local_asset, local_text, local_slice = map(str, (pdf_path, text_path, slice_path))
            except Exception as exc:
                error = str(exc)
        if not local_asset:
            status = "获取失败"; failed += 1
        layer = classify_technology_scope(candidate)
        themes = classify_themes(candidate)
        role = classify_report_role(candidate.report_type)
        catalog_row = existing or {
            "报告ID": report_id, "机构ID": "jst-crds", "机构英文名": "JST Center for Research and Development Strategy",
            "国家或地区": "日本", "发布日期": candidate.published, "观察窗": observation_window(candidate.published),
            "报告名称": candidate.title_ja, "报告类型": role, "原文链接": candidate.landing_url, "本地路径": "",
            "正文完整度": "本地日文原文已保存" if local_asset else "获取失败",
            "优先级": "P0-China-tech-corpus" if "中国科技政策" in themes else ("P0-core-tech" if layer == "核心科技直接材料" else "P1-STI-baseline"),
            "示踪问题": themes, "机构观点等级": "机构正式研究", "样本角色": f"CRDS日文正式报告库/{layer}",
            "编码状态": "待编码", "预期用途": "日本科技战略、关键技术国际比较、中国科技能力、研究安全与创新体系专题复用",
            "本地原始资产路径": local_asset, "原始资产状态": status,
        }
        if report_id.startswith("C-CRDS-FY"):
            new_catalog.append(catalog_row)
        ledger_rows.append({
            "报告ID": report_id, "报告编号": candidate.report_code, "发布日期": candidate.published,
            "观察窗": observation_window(candidate.published), "日文题名": candidate.title_ja, "语言": "日文",
            "报告类型": role, "资料角色": "CRDS机构正式研究", "科技关联层级": layer, "主题标签": themes,
            "官方落地页": candidate.landing_url, "官方PDF": candidate.pdf_urls[0], "本地原始资产": local_asset,
            "本地文本": local_text, "本地切片或转写": local_slice, "字节数": str(byte_count), "SHA256": digest,
            "PDF页数": str(pages), "提取文本字符数": str(chars), "本地状态": status, "错误": error, "获取日期": date.today().isoformat(),
        })
        print(f"processed={index}/{len(candidates)} id={report_id} status={status}", flush=True)
    merged = [row for row in catalog if not row.get("报告ID", "").startswith("C-CRDS-FY")] + new_catalog
    merged.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(root / "05_报告总目录.csv", merged, CATALOG_FIELDS)
    ledger_fields = ["报告ID", "报告编号", "发布日期", "观察窗", "日文题名", "语言", "报告类型", "资料角色", "科技关联层级", "主题标签", "官方落地页", "官方PDF", "本地原始资产", "本地文本", "本地切片或转写", "字节数", "SHA256", "PDF页数", "提取文本字符数", "本地状态", "错误", "获取日期"]
    write_csv(root / "51_CRDS日文科技与中国专题增补台账.csv", ledger_rows, ledger_fields)
    theme_input = [{**row, "报告名称": row["日文题名"]} for row in ledger_rows]
    theme_rows = build_theme_rows(theme_input)
    write_csv(root / "53_CRDS日文科技与中国主题索引.csv", theme_rows, ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"])
    counts = Counter((r["主题标签"], r["科技关联层级"], r["观察窗"], r["本地状态"]) for r in theme_rows)
    matrix = [{"主题标签": k[0], "科技关联层级": k[1], "观察窗": k[2], "本地状态": k[3], "材料数": str(v)} for k, v in sorted(counts.items())]
    write_csv(root / "54_CRDS日文科技与中国复用矩阵.csv", matrix, ["主题标签", "科技关联层级", "观察窗", "本地状态", "材料数"])
    status_counts = Counter(r["本地状态"] for r in ledger_rows); layer_counts = Counter(r["科技关联层级"] for r in ledger_rows)
    lines = ["# CRDS近十年日文科技与中国专题库增补结果", "", f"- 纳入机构正式报告：{len(ledger_rows)}项。", f"- 核心科技直接材料：{layer_counts['核心科技直接材料']}项；科技创新政策与国际比较基线：{layer_counts['科技创新政策与国际比较基线']}项。", f"- 复用库内既有资产：{status_counts['复用库内既有资产']}项；新增官方PDF：{status_counts['官方PDF已保存并校验']}项；关联同版PDF：{status_counts['关联既有官方PDF']}项；失败：{status_counts['获取失败']}项。", f"- 报告总目录：{len(catalog)}项扩展至{len(merged)}项。", "", "## 纳入边界", "", "限定2016年1月1日至2026年8月22日CRDS官方年度目录中的研究开发全景报告、战略建议、调查分析报告和海外科技政策调查。研讨会、会议、转载和其他材料不进入正式研究层。", "", "## 多语种边界", "", "保留官方日文题名和日文全文，不进行大规模机器翻译。跨项目调用先依据中文主题标签定位，再回到日文逐页文本；精确观点引用须保留日文原句、页码和报告编号。", ""]
    (root / "52_CRDS日文科技与中国专题增补结果.md").write_text("\n".join(lines), encoding="utf-8")
    cache_manager.cleanup()
    print(f"candidates={len(candidates)} reused={status_counts['复用库内既有资产']} pdf={status_counts['官方PDF已保存并校验']} linked={status_counts['关联既有官方PDF']} failed={failed} catalog={len(merged)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
