from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import clean_page_text, pdf_candidates, request
from extract_viewpoint_pdf_slices import process_pdf


API_ROOT = "https://cset.georgetown.edu/wp-json/wp/v2/document"
AFTER = "2019-01-01T00:00:00"
BEFORE = "2023-01-01T00:00:00"
REPORT_TYPE = 18
TRANSLATION_TYPE = 20
TESTIMONY_TYPE = 22
CHINA_TOPIC = 8

REPORT_RE = re.compile(
    r"china|chinese|beijing|semiconductor|chip|technology transfer|military.civil|"
    r"research security|tech competition|talent recruitment|export control|supply chain",
    re.I,
)
NONREPORT_TECH_RE = re.compile(
    r"artificial intelligence|\bAI\b|technology|science|innovation|strategic emerging|"
    r"military.civil|talent|expert|scholarship|education|space|cyber|digital|export control|"
    r"semiconductor|chip|research|tech-related|scientists|engineering|natural science foundation|"
    r"association for science",
    re.I,
)
FIRST_PARTY_PDF_RE = re.compile(
    r"href=[\"'](https://cset\.georgetown\.edu/wp-content/uploads/[^\"']+?\.pdf(?:\?[^\"']*)?)[\"']",
    re.I,
)

CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]


@dataclass(frozen=True)
class Candidate:
    report_id: str
    wp_id: int
    published: str
    title: str
    landing_url: str
    content_type_id: int
    content_type: str
    selection_basis: str
    abstract: str
    themes: str


@dataclass
class Acquisition:
    candidate: Candidate
    page_data: bytes = b""
    page_text: str = ""
    pdf_url: str = ""
    pdf_data: bytes = b""
    status: str = ""
    error: str = ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def merge_ledger_rows(
    existing_rows: list[dict[str, str]],
    refreshed_rows: list[dict[str, str]],
    ordered_ids: list[str],
) -> list[dict[str, str]]:
    by_id = {row["报告ID"]: row for row in existing_rows}
    by_id.update({row["报告ID"]: row for row in refreshed_rows})
    return [by_id[report_id] for report_id in ordered_ids if report_id in by_id]


def normalize_extracted_text(path: Path) -> None:
    value = path.read_text(encoding="utf-8")
    normalized = re.sub(r"[ \t\r]+(?=\n|$)", "", value)
    if normalized != value:
        path.write_text(normalized, encoding="utf-8")


def refresh_ledger_text_counts(rows: list[dict[str, str]]) -> None:
    for row in rows:
        text_value = row.get("本地文本", "")
        if not text_value:
            continue
        text_path = Path(text_value)
        if not text_path.exists():
            continue
        normalize_extracted_text(text_path)
        row["提取文本字符数"] = str(len(text_path.read_text(encoding="utf-8")))


def clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def safe_url(url: str) -> str:
    parts = urlsplit(html.unescape(url))
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), parts.query, parts.fragment))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_json(url: str):
    raw, _, _ = request(url, timeout=60)
    return json.loads(raw.decode("utf-8"))


def fetch_all(extra: str) -> list[dict]:
    items: list[dict] = []
    page = 1
    while True:
        url = (
            f"{API_ROOT}?per_page=100&page={page}&orderby=date&order=asc&"
            f"after={AFTER}&before={BEFORE}&{extra}"
        )
        batch = fetch_json(url)
        if not batch:
            break
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def classify_themes(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    themes: list[str] = []
    rules = [
        ("人工智能与算力", r"artificial intelligence|\bai\b|compute|chip|semiconductor"),
        ("科技人才与科研安全", r"talent|education|scholarship|student|workforce|research security|scientist|stem"),
        ("技术转移与出口管制", r"technology transfer|export control|chokepoint|decoupl|supply chain|foreign technology"),
        ("军民融合与国防科技", r"military|defen[cs]e|military.civil|pla"),
        ("数字治理与网络安全", r"cyber|surveillance|digital|data|privacy"),
        ("国家创新体系与产业政策", r"innovation|science|strategic emerging|industrial|government guidance|budget|fund"),
        ("航天与其他前沿技术", r"space|biotech|robot|quantum|brain"),
    ]
    for label, pattern in rules:
        if re.search(pattern, text, re.I):
            themes.append(label)
    return "；".join(themes or ["综合科技竞争"])


def content_type_info(type_ids: list[int]) -> tuple[int, str]:
    if REPORT_TYPE in type_ids:
        return REPORT_TYPE, "CSET原创研究报告"
    if TESTIMONY_TYPE in type_ids:
        return TESTIMONY_TYPE, "涉华科技政策证词"
    if TRANSLATION_TYPE in type_ids:
        return TRANSLATION_TYPE, "中国科技政策英译"
    value = type_ids[0] if type_ids else 0
    return value, "其他官方研究材料"


def build_candidates() -> list[Candidate]:
    reports = fetch_all(f"content_type={REPORT_TYPE}")
    china_items = fetch_all(f"topic={CHINA_TOPIC}")
    selected: dict[int, tuple[dict, str]] = {}
    for item in reports:
        title = clean_html(item.get("title", {}).get("rendered", ""))
        abstract = clean_html(item.get("excerpt", {}).get("rendered", ""))
        if REPORT_RE.search(f"{title} {abstract}"):
            selected[int(item["id"])] = (item, "正式报告涉华科技关键词命中")
    for item in china_items:
        type_ids = [int(value) for value in item.get("content_type", [])]
        if REPORT_TYPE in type_ids:
            continue
        title = clean_html(item.get("title", {}).get("rendered", ""))
        if TESTIMONY_TYPE in type_ids or NONREPORT_TECH_RE.search(title):
            basis = "China主题下的科技政策证词" if TESTIMONY_TYPE in type_ids else "China主题下的科技政策英译"
            selected[int(item["id"])] = (item, basis)

    candidates: list[Candidate] = []
    for wp_id, (item, basis) in selected.items():
        title = clean_html(item.get("title", {}).get("rendered", ""))
        abstract = clean_html(item.get("excerpt", {}).get("rendered", ""))
        type_id, type_name = content_type_info([int(value) for value in item.get("content_type", [])])
        candidates.append(
            Candidate(
                report_id=f"C-CSET-{wp_id}",
                wp_id=wp_id,
                published=str(item["date"])[:10],
                title=title,
                landing_url=item["link"],
                content_type_id=type_id,
                content_type=type_name,
                selection_basis=basis,
                abstract=abstract,
                themes=classify_themes(title, abstract),
            )
        )
    return sorted(candidates, key=lambda item: (item.published, item.wp_id))


def acquire_candidate(candidate: Candidate) -> Acquisition:
    result = Acquisition(candidate=candidate)
    try:
        page_data, final_url, _ = request(candidate.landing_url, timeout=60)
        result.page_data = page_data
        result.page_text = clean_page_text(page_data)
        source = page_data.decode("utf-8", errors="replace")
        first_party = [html.unescape(match) for match in FIRST_PARTY_PDF_RE.findall(source)]
        if not first_party:
            first_party = [
                url for url in pdf_candidates(final_url, page_data, candidate.title)
                if url.startswith("https://cset.georgetown.edu/wp-content/uploads/")
            ]
        if not first_party:
            result.status = "官方网页全文已保存"
            return result
        result.pdf_url = safe_url(first_party[0])
        pdf_data, final_pdf_url, _ = request(result.pdf_url, referer=final_url, timeout=90)
        result.pdf_url = final_pdf_url
        if not pdf_data.startswith(b"%PDF"):
            result.status = "PDF链接返回非PDF"
            result.error = f"bytes={len(pdf_data)}"
            return result
        result.pdf_data = pdf_data
        result.status = "官方PDF已获取"
    except Exception as exc:
        result.status = "获取失败"
        result.error = f"{type(exc).__name__}: {exc}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()

    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    html_dir = root / "03_证据底稿" / "网页快照"
    web_text_dir = root / "03_证据底稿" / "网页文本"
    web_transcript_dir = root / "03_证据底稿" / "网页转写"
    for directory in (pdf_dir, text_dir, slice_dir, html_dir, web_text_dir, web_transcript_dir):
        directory.mkdir(parents=True, exist_ok=True)

    candidates = build_candidates()
    catalog = read_csv(catalog_path)
    existing_by_id = {row["报告ID"]: row for row in catalog}
    ledger_path = root / "27_CSET涉华科技专题增补台账.csv"
    existing_ledger = read_csv(ledger_path) if ledger_path.exists() else []
    existing_ledger_by_id = {row["报告ID"]: row for row in existing_ledger}
    existing_hashes: dict[str, Path] = {}
    for pdf_path in pdf_dir.glob("*.pdf"):
        digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
        existing_hashes.setdefault(digest, pdf_path)

    targets = [
        item
        for item in candidates
        if item.report_id not in existing_ledger_by_id
        or existing_ledger_by_id[item.report_id].get("本地状态") == "获取失败"
        or not Path(existing_ledger_by_id[item.report_id].get("本地原始资产", "")).exists()
        or Path(existing_ledger_by_id[item.report_id].get("本地原始资产", "")).suffix.lower() == ".html"
    ]
    acquisitions: dict[str, Acquisition] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(acquire_candidate, item): item.report_id for item in targets}
        for future in as_completed(futures):
            report_id = futures[future]
            try:
                acquisitions[report_id] = future.result()
            except Exception as exc:
                candidate = next(item for item in targets if item.report_id == report_id)
                acquisitions[report_id] = Acquisition(
                    candidate=candidate,
                    status="获取失败",
                    error=f"{type(exc).__name__}: {exc}",
                )

    refreshed_ledger_rows: list[dict[str, str]] = []
    new_catalog_rows: list[dict[str, str]] = []
    for candidate in candidates:
        if candidate.report_id not in acquisitions:
            continue
        result = acquisitions[candidate.report_id]
        digest = ""
        pages = 0
        chars = 0
        local_asset = ""
        local_text = ""
        local_slice = ""
        asset_status = result.status
        if result.pdf_data:
            digest = sha256_bytes(result.pdf_data)
            duplicate = existing_hashes.get(digest)
            if duplicate:
                pdf_path = duplicate
                asset_status = "关联既有官方PDF"
            else:
                pdf_path = pdf_dir / f"{candidate.report_id}.pdf"
                pdf_path.write_bytes(result.pdf_data)
                existing_hashes[digest] = pdf_path
            reader = PdfReader(str(pdf_path))
            pages = len(reader.pages)
            text_path = text_dir / f"{pdf_path.stem}.txt"
            slice_path = slice_dir / f"{pdf_path.stem}.md"
            if not text_path.exists() or not slice_path.exists():
                process_pdf(pdf_path, text_dir, slice_dir)
            normalize_extracted_text(text_path)
            chars = len(text_path.read_text(encoding="utf-8"))
            local_asset = str(pdf_path)
            local_text = str(text_path)
            local_slice = str(slice_path)
            if asset_status != "关联既有官方PDF":
                asset_status = "官方PDF已保存并校验"
        elif result.page_data and result.page_text:
            html_path = html_dir / f"{candidate.report_id}.html"
            page_text_path = web_text_dir / f"{candidate.report_id}.txt"
            transcript_path = web_transcript_dir / f"{candidate.report_id}.md"
            html_path.write_bytes(result.page_data)
            page_text_path.write_text(result.page_text, encoding="utf-8")
            transcript_path.write_text(
                "\n".join(
                    [
                        f"# {candidate.title}",
                        "",
                        f"- 发布机构：Center for Security and Emerging Technology",
                        f"- 发布日期：{candidate.published}",
                        f"- 官方页面：{candidate.landing_url}",
                        f"- 材料类型：{candidate.content_type}",
                        "",
                        result.page_text,
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            local_asset = str(page_text_path)
            local_text = str(page_text_path)
            local_slice = str(transcript_path)
            chars = len(result.page_text)
            digest = sha256_bytes(result.page_text.encode("utf-8"))
            asset_status = "官方网页全文已保存"

        viewpoint_level = {
            REPORT_TYPE: "作者/项目正式研究",
            TRANSLATION_TYPE: "翻译材料，不代表机构观点",
            TESTIMONY_TYPE: "作者政策证词",
        }.get(candidate.content_type_id, "官方研究材料")
        catalog_row = {
            "报告ID": candidate.report_id,
            "机构ID": "cset",
            "机构英文名": "Center for Security and Emerging Technology",
            "国家或地区": "美国",
            "发布日期": candidate.published,
            "观察窗": "W2" if candidate.published[:4] in {"2019", "2020", "2021"} else "W3",
            "报告名称": candidate.title,
            "报告类型": candidate.content_type,
            "原文链接": candidate.landing_url,
            "本地路径": "",
            "正文完整度": "本地原文已保存" if local_asset else "获取失败",
            "优先级": "P0-China-tech-corpus" if candidate.content_type_id == REPORT_TYPE else "P1-China-tech-source",
            "示踪问题": candidate.themes,
            "机构观点等级": viewpoint_level,
            "样本角色": "CSET涉华科技专题库",
            "编码状态": "待编码",
            "预期用途": "中国科技战略、创新体系、技术竞争与供应链专题复用",
            "本地原始资产路径": local_asset,
            "原始资产状态": asset_status if local_asset else "获取失败",
        }
        if candidate.report_id in existing_by_id:
            existing_by_id[candidate.report_id].update(catalog_row)
        else:
            new_catalog_rows.append(catalog_row)
        refreshed_ledger_rows.append(
            {
                "报告ID": candidate.report_id,
                "WordPress_ID": str(candidate.wp_id),
                "发布日期": candidate.published,
                "观察窗": catalog_row["观察窗"],
                "材料类型": candidate.content_type,
                "报告名称": candidate.title,
                "资料角色": viewpoint_level,
                "主题标签": candidate.themes,
                "筛选依据": candidate.selection_basis,
                "官方摘要": candidate.abstract,
                "官方落地页": candidate.landing_url,
                "官方PDF": result.pdf_url,
                "本地原始资产": local_asset,
                "本地文本": local_text,
                "本地切片或转写": local_slice,
                "字节数": str(len(result.pdf_data) if result.pdf_data else len(result.page_data)),
                "SHA256": digest,
                "PDF页数": str(pages),
                "提取文本字符数": str(chars),
                "本地状态": asset_status if local_asset else "获取失败",
                "错误": result.error,
                "获取日期": date.today().isoformat(),
            }
        )

    ledger_rows = merge_ledger_rows(
        existing_ledger,
        refreshed_ledger_rows,
        [candidate.report_id for candidate in candidates],
    )
    refresh_ledger_text_counts(ledger_rows)
    merged = catalog + new_catalog_rows
    merged.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, merged, CATALOG_FIELDS)

    ledger_fields = [
        "报告ID", "WordPress_ID", "发布日期", "观察窗", "材料类型", "报告名称", "资料角色",
        "主题标签", "筛选依据", "官方摘要", "官方落地页", "官方PDF", "本地原始资产",
        "本地文本", "本地切片或转写", "字节数", "SHA256", "PDF页数", "提取文本字符数",
        "本地状态", "错误", "获取日期",
    ]
    write_csv(ledger_path, ledger_rows, ledger_fields)

    theme_rows: list[dict[str, str]] = []
    for row in ledger_rows:
        for theme in row["主题标签"].split("；"):
            theme_rows.append(
                {
                    "主题标签": theme,
                    "报告ID": row["报告ID"],
                    "发布日期": row["发布日期"],
                    "观察窗": row["观察窗"],
                    "材料类型": row["材料类型"],
                    "报告名称": row["报告名称"],
                    "资料角色": row["资料角色"],
                    "官方摘要": row["官方摘要"],
                    "本地原始资产": row["本地原始资产"],
                    "本地文本": row["本地文本"],
                    "官方落地页": row["官方落地页"],
                }
            )
    write_csv(
        root / "29_CSET涉华科技主题索引.csv",
        theme_rows,
        [
            "主题标签", "报告ID", "发布日期", "观察窗", "材料类型", "报告名称", "资料角色",
            "官方摘要", "本地原始资产", "本地文本", "官方落地页",
        ],
    )

    matrix_counter: Counter[tuple[str, str, str]] = Counter()
    for row in theme_rows:
        matrix_counter[(row["主题标签"], row["观察窗"], row["材料类型"])] += 1
    matrix_rows = [
        {"主题标签": theme, "观察窗": window, "材料类型": material_type, "材料数": str(count)}
        for (theme, window, material_type), count in sorted(matrix_counter.items())
    ]
    write_csv(root / "30_CSET涉华科技复用矩阵.csv", matrix_rows, ["主题标签", "观察窗", "材料类型", "材料数"])

    status_counts = Counter(row["本地状态"] for row in ledger_rows)
    type_counts = Counter(row["材料类型"] for row in ledger_rows)
    lines = [
        "# CSET 2019—2022年涉华科技专题库增补结果",
        "",
        f"- 候选材料：{len(ledger_rows)}项。",
        f"- CSET原创研究报告：{type_counts['CSET原创研究报告']}项。",
        f"- 中国科技政策英译：{type_counts['中国科技政策英译']}项。",
        f"- 涉华科技政策证词：{type_counts['涉华科技政策证词']}项。",
        f"- 官方PDF保存：{status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']}项。",
        f"- 官方网页全文保存：{status_counts['官方网页全文已保存']}项。",
        f"- 获取失败：{status_counts['获取失败']}项。",
        f"- 新增原始资料字节数：{sum(int(row['字节数']) for row in ledger_rows):,}。",
        f"- 新增PDF物理页数：{sum(int(row['PDF页数']) for row in ledger_rows):,}。",
        f"- 报告总目录：{len(catalog)}项扩展至{len(merged)}项。",
        "",
        "## 资料角色边界",
        "",
        "原创研究报告可用于识别CSET作者和项目的判断；政策英译用于保存中国科技政策的英文可检索版本，不代表CSET机构立场；政策证词反映作者向美国决策机构提交的判断，也不自动上升为机构统一观点。",
        "",
        "## 跨项目调用",
        "",
        "优先从`29_CSET涉华科技主题索引.csv`按主题和摘要检索，再回到本地逐页文本及官方PDF。`30_CSET涉华科技复用矩阵.csv`用于判断主题、观察窗和材料类型的覆盖结构。",
        "",
    ]
    failed = [row for row in ledger_rows if row["本地状态"] == "获取失败"]
    if failed:
        lines.extend(["## 未完成项", ""])
        lines.extend(f"- `{row['报告ID']}`：{row['错误']}" for row in failed)
        lines.append("")
    (root / "28_CSET涉华科技专题增补结果.md").write_text("\n".join(lines), encoding="utf-8")

    print(
        f"candidates={len(ledger_rows)} pdf={status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']} "
        f"web={status_counts['官方网页全文已保存']} failed={status_counts['获取失败']} catalog={len(merged)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
