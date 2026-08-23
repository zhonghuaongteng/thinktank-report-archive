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


SERIES_ROLE = "中国科研体系、研发投入与国际科技活动定点全文"

SELECTED_ITEMS = (
    {
        "id": "C-CSET-15208",
        "institution_id": "cset",
        "institution": "Center for Security and Emerging Technology",
        "date": "2023-09-20",
        "title": "The PRC’s Domestic Approach",
        "landing_url": "https://cset.georgetown.edu/publication/the-prcs-domestic-approach/",
        "asset_url": "https://cset.georgetown.edu/wp-content/uploads/20230035_The-PRCs-Domestic-Approach.pdf",
        "axes": "科学体系与科研能力；研发投入与创新政策；科技人才与技能；产业创新与成果转化；国际合作与中国比较",
        "role": "中国科技人才培养、国家重点实验室、创新基础设施、专利制度和技术自立机制的综合入口",
    },
    {
        "id": "C-CSET-15209",
        "institution_id": "cset",
        "institution": "Center for Security and Emerging Technology",
        "date": "2023-09-20",
        "title": "The PRC’s Efforts Abroad",
        "landing_url": "https://cset.georgetown.edu/publication/the-prcs-efforts-abroad/",
        "asset_url": "https://cset.georgetown.edu/wp-content/uploads/20230036_The-PRCs-Efforts-Abroad_FINAL9.20.2023.pdf",
        "axes": "科学体系与科研能力；科技人才与技能；关键与新兴技术；国际合作与中国比较",
        "role": "中国高影响力AI研究、技术标准、科技外交、人才流动和国际研发合作的综合入口",
    },
    {
        "id": "C-EU-JRC-JRC118983",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2019-01-01",
        "title": "The 2019 EU Industrial R&D Investment Scoreboard",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC118983",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC118983/eu_rd_scoreboard_2019_final_online.pdf",
        "axes": "研发投入与创新政策；产业创新与成果转化；创新测量与政策方法；国际合作与中国比较",
        "role": "全球头部企业研发投入、研发强度和中国企业位置的2019比较节点",
    },
    {
        "id": "C-EU-JRC-JRC127360",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2021-01-01",
        "title": "The 2021 EU Industrial R&D Investment Scoreboard",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC127360",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC127360/JRC127360_01.pdf",
        "axes": "研发投入与创新政策；产业创新与成果转化；创新测量与政策方法；国际合作与中国比较",
        "role": "疫情冲击后全球企业研发恢复及中国企业研发结构的2021比较节点",
    },
    {
        "id": "C-EU-JRC-JRC135576",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2023-01-01",
        "title": "The 2023 EU Industrial R&D Investment Scoreboard",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC135576",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC135576/JRC135576_01.pdf",
        "axes": "研发投入与创新政策；产业创新与成果转化；创新测量与政策方法；国际合作与中国比较",
        "role": "绿色与数字技术转型阶段全球头部企业研发及中国企业位置的2023节点",
    },
    {
        "id": "C-EU-JRC-JRC140129",
        "institution_id": "eu-jrc",
        "institution": "European Commission Joint Research Centre",
        "date": "2024-01-01",
        "title": "The 2024 EU Industrial R&D Investment Scoreboard",
        "landing_url": "https://publications.jrc.ec.europa.eu/repository/handle/JRC140129",
        "asset_url": "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC140129/JRC140129_01.pdf",
        "axes": "研发投入与创新政策；产业创新与成果转化；创新测量与政策方法；国际合作与中国比较",
        "role": "全球产业研发竞争、技术领域分布和中国企业研发投入的2024比较节点",
    },
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


def clean_text(text: str) -> str:
    marker = "[REDACTED_CREDENTIAL_SHAPED_EXAMPLE]"
    text = re.sub(r"AKIA[0-9A-Z]{16}", marker, text)
    lines = [marker if re.fullmatch(r"[A-Za-z0-9/+=]{40}", line.strip()) else line.rstrip() for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def extract_pdf(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return clean_text(text), len(reader.pages)


def download_pdf(target: str, landing_url: str, asset_url: str) -> bytes:
    _proxy_json("/navigate?target=" + target + "&url=" + quote(landing_url, safe=""))
    for _ in range(80):
        if int(_eval(target, "document.body?.innerText.length||0")) >= 100:
            break
        time.sleep(0.25)
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


def make_slice(item: dict[str, str], text: str) -> str:
    terms = (
        "science", "scientific", "research", "r&d", "innovation", "technology", "talent",
        "laboratory", "university", "patent", "standard", "collaboration", "cooperation",
        "investment", "china", "chinese", "prc",
    )
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 60]
    selected = [part for part in paragraphs if any(term in part.lower() for term in terms)][:300]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 机构：{item['institution']}\n"
        f"- 科技创新复用角色：{item['role']}\n- 主轴：{item['axes']}\n\n"
        "## 科学技术创新定向摘录\n\n" + "\n\n".join(selected) + "\n"
    )


def update_light_catalog(path: Path, selected_ids: set[str]) -> None:
    rows, fields = read_csv(path)
    changed = False
    for row in rows:
        report_id = row.get("统一目录报告ID") or row.get("报告ID")
        if report_id in selected_ids:
            row["全文策略"] = "已进入中国科研体系、研发投入与国际科技活动定点全文；按官方PDF、提取文本和科技创新切片调用"
            changed = True
    if changed:
        write_csv(path, rows, fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a bounded China research-system and R&D evidence batch.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    catalog, fields = read_csv(catalog_path)
    by_id = {row["报告ID"]: row for row in catalog}
    ids = {item["id"] for item in SELECTED_ITEMS}
    if missing := ids - set(by_id):
        raise RuntimeError(f"selected reports missing from catalog: {sorted(missing)}")
    for item in SELECTED_ITEMS:
        row = by_id[item["id"]]
        if row["发布日期"] != item["date"] or row["报告名称"] != item["title"]:
            raise RuntimeError(f"selected metadata drift: {item['id']}")

    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (pdf_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)

    opened = _proxy_json("/new?url=" + quote(SELECTED_ITEMS[0]["landing_url"], safe=""))
    target = str(opened["targetId"])
    ledger: list[dict[str, str]] = []
    try:
        for index, item in enumerate(SELECTED_ITEMS, 1):
            rid = item["id"]
            pdf_path = pdf_dir / f"{rid}.pdf"
            if not pdf_path.exists() or not pdf_path.read_bytes().startswith(b"%PDF"):
                pdf_path.write_bytes(download_pdf(target, item["landing_url"], item["asset_url"]))
            payload = pdf_path.read_bytes()
            if not payload.startswith(b"%PDF"):
                raise RuntimeError(f"invalid official PDF: {rid}")
            text, pages = extract_pdf(pdf_path)
            if len(text) < 1_000:
                raise RuntimeError(f"extracted PDF text too short: {rid} {len(text)}")
            text_path = text_dir / f"{rid}.txt"
            slice_path = slice_dir / f"{rid}.md"
            text_path.write_text(text, encoding="utf-8", newline="\n")
            slice_path.write_text(make_slice(item, text), encoding="utf-8", newline="\n")
            lower = text.lower()
            china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
            row = by_id[rid]
            row["本地路径"] = str(text_path)
            row["正文完整度"] = "官方PDF全文已保存；同时生成提取文本和科技创新切片"
            row["优先级"] = "P0-China-STI-node"
            row["示踪问题"] = item["axes"] + "；中国科技横向维度"
            row["样本角色"] = SERIES_ROLE
            row["编码状态"] = "全文待观点编码"
            row["预期用途"] = item["role"]
            row["本地原始资产路径"] = str(pdf_path)
            row["原始资产状态"] = "官方PDF已获取并校验"
            ledger.append({
                "报告ID": rid, "机构ID": item["institution_id"], "机构": item["institution"],
                "发布日期": item["date"], "报告名称": item["title"], "官方落地页": item["landing_url"],
                "官方PDF入口": item["asset_url"], "本地原始资产": str(pdf_path), "本地文本": str(text_path),
                "本地切片": str(slice_path), "PDF页数": str(pages), "字节数": str(len(payload)),
                "清洗文本字符数": str(len(text)), "China词形命中数": str(china_hits),
                "SHA256": hashlib.sha256(payload).hexdigest(), "科技创新主轴": item["axes"],
                "科技创新复用角色": item["role"],
                "选择理由": "直接支撑中国科研体系、研发投入、人才、技术创新或国际科技活动；不以安全题名作为选择依据",
                "获取日期": date.today().isoformat(),
            })
            print(f"acquired={index}/{len(SELECTED_ITEMS)} id={rid} pages={pages} chars={len(text)}", flush=True)
    finally:
        try:
            _proxy_json("/close?target=" + target)
        except Exception:
            pass

    catalog.sort(key=lambda row: (row.get("发布日期", ""), row.get("报告ID", "")))
    write_csv(catalog_path, catalog, fields)
    update_light_catalog(root / "75_CSET_2023-2024正式报告轻量目录.csv", ids)
    update_light_catalog(root / "186_欧委会JRC科技创新政策近十年轻量总目录.csv", ids)
    write_csv(root / "216_中国科研体系与企业研发投入定点增补台账.csv", ledger, list(ledger[0]))
    totals = {key: sum(int(row[key]) for row in ledger) for key in ("PDF页数", "字节数", "清洗文本字符数", "China词形命中数")}
    (root / "217_中国科研体系与企业研发投入定点增补结果.md").write_text(
        "# 中国科研体系与企业研发投入定点增补结果\n\n"
        f"- 从既有轻量目录定点选择{len(ledger)}份正式材料：CSET 2份、欧委会JRC 4份。\n"
        f"- 保存6份官方PDF，共{totals['PDF页数']:,}页、{totals['字节数']:,}字节、{totals['清洗文本字符数']:,}个清洗文本字符。\n"
        f"- China/Chinese/PRC词形共命中{totals['China词形命中数']:,}次。\n"
        "- CSET材料覆盖科技人才、国家重点实验室、专利与创新基础设施、科技外交和国际合作；JRC材料形成2019、2021、2023、2024企业研发投入比较节点。\n"
        "- 贸易制裁、军事技术和纯安全治理材料未进入本批全文。\n",
        encoding="utf-8",
    )
    print(f"selected={len(ledger)} pages={totals['PDF页数']} bytes={totals['字节数']} chars={totals['清洗文本字符数']} china_hits={totals['China词形命中数']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
