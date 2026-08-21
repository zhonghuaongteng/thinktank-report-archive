from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import zipfile
from pathlib import Path

from pypdf import PdfReader


logging.getLogger("pypdf").setLevel(logging.ERROR)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def expected_catalog_size(
    seed_count: int,
    catalog_asset_count: int,
    early_asset_count: int,
    cset_asset_count: int,
    atlantic_asset_count: int,
    belfer_asset_count: int = 0,
) -> int:
    return seed_count + catalog_asset_count + early_asset_count + cset_asset_count + atlantic_asset_count + belfer_asset_count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True, type=Path)
    ap.add_argument("--kb", required=True, type=Path)
    args = ap.parse_args()
    root, kb = args.research, args.kb

    required = [
        "00_执行台账.md", "01_研究设计与概念边界.md", "03_编码手册.md",
        "04_既有资料覆盖审计.csv", "05_官方锚点种子.csv", "05_报告总目录.csv",
        "09_观点变化证据表.csv", "10_长期核心观点表.csv", "11_新观点检验表.csv",
        "12_机构群体构成变化表.csv", "13_竞争性解释与零假设.md", "14_政策吸收验证表.csv",
        "15_反证与异常机构清单.md", "16_信度检验记录.md", "17_战略故事候选稿.md", "18_专报主稿.md",
        "23_早期旗舰报告增补台账.csv", "24_早期旗舰报告增补结果.md",
        "25_早期连续覆盖矩阵.csv", "26_早期材料主题索引.csv",
        "27_CSET涉华科技专题增补台账.csv", "28_CSET涉华科技专题增补结果.md",
        "29_CSET涉华科技主题索引.csv", "30_CSET涉华科技复用矩阵.csv",
        "31_Atlantic_Council涉华科技专题增补台账.csv", "32_Atlantic_Council涉华科技专题增补结果.md",
        "33_Atlantic_Council涉华科技主题索引.csv", "34_Atlantic_Council涉华科技复用矩阵.csv",
        "35_Belfer涉华科技专题增补台账.csv", "36_Belfer涉华科技专题增补结果.md",
        "37_Belfer涉华科技主题索引.csv", "38_Belfer涉华科技复用矩阵.csv",
        "从开放创新到受控互赖_国际科技智库十年战略转向专报_2026-08-21.docx",
    ]
    missing = [name for name in required if not (root / name).exists()]
    assert not missing, f"missing={missing}"

    seeds = rows(root / "05_官方锚点种子.csv")
    catalog = rows(root / "05_报告总目录.csv")
    evidence = rows(root / "09_观点变化证据表.csv")
    assert len(seeds) == 49, len(seeds)
    assert len(evidence) == 24, len(evidence)
    assert len(list((root / "02_机构轨迹卡").glob("*.md"))) == 11
    pdfs = list((root / "03_证据底稿" / "原文PDF").glob("*.pdf"))
    assert len(list((root / "03_证据底稿" / "文本").glob("*.txt"))) >= len(pdfs)
    assert len(list((root / "03_证据底稿" / "切片").glob("*.md"))) >= len(pdfs)
    assets = rows(root / "19_本地全文资产台账.csv")
    assert len(assets) == len(seeds)
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in assets) >= 46
    assert all(len(r["SHA256"]) == 64 for r in assets if r["本地PDF"])
    catalog_assets = rows(root / "21_非锚点全文补存台账.csv")
    assert len(catalog_assets) == 105, len(catalog_assets)
    assert sum(r["资产类型"] == "PDF" for r in catalog_assets) == 102
    assert sum(r["资产类型"] == "官方网页" for r in catalog_assets) == 3
    assert all(r["本地资产"] and Path(r["本地资产"]).exists() for r in catalog_assets)
    assert not any(r["本地状态"] == "获取失败" for r in catalog_assets)
    early_assets = rows(root / "23_早期旗舰报告增补台账.csv")
    assert len(early_assets) == 47, len(early_assets)
    assert all(r["本地状态"] == "官方PDF已保存并校验" for r in early_assets)
    assert all(r["本地PDF"] and Path(r["本地PDF"]).exists() for r in early_assets)
    assert all(len(r["SHA256"]) == 64 for r in early_assets)
    assert {r["报告ID"] for r in early_assets}.issubset({r["报告ID"] for r in catalog})
    early_matrix = rows(root / "25_早期连续覆盖矩阵.csv")
    early_topics = rows(root / "26_早期材料主题索引.csv")
    assert len(early_matrix) == 11, len(early_matrix)
    assert all(r["连续性判断"] == "W1/W2均有样本" for r in early_matrix)
    assert len(early_topics) == len(early_assets)
    assert all(Path(r["逐页文本"]).exists() and Path(r["示踪切片"]).exists() for r in early_topics)
    cset_assets = rows(root / "27_CSET涉华科技专题增补台账.csv")
    assert len(cset_assets) == 104, len(cset_assets)
    assert sum(r["材料类型"] == "CSET原创研究报告" for r in cset_assets) == 60
    assert sum(r["材料类型"] == "中国科技政策英译" for r in cset_assets) == 35
    assert sum(r["材料类型"] == "涉华科技政策证词" for r in cset_assets) == 9
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in cset_assets) == 103
    assert sum(r["本地状态"] == "官方网页全文已保存" for r in cset_assets) == 1
    assert not any(r["本地状态"] == "获取失败" for r in cset_assets)
    assert all(r["本地原始资产"] and Path(r["本地原始资产"]).exists() for r in cset_assets)
    assert all(r["本地文本"] and Path(r["本地文本"]).exists() for r in cset_assets)
    assert all(r["本地切片或转写"] and Path(r["本地切片或转写"]).exists() for r in cset_assets)
    assert all(len(r["SHA256"]) == 64 for r in cset_assets)
    assert {r["报告ID"] for r in cset_assets}.issubset({r["报告ID"] for r in catalog})
    cset_topics = rows(root / "29_CSET涉华科技主题索引.csv")
    cset_matrix = rows(root / "30_CSET涉华科技复用矩阵.csv")
    assert len(cset_topics) >= len(cset_assets)
    assert cset_matrix
    assert {r["材料类型"] for r in cset_topics} == {"CSET原创研究报告", "中国科技政策英译", "涉华科技政策证词"}
    cset_catalog = [r for r in catalog if r["报告ID"].startswith("C-CSET-")]
    assert len(cset_catalog) == len(cset_assets)
    assert all(r["机构观点等级"] == "翻译材料，不代表机构观点" for r in cset_catalog if r["报告类型"] == "中国科技政策英译")
    atlantic_assets = rows(root / "31_Atlantic_Council涉华科技专题增补台账.csv")
    assert len(atlantic_assets) == 95, len(atlantic_assets)
    assert sum(r["材料类型"] == "正式研究报告" for r in atlantic_assets) == 47
    assert sum(r["材料类型"] == "深度研究报告" for r in atlantic_assets) == 3
    assert sum(r["材料类型"] == "议题简报" for r in atlantic_assets) == 34
    assert sum(r["材料类型"] == "Atlantic Council战略论文" for r in atlantic_assets) == 11
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in atlantic_assets) == 53
    assert sum(r["本地状态"] == "关联既有官方PDF" for r in atlantic_assets) == 4
    assert sum(r["本地状态"] == "官方网页全文已保存" for r in atlantic_assets) == 38
    assert not any(r["本地状态"] == "获取失败" for r in atlantic_assets)
    assert all(r["本地原始资产"] and Path(r["本地原始资产"]).exists() for r in atlantic_assets)
    assert all(r["本地文本"] and Path(r["本地文本"]).exists() for r in atlantic_assets)
    assert all(r["本地切片或转写"] and Path(r["本地切片或转写"]).exists() for r in atlantic_assets)
    assert all(len(r["SHA256"]) == 64 for r in atlantic_assets)
    assert {r["报告ID"] for r in atlantic_assets}.issubset({r["报告ID"] for r in catalog})
    atlantic_topics = rows(root / "33_Atlantic_Council涉华科技主题索引.csv")
    atlantic_matrix = rows(root / "34_Atlantic_Council涉华科技复用矩阵.csv")
    assert len(atlantic_topics) >= len(atlantic_assets)
    assert atlantic_matrix
    atlantic_catalog = [r for r in catalog if r["报告ID"].startswith("C-ATL-")]
    assert len(atlantic_catalog) == len(atlantic_assets)
    assert all(
        r["机构观点等级"] == "作者/项目政策简报"
        for r in atlantic_catalog if r["报告类型"] == "议题简报"
    )
    belfer_assets = rows(root / "35_Belfer涉华科技专题增补台账.csv")
    assert len(belfer_assets) == 29, len(belfer_assets)
    assert sum(r["材料类型"] == "研究报告与论文" for r in belfer_assets) == 22
    assert sum(r["材料类型"] == "政策简报" for r in belfer_assets) == 4
    assert sum(r["材料类型"] == "政策证词" for r in belfer_assets) == 3
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in belfer_assets) == 20
    assert sum(r["本地状态"] == "官方网页全文已保存" for r in belfer_assets) == 9
    assert not any(r["本地状态"] == "获取失败" for r in belfer_assets)
    assert all(r["本地原始资产"] and Path(r["本地原始资产"]).exists() for r in belfer_assets)
    assert all(r["本地文本"] and Path(r["本地文本"]).exists() for r in belfer_assets)
    assert all(r["本地切片或转写"] and Path(r["本地切片或转写"]).exists() for r in belfer_assets)
    assert all(len(r["SHA256"]) == 64 for r in belfer_assets)
    assert {r["报告ID"] for r in belfer_assets}.issubset({r["报告ID"] for r in catalog})
    belfer_topics = rows(root / "37_Belfer涉华科技主题索引.csv")
    belfer_matrix = rows(root / "38_Belfer涉华科技复用矩阵.csv")
    assert len(belfer_topics) >= len(belfer_assets)
    assert belfer_matrix
    belfer_catalog = [r for r in catalog if r["报告ID"].startswith("C-BEL-")]
    assert len(belfer_catalog) == len(belfer_assets)
    assert all(
        r["机构观点等级"] == "作者/项目政策证词"
        for r in belfer_catalog if r["报告类型"] == "政策证词"
    )
    assert len(catalog) == expected_catalog_size(
        seed_count=len(seeds),
        catalog_asset_count=len(catalog_assets),
        early_asset_count=len(early_assets),
        cset_asset_count=len(cset_assets),
        atlantic_asset_count=len(atlantic_assets),
        belfer_asset_count=len(belfer_assets),
    ), len(catalog)
    expected_pdf_paths = {
        Path(value).resolve()
        for ledger, fields in (
            (assets, ("本地PDF",)),
            (catalog_assets, ("本地资产",)),
            (early_assets, ("本地PDF",)),
            (cset_assets, ("本地原始资产",)),
            (atlantic_assets, ("本地原始资产",)),
            (belfer_assets, ("本地原始资产",)),
        )
        for row in ledger
        for field in fields
        for value in (row.get(field, ""),)
        if value and Path(value).suffix.lower() == ".pdf"
    }
    assert {pdf.resolve() for pdf in pdfs} == expected_pdf_paths
    pdf_hashes: set[str] = set()
    for pdf in pdfs:
        assert pdf.read_bytes()[:4] == b"%PDF", pdf
        digest = sha(pdf)
        assert digest not in pdf_hashes, f"duplicate PDF hash: {pdf}"
        pdf_hashes.add(digest)
        page_count = len(PdfReader(str(pdf)).pages)
        text_path = root / "03_证据底稿" / "文本" / f"{pdf.stem}.txt"
        assert page_count > 0
        assert len(text_path.read_text(encoding="utf-8")) / page_count >= 200, pdf
    expected_web = {"L-7D859D5B15", "L-45F9A8A2BD", "L-69CC5834D1"}
    assert {r["报告ID"] for r in catalog_assets if r["资产类型"] == "官方网页"} == expected_web
    assert {r["观察窗"] for r in seeds} == {"W1", "W2", "W3"}
    assert all(r["官方页面或PDF"].startswith("https://") for r in seeds)
    seed_text = (root / "05_官方锚点种子.csv").read_text(encoding="utf-8-sig")
    assert "mobilizing-for-techno-economic-war-part-1" in seed_text
    assert "without-fundamental-policy-change-us-risks-losing-techno-economic-trade-war-with-china/" not in seed_text
    assert "The United States and China—Designing a Shared Future" in seed_text
    assert "The Effectiveness of U.S. Economic Policies Regarding China Pursued from 2017 to 2024" in seed_text

    docx = root / required[-1]
    assert zipfile.is_zipfile(docx)
    with zipfile.ZipFile(docx) as zf:
        names = set(zf.namelist())
        assert "word/document.xml" in names
        xml = zf.read("word/document.xml").decode("utf-8")
        assert "从开放创新到受控互赖" in xml
        assert "国际主要科技智库" in xml

    kb_catalog = kb / "06_数据资产" / "国际科技智库观点演变_官方报告目录_2016-2026.csv"
    kb_evidence = kb / "06_数据资产" / "国际科技智库观点演变_观点变化证据表.csv"
    assert sha(root / "05_报告总目录.csv") == sha(kb_catalog)
    assert sha(root / "09_观点变化证据表.csv") == sha(kb_evidence)
    for source_name, kb_name in (
        ("31_Atlantic_Council涉华科技专题增补台账.csv", "国际科技智库观点演变_Atlantic_Council涉华科技专题增补台账.csv"),
        ("33_Atlantic_Council涉华科技主题索引.csv", "国际科技智库观点演变_Atlantic_Council涉华科技主题索引.csv"),
        ("34_Atlantic_Council涉华科技复用矩阵.csv", "国际科技智库观点演变_Atlantic_Council涉华科技复用矩阵.csv"),
        ("35_Belfer涉华科技专题增补台账.csv", "国际科技智库观点演变_Belfer涉华科技专题增补台账.csv"),
        ("37_Belfer涉华科技主题索引.csv", "国际科技智库观点演变_Belfer涉华科技主题索引.csv"),
        ("38_Belfer涉华科技复用矩阵.csv", "国际科技智库观点演变_Belfer涉华科技复用矩阵.csv"),
    ):
        assert sha(root / source_name) == sha(kb / "06_数据资产" / kb_name)
    assert len(rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv")) >= 1
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv"))
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "06_数据资产" / "数据资产清单.csv"))
    print("viewpoint_research_validation=ok")
    print(f"official_seeds={len(seeds)} catalog={len(catalog)} evidence={len(evidence)} institution_cards=11 pdfs={len(pdfs)} non_anchor_assets={len(catalog_assets)} early_assets={len(early_assets)} cset_assets={len(cset_assets)} atlantic_assets={len(atlantic_assets)} belfer_assets={len(belfer_assets)}")


if __name__ == "__main__":
    main()
