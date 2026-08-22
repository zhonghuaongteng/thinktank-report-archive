from __future__ import annotations

import csv
import hashlib
from datetime import date
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from extract_viewpoint_pdf_slices import process_pdf


USER_AGENT = "Mozilla/5.0 (compatible; ThinktankResearchArchive/1.0)"


def clean_html_text(data: bytes) -> str:
    soup = BeautifulSoup(data, "html.parser")
    for node in soup.select("script, style, nav, header, footer, aside"):
        node.decompose()
    content = soup.select_one("article, .entry-content, main, #content") or soup
    lines = [line.strip() for line in content.get_text("\n", strip=True).splitlines()]
    return "\n".join(line for line in lines if line)


def fetch(url: str) -> bytes:
    response = httpx.get(url, follow_redirects=True, timeout=180, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.content


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "国际主要科技智库观点演变_研判"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    snapshot_dir = root / "03_证据底稿" / "网页快照"
    web_text_dir = root / "03_证据底稿" / "网页文本"
    transcript_dir = root / "03_证据底稿" / "网页转写"
    for directory in (pdf_dir, text_dir, slice_dir, snapshot_dir, web_text_dir, transcript_dir):
        directory.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    today = date.today().isoformat()

    hub_url = "https://www.nistep.go.jp/research/science-and-technology-indicators-and-scientometrics/sciencemap/"
    hub_data = fetch(hub_url)
    hub_text = clean_html_text(hub_data)
    if len(hub_text) < 3000:
        raise RuntimeError(f"NISTEP Science Map hub text too short: {len(hub_text)}")
    hub_id = "S-NISTEP-SCIENCEMAP-HUB"
    hub_snapshot = snapshot_dir / f"{hub_id}.html"
    hub_local_text = web_text_dir / f"{hub_id}.txt"
    hub_transcript = transcript_dir / f"{hub_id}.md"
    hub_snapshot.write_bytes(hub_data)
    hub_local_text.write_text(hub_text, encoding="utf-8")
    hub_transcript.write_text(
        "# NISTEP Science Map专题页\n\n"
        f"- 官方来源：{hub_url}\n- 获取日期：{today}\n"
        "- 使用边界：用于补强Science Map 2018/2020的专题结构、可视化入口和历年连续性；不替代NR187、NR196逐页精确引用。\n\n"
        + hub_text,
        encoding="utf-8",
    )
    rows.append({
        "补充资产ID": hub_id,
        "关联正式报告": "NR:187；NR:196",
        "证据关系": "NISTEP官方专题页连续序列",
        "发布机构": "NISTEP",
        "题名": "Science Map专题页",
        "官方链接": hub_url,
        "本地原始资产": str(hub_snapshot),
        "本地文本": str(hub_local_text),
        "本地切片或转写": str(hub_transcript),
        "资产类型": "官方HTML专题页",
        "字节数": str(len(hub_data)),
        "PDF页数": "0",
        "提取文本字符数": str(len(hub_text)),
        "SHA256": sha256(hub_data),
        "使用边界": "补强Science Map连续性和专题结构；精确观点仍回查正式报告全文或官方摘要",
        "获取日期": today,
    })

    pdf_sources = [
        {
            "id": "S-NISTEP-STIH00411",
            "related": "RM:348",
            "relation": "NISTEP官方后续全文解读",
            "institution": "NISTEP",
            "title": "人工知能分野における国・地域別の発表概況（2025）－国際会議及びOpenAlexに基づく分析－",
            "url": "https://www.nistep.go.jp/wp/wp-content/uploads/NISTEP-STIH11-4-00411.pdf",
            "boundary": "补强RM348的十年AI科研产出、中国追赶和国际共著分析；文种为STI Horizon解读稿",
        },
        {
            "id": "S-RIETI-21E025",
            "related": "DP:192",
            "relation": "共同作者机构正式英文版本",
            "institution": "RIETI",
            "title": "New Indicator of Science and Technology Inter-Relationship by Using Text Information of Research Articles and Patents in Japan",
            "url": "https://www.rieti.go.jp/jp/publications/dp/21e025.pdf",
            "boundary": "补强DP192的论文—专利双向知识联系分析；版本来自共同作者所属RIETI，机构归因不转写为NISTEP",
        },
    ]
    for item in pdf_sources:
        data = fetch(item["url"])
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"not a PDF: {item['url']}")
        pdf_path = pdf_dir / f"{item['id']}.pdf"
        pdf_path.write_bytes(data)
        process_pdf(pdf_path, text_dir, slice_dir)
        text_path = text_dir / f"{item['id']}.txt"
        slice_path = slice_dir / f"{item['id']}.md"
        extracted = text_path.read_text(encoding="utf-8", errors="replace")
        pages = len(PdfReader(pdf_path).pages)
        if len(extracted) < 1000:
            raise RuntimeError(f"thin extracted PDF text: {item['id']} {len(extracted)}")
        rows.append({
            "补充资产ID": item["id"],
            "关联正式报告": item["related"],
            "证据关系": item["relation"],
            "发布机构": item["institution"],
            "题名": item["title"],
            "官方链接": item["url"],
            "本地原始资产": str(pdf_path),
            "本地文本": str(text_path),
            "本地切片或转写": str(slice_path),
            "资产类型": "正式PDF补充证据",
            "字节数": str(len(data)),
            "PDF页数": str(pages),
            "提取文本字符数": str(len(extracted)),
            "SHA256": sha256(data),
            "使用边界": item["boundary"],
            "获取日期": today,
        })

    fields = [
        "补充资产ID", "关联正式报告", "证据关系", "发布机构", "题名", "官方链接",
        "本地原始资产", "本地文本", "本地切片或转写", "资产类型", "字节数",
        "PDF页数", "提取文本字符数", "SHA256", "使用边界", "获取日期",
    ]
    write_csv(root / "120_NISTEP科技创新主轴补充证据台账.csv", rows, fields)
    total_pages = sum(int(row["PDF页数"]) for row in rows)
    total_chars = sum(int(row["提取文本字符数"]) for row in rows)
    total_bytes = sum(int(row["字节数"]) for row in rows)
    result = [
        "# NISTEP科技创新主轴补充证据结果",
        "",
        f"- 新增补充证据资产：{len(rows)}项。",
        f"- PDF：2项，共{total_pages}页；官方HTML专题页：1项。",
        f"- 可检索文本：{total_chars:,}字符；原始资产：{total_bytes:,}字节。",
        "- 关联正式报告：NR187、NR196、DP192、RM348。",
        "",
        "## 采集判断",
        "",
        "本批围绕科学计量、科学—技术知识流动与人工智能科研态势补充证据。NISTEP仓储旧式正式PDF链接当前受到访问限制，保留正式报告摘要和已核验的FullJ元数据，同时优先保存同一机构专题页、同一研究的共同作者机构正式版本，以及NISTEP后续完整解读稿。",
        "",
        "RM290已有DP172正式全文与RM292代理全文支撑，RM346已有NR208综合报告代理全文支撑，本批不重复下载。安全、供应链和治理材料未进入补充范围。",
        "",
        "## 使用边界",
        "",
        "补充资产可用于主题理解、趋势识别和候选观点筛选。涉及NR187、NR196、RM348、DP192的逐页精确引文时，仍需回查对应正式报告原文；RIETI版本保持RIETI归因。",
    ]
    (root / "121_NISTEP科技创新主轴补充证据结果.md").write_text("\n".join(result), encoding="utf-8")
    print(f"assets={len(rows)} pdfs=2 pages={total_pages} chars={total_chars} bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
