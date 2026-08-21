from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tempfile
import time
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import request
from extract_viewpoint_pdf_slices import process_pdf
from extend_viewpoint_bruegel_technology import bruegel_asset_details, catalog_asset_path
from extend_viewpoint_merics_technology import CATALOG_FIELDS, build_theme_rows, normalize_text_content, read_csv, write_csv
from extend_viewpoint_nbr_technology import fetch_jina


REPORT_LIST_URL = "https://www.nistep.go.jp/reportlist/"
CUTOFF_YEAR = 2016
END_DATE = "2026-08-22"
FORMAL_TYPES = {"NR", "PS", "RM", "DP"}
TYPE_ROLES = {
    "NR": ("NISTEP正式报告", "机构正式研究"),
    "PS": ("政策研究", "机构正式研究"),
    "RM": ("调查资料", "机构正式研究"),
    "DP": ("讨论论文", "作者讨论论文"),
}

KNOWN_RELEASE_ARCHIVES = {
    # This report was issued on a shared "11th foresight survey" release page;
    # neither title search nor the archive title contains RM:290 reliably.
    ("RM", "290"): "https://www.nistep.go.jp/archives/44457/",
}
THEME_PATTERNS = {
    "人工智能、数据与数字技术": re.compile(r"人工知能|\bAI\b|情報技術|デジタル|データ|ソフトウェア|計算", re.I),
    "关键技术、专利与产业竞争力": re.compile(r"特定科学技術|技術領域|半導体|量子|バイオ|ロボット|特許|知的財産|技術多様化", re.I),
    "科技指标、论文与国际比较": re.compile(r"科学技術指標|サイエンスマップ|論文|引用|計量|ベンチマーキング|主要国|国際比較", re.I),
    "科研体系、资助与研究基础": re.compile(r"研究費|研究資金|研究開発|研究活動|研究力|研究施設|大学|学術研究|基礎研究", re.I),
    "科技人才、博士与职业流动": re.compile(r"博士|研究者|人材|キャリア|雇用|移動|ウェルビーイング|女性研究", re.I),
    "企业研发、创新与产学合作": re.compile(r"企業|イノベーション|産学|共同研究|スタートアップ|起業|生産性|地域イノベーション", re.I),
    "科技前瞻、新兴议题与社会": re.compile(r"予測|未来|ホライズン|兆し|新興|科学技術と社会|ELSI|社会受容", re.I),
    "开放科学、研究诚信与治理": re.compile(r"オープン|研究公正|研究セキュリティ|倫理|ガバナンス|政策文書|政策評価", re.I),
    "中国科技能力与国际比较": re.compile(r"中国|中華|China|Chinese", re.I),
}
CORE_TECH_RE = re.compile(r"人工知能|\bAI\b|半導体|量子|バイオ|ロボット|情報技術|特定科学技術|技術領域|特許", re.I)


@dataclass(frozen=True)
class Candidate:
    report_type: str
    number: str
    published: str
    title_ja: str
    landing_url: str
    record_id: str = ""


@dataclass
class Acquisition:
    candidate: Candidate
    pdf_url: str = ""
    pdf_cache: str = ""
    proxy_cache: str = ""
    oai_cache: str = ""
    source: str = ""
    status: str = ""
    error: str = ""


def parse_report_list(html_text: str) -> list[Candidate]:
    soup = BeautifulSoup(html_text, "html.parser")
    rows: list[Candidate] = []
    for table_row in soup.select("tr"):
        cells = table_row.find_all("td", recursive=False)
        if len(cells) < 3:
            continue
        code = " ".join(cells[0].get_text(" ", strip=True).split())
        when = " ".join(cells[1].get_text(" ", strip=True).split())
        match = re.fullmatch(r"(NR|PS|RM|DP):\s*(\d+)", code, re.I)
        date_match = re.search(r"(20\d{2})年\s*(\d{1,2})月", when)
        link = cells[2].find("a", href=True)
        if not match or not date_match or not link:
            continue
        year, month = int(date_match.group(1)), int(date_match.group(2))
        if year < CUTOFF_YEAR:
            continue
        candidate = Candidate(
            report_type=match.group(1).upper(), number=match.group(2),
            published=f"{year:04d}-{month:02d}-01",
            title_ja=" ".join(cells[2].get_text(" ", strip=True).split()),
            landing_url=urljoin(REPORT_LIST_URL, link.get("href", "").strip()),
        )
        if candidate.published <= END_DATE:
            rows.append(candidate)
    unique = {stable_report_id(row.report_type, row.number, row.landing_url): row for row in rows}
    return sorted(unique.values(), key=lambda row: (row.published, row.report_type, int(row.number), row.landing_url))


def stable_report_id(report_type: str, number: str, landing_url: str) -> str:
    digest = hashlib.sha1(landing_url.strip().encode("utf-8")).hexdigest()[:8].upper()
    return f"C-NISTEP-{report_type}{number}-{digest}"


def mirror_pdf_names(report_type: str, number: str) -> list[str]:
    return [
        f"NISTEP-{report_type}{number}-FullJ.pdf", f"NISTEP-{report_type}-{number}-FullJ.pdf",
        f"NISTEP-{report_type}{number}-Full.pdf", f"NISTEP-{report_type}-{number}-Full.pdf",
    ]


def indicator_html_index_url(title: str, number: str) -> str:
    match = re.fullmatch(r"科学技術指標(\d{4})", "".join(title.split()))
    if not match:
        return ""
    year = match.group(1)
    return f"https://www.nistep.go.jp/sti_indicator/{year}/RM{number}_00.html"


def extract_indicator_html_links(html: bytes, index_url: str) -> list[str]:
    base = urlsplit(index_url)
    directory = base.path.rsplit("/", 1)[0] + "/"
    links: list[str] = []
    for anchor in BeautifulSoup(html, "html.parser").select("a[href]"):
        resolved = urlsplit(urljoin(index_url, anchor.get("href", "")))
        if resolved.scheme not in {"http", "https"} or resolved.netloc != base.netloc:
            continue
        if not resolved.path.startswith(directory) or not resolved.path.lower().endswith((".html", ".htm")):
            continue
        clean = urlunsplit(("https", resolved.netloc, resolved.path, resolved.query, ""))
        if clean != index_url and clean not in links:
            links.append(clean)
    return links


def fetch_indicator_html_report(candidate: Candidate, fetcher=None) -> tuple[str, str]:
    index_url = indicator_html_index_url(candidate.title_ja, candidate.number)
    if not index_url:
        return "", ""
    loader = fetcher or request
    index_html, _, content_type = loader(index_url, timeout=60)
    if "html" not in content_type.lower():
        return "", ""
    page_urls = [index_url, *extract_indicator_html_links(index_html, index_url)]
    sections: list[str] = []
    for page_url in page_urls:
        try:
            html = index_html if page_url == index_url else loader(page_url, timeout=60)[0]
            soup = BeautifulSoup(html.decode("utf-8", errors="replace"), "html.parser")
            for node in soup.select("script, style, nav, header, footer"):
                node.decompose()
            text = normalize_text_content(soup.get_text("\n", strip=True))
            if text:
                sections.append(f"## SOURCE {page_url}\n\n{text}")
        except Exception:
            continue
    return normalize_text_content("\n\n".join(sections)), index_url


def fetch_official_release_page(candidate: Candidate, fetcher=None) -> tuple[str, str]:
    loader = fetcher or request
    normalized_title = unicodedata.normalize("NFKC", candidate.title_ja)
    known_url = KNOWN_RELEASE_ARCHIVES.get((candidate.report_type, candidate.number), "")
    if known_url:
        page_html, final_url, page_type = loader(known_url, timeout=60)
        if "html" not in page_type.lower():
            return "", ""
        soup = BeautifulSoup(page_html.decode("utf-8", errors="replace"), "html.parser")
        for node in soup.select("script, style, nav, header, footer, aside"):
            node.decompose()
        content = soup.select_one("article, .entry-content, main") or soup
        text = normalize_text_content(content.get_text("\n", strip=True))
        normalized_page = unicodedata.normalize("NFKC", text)
        if candidate.number not in normalized_page:
            return "", ""
        return (f"## SOURCE {final_url}\n\n{text}" if text else ""), final_url
    designation = {
        "RM": f"調査資料-{candidate.number}",
        "NR": f"NISTEP REPORT No.{candidate.number}",
        "PS": f"POLICY STUDY No.{candidate.number}",
        "DP": f"DISCUSSION PAPER No.{candidate.number}",
    }.get(candidate.report_type, f"{candidate.report_type}{candidate.number}")
    queries = [candidate.title_ja, normalized_title, designation, f"{candidate.report_type}{candidate.number}"]
    teiten_year = re.search(r"NISTEP\s*定点調査\s*(20\d{2})", normalized_title)
    if teiten_year:
        queries.append(f"NISTEP定点調査{teiten_year.group(1)}")
    if candidate.report_type == "RM" and candidate.number == "290":
        queries.append("第11回科学技術予測調査 各論報告書")
    if candidate.report_type == "DP" and candidate.number == "248":
        queries.append("プレプリント 査読論文 先行性 実証分析")
    queries = list(dict.fromkeys(queries))
    target = re.sub(r"[^0-9A-Za-z一-龥ぁ-んァ-ヶ]+", "", normalized_title)
    candidates: list[tuple[float, str]] = []
    seen_urls: set[str] = set()
    for query in queries:
        search_url = f"https://www.nistep.go.jp/?s={quote(query)}"
        try:
            search_html, _, content_type = loader(search_url, timeout=60)
        except Exception:
            continue
        if "html" not in content_type.lower():
            continue
        for anchor in BeautifulSoup(search_html.decode("utf-8", errors="replace"), "html.parser").select('a[href*="/archives/"]'):
            href = urljoin(search_url, anchor.get("href", "")).rstrip("/") + "/"
            if href in seen_urls or not re.fullmatch(r"https://www\.nistep\.go\.jp/archives/\d+/?", href):
                continue
            seen_urls.add(href)
            raw_label = anchor.get_text(" ", strip=True)
            label = re.sub(r"[^0-9A-Za-z一-龥ぁ-んァ-ヶ]+", "", raw_label)
            score = SequenceMatcher(None, target, label).ratio()
            if designation.lower().replace(" ", "") in raw_label.lower().replace(" ", ""):
                score += 0.35
            candidates.append((score, href))
    if not candidates or max(candidates)[0] < 0.35:
        for query in queries:
            rest_url = f"https://www.nistep.go.jp/wp-json/wp/v2/search?search={quote(query)}&per_page=20"
            try:
                rest_data, _, rest_type = loader(rest_url, timeout=60)
                if "json" not in rest_type.lower():
                    continue
                for item in json.loads(rest_data.decode("utf-8", errors="replace")):
                    href = str(item.get("url", "")).rstrip("/") + "/"
                    if not re.fullmatch(r"https://www\.nistep\.go\.jp/archives/\d+/?", href):
                        continue
                    raw_label = BeautifulSoup(str(item.get("title", "")), "html.parser").get_text(" ", strip=True)
                    label = re.sub(r"[^0-9A-Za-z一-龥ぁ-んァ-ヶ]+", "", raw_label)
                    score = SequenceMatcher(None, target, label).ratio()
                    if candidate.number in raw_label:
                        score += 0.35
                    candidates.append((score, href))
            except Exception:
                continue
    if not candidates:
        return "", ""
    score, page_url = max(candidates)
    if score < 0.35:
        return "", ""
    page_html, final_url, page_type = loader(page_url, timeout=60)
    if "html" not in page_type.lower():
        return "", ""
    soup = BeautifulSoup(page_html.decode("utf-8", errors="replace"), "html.parser")
    for node in soup.select("script, style, nav, header, footer, aside"):
        node.decompose()
    content = soup.select_one("article, .entry-content, main") or soup
    text = normalize_text_content(content.get_text("\n", strip=True))
    return (f"## SOURCE {final_url}\n\n{text}" if text else ""), final_url


def safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), parts.query, ""))


def select_full_pdf_url(metadata_text: str) -> str:
    urls = list(dict.fromkeys(re.findall(r"https?://nistep\.repo\.nii\.ac\.jp/record/\d+/files/[^\s\])]+?\.pdf", metadata_text, re.I)))
    if not urls:
        return ""
    excluded = re.compile(r"Abstract|Summary|Statistics|Press|Slide|Data|Questionnaire|Errata|Appendix", re.I)
    for pattern in (r"FullJ\.pdf$", r"Full(?:_?J)?\.pdf$", r"\.pdf$"):
        for url in urls:
            if re.search(pattern, url, re.I) and (pattern == r"\.pdf$" or not excluded.search(url)):
                return url
    return urls[0]


def classify_report_role(report_type: str) -> tuple[str, str]:
    return TYPE_ROLES[report_type]


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def classify_technology_scope(title: str) -> str:
    return "核心科技直接材料" if CORE_TECH_RE.search(title) else "科技创新政策与能力基线"


def classify_themes(title: str, evidence_text: str) -> str:
    text = f"{title} {evidence_text[:12000]}"
    themes = [label for label, pattern in THEME_PATTERNS.items() if pattern.search(text)]
    return "；".join(themes or ["科技创新政策与研究体系"])


def resolve_record_id(candidate: Candidate) -> Candidate:
    if "nistep.repo.nii.ac.jp/records/" in candidate.landing_url:
        match = re.search(r"/records/(\d+)", candidate.landing_url)
        return replace(candidate, record_id=match.group(1) if match else "")
    try:
        response = httpx.get(candidate.landing_url, follow_redirects=True, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        match = re.search(r"/records?/(\d+)", str(response.url))
        return replace(candidate, record_id=match.group(1) if match else "")
    except Exception:
        return candidate


def probe_mirror(candidate: Candidate, names: list[str] | None = None) -> str:
    for filename in names or mirror_pdf_names(candidate.report_type, candidate.number):
        url = f"https://www.nistep.go.jp/wp/wp-content/uploads/{filename}"
        try:
            response = httpx.head(url, follow_redirects=True, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200 and "pdf" in response.headers.get("content-type", "").lower():
                return url
        except Exception:
            continue
    return ""


def oai_proxy_url(record_id: str) -> str:
    identifier = record_id.zfill(8)
    source = f"https://nistep.repo.nii.ac.jp/oai?verb=GetRecord&metadataPrefix=jpcoar_2.0&identifier=oai:nistep.repo.nii.ac.jp:{identifier}"
    return f"https://r.jina.ai/{source}"


def official_archive_pdf_from_page(candidate: Candidate) -> tuple[str, str]:
    if "nistep.go.jp/archives/" not in candidate.landing_url:
        return "", ""
    data, final_url, content_type = request(candidate.landing_url, timeout=60)
    if "html" not in content_type.lower():
        return "", ""
    soup = BeautifulSoup(data.decode("utf-8", errors="replace"), "html.parser")
    links = [urljoin(final_url, link.get("href", "")) for link in soup.select('a[href*=".pdf"], a[href*=".PDF"]')]
    full = [url for url in links if re.search(r"FullJ|報告書", url, re.I)]
    return (full or links or [""])[0], normalize_text_content(soup.get_text("\n", strip=True))


def fetch_pdf(url: str, referer: str) -> bytes:
    data, _, _ = request(safe_url(url), referer=referer, timeout=180)
    return data if data[:4] == b"%PDF" else b""


def acquire(candidate: Candidate, mirror_url: str, cache_dir: Path) -> Acquisition:
    result = Acquisition(candidate=candidate)
    try:
        archive_pdf, archive_text = official_archive_pdf_from_page(candidate)
        result.pdf_url = mirror_url or archive_pdf
        if result.pdf_url:
            pdf_data = fetch_pdf(result.pdf_url, candidate.landing_url)
            if pdf_data:
                pdf_cache = cache_dir / f"{stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)}.pdf"
                pdf_cache.write_bytes(pdf_data)
                result.pdf_cache = str(pdf_cache)
                result.source = "NISTEP主站官方PDF"
                result.status = "官方PDF已保存并校验"
                return result
        indicator_text, indicator_url = fetch_indicator_html_report(candidate)
        if len(indicator_text) >= 400:
            report_id = stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)
            proxy_cache = cache_dir / f"{report_id}.txt"
            page_cache = cache_dir / f"{report_id}-html.md"
            proxy_cache.write_text(indicator_text, encoding="utf-8")
            page_cache.write_text(indicator_text, encoding="utf-8")
            result.proxy_cache = str(proxy_cache)
            result.oai_cache = str(page_cache)
            result.source = "NISTEP官方HTML版报告"
            result.status = "官方HTML版报告已保存"
            return result
        release_text, release_url = fetch_official_release_page(candidate)
        if len(release_text) >= 180:
            report_id = stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)
            proxy_cache = cache_dir / f"{report_id}.txt"
            page_cache = cache_dir / f"{report_id}-release.md"
            proxy_cache.write_text(release_text, encoding="utf-8")
            page_cache.write_text(release_text, encoding="utf-8")
            result.proxy_cache = str(proxy_cache)
            result.oai_cache = str(page_cache)
            result.source = "NISTEP官方发布页摘要"
            result.status = "官方发布页摘要已保存"
            result.pdf_url = release_url
            return result
        if not candidate.record_id:
            if archive_text:
                proxy_cache = cache_dir / f"{stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)}.txt"
                proxy_cache.write_text(archive_text, encoding="utf-8")
                result.proxy_cache = str(proxy_cache)
                result.source = "NISTEP官方发布页全文"
                result.status = "官方网页全文已保存"
                return result
            raise RuntimeError("repository record id unavailable")
        oai_text = fetch_jina(oai_proxy_url(candidate.record_id), timeout=120)
        oai_cache = cache_dir / f"{stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)}-oai.md"
        oai_cache.write_text(oai_text, encoding="utf-8")
        result.oai_cache = str(oai_cache)
        result.pdf_url = select_full_pdf_url(oai_text)
        if not result.pdf_url:
            raise RuntimeError("OAI metadata contains no report PDF")
        exact_mirror = probe_mirror(candidate, [Path(urlsplit(result.pdf_url).path).name])
        if exact_mirror:
            result.pdf_url = exact_mirror
            pdf_data = fetch_pdf(exact_mirror, candidate.landing_url)
            if pdf_data:
                pdf_cache = cache_dir / f"{stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)}.pdf"
                pdf_cache.write_bytes(pdf_data)
                result.pdf_cache = str(pdf_cache)
                result.source = "NISTEP主站官方PDF"
                result.status = "官方PDF已保存并校验"
                return result
        time.sleep(3.1)
        proxy_text = fetch_jina(f"https://r.jina.ai/{result.pdf_url}", timeout=180)
        if len(proxy_text) < 400:
            raise RuntimeError(f"thin repository PDF proxy text: {len(proxy_text)}")
        proxy_cache = cache_dir / f"{stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)}.txt"
        proxy_cache.write_text(proxy_text, encoding="utf-8")
        result.proxy_cache = str(proxy_cache)
        result.source = "NISTEP官方仓储PDF的Jina代理全文"
        result.status = "官方仓储PDF代理全文已保存"
    except Exception as exc:
        result.status = "获取失败"
        result.error = f"{type(exc).__name__}: {exc}"
    return result


def status_for_existing(row: dict[str, str], asset: Path) -> str:
    if not row.get("报告ID", "").startswith("C-NISTEP-"):
        return "复用库内既有资产"
    if asset.suffix.lower() == ".pdf":
        return "官方PDF已保存并校验" if asset.stem == row["报告ID"] else "关联既有官方PDF"
    return row.get("原始资产状态") or "官方仓储PDF代理全文已保存"


def nistep_status_summary(statuses: Counter) -> str:
    return (
        f"复用既有资产：{statuses['复用库内既有资产']}项；"
        f"官方PDF保存：{statuses['官方PDF已保存并校验']}项；"
        f"同版PDF关联：{statuses['关联既有官方PDF']}项；"
        f"仓储PDF代理全文：{statuses['官方仓储PDF代理全文已保存']}项；"
        f"官方HTML版报告：{statuses['官方HTML版报告已保存']}项；"
        f"官方网页全文：{statuses['官方网页全文已保存']}项；"
        f"官方发布页摘要：{statuses['官方发布页摘要已保存']}项；"
        f"失败：{statuses['获取失败']}项。"
    )


COMPARISON_FIELDS = [
    "对照层级", "主题或维度", "机构", "机构功能", "材料数", "W1", "W2", "W3",
    "核心科技直接材料", "中国主题材料", "机构正式研究", "作者讨论研究",
    "官方PDF或复用", "网页或代理全文", "待补全文", "使用边界",
]


def build_crds_nistep_comparison(crds_rows: list[dict[str, str]], nistep_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    definitions = [
        (
            "CRDS", crds_rows, "技术路线、研发战略、领域全景与国际科技政策",
            "CRDS材料按机构正式研究使用；机器主题标签只作检索入口，精确引用回查日文PDF、报告编号和页码。",
        ),
        (
            "NISTEP", nistep_rows, "科技指标、科研体系、人才、企业创新与科技前瞻",
            "NR、PS、RM可按机构成果使用；DP按作者归因；代理或HTML资产精确引用时回查官方日文原文。",
        ),
    ]

    def make_row(level: str, theme: str, institution: str, function: str, boundary: str, rows: list[dict[str, str]]) -> dict[str, str]:
        statuses = Counter(row.get("本地状态", "") for row in rows)
        return {
            "对照层级": level, "主题或维度": theme, "机构": institution, "机构功能": function,
            "材料数": str(len(rows)),
            "W1": str(sum(row.get("观察窗") == "W1" for row in rows)),
            "W2": str(sum(row.get("观察窗") == "W2" for row in rows)),
            "W3": str(sum(row.get("观察窗") == "W3" for row in rows)),
            "核心科技直接材料": str(sum(row.get("科技关联层级") == "核心科技直接材料" for row in rows)),
            "中国主题材料": str(sum("中国" in row.get("主题标签", "") for row in rows)),
            "机构正式研究": str(sum("机构" in row.get("资料角色", "") for row in rows)),
            "作者讨论研究": str(sum("作者" in row.get("资料角色", "") for row in rows)),
            "官方PDF或复用": str(
                statuses["官方PDF已保存并校验"] + statuses["关联既有官方PDF"] + statuses["复用库内既有资产"]
            ),
            "网页或代理全文": str(
                statuses["官方仓储PDF代理全文已保存"] + statuses["官方HTML版报告已保存"] + statuses["官方网页全文已保存"]
            ),
            "待补全文": str(statuses["获取失败"] + statuses["官方发布页摘要已保存"]), "使用边界": boundary,
        }

    output: list[dict[str, str]] = []
    for institution, rows, function, boundary in definitions:
        output.append(make_row("机构总览", "全部材料", institution, function, boundary, rows))
        themes = sorted({theme for row in rows for theme in row.get("主题标签", "").split("；") if theme})
        for theme in themes:
            subset = [row for row in rows if theme in row.get("主题标签", "").split("；")]
            output.append(make_row("主题覆盖", theme, institution, function, boundary, subset))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument(
        "--retry-summaries",
        action="store_true",
        help="retry rows that currently have only an official release-page summary",
    )
    args = parser.parse_args()
    root = args.research.resolve()
    directories = {
        "pdf": root / "03_证据底稿" / "原文PDF", "text": root / "03_证据底稿" / "文本",
        "slice": root / "03_证据底稿" / "切片", "html": root / "03_证据底稿" / "网页快照",
        "web_text": root / "03_证据底稿" / "网页文本", "transcript": root / "03_证据底稿" / "网页转写",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    data, _, _ = request(REPORT_LIST_URL, timeout=90)
    candidates = parse_report_list(data.decode("utf-8", errors="replace"))
    with ThreadPoolExecutor(max_workers=16) as executor:
        candidates = list(executor.map(resolve_record_id, candidates))
    catalog = read_csv(root / "05_报告总目录.csv")
    # A catalog row with no local asset is an acquisition placeholder, not a
    # completed item.  Keep it eligible for retry on later runs.
    existing_by_url = {
        row["原文链接"].strip(): row
        for row in catalog
        if (row.get("机构ID") == "nistep" or row.get("报告ID", "").startswith("C-NISTEP-"))
        and row.get("本地原始资产路径", "").strip()
        and Path(row["本地原始资产路径"]).exists()
        and (not args.retry_summaries or row.get("原始资产状态") != "官方发布页摘要已保存")
    }
    ledger_path = root / "55_NISTEP日文科技与中国专题增补台账.csv"
    if ledger_path.exists():
        catalog_by_id = {row["报告ID"]: row for row in catalog}
        for item in read_csv(ledger_path):
            catalog_row = catalog_by_id.get(item.get("报告ID", ""))
            if catalog_row and catalog_row.get("本地原始资产路径", "").strip() and Path(catalog_row["本地原始资产路径"]).exists():
                if not args.retry_summaries or catalog_row.get("原始资产状态") != "官方发布页摘要已保存":
                    existing_by_url[item["官方落地页"].strip()] = catalog_by_id[item["报告ID"]]
    targets = [candidate for candidate in candidates if candidate.landing_url.strip() not in existing_by_url]
    mirror_urls: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(probe_mirror, candidate): candidate for candidate in targets}
        for future in as_completed(futures):
            candidate = futures[future]
            mirror_urls[stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)] = future.result()
    cache_manager = tempfile.TemporaryDirectory(prefix="nistep-cache-")
    cache_dir = Path(cache_manager.name)
    acquisitions: dict[str, Acquisition] = {}
    direct_targets = [candidate for candidate in targets if mirror_urls.get(stable_report_id(candidate.report_type, candidate.number, candidate.landing_url))]
    proxy_targets = [candidate for candidate in targets if candidate not in direct_targets]
    completed = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(acquire, candidate, mirror_urls[stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)], cache_dir): candidate
            for candidate in direct_targets
        }
        for future in as_completed(futures):
            candidate = futures[future]
            report_id = stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)
            acquisitions[report_id] = future.result()
            completed += 1
            print(f"acquired={completed}/{len(targets)} id={report_id} status={acquisitions[report_id].status}", flush=True)
    for candidate in proxy_targets:
        report_id = stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)
        acquisitions[report_id] = acquire(candidate, "", cache_dir)
        completed += 1
        print(f"acquired={completed}/{len(targets)} id={report_id} status={acquisitions[report_id].status}", flush=True)
        if completed < len(targets):
            time.sleep(3.1)

    existing_hashes = {hashlib.sha256(path.read_bytes()).hexdigest(): path for path in directories["pdf"].glob("*.pdf")}
    legacy_by_hash: dict[str, dict[str, str]] = {}
    for row in catalog:
        if row.get("机构ID") != "nistep" or row.get("报告ID", "").startswith("C-NISTEP-"):
            continue
        asset = catalog_asset_path(row)
        if asset.exists() and asset.suffix.lower() == ".pdf":
            legacy_by_hash.setdefault(hashlib.sha256(asset.read_bytes()).hexdigest(), row)
    ledger_rows: list[dict[str, str]] = []
    new_catalog: list[dict[str, str]] = []
    for candidate in candidates:
        generated_id = stable_report_id(candidate.report_type, candidate.number, candidate.landing_url)
        existing = existing_by_url.get(candidate.landing_url.strip())
        report_id = existing["报告ID"] if existing else generated_id
        local_asset = local_text = local_slice = digest = error = source = pdf_url = evidence_text = ""
        pages = chars = byte_count = 0
        status = ""
        if existing:
            try:
                local_asset, local_text, local_slice, pages, chars, digest, byte_count = bruegel_asset_details(existing, directories)
                status = status_for_existing(existing, Path(local_asset))
                evidence_text = Path(local_text).read_text(encoding="utf-8", errors="replace") if Path(local_text).exists() else ""
                source = "既有本地资产"
            except Exception as exc:
                error = str(exc)
        result = acquisitions.get(generated_id)
        if not local_asset and result:
            error = result.error
            source, pdf_url, status = result.source, result.pdf_url, result.status
            if result.pdf_cache:
                pdf_data = Path(result.pdf_cache).read_bytes()
                digest = hashlib.sha256(pdf_data).hexdigest()
                if digest in legacy_by_hash:
                    existing = legacy_by_hash[digest]
                    report_id = existing["报告ID"]
                    local_asset, local_text, local_slice, pages, chars, digest, byte_count = bruegel_asset_details(existing, directories)
                    evidence_text = Path(local_text).read_text(encoding="utf-8", errors="replace")
                    status, source = "复用库内既有资产", "既有本地资产"
                else:
                    duplicate = existing_hashes.get(digest)
                    if duplicate:
                        pdf_path = duplicate
                        status = "官方PDF已保存并校验" if duplicate.stem == report_id else "关联既有官方PDF"
                    else:
                        pdf_path = directories["pdf"] / f"{report_id}.pdf"
                        pdf_path.write_bytes(pdf_data)
                        existing_hashes[digest] = pdf_path
                    text_path = directories["text"] / f"{pdf_path.stem}.txt"
                    slice_path = directories["slice"] / f"{pdf_path.stem}.md"
                    if not text_path.exists() or not slice_path.exists():
                        process_pdf(pdf_path, directories["text"], directories["slice"])
                    pages = len(PdfReader(io.BytesIO(pdf_data)).pages)
                    evidence_text = text_path.read_text(encoding="utf-8", errors="replace")
                    chars, byte_count = len(evidence_text), len(pdf_data)
                    local_asset, local_text, local_slice = map(str, (pdf_path, text_path, slice_path))
            elif result.proxy_cache:
                proxy_text = normalize_text_content(Path(result.proxy_cache).read_text(encoding="utf-8", errors="replace"))
                snapshot = directories["html"] / f"{report_id}.md"
                text_path = directories["web_text"] / f"{report_id}.txt"
                transcript = directories["transcript"] / f"{report_id}.md"
                oai_text = Path(result.oai_cache).read_text(encoding="utf-8", errors="replace") if result.oai_cache else proxy_text
                snapshot.write_text(normalize_text_content(oai_text), encoding="utf-8")
                text_path.write_text(proxy_text, encoding="utf-8")
                transcript.write_text(
                    f"# {candidate.title_ja}\n\n- 发布机构：National Institute of Science and Technology Policy\n"
                    f"- 报告编号：{candidate.report_type}:{candidate.number}\n- 发布日期：{candidate.published}\n"
                    f"- 官方落地页：{candidate.landing_url}\n- 官方PDF：{result.pdf_url}\n- 获取方式：{result.source}\n\n{proxy_text}",
                    encoding="utf-8",
                )
                digest = hashlib.sha256(proxy_text.encode("utf-8")).hexdigest()
                evidence_text, chars, byte_count = proxy_text, len(proxy_text), len(proxy_text.encode("utf-8"))
                local_asset, local_text, local_slice = map(str, (text_path, text_path, transcript))
        if not local_asset:
            status = "获取失败"
        material_type, viewpoint_level = classify_report_role(candidate.report_type)
        tech_layer = classify_technology_scope(candidate.title_ja)
        themes = classify_themes(candidate.title_ja, evidence_text)
        catalog_row = existing or {
            "报告ID": report_id, "机构ID": "nistep", "机构英文名": "National Institute of Science and Technology Policy",
            "国家或地区": "日本", "发布日期": candidate.published, "观察窗": observation_window(candidate.published),
            "报告名称": candidate.title_ja, "报告类型": material_type, "原文链接": candidate.landing_url, "本地路径": "",
            "正文完整度": (
                "仅官方发布页摘要，全文待补" if status == "官方发布页摘要已保存"
                else "本地日文原文已保存" if local_asset else "获取失败"
            ),
            "优先级": "P0-China-tech-corpus" if "中国科技能力" in themes else ("P0-core-tech" if tech_layer == "核心科技直接材料" else "P1-STI-baseline"),
            "示踪问题": themes, "机构观点等级": viewpoint_level, "样本角色": f"NISTEP日文正式研究库/{tech_layer}",
            "编码状态": "待编码", "预期用途": "科技指标、中国国际比较、研发体系、科技人才、企业创新与科技前瞻专题复用",
            "本地原始资产路径": local_asset, "原始资产状态": status,
        }
        if report_id.startswith("C-NISTEP-"):
            new_catalog.append(catalog_row)
        ledger_rows.append({
            "报告ID": report_id, "报告编号": f"{candidate.report_type}:{candidate.number}", "发布日期": candidate.published,
            "观察窗": observation_window(candidate.published), "日文题名": candidate.title_ja, "语言": "日文",
            "报告类型": material_type, "资料角色": viewpoint_level, "科技关联层级": tech_layer, "主题标签": themes,
            "官方落地页": candidate.landing_url, "仓储记录ID": candidate.record_id, "官方PDF": pdf_url,
            "页面来源": source, "本地原始资产": local_asset, "本地文本": local_text, "本地切片或转写": local_slice,
            "字节数": str(byte_count), "SHA256": digest, "PDF页数": str(pages), "提取文本字符数": str(chars),
            "本地状态": status, "错误": error, "获取日期": date.today().isoformat(),
        })
    merged = [row for row in catalog if not row.get("报告ID", "").startswith("C-NISTEP-")] + new_catalog
    merged.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(root / "05_报告总目录.csv", merged, CATALOG_FIELDS)
    fields = ["报告ID", "报告编号", "发布日期", "观察窗", "日文题名", "语言", "报告类型", "资料角色", "科技关联层级", "主题标签", "官方落地页", "仓储记录ID", "官方PDF", "页面来源", "本地原始资产", "本地文本", "本地切片或转写", "字节数", "SHA256", "PDF页数", "提取文本字符数", "本地状态", "错误", "获取日期"]
    write_csv(ledger_path, ledger_rows, fields)
    theme_input = [{**row, "报告名称": row["日文题名"]} for row in ledger_rows]
    theme_rows = build_theme_rows(theme_input)
    write_csv(root / "57_NISTEP日文科技与中国主题索引.csv", theme_rows, ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"])
    matrix_counts = Counter(
        (theme, row["科技关联层级"], row["观察窗"], row["报告类型"], row["本地状态"])
        for row in ledger_rows for theme in row["主题标签"].split("；")
    )
    matrix = [{"主题标签": key[0], "科技关联层级": key[1], "观察窗": key[2], "报告类型": key[3], "本地状态": key[4], "材料数": str(value)} for key, value in sorted(matrix_counts.items())]
    write_csv(root / "58_NISTEP日文科技与中国复用矩阵.csv", matrix, ["主题标签", "科技关联层级", "观察窗", "报告类型", "本地状态", "材料数"])
    crds_path = root / "51_CRDS日文科技与中国专题增补台账.csv"
    if crds_path.exists():
        comparison = build_crds_nistep_comparison(read_csv(crds_path), ledger_rows)
        write_csv(root / "59_CRDS_NISTEP科技主题与机构功能对照.csv", comparison, COMPARISON_FIELDS)
    statuses, types = Counter(row["本地状态"] for row in ledger_rows), Counter(row["报告类型"] for row in ledger_rows)
    lines = [
        "# NISTEP近十年日文科技与中国专题库增补结果", "", f"- 纳入正式研究成果：{len(ledger_rows)}项。",
        f"- NISTEP正式报告：{types['NISTEP正式报告']}项；政策研究：{types['政策研究']}项；调查资料：{types['调查资料']}项；讨论论文：{types['讨论论文']}项。",
        f"- {nistep_status_summary(statuses)}",
        f"- 报告总目录现为：{len(merged)}项。", "", "## 纳入边界", "",
        "限定2016年1月1日至2026年8月22日NISTEP官方报告总目录中的NISTEP REPORT、POLICY STUDY、调查资料和DISCUSSION PAPER。政策笔记、讲演录和STI Horizon短文暂不进入正式研究层。", "",
        "## 归因与多语种边界", "", "NR、PS和RM按机构正式研究处理；DP按作者讨论论文处理。保留日文题名和日文全文。仓储域无法直接下载的材料优先保存官方HTML版报告或官方PDF代理全文；仅取得官方发布页摘要的条目继续标记全文待补，不据此提炼报告核心观点。精确引用须回查官方PDF、日文原句和页码。", "",
    ]
    (root / "56_NISTEP日文科技与中国专题增补结果.md").write_text("\n".join(lines), encoding="utf-8")
    cache_manager.cleanup()
    print(f"candidates={len(candidates)} reused={statuses['复用库内既有资产']} pdf={statuses['官方PDF已保存并校验']} linked={statuses['关联既有官方PDF']} proxy={statuses['官方仓储PDF代理全文已保存']} html={statuses['官方HTML版报告已保存']} web={statuses['官方网页全文已保存']} release_summary={statuses['官方发布页摘要已保存']} failed={statuses['获取失败']} catalog={len(merged)}")
    return 1 if statuses["获取失败"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
