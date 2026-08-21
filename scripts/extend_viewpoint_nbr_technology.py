from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import request
from extract_viewpoint_pdf_slices import process_pdf


PROGRAM_URL = "https://www.nbr.org/program/technology-and-geoeconomic-affairs/"
PROXY_URL = f"https://r.jina.ai/{PROGRAM_URL}"
SITE_ROOT = "https://www.nbr.org/"
CUTOFF = "2016-01-01"
END_DATE = "2026-08-22"
EXCLUDED_TYPES = {"Podcast", "Podcast Series"}
OFFICIAL_HOSTS = {"nbr.org", "www.nbr.org"}
PDF_RE = re.compile(r"https?://www\.nbr\.org/wp-content/uploads/pdfs/publications/[^\s)\]\"']+?\.pdf(?:\?[^\s)\]\"']*)?", re.I)
CHINA_RE = re.compile(r"\b(?:China|Chinese|Beijing|PRC|Sino-|CCP|Huawei)\b", re.I)
CORE_TECH_RE = re.compile(
    r"artificial intelligence|\bAI\b|quantum|semiconductor|\bchips?\b|cyber|digital|data |"
    r"technology|technolog|innovation|biotech|battery|critical mineral|rare earth|5G|cloud|"
    r"technical standard|intellectual property|\bIP theft\b|supply chain|export control|"
    r"advanced manufacturing|computing|internet|platform",
    re.I,
)
TECH_THEME_PATTERNS = {
    "人工智能、芯片与算力": re.compile(r"artificial intelligence|\bAI\b|semiconductor|\bchips?\b|computing|data cent(?:er|re)", re.I),
    "网络安全与数字治理": re.compile(r"cyber|digital|data governance|data security|internet|cloud|platform|5G|information operation", re.I),
    "技术供应链与出口管制": re.compile(r"supply chain|export control|critical mineral|rare earth|battery|de-risk|economic security", re.I),
    "创新体系、标准与知识产权": re.compile(r"innovation|industrial policy|technical standard|intellectual property|\bIP theft\b|technology leadership", re.I),
    "生物、量子及其他前沿技术": re.compile(r"biotech|biosecurity|biopharmaceutical|quantum|advanced manufacturing", re.I),
}
TYPE_CN = {
    "Report": "NBR研究报告",
    "Brief": "NBR政策简报",
    "Policy Brief": "NBR政策简报",
    "Commentary": "NBR评论",
    "Interview": "NBR访谈",
    "Backgrounder": "NBR背景材料",
    "Roundtable": "NBR圆桌论文",
    "Testimony": "NBR政策证词",
    "Essay": "NBR论文",
}
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]


@dataclass(frozen=True)
class Candidate:
    report_id: str
    published: str
    title: str
    landing_url: str
    category: str
    material_type: str
    authors: str = ""
    pdf_url: str = ""
    selection_basis: str = "NBR技术与地缘经济事务项目正式出版物"


@dataclass
class Acquisition:
    candidate: Candidate
    page_html: str = ""
    page_text: str = ""
    page_source: str = ""
    pdf_url: str = ""
    pdf_data: bytes = b""
    status: str = ""
    error: str = ""


def canonical_url(url: str) -> str:
    parts = urlsplit(urljoin(SITE_ROOT, html.unescape(url)))
    path = re.sub(r"/+", "/", parts.path).rstrip("/") + "/"
    return urlunsplit(("https", "www.nbr.org", path, "", ""))


def safe_url(url: str) -> str:
    parts = urlsplit(html.unescape(url))
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%:@"), parts.query, ""))


def stable_report_id(url: str) -> str:
    digest = hashlib.sha1(canonical_url(url).encode("utf-8")).hexdigest()[:10].upper()
    return f"C-NBR-{digest}"


def clean_markdown_label(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", html.unescape(value))).strip()


def parse_program_publications(markdown_text: str) -> list[Candidate]:
    lines = markdown_text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == "All Program Publications") + 1
    except StopIteration:
        start = 0
    candidates: list[Candidate] = []
    header_re = re.compile(r"^### \[([^\]]+)\]\((https://www\.nbr\.org/publication/[^)]+)\)$")
    type_date_re = re.compile(r"^([^|]+?)\s*\|\s*([A-Z][a-z]{2} \d{1,2}, \d{4})$")
    for index in range(start, len(lines)):
        header = header_re.match(lines[index].strip())
        if not header:
            continue
        previous = index - 1
        while previous >= start and not lines[previous].strip():
            previous -= 1
        category = clean_markdown_label(lines[previous]) if previous >= start else ""
        metadata: list[str] = []
        cursor = index + 1
        while cursor < len(lines) and cursor <= index + 8 and not lines[cursor].startswith("### "):
            if lines[cursor].strip():
                metadata.append(lines[cursor].strip())
            cursor += 1
        type_line_index = next((i for i, value in enumerate(metadata) if type_date_re.match(value)), None)
        if type_line_index is None:
            continue
        type_match = type_date_re.match(metadata[type_line_index])
        assert type_match is not None
        material_type = type_match.group(1).strip()
        if material_type in EXCLUDED_TYPES:
            continue
        published = datetime.strptime(type_match.group(2), "%b %d, %Y").date().isoformat()
        if not (CUTOFF <= published <= END_DATE):
            continue
        landing_url = canonical_url(header.group(2))
        candidates.append(
            Candidate(
                report_id=stable_report_id(landing_url),
                published=published,
                title=clean_markdown_label(header.group(1)),
                landing_url=landing_url,
                category=category,
                material_type=material_type,
                authors=" ".join(metadata[:type_line_index]).strip(),
            )
        )
    by_url = {item.landing_url: item for item in candidates}
    return sorted(by_url.values(), key=lambda item: (item.published, item.report_id))


def ip_commission_supplements() -> list[Candidate]:
    rows = [
        ("2017-02-01", "Update to the IP Commission Report: The Theft of American Intellectual Property", "IP_Commission_Report_Update.pdf", "NBR研究报告"),
        ("2018-03-01", "Recommendations Regarding the Section 301 Investigation", "IPC_Recommendations_to_Section_301_Investigation_March2018.pdf", "NBR政策意见"),
        ("2018-05-01", "Written Comments on the Section 301 Tariffs", "ustr_written_comments_301_tariffs-may2018.pdf", "NBR政策意见"),
        ("2019-02-01", "IP Commission 2019 Review: Progress and Updated Recommendations", "ip_commission_2019_review_of_progress_and_updated_recommendations.pdf", "NBR研究报告"),
        ("2021-03-01", "IP Commission 2021 Review: Updated Recommendations", "ip_commission_2021_recommendations_mar2021.pdf", "NBR政策简报"),
        ("2021-03-01", "IP Commission 2021 Background Memo", "ip_commission_2021_background_memo_mar21.pdf", "NBR背景材料"),
    ]
    values: list[Candidate] = []
    for published, title, filename, material_type in rows:
        pdf_url = f"https://www.nbr.org/wp-content/uploads/pdfs/publications/{filename}"
        values.append(
            Candidate(
                report_id=stable_report_id(pdf_url),
                published=published,
                title=title,
                landing_url="https://www.nbr.org/publication/the-ip-commission-report/",
                category="IP Theft",
                material_type=material_type,
                pdf_url=pdf_url,
                selection_basis="NBR知识产权委员会官方更新附件",
            )
        )
    return values


def extract_official_pdf_urls(text: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for match in PDF_RE.findall(text):
        url = safe_url(match)
        if urlsplit(url).hostname not in OFFICIAL_HOSTS or url in seen:
            continue
        seen.add(url)
        values.append(url)
    return values


def classify_china_relevance(title: str, text: str, category: str) -> str:
    if CHINA_RE.search(f"{title} {category}"):
        return "直接涉华科技"
    if len(CHINA_RE.findall(text)) >= 5:
        return "含中国比较的印太技术材料"
    return "区域技术基线"


def classify_technology_scope(title: str, category: str) -> str:
    return "核心科技直接材料" if CORE_TECH_RE.search(f"{title} {category}") else "科技地缘经济基线"


def classify_themes(title: str, category: str, text: str) -> str:
    combined = f"{title} {category} {text}"
    themes = [label for label, pattern in TECH_THEME_PATTERNS.items() if pattern.search(combined)]
    return "；".join(themes or ["技术地缘经济与区域合作"])


def merge_ledger_rows(existing_rows, refreshed_rows, ordered_ids):
    by_id = {row["报告ID"]: row for row in existing_rows}
    by_id.update({row["报告ID"]: row for row in refreshed_rows})
    return [by_id[report_id] for report_id in ordered_ids if report_id in by_id]


def replace_institution_catalog_rows(catalog, refreshed_rows, report_id_prefix):
    return [row for row in catalog if not row.get("报告ID", "").startswith(report_id_prefix)] + refreshed_rows


def merge_nbr_catalog_rows(existing_rows, refreshed_rows, ordered_ids):
    by_id = {row["报告ID"]: row for row in existing_rows if row["报告ID"] in ordered_ids}
    by_id.update({row["报告ID"]: row for row in refreshed_rows})
    return [by_id[report_id] for report_id in ordered_ids if report_id in by_id]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def jina_request_headers() -> dict[str, str]:
    return {"Accept": "text/markdown"}


def fetch_jina(url: str, timeout: int = 90) -> str:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=jina_request_headers()), timeout=timeout) as response:
                return response.read(20 * 1024 * 1024).decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def _proxy_call(path: str, params: dict[str, str] | None = None, body: str | None = None):
    url = f"http://localhost:3456/{path}"
    if params:
        url += "?" + urlencode(params)
    request_obj = Request(url, data=body.encode("utf-8") if body is not None else None, method="POST" if body is not None else "GET")
    with urlopen(request_obj, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def cdp_new(url: str) -> str:
    return _proxy_call("new", {"url": url})["targetId"]


def cdp_close(target: str) -> None:
    try:
        _proxy_call("close", {"target": target})
    except Exception:
        pass


def cdp_detail(target: str, url: str) -> tuple[str, str, list[str]]:
    _proxy_call("navigate", {"target": target, "url": url})
    expression = r"""(() => ({
      title: document.title,
      html: document.documentElement.outerHTML,
      text: document.body.innerText,
      pdfs: [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => /\/wp-content\/uploads\/pdfs\/publications\/.*\.pdf(?:$|\?)/i.test(h))
    }))()"""
    value = _proxy_call("eval", {"target": target}, expression).get("value", {})
    title = str(value.get("title", ""))
    page_text = str(value.get("text", ""))
    if "Just a moment" in title or len(page_text) < 400:
        raise RuntimeError(f"blocked or thin official page: title={title!r} chars={len(page_text)}")
    return str(value.get("html", "")), page_text, list(dict.fromkeys(value.get("pdfs", [])))


def jina_detail(url: str) -> tuple[str, str, list[str]]:
    markdown = fetch_jina(f"https://r.jina.ai/{url}")
    if len(markdown) < 400 or "Security Verification Required" in markdown:
        raise RuntimeError(f"thin or blocked proxy page: chars={len(markdown)}")
    return markdown, markdown, extract_official_pdf_urls(markdown)


def acquire_candidate(candidate: Candidate, target: str | None) -> Acquisition:
    result = Acquisition(candidate=candidate, pdf_url=candidate.pdf_url)
    try:
        pdf_urls: list[str] = [candidate.pdf_url] if candidate.pdf_url else []
        if not candidate.pdf_url:
            try:
                if not target:
                    raise RuntimeError("CDP unavailable")
                result.page_html, result.page_text, pdf_urls = cdp_detail(target, candidate.landing_url)
                result.page_source = "官方网页原始HTML"
            except Exception as cdp_error:
                result.page_html, result.page_text, pdf_urls = jina_detail(candidate.landing_url)
                result.page_source = "官方页面Jina代理文本"
                result.error = f"CDP降级: {type(cdp_error).__name__}: {cdp_error}"
        if pdf_urls:
            result.pdf_url = safe_url(pdf_urls[0])
            pdf_data, final_url, _ = request(result.pdf_url, referer=candidate.landing_url, timeout=150)
            result.pdf_url = final_url
            if pdf_data.startswith(b"%PDF"):
                result.pdf_data = pdf_data
                result.status = "官方PDF已获取"
                return result
            result.error = (result.error + "；" if result.error else "") + f"PDF链接返回非PDF: bytes={len(pdf_data)}"
        if result.page_text:
            result.status = "官方网页全文已保存" if result.page_source == "官方网页原始HTML" else "官方页面代理全文已保存"
        else:
            result.status = "获取失败"
    except Exception as exc:
        result.status = "获取失败"
        result.error = (result.error + "；" if result.error else "") + f"{type(exc).__name__}: {exc}"
    return result


def observation_window(published: str) -> str:
    year = int(published[:4])
    return "W1" if year <= 2018 else "W2" if year <= 2021 else "W3"


def normalize_text_content(value: str) -> str:
    normalized = re.sub(r"[ \t\r]+(?=\n|$)", "", value)
    return re.sub(r"\n+\Z", "\n", normalized)


def normalize_extracted_text(path: Path) -> None:
    value = path.read_text(encoding="utf-8")
    normalized = normalize_text_content(value)
    if normalized != value:
        path.write_text(normalized, encoding="utf-8")


def viewpoint_level(material_type: str) -> str:
    if material_type in {"Testimony", "NBR政策证词"}:
        return "作者政策证词"
    if material_type in {"Interview", "NBR访谈"}:
        return "作者访谈"
    if material_type in {"Commentary", "Essay", "NBR评论", "NBR论文"}:
        return "作者评论或论文"
    return "作者/项目正式研究"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    candidates = parse_program_publications(fetch_jina(PROXY_URL)) + ip_commission_supplements()
    candidates = sorted({item.report_id: item for item in candidates}.values(), key=lambda item: (item.published, item.report_id))

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
    ledger_path = root / "39_NBR科技与中国专题增补台账.csv"
    existing_ledger = read_csv(ledger_path) if ledger_path.exists() else []
    existing_by_id = {row["报告ID"]: row for row in existing_ledger}
    targets = [
        item for item in candidates
        if item.report_id not in existing_by_id
        or existing_by_id[item.report_id].get("本地状态") == "获取失败"
        or not Path(existing_by_id[item.report_id].get("本地原始资产", "")).exists()
    ]

    target_id: str | None = None
    acquisitions: dict[str, Acquisition] = {}
    try:
        if any(not item.pdf_url for item in targets):
            try:
                target_id = cdp_new(PROGRAM_URL)
            except Exception:
                target_id = None
        for index, candidate in enumerate(targets, 1):
            acquisitions[candidate.report_id] = acquire_candidate(candidate, target_id)
            print(f"acquired={index}/{len(targets)} id={candidate.report_id} status={acquisitions[candidate.report_id].status}", flush=True)
            if not target_id and index < len(targets):
                time.sleep(3.1)
    finally:
        if target_id:
            cdp_close(target_id)

    catalog = read_csv(root / "05_报告总目录.csv")
    existing_hashes: dict[str, Path] = {}
    for pdf_path in directories["pdf"].glob("*.pdf"):
        existing_hashes.setdefault(hashlib.sha256(pdf_path.read_bytes()).hexdigest(), pdf_path)
    refreshed_ledger: list[dict[str, str]] = []
    nbr_catalog: list[dict[str, str]] = []
    for candidate in candidates:
        result = acquisitions.get(candidate.report_id)
        if not result:
            continue
        local_asset = local_text = local_slice = digest = ""
        pages = chars = 0
        status = result.status
        evidence_text = result.page_text
        if result.pdf_data:
            digest = hashlib.sha256(result.pdf_data).hexdigest()
            duplicate = existing_hashes.get(digest)
            expected = directories["pdf"] / f"{candidate.report_id}.pdf"
            if duplicate:
                pdf_path = duplicate
                status = "官方PDF已保存并校验" if duplicate.stem == candidate.report_id else "关联既有官方PDF"
            else:
                pdf_path = expected
                pdf_path.write_bytes(result.pdf_data)
                existing_hashes[digest] = pdf_path
                status = "官方PDF已保存并校验"
            text_path = directories["text"] / f"{pdf_path.stem}.txt"
            slice_path = directories["slice"] / f"{pdf_path.stem}.md"
            if not text_path.exists() or not slice_path.exists():
                process_pdf(pdf_path, directories["text"], directories["slice"])
            normalize_extracted_text(text_path)
            pages = len(PdfReader(str(pdf_path)).pages)
            evidence_text = text_path.read_text(encoding="utf-8")
            chars = len(evidence_text)
            local_asset, local_text, local_slice = map(str, (pdf_path, text_path, slice_path))
        elif result.page_text:
            result.page_text = normalize_text_content(result.page_text)
            suffix = ".html" if result.page_source == "官方网页原始HTML" else ".md"
            snapshot = directories["html"] / f"{candidate.report_id}{suffix}"
            text_path = directories["web_text"] / f"{candidate.report_id}.txt"
            transcript = directories["transcript"] / f"{candidate.report_id}.md"
            snapshot.write_text(result.page_html, encoding="utf-8")
            text_path.write_text(result.page_text, encoding="utf-8")
            transcript.write_text(
                f"# {candidate.title}\n\n- 发布机构：National Bureau of Asian Research\n- 发布日期：{candidate.published}\n"
                f"- 官方页面：{candidate.landing_url}\n- 材料类型：{candidate.material_type}\n- 页面来源：{result.page_source}\n\n{result.page_text}\n",
                encoding="utf-8",
            )
            digest = hashlib.sha256(result.page_text.encode("utf-8")).hexdigest()
            chars = len(result.page_text)
            local_asset, local_text, local_slice = map(str, (text_path, text_path, transcript))

        material_cn = TYPE_CN.get(candidate.material_type, candidate.material_type)
        china_layer = classify_china_relevance(candidate.title, evidence_text, candidate.category)
        tech_layer = classify_technology_scope(candidate.title, candidate.category)
        themes = classify_themes(candidate.title, candidate.category, evidence_text)
        role = viewpoint_level(candidate.material_type)
        catalog_row = {
            "报告ID": candidate.report_id, "机构ID": "nbr", "机构英文名": "National Bureau of Asian Research",
            "国家或地区": "美国", "发布日期": candidate.published, "观察窗": observation_window(candidate.published),
            "报告名称": candidate.title, "报告类型": material_cn, "原文链接": candidate.landing_url, "本地路径": "",
            "正文完整度": "本地原文已保存" if local_asset else "获取失败", "优先级": "P0-China-tech-corpus" if china_layer != "区域技术基线" else "P1-regional-tech-baseline",
            "示踪问题": themes, "机构观点等级": role, "样本角色": f"NBR科技与中国专题库/{china_layer}/{tech_layer}",
            "编码状态": "待编码", "预期用途": "中国科技竞争、印太技术治理、供应链安全、创新合作及区域比较专题复用",
            "本地原始资产路径": local_asset, "原始资产状态": status if local_asset else "获取失败",
        }
        nbr_catalog.append(catalog_row)
        refreshed_ledger.append({
            "报告ID": candidate.report_id, "发布日期": candidate.published, "观察窗": catalog_row["观察窗"], "材料类型": material_cn,
            "原始类型": candidate.material_type, "报告名称": candidate.title, "作者": candidate.authors, "资料角色": role,
            "项目分类": candidate.category, "中国关联层级": china_layer, "科技关联层级": tech_layer, "主题标签": themes,
            "筛选依据": candidate.selection_basis, "官方落地页": candidate.landing_url, "官方PDF": result.pdf_url,
            "页面来源": result.page_source, "本地原始资产": local_asset, "本地文本": local_text, "本地切片或转写": local_slice,
            "字节数": str(len(result.pdf_data) if result.pdf_data else len(result.page_html.encode("utf-8"))), "SHA256": digest,
            "PDF页数": str(pages), "提取文本字符数": str(chars), "本地状态": status if local_asset else "获取失败",
            "错误": result.error, "获取日期": date.today().isoformat(),
        })

    ordered_ids = [item.report_id for item in candidates]
    ledger_rows = merge_ledger_rows(existing_ledger, refreshed_ledger, ordered_ids)
    for row in ledger_rows:
        asset = Path(row.get("本地原始资产", ""))
        transcript = Path(row.get("本地切片或转写", ""))
        if asset.suffix.lower() != ".pdf" and asset.exists():
            normalize_extracted_text(asset)
            value = asset.read_text(encoding="utf-8")
            row["SHA256"] = hashlib.sha256(value.encode("utf-8")).hexdigest()
            row["提取文本字符数"] = str(len(value))
        if transcript.exists() and transcript.suffix.lower() == ".md":
            normalize_extracted_text(transcript)
    ledger_fields = [
        "报告ID", "发布日期", "观察窗", "材料类型", "原始类型", "报告名称", "作者", "资料角色", "项目分类",
        "中国关联层级", "科技关联层级", "主题标签", "筛选依据", "官方落地页", "官方PDF", "页面来源",
        "本地原始资产", "本地文本", "本地切片或转写", "字节数", "SHA256", "PDF页数", "提取文本字符数",
        "本地状态", "错误", "获取日期",
    ]
    write_csv(ledger_path, ledger_rows, ledger_fields)
    existing_nbr_catalog = [row for row in catalog if row["报告ID"].startswith("C-NBR-")]
    complete_nbr_catalog = merge_nbr_catalog_rows(existing_nbr_catalog, nbr_catalog, ordered_ids)
    merged_catalog = replace_institution_catalog_rows(catalog, complete_nbr_catalog, "C-NBR-")
    merged_catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(root / "05_报告总目录.csv", merged_catalog, CATALOG_FIELDS)

    theme_rows = [
        {"主题标签": theme, "中国关联层级": row["中国关联层级"], "科技关联层级": row["科技关联层级"],
         "报告ID": row["报告ID"], "发布日期": row["发布日期"], "观察窗": row["观察窗"], "材料类型": row["材料类型"],
         "报告名称": row["报告名称"], "资料角色": row["资料角色"], "本地原始资产": row["本地原始资产"],
         "本地文本": row["本地文本"], "官方落地页": row["官方落地页"]}
        for row in ledger_rows for theme in row["主题标签"].split("；")
    ]
    theme_fields = ["主题标签", "中国关联层级", "科技关联层级", "报告ID", "发布日期", "观察窗", "材料类型", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页"]
    write_csv(root / "41_NBR科技与中国主题索引.csv", theme_rows, theme_fields)
    matrix_counts = Counter((row["主题标签"], row["中国关联层级"], row["观察窗"], row["材料类型"]) for row in theme_rows)
    matrix_rows = [
        {"主题标签": key[0], "中国关联层级": key[1], "观察窗": key[2], "材料类型": key[3], "材料数": str(value)}
        for key, value in sorted(matrix_counts.items())
    ]
    write_csv(root / "42_NBR科技与中国复用矩阵.csv", matrix_rows, ["主题标签", "中国关联层级", "观察窗", "材料类型", "材料数"])

    status_counts = Counter(row["本地状态"] for row in ledger_rows)
    type_counts = Counter(row["材料类型"] for row in ledger_rows)
    china_counts = Counter(row["中国关联层级"] for row in ledger_rows)
    lines = [
        "# NBR近十年科技与中国专题库增补结果", "", f"- 纳入材料：{len(ledger_rows)}项。",
        f"- 直接涉华科技：{china_counts['直接涉华科技']}项；含中国比较的印太技术材料：{china_counts['含中国比较的印太技术材料']}项；区域技术基线：{china_counts['区域技术基线']}项。",
        f"- NBR研究报告：{type_counts['NBR研究报告']}项；政策简报：{type_counts['NBR政策简报']}项；评论：{type_counts['NBR评论']}项；访谈：{type_counts['NBR访谈']}项。",
        f"- 官方PDF保存或关联：{status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']}项。",
        f"- 官方网页全文保存：{status_counts['官方网页全文已保存']}项；官方页面代理全文保存：{status_counts['官方页面代理全文已保存']}项；获取失败：{status_counts['获取失败']}项。",
        f"- PDF物理页数：{sum(int(row['PDF页数']) for row in ledger_rows):,}。", f"- 报告总目录：{len(catalog)}项扩展至{len(merged_catalog)}项。", "",
        "## 纳入边界", "", "以NBR Technology and Geoeconomic Affairs项目官方出版物目录为入口，限定2016年1月1日至2026年8月22日，排除活动、播客及播客系列。报告、简报、评论、访谈、背景材料、圆桌论文、证词和论文均保留，并区分核心科技直接材料与科技地缘经济基线。另补入2017—2021年IP Commission六项官方更新附件。", "",
        "## 中国关联分层", "", "标题或官方分类直接出现China、PRC、Huawei等对象的材料标记为直接涉华；全文存在持续中国比较的材料标记为含中国比较的印太技术材料；其余材料保留为区域技术基线，便于后续项目进行同类国家和区域政策对照。", "",
        "## 资料角色边界", "", "报告、简报、背景材料和圆桌论文按作者或项目正式研究处理；评论和论文按作者观点处理；访谈和证词分别按受访者或证词作者处理。各类材料均不自动上升为NBR统一机构观点。", "",
        "## 跨项目调用", "", "优先从`41_NBR科技与中国主题索引.csv`按中国关联层级、科技关联层级、主题和观察窗筛选，再回到本地逐页文本或网页转写。`42_NBR科技与中国复用矩阵.csv`用于比较主题、时间窗、材料类型和中国关联结构。", "",
    ]
    failed = [row for row in ledger_rows if row["本地状态"] == "获取失败"]
    if failed:
        lines.extend(["## 未完成项", ""] + [f"- `{row['报告ID']}`：{row['错误']}" for row in failed] + [""])
    (root / "40_NBR科技与中国专题增补结果.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"candidates={len(candidates)} pdf={status_counts['官方PDF已保存并校验'] + status_counts['关联既有官方PDF']} web={status_counts['官方网页全文已保存']} proxy={status_counts['官方页面代理全文已保存']} failed={status_counts['获取失败']} catalog={len(merged_catalog)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
