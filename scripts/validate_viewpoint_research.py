from __future__ import annotations

import argparse
import csv
import hashlib
import zipfile
from pathlib import Path


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


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
        "从开放创新到受控互赖_国际科技智库十年战略转向专报_2026-08-21.docx",
    ]
    missing = [name for name in required if not (root / name).exists()]
    assert not missing, f"missing={missing}"

    seeds = rows(root / "05_官方锚点种子.csv")
    catalog = rows(root / "05_报告总目录.csv")
    evidence = rows(root / "09_观点变化证据表.csv")
    assert len(seeds) == 49, len(seeds)
    assert len(catalog) == 154, len(catalog)
    assert len(evidence) == 24, len(evidence)
    assert len(list((root / "02_机构轨迹卡").glob("*.md"))) == 11
    pdfs = list((root / "03_证据底稿" / "原文PDF").glob("*.pdf"))
    assert len(pdfs) >= 46, len(pdfs)
    assert len(list((root / "03_证据底稿" / "文本").glob("*.txt"))) >= len(pdfs)
    assert len(list((root / "03_证据底稿" / "切片").glob("*.md"))) >= len(pdfs)
    assets = rows(root / "19_本地全文资产台账.csv")
    assert len(assets) == len(seeds)
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in assets) >= 46
    assert all(len(r["SHA256"]) == 64 for r in assets if r["本地PDF"])
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
    assert len(rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv")) >= 1
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv"))
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "06_数据资产" / "数据资产清单.csv"))
    print("viewpoint_research_validation=ok")
    print(f"official_seeds={len(seeds)} catalog={len(catalog)} evidence={len(evidence)} institution_cards=11 pdfs={len(pdfs)}")


if __name__ == "__main__":
    main()
