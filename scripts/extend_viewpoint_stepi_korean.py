from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from io import BytesIO
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup
from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import request
from extract_viewpoint_pdf_slices import process_pdf
from extend_viewpoint_bruegel_technology import bruegel_asset_details, catalog_asset_path
from extend_viewpoint_merics_technology import (
    CATALOG_FIELDS,
    build_theme_rows,
    read_csv,
    write_csv,
)


BASE_URL = "https://www.stepi.re.kr"
FORMAL_CATEGORIES = {
    "A0201": "정책연구",
    "A0203": "조사연구",
    "A0202": "정책자료",
    "A0204": "기타연구",
}


@dataclass(frozen=True)
class Entry:
    record_id: str
    category_code: str
    report_type: str
    title_ko: str
    author: str
    published: str
    pdf_filename: str


@dataclass
class Acquisition:
    entry: Entry
    cache_path: str = ""
    pages: int = 0
    status: str = ""
    error: str = ""


CORE_TECH_RE = re.compile(
    r"인공지능|\bAI\b|반도체|양자|바이오|합성생물|로봇|데이터|디지털|사이버|우주|위성|"
    r"배터리|이차전지|수소|핵융합|원자력|기술주권|전략기술|첨단기술|신흥기술|기술패권|공급망",
    re.I,
)

THEME_PATTERNS = {
    "中国科技与国际比较": re.compile(r"중국|대중국|한중|미중|중미|China", re.I),
    "人工智能、数据与数字技术": re.compile(r"인공지능|\bAI\b|데이터|디지털|소프트웨어|클라우드|사이버", re.I),
    "半导体、量子与战略技术": re.compile(r"반도체|양자|전략기술|첨단기술|신흥기술|기술주권|기술패권", re.I),
    "生命科学、生物技术与健康": re.compile(r"바이오|생명과학|합성생물|헬스|의료|백신", re.I),
    "能源、气候与绿色转型": re.compile(r"에너지|기후|탄소|수소|배터리|이차전지|원자력|핵융합|재생에너지", re.I),
    "科研体系、研发投入与评价": re.compile(r"연구개발|\bR&D\b|과학기술정책|연구비|투자|평가|성과", re.I),
    "科技人才、大学与知识流动": re.compile(r"인재|연구자|대학|박사|인력|두뇌|지식", re.I),
    "产业创新、创业与区域体系": re.compile(r"혁신|창업|기업|산업|지역|클러스터|사업화", re.I),
    "技术安全、供应链与国际合作": re.compile(r"안보|공급망|국제협력|경제안보|수출통제|제재|외교", re.I),
    "科技前瞻与未来社会": re.compile(r"미래|예측|전망|시나리오|포사이트|foresight", re.I),
}


def parse_catalog_page(html: bytes, category_code: str) -> tuple[list[Entry], int, int]:
    soup = BeautifulSoup(html.decode("utf-8", errors="replace"), "html.parser")
    top = soup.select_one(".boardTop")
    total = pages = 0
    if top:
        text = top.get_text(" ", strip=True)
        total_match = re.search(r"총\s*([0-9,]+)\s*건", text)
        page_match = re.search(r"\d+\s*/\s*(\d+)\s*페이지", text)
        total = int(total_match.group(1).replace(",", "")) if total_match else 0
        pages = int(page_match.group(1)) if page_match else 0
    entries: list[Entry] = []
    for row in soup.select("table.list tr"):
        title_anchor = row.select_one("td.title a[href*='reIdx=']")
        if not title_anchor:
            continue
        record_match = re.search(r"reIdx=(\d+)", title_anchor.get("href", ""))
        cells = row.select("td")
        if not record_match or len(cells) < 4:
            continue
        pdf_anchor = row.select_one("td.file a.btnFile.pdf[data-file]")
        entries.append(
            Entry(
                record_id=record_match.group(1),
                category_code=category_code,
                report_type=FORMAL_CATEGORIES[category_code],
                title_ko=title_anchor.get_text(" ", strip=True),
                author=cells[2].get_text(" ", strip=True),
                published=normalize_published(cells[3].get_text(" ", strip=True)),
                pdf_filename=pdf_anchor.get("data-file", "") if pdf_anchor else "",
            )
        )
    return entries, total, pages


def normalize_published(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"\d{4}", value):
        return value + "-01-01"
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return value + "-01"
    return value


def download_url(entry: Entry) -> str:
    return (
        f"{BASE_URL}/common/report/Download.do?reIdx={entry.record_id}"
        f"&streFileNm={quote(entry.pdf_filename)}&cateCont={entry.category_code}&purpose=&jobGroup="
    )


def landing_url(entry: Entry) -> str:
    return f"{BASE_URL}/site/stepiko/report/View.do?reIdx={entry.record_id}"


def report_role(category_code: str) -> str:
    if category_code not in FORMAL_CATEGORIES:
        raise ValueError(f"unsupported STEPI formal category: {category_code}")
    return "机构正式研究"


def classify_technology_scope(title: str) -> str:
    return "核心科技直接材料" if CORE_TECH_RE.search(title) else "科技创新政策与能力基线"


def classify_themes(title: str, evidence_text: str) -> str:
    text = f"{title} {evidence_text[:12000]}"
    themes = [label for label, pattern in THEME_PATTERNS.items() if pattern.search(text)]
    return "；".join(themes or ["科技创新政策与研究体系"])


def classify_text_quality(chars: int, pages: int, has_asset: bool) -> str:
    if not has_asset:
        return "官方目录无PDF正文"
    if not pages or chars / pages < 200:
        return "图像型PDF，OCR待补"
    return "可检索文本"


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def stable_report_id(category_code: str, record_id: str) -> str:
    return f"C-STEPI-{category_code}-{record_id}"


def catalog_url(year: int, category_code: str, page: int) -> str:
    return (
        f"{BASE_URL}/site/stepiko/report/List.do?cbIdx=1292"
        f"&searchYear={year}&cateCont={category_code}&pageIndex={page}"
    )


def collect_catalog(
    *,
    years=range(2016, 2027),
    categories=FORMAL_CATEGORIES,
    fetcher=None,
) -> list[Entry]:
    loader = fetcher or request
    unique: dict[str, Entry] = {}
    for year in years:
        for category_code in categories:
            first, _final_url, _content_type = loader(
                catalog_url(year, category_code, 1), timeout=60
            )
            entries, _total, pages = parse_catalog_page(first, category_code)
            for entry in entries:
                unique.setdefault(entry.record_id, entry)
            for page in range(2, pages + 1):
                content, _final_url, _content_type = loader(
                    catalog_url(year, category_code, page), timeout=60
                )
                entries, _total, _pages = parse_catalog_page(content, category_code)
                for entry in entries:
                    unique.setdefault(entry.record_id, entry)
    return sorted(unique.values(), key=lambda entry: int(entry.record_id))


def fetch_official_pdf(entry: Entry, fetcher=None) -> tuple[bytes, int]:
    loader = fetcher or request
    data, _final_url, _content_type = loader(
        download_url(entry), referer=catalog_url(int(entry.published[:4]), entry.category_code, 1), timeout=180
    )
    if not data.startswith(b"%PDF"):
        raise ValueError("STEPI download did not return a PDF")
    try:
        pages = len(PdfReader(BytesIO(data)).pages)
    except Exception as exc:
        raise ValueError(f"STEPI PDF is not parseable: {exc}") from exc
    if pages < 1:
        raise ValueError("STEPI PDF has no pages")
    return data, pages


def acquire(entry: Entry, cache_dir: Path) -> Acquisition:
    result = Acquisition(entry=entry)
    if not entry.pdf_filename:
        result.status = "官方目录无PDF"
        return result
    try:
        cache_path = cache_dir / f"{stable_report_id(entry.category_code, entry.record_id)}.pdf"
        if cache_path.exists():
            data = cache_path.read_bytes()
            if not data.startswith(b"%PDF"):
                raise ValueError("persistent STEPI cache is not a PDF")
            pages = len(PdfReader(BytesIO(data)).pages)
            if pages < 1:
                raise ValueError("persistent STEPI cache has no pages")
        else:
            data, pages = fetch_official_pdf(entry)
            cache_path.write_bytes(data)
        result.cache_path = str(cache_path)
        result.pages = pages
        result.status = "官方PDF已保存并校验"
    except Exception as exc:
        result.status = "获取失败"
        result.error = f"{type(exc).__name__}: {exc}"
    return result


def existing_status(row: dict[str, str], asset: Path) -> str:
    if row.get("报告ID", "").startswith("C-STEPI-"):
        return row.get("原始资产状态") or "官方PDF已保存并校验"
    return "关联既有官方PDF"


def discover_local_assets(pdf_dir: Path) -> dict[str, dict[str, str]]:
    return {
        path.stem: {
            "报告ID": path.stem,
            "本地原始资产路径": str(path),
            "原始资产状态": "官方PDF已保存并校验",
        }
        for path in sorted(pdf_dir.glob("C-STEPI-*.pdf"))
        if path.is_file() and path.stat().st_size > 0
    }


def ensure_pdf_derivatives(pdf_path: Path, directories: dict[str, Path]) -> None:
    text_path = directories["text"] / f"{pdf_path.stem}.txt"
    slice_path = directories["slice"] / f"{pdf_path.stem}.md"
    if not text_path.exists() or not slice_path.exists():
        process_pdf(pdf_path, directories["text"], directories["slice"])


LEDGER_FIELDS = [
    "报告ID", "官方记录ID", "官方分类代码", "韩文报告类型", "发布日期", "观察窗", "韩文题名",
    "作者", "语言", "资料角色", "科技关联层级", "主题标签", "官方落地页", "官方PDF",
    "本地原始资产", "本地文本", "本地切片", "字节数", "SHA256", "PDF页数",
    "提取文本字符数", "文本质量", "本地状态", "错误", "获取日期",
]


def result_summary(statuses: Counter) -> str:
    return (
        f"官方PDF保存：{statuses['官方PDF已保存并校验']}项；"
        f"同版PDF关联：{statuses['关联既有官方PDF']}项；"
        f"官方目录无PDF：{statuses['官方目录无PDF']}项；"
        f"获取失败：{statuses['获取失败']}项。"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.research.resolve()
    directories = {
        "pdf": root / "03_证据底稿" / "原文PDF",
        "text": root / "03_证据底稿" / "文本",
        "slice": root / "03_证据底稿" / "切片",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)

    entries = collect_catalog()
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    existing_by_id = {
        row["报告ID"]: row
        for row in catalog
        if row.get("报告ID", "").startswith("C-STEPI-")
        and row.get("本地原始资产路径", "").strip()
        and Path(row["本地原始资产路径"]).exists()
    }
    for report_id, row in discover_local_assets(directories["pdf"]).items():
        existing_by_id.setdefault(report_id, row)
    targets = [
        entry for entry in entries
        if stable_report_id(entry.category_code, entry.record_id) not in existing_by_id
    ]
    cache_dir = root / "03_证据底稿" / ".stepi_download_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    acquisitions: dict[str, Acquisition] = {}
    completed = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(acquire, entry, cache_dir): entry for entry in targets}
        for future in as_completed(futures):
            entry = futures[future]
            report_id = stable_report_id(entry.category_code, entry.record_id)
            acquisitions[report_id] = future.result()
            completed += 1
            result = acquisitions[report_id]
            print(
                f"acquired={completed}/{len(targets)} id={report_id} status={result.status}",
                flush=True,
            )

    existing_hashes: dict[str, Path] = {}
    for asset in directories["pdf"].glob("*.pdf"):
        try:
            existing_hashes.setdefault(hashlib.sha256(asset.read_bytes()).hexdigest(), asset)
        except OSError:
            continue

    ledger_rows: list[dict[str, str]] = []
    new_catalog: list[dict[str, str]] = []
    for index, entry in enumerate(entries, start=1):
        report_id = stable_report_id(entry.category_code, entry.record_id)
        existing = existing_by_id.get(report_id)
        local_asset = local_text = local_slice = digest = evidence_text = error = ""
        pages = chars = byte_count = 0
        status = ""
        if existing:
            try:
                ensure_pdf_derivatives(Path(existing["本地原始资产路径"]), directories)
                local_asset, local_text, local_slice, pages, chars, digest, byte_count = bruegel_asset_details(existing, directories)
                evidence_text = Path(local_text).read_text(encoding="utf-8", errors="replace")
                status = existing_status(existing, Path(local_asset))
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        result = acquisitions.get(report_id)
        if not local_asset and result:
            status, error = result.status, result.error
            if result.cache_path:
                data = Path(result.cache_path).read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                duplicate = existing_hashes.get(digest)
                if duplicate:
                    pdf_path = duplicate
                    status = "关联既有官方PDF" if duplicate.stem != report_id else "官方PDF已保存并校验"
                else:
                    pdf_path = directories["pdf"] / f"{report_id}.pdf"
                    pdf_path.write_bytes(data)
                    existing_hashes[digest] = pdf_path
                text_path = directories["text"] / f"{pdf_path.stem}.txt"
                slice_path = directories["slice"] / f"{pdf_path.stem}.md"
                ensure_pdf_derivatives(pdf_path, directories)
                evidence_text = text_path.read_text(encoding="utf-8", errors="replace")
                pages = result.pages
                chars, byte_count = len(evidence_text), len(data)
                local_asset, local_text, local_slice = map(str, (pdf_path, text_path, slice_path))
                Path(result.cache_path).unlink(missing_ok=True)
        if not local_asset and not status:
            status = "官方目录无PDF" if not entry.pdf_filename else "获取失败"

        tech_layer = classify_technology_scope(entry.title_ko)
        themes = classify_themes(entry.title_ko, evidence_text)
        text_quality = classify_text_quality(chars, pages, bool(local_asset))
        catalog_row = {
            "报告ID": report_id,
            "机构ID": "stepi",
            "机构英文名": "Science and Technology Policy Institute",
            "国家或地区": "韩国",
            "发布日期": entry.published,
            "观察窗": observation_window(entry.published),
            "报告名称": entry.title_ko,
            "报告类型": f"STEPI {entry.report_type}",
            "原文链接": landing_url(entry),
            "本地路径": "",
            "正文完整度": (
                "官方图像型PDF已保存，OCR待补" if text_quality == "图像型PDF，OCR待补"
                else "本地韩文原文已保存" if local_asset
                else "官方目录元数据，正文待补"
            ),
            "优先级": (
                "P0-China-tech-corpus" if "中国科技" in themes
                else "P0-core-tech" if tech_layer == "核心科技直接材料"
                else "P1-STI-baseline"
            ),
            "示踪问题": themes,
            "机构观点等级": "机构正式研究",
            "样本角色": f"STEPI韩文正式研究库/{tech_layer}",
            "编码状态": "待编码",
            "预期用途": "韩国科技创新政策、核心技术、中国比较、研发体系、人才与产业创新专题复用",
            "本地原始资产路径": local_asset,
            "原始资产状态": status,
        }
        new_catalog.append(catalog_row)
        ledger_rows.append({
            "报告ID": report_id,
            "官方记录ID": entry.record_id,
            "官方分类代码": entry.category_code,
            "韩文报告类型": entry.report_type,
            "发布日期": entry.published,
            "观察窗": observation_window(entry.published),
            "韩文题名": entry.title_ko,
            "作者": entry.author,
            "语言": "韩文",
            "资料角色": "机构正式研究",
            "科技关联层级": tech_layer,
            "主题标签": themes,
            "官方落地页": landing_url(entry),
            "官方PDF": download_url(entry) if entry.pdf_filename else "",
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
        if index % 25 == 0 or index == len(entries):
            print(f"processed={index}/{len(entries)}", flush=True)

    merged = [row for row in catalog if not row.get("报告ID", "").startswith("C-STEPI-")] + new_catalog
    merged.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, merged, CATALOG_FIELDS)
    ledger_path = root / "60_STEPI韩文科技与中国专题增补台账.csv"
    write_csv(ledger_path, ledger_rows, LEDGER_FIELDS)
    theme_input = [{**row, "报告名称": row["韩文题名"]} for row in ledger_rows]
    theme_rows = build_theme_rows(theme_input)
    write_csv(
        root / "62_STEPI韩文科技与中国主题索引.csv",
        theme_rows,
        ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"],
    )
    matrix_counts = Counter(
        (theme, row["科技关联层级"], row["观察窗"], row["韩文报告类型"], row["本地状态"])
        for row in ledger_rows for theme in row["主题标签"].split("；")
    )
    matrix_rows = [
        {"主题标签": key[0], "科技关联层级": key[1], "观察窗": key[2], "韩文报告类型": key[3], "本地状态": key[4], "材料数": str(value)}
        for key, value in sorted(matrix_counts.items())
    ]
    write_csv(
        root / "63_STEPI韩文科技与中国复用矩阵.csv",
        matrix_rows,
        ["主题标签", "科技关联层级", "观察窗", "韩文报告类型", "本地状态", "材料数"],
    )
    statuses = Counter(row["本地状态"] for row in ledger_rows)
    categories = Counter(row["韩文报告类型"] for row in ledger_rows)
    windows = Counter(row["观察窗"] for row in ledger_rows)
    core_count = sum(row["科技关联层级"] == "核心科技直接材料" for row in ledger_rows)
    china_count = sum("中国科技与国际比较" in row["主题标签"] for row in ledger_rows)
    image_pdf_count = sum(row["文本质量"] == "图像型PDF，OCR待补" for row in ledger_rows)
    result_lines = [
        "# STEPI近十年韩文科技与中国专题库增补结果", "",
        f"- 纳入2016—2026年正式研究成果：{len(ledger_rows)}项。",
        f"- 政策研究：{categories['정책연구']}项；调查研究：{categories['조사연구']}项；政策资料：{categories['정책자료']}项；其他研究：{categories['기타연구']}项。",
        f"- W1：{windows['W1']}项；W2：{windows['W2']}项；W3：{windows['W3']}项。",
        f"- 核心科技直接材料：{core_count}项；中国科技与国际比较材料：{china_count}项。",
        f"- 可检索PDF正文：{statuses['官方PDF已保存并校验'] - image_pdf_count}项；图像型PDF、OCR待补：{image_pdf_count}项。",
        f"- {result_summary(statuses)}",
        f"- 报告总目录现为：{len(merged)}项。", "",
        "## 纳入边界", "",
        "限定STEPI韩文官方出版物目录中2016—2026年政策研究、调查研究、政策资料和其他研究四类正式成果。STEPI Insight、科技政策Brief、Future Horizon+、Outlook及期刊文章保留为后续第二层材料，未与正式研究混合。", "",
        "## 使用边界", "",
        "全部条目按机构正式研究处理，保留韩文题名、作者和韩文原文。机器主题标签仅作检索入口；精确引用须回查官方PDF、韩文原句与页码。官方目录未提供PDF的条目只保留元数据，不据此提炼核心观点。", "",
    ]
    (root / "61_STEPI韩文科技与中国专题增补结果.md").write_text("\n".join(result_lines), encoding="utf-8")
    print(
        f"entries={len(entries)} pdf={statuses['官方PDF已保存并校验']} "
        f"linked={statuses['关联既有官方PDF']} no_pdf={statuses['官方目录无PDF']} "
        f"failed={statuses['获取失败']} catalog={len(merged)}",
        flush=True,
    )
    return 1 if statuses["获取失败"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
