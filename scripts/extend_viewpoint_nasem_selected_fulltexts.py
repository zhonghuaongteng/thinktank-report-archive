from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import html as html_module
import re
import time
import tempfile
from datetime import date
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


def _item(record_id: int, title: str, axes: str, role: str) -> tuple[int, str, str, str]:
    return record_id, title, axes, role


SELECTED = (
    _item(21824, "Optimizing the Nation's Investment in Academic Research", "科学体系与基础研究；创新政策与研发治理；人才大学与科研组织", "联邦资助、大学成本与科研监管如何共同塑造学术研究能力"),
    _item(24905, "Returns to Federal Investments in the Innovation System", "科学体系与基础研究；创新政策与研发治理；产业创新转化与区域生态", "公共科研投入经知识、人才与技术扩散形成创新回报"),
    _item(23472, "Building America's Skilled Technical Workforce", "人才大学与科研组织；产业创新转化与区域生态", "中等技能技术人才形成、认证与雇主协同机制"),
    _item(25116, "Open Science by Design", "科学体系与基础研究；创新政策与研发治理；国际合作开放科学与比较", "开放科学由自发共享转向基础设施、激励和规范的系统设计"),
    _item(25303, "Reproducibility and Replicability in Science", "科学体系与基础研究；创新政策与研发治理；人才大学与科研组织", "科研质量、数据方法透明度与机构责任机制"),
    _item(25384, "Adapting to the 21st Century Innovation Environment", "创新政策与研发治理；产业创新转化与区域生态；国际合作开放科学与比较", "创新环境变化对政策工具、合作关系与技术商业化的影响"),
    _item(25729, "A Quadrennial Review of the National Nanotechnology Initiative", "科学体系与基础研究；技术创新与关键技术；产业创新转化与区域生态", "国家纳米技术计划的跨机构研发、基础设施和转化机制"),
    _item(26006, "Advancing Commercialization of Digital Products from Federal Laboratories", "技术创新与关键技术；创新政策与研发治理；产业创新转化与区域生态", "联邦实验室数字成果的知识产权、许可与商业化障碍"),
    _item(26290, "Strengthening U.S. Science and Technology Leadership through Global Cooperation and Partnerships", "科学体系与基础研究；人才大学与科研组织；国际合作开放科学与比较", "全球合作、科研人才与开放网络对科技领导力的作用"),
    _item(26830, "Enhancing U.S. Science and Innovation with Novel Cross-Sector Partnerships", "科学体系与基础研究；创新政策与研发治理；产业创新转化与区域生态", "政府、大学、企业和公益资本的新型跨部门合作机制"),
    _item(26647, "Protecting U.S. Technological Advantage", "技术创新与关键技术；人才大学与科研组织；产业创新转化与区域生态；国际合作开放科学与比较；中国科技横向维度", "安全语境下仍以扩大创新生态、科研人才和共享技术平台能力为核心，并提供中国技术体系比较"),
    _item(27042, "Developing Human Capital to Support U.S. Innovation Capacity", "人才大学与科研组织；创新政策与研发治理；产业创新转化与区域生态", "教育、技能、移民与职业路径如何支撑国家创新能力"),
    _item(27091, "Openness, International Engagement, and the Federally Funded Science and Technology Research Enterprise", "科学体系与基础研究；创新政策与研发治理；国际合作开放科学与比较；中国科技横向维度", "科研开放与风险管理如何共同作用于联邦资助研究体系"),
    _item(27190, "Strategic Innovation and Commercialization: Supporting IP and Tech Transfer to Advance U.S. Research Competitiveness", "创新政策与研发治理；产业创新转化与区域生态", "知识产权和技术转移制度对科研竞争力与成果扩散的作用"),
    _item(27787, "International Talent Programs in the Changing Global Environment", "人才大学与科研组织；国际合作开放科学与比较；中国科技横向维度", "国际人才计划、研究人员流动和中国科研合作的证据边界"),
    _item(27873, "Impacts of National Science Foundation Engineering Research Support on Society", "科学体系与基础研究；技术创新与关键技术；产业创新转化与区域生态", "NSF工程研究资助如何产生技术、企业、人才与社会影响"),
    _item(29212, "Foundation Models for Scientific Discovery and Innovation", "科学体系与基础研究；技术创新与关键技术；创新政策与研发治理", "基础模型进入科学发现的科研基础设施、评测与组织条件"),
    _item(29063, "Quadrennial Review of the National Nanotechnology Initiative (2025)", "科学体系与基础研究；技术创新与关键技术；人才大学与科研组织；产业创新转化与区域生态", "纳米技术计划由研发网络转向共享设施、人才与产业扩散的近期节点"),
)
SELECTED_IDS = tuple(f"C-US-NASEM-{item[0]}" for item in SELECTED)


def discover_chapter_urls(page_html: str, record_id: int) -> list[str]:
    soup = BeautifulSoup(page_html, "html.parser")
    pattern = re.compile(rf"/read/{record_id}/chapter/(\d+)(?:$|[?#])")
    found: dict[int, str] = {1: f"https://www.nationalacademies.org/read/{record_id}/chapter/1"}
    for link in soup.find_all("a", href=True):
        href = urljoin("https://www.nationalacademies.org", str(link["href"]))
        match = pattern.search(href)
        if match:
            found[int(match.group(1))] = href.split("#", 1)[0].split("?", 1)[0]
    return [found[number] for number in sorted(found)]


def discover_chapter_count_from_markdown(markdown: str, record_id: int) -> int:
    matches = re.findall(rf"https://www\.nationalacademies\.org/read/{record_id}/chapter/(\d+)", markdown)
    if not matches:
        return 0
    return max(int(number) for number in matches)


def count_archived_chapters(archive: str) -> int:
    markdown_count = len(re.findall(r"<!-- source: ", archive))
    if markdown_count:
        return markdown_count
    return len(re.findall(r'<section data-source="', archive))


def same_chapter_content(left: str, right: str) -> bool:
    left_normalized = re.sub(r"\s+", " ", left).strip()[:50000]
    right_normalized = re.sub(r"\s+", " ", right).strip()[:50000]
    if not left_normalized or not right_normalized:
        return left_normalized == right_normalized
    return difflib.SequenceMatcher(None, left_normalized, right_normalized, autojunk=True).ratio() >= 0.985


def normalize_archive_whitespace(content: str) -> str:
    """Keep fetched content stable while removing line-end padding."""
    return "\n".join(line.rstrip() for line in content.splitlines()).rstrip() + "\n"


def extract_main_text(page_html: str) -> str:
    soup = BeautifulSoup(page_html, "html.parser")
    main = soup.find("main") or soup.body or soup
    for element in main.select("script,style,form,nav,footer,button,svg"):
        element.decompose()
    return re.sub(r"\n{3,}", "\n\n", main.get_text("\n", strip=True)).strip()


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 Codex research archive"})
    for attempt in range(6):
        try:
            with urlopen(request, timeout=120) as response:
                content = response.read().decode("utf-8", errors="replace")
            time.sleep(3.0)
            return content
        except HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            retry_after = float((exc.headers or {}).get("Retry-After", 0) or 0)
            time.sleep(max(retry_after, min(180.0, 30.0 * (attempt + 1))))
    raise RuntimeError(f"unreachable fetch retry state: {url}")


def fetch_book(record_id: int, title: str, cache_root: Path | None = None) -> tuple[str, str, int]:
    cache_root = cache_root or (Path(tempfile.gettempdir()) / "codex_nasem_chapter_cache")
    record_cache = cache_root / str(record_id)
    record_cache.mkdir(parents=True, exist_ok=True)
    first_url = f"https://www.nationalacademies.org/read/{record_id}/chapter/1"
    first_cache = record_cache / "chapter-1.html"
    if first_cache.exists():
        first_html = first_cache.read_text(encoding="utf-8")
    else:
        first_html = fetch_html(first_url)
        first_cache.write_text(first_html, encoding="utf-8", newline="\n")
    urls = discover_chapter_urls(first_html, record_id)
    pages = [first_html]
    for url in urls[1:]:
        chapter = int(re.search(r"/chapter/(\d+)", url).group(1))
        cache_path = record_cache / f"chapter-{chapter}.html"
        if cache_path.exists():
            pages.append(cache_path.read_text(encoding="utf-8"))
        else:
            page_html = fetch_html(url)
            cache_path.write_text(page_html, encoding="utf-8", newline="\n")
            pages.append(page_html)
    sections: list[str] = []
    texts: list[str] = []
    for url, page_html in zip(urls, pages):
        soup = BeautifulSoup(page_html, "html.parser")
        main = soup.find("main") or soup.body or soup
        sections.append(f'<section data-source="{html_module.escape(url)}">{str(main)}</section>')
        texts.append(extract_main_text(page_html))
    archive = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>"
        + html_module.escape(title) + "</title></head><body>" + "\n".join(sections) + "</body></html>\n"
    )
    text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(texts)).strip() + "\n"
    return archive, text, len(urls)


def fetch_jina_markdown(official_url: str) -> str:
    request = Request(f"https://r.jina.ai/{official_url}", headers={"User-Agent": "Mozilla/5.0 Codex research archive"})
    for attempt in range(6):
        try:
            with urlopen(request, timeout=180) as response:
                content = response.read().decode("utf-8", errors="replace")
            time.sleep(3.1)
            return content
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 5:
                raise
            retry_after = float((exc.headers or {}).get("Retry-After", 0) or 0)
            base = 20.0 if exc.code == 429 else 5.0
            time.sleep(max(retry_after, min(120.0, base * (attempt + 1))))
    raise RuntimeError(f"unreachable Jina retry state: {official_url}")


def fetch_book_via_jina(record_id: int, title: str, cache_root: Path | None = None) -> tuple[str, str, int]:
    cache_root = cache_root or (Path(tempfile.gettempdir()) / "codex_nasem_jina_cache")
    record_cache = cache_root / str(record_id)
    record_cache.mkdir(parents=True, exist_ok=True)
    chapters: list[str] = []
    seen_bodies: list[str] = []
    for chapter in range(1, 61):
        cache_path = record_cache / f"chapter-{chapter}.md"
        if cache_path.exists():
            content = cache_path.read_text(encoding="utf-8")
        else:
            url = f"https://www.nationalacademies.org/read/{record_id}/chapter/{chapter}"
            content = fetch_jina_markdown(url)
            cache_path.write_text(content, encoding="utf-8", newline="\n")
        body = content.split("Markdown Content:", 1)[-1].strip()
        if chapter > 1 and any(same_chapter_content(body, previous) for previous in seen_bodies):
            break
        if len(body) < 1000 or re.search(r"page not found|could not be found|404 error", body[:2000], re.I):
            break
        seen_bodies.append(body)
        chapters.append(content)
    else:
        raise RuntimeError(f"NASEM chapter probe exceeded safety ceiling: {record_id}")
    chapter_count = len(chapters)
    if chapter_count < 1:
        raise RuntimeError(f"could not collect NASEM chapters: {record_id}")
    sections: list[str] = []
    cleaned: list[str] = []
    for chapter, content in enumerate(chapters, 1):
        source = f"https://www.nationalacademies.org/read/{record_id}/chapter/{chapter}"
        body = content.split("Markdown Content:", 1)[-1].strip()
        sections.append(f"<!-- source: {source} -->\n\n## 官方在线阅读第{chapter}章\n\n{body}")
        plain = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
        plain = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", plain)
        cleaned.append(plain)
    archive = f"# {title}\n\n<!-- collection-complete: chapter-probe-v2 -->\n\n- 转换说明：以下内容由Jina从NASEM官方在线阅读页转换为Markdown；每章保留官方来源URL。\n\n" + "\n\n".join(sections) + "\n"
    text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(cleaned)).strip() + "\n"
    return archive, text, chapter_count


def selected_slice(title: str, text: str) -> str:
    keywords = (
        "science", "scientific", "research", "technology", "innovation", "engineering", "r&d", "funding",
        "laboratory", "university", "workforce", "talent", "commercial", "transfer", "intellectual property",
        "open science", "reproducib", "international", "cooperation", "partnership", "china", "chinese",
        "artificial intelligence", "foundation model", "nanotechnology",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 70]
    hits = [part for part in paragraphs if any(keyword in part.lower() for keyword in keywords)][:280]
    return f"# {title}\n\n- 证据类型：NASEM官方在线全文的科学技术创新定向摘录\n\n## 科学技术创新定向摘录\n\n" + "\n\n".join(hits) + "\n"


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Save selected NASEM science and technology innovation online full texts.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "206_NASEM科学技术创新政策近十年轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light, light_fields = read_csv(light_path)
    catalog, catalog_fields = read_csv(catalog_path)
    light_by_id = {row["报告ID"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    missing = sorted(set(SELECTED_IDS) - set(light_by_id))
    if missing:
        raise RuntimeError(f"selected NASEM metadata missing: {missing}")
    html_dir = root / "03_证据底稿" / "网页原文"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (html_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    ledger: list[dict[str, str]] = []
    for index, (record_id, title, axes, role) in enumerate(SELECTED, 1):
        rid = f"C-US-NASEM-{record_id}"
        source = light_by_id[rid]
        if source["报告名称"] != title:
            raise RuntimeError(f"NASEM metadata drift: {rid} {source['报告名称']!r}")
        html_path = html_dir / f"{rid}.md"
        text_path = text_dir / f"{rid}.txt"
        slice_path = slice_dir / f"{rid}.md"
        if html_path.exists() and text_path.exists() and "collection-complete: chapter-probe-v2" in html_path.read_text(encoding="utf-8"):
            archive = html_path.read_text(encoding="utf-8")
            text = text_path.read_text(encoding="utf-8")
            chapter_count = count_archived_chapters(archive)
        else:
            archive, text, chapter_count = fetch_book_via_jina(record_id, title)
        archive = normalize_archive_whitespace(archive)
        text = normalize_archive_whitespace(text)
        html_path.write_text(archive, encoding="utf-8", newline="\n")
        text_path.write_text(text, encoding="utf-8", newline="\n")
        if len(text) < 5000 or chapter_count < 1:
            raise RuntimeError(f"NASEM online full text incomplete: {rid} chapters={chapter_count} chars={len(text)}")
        slice_path.write_text(normalize_archive_whitespace(selected_slice(title, text)), encoding="utf-8", newline="\n")
        lower = text.lower()
        china_hits = lower.count("china") + lower.count("chinese") + lower.count("sino-")
        if china_hits:
            source["中国直接信号"] = "是（全文核验）"
        source["全文策略"] = "已进入精选全文；保存官方逐章网页合并档、全文文本和科技创新切片"
        row = catalog_by_id[rid]
        row["本地路径"] = str(text_path)
        row["正文完整度"] = "NASEM官方在线全文逐章经Jina转换为Markdown并提取文本；精确引用回查官方章节与印刷页码"
        row["优先级"] = "P1-STI-node"
        row["样本角色"] = "NASEM科学技术创新机制与中国比较跨期精选全文"
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = role
        row["本地原始资产路径"] = str(html_path)
        row["原始资产状态"] = "NASEM官方在线全文已逐章转换保存并校验；非原始PDF"
        data = archive.encode("utf-8")
        ledger.append({
            "报告ID": rid, "发布日期": source["发布日期"], "报告名称": title, "DOI": source["DOI"],
            "官方落地页": source["官方落地页"], "官方在线全文入口": source["官方在线全文入口"],
            "本地网页转写": str(html_path), "本地文本": str(text_path), "本地切片": str(slice_path),
            "章节数": str(chapter_count), "网页归档字节数": str(len(data)), "清洗文本字符数": str(len(text)),
            "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(data).hexdigest(),
            "科技创新主轴": axes, "科技创新复用角色": role,
            "选择理由": "跨期科研制度、技术路线、人才、转化、开放科学或中国比较机制节点；安全语境仅保留一项经正文机制核验材料",
            "获取日期": date.today().isoformat(),
        })
        print(f"nasem_selected={index}/{len(SELECTED)} id={rid} chapters={chapter_count} chars={len(text)}", flush=True)
    selected_ids = set(SELECTED_IDS)
    for row in catalog:
        if row.get("机构ID") == "us-nasem" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            row["原始资产状态"] = "NASEM跨期精选已完成；其余主题成果保留轻量目录和官方在线全文入口"
    write_csv(light_path, light, light_fields)
    write_csv(catalog_path, sorted(catalog, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", ""))), catalog_fields)
    light_counts = {key: sum(row["科技创新相关度"] == key for row in light) for key in ("核心", "支撑", "语境")}
    light_china = sum(row["中国直接信号"].startswith("是") for row in light)
    (root / "207_NASEM科学技术创新政策近十年轻量总目录结果.md").write_text(
        "# NASEM科学技术创新政策近十年轻量总目录结果\n\n"
        f"- Crossref官方注册元数据显示10.17226前缀在观察期共有3,918项成果；经科技创新政策主题与正式报告文类筛选，保留{len(light)}项：核心{light_counts['核心']}项、支撑{light_counts['支撑']}项、语境{light_counts['语境']}项。\n"
        f"- 精选全文核验后，中国直接信号增至{light_china}项；词形只用于定位，具体中国证据须回查官方章节。\n"
        "- 交通工程项目报告、临床专题和单篇章节不因宽泛research词进入目录；安全与国防主导标题仅保留语境级，不自动触发全文。\n",
        encoding="utf-8",
    )
    ledger_path = root / "208_NASEM科学技术创新机制与中国比较跨期精选全文台账.csv"
    result_path = root / "209_NASEM科学技术创新机制与中国比较跨期精选全文结果.md"
    write_csv(ledger_path, ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("章节数", "网页归档字节数", "清洗文本字符数", "China词形命中数")}
    china_docs = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    result_path.write_text(
        "# NASEM科学技术创新机制与中国比较跨期精选全文结果\n\n"
        f"- 从科技创新主题目录中选择{len(ledger)}项官方在线全文，共{totals['章节数']:,}个章节、网页Markdown转写{totals['网页归档字节数']:,}字节、提取文本{totals['清洗文本字符数']:,}字符。\n"
        f"- {china_docs}项全文出现China、Chinese或Sino-词形，共{totals['China词形命中数']:,}次；中国相关性须回到具体章节判断，不能由词频直接推导立场。\n"
        "- 证据链覆盖公共科研投入、创新回报、技术人才、开放科学、可重复性、国家技术计划、联邦实验室商业化、全球合作、跨部门伙伴关系、国际人才和AI辅助科学发现。\n"
        "- 安全语境材料仅保留《Protecting U.S. Technological Advantage》一项，其入选依据是正文对创新生态、人才、共享技术平台和中国技术体系的机制分析。网页资产为Jina对NASEM官方逐章页面的Markdown转换，保留每章官方URL，不冒充原始PDF。\n",
        encoding="utf-8",
    )
    print(f"nasem_selected_total={len(ledger)} chapters={totals['章节数']} chars={totals['清洗文本字符数']} china_docs={china_docs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
