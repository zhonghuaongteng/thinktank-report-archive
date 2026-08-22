from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

from pypdf import PdfReader

try:
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json
    from scripts.extend_viewpoint_eu_stoa_selected_fulltexts import browser_pdf
except ModuleNotFoundError:
    from extend_viewpoint_eu_stoa_light_catalog import _eval, _proxy_json
    from extend_viewpoint_eu_stoa_selected_fulltexts import browser_pdf


SERIES_ROLE = "日本RIETI科学技术创新机制与中国比较跨期精选全文"
ENTRY_URL = "https://www.rieti.go.jp/en/publications/act_dp2025.html"


def _item(code: str, published: str, title: str, axes: tuple[str, ...], role: str,
          china_supplement: bool = False) -> dict[str, object]:
    return {
        "id": f"C-JP-RIETI-{code}", "date": published, "title": title, "axes": axes,
        "role": role, "china_supplement": china_supplement,
    }


SELECTED_ITEMS = (
    _item("16-E-041", "2016-03-01", "Role of Public Research Institutes in National Innovation Systems in Industrialized Countries: The cases of Fraunhofer, NIST, CSIRO, AIST, and ITRI", ("科学体系与科研能力", "研发投入与创新政策"), "公共科研机构在国家创新体系中的功能比较基线"),
    _item("17-E-056", "2017-03-01", "Measuring Science Intensity of Industry using Linked Dataset of Science, Technology and Industry", ("创新测量与政策方法", "科学体系与科研能力", "产业创新与成果转化"), "连接论文、专利与产业数据测量科学密集度的方法节点"),
    _item("18-P-012", "2018-07-01", "The Regional Innovation System in China: Regional comparison of technology, venture financing, and human capital focusing on Shenzhen", ("国际合作与中国比较", "产业创新与成果转化", "科技人才与技能"), "深圳区域创新系统、技术融资与人力资本的中国直接材料"),
    _item("19-E-095", "2019-11-01", "Determinants and Impacts of Incorporation of Local Public Technology Transfer Organizations: Evidence from Japan's Kohsetsushi", ("产业创新与成果转化", "科学体系与科研能力"), "地方公共技术转移组织及其中小企业技术扩散机制"),
    _item("20-E-058", "2020-06-01", "Incentive or Disincentive for Disclosure of Research Data? A Large-Scale Empirical Analysis and Implications for Open Science Policy", ("科学体系与科研能力", "研发投入与创新政策", "创新测量与政策方法"), "科研数据披露激励与开放科学政策节点"),
    _item("21-E-026", "2021-03-01", "Chasing Two Hares at Once? Effect of Joint Institutional Change for Promoting Commercial Use of University Knowledge and Scientific Research", ("产业创新与成果转化", "科学体系与科研能力"), "大学知识与科研成果商业化的制度联动节点"),
    _item("22-E-030", "2022-04-01", "Government R&D Spending as a Driving Force of Technology Convergence", ("研发投入与创新政策", "关键与新兴技术"), "政府研发支出推动技术融合的机制节点"),
    _item("23-E-053", "2023-07-01", "Determinants of Commercialization Modes of Science: Evidence from panel data of university technology transfer in Japan", ("产业创新与成果转化", "科学体系与科研能力"), "大学技术转移中科学成果商业化模式的比较节点"),
    _item("24-E-013", "2024-02-01", "Economic Growth through Basic Research by Firms: A science linkage approach", ("科学体系与科研能力", "产业创新与成果转化", "创新测量与政策方法"), "企业基础研究、科学关联与经济增长节点"),
    _item("25-E-089", "2025-09-01", "Do Corporate Scientists Contribute to Firm Innovation? Empirical analysis by using linked dataset of research papers and patents in Japanese firms", ("科技人才与技能", "科学体系与科研能力", "产业创新与成果转化"), "企业科学家连接论文、专利与企业创新的近期证据"),
    _item("26-E-021", "2026-03-01", "Design Right Commercialization by Public Technology Transfer Organizations: Disseminating design knowledge in regional innovation systems", ("产业创新与成果转化", "科学体系与科研能力"), "公共技术转移组织推动设计知识商业化的最新节点"),
    _item("20-E-045", "2020-05-01", "Technological Competitiveness of China's Internet Platforms: Comparison of Google and Baidu Using Patent Text Information", ("关键与新兴技术", "国际合作与中国比较", "创新测量与政策方法"), "基于专利文本比较中国互联网平台技术竞争力", True),
    _item("24-E-075", "2024-10-01", "Quantifying the Differences in Innovation Processes in China, Japan and the United States by Document Level Concordance between Patents and Web Contents", ("创新测量与政策方法", "国际合作与中国比较"), "利用专利与网页内容比较中日美创新过程", True),
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


def sanitize_extracted_text(text: str) -> str:
    marker = "[REDACTED_CREDENTIAL_SHAPED_EXAMPLE]"
    text = re.sub(r"AKIA[0-9A-Z]{16}", marker, text)
    return "\n".join(marker if re.fullmatch(r"[A-Za-z0-9/+=]{40}", line.strip()) else line for line in text.split("\n"))


def extract_pdf_text(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return sanitize_extracted_text(re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"), len(reader.pages)


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = (
        "science", "scientific", "research", "r&d", "innovation", "technology", "technological",
        "patent", "knowledge", "university", "commercial", "transfer", "institute", "scientist",
        "funding", "data", "china", "chinese", "shenzhen", "artificial intelligence",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 60]
    hits = [part for part in paragraphs if any(keyword in part.lower() for keyword in keywords)][:240]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 科技创新复用角色：{item['role']}\n"
        f"- 主轴：{'；'.join(item['axes'])}\n\n## 科学技术创新定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def page_html(target: str, url: str) -> str:
    _proxy_json("/navigate?target=" + target + "&url=" + quote(url, safe=""))
    for _ in range(80):
        length = int(_eval(target, "document.body?.innerText.length||0"))
        if length >= 250:
            break
        time.sleep(0.25)
    else:
        raise RuntimeError(f"RIETI landing page did not become ready: {url}")
    html = str(_eval(target, "document.documentElement?.outerHTML||''"))
    if len(html) < 500:
        raise RuntimeError(f"thin RIETI landing page: {url}")
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Save selected RIETI science, technology and innovation full texts.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "194_RIETI科技创新与中国近十年轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light, light_fields = read_csv(light_path)
    catalog, catalog_fields = read_csv(catalog_path)
    light_by_id = {row["报告ID"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    missing = selected_ids - set(light_by_id)
    if missing:
        raise RuntimeError(f"selected RIETI items missing from light catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        source = light_by_id[str(item["id"])]
        if source["发布日期"] != item["date"] or source["报告名称"] != item["title"]:
            raise RuntimeError(f"selected RIETI metadata drift: {item['id']}")

    html_dir = root / "03_证据底稿" / "网页原文"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (html_dir, pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    opened = _proxy_json("/new?url=" + quote(ENTRY_URL, safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for _ in range(80):
            if "RIETI" in str(_eval(target, "document.title")):
                break
            time.sleep(0.25)
        else:
            raise RuntimeError("RIETI browser entry page did not become ready")
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = str(item["id"])
            source = light_by_id[rid]
            pdf_url = source["官方PDF入口"]
            if not pdf_url.startswith("https://www.rieti.go.jp/jp/publications/"):
                raise RuntimeError(f"official RIETI PDF missing: {rid}")
            html_path = html_dir / f"{rid}.html"
            pdf_path = pdf_dir / f"{rid}.pdf"
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            html_path.write_text(page_html(target, source["官方落地页"]), encoding="utf-8", newline="\n")
            if not pdf_path.exists():
                pdf_path.write_bytes(browser_pdf(target, pdf_url))
            pdf_data = pdf_path.read_bytes()
            if not pdf_data.startswith(b"%PDF"):
                raise RuntimeError(f"invalid RIETI PDF: {rid}")
            text, pages = extract_pdf_text(pdf_path)
            if len(text) < 500:
                raise RuntimeError(f"RIETI selected text too short: {rid} {len(text)}")
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(selected_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            catalog_row = catalog_by_id[rid]
            catalog_row["本地路径"] = str(text_path)
            catalog_row["正文完整度"] = "RIETI官方PDF已保存；同时保存官方摘要页HTML、逐页提取文本和科技创新切片"
            catalog_row["优先级"] = "P1-STI-node"
            catalog_row["样本角色"] = SERIES_ROLE
            catalog_row["编码状态"] = "全文待观点编码"
            catalog_row["预期用途"] = str(item["role"])
            catalog_row["本地原始资产路径"] = str(pdf_path)
            catalog_row["原始资产状态"] = "RIETI官方PDF已获取并校验；官方摘要页HTML同步保存"
            source["全文策略"] = "已进入精选全文；按官方PDF、页面HTML、提取文本和科技创新切片调用"
            ledger.append({
                "报告ID": rid, "发布日期": source["发布日期"], "报告名称": source["报告名称"],
                "作者": source["作者"], "官方落地页": source["官方落地页"], "官方PDF入口": pdf_url,
                "本地原始PDF": str(pdf_path), "本地页面HTML": str(html_path), "本地文本": str(text_path),
                "本地切片": str(slice_path), "页数": str(pages), "字节数": str(len(pdf_data)),
                "清洗文本字符数": str(len(text)), "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(pdf_data).hexdigest(), "科技创新主轴": "；".join(item["axes"]),
                "科技创新复用角色": str(item["role"]),
                "选择理由": "每年一个科学技术创新机制节点，并增加两个中国技术创新比较节点；安全议题不触发全文",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={pages} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    marker = "RIETI跨期精选已完成；其余成果保留轻量目录"
    for row in catalog:
        if row.get("机构ID") == "jp-rieti" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            row["原始资产状态"] = marker
    write_csv(catalog_path, sorted(catalog, key=lambda row: (row.get("发布日期", ""), row.get("报告ID", ""))), catalog_fields)
    write_csv(light_path, light, light_fields)
    ledger_path = root / "196_RIETI科学技术创新机制与中国比较跨期精选全文台账.csv"
    result_path = root / "197_RIETI科学技术创新机制与中国比较跨期精选全文结果.md"
    write_csv(ledger_path, ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("页数", "字节数", "清洗文本字符数", "China词形命中数")}
    china_docs = sum(int(row["China词形命中数"]) > 0 for row in ledger)
    result_path.write_text(
        "# RIETI科学技术创新机制与中国比较跨期精选全文结果\n\n"
        f"- 从224项轻量目录中选择{len(ledger)}份官方全文：2016—2026年每年一个科技创新机制节点，另补两个中国技术创新比较节点。\n"
        f"- 共{totals['页数']:,}页、{totals['字节数']:,}字节、提取文本{totals['清洗文本字符数']:,}字符；{china_docs}份出现China/Chinese/PRC词形，共{totals['China词形命中数']:,}次。\n"
        "- 覆盖公共科研机构、科技创新测量、区域创新系统、技术转移、开放科学、大学知识商业化、政府研发支出、基础研究、企业科学家及中国技术创新比较。\n"
        "- 安全、出口管制、脱钩和一般供应链议题未进入精选全文。讨论论文观点继续按作者归因。\n",
        encoding="utf-8",
    )
    print(f"rieti_selected={len(ledger)} pages={totals['页数']} chars={totals['清洗文本字符数']} china_docs={china_docs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
