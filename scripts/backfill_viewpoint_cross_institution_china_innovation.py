from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from pypdf import PdfReader

try:
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from scripts.extend_viewpoint_eu_stoa_selected_fulltexts import _eval, browser_pdf
except ModuleNotFoundError:
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from extend_viewpoint_eu_stoa_selected_fulltexts import _eval, browser_pdf


SERIES_ROLE = "跨机构中国科技创新机制定点全文"


def _item(
    report_id: str,
    institution_id: str,
    institution: str,
    published: str,
    title: str,
    landing_url: str,
    asset_url: str,
    asset_type: str,
    axes: tuple[str, ...],
    role: str,
) -> dict[str, object]:
    return {
        "id": report_id,
        "institution_id": institution_id,
        "institution": institution,
        "date": published,
        "title": title,
        "landing_url": landing_url,
        "asset_url": asset_url,
        "asset_type": asset_type,
        "axes": axes,
        "role": role,
    }


SELECTED_ITEMS = (
    _item(
        "C-LIGHT-MERICS-2018-CHINAS-WAY-INNOVATION-SUPERPOWER",
        "merics",
        "Mercator Institute for China Studies",
        "2018-03-27",
        "China’s way to an innovation superpower",
        "https://merics.org/en/comment/chinas-way-innovation-superpower",
        "https://merics.org/en/comment/chinas-way-innovation-superpower",
        "web",
        ("科学体系与科研能力", "研发投入与创新政策", "关键与新兴技术", "科技人才与技能", "产业创新与成果转化", "国际合作与中国比较"),
        "中国研发支持、国际化人才、数据规模与AI、5G、区块链、电动汽车追赶机制的早期观察",
    ),
    _item(
        "C-EU-JRC-JRC110333",
        "eu-jrc",
        "European Commission Joint Research Centre",
        "2017-01-01",
        "A China-EU electricity transmission link: Assessment of potential connecting countries and routes",
        "https://publications.jrc.ec.europa.eu/repository/handle/JRC110333",
        "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC110333/intercon_report_v03.pdf",
        "pdf",
        ("关键与新兴技术", "产业创新与成果转化", "国际合作与中国比较"),
        "高压直流跨洲电力互联的技术路线、基础设施条件与中欧合作基线",
    ),
    _item(
        "C-OECD-DOI-BB222C73-EN",
        "oecd-sti",
        "OECD",
        "2021-04-09",
        "Report on China’s shipbuilding industry and policies affecting it",
        "https://www.oecd.org/en/publications/report-on-china-s-shipbuilding-industry-and-policies-affecting-it_bb222c73-en.html",
        "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/04/report-on-china-s-shipbuilding-industry-and-policies-affecting-it_f15b480d/bb222c73-en.pdf",
        "pdf",
        ("研发投入与创新政策", "产业创新与成果转化", "创新测量与政策方法", "国际合作与中国比较"),
        "中国造船产业升级、国有企业组织、政府支持与全球产能结构的系统材料",
    ),
    _item(
        "C-EU-JRC-JRC122755",
        "eu-jrc",
        "European Commission Joint Research Centre",
        "2021-01-01",
        "Data access and regime competition: A case study of car data sharing in China",
        "https://publications.jrc.ec.europa.eu/repository/handle/JRC122755",
        "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC122755/JRC122755_01.pdf",
        "pdf",
        ("研发投入与创新政策", "关键与新兴技术", "产业创新与成果转化", "国际合作与中国比较"),
        "上海新能源汽车数据汇聚、补贴评估和制造商竞争力之间的创新政策机制",
    ),
    _item(
        "C-JP-RIETI-24-E-042",
        "jp-rieti",
        "Research Institute of Economy, Trade and Industry (RIETI)",
        "2024-03-01",
        "The Welfare Effects of Government Intervention into the Licensing of Standard-essential Patents: An analysis of the Chinese smartphone and SoC markets",
        "https://www.rieti.go.jp/en/publications/summary/24030019.html",
        "https://www.rieti.go.jp/jp/publications/dp/24e042.pdf",
        "pdf",
        ("关键与新兴技术", "产业创新与成果转化", "创新测量与政策方法", "国际合作与中国比较"),
        "标准必要专利许可干预对中国智能手机和系统级芯片市场创新与福利的量化证据",
    ),
)


SOURCE_CATALOGS = (
    "90_Belfer_MERICS科学技术创新缺口轻量目录.csv",
    "77_OECD_STI正式系列轻量目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "194_RIETI科技创新与中国近十年轻量总目录.csv",
)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sanitize_text(text: str) -> str:
    marker = "[REDACTED_CREDENTIAL_SHAPED_EXAMPLE]"
    text = re.sub(r"AKIA[0-9A-Z]{16}", marker, text)
    lines = [marker if re.fullmatch(r"[A-Za-z0-9/+=]{40}", line.strip()) else line.rstrip() for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def sanitize_html(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()).strip() + "\n"


def extract_pdf_text(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return sanitize_text(text), len(reader.pages)


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = (
        "science", "scientific", "research", "r&d", "innovation", "technology", "technological",
        "patent", "licensing", "standard", "data", "artificial intelligence", "5g", "blockchain",
        "electric", "shipbuilding", "industrial policy", "government support", "talent", "china", "chinese",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 60]
    hits = [part for part in paragraphs if any(keyword in part.lower() for keyword in keywords)][:260]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 机构：{item['institution']}\n"
        f"- 科技创新复用角色：{item['role']}\n- 主轴：{'；'.join(item['axes'])}\n\n"
        "## 科学技术创新定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def navigate(target: str, url: str, minimum_text: int = 100) -> dict[str, str]:
    _proxy_json("/navigate?target=" + target + "&url=" + quote(url, safe=""))
    for _ in range(100):
        length = int(_eval(target, "document.body?.innerText.length||0"))
        if length >= minimum_text:
            break
        time.sleep(0.25)
    value = _eval(
        target,
        "(() => {const n=document.querySelector('main')||document.body; return {title:document.title,html:n?.outerHTML||'',text:n?.innerText||''}})()",
    )
    if not isinstance(value, dict):
        raise RuntimeError(f"unexpected page result: {url}")
    return {key: str(value.get(key, "")) for key in ("title", "html", "text")}


def download_pdf(target: str, landing_url: str, asset_url: str) -> bytes:
    navigate(target, landing_url)
    try:
        return browser_pdf(target, asset_url)
    except Exception:
        request = Request(
            asset_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
                "Referer": landing_url,
            },
        )
        with urlopen(request, timeout=180) as response:
            return response.read()


def update_source_catalogs(root: Path, selected_ids: set[str]) -> None:
    for filename in SOURCE_CATALOGS:
        path = root / filename
        data, fields = read_csv(path)
        changed = False
        for row in data:
            if row.get("报告ID") in selected_ids and "全文策略" in fields:
                row["全文策略"] = "已进入跨机构中国科技创新机制定点全文；按本地原始资产、提取文本和科技创新切片调用"
                changed = True
        if changed:
            write_csv(path, data, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill a bounded cross-institution China innovation evidence batch.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    catalog, catalog_fields = read_csv(catalog_path)
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    missing = selected_ids - set(catalog_by_id)
    if missing:
        raise RuntimeError(f"selected reports missing from catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        row = catalog_by_id[str(item["id"])]
        if row["发布日期"] != item["date"] or row["报告名称"] != item["title"]:
            raise RuntimeError(f"selected metadata drift: {item['id']}")

    dirs = {
        "pdf": root / "03_证据底稿" / "原文PDF",
        "html": root / "03_证据底稿" / "网页原文",
        "text": root / "03_证据底稿" / "文本",
        "slice": root / "03_证据底稿" / "切片",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)

    opened = _proxy_json("/new?url=" + quote(str(SELECTED_ITEMS[0]["landing_url"]), safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = str(item["id"])
            text_path = dirs["text"] / f"{rid}.txt"
            slice_path = dirs["slice"] / f"{rid}.md"
            pages = 0
            if item["asset_type"] == "pdf":
                pdf_path = dirs["pdf"] / f"{rid}.pdf"
                if not pdf_path.exists():
                    pdf_path.write_bytes(
                        download_pdf(target, str(item["landing_url"]), str(item["asset_url"]))
                    )
                payload = pdf_path.read_bytes()
                if not payload.startswith(b"%PDF"):
                    raise RuntimeError(f"invalid official PDF: {rid}")
                text, pages = extract_pdf_text(pdf_path)
                if len(text) < 1_000:
                    raise RuntimeError(f"extracted PDF text too short: {rid} {len(text)}")
                asset_path = pdf_path
                asset_status = "官方PDF已获取并校验"
                completeness = "官方PDF全文已保存；同时生成提取文本和科技创新切片"
            else:
                page = navigate(target, str(item["landing_url"]), minimum_text=500)
                if "innovation superpower" not in page["title"].lower() or len(page["text"]) < 2_000:
                    raise RuntimeError(f"thin or incorrect official web page: {rid}")
                asset_path = dirs["html"] / f"{rid}.html"
                asset_path.write_text(sanitize_html(page["html"]), encoding="utf-8", newline="\n")
                text = sanitize_text(page["text"])
                payload = asset_path.read_bytes()
                asset_status = "官方网页正文及HTML快照已获取"
                completeness = "官方网页正文与HTML快照已保存；同时生成科技创新切片"
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(selected_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            row = catalog_by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = completeness
            row["优先级"] = "P0-China-STI-node"
            row["示踪问题"] = "；".join(item["axes"]) + "；中国科技横向维度"
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = str(item["role"])
            row["本地原始资产路径"] = str(asset_path)
            row["原始资产状态"] = asset_status
            ledger.append(
                {
                    "报告ID": rid,
                    "机构ID": str(item["institution_id"]),
                    "机构": str(item["institution"]),
                    "发布日期": str(item["date"]),
                    "报告名称": str(item["title"]),
                    "官方落地页": str(item["landing_url"]),
                    "官方原始资产入口": str(item["asset_url"]),
                    "资产类型": "官方PDF" if item["asset_type"] == "pdf" else "官方网页HTML",
                    "本地原始资产": str(asset_path),
                    "本地文本": str(text_path),
                    "本地切片": str(slice_path),
                    "PDF页数": str(pages),
                    "字节数": str(len(payload)),
                    "清洗文本字符数": str(len(text)),
                    "China词形命中数": str(china_hits),
                    "SHA256": hashlib.sha256(payload).hexdigest(),
                    "科技创新主轴": "；".join(item["axes"]),
                    "科技创新复用角色": str(item["role"]),
                    "选择理由": "中国科技创新机制直接材料；安全、出口管制和一般贸易不构成选择理由",
                    "获取日期": date.today().isoformat(),
                }
            )
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={pages} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, catalog_fields)
    update_source_catalogs(root, selected_ids)
    ledger_path = root / "214_跨机构中国科技创新机制定点增补台账.csv"
    write_csv(ledger_path, ledger, list(ledger[0]))
    totals = {
        key: sum(int(row[key]) for row in ledger)
        for key in ("PDF页数", "字节数", "清洗文本字符数", "China词形命中数")
    }
    (root / "215_跨机构中国科技创新机制定点增补结果.md").write_text(
        "# 跨机构中国科技创新机制定点增补结果\n\n"
        f"- 从既有轻量目录中选择{len(ledger)}份正式材料，涉及MERICS、JRC、OECD和RIETI四个机构家族。\n"
        f"- 保存4份官方PDF和1项官方网页正文，共{totals['PDF页数']:,}页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- China/Chinese/PRC词形共命中{totals['China词形命中数']:,}次。\n"
        "- 机制覆盖研发支持与人才、跨境技术基础设施、产业升级与政府支持、汽车数据汇聚、标准必要专利许可及芯片市场。\n"
        "- 军事、出口管制、工业间谍、一般贸易和纯安全治理材料未进入本批全文。\n",
        encoding="utf-8",
    )
    print(
        f"selected={len(ledger)} pages={totals['PDF页数']} bytes={totals['字节数']} "
        f"chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
