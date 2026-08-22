from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from pypdf import PdfReader


def _item(post_id: int, slug: str, title: str, axes: str, role: str) -> tuple[int, str, str, str, str]:
    return post_id, slug, title, axes, role


SELECTED = (
    _item(2791, "engineering-im-umfeld-von-industrie-4-0-einschaetzungen-und-handlungsbedarf", "Engineering im Umfeld von Industrie 4.0 – Einschätzungen und Handlungsbedarf", "技术创新与关键技术；人才大学与科研组织；产业创新转化与区域生态", "工程方法、组织与能力如何适应工业4.0"),
    _item(2786, "industrie-4-0-im-globalen-kontext-strategien-der-zusammenarbeit-mit-internationalen-partnern", "Industrie 4.0 im globalen Kontext – Strategien der Zusammenarbeit mit internationalen Partnern", "技术创新与关键技术；国际合作开放科学与比较；中国科技横向维度", "中德及主要工业国工业4.0技术、创新中心和合作机制比较"),
    _item(2739, "industrie-4-0-maturity-index-die-digitale-transformation-von-unternehmen-gestalten", "Industrie 4.0 Maturity Index – Die digitale Transformation von Unternehmen gestalten", "技术创新与关键技术；产业创新转化与区域生态", "企业数字化由单点技术走向组织能力和成熟度路线图"),
    _item(2638, "impulse-fuer-sprunginnovationen-in-deutschland", "Impulse für Sprunginnovationen in Deutschland", "创新政策与研发治理；产业创新转化与区域生态", "突破性创新的组织、资助与转化机制"),
    _item(18133, "themenfelder-industrie-4-0", "Themenfelder Industrie 4.0", "技术创新与关键技术；创新政策与研发治理；产业创新转化与区域生态", "从应用基线识别工业4.0前竞争性研发需求"),
    _item(21040, "innovationspotenziale-der-quantentechnologien", "Innovationspotenziale der Quantentechnologien der zweiten Generation", "科学体系与基础研究；技术创新与关键技术；产业创新转化与区域生态", "量子研究到应用创新的潜力与瓶颈"),
    _item(27003, "engineering-in-deutschland", "Engineering in Deutschland – Status quo in Wirtschaft und Wissenschaft. Ein Beitrag zum Advanced Systems Engineering", "科学体系与基础研究；人才大学与科研组织；产业创新转化与区域生态", "工程科学与产业工程能力的组织基线"),
    _item(37012, "die-advanced-systems-engineering-strategie", "Die Advanced Systems Engineering Strategie – Eine Leitinitiative zur Zukunft des Engineering- und Innovationsstandorts Deutschland", "技术创新与关键技术；创新政策与研发治理；人才大学与科研组织", "先进系统工程由方法议题上升为创新体系战略"),
    _item(44304, "potenziale-der-biotechnologie", "„Lost in Translation?“ – Ansätze zur Entfesselung gesellschaftlicher und ökonomischer Potenziale der Biotechnologie", "科学体系与基础研究；技术创新与关键技术；产业创新转化与区域生态", "生物技术从科学发现到经济社会应用的转化机制"),
    _item(51945, "kernfusion-made-in-germany", "Kernfusion Made in Germany. Handlungsoptionen für den Aufbau eines Innovationsökosystems Kernfusion", "科学体系与基础研究；技术创新与关键技术；产业创新转化与区域生态", "聚变技术创新生态的科研、基础设施和企业组织"),
    _item(54254, "ki-standortanalyse-baden-wuerttemberg", "KI-Standortanalyse Baden-Württemberg", "技术创新与关键技术；人才大学与科研组织；产业创新转化与区域生态", "区域AI科研、人才、企业与转化能力测度"),
    _item(60073, "forschungsbeirat-industrie40-zirkulaere-wertschoepfung", "Industrie 4.0 für zirkuläre Wertschöpfung", "技术创新与关键技术；产业创新转化与区域生态", "工业4.0技术支持循环价值创造的近期研发路线"),
)
SELECTED_IDS = tuple(f"C-DE-ACATECH-{item[0]}" for item in SELECTED)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def download_pdf(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 Codex research archive"})
    with urlopen(request, timeout=120) as response:
        data = response.read()
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"acatech endpoint did not return a PDF: {url}")
    return data


def extract_pdf_text(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n", len(reader.pages)


def selected_slice(title: str, text: str) -> str:
    keywords = (
        "wissenschaft", "science", "forschung", "research", "entwicklung", "r&d", "innovation", "engineering",
        "technolog", "industrie 4.0", "quant", "biotech", "kernfusion", "künstliche intelligenz", " ki ",
        "hochschul", "universit", "kompetenz", "transfer", "unternehmen", "wirtschaft", "ökosystem", "china", "chines",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 65]
    hits = [part for part in paragraphs if any(keyword in f" {part.lower()} " for keyword in keywords)][:240]
    return f"# {title}\n\n- 证据类型：acatech正式成果的科学技术创新定向摘录\n\n## 科学技术创新定向摘录\n\n" + "\n\n".join(hits) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Save selected acatech science and technology innovation PDFs.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "202_acatech科学与技术创新正式成果轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light, light_fields = read_csv(light_path)
    catalog, catalog_fields = read_csv(catalog_path)
    light_by_id = {row["报告ID"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    missing = sorted(set(SELECTED_IDS) - set(light_by_id))
    if missing:
        raise RuntimeError(f"selected acatech metadata missing: {missing}")
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    ledger: list[dict[str, str]] = []
    for index, (post_id, slug, title, axes, role) in enumerate(SELECTED, 1):
        rid = f"C-DE-ACATECH-{post_id}"
        source = light_by_id[rid]
        if source["报告名称"] != title:
            raise RuntimeError(f"acatech metadata drift: {rid} {source['报告名称']!r}")
        pdf_url = f"https://www.acatech.de/publikation/{slug}/download-pdf?lang=de"
        pdf_path = pdf_dir / f"{rid}.pdf"
        text_path = text_dir / f"{rid}.txt"
        slice_path = slice_dir / f"{rid}.md"
        if not pdf_path.exists():
            pdf_path.write_bytes(download_pdf(pdf_url))
        data = pdf_path.read_bytes()
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"invalid acatech PDF: {rid}")
        text, pages = extract_pdf_text(pdf_path)
        if len(text) < 1000:
            raise RuntimeError(f"acatech text too short: {rid} {len(text)}")
        text_path.write_text(text, encoding="utf-8", newline="\n")
        slice_path.write_text(selected_slice(title, text), encoding="utf-8", newline="\n")
        lower = text.lower()
        china_hits = lower.count("china") + lower.count("chines") + lower.count("volksrepublik")
        source["官方PDF入口"] = pdf_url
        source["全文策略"] = "已进入精选全文；本地保存官方PDF、提取文本和科技创新切片"
        row = catalog_by_id[rid]
        row["本地路径"] = str(text_path)
        row["正文完整度"] = "acatech官方PDF已保存并提取全文；精确引用回查PDF页码"
        row["优先级"] = "P1-STI-node"
        row["样本角色"] = "acatech工程科学与技术创新跨期精选全文"
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = role
        row["本地原始资产路径"] = str(pdf_path)
        row["原始资产状态"] = "acatech官方PDF已获取并校验"
        ledger.append({
            "报告ID": rid, "发布日期": source["发布日期"], "报告名称": title, "官方文类": source["官方文类"],
            "官方落地页": source["官方落地页"], "官方PDF入口": pdf_url, "本地原始PDF": str(pdf_path),
            "本地文本": str(text_path), "本地切片": str(slice_path), "页数": str(pages), "字节数": str(len(data)),
            "清洗文本字符数": str(len(text)), "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(data).hexdigest(),
            "科技创新主轴": axes, "科技创新复用角色": role,
            "选择理由": "跨期科学与技术创新机制节点；安全语境题名不自动触发全文", "获取日期": date.today().isoformat(),
        })
        print(f"acatech_selected={index}/{len(SELECTED)} id={rid} pages={pages} chars={len(text)}", flush=True)
    selected_ids = set(SELECTED_IDS)
    for row in catalog:
        if row.get("机构ID") == "de-acatech" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            row["原始资产状态"] = "acatech跨期精选已完成；其余正式成果保留轻量目录"
    write_csv(light_path, light, light_fields)
    write_csv(catalog_path, sorted(catalog, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", ""))), catalog_fields)
    ledger_path = root / "204_acatech工程科学与技术创新跨期精选全文台账.csv"
    result_path = root / "205_acatech工程科学与技术创新跨期精选全文结果.md"
    write_csv(ledger_path, ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_docs = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    result_path.write_text(
        "# acatech工程科学与技术创新跨期精选全文结果\n\n"
        f"- 从官方轻量目录中选择{len(ledger)}份机制增量较高的PDF，共{totals['页数']:,}页、{totals['字节数']:,}字节、提取文本{totals['清洗文本字符数']:,}字符。\n"
        f"- {china_docs}份全文出现China/Chinese/Volksrepublik词形，共{totals['China词形命中数']:,}次；2016年全球工业4.0比较提供直接中国技术创新材料。\n"
        "- 证据链覆盖工程组织、工业4.0成熟度、突破性创新、竞争前研发、量子技术、先进系统工程、生物技术转化、聚变创新生态、区域AI能力和循环制造。\n"
        "- 技术主权、韧性、安全、军民融合和供应链主导出版物保留在轻量目录，未进入自动全文选择。\n",
        encoding="utf-8",
    )
    print(f"acatech_selected_total={len(ledger)} pages={totals['页数']} chars={totals['清洗文本字符数']} china_docs={china_docs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
