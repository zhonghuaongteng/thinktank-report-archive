from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path

try:
    from scripts.extend_viewpoint_royal_society_light_catalog import fetch_markdown
except ModuleNotFoundError:
    from extend_viewpoint_royal_society_light_catalog import fetch_markdown


SELECTED = (
    ("Machine learning: the power and promise of computers that learn by example", "机器学习由研究前沿走向通用技术的早期判断", "技术创新与关键技术；创新政策与研发治理"),
    ("Research culture: Embedding inclusive excellence", "科研文化与包容性卓越的组织基础", "科学体系与基础研究；人才大学与科研组织"),
    ("Dynamics of data science skills", "数据科学人才需求、大学供给与产业吸纳机制", "技术创新与关键技术；人才大学与科研组织"),
    ("The role of public and non-profit research organisations in the UK research and innovation landscape", "公共及非营利研究组织在创新体系中的功能", "科学体系与基础研究；创新政策与研发治理；产业创新转化与区域生态"),
    ("The research and technical workforce in the UK", "科研与技术劳动力的规模、结构与政策条件", "人才大学与科研组织；创新政策与研发治理"),
    ("Regional absorptive capacity: the skills dimension", "区域吸收能力、技能与创新扩散", "人才大学与科研组织；产业创新转化与区域生态"),
    ("Transforming UK Translation - six years in", "科研成果转化体系的跨期评估", "产业创新转化与区域生态；创新政策与研发治理"),
    ("Science in the age of AI", "AI改变科学方法、科研技能与研究完整性", "科学体系与基础研究；技术创新与关键技术；人才大学与科研组织"),
    ("Science and the economy", "科学投入经多路径形成经济与社会价值", "科学体系与基础研究；创新政策与研发治理；产业创新转化与区域生态"),
    ("Science 2040 Interim Report", "长期科学战略与国家科研能力", "科学体系与基础研究；创新政策与研发治理"),
    ("2026 China-UK Science Policy Dialogue on food systems and biodiversity loss", "中英科学政策对话与联合科研合作", "国际合作开放科学与比较；科学体系与基础研究"),
)
SELECTED_TITLES = tuple(item[0] for item in SELECTED)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def official_pdf_urls(source: str) -> list[str]:
    urls = re.findall(r"https?://royalsociety\.org/[^\s\)]+?\.pdf(?:\?[^\s\)]*)?", source, re.I)
    cleaned = []
    for url in urls:
        normalized = url.replace("http://", "https://", 1)
        if normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def first_official_pdf(source: str) -> str:
    urls = official_pdf_urls(source)
    if not urls:
        return ""
    penalties = ("summary", "case-stud", "appendix", "technical-report", "supporting")
    ranked = sorted(enumerate(urls), key=lambda pair: (sum(token in pair[1].lower() for token in penalties), pair[0]))
    return ranked[0][1]


def plain_text(markdown: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", markdown)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^[-*]\s+", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def selected_slice(title: str, text: str) -> str:
    keywords = (
        "science", "scientific", "research", "r&d", "innovation", "technology", "technical", "skills",
        "workforce", "talent", "university", "organisation", "organization", "funding", "translation",
        "commercial", "industry", "regional", "collaboration", "china", "chinese", "artificial intelligence", "ai",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 70]
    hits = [part for part in paragraphs if any(word in part.lower() for word in keywords)][:180]
    return f"# {title}\n\n- 证据类型：英国皇家学会正式成果的科学技术创新定向摘录\n\n" + "\n\n".join(hits) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire selected Royal Society science and technology full-text proxies.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "198_英国皇家学会科学技术创新专题轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light, light_fields = read_csv(light_path)
    catalog, catalog_fields = read_csv(catalog_path)
    light_by_title = {row["报告名称"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    missing = [title for title in SELECTED_TITLES if title not in light_by_title]
    if missing:
        raise RuntimeError(f"Royal Society selected metadata missing: {missing}")

    proxy_dir = root / "03_证据底稿" / "网页原文"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (proxy_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    ledger: list[dict[str, str]] = []
    selected_ids: set[str] = set()
    for index, (title, role, axes) in enumerate(SELECTED, 1):
        source = light_by_title[title]
        rid = source["报告ID"]
        selected_ids.add(rid)
        landing_markdown = fetch_markdown(source["官方落地页"])
        pdf_url = source["官方PDF入口"] or first_official_pdf(landing_markdown)
        if pdf_url:
            proxy_markdown = fetch_markdown(pdf_url)
            proxy_kind = "官方PDF经Jina Reader规范化的全文Markdown代理"
            proxy_source = pdf_url
        else:
            proxy_markdown = landing_markdown
            proxy_kind = "Royal Society官方发布页全文Markdown快照"
            proxy_source = source["官方落地页"]
        proxy_markdown = re.sub(r"[ \t]+$", "", proxy_markdown, flags=re.MULTILINE)
        if len(proxy_markdown) < 1500:
            raise RuntimeError(f"Royal Society selected proxy too short: {rid}")
        text = plain_text(proxy_markdown)
        if len(text) < 1000:
            raise RuntimeError(f"Royal Society selected text too short: {rid}")
        proxy_path = proxy_dir / f"{rid}-FULLTEXT-PROXY.md"
        text_path = text_dir / f"{rid}.txt"
        slice_path = slice_dir / f"{rid}.md"
        proxy_path.write_text(proxy_markdown, encoding="utf-8", newline="\n")
        text_path.write_text(text, encoding="utf-8", newline="\n")
        slice_path.write_text(selected_slice(title, text), encoding="utf-8", newline="\n")
        digest = hashlib.sha256(proxy_markdown.encode("utf-8")).hexdigest()
        lower = text.lower()
        china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
        source["官方PDF入口"] = pdf_url
        source["全文策略"] = "已进入精选全文；本地保存官方入口、全文Markdown代理、清洗文本和科技创新切片"
        catalog_row = catalog_by_id[rid]
        catalog_row["本地路径"] = str(text_path)
        catalog_row["正文完整度"] = proxy_kind + "；精确引文需回查官方PDF或官方发布页"
        catalog_row["优先级"] = "P1-STI-node"
        catalog_row["样本角色"] = "英国皇家学会科学体系与技术创新跨期精选全文"
        catalog_row["编码状态"] = "全文待观点编码"
        catalog_row["预期用途"] = role
        catalog_row["本地原始资产路径"] = str(proxy_path)
        catalog_row["原始资产状态"] = proxy_kind + "已保存；官方入口已核验"
        ledger.append({
            "报告ID": rid, "发布日期": source["发布日期"], "报告名称": title, "官方文类": source["官方文类"],
            "官方落地页": source["官方落地页"], "官方PDF入口": pdf_url, "本地全文代理": str(proxy_path),
            "本地文本": str(text_path), "本地切片": str(slice_path), "代理形态": proxy_kind,
            "全文代理字符数": str(len(proxy_markdown)), "清洗文本字符数": str(len(text)),
            "China词形命中数": str(china_hits), "SHA256": digest, "科技创新主轴": axes,
            "科技创新复用角色": role, "证据边界": "主题理解与观点筛选可直接使用；逐字引文、页码和版式证据回查Royal Society官方PDF",
            "获取日期": date.today().isoformat(),
        })
        print(f"royal_society_selected={index}/{len(SELECTED)} id={rid} chars={len(text)}", flush=True)

    marker = "Royal Society跨期精选已完成；其余成果保留轻量目录"
    for row in catalog:
        if row.get("机构ID") == "uk-royal-society" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            row["原始资产状态"] = marker
    write_csv(light_path, light, light_fields)
    write_csv(catalog_path, sorted(catalog, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", ""))), catalog_fields)
    ledger_path = root / "200_英国皇家学会科学体系与技术创新跨期精选全文台账.csv"
    result_path = root / "201_英国皇家学会科学体系与技术创新跨期精选全文结果.md"
    write_csv(ledger_path, ledger, list(ledger[0]))
    total_proxy = sum(int(row["全文代理字符数"]) for row in ledger)
    total_text = sum(int(row["清洗文本字符数"]) for row in ledger)
    china_docs = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    result_path.write_text(
        "# 英国皇家学会科学体系与技术创新跨期精选全文结果\n\n"
        f"- 从42项专题轻量目录中选择{len(ledger)}项跨期材料，保存全文Markdown代理{total_proxy:,}字符、清洗文本{total_text:,}字符；{china_docs}项出现China/Chinese/PRC词形。\n"
        "- 证据链覆盖机器学习、科研文化、数据科学人才、公共研究组织、技术劳动力、区域吸收能力、科研成果转化、AI赋能科学、科学经济价值、长期科学战略和中英科研合作。\n"
        "- Royal Society站点对自动化下载返回403，本地资产采用官方PDF或官方发布页经Jina Reader规范化的全文代理。主题理解和观点筛选可直接使用；逐字引文、页码及版式证据须回查官方PDF。\n"
        "- 科研安全、出口管制、国防和一般治理议题未进入精选全文。\n",
        encoding="utf-8",
    )
    print(f"royal_society_selected_total={len(ledger)} proxy_chars={total_proxy} text_chars={total_text} china_docs={china_docs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
