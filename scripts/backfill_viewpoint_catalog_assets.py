from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
import ssl
import time
from http.client import IncompleteRead, InvalidURL
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
PDF_RE = re.compile(r"https?://[^\s\"'<>]+?\.pdf(?:\?[^\s\"'<>]*)?", re.I)
HREF_PDF_RE = re.compile(r"href=[\"']([^\"']+?\.pdf(?:\?[^\"']*)?)[\"']", re.I)
STEPI_DOWNLOAD_RE = re.compile(
    r'href="([^"]*?/common/report/Download\.do\?[^\"]*?reIdx\s*=\s*(\d+)[^\"]*?)"',
    re.I | re.S,
)
DIRECT_OVERRIDES: dict[str, str] = {}
OFFICIAL_PDF_OVERRIDES = {
    "C-OECD-DOI-7CC876F7-EN": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/08/optimising-the-operation-and-use-of-national-research-infrastructures_fcf87118/7cc876f7-en.pdf",
    "C-OECD-DOI-0002217C-EN": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/05/an-industrial-policy-framework-for-oecd-countries_233e3061/0002217c-en.pdf",
    "C-OECD-DOI-154981D7-EN": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/12/identifying-and-characterising-ai-adopters_adad5b31/154981d7-en.pdf",
    "C-OECD-DOI-EBC2DEBE-EN": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2026/01/digital-technology-diffusion-in-the-age-of-ai_7f11be5d/ebc2debe-en.pdf",
    "C-STANFORD-HAI-AI-INDEX-2019": "https://hai.stanford.edu/assets/files/ai_index_2019_report.pdf",
    "C-STANFORD-HAI-WHITE-PAPER-BUILDING-NATIONAL-AI-RESEARCH-RESOURCE": "https://hai.stanford.edu/sites/default/files/2021-10/HAI_NRCR_2021_0.pdf",
}


def load_light_catalog_overrides(root: Path) -> dict[str, str]:
    """Reuse official attachment URLs already verified in lightweight ledgers."""
    overrides: dict[str, str] = {}
    for name in (
        "64_KISTEP韩文正式报告总目录与重点附件台账.csv",
        "75_CSET_2023-2024正式报告轻量目录.csv",
        "82_ITIF科学技术创新节点轻量目录.csv",
        "84_Fraunhofer_ISI创新系统政策分析轻量目录.csv",
        "86_Stanford_HAI科学技术创新轻量目录.csv",
        "88_美国OSTP科学技术创新政策轻量目录.csv",
    ):
        path = root / name
        if not path.exists():
            continue
        for row in read_csv(path):
            report_id = row.get("统一目录报告ID") or row.get("报告ID", "")
            direct = row.get("官方PDF入口") or row.get("官方附件") or ""
            if report_id and direct:
                overrides[report_id] = direct
    return overrides


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request(url: str, *, referer: str = "", timeout: int = 45) -> tuple[bytes, str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf,text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if referer:
        headers["Referer"] = referer
    context = ssl.create_default_context()
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout, context=context) as response:
                data = response.read(120 * 1024 * 1024)
                return data, response.geturl(), response.headers.get("Content-Type", "")
        except (IncompleteRead, URLError, TimeoutError, ssl.SSLError) as exc:
            last_error = exc
            time.sleep(0.8 * (attempt + 1))
    assert last_error is not None
    raise last_error


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href = ""
        self._text: list[str] = []
        self.text: list[str] = []
        self._ignored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._ignored += 1
        if tag.lower() == "a" and values.get("href"):
            self._href = values["href"]
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            self.links.append((self._href, " ".join(self._text).strip()))
            self._href = ""
            self._text = []
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._ignored:
            self._ignored -= 1

    def handle_data(self, data: str) -> None:
        value = re.sub(r"\s+", " ", data).strip()
        if not value:
            return
        if self._href:
            self._text.append(value)
        if not self._ignored:
            self.text.append(value)


def title_tokens(title: str) -> set[str]:
    stop = {"the", "and", "for", "with", "from", "into", "that", "this", "report", "research"}
    return {word for word in re.findall(r"[a-z0-9]{4,}", title.lower()) if word not in stop}


def pdf_candidates(page_url: str, raw: bytes, title: str) -> list[str]:
    source = raw.decode("utf-8", errors="replace")
    for escaped, value in {
        "\\u0022": '"', "\\u0026": "&", "\\u003c": "<", "\\u003e": ">",
        "\\u002F": "/", "\\u002f": "/",
    }.items():
        source = source.replace(escaped, value)
    parser = LinkParser()
    parser.feed(source)
    tokens = title_tokens(title)
    ranked: list[tuple[int, str]] = []
    seen: set[str] = set()

    def add(href: str, label: str = "") -> None:
        href = html.unescape(href).replace("\\/", "/")
        if re.search(r"[\x00-\x20|]", href):
            return
        url = urljoin(page_url, href)
        if url in seen or not url.lower().startswith(("http://", "https://")):
            return
        if ".pdf" not in url.lower():
            return
        seen.add(url)
        haystack = f"{url} {label}".lower()
        token_hits = sum(token in haystack for token in tokens)
        label_lower = label.lower().strip()
        explicit_download = (
            "download" in label_lower
            or ("pdf" in label_lower and not label_lower.startswith(("http://", "https://")))
            or label_lower in {"full report", "research report", "report"}
        )
        if not explicit_download and token_hits < 2:
            return
        score = 20 if explicit_download else 0
        score += 5 * token_hits
        if "summary" in haystack or "brief" in haystack:
            score -= 2
        ranked.append((score, url))

    for href, label in parser.links:
        add(href, label)
    for match in PDF_RE.findall(source.replace("\\/", "/")):
        add(match)
    for match in HREF_PDF_RE.findall(source.replace("\\/", "/")):
        add(match, "embedded PDF")
    ranked.sort(key=lambda item: (-item[0], len(item[1])))
    return [url for _, url in ranked[:16]]


def clean_page_text(raw: bytes) -> str:
    parser = LinkParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return "\n".join(parser.text)


def load_stepi_downloads() -> dict[str, str]:
    downloads: dict[str, str] = {}
    base = "https://www.stepi.re.kr"
    for page in range(1, 5):
        url = f"{base}/site/stepien/ex/bbs/List.do?cbIdx=1303&searchSort=REG_DT&pageIndex={page}"
        raw, _, _ = request(url)
        source = raw.decode("utf-8", errors="replace")
        for href, re_idx in STEPI_DOWNLOAD_RE.findall(source):
            href = html.unescape(re.sub(r"\s+", "", href))
            downloads[re_idx] = urljoin(base, href)
    return downloads


@dataclass
class Result:
    report_id: str
    landing_url: str
    final_landing_url: str = ""
    download_url: str = ""
    pdf_data: bytes = b""
    html_data: bytes = b""
    page_text: str = ""
    status: str = ""
    error: str = ""


def acquire(row: dict[str, str]) -> Result:
    report_id = row["报告ID"]
    landing = row["原文链接"]
    result = Result(report_id=report_id, landing_url=landing)
    try:
        direct = DIRECT_OVERRIDES.get(report_id, "")
        if direct:
            data, pdf_url, _ = request(direct, referer=landing)
            if data.startswith(b"%PDF"):
                result.final_landing_url = landing
                result.download_url = pdf_url
                result.pdf_data = data
                result.status = "官方PDF已获取"
                return result
        raw, final_url, content_type = request(landing)
        result.final_landing_url = final_url
        if raw.startswith(b"%PDF"):
            result.download_url = final_url
            result.pdf_data = raw
            result.status = "官方PDF已获取"
            return result
        if "html" not in content_type.lower() and b"<html" not in raw[:4096].lower():
            result.status = "落地页非HTML且非PDF"
            return result
        result.html_data = raw
        result.page_text = clean_page_text(raw)
        candidates = pdf_candidates(final_url, raw, row["报告名称"])
        errors: list[str] = []
        for candidate in candidates:
            try:
                data, pdf_url, _ = request(candidate, referer=final_url)
                if data.startswith(b"%PDF"):
                    result.download_url = pdf_url
                    result.pdf_data = data
                    result.status = "官方PDF已获取"
                    return result
                errors.append(f"非PDF:{candidate}")
            except (HTTPError, URLError, TimeoutError, ssl.SSLError, IncompleteRead, InvalidURL, ValueError) as exc:
                errors.append(f"{type(exc).__name__}:{candidate}")
        result.status = "无独立PDF，已保存官方网页"
        result.error = " | ".join(errors[:5])
        return result
    except (HTTPError, URLError, TimeoutError, ssl.SSLError, IncompleteRead, InvalidURL, ValueError) as exc:
        result.status = "获取失败"
        result.error = f"{type(exc).__name__}: {exc}"
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--roles", default="本地近期候选")
    parser.add_argument("--priority", default="")
    parser.add_argument("--ids", default="", help="comma-separated report IDs; overrides role selection")
    parser.add_argument("--retry-web", action="store_true")
    parser.add_argument("--reset-ids", default="")
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    DIRECT_OVERRIDES.update(OFFICIAL_PDF_OVERRIDES)
    DIRECT_OVERRIDES.update(load_light_catalog_overrides(root))
    roles = {value.strip() for value in args.roles.split(",") if value.strip()}
    selected_ids = {value.strip() for value in args.ids.split(",") if value.strip()}
    for row in catalog:
        row.setdefault("本地原始资产路径", "")
        row.setdefault("原始资产状态", "")
    reset_ids = {value.strip() for value in args.reset_ids.split(",") if value.strip()}
    for row in catalog:
        if row["报告ID"] in reset_ids:
            row["本地原始资产路径"] = ""
            row["原始资产状态"] = ""
    targets = []
    for row in catalog:
        if selected_ids and row["报告ID"] not in selected_ids:
            continue
        if not selected_ids and row["样本角色"] not in roles:
            continue
        missing = not row["本地原始资产路径"]
        web_only = row["原始资产状态"].startswith("无独立PDF")
        if missing or (args.retry_web and web_only):
            targets.append(row)
    if selected_ids:
        missing_ids = selected_ids - {row["报告ID"] for row in targets} - {
            row["报告ID"] for row in catalog if row["报告ID"] in selected_ids and row["本地原始资产路径"]
        }
        if missing_ids:
            raise ValueError(f"selected report IDs missing from catalog: {sorted(missing_ids)}")
    if any(row["机构ID"] == "stepi" for row in targets):
        stepi_downloads = load_stepi_downloads()
        for row in targets:
            if row["机构ID"] != "stepi":
                continue
            match = re.search(r"[?&]reIdx=(\d+)", row["原文链接"])
            if match and match.group(1) in stepi_downloads:
                DIRECT_OVERRIDES[row["报告ID"]] = stepi_downloads[match.group(1)]
    if args.priority:
        priorities = {value.strip() for value in args.priority.split(",") if value.strip()}
        targets = [row for row in targets if row["优先级"] in priorities]

    pdf_dir = root / "03_证据底稿" / "原文PDF"
    html_dir = root / "03_证据底稿" / "网页快照"
    web_text_dir = root / "03_证据底稿" / "网页文本"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    web_text_dir.mkdir(parents=True, exist_ok=True)

    known_hashes: dict[str, Path] = {}
    for path in pdf_dir.glob("*.pdf"):
        known_hashes[digest(path.read_bytes())] = path

    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(acquire, row): row for row in targets}
        for index, future in enumerate(as_completed(futures), start=1):
            try:
                result = future.result()
            except Exception as exc:  # one malformed response must not abort the batch
                result = Result(
                    report_id=futures[future]["报告ID"],
                    landing_url=futures[future]["原文链接"],
                    status="获取失败",
                    error=f"{type(exc).__name__}: {exc}",
                )
            results.append(result)
            print(f"[{index}/{len(futures)}] {result.report_id} {result.status}", flush=True)
            time.sleep(0.02)

    result_by_id = {result.report_id: result for result in results}
    output: list[dict[str, str]] = []
    today = date.today().isoformat()
    for row in catalog:
        result = result_by_id.get(row["报告ID"])
        if not result:
            continue
        local_path = ""
        byte_count = 0
        sha256 = ""
        if result.pdf_data:
            sha256 = digest(result.pdf_data)
            if sha256 in known_hashes:
                path = known_hashes[sha256]
                result.status = "官方PDF与既有资产重复，已关联"
            else:
                path = pdf_dir / f"{result.report_id}.pdf"
                path.write_bytes(result.pdf_data)
                known_hashes[sha256] = path
            local_path = str(path)
            byte_count = path.stat().st_size
            row["本地原始资产路径"] = local_path
            row["原始资产状态"] = result.status
        elif result.html_data:
            html_path = html_dir / f"{result.report_id}.html"
            text_path = web_text_dir / f"{result.report_id}.txt"
            html_path.write_bytes(result.html_data)
            text_path.write_text(result.page_text, encoding="utf-8")
            local_path = str(text_path)
            byte_count = html_path.stat().st_size
            sha256 = digest(result.html_data)
            row["本地原始资产路径"] = local_path
            row["原始资产状态"] = result.status
        output.append({
            "报告ID": result.report_id,
            "机构ID": row["机构ID"],
            "发布日期": row["发布日期"],
            "报告名称": row["报告名称"],
            "官方落地页": result.landing_url,
            "最终落地页": result.final_landing_url,
            "直接下载地址": result.download_url,
            "本地资产": local_path,
            "资产类型": "PDF" if result.pdf_data else ("官方网页" if result.html_data else ""),
            "字节数": str(byte_count),
            "SHA256": sha256,
            "本地状态": result.status,
            "错误或限制": result.error,
            "获取日期": today,
        })

    write_csv(catalog_path, catalog, list(catalog[0]))
    fields = list(output[0]) if output else [
        "报告ID", "机构ID", "发布日期", "报告名称", "官方落地页", "最终落地页",
        "直接下载地址", "本地资产", "资产类型", "字节数", "SHA256", "本地状态", "错误或限制", "获取日期",
    ]
    log_path = root / "21_非锚点全文补存台账.csv"
    previous = read_csv(log_path) if log_path.exists() else []
    merged = {row["报告ID"]: row for row in previous}
    merged.update({row["报告ID"]: row for row in output})
    ordered = [merged[row["报告ID"]] for row in catalog if row["报告ID"] in merged]
    write_csv(log_path, ordered, fields)
    print(f"targets={len(targets)} pdf={sum(bool(r.pdf_data) for r in results)} html={sum(bool(r.html_data) and not r.pdf_data for r in results)} failed={sum(not r.pdf_data and not r.html_data for r in results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
