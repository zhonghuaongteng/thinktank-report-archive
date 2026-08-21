from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_lib
import io
import re
import xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import request
from extract_viewpoint_pdf_slices import process_pdf
from extend_viewpoint_merics_technology import (
    CATALOG_FIELDS,
    asset_details,
    build_theme_rows,
    normalize_text_content,
    read_csv,
    write_csv,
)


SITEMAP_URL = "https://www.bruegel.org/sitemap.xml"
SITE_ROOT = "https://www.bruegel.org/"
CUTOFF = "2016-01-01"
END_DATE = "2026-08-22"
CATALOG_PREFIX = "C-BRUEGEL-"
PUBLICATION_TYPES = {
    "analysis", "blueprint", "policy-brief", "policy-contribution", "report", "working-paper",
}
DISCOVERY_RE = re.compile(
    r"artificial-intelligence|(?:^|-)ai(?:-|$)|technolog|innovat|digital|semiconductor|microchip|chip-|"
    r"quantum|cyber|data-|cloud|comput|automation|robot|biotech|bioeconom|clean-tech|cleantech|"
    r"green-tech|critical-mineral|rare-earth|industrial-polic|industrial-strateg|economic-security|"
    r"supply-chain|research-and-development|productivity|china|chinese|geoeconomic|export-control|"
    r"de-risk|strategic-autonomy|electric-vehicle|solar-panel|battery-alliance|defence-industrial",
    re.I,
)
CORE_TECH_RE = re.compile(
    r"artificial intelligence|\bAI\b|generative AI|semiconductor|microchip|\bchips?\b|critical technolog|"
    r"frontier innovat|technological|technology (?:adoption|deployment|diffusion|competition|support)|"
    r"science and technology|research and innovation|innovation (?:competition|policy|push|deficit)|"
    r"digitalisation|digital economy|cyber|cloud computing|industrial robots?|automation|biometric|"
    r"data (?:act|market|space|sharing)|clean.?tech|low.carbon technolog|green technolog|"
    r"patent speciali[sz]ation|industrial internet|compute gap|military innovation|defence innovation",
    re.I,
)
BASELINE_RE = re.compile(
    r"industrial policy|industrial strategy|economic security|supply chains?|export controls?|de.risk|"
    r"strategic autonomy|critical minerals?|rare earth|battery alliance|solar panels?|electric vehicles?|"
    r"green industrial policy|clean.energy overcapacity|knowledge spillovers|industrial competitiveness|"
    r"public procurement|defence industrial|rearmament|fifth freedom",
    re.I,
)
EXCLUDED_RE = re.compile(
    r"central bank digital currenc|digital euro|decentralised finance|monetary|renminbi|bank credit|"
    r"financial regul|digital markets act|digital competition law|digital competition regulation|"
    r"digital single market|e-commerce|postal sector|welfare states|antitrust|google.android|"
    r"online search|copyright protection|copyright bind|digital enforcement authority|"
    r"digital deregulation|digital services competitive|digital omnibus",
    re.I,
)
THEME_PATTERNS = {
    "人工智能、算力与数字技术": re.compile(r"artificial intelligence|\bAI\b|cloud computing|compute gap|digitalisation|digital economy", re.I),
    "芯片、关键技术与科研创新": re.compile(r"semiconductor|microchip|\bchips?\b|critical technolog|science and technology|research and innovation|innovation|patent", re.I),
    "机器人、自动化与技术就业": re.compile(r"robot|automation|workforce|jobs?|skills|labour", re.I),
    "清洁技术、能源与绿色产业": re.compile(r"clean.?tech|low.carbon technolog|green technolog|solar|battery|electric vehicle|decarbon", re.I),
    "工业政策、产业能力与竞争力": re.compile(r"industrial policy|industrial strategy|industrial competitiveness|public procurement|defence industrial|rearmament", re.I),
    "供应链、技术管制与经济安全": re.compile(r"supply chain|export control|economic security|de.risk|strategic autonomy|critical mineral|rare earth|geopolitical", re.I),
    "中国科技能力与中欧竞争合作": re.compile(r"China|Chinese|US-China|EU-China", re.I),
}


@dataclass(frozen=True)
class Candidate:
    landing_url: str
    published: str
    title: str
    authors: str
    description: str
    report_type: str
    page_html: str
    page_text: str
    pdf_urls: tuple[str, ...]


def canonical_url(url: str) -> str:
    parts = urlsplit(urljoin(SITE_ROOT, html_lib.unescape(url)))
    path = re.sub(r"/+", "/", parts.path).rstrip("/")
    return urlunsplit(("https", "www.bruegel.org", path, "", ""))


def stable_report_id(url: str) -> str:
    digest = hashlib.sha1(canonical_url(url).encode("utf-8")).hexdigest()[:10].upper()
    return f"{CATALOG_PREFIX}{digest}"


def safe_url(url: str) -> str:
    parts = urlsplit(html_lib.unescape(url))
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), parts.query, ""))


def _xml_locations(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    return [node.text.strip() for node in root.iter() if node.tag.endswith("loc") and node.text]


def parse_sitemap_index(xml_text: str) -> list[str]:
    return sorted(dict.fromkeys(url for url in _xml_locations(xml_text) if "sitemap.xml?page=" in url))


def parse_sitemap_publication_urls(xml_text: str) -> list[str]:
    urls = []
    for url in _xml_locations(xml_text):
        parts = urlsplit(url)
        segments = [part for part in parts.path.split("/") if part]
        if len(segments) == 2 and segments[0] in PUBLICATION_TYPES:
            urls.append(canonical_url(url))
    return sorted(dict.fromkeys(urls))


def extract_official_pdf_urls(html_text: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html_text, "html.parser")
    main = soup.find("main") or soup
    urls = []
    for link in main.select('a[href*=".pdf"], a[href*=".PDF"]'):
        label = link.get_text(" ", strip=True).lower()
        url = urljoin(page_url, html_lib.unescape(link.get("href", "")))
        parts = urlsplit(url)
        if parts.hostname not in {"bruegel.org", "www.bruegel.org"}:
            continue
        if not ("/sites/default/files/" in parts.path or "/system/files/wp_attachments/" in parts.path):
            continue
        if "footnote" in " ".join(link.get("class", [])) or "citation" in label:
            continue
        urls.append(urlunsplit(("https", "www.bruegel.org", parts.path, parts.query, "")))
    return list(dict.fromkeys(urls))


def parse_report_page(html_text: str, page_url: str) -> Candidate:
    soup = BeautifulSoup(html_text, "html.parser")
    main = soup.find("main") or soup
    heading = main.find("h1") or soup.find("h1")
    meta_title = soup.select_one('meta[property="og:title"]')
    title = heading.get_text(" ", strip=True) if heading else str(meta_title.get("content", "") if meta_title else "")
    published = ""
    for row in main.select(".c-single-header__meta-row"):
        label = row.select_one(".c-single-header__meta-label")
        value = row.select_one(".c-single-header__meta-term")
        if label and value and "publishing date" in label.get_text(" ", strip=True).lower():
            try:
                published = datetime.strptime(value.get_text(" ", strip=True), "%d %B %Y").date().isoformat()
            except ValueError:
                pass
    description_element = soup.find("meta", attrs={"name": "description"})
    description = html_lib.unescape(str(description_element.get("content", ""))).strip() if description_element else ""
    author_links = main.select('a[href^="/people/"], a[href*="bruegel.org/people/"]')
    authors = "；".join(dict.fromkeys(a.get_text(" ", strip=True) for a in author_links if a.get_text(" ", strip=True)))
    segments = [part for part in urlsplit(page_url).path.split("/") if part]
    report_type = segments[0] if segments else ""
    return Candidate(
        landing_url=canonical_url(page_url), published=published, title=html_lib.unescape(title).strip(),
        authors=authors, description=description, report_type=report_type,
        page_html=html_text, page_text=normalize_text_content(main.get_text("\n", strip=True)),
        pdf_urls=tuple(extract_official_pdf_urls(html_text, page_url)),
    )


def in_scope_title(title: str) -> bool:
    if not title or EXCLUDED_RE.search(title):
        return False
    return bool(CORE_TECH_RE.search(title) or BASELINE_RE.search(title))


def classify_technology_scope(title: str) -> str:
    return "核心科技直接材料" if CORE_TECH_RE.search(title) else "科技产业与经济安全基线"


def classify_themes(candidate: Candidate) -> str:
    text = f"{candidate.title} {candidate.description}"
    themes = [label for label, pattern in THEME_PATTERNS.items() if pattern.search(text)]
    return "；".join(themes or ["欧洲科技产业与经济安全政策"])


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def fetch_candidate(url: str) -> Candidate:
    data, final_url, content_type = request(url, timeout=60)
    if "html" not in content_type.lower() and not data.lstrip().lower().startswith(b"<!doctype"):
        raise RuntimeError(f"unexpected page content type: {content_type}")
    return parse_report_page(data.decode("utf-8", errors="replace"), final_url)


def load_candidates() -> list[Candidate]:
    index_data, _, _ = request(SITEMAP_URL, timeout=60)
    child_urls = parse_sitemap_index(index_data.decode("utf-8", errors="replace"))
    publication_urls = []
    for sitemap_url in child_urls:
        data, _, _ = request(sitemap_url, timeout=60)
        publication_urls.extend(parse_sitemap_publication_urls(data.decode("utf-8", errors="replace")))
    seeded = [url for url in sorted(set(publication_urls)) if DISCOVERY_RE.search(urlsplit(url).path)]
    candidates, errors = [], []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(fetch_candidate, url): url for url in seeded}
        for future in as_completed(futures):
            try:
                candidate = future.result()
                if CUTOFF <= candidate.published <= END_DATE and in_scope_title(candidate.title):
                    candidates.append(candidate)
            except Exception as exc:
                errors.append(f"{futures[future]}: {exc}")
    if errors:
        raise RuntimeError(f"Bruegel discovery failed for {len(errors)} pages; first={errors[0]}")
    return sorted(candidates, key=lambda item: (item.published, item.landing_url))


def choose_pdf(candidate: Candidate) -> tuple[bytes, str, int]:
    best: tuple[bytes, str, int] = (b"", "", 0)
    for url in candidate.pdf_urls:
        try:
            data, final_url, _ = request(safe_url(url), referer=candidate.landing_url, timeout=90)
            if data[:4] != b"%PDF":
                continue
            pages = len(PdfReader(io.BytesIO(data)).pages)
            if pages > best[2] or (pages == best[2] and len(data) > len(best[0])):
                best = data, final_url, pages
        except Exception:
            continue
    return best


def status_for_existing_catalog_row(row: dict[str, str], asset: Path) -> str:
    if not row.get("报告ID", "").startswith(CATALOG_PREFIX):
        return "复用库内既有资产"
    if asset.suffix.lower() != ".pdf":
        return "官方网页全文已保存"
    return "官方PDF已保存并校验" if asset.stem == row.get("报告ID") else "关联既有官方PDF"


def catalog_asset_path(row: dict[str, str]) -> Path:
    return Path(row.get("本地原始资产路径") or row.get("本地路径") or "")


def bruegel_asset_details(row: dict[str, str], directories: dict[str, Path]):
    normalized = dict(row)
    normalized["本地原始资产路径"] = str(catalog_asset_path(row))
    return asset_details(normalized, directories)


def prefer_legacy_catalog_row(
    current: dict[str, str], asset_hash: str, legacy_by_hash: dict[str, dict[str, str]],
) -> dict[str, str]:
    return legacy_by_hash.get(asset_hash, current)


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
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates()
    catalog = read_csv(root / "05_报告总目录.csv")
    existing_by_url = {
        canonical_url(row["原文链接"]): row for row in catalog
        if row.get("机构ID") == "bruegel" or row.get("报告ID", "").startswith(CATALOG_PREFIX)
    }
    existing_hashes = {}
    for pdf_path in directories["pdf"].glob("*.pdf"):
        existing_hashes.setdefault(hashlib.sha256(pdf_path.read_bytes()).hexdigest(), pdf_path)
    legacy_bruegel_by_hash = {}
    for row in catalog:
        if row.get("机构ID") != "bruegel" or row.get("报告ID", "").startswith(CATALOG_PREFIX):
            continue
        asset = catalog_asset_path(row)
        if asset.exists() and asset.suffix.lower() == ".pdf":
            legacy_bruegel_by_hash.setdefault(hashlib.sha256(asset.read_bytes()).hexdigest(), row)
    ledger_rows, prefixed_catalog = [], []
    failed = 0
    for index, candidate in enumerate(candidates, 1):
        existing = existing_by_url.get(canonical_url(candidate.landing_url))
        report_id = existing["报告ID"] if existing else stable_report_id(candidate.landing_url)
        local_asset = local_text = local_slice = digest = pdf_url = error = ""
        pages = chars = byte_count = 0
        status = ""
        if existing:
            try:
                local_asset, local_text, local_slice, pages, chars, digest, byte_count = bruegel_asset_details(existing, directories)
                existing = prefer_legacy_catalog_row(existing, digest, legacy_bruegel_by_hash)
                report_id = existing["报告ID"]
                if Path(local_asset) != catalog_asset_path(existing):
                    local_asset, local_text, local_slice, pages, chars, digest, byte_count = bruegel_asset_details(existing, directories)
                status = status_for_existing_catalog_row(existing, Path(local_asset))
            except Exception as exc:
                error = str(exc)
        if not local_asset:
            data, pdf_url, pages = choose_pdf(candidate)
            try:
                if data:
                    digest = hashlib.sha256(data).hexdigest()
                    if not existing and digest in legacy_bruegel_by_hash:
                        existing = legacy_bruegel_by_hash[digest]
                        report_id = existing["报告ID"]
                    duplicate = existing_hashes.get(digest)
                    if duplicate:
                        pdf_path = duplicate
                        status = "复用库内既有资产" if existing and not report_id.startswith(CATALOG_PREFIX) else "关联既有官方PDF"
                    else:
                        pdf_path = directories["pdf"] / f"{report_id}.pdf"
                        pdf_path.write_bytes(data)
                        existing_hashes[digest] = pdf_path
                        status = "官方PDF已保存并校验"
                    text_path = directories["text"] / f"{pdf_path.stem}.txt"
                    slice_path = directories["slice"] / f"{pdf_path.stem}.md"
                    if not text_path.exists() or not slice_path.exists():
                        process_pdf(pdf_path, directories["text"], directories["slice"])
                    chars = len(text_path.read_text(encoding="utf-8"))
                    byte_count = len(data)
                    local_asset, local_text, local_slice = map(str, (pdf_path, text_path, slice_path))
                elif candidate.page_text:
                    snapshot = directories["html"] / f"{report_id}.html"
                    text_path = directories["web_text"] / f"{report_id}.txt"
                    transcript = directories["transcript"] / f"{report_id}.md"
                    snapshot.write_text(candidate.page_html, encoding="utf-8")
                    text_path.write_text(candidate.page_text, encoding="utf-8")
                    transcript.write_text(normalize_text_content(
                        f"# {candidate.title}\n\n- 发布机构：Bruegel\n- 发布日期：{candidate.published}\n"
                        f"- 官方页面：{candidate.landing_url}\n- 材料类型：{candidate.report_type}\n\n{candidate.page_text}"
                    ), encoding="utf-8")
                    digest = hashlib.sha256(candidate.page_text.encode("utf-8")).hexdigest()
                    byte_count = len(candidate.page_html.encode("utf-8")); chars = len(candidate.page_text)
                    local_asset, local_text, local_slice = map(str, (text_path, text_path, transcript))
                    status = "官方网页全文已保存"
            except Exception as exc:
                error = str(exc)
        if not local_asset:
            status = "获取失败"; failed += 1
        layer = classify_technology_scope(candidate.title)
        themes = classify_themes(candidate)
        role = "作者/项目正式研究"
        catalog_row = existing or {
            "报告ID": report_id, "机构ID": "bruegel", "机构英文名": "Bruegel", "国家或地区": "欧盟",
            "发布日期": candidate.published, "观察窗": observation_window(candidate.published), "报告名称": candidate.title,
            "报告类型": candidate.report_type, "原文链接": candidate.landing_url, "本地路径": "",
            "正文完整度": "本地原文已保存" if local_asset else "获取失败",
            "优先级": "P0-China-tech-corpus" if "中国科技能力" in themes else ("P0-core-tech" if layer == "核心科技直接材料" else "P1-tech-geoeconomic-baseline"),
            "示踪问题": themes, "机构观点等级": role, "样本角色": f"Bruegel科技与中国专题库/{layer}",
            "编码状态": "待编码", "预期用途": "欧洲科技创新、产业政策、关键技术、中欧竞争合作及经济安全专题复用",
            "本地原始资产路径": local_asset, "原始资产状态": status,
        }
        if report_id.startswith(CATALOG_PREFIX):
            if existing:
                catalog_row = dict(existing); catalog_row["本地原始资产路径"] = local_asset; catalog_row["原始资产状态"] = status
            prefixed_catalog.append(catalog_row)
        ledger_rows.append({
            "报告ID": report_id, "发布日期": candidate.published, "观察窗": observation_window(candidate.published),
            "报告名称": candidate.title, "作者": candidate.authors, "报告类型": candidate.report_type,
            "资料角色": role, "科技关联层级": layer, "主题标签": themes,
            "筛选依据": "Bruegel官方sitemap正式出版物；标题命中核心科技或科技产业与经济安全词族",
            "官方落地页": candidate.landing_url, "官方PDF": pdf_url or (candidate.pdf_urls[0] if candidate.pdf_urls else ""),
            "本地原始资产": local_asset, "本地文本": local_text, "本地切片或转写": local_slice,
            "字节数": str(byte_count), "SHA256": digest, "PDF页数": str(pages), "提取文本字符数": str(chars),
            "本地状态": status, "错误": error, "获取日期": date.today().isoformat(),
        })
        print(f"processed={index}/{len(candidates)} id={report_id} status={status}", flush=True)
    catalog_without_refresh = [row for row in catalog if not row.get("报告ID", "").startswith(CATALOG_PREFIX)]
    merged_catalog = catalog_without_refresh + prefixed_catalog
    merged_catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(root / "05_报告总目录.csv", merged_catalog, CATALOG_FIELDS)
    ledger_fields = ["报告ID", "发布日期", "观察窗", "报告名称", "作者", "报告类型", "资料角色", "科技关联层级", "主题标签", "筛选依据", "官方落地页", "官方PDF", "本地原始资产", "本地文本", "本地切片或转写", "字节数", "SHA256", "PDF页数", "提取文本字符数", "本地状态", "错误", "获取日期"]
    write_csv(root / "47_Bruegel科技与中国专题增补台账.csv", ledger_rows, ledger_fields)
    theme_rows = build_theme_rows(ledger_rows)
    theme_fields = ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"]
    write_csv(root / "49_Bruegel科技与中国主题索引.csv", theme_rows, theme_fields)
    counts = Counter((row["主题标签"], row["科技关联层级"], row["观察窗"], row["本地状态"]) for row in theme_rows)
    matrix_rows = [{"主题标签": key[0], "科技关联层级": key[1], "观察窗": key[2], "本地状态": key[3], "材料数": str(value)} for key, value in sorted(counts.items())]
    write_csv(root / "50_Bruegel科技与中国复用矩阵.csv", matrix_rows, ["主题标签", "科技关联层级", "观察窗", "本地状态", "材料数"])
    status_counts = Counter(row["本地状态"] for row in ledger_rows)
    layer_counts = Counter(row["科技关联层级"] for row in ledger_rows)
    report = [
        "# Bruegel近十年科技与中国专题库增补结果", "", f"- 纳入正式出版物：{len(ledger_rows)}项。",
        f"- 核心科技直接材料：{layer_counts['核心科技直接材料']}项；科技产业与经济安全基线：{layer_counts['科技产业与经济安全基线']}项。",
        f"- 复用库内既有资产：{status_counts['复用库内既有资产']}项；新增或关联官方PDF：{status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']}项；新增官方网页全文：{status_counts['官方网页全文已保存']}项；获取失败：{status_counts['获取失败']}项。",
        f"- PDF材料页次：{sum(int(row['PDF页数']) for row in ledger_rows):,}。", f"- 报告总目录：{len(catalog)}项扩展至{len(merged_catalog)}项。", "",
        "## 纳入边界", "", "以Bruegel官方sitemap中的policy brief、working paper、report、analysis、policy contribution和blueprint为入口，限定2016年1月1日至2026年8月22日。保留核心科技、科研创新、清洁技术、产业政策、供应链及经济安全材料；排除数字货币、一般金融监管、纯数字市场竞争执法和邮政等词面误命中。", "",
        "## 资料角色边界", "", "Bruegel明确以作者署名研究为主要生产方式，所有材料保持作者或项目归因，不自动上升为机构统一立场。经济安全与产业政策材料进入基线层，只有明确出现技术、创新或关键产业机制时才可作为科技战略证据。", "",
        "## 跨项目调用", "", "优先从`49_Bruegel科技与中国主题索引.csv`按主题、观察窗和科技关联层级筛选，再回到本地全文。`50_Bruegel科技与中国复用矩阵.csv`用于检查中欧技术竞争、创新政策和经济安全议题的跨期分布。", "",
    ]
    (root / "48_Bruegel科技与中国专题增补结果.md").write_text("\n".join(report), encoding="utf-8")
    print(f"candidates={len(candidates)} reused={status_counts['复用库内既有资产']} pdf={status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']} web={status_counts['官方网页全文已保存']} failed={status_counts['获取失败']} catalog={len(merged_catalog)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
