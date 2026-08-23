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
    from scripts.extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from scripts.extend_viewpoint_eu_stoa_selected_fulltexts import _eval, browser_pdf
except ModuleNotFoundError:
    from extend_viewpoint_eu_stoa_light_catalog import _proxy_json
    from extend_viewpoint_eu_stoa_selected_fulltexts import _eval, browser_pdf


SERIES_ROLE = "欧委会JRC科学技术创新政策跨期精选全文"


def _item(report_id: str, year: int, title: str, axes: tuple[str, ...], role: str) -> dict[str, object]:
    return {"id": report_id, "date": f"{year}-01-01", "title": title, "axes": axes, "role": role}


SELECTED_ITEMS = (
    _item("C-EU-JRC-JRC100825", 2016, "The Innovation Output Indicator 2016: Methodology Update", ("创新测量与政策方法", "研发投入与创新政策"), "创新产出测量方法的早期基线"),
    _item("C-EU-JRC-JRC101970", 2016, "Advanced Manufacturing Activities of Top R&D investors: Geographical and Technological Patterns", ("研发投入与创新政策", "关键与新兴技术", "产业创新与成果转化", "国际合作与中国比较"), "中欧美龙头研发企业的先进制造活动、空间分布与技术组合比较"),
    _item("C-EU-JRC-JRC102148", 2016, "EU corporate R&D intensity gap: What has changed over the last decade? IPTS Working Papers on Corporate R&D and Innovation No 05/2016", ("研发投入与创新政策", "国际合作与中国比较"), "欧盟与中美企业研发强度差距及产业结构变化的早期比较"),
    _item("C-EU-JRC-JRC103716", 2016, "The 2016 EU Industrial R&D Investment Scoreboard", ("研发投入与创新政策", "产业创新与成果转化"), "全球企业研发投入和产业结构的年度基线"),
    _item("C-EU-JRC-JRC107386", 2017, "THE IMPACT OF QUANTUM TECHNOLOGIES ON EU’S FUTURE POLICIES PART 2 Quantum Communications: from science to policies", ("关键与新兴技术", "科学体系与科研能力"), "量子通信从科学研究进入政策议程的早期节点"),
    _item("C-EU-JRC-JRC108520", 2017, "The 2017 EU Industrial R&D Investment Scoreboard", ("研发投入与创新政策", "产业创新与成果转化"), "企业研发投入连续观测节点"),
    _item("C-EU-JRC-JRC113807", 2018, "The 2018 EU Industrial R&D Investment Scoreboard", ("研发投入与创新政策", "产业创新与成果转化"), "企业研发投入与全球技术竞争比较节点"),
    _item("C-EU-JRC-JRC113826", 2018, "Artificial Intelligence: A European Perspective", ("关键与新兴技术", "研发投入与创新政策"), "欧洲AI能力、应用与政策选择的早期综合判断"),
    _item("C-EU-JRC-JRC116516", 2019, "China: Challenges and Prospects from an Industrial and Innovation Powerhouse", ("产业创新与成果转化", "国际合作与中国比较"), "中国由制造大国向产业创新强国转变的直接比较材料"),
    _item("C-EU-JRC-JRC118614", 2019, "Labor mobility from R&D-intensive multinational companies: Implications for knowledge and technology transfer", ("科技人才与技能", "产业创新与成果转化"), "研发密集型企业人才流动与知识技术转移机制"),
    _item("C-EU-JRC-JRC119974", 2020, "AI Watch - National strategies on Artificial Intelligence: A European perspective in 2019", ("关键与新兴技术", "研发投入与创新政策"), "国家AI战略比较与政策工具节点"),
    _item("C-EU-JRC-JRC121184", 2020, "Global race for robotisation – Looking at the entire robotisation chain", ("研发投入与创新政策", "关键与新兴技术", "产业创新与成果转化", "国际合作与中国比较"), "中欧美机器人科研、专利、制造与应用链条的系统比较"),
    _item("C-EU-JRC-JRC121318", 2020, "New and Emerging Transport Technologies and Trends in European Research and Innovation Projects", ("关键与新兴技术", "创新测量与政策方法"), "以项目数据识别新兴技术和技术趋势的方法样本"),
    _item("C-EU-JRC-JRC124072", 2021, "The impact of Smart Specialisation on the governance of research and innovation policy systems", ("研发投入与创新政策", "科学体系与科研能力"), "区域专门化对科研创新治理结构的影响"),
    _item("C-EU-JRC-JRC125613", 2021, "EU in the global Artificial Intelligence landscape", ("关键与新兴技术", "国际合作与中国比较"), "欧盟在全球AI科研和产业格局中的定位"),
    _item("C-EU-JRC-JRC129967", 2022, "Where the EU stands vis-à-vis the USA and China? Corporate R&D intensity gap and structural change", ("研发投入与创新政策", "国际合作与中国比较"), "欧中美企业研发强度差距和产业结构变化的直接证据"),
    _item("C-EU-JRC-JRC131882", 2022, "China 2.0 - Status and Foresight of EU-China Trade, Investment and Technological Race", ("关键与新兴技术", "国际合作与中国比较"), "中欧技术竞争、投资和产业能力的综合前瞻"),
    _item("C-EU-JRC-JRC134319", 2023, "Everybody is looking into the Future! A literature review of reports on emerging technologies and disruptive innovation", ("关键与新兴技术", "创新测量与政策方法"), "新兴技术报告的系统综述和识别框架"),
    _item("C-EU-JRC-JRC133613", 2023, "Mapping the Scientific Base for SDGs and Digital Technologies", ("科学体系与科研能力", "关键与新兴技术", "国际合作与中国比较"), "数字技术与可持续发展目标的全球科学基础和中国科研位置比较"),
    _item("C-EU-JRC-JRC134544", 2023, "Technology Foresight for Public Funding of Innovation: Methods and Best Practices", ("创新测量与政策方法", "研发投入与创新政策"), "技术前瞻介入公共创新资助的机制节点"),
    _item("C-EU-JRC-JRC137266", 2024, "Exploring the global landscape of biotech Innovation: preliminary insights from patent analysis", ("关键与新兴技术", "产业创新与成果转化", "国际合作与中国比较"), "以专利数据比较中国、美国和欧洲生物技术创新版图"),
    _item("C-EU-JRC-JRC137811", 2024, "Eyes on the Future - Signals from recent reports on emerging technologies and breakthrough innovations to support European Innovation Council strategic intelligence - Volume 1", ("关键与新兴技术", "创新测量与政策方法"), "突破性创新信号进入资助决策的情报方法"),
    _item("C-EU-JRC-JRC138601", 2024, "Scientific Excellence 2018-2022", ("科学体系与科研能力", "国际合作与中国比较"), "科研卓越度、学科结构和全球位置的比较节点"),
    _item("C-EU-JRC-JRC142093", 2025, "Putting knowledge and technology to work: Insights from the Innovation Output Indicator", ("创新测量与政策方法", "产业创新与成果转化"), "知识与技术转化为创新产出的测量框架"),
    _item("C-EU-JRC-JRC142637", 2025, "Green Patenting of EU vs. Global Competitors in the Digital Techno Economic Ecosystem", ("关键与新兴技术", "创新测量与政策方法", "国际合作与中国比较"), "绿色数字技术专利中的欧盟、中国与全球竞争者比较"),
    _item("C-EU-JRC-JRC144638", 2025, "The 2025 EU Industrial R&D Investment Scoreboard", ("研发投入与创新政策", "国际合作与中国比较"), "最新完整企业研发投入与全球竞争比较节点"),
    _item("C-EU-JRC-JRC145507", 2026, "Tracking country innovation performance: The Innovation Output Indicator 2025", ("创新测量与政策方法", "产业创新与成果转化"), "国家创新绩效最新测量节点"),
    _item("C-EU-JRC-JRC147828", 2026, "Quantum Technologies. Comparative Analysis of Media Narratives and the Scientific Landscape", ("关键与新兴技术", "科学体系与科研能力", "国际合作与中国比较"), "量子科技科学版图与政策叙事的跨国比较节点"),
    _item("C-EU-JRC-JRC111622", 2018, "Monitoring scientific collaboration trends in wind energy components", ("科学体系与科研能力", "关键与新兴技术", "创新测量与政策方法", "国际合作与中国比较"), "以论文与专利联系观察风能部件科研合作网络及中国位置"),
    _item("C-EU-JRC-JRC115449", 2019, "Distribution of industrial research & innovation activities: An application of the technology readiness levels", ("研发投入与创新政策", "关键与新兴技术", "产业创新与成果转化", "国际合作与中国比较"), "以技术成熟度分布比较工业研发和创新活动的空间组织"),
    _item("C-EU-JRC-JRC128744", 2022, "AI Watch Index 2021", ("研发投入与创新政策", "关键与新兴技术", "创新测量与政策方法", "国际合作与中国比较"), "AI能力、科研、人才、投资与产业活动的国际综合测量节点"),
    _item("C-EU-JRC-JRC137550", 2024, "Diversity in Artificial Intelligence Conferences", ("科学体系与科研能力", "关键与新兴技术", "科技人才与技能", "创新测量与政策方法", "国际合作与中国比较"), "从AI会议参与结构比较科研共同体的地域与人才多样性"),
    _item("C-EU-JRC-JRC140126", 2025, "Interrogating the research and development pipeline of artificial intelligence (AI) in health: diagnosis and prediction-based diagnosis", ("科学体系与科研能力", "研发投入与创新政策", "关键与新兴技术", "国际合作与中国比较"), "医疗AI从科研产出、临床开发到应用管线的跨国比较"),
    _item("C-EU-JRC-JRC142609", 2025, "Trends in Patents in Life Sciences: focus on Pharmaceuticals and Medical Technologies", ("科学体系与科研能力", "关键与新兴技术", "产业创新与成果转化", "创新测量与政策方法", "国际合作与中国比较"), "以专利趋势观察生命科学技术能力、转化方向与中国位置"),
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


def reusable_existing_row(row: dict[str, str] | None, paths: list[Path]) -> bool:
    return row is not None and all(path.exists() for path in paths)


def page_html(target: str, url: str) -> str:
    _proxy_json("/navigate?target=" + target + "&url=" + quote(url, safe=""))
    for _ in range(60):
        length = int(_eval(target, "document.body?.innerText.length||0"))
        if length >= 300:
            break
        time.sleep(0.25)
    result = str(_eval(target, "document.documentElement?.outerHTML||''"))
    if len(result) < 500:
        raise RuntimeError(f"thin JRC landing page: {url}")
    return result


def extract_pdf_text(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return sanitize_extracted_text(re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"), len(reader.pages)


def sanitize_extracted_text(text: str) -> str:
    marker = "[REDACTED_CREDENTIAL_SHAPED_EXAMPLE]"
    text = re.sub(r"AKIA[0-9A-Z]{16}", marker, text)
    return "\n".join(
        marker if re.fullmatch(r"[A-Za-z0-9/+=]{40}", line.strip()) else line
        for line in text.split("\n")
    )


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = (
        "science", "scientific", "research", "r&d", "innovation", "technology", "technological",
        "investment", "funding", "patent", "knowledge transfer", "commercial", "talent", "skills",
        "foresight", "indicator", "scoreboard", "artificial intelligence", "quantum", "china", "chinese",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 60]
    hits = [part for part in paragraphs if any(word in part.lower() for word in keywords)][:240]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 科技创新复用角色：{item['role']}\n"
        f"- 主轴：{'；'.join(item['axes'])}\n\n## 科学技术创新定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Save selected JRC science, technology and innovation full texts.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    light_path = root / "186_欧委会JRC科技创新政策近十年轻量总目录.csv"
    catalog_path = root / "05_报告总目录.csv"
    light, light_fields = read_csv(light_path)
    catalog, catalog_fields = read_csv(catalog_path)
    light_by_id = {row["报告ID"]: row for row in light}
    catalog_by_id = {row["报告ID"]: row for row in catalog}
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    missing = selected_ids - set(light_by_id)
    if missing:
        raise RuntimeError(f"selected JRC items missing from light catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        source = light_by_id[str(item["id"])]
        if source["发布日期"] != item["date"] or source["报告名称"] != item["title"]:
            raise RuntimeError(f"selected JRC metadata drift: {item['id']}")
    html_dir = root / "03_证据底稿" / "网页原文"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (html_dir, pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    ledger_path = root / "188_欧委会JRC科学技术创新政策跨期精选全文台账.csv"
    existing_ledger = read_csv(ledger_path)[0] if ledger_path.exists() else []
    existing_by_id = {row["报告ID"]: row for row in existing_ledger}
    opened = _proxy_json("/new?url=" + quote("https://publications.jrc.ec.europa.eu/repository/search", safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = str(item["id"])
            source = light_by_id[rid]
            pdf_url = source["官方PDF入口"]
            if not pdf_url.startswith("https://publications.jrc.ec.europa.eu/repository/bitstream/"):
                raise RuntimeError(f"official JRC PDF missing: {rid}")
            html_path = html_dir / f"{rid}.html"
            pdf_path = pdf_dir / f"{rid}.pdf"
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            row = catalog_by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = "JRC官方PDF已保存；同时保存官方页面HTML、逐页提取文本和科技创新切片"
            row["优先级"] = "P1-STI-node"
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = str(item["role"])
            row["本地原始资产路径"] = str(pdf_path)
            row["原始资产状态"] = "欧委会JRC官方PDF已获取并校验；官方落地页HTML同步保存"
            source["全文策略"] = "已进入精选全文；按官方PDF、页面HTML、提取文本和科技创新切片调用"
            existing = existing_by_id.get(rid)
            if reusable_existing_row(existing, [pdf_path, html_path, text_path, slice_path]):
                preserved = dict(existing or {})
                preserved["中国直接信号"] = source["中国直接信号"]
                ledger.append(preserved)
                print(f"reused={index}/{len(SELECTED_ITEMS)} id={rid}", flush=True)
                continue
            html_path.write_text(page_html(target, source["官方落地页"]), encoding="utf-8", newline="\n")
            if not pdf_path.exists():
                pdf_path.write_bytes(browser_pdf(target, pdf_url))
            pdf_data = pdf_path.read_bytes()
            if not pdf_data.startswith(b"%PDF"):
                raise RuntimeError(f"invalid JRC PDF: {rid}")
            text, pages = extract_pdf_text(pdf_path)
            if len(text) < 500:
                raise RuntimeError(f"JRC selected text too short: {rid} {len(text)}")
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(selected_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            ledger.append({
                "报告ID": rid, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
                "官方落地页": source["官方落地页"], "官方PDF入口": pdf_url,
                "本地原始PDF": str(pdf_path), "本地页面HTML": str(html_path), "本地文本": str(text_path),
                "本地切片": str(slice_path), "页数": str(pages), "字节数": str(len(pdf_data)),
                "清洗文本字符数": str(len(text)), "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(pdf_data).hexdigest(), "中国直接信号": source["中国直接信号"],
                "科技创新主轴": "；".join(item["axes"]),
                "科技创新复用角色": str(item["role"]),
                "选择理由": "跨期科学技术创新节点；安全与一般治理不单独触发", "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={pages} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass
    marker = "JRC跨期精选已完成；其余成果保留轻量目录"
    for row in catalog:
        if row.get("机构ID") == "eu-jrc" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            if marker not in row.get("原始资产状态", ""):
                row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")
    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, catalog_fields)
    write_csv(light_path, light, light_fields)
    result_path = root / "189_欧委会JRC科学技术创新政策跨期精选全文结果.md"
    write_csv(ledger_path, ledger, list(ledger[0]))
    totals = {
        "bytes": sum(int(row["字节数"]) for row in ledger), "pages": sum(int(row["页数"]) for row in ledger),
        "chars": sum(int(row["清洗文本字符数"]) for row in ledger),
        "china": sum(int(row["China词形命中数"]) for row in ledger),
        "china_docs": sum(int(row["China词形命中数"]) > 0 for row in ledger),
        "direct": sum(row["中国直接信号"] == "是" for row in ledger),
    }
    result_path.write_text(
        "# 欧委会JRC科学技术创新政策跨期精选全文结果\n\n"
        f"- 从{len(light):,}项近十年轻量目录中选择{len(ledger)}项跨期节点，保存JRC官方PDF、官方页面HTML、提取文本和科技创新切片。\n"
        f"- 共{totals['bytes']:,}字节、{totals['pages']:,}页、提取文本{totals['chars']:,}字符。\n"
        f"- {totals['china_docs']}份全文出现China/Chinese/PRC词形，共{totals['china']}次；轻量目录标记的直接中国比较材料{totals['direct']}份。\n"
        "- 机制覆盖科研卓越度、企业研发投入、创新产出测量、先进制造、机器人、数字技术科学基础、生物技术与绿色专利、技术前瞻、人才流动与技术转移、AI和量子科技，以及欧中美创新能力比较。\n"
        "- 安全、执法、军事、出口管制及一般风险治理未作为全文选择理由；其余成果继续保留轻量目录。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} pages={totals['pages']} bytes={totals['bytes']} text_chars={totals['chars']} china_docs={totals['china_docs']} china_hits={totals['china']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
