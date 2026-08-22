from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

try:
    from scripts.extract_viewpoint_pdf_slices import process_pdf
except ModuleNotFoundError:
    from extract_viewpoint_pdf_slices import process_pdf


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"
CATALOG_FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]
SERIES_ROLE = "Rathenau科技创新与中国比较跨期精选全文"


def _item(report_id, published, title, landing, asset_url, axes, role, china=False, asset_type="PDF"):
    return {
        "id": report_id, "date": published, "title": title, "landing": landing,
        "asset_url": asset_url, "asset_type": asset_type, "axes": tuple(axes), "role": role, "china": china,
    }


SELECTED_ITEMS = (
    _item("C-RATHENAU-2015-RD-GOES-GLOBAL", "2015-10-19", "R&D goes global",
          "https://www.rathenau.nl/en/how-science-system-works/rd-goes-global",
          "https://www.rathenau.nl/sites/default/files/2018-04/RATH-rapport%20R%26D%20goes%20global_WEB.pdf",
          ("技术创新与产业转化", "开放科学与国际合作"), "跨国企业研发全球化、中国创新生态与上海北京研发区位", True),
    _item("C-RATHENAU-2016-PUBLIC-KNOWLEDGE-ORGANISATIONS-NETHERLANDS", "2016-03-08", "Public knowledge organisations in the Netherlands",
          "https://www.rathenau.nl/en/knowledge-and-innovation-transitions/public-knowledge-organisations-netherlands",
          "https://www.rathenau.nl/sites/default/files/2018-03/FF17_PKOs%20in%20the%20Netherlands_WEB_0.pdf",
          ("科学体系与基础研究", "研发治理与科研组织"), "公共知识机构的功能分工、资金结构与应用研究组织"),
    _item("C-RATHENAU-2016-SHAPING-INNOVATION-THROUGH-POLICY", "2016-05-07", "Shaping innovation through policy",
          "https://www.rathenau.nl/en/werking-van-het-wetenschapssysteem/shaping-innovation-through-policy",
          "https://www.rathenau.nl/sites/default/files/2018-03/Shaping%20socio-technical%20innovation%20through%20policy%20-%20Rathenau%20Instituut.pdf",
          ("技术创新与产业转化", "研发治理与科研组织"), "社会技术创新、系统性创新政策与主动知识战略"),
    _item("C-RATHENAU-2018-REGIONAL-INNOVATION", "2018-03-05", "Regional innovation",
          "https://www.rathenau.nl/en/werking-van-het-wetenschapssysteem/regional-innovation",
          "https://www.rathenau.nl/sites/default/files/2018-03/Regional%20Innovation_1.pdf",
          ("技术创新与产业转化",), "区域知识生产、创新生态与地方政策工具"),
    _item("C-RATHENAU-2018-INDUSTRY-SEEKING-UNIVERSITY", "2018-11-27", "Industry seeking university",
          "https://www.rathenau.nl/en/werking-van-het-wetenschapssysteem/industry-seeking-university",
          "https://www.rathenau.nl/sites/default/files/2018-11/Industry%20seeking%20university%202018_11_27_0.pdf",
          ("研发治理与科研组织", "技术创新与产业转化"), "大学企业合作、知识交换与科研成果产业转化"),
    _item("C-RATHENAU-2020-EUROPEAN-RESEARCH-AND-INNOVATION-NEW-GEOPOLITICAL-ARENA", "2020-05-19", "European research and innovation in a new geopolitical arena",
          "https://www.rathenau.nl/en/werking-van-het-wetenschapssysteem/european-research-and-innovation-new-geopolitical-arena",
          "https://www.rathenau.nl/sites/default/files/2020-05/European%20Research%20and%20Innovation%20in%20a%20new%20geopolitical%20arena.pdf",
          ("科学体系与基础研究", "开放科学与国际合作"), "欧洲科研创新体系、技术能力与中美比较", True),
    _item("C-RATHENAU-2021-PERSPECTIVES-FUTURE-OPEN-SCIENCE", "2021-10-01", "Perspectives on the future of Open Science",
          "https://www.rathenau.nl/en/how-science-system-works/perspectives-future-open-science",
          "https://www.rathenau.nl/sites/default/files/2021-12/perspectives_on_future_open_science_Rathenau_Instituut_EU_publication.pdf",
          ("科学体系与基础研究", "开放科学与国际合作"), "开放科学情景、科研基础设施和中国创新能力演变", True),
    _item("C-RATHENAU-2022-RESEARCH-PROGRAMMES-MISSION", "2022-03-22", "Research programmes with a mission",
          "https://www.rathenau.nl/en/how-science-system-works/research-programmes-mission",
          "https://www.rathenau.nl/sites/default/files/2022-03/Research_programmes_with_a_mission_Rathenau_Instituut.pdf",
          ("研发治理与科研组织", "技术创新与产业转化"), "使命导向科研计划、挑战驱动创新与社会技术系统转型"),
    _item("C-RATHENAU-2022-TOTAL-INVESTMENT-RESEARCH-AND-INNOVATION-2020-2026", "2022-08-31", "Total Investment in Research and Innovation 2020-2026",
          "https://www.rathenau.nl/en/how-science-system-works/total-investment-research-and-innovation-2020-2026",
          "https://www.rathenau.nl/sites/default/files/2022-09/Vertaling%20TWIN%20incl%20figuren.pdf",
          ("科学体系与基础研究", "研发治理与科研组织"), "公共研发投入、预算结构与科研创新政策基线"),
    _item("C-RATHENAU-2024-NWO-PROGRAMMES-CURIOSITY-DRIVEN-RESEARCH", "2024-01-16", "NWO programmes for curiosity-driven research",
          "https://www.rathenau.nl/en/how-science-system-works/nwo-programmes-curiosity-driven-research",
          "https://www.rathenau.nl/sites/default/files/2024-01/Rathenau%20Instituut%20I%20Rapport%20I%20NWO-programma%27s%20voor%20vrij%20onderzoek%20Engelse%20versie%20door%20DeepL%20aangepast%20PD_LM_schoon.pdf",
          ("科学体系与基础研究", "研发治理与科研组织"), "自由探索研究资助、项目组合与基础研究组织"),
    _item("C-RATHENAU-2024-KNOWLEDGE-FUTURE", "2024-10-09", "Knowledge of the Future",
          "https://www.rathenau.nl/en/how-science-system-works/knowledge-future",
          "https://www.rathenau.nl/sites/default/files/2024-10/Rathenau%20Instituut_REPORT_Knowledge%20of%20the%20Future.pdf",
          ("科学体系与基础研究", "研发治理与科研组织"), "荷兰知识基础、研究能力与长期科学政策选择"),
    _item("C-RATHENAU-2025-CHINA-SCIENTIFIC-SUPERPOWER", "2025-06-02", "China: a scientific superpower in the making",
          "https://www.rathenau.nl/en/science-figures/process/collaboration/china-scientific-superpower-making",
          "https://www.rathenau.nl/en/science-figures/process/collaboration/china-scientific-superpower-making",
          ("科学体系与基础研究", "开放科学与国际合作"), "中国研发投入、科研人员、论文产出、学科结构与国际合作比较", True, "WEB"),
    _item("C-RATHENAU-2026-GEOPOLITICS-SCIENCE-POLICY", "2026-05-04", "Geopolitics in Science Policy",
          "https://www.rathenau.nl/en/knowledge-and-innovation-transitions/challenge-driven-knowledge-and-innovation-policy/geopolitics-science-policy",
          "https://www.rathenau.nl/sites/default/files/2026-05/Geopolitics%20in%20science%20policy%20.pdf",
          ("科学体系与基础研究", "开放科学与国际合作"), "地缘变化如何重塑科研议程、技术能力和国际合作条件", True),
)


def mark_selected_light_rows(rows: list[dict[str, str]]) -> None:
    selected = {str(item["id"]): item for item in SELECTED_ITEMS}
    for row in rows:
        item = selected.get(row.get("报告ID", ""))
        if not item:
            continue
        row["中国关联"] = "是" if item["china"] else row.get("中国关联", "否")
        row["全文策略"] = "已进入精选全文；按本地原始资产、文本和切片调用"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fetch(url: str) -> bytes:
    response = httpx.get(url, follow_redirects=True, timeout=600, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.content


def normalize_generated_file(path: Path) -> None:
    current = path.read_text(encoding="utf-8", errors="replace")
    normalized = re.sub(r"\r+\n?", "\n", current)
    if normalized != current:
        path.write_text(normalized, encoding="utf-8", newline="\n")


def web_text(source_html: str) -> str:
    soup = BeautifulSoup(source_html, "html.parser")
    main = soup.select_one("main") or soup
    for node in main.select("nav, footer, script, style, form, picture, svg"):
        node.decompose()
    lines = [re.sub(r"\s+", " ", line).strip() for line in main.get_text("\n").splitlines()]
    return "\n".join(line for line in lines if line)


def web_slice(item: dict[str, object], text: str) -> str:
    keywords = ("China", "Chinese", "R&D", "research", "scientific", "innovation", "collaboration")
    paragraphs = [line for line in text.splitlines() if len(line) >= 60]
    hits = [line for line in paragraphs if any(word.lower() in line.lower() for word in keywords)][:80]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 官方页面：{item['landing']}\n"
        f"- 资料类型：Rathenau官方网页全文\n\n## 科技创新与中国定向摘录\n\n"
        + "\n\n".join(hits) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    web_dir = root / "03_证据底稿" / "网页原文"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, web_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    catalog_path = root / "05_报告总目录.csv"
    catalog = read_csv(catalog_path)
    by_id = {row["报告ID"]: row for row in catalog}
    light_path = root / "162_Rathenau英文正式报告近十年轻量总目录.csv"
    light_rows = read_csv(light_path)
    missing = {item["id"] for item in SELECTED_ITEMS} - set(by_id)
    if missing:
        raise RuntimeError(f"selected Rathenau items missing from light catalog: {sorted(missing)}")

    ledger: list[dict[str, str]] = []
    for item in SELECTED_ITEMS:
        report_id = str(item["id"])
        text_path = text_dir / f"{report_id}.txt"
        slice_path = slice_dir / f"{report_id}.md"
        if item["asset_type"] == "PDF":
            asset_path = pdf_dir / f"{report_id}.pdf"
            data = asset_path.read_bytes() if asset_path.exists() else fetch(str(item["asset_url"]))
            if not data.startswith(b"%PDF"):
                raise RuntimeError(f"official attachment is not a PDF: {item['asset_url']}")
            if not asset_path.exists():
                part = asset_path.with_suffix(".pdf.part")
                part.write_bytes(data)
                part.replace(asset_path)
            if not text_path.exists() or not slice_path.exists():
                process_pdf(asset_path, text_dir, slice_dir)
            normalize_generated_file(text_path)
            normalize_generated_file(slice_path)
            pages = len(PdfReader(asset_path).pages)
        else:
            asset_path = web_dir / f"{report_id}.html"
            data = asset_path.read_bytes() if asset_path.exists() else fetch(str(item["asset_url"]))
            if not asset_path.exists():
                asset_path.write_bytes(data)
            source = data.decode("utf-8", errors="replace")
            extracted = web_text(source)
            text_path.write_text(extracted, encoding="utf-8", newline="\n")
            slice_path.write_text(web_slice(item, extracted), encoding="utf-8", newline="\n")
            pages = 0
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        if len(extracted) < 2_000:
            raise RuntimeError(f"extracted text too short: {report_id} {len(extracted)}")
        lower = extracted.lower()
        china_hits = lower.count("china") + lower.count("chinese")
        row = by_id[report_id]
        row["本地路径"] = str(asset_path)
        row["正文完整度"] = "官方PDF全文已保存" if item["asset_type"] == "PDF" else "官方网页全文已保存"
        row["优先级"] = "P0-China-STI-node" if item["china"] else "P1-STI-node"
        row["样本角色"] = SERIES_ROLE
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = str(item["role"])
        row["本地原始资产路径"] = str(asset_path)
        row["原始资产状态"] = "Rathenau官方原始资产已获取；已生成文本与科技创新定向切片"
        ledger.append({
            "报告ID": report_id, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
            "官方落地页": str(item["landing"]), "原始资产类型": str(item["asset_type"]), "官方资产": str(item["asset_url"]),
            "本地原始资产": str(asset_path), "本地文本": str(text_path), "本地切片": str(slice_path),
            "PDF页数": str(pages), "字节数": str(len(data)), "提取文本字符数": str(len(extracted)),
            "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(data).hexdigest(),
            "中国关联": "是" if item["china"] else "否", "科技创新主轴": "；".join(item["axes"]),
            "科技创新复用角色": str(item["role"]), "选择理由": "跨期节点；直接解释科学技术创新机制；相对既有全文具有证据增量",
            "获取日期": date.today().isoformat(),
        })

    selected_ids = {item["id"] for item in SELECTED_ITEMS}
    for row in catalog:
        if row.get("机构ID") != "rathenau" or row.get("报告ID") in selected_ids:
            continue
        marker = "机构跨期精选已完成；低增量节点保留轻量目录"
        if marker not in row.get("原始资产状态", ""):
            row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")

    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    mark_selected_light_rows(light_rows)
    write_csv(light_path, light_rows, list(light_rows[0]))
    write_csv(root / "164_Rathenau科技创新与中国比较跨期精选全文台账.csv", ledger, list(ledger[0]))
    totals = {
        "pages": sum(int(row["PDF页数"]) for row in ledger), "bytes": sum(int(row["字节数"]) for row in ledger),
        "chars": sum(int(row["提取文本字符数"]) for row in ledger), "china": sum(int(row["China词形命中数"]) for row in ledger),
    }
    (root / "165_Rathenau科技创新与中国比较跨期精选全文结果.md").write_text(
        "# Rathenau科技创新与中国比较跨期精选全文结果\n\n"
        f"- 从轻量总目录中定点保存{len(ledger)}项官方原始资产，其中12份PDF、1份官方网页全文，共{totals['pages']}页、{totals['bytes']:,}字节、{totals['chars']:,}字符。\n"
        f"- China/Chinese词形命中{totals['china']}次；中国维度覆盖跨国研发区位、欧洲科研创新比较、开放科学情景、中国科研投入与产出，以及地缘变化下的科研合作。\n"
        "- 跨期主线覆盖公共知识机构、系统性创新政策、区域创新、大学企业合作、科研创新国际格局、开放科学、使命导向研究、研发投入、自由探索研究与长期知识基础。\n"
        "- 网络冲突、平台治理、数字民主等语境类题名保留于轻量总目录，不进入本批全文层。\n",
        encoding="utf-8",
    )
    print(f"assets={len(ledger)} pdfs=12 web=1 pages={totals['pages']} bytes={totals['bytes']} chars={totals['chars']} china_hits={totals['china']} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
