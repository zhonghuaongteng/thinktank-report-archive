from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import request
from extract_viewpoint_pdf_slices import process_pdf
from extend_viewpoint_bruegel_technology import bruegel_asset_details
from extend_viewpoint_merics_technology import CATALOG_FIELDS, build_theme_rows, read_csv, write_csv


BASE_URL = "https://www.kistep.re.kr"
LIST_PATH = "/reportAllList.es?mid=a10305010000"


@dataclass(frozen=True)
class Entry:
    record_id: str
    category_code: str
    report_type: str
    title_ko: str
    author: str
    published: str
    keywords: str
    download_path: str


@dataclass
class Acquisition:
    entry: Entry
    cache_path: str = ""
    pages: int = 0
    status: str = ""
    error: str = ""


CHINA_RE = re.compile(r"중국|대중국|대중\b|한중|미중|중미|China", re.I)
CORE_TECH_RE = re.compile(
    r"인공지능|\bAI\b|반도체|양자|바이오|합성생물|로봇|데이터|디지털|사이버|우주|위성|"
    r"배터리|이차전지|수소|핵융합|원자력|기술주권|전략기술|첨단기술|신흥기술|기술패권|공급망|"
    r"초전도|드론|자율주행|모빌리티|6G|5G|클라우드|블록체인|첨단소재",
    re.I,
)
GLOBAL_RE = re.compile(r"글로벌|국제|해외|미국|일본|유럽|EU|경제안보|수출통제|협력|경쟁", re.I)

THEME_PATTERNS = {
    "中国科技与国际比较": CHINA_RE,
    "人工智能、数据与数字技术": re.compile(r"인공지능|\bAI\b|데이터|디지털|소프트웨어|클라우드|사이버|6G|5G|블록체인", re.I),
    "半导体、量子与战略技术": re.compile(r"반도체|양자|전략기술|첨단기술|신흥기술|기술주권|기술패권|첨단소재", re.I),
    "生命科学、生物技术与健康": re.compile(r"바이오|생명과학|합성생물|헬스|의료|백신|유전체", re.I),
    "能源、气候与绿色转型": re.compile(r"에너지|기후|탄소|수소|배터리|이차전지|원자력|핵융합|재생에너지", re.I),
    "科研体系、研发投入与评价": re.compile(r"연구개발|\bR&D\b|과학기술정책|연구비|투자|평가|성과|예비타당성", re.I),
    "科技人才、大学与知识流动": re.compile(r"인재|연구자|대학|박사|인력|두뇌|지식|STEM", re.I),
    "产业创新、创业与区域体系": re.compile(r"혁신|창업|기업|산업|지역|클러스터|사업화|기술이전", re.I),
    "技术安全、供应链与国际合作": re.compile(r"안보|공급망|국제협력|경제안보|수출통제|제재|외교|기술패권", re.I),
    "科技前瞻与未来社会": re.compile(r"미래|예측|전망|시나리오|포사이트|foresight|기술영향평가", re.I),
    "航天、核能与大型技术系统": re.compile(r"우주|위성|항공|원자력|핵융합|SMR|대형연구시설", re.I),
}


def catalog_url(page: int) -> str:
    return f"{BASE_URL}{LIST_PATH}&nPage={page}"


def stable_report_id(record_id: str) -> str:
    return f"C-KISTEP-{record_id}"


def landing_url(entry: Entry) -> str:
    return f"{BASE_URL}/reportAllDetail.es?mid=a10305010000&rpt_no={entry.record_id}&rpt_tp={entry.category_code}"


def download_url(entry: Entry) -> str:
    return urljoin(BASE_URL, entry.download_path) if entry.download_path else ""


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def parse_catalog_page(html: bytes) -> tuple[list[Entry], int, int]:
    soup = BeautifulSoup(html.decode("utf-8", errors="replace"), "html.parser")
    page_text = soup.select_one("p.page")
    total = pages = 0
    if page_text:
        text = page_text.get_text(" ", strip=True)
        total_match = re.search(r"전체\s*([0-9,]+)건", text)
        pages_match = re.search(r"/\s*([0-9,]+)", text)
        total = int(total_match.group(1).replace(",", "")) if total_match else 0
        pages = int(pages_match.group(1).replace(",", "")) if pages_match else 0
    entries: list[Entry] = []
    for item in soup.select("div.board_list li"):
        title_anchor = item.select_one("strong.title a[href*='rpt_no=']")
        if not title_anchor:
            continue
        href = title_anchor.get("href", "")
        record_match = re.search(r"rpt_no=([^&]+)", href)
        onclick = title_anchor.get("onclick", "")
        category_match = re.search(r"goViewAll\('([^']+)'", onclick)
        date_node = item.select_one("span.date")
        if not record_match or not date_node:
            continue
        download_anchor = next(
            (
                anchor for anchor in item.select("a.btn_type[href*='reportDownload']")
                if "다운로드" in anchor.get_text(" ", strip=True)
            ),
            None,
        )
        script_text = " ".join(script.get_text(" ", strip=True) for script in item.select("script"))
        keyword_match = re.search(r"fncKeywordSplit\('([^']*)'", script_text)
        category_node = item.select_one("em.spanCategory")
        author_node = item.select_one("span.name")
        entries.append(
            Entry(
                record_id=record_match.group(1),
                category_code=category_match.group(1) if category_match else "",
                report_type=category_node.get_text(" ", strip=True) if category_node else "기타연구자료",
                title_ko=title_anchor.get_text(" ", strip=True),
                author=author_node.get_text(" ", strip=True) if author_node else "",
                published=date_node.get_text(" ", strip=True),
                keywords=keyword_match.group(1) if keyword_match else "",
                download_path=download_anchor.get("href", "").replace("&amp;", "&") if download_anchor else "",
            )
        )
    return entries, total, pages


def classify_technology_scope(title: str, keywords: str) -> str:
    return "核心科技直接材料" if CORE_TECH_RE.search(f"{title} {keywords}") else "科技创新政策与能力基线"


def classify_themes(title: str, keywords: str, evidence_text: str = "") -> str:
    text = f"{title} {keywords} {evidence_text[:12000]}"
    themes = [label for label, pattern in THEME_PATTERNS.items() if pattern.search(text)]
    return "；".join(themes or ["科技创新政策与研究体系"])


def download_priority(title: str, keywords: str) -> str:
    text = f"{title} {keywords}"
    if CHINA_RE.search(text):
        return "P0-China-tech"
    if CORE_TECH_RE.search(text):
        return "P0-core-tech"
    if GLOBAL_RE.search(text):
        return "P1-global-STI"
    return "P2-STI-baseline"


def priority_rank(priority: str) -> int:
    return {
        "P0-China-tech": 0,
        "P0-core-tech": 1,
        "P1-global-STI": 2,
        "P2-STI-baseline": 3,
    }.get(priority, 9)


def should_download(entry: Entry, include_p1: bool = False) -> bool:
    if not entry.download_path:
        return False
    priority = download_priority(entry.title_ko, entry.keywords)
    return priority.startswith("P0") or (include_p1 and priority.startswith("P1"))


def collect_catalog_from_cache(cache_dir: Path) -> list[Entry]:
    unique: dict[str, Entry] = {}
    files = sorted(cache_dir.glob("page-*.html"))
    if not files:
        raise ValueError(f"no KISTEP catalog pages in {cache_dir}")
    expected_total = expected_pages = 0
    for path in files:
        entries, total, pages = parse_catalog_page(path.read_bytes())
        expected_total = max(expected_total, total)
        expected_pages = max(expected_pages, pages)
        for entry in entries:
            unique.setdefault(entry.record_id, entry)
    if expected_pages and len(files) != expected_pages:
        raise ValueError(f"KISTEP page cache incomplete: {len(files)}/{expected_pages}")
    if expected_total and len(unique) != expected_total:
        raise ValueError(f"KISTEP catalog incomplete: {len(unique)}/{expected_total}")
    return sorted(unique.values(), key=lambda entry: (entry.published, entry.record_id))


def fetch_official_pdf(entry: Entry) -> tuple[bytes, int]:
    data, _final_url, _content_type = request(
        download_url(entry), referer=landing_url(entry), timeout=240
    )
    if not data.startswith(b"%PDF"):
        raise ValueError("KISTEP attachment is not a PDF")
    try:
        pages = len(PdfReader(BytesIO(data)).pages)
    except Exception as exc:
        raise ValueError(f"KISTEP PDF is not parseable: {exc}") from exc
    if pages < 1:
        raise ValueError("KISTEP PDF has no pages")
    return data, pages


def acquire(entry: Entry, cache_dir: Path) -> Acquisition:
    result = Acquisition(entry=entry)
    try:
        cache_path = cache_dir / f"{stable_report_id(entry.record_id)}.pdf"
        if cache_path.exists():
            data = cache_path.read_bytes()
            pages = len(PdfReader(BytesIO(data)).pages)
        else:
            data, pages = fetch_official_pdf(entry)
            cache_path.write_bytes(data)
        result.cache_path = str(cache_path)
        result.pages = pages
        result.status = "官方PDF已保存并校验"
    except Exception as exc:
        result.status = "附件非PDF或获取失败"
        result.error = f"{type(exc).__name__}: {exc}"
    return result


LEDGER_FIELDS = [
    "报告ID", "官方记录ID", "官方分类代码", "韩文报告类型", "发布日期", "观察窗", "韩文题名",
    "作者", "官方关键词", "语言", "资料角色", "科技关联层级", "主题标签", "下载优先级",
    "官方落地页", "官方附件", "本地原始资产", "本地文本", "本地切片", "字节数", "SHA256",
    "PDF页数", "提取文本字符数", "文本质量", "本地状态", "错误", "获取日期",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--catalog-cache", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--max-assets", type=int, default=0)
    parser.add_argument("--include-p1", action="store_true")
    args = parser.parse_args()

    root = args.research.resolve()
    directories = {
        "pdf": root / "03_证据底稿" / "原文PDF",
        "text": root / "03_证据底稿" / "文本",
        "slice": root / "03_证据底稿" / "切片",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)

    entries = collect_catalog_from_cache(args.catalog_cache.resolve())
    candidates = [entry for entry in entries if should_download(entry, args.include_p1)]
    candidates.sort(
        key=lambda entry: (
            priority_rank(download_priority(entry.title_ko, entry.keywords)),
            -int(entry.published.replace("-", "")),
            entry.record_id,
        )
    )
    if args.max_assets == 0:
        candidates = []
    elif args.max_assets > 0:
        candidates = candidates[: args.max_assets]
    existing = {path.stem: path for path in directories["pdf"].glob("C-KISTEP-*.pdf")}
    targets = [entry for entry in candidates if stable_report_id(entry.record_id) not in existing]
    cache_dir = root / "03_证据底稿" / ".kistep_download_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    acquisitions: dict[str, Acquisition] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(acquire, entry, cache_dir): entry for entry in targets}
        for completed, future in enumerate(as_completed(futures), start=1):
            entry = futures[future]
            report_id = stable_report_id(entry.record_id)
            acquisitions[report_id] = future.result()
            print(f"acquired={completed}/{len(targets)} id={report_id} status={acquisitions[report_id].status}", flush=True)

    ledger_rows: list[dict[str, str]] = []
    for index, entry in enumerate(entries, start=1):
        report_id = stable_report_id(entry.record_id)
        local_asset = local_text = local_slice = digest = evidence_text = error = ""
        pages = chars = byte_count = 0
        status = "官方目录元数据，附件未列入本批" if entry.download_path else "官方目录无附件"
        pdf_path = existing.get(report_id)
        result = acquisitions.get(report_id)
        if result and result.cache_path:
            pdf_path = directories["pdf"] / f"{report_id}.pdf"
            data = Path(result.cache_path).read_bytes()
            pdf_path.write_bytes(data)
            Path(result.cache_path).unlink(missing_ok=True)
            pages = result.pages
            status = result.status
        elif result:
            status, error = result.status, result.error
        if pdf_path and pdf_path.exists():
            try:
                text_path = directories["text"] / f"{report_id}.txt"
                slice_path = directories["slice"] / f"{report_id}.md"
                if not text_path.exists() or not slice_path.exists():
                    process_pdf(pdf_path, directories["text"], directories["slice"])
                row = {"本地原始资产路径": str(pdf_path)}
                local_asset, local_text, local_slice, measured_pages, chars, digest, byte_count = bruegel_asset_details(row, directories)
                pages = pages or measured_pages
                evidence_text = Path(local_text).read_text(encoding="utf-8", errors="replace")
                status = "官方PDF已保存并校验"
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                status = "本地衍生处理失败"
        themes = classify_themes(entry.title_ko, entry.keywords, evidence_text)
        text_quality = (
            "官方目录无本地正文" if not local_asset
            else "图像型PDF，OCR待补" if not pages or chars / pages < 200
            else "可检索文本"
        )
        ledger_rows.append({
            "报告ID": report_id,
            "官方记录ID": entry.record_id,
            "官方分类代码": entry.category_code,
            "韩文报告类型": entry.report_type,
            "发布日期": entry.published,
            "观察窗": observation_window(entry.published),
            "韩文题名": entry.title_ko,
            "作者": entry.author,
            "官方关键词": entry.keywords,
            "语言": "韩文",
            "资料角色": "机构正式研究",
            "科技关联层级": classify_technology_scope(entry.title_ko, entry.keywords),
            "主题标签": themes,
            "下载优先级": download_priority(entry.title_ko, entry.keywords),
            "官方落地页": landing_url(entry),
            "官方附件": download_url(entry),
            "本地原始资产": local_asset,
            "本地文本": local_text,
            "本地切片": local_slice,
            "字节数": str(byte_count),
            "SHA256": digest,
            "PDF页数": str(pages),
            "提取文本字符数": str(chars),
            "文本质量": text_quality,
            "本地状态": status,
            "错误": error,
            "获取日期": date.today().isoformat(),
        })
        if index % 100 == 0 or index == len(entries):
            print(f"processed={index}/{len(entries)}", flush=True)

    write_csv(root / "64_KISTEP韩文正式报告总目录与重点附件台账.csv", ledger_rows, LEDGER_FIELDS)
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    new_catalog = []
    for row in ledger_rows:
        text_quality = row["文本质量"]
        new_catalog.append({
            "报告ID": row["报告ID"],
            "机构ID": "kistep",
            "机构英文名": "Korea Institute of S&T Evaluation and Planning",
            "国家或地区": "韩国",
            "发布日期": row["发布日期"],
            "观察窗": row["观察窗"],
            "报告名称": row["韩文题名"],
            "报告类型": f"KISTEP {row['韩文报告类型']}",
            "原文链接": row["官方落地页"],
            "本地路径": "",
            "正文完整度": (
                "官方图像型PDF已保存，OCR待补" if text_quality == "图像型PDF，OCR待补"
                else "本地韩文原文已保存" if row["本地原始资产"]
                else "官方目录元数据，正文待补"
            ),
            "优先级": row["下载优先级"],
            "示踪问题": row["主题标签"],
            "机构观点等级": "机构正式研究",
            "样本角色": f"KISTEP韩文正式研究库/{row['科技关联层级']}",
            "编码状态": "待编码",
            "预期用途": "韩国国家研发战略、核心技术、中国比较、技术水平与科技治理专题复用",
            "本地原始资产路径": row["本地原始资产"],
            "原始资产状态": row["本地状态"],
        })
    merged = [row for row in catalog if not row.get("报告ID", "").startswith("C-KISTEP-")] + new_catalog
    merged.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, merged, CATALOG_FIELDS)
    theme_input = [{**row, "报告名称": row["韩文题名"]} for row in ledger_rows]
    write_csv(
        root / "66_KISTEP韩文科技与中国主题索引.csv",
        build_theme_rows(theme_input),
        ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"],
    )
    matrix_counts = Counter(
        (theme, row["科技关联层级"], row["观察窗"], row["韩文报告类型"], row["下载优先级"], row["本地状态"])
        for row in ledger_rows for theme in row["主题标签"].split("；")
    )
    matrix_rows = [
        {"主题标签": key[0], "科技关联层级": key[1], "观察窗": key[2], "韩文报告类型": key[3], "下载优先级": key[4], "本地状态": key[5], "材料数": str(value)}
        for key, value in sorted(matrix_counts.items())
    ]
    write_csv(
        root / "67_KISTEP韩文科技与中国复用矩阵.csv",
        matrix_rows,
        ["主题标签", "科技关联层级", "观察窗", "韩文报告类型", "下载优先级", "本地状态", "材料数"],
    )
    statuses = Counter(row["本地状态"] for row in ledger_rows)
    categories = Counter(row["韩文报告类型"] for row in ledger_rows)
    priorities = Counter(row["下载优先级"] for row in ledger_rows)
    windows = Counter(row["观察窗"] for row in ledger_rows)
    china_count = sum("中国科技与国际比较" in row["主题标签"] for row in ledger_rows)
    core_count = sum(row["科技关联层级"] == "核心科技直接材料" for row in ledger_rows)
    result_lines = [
        "# KISTEP近十年韩文正式报告总目录与重点附件增补结果", "",
        f"- 官方正式报告总目录：{len(ledger_rows)}项；现有目录最早发布日期：{min(row['发布日期'] for row in ledger_rows)}。",
        f"- W1：{windows['W1']}项；W2：{windows['W2']}项；W3：{windows['W3']}项。",
        f"- 核心科技直接材料：{core_count}项；中国科技与国际比较：{china_count}项。",
        f"- P0中国科技：{priorities['P0-China-tech']}项；P0核心技术：{priorities['P0-core-tech']}项；P1全球科技创新：{priorities['P1-global-STI']}项。",
        f"- 本批官方PDF保存：{statuses['官方PDF已保存并校验']}项；附件非PDF或获取失败：{statuses['附件非PDF或获取失败']}项。", "",
        f"- 报告总目录现为：{len(merged)}项。", "",
        "## 类型分布", "",
    ]
    result_lines.extend(f"- {label}：{count}项。" for label, count in sorted(categories.items()))
    result_lines += [
        "", "## 纳入与使用边界", "",
        "纳入KISTEP官方‘全部研究报告’目录当前可见的全部正式成果。官方目录最早记录为2018年，整体落在近十年观察范围内。重点附件依据韩文题名与官方关键词中的中国、战略技术和核心技术信号选择；未下载附件的记录仍保留官方落地页、附件链接、分类、作者、日期和关键词。机器主题标签仅承担检索入口，观点引用须回查本地PDF、韩文原句与页码。", "",
    ]
    (root / "65_KISTEP韩文正式报告总目录与重点附件结果.md").write_text("\n".join(result_lines), encoding="utf-8")
    print(
        f"entries={len(entries)} candidates={len(candidates)} pdf={statuses['官方PDF已保存并校验']} "
        f"failed={statuses['附件非PDF或获取失败']}",
        flush=True,
    )
    return 1 if statuses["附件非PDF或获取失败"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
