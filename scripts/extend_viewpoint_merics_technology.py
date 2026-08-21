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
from datetime import date
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import request
from extract_viewpoint_pdf_slices import process_pdf


SITEMAP_URL = "https://merics.org/sitemap.xml"
SITE_ROOT = "https://merics.org/"
CUTOFF = "2016-01-01"
END_DATE = "2026-08-22"
CATALOG_PREFIX = "C-MERICS-"
CORE_TECH_RE = re.compile(
    r"technolog|techno-|innovation|digital|cyber|artificial intelligence|\bAI\b|semiconductor|\bchips?\b|"
    r"robot|quantum|biotech|biopharma|research|science-tech|blockchain|internet of things|open-source|"
    r"platform economy|data management|data governance|green hydrogen|electric vehicle|EV battery|"
    r"space internet|outer space|talent|industry 4\.0|made in china 2025|medical technology|"
    r"telecommunication|information control|internet",
    re.I,
)
GEOECON_RE = re.compile(
    r"industrial policy|industrial strategy|supply chain|value chain|export control|economic security|de-risk|"
    r"resilience|decoupling|interdependence|dependency|dependenc|overcapacity|critical mineral|rare earth|"
    r"strategic autonomy|economic coercion|economic vulnerabil|localization dilemma|little giant|"
    r"accelerator state|world.s factory|transportation superpower",
    re.I,
)
EXCLUDED_TITLE_RE = re.compile(
    r"^Executive Summary:|^Programming China$|^Manufacturing creativity and maintaining control$|"
    r"^Olaf Scholz in Beijing \+|^Pelosi in Taiwan,|^Arbeitnehmer streben zurück|^Key graphics:",
    re.I,
)
THEME_PATTERNS = {
    "人工智能、芯片与算力": re.compile(r"artificial intelligence|\bAI\b|semiconductor|\bchips?\b|computing|large language model", re.I),
    "网络安全、数据与数字治理": re.compile(r"cyber|digital|data management|data governance|internet|blockchain|open-source|platform|telecommunication", re.I),
    "先进制造、机器人与交通技术": re.compile(r"industrial|manufactur|robot|automotive|electric vehicle|transportation|industry 4\.0", re.I),
    "生物、量子、航天与绿色技术": re.compile(r"biotech|biopharma|medical technolog|quantum|space|hydrogen|battery|green tech", re.I),
    "创新体系、科研与技术人才": re.compile(r"innovation|research|science-tech|talent|little giant|accelerator state", re.I),
    "供应链、技术管制与经济安全": re.compile(r"supply chain|value chain|export control|economic security|de-risk|resilien|decoupl|interdepend|dependenc|critical mineral|rare earth|overcapacity|strategic autonomy", re.I),
}
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]


@dataclass(frozen=True)
class Candidate:
    landing_url: str
    published: str
    title: str
    authors: str
    description: str
    page_html: str
    page_text: str
    pdf_urls: tuple[str, ...]


def canonical_url(url: str) -> str:
    parts = urlsplit(urljoin(SITE_ROOT, html_lib.unescape(url)))
    path = re.sub(r"/+", "/", parts.path).rstrip("/")
    if path.startswith("/en/report/"):
        path = path[3:]
    return urlunsplit(("https", "merics.org", path, "", ""))


def stable_report_id(url: str) -> str:
    digest = hashlib.sha1(canonical_url(url).encode("utf-8")).hexdigest()[:10].upper()
    return f"{CATALOG_PREFIX}{digest}"


def safe_url(url: str) -> str:
    parts = urlsplit(html_lib.unescape(url))
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), parts.query, ""))


def normalize_text_content(value: str) -> str:
    normalized = re.sub(r"[ \t\r]+(?=\n|$)", "", value)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return re.sub(r"\n+\Z", "\n", normalized).strip() + "\n"


def parse_sitemap_report_urls(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    urls: list[str] = []
    for element in root.iter():
        if element.tag.endswith("loc") and element.text:
            url = element.text.strip()
            path = urlsplit(url).path.rstrip("/")
            marker = "/en/report/"
            if marker in path and "/" not in path.split(marker, 1)[1]:
                urls.append(url)
    return sorted(dict.fromkeys(urls))


def extract_official_pdf_urls(html_text: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html_text, "html.parser")
    scope = soup.find("main") or soup
    links = list(scope.select("a.file-download[href]")) or list(scope.select('a[href$=".pdf"], a[href*=".pdf?"]'))
    urls: list[str] = []
    for link in links:
        url = urljoin(page_url, html_lib.unescape(link.get("href", "")))
        parts = urlsplit(url)
        if parts.hostname in {"merics.org", "www.merics.org"} and "/sites/default/files/" in parts.path and parts.path.lower().endswith(".pdf"):
            urls.append(urlunsplit(("https", "merics.org", parts.path, parts.query, "")))
    return list(dict.fromkeys(urls))


def parse_report_page(html_text: str, page_url: str) -> Candidate:
    soup = BeautifulSoup(html_text, "html.parser")
    main = soup.find("main") or soup
    heading = main.find("h1") or soup.find("h1")
    title = heading.get_text(" ", strip=True) if heading else ""
    time_element = main.select_one(".field-name-field-date-published time[datetime]") or main.find("time", attrs={"datetime": True})
    published = str(time_element.get("datetime", ""))[:10] if time_element else ""
    description_element = soup.find("meta", attrs={"name": "description"})
    description = html_lib.unescape(str(description_element.get("content", ""))).strip() if description_element else ""
    author_links = main.select('[class*="field-name-field-author"] a[href*="/team/"]')
    if not author_links:
        author_links = main.select('a[href*="/team/"]')
    authors = "；".join(dict.fromkeys(link.get_text(" ", strip=True) for link in author_links if link.get_text(" ", strip=True)))
    page_text = normalize_text_content(main.get_text("\n", strip=True))
    return Candidate(
        landing_url=page_url,
        published=published,
        title=html_lib.unescape(title).strip(),
        authors=authors,
        description=description,
        page_html=html_text,
        page_text=page_text,
        pdf_urls=tuple(extract_official_pdf_urls(html_text, page_url)),
    )


def in_scope_title(title: str) -> bool:
    if not title or EXCLUDED_TITLE_RE.search(title):
        return False
    return bool(CORE_TECH_RE.search(title) or GEOECON_RE.search(title))


def classify_technology_scope(title: str) -> str:
    return "核心科技直接材料" if CORE_TECH_RE.search(title) else "科技产业与经济安全基线"


def classify_themes(candidate: Candidate) -> str:
    text = f"{candidate.title} {candidate.description}"
    themes = [label for label, pattern in THEME_PATTERNS.items() if pattern.search(text)]
    return "；".join(themes or ["技术地缘经济与欧洲对华政策"])


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_theme_rows(ledger_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"主题标签": theme, "科技关联层级": row["科技关联层级"], "报告ID": row["报告ID"],
         "发布日期": row["发布日期"], "观察窗": row["观察窗"], "报告名称": row["报告名称"],
         "资料角色": row["资料角色"], "本地原始资产": row["本地原始资产"], "本地文本": row["本地文本"],
         "官方落地页": row["官方落地页"], "本地状态": row["本地状态"]}
        for row in ledger_rows for theme in row["主题标签"].split("；")
    ]


def fetch_candidate(url: str) -> Candidate:
    data, final_url, content_type = request(url, timeout=60)
    if "html" not in content_type.lower() and not data.lstrip().lower().startswith(b"<!doctype"):
        raise RuntimeError(f"unexpected page content type: {content_type}")
    return parse_report_page(data.decode("utf-8", errors="replace"), final_url)


def load_candidates() -> list[Candidate]:
    sitemap_data, _, _ = request(SITEMAP_URL, timeout=60)
    urls = parse_sitemap_report_urls(sitemap_data.decode("utf-8", errors="replace"))
    candidates: list[Candidate] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(fetch_candidate, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                candidate = future.result()
                if CUTOFF <= candidate.published <= END_DATE and in_scope_title(candidate.title):
                    candidates.append(candidate)
            except Exception as exc:
                errors.append(f"{url}: {exc}")
    if errors:
        raise RuntimeError(f"MERICS discovery failed for {len(errors)} report pages; first={errors[0]}")
    return sorted(candidates, key=lambda item: (item.published, canonical_url(item.landing_url)))


def choose_pdf(candidate: Candidate) -> tuple[bytes, str, int]:
    best: tuple[bytes, str, int] = (b"", "", 0)
    for url in candidate.pdf_urls:
        try:
            data, final_url, _ = request(safe_url(url), referer=candidate.landing_url, timeout=90)
            if data[:4] != b"%PDF":
                continue
            pages = len(PdfReader(io.BytesIO(data)).pages)
            if pages > best[2] or (pages == best[2] and len(data) > len(best[0])):
                best = (data, final_url, pages)
        except Exception:
            continue
    return best


def asset_details(row: dict[str, str], directories: dict[str, Path]) -> tuple[str, str, str, int, int, str, int]:
    asset = Path(row.get("本地原始资产路径", ""))
    if not asset.exists():
        raise FileNotFoundError(asset)
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    if asset.suffix.lower() == ".pdf":
        text_path = directories["text"] / f"{asset.stem}.txt"
        slice_path = directories["slice"] / f"{asset.stem}.md"
        pages = len(PdfReader(str(asset)).pages)
        chars = len(text_path.read_text(encoding="utf-8")) if text_path.exists() else 0
        return str(asset), str(text_path), str(slice_path), pages, chars, digest, asset.stat().st_size
    transcript = directories["transcript"] / f"{asset.stem}.md"
    if not transcript.exists():
        transcript = asset
    chars = len(asset.read_text(encoding="utf-8", errors="replace"))
    return str(asset), str(asset), str(transcript), 0, chars, digest, asset.stat().st_size


def status_for_existing_catalog_row(row: dict[str, str], asset: Path) -> str:
    report_id = row.get("报告ID", "")
    if not report_id.startswith(CATALOG_PREFIX):
        return "复用库内既有资产"
    if asset.suffix.lower() != ".pdf":
        return "官方网页全文已保存"
    return "官方PDF已保存并校验" if asset.stem == report_id else "关联既有官方PDF"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
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

    candidates = load_candidates()
    catalog = read_csv(root / "05_报告总目录.csv")
    existing_by_url = {
        canonical_url(row["原文链接"]): row
        for row in catalog
        if row.get("机构ID") in {"merics", "merics-tech"} or row.get("报告ID", "").startswith(CATALOG_PREFIX)
    }
    existing_hashes: dict[str, Path] = {}
    for pdf_path in directories["pdf"].glob("*.pdf"):
        existing_hashes.setdefault(hashlib.sha256(pdf_path.read_bytes()).hexdigest(), pdf_path)

    ledger_rows: list[dict[str, str]] = []
    prefixed_catalog: list[dict[str, str]] = []
    failed = 0
    for index, candidate in enumerate(candidates, 1):
        existing = existing_by_url.get(canonical_url(candidate.landing_url))
        report_id = existing["报告ID"] if existing else stable_report_id(candidate.landing_url)
        local_asset = local_text = local_slice = digest = pdf_url = error = ""
        pages = chars = byte_count = 0
        status = ""
        if existing:
            try:
                local_asset, local_text, local_slice, pages, chars, digest, byte_count = asset_details(existing, directories)
                status = status_for_existing_catalog_row(existing, Path(local_asset))
            except Exception as exc:
                error = str(exc)
        if not local_asset:
            data, pdf_url, pages = choose_pdf(candidate)
            try:
                if data:
                    digest = hashlib.sha256(data).hexdigest()
                    duplicate = existing_hashes.get(digest)
                    if duplicate:
                        pdf_path = duplicate
                        status = "关联既有官方PDF"
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
                    transcript.write_text(
                        normalize_text_content(
                            f"# {candidate.title}\n\n- 发布机构：MERICS\n- 发布日期：{candidate.published}\n"
                            f"- 官方页面：{candidate.landing_url}\n- 材料类型：MERICS研究报告\n\n{candidate.page_text}"
                        ),
                        encoding="utf-8",
                    )
                    digest = hashlib.sha256(candidate.page_text.encode("utf-8")).hexdigest()
                    byte_count = len(candidate.page_html.encode("utf-8"))
                    chars = len(candidate.page_text)
                    local_asset, local_text, local_slice = map(str, (text_path, text_path, transcript))
                    status = "官方网页全文已保存"
            except Exception as exc:
                error = str(exc)
        if not local_asset:
            status = "获取失败"
            failed += 1

        tech_layer = classify_technology_scope(candidate.title)
        themes = classify_themes(candidate)
        role = "作者/项目正式研究"
        catalog_row = existing or {
            "报告ID": report_id, "机构ID": "merics", "机构英文名": "MERICS Industrial Policy and Technology",
            "国家或地区": "德国", "发布日期": candidate.published, "观察窗": observation_window(candidate.published),
            "报告名称": candidate.title, "报告类型": "MERICS研究报告", "原文链接": candidate.landing_url,
            "本地路径": "", "正文完整度": "本地原文已保存" if local_asset else "获取失败",
            "优先级": "P0-China-tech-corpus" if tech_layer == "核心科技直接材料" else "P1-tech-geoeconomic-baseline",
            "示踪问题": themes, "机构观点等级": role,
            "样本角色": f"MERICS科技与中国专题库/{tech_layer}", "编码状态": "待编码",
            "预期用途": "中国科技创新、产业政策、数字治理、供应链与欧洲对华经济安全专题复用",
            "本地原始资产路径": local_asset, "原始资产状态": status,
        }
        if report_id.startswith(CATALOG_PREFIX):
            if existing:
                catalog_row = dict(existing)
                catalog_row["本地原始资产路径"] = local_asset
                catalog_row["原始资产状态"] = status
            prefixed_catalog.append(catalog_row)
        ledger_rows.append({
            "报告ID": report_id, "发布日期": candidate.published, "观察窗": observation_window(candidate.published),
            "报告名称": candidate.title, "作者": candidate.authors, "资料角色": role, "科技关联层级": tech_layer,
            "主题标签": themes, "筛选依据": "MERICS官方sitemap正式报告；标题命中科技或技术地缘经济词族",
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

    ledger_fields = [
        "报告ID", "发布日期", "观察窗", "报告名称", "作者", "资料角色", "科技关联层级", "主题标签", "筛选依据",
        "官方落地页", "官方PDF", "本地原始资产", "本地文本", "本地切片或转写", "字节数", "SHA256",
        "PDF页数", "提取文本字符数", "本地状态", "错误", "获取日期",
    ]
    write_csv(root / "43_MERICS科技与中国专题增补台账.csv", ledger_rows, ledger_fields)
    theme_rows = build_theme_rows(ledger_rows)
    theme_fields = ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"]
    write_csv(root / "45_MERICS科技与中国主题索引.csv", theme_rows, theme_fields)
    counts = Counter((row["主题标签"], row["科技关联层级"], row["观察窗"], row["本地状态"]) for row in theme_rows)
    matrix_rows = [
        {"主题标签": key[0], "科技关联层级": key[1], "观察窗": key[2], "本地状态": key[3], "材料数": str(value)}
        for key, value in sorted(counts.items())
    ]
    write_csv(root / "46_MERICS科技与中国复用矩阵.csv", matrix_rows, ["主题标签", "科技关联层级", "观察窗", "本地状态", "材料数"])

    status_counts = Counter(row["本地状态"] for row in ledger_rows)
    layer_counts = Counter(row["科技关联层级"] for row in ledger_rows)
    lines = [
        "# MERICS近十年科技与中国专题库增补结果", "",
        f"- 纳入正式报告：{len(ledger_rows)}项。",
        f"- 核心科技直接材料：{layer_counts['核心科技直接材料']}项；科技产业与经济安全基线：{layer_counts['科技产业与经济安全基线']}项。",
        f"- 复用库内既有资产：{status_counts['复用库内既有资产']}项；新增或关联官方PDF：{status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']}项；新增官方网页全文：{status_counts['官方网页全文已保存']}项；获取失败：{status_counts['获取失败']}项。",
        f"- PDF材料页次：{sum(int(row['PDF页数']) for row in ledger_rows):,}。",
        f"- 报告总目录：{len(catalog)}项扩展至{len(merged_catalog)}项。", "",
        "## 纳入边界", "",
        "以MERICS官方sitemap中的独立`/en/report/`页面为发现入口，限定2016年1月1日至2026年8月22日。标题须直接命中核心科技、创新体系、先进制造、数字治理、技术供应链或经济安全词族；排除章节碎片、执行摘要重复页和新闻拼盘。", "",
        "## 资料角色边界", "",
        "MERICS报告均按作者或项目正式研究处理，不自动上升为机构统一立场。经济安全、韧性和去风险材料只有在标题呈现明确技术产业关联时进入基线层。", "",
        "## 跨项目调用", "",
        "优先从`45_MERICS科技与中国主题索引.csv`按主题、科技关联层级和观察窗筛选，再回到本地逐页文本或网页转写。`46_MERICS科技与中国复用矩阵.csv`用于识别跨期主题密度和全文形态。", "",
    ]
    (root / "44_MERICS科技与中国专题增补结果.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        f"candidates={len(candidates)} reused={status_counts['复用库内既有资产']} "
        f"pdf={status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']} "
        f"web={status_counts['官方网页全文已保存']} failed={status_counts['获取失败']} catalog={len(merged_catalog)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
