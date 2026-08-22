from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import re
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
    nbr_asset_count: int = 0,
    merics_asset_count: int = 0,
    bruegel_asset_count: int = 0,
    crds_asset_count: int = 0,
    nistep_asset_count: int = 0,
    stepi_asset_count: int = 0,
    kistep_asset_count: int = 0,
    light_catalog_count: int = 0,
) -> int:
    return seed_count + catalog_asset_count + early_asset_count + cset_asset_count + atlantic_asset_count + belfer_asset_count + nbr_asset_count + merics_asset_count + bruegel_asset_count + crds_asset_count + nistep_asset_count + stepi_asset_count + kistep_asset_count + light_catalog_count


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
        "39_NBR科技与中国专题增补台账.csv", "40_NBR科技与中国专题增补结果.md",
        "41_NBR科技与中国主题索引.csv", "42_NBR科技与中国复用矩阵.csv",
        "43_MERICS科技与中国专题增补台账.csv", "44_MERICS科技与中国专题增补结果.md",
        "45_MERICS科技与中国主题索引.csv", "46_MERICS科技与中国复用矩阵.csv",
        "47_Bruegel科技与中国专题增补台账.csv", "48_Bruegel科技与中国专题增补结果.md",
        "49_Bruegel科技与中国主题索引.csv", "50_Bruegel科技与中国复用矩阵.csv",
        "51_CRDS日文科技与中国专题增补台账.csv", "52_CRDS日文科技与中国专题增补结果.md",
        "53_CRDS日文科技与中国主题索引.csv", "54_CRDS日文科技与中国复用矩阵.csv",
        "55_NISTEP日文科技与中国专题增补台账.csv", "56_NISTEP日文科技与中国专题增补结果.md",
        "57_NISTEP日文科技与中国主题索引.csv", "58_NISTEP日文科技与中国复用矩阵.csv",
        "59_CRDS_NISTEP科技主题与机构功能对照.csv",
        "60_STEPI韩文科技与中国专题增补台账.csv", "61_STEPI韩文科技与中国专题增补结果.md",
        "62_STEPI韩文科技与中国主题索引.csv", "63_STEPI韩文科技与中国复用矩阵.csv",
        "64_KISTEP韩文正式报告总目录与重点附件台账.csv", "65_KISTEP韩文正式报告总目录与重点附件结果.md",
        "66_KISTEP韩文科技与中国主题索引.csv", "67_KISTEP韩文科技与中国复用矩阵.csv",
        "68_智库分层与转向节点采集矩阵.md",
        "69_机构节点主题覆盖缺口矩阵.csv", "70_定点补源优先队列.csv",
        "71_覆盖缺口结果.md", "72_轻量目录扩展优先队列.csv",
        "73_STEPI中国先进技术连续序列附卷台账.csv", "74_STEPI中国先进技术连续序列结果.md",
        "75_CSET_2023-2024正式报告轻量目录.csv", "76_CSET_2023-2024正式报告轻量目录结果.md",
        "77_OECD_STI正式系列轻量目录.csv", "78_OECD_STI正式系列轻量目录结果.md",
        "79_ITIF中国先进产业创新系列轻量目录.csv", "80_ITIF中国先进产业创新系列轻量目录结果.md",
        "81_科学技术创新主轴采集规则.md",
        "82_ITIF科学技术创新节点轻量目录.csv", "83_ITIF科学技术创新节点轻量目录结果.md",
        "84_Fraunhofer_ISI创新系统政策分析轻量目录.csv", "85_Fraunhofer_ISI创新系统政策分析轻量目录结果.md",
        "86_Stanford_HAI科学技术创新轻量目录.csv", "87_Stanford_HAI科学技术创新轻量目录结果.md",
        "88_美国OSTP科学技术创新政策轻量目录.csv", "89_美国OSTP科学技术创新政策轻量目录结果.md",
        "90_Belfer_MERICS科学技术创新缺口轻量目录.csv", "91_Belfer_MERICS科学技术创新缺口轻量目录结果.md",
        "92_定点全文候选证据增量复核台账.csv", "93_定点全文候选证据增量复核结果.md",
        "94_第二批定点全文候选证据增量复核台账.csv", "95_第二批定点全文候选证据增量复核结果.md",
        "96_第三批定点全文候选证据增量复核台账.csv", "97_第三批定点全文候选证据增量复核结果.md",
        "98_第四批定点全文候选证据增量复核台账.csv", "99_第四批定点全文候选证据增量复核结果.md",
        "100_第五批定点全文候选证据增量复核台账.csv", "101_第五批定点全文候选证据增量复核结果.md",
        "102_第六批定点全文候选证据增量复核台账.csv", "103_第六批定点全文候选证据增量复核结果.md",
        "104_第七批中国科技创新全文候选复核台账.csv", "105_第七批中国科技创新全文候选复核结果.md",
        "106_第八批科技创新与中国比较全文候选复核台账.csv", "107_第八批科技创新与中国比较全文候选复核结果.md",
        "108_第九批科学体系与创新政策纵向全文候选复核台账.csv", "109_第九批科学体系与创新政策纵向全文候选复核结果.md",
        "110_第十批OECD科学体系与科研机制纵向全文候选复核台账.csv", "111_第十批OECD科学体系与科研机制纵向全文候选复核结果.md",
        "112_STEPI韩文扫描件OCR补全台账.csv", "113_STEPI韩文扫描件OCR补全结果.md",
        "114_KISTEP高价值韩文扫描件OCR补全台账.csv", "115_KISTEP高价值韩文扫描件OCR补全结果.md",
        "116_KISTEP科技政策与AI半导体扫描件OCR补全台账.csv", "117_KISTEP科技政策与AI半导体扫描件OCR补全结果.md",
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
    assert len(catalog_assets) == 231, len(catalog_assets)
    assert sum(r["资产类型"] == "PDF" for r in catalog_assets) == 228
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
    assert {r["报告ID"] for r in cset_assets}.issubset({r["报告ID"] for r in cset_catalog})
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
    nbr_assets = rows(root / "39_NBR科技与中国专题增补台账.csv")
    assert len(nbr_assets) == 89, len(nbr_assets)
    assert sum(r["材料类型"] == "NBR研究报告" for r in nbr_assets) == 17
    assert sum(r["材料类型"] == "NBR政策简报" for r in nbr_assets) == 20
    assert sum(r["材料类型"] == "NBR评论" for r in nbr_assets) == 29
    assert sum(r["材料类型"] == "NBR访谈" for r in nbr_assets) == 13
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in nbr_assets) == 32
    assert sum(r["本地状态"] == "官方网页全文已保存" for r in nbr_assets) == 50
    assert sum(r["本地状态"] == "官方页面代理全文已保存" for r in nbr_assets) == 7
    assert not any(r["本地状态"] == "获取失败" for r in nbr_assets)
    assert sum(r["中国关联层级"] == "直接涉华科技" for r in nbr_assets) == 19
    assert sum(r["中国关联层级"] == "含中国比较的印太技术材料" for r in nbr_assets) == 48
    assert sum(r["中国关联层级"] == "区域技术基线" for r in nbr_assets) == 22
    assert sum(r["科技关联层级"] == "核心科技直接材料" for r in nbr_assets) == 62
    assert sum(r["科技关联层级"] == "科技地缘经济基线" for r in nbr_assets) == 27
    assert all(r["本地原始资产"] and Path(r["本地原始资产"]).exists() for r in nbr_assets)
    assert all(r["本地文本"] and Path(r["本地文本"]).exists() for r in nbr_assets)
    assert all(r["本地切片或转写"] and Path(r["本地切片或转写"]).exists() for r in nbr_assets)
    assert all(len(r["SHA256"]) == 64 for r in nbr_assets)
    assert {r["报告ID"] for r in nbr_assets}.issubset({r["报告ID"] for r in catalog})
    nbr_topics = rows(root / "41_NBR科技与中国主题索引.csv")
    nbr_matrix = rows(root / "42_NBR科技与中国复用矩阵.csv")
    assert len(nbr_topics) == 305, len(nbr_topics)
    assert len(nbr_matrix) == 119, len(nbr_matrix)
    nbr_catalog = [r for r in catalog if r["报告ID"].startswith("C-NBR-")]
    assert len(nbr_catalog) == len(nbr_assets)
    assert all(
        r["机构观点等级"] == "作者访谈"
        for r in nbr_catalog if r["报告类型"] == "NBR访谈"
    )
    merics_assets = rows(root / "43_MERICS科技与中国专题增补台账.csv")
    assert len(merics_assets) == 62, len(merics_assets)
    assert sum(r["本地状态"] == "复用库内既有资产" for r in merics_assets) == 22
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in merics_assets) == 33
    assert sum(r["本地状态"] == "关联既有官方PDF" for r in merics_assets) == 3
    assert sum(r["本地状态"] == "官方网页全文已保存" for r in merics_assets) == 4
    assert not any(r["本地状态"] == "获取失败" for r in merics_assets)
    assert sum(r["科技关联层级"] == "核心科技直接材料" for r in merics_assets) == 42
    assert sum(r["科技关联层级"] == "科技产业与经济安全基线" for r in merics_assets) == 20
    assert sum(r["观察窗"] == "W1" for r in merics_assets) == 3
    assert sum(r["观察窗"] == "W2" for r in merics_assets) == 16
    assert sum(r["观察窗"] == "W3" for r in merics_assets) == 43
    assert all(r["本地原始资产"] and Path(r["本地原始资产"]).exists() for r in merics_assets)
    assert all(r["本地文本"] and Path(r["本地文本"]).exists() for r in merics_assets)
    assert all(r["本地切片或转写"] and Path(r["本地切片或转写"]).exists() for r in merics_assets)
    assert all(len(r["SHA256"]) == 64 for r in merics_assets)
    assert {r["报告ID"] for r in merics_assets}.issubset({r["报告ID"] for r in catalog})
    assert len(rows(root / "45_MERICS科技与中国主题索引.csv")) == 170
    assert len(rows(root / "46_MERICS科技与中国复用矩阵.csv")) == 59
    merics_catalog = [r for r in catalog if r["报告ID"].startswith("C-MERICS-")]
    assert len(merics_catalog) == 40, len(merics_catalog)
    assert all(r["机构观点等级"] == "作者/项目正式研究" for r in merics_catalog)
    bruegel_assets = rows(root / "47_Bruegel科技与中国专题增补台账.csv")
    assert len(bruegel_assets) == 90, len(bruegel_assets)
    assert sum(r["本地状态"] == "复用库内既有资产" for r in bruegel_assets) == 2
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in bruegel_assets) == 55
    assert sum(r["本地状态"] == "关联既有官方PDF" for r in bruegel_assets) == 2
    assert sum(r["本地状态"] == "官方网页全文已保存" for r in bruegel_assets) == 31
    assert not any(r["本地状态"] == "获取失败" for r in bruegel_assets)
    assert sum(r["科技关联层级"] == "核心科技直接材料" for r in bruegel_assets) == 56
    assert sum(r["科技关联层级"] == "科技产业与经济安全基线" for r in bruegel_assets) == 34
    assert sum(r["观察窗"] == "W1" for r in bruegel_assets) == 8
    assert sum(r["观察窗"] == "W2" for r in bruegel_assets) == 12
    assert sum(r["观察窗"] == "W3" for r in bruegel_assets) == 70
    assert all(r["本地原始资产"] and Path(r["本地原始资产"]).exists() for r in bruegel_assets)
    assert all(r["本地文本"] and Path(r["本地文本"]).exists() for r in bruegel_assets)
    assert all(r["本地切片或转写"] and Path(r["本地切片或转写"]).exists() for r in bruegel_assets)
    assert all(len(r["SHA256"]) == 64 for r in bruegel_assets)
    assert {r["报告ID"] for r in bruegel_assets}.issubset({r["报告ID"] for r in catalog})
    assert len(rows(root / "49_Bruegel科技与中国主题索引.csv")) == 129
    assert len(rows(root / "50_Bruegel科技与中国复用矩阵.csv")) == 38
    bruegel_catalog = [r for r in catalog if r["报告ID"].startswith("C-BRUEGEL-")]
    assert len(bruegel_catalog) == 88, len(bruegel_catalog)
    assert all(r["机构观点等级"] == "作者/项目正式研究" for r in bruegel_catalog)
    crds_assets = rows(root / "51_CRDS日文科技与中国专题增补台账.csv")
    assert len(crds_assets) == 209, len(crds_assets)
    assert sum(r["本地状态"] == "复用库内既有资产" for r in crds_assets) == 17
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in crds_assets) == 192
    assert not any(r["本地状态"] in {"关联既有官方PDF", "获取失败"} for r in crds_assets)
    assert sum(r["报告类型"] == "研究开发全景报告" for r in crds_assets) == 49
    assert sum(r["报告类型"] == "调查分析报告" for r in crds_assets) == 77
    assert sum(r["报告类型"] == "海外科技政策调查" for r in crds_assets) == 17
    assert sum(r["报告类型"] == "研究推进战略建议" for r in crds_assets) == 66
    assert sum(r["观察窗"] == "W1" for r in crds_assets) == 32
    assert sum(r["观察窗"] == "W2" for r in crds_assets) == 65
    assert sum(r["观察窗"] == "W3" for r in crds_assets) == 112
    assert all(r["科技关联层级"] == "核心科技直接材料" for r in crds_assets)
    assert all(r["本地原始资产"] and Path(r["本地原始资产"]).exists() for r in crds_assets)
    assert all(r["本地文本"] and Path(r["本地文本"]).exists() for r in crds_assets)
    assert all(r["本地切片或转写"] and Path(r["本地切片或转写"]).exists() for r in crds_assets)
    assert all(len(r["SHA256"]) == 64 for r in crds_assets)
    assert {r["报告ID"] for r in crds_assets}.issubset({r["报告ID"] for r in catalog})
    assert len(rows(root / "53_CRDS日文科技与中国主题索引.csv")) == 1389
    assert len(rows(root / "54_CRDS日文科技与中国复用矩阵.csv")) == 45
    crds_catalog = [r for r in catalog if r["报告ID"].startswith("C-CRDS-FY")]
    assert len(crds_catalog) == 192, len(crds_catalog)
    assert all(r["机构观点等级"] == "机构正式研究" for r in crds_catalog)
    nistep_assets = rows(root / "55_NISTEP日文科技与中国专题增补台账.csv")
    assert len(nistep_assets) == 283, len(nistep_assets)
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in nistep_assets) == 150
    assert sum(r["本地状态"] == "官方仓储PDF代理全文已保存" for r in nistep_assets) == 100
    assert sum(r["本地状态"] == "官方HTML版报告已保存" for r in nistep_assets) == 6
    assert sum(r["本地状态"] == "官方发布页摘要已保存" for r in nistep_assets) == 26
    assert sum(r["本地状态"] == "获取失败" for r in nistep_assets) == 1
    assert sum(r["报告类型"] == "NISTEP正式报告" for r in nistep_assets) == 48
    assert sum(r["报告类型"] == "政策研究" for r in nistep_assets) == 1
    assert sum(r["报告类型"] == "调查资料" for r in nistep_assets) == 111
    assert sum(r["报告类型"] == "讨论论文" for r in nistep_assets) == 123
    assert sum(r["观察窗"] == "W1" for r in nistep_assets) == 85
    assert sum(r["观察窗"] == "W2" for r in nistep_assets) == 86
    assert sum(r["观察窗"] == "W3" for r in nistep_assets) == 112
    assert sum(r["资料角色"] == "机构正式研究" for r in nistep_assets) == 160
    assert sum(r["资料角色"] == "作者讨论论文" for r in nistep_assets) == 123
    assert sum("中国" in r["主题标签"] for r in nistep_assets) == 44
    assert all(
        r["本地原始资产"] and Path(r["本地原始资产"]).exists()
        and r["本地文本"] and Path(r["本地文本"]).exists()
        and r["本地切片或转写"] and Path(r["本地切片或转写"]).exists()
        and len(r["SHA256"]) == 64
        for r in nistep_assets if r["本地状态"] != "获取失败"
    )
    assert all(not r["本地原始资产"] and not r["SHA256"] for r in nistep_assets if r["本地状态"] == "获取失败")
    assert len(rows(root / "57_NISTEP日文科技与中国主题索引.csv")) == 1601
    assert len(rows(root / "58_NISTEP日文科技与中国复用矩阵.csv")) == 272
    comparison = rows(root / "59_CRDS_NISTEP科技主题与机构功能对照.csv")
    assert len(comparison) == 20, len(comparison)
    assert {r["机构"] for r in comparison if r["对照层级"] == "机构总览"} == {"CRDS", "NISTEP"}
    nistep_overview = next(r for r in comparison if r["对照层级"] == "机构总览" and r["机构"] == "NISTEP")
    assert nistep_overview["待补全文"] == "27"
    nistep_catalog = [r for r in catalog if r["报告ID"].startswith("C-NISTEP-")]
    assert len(nistep_catalog) == len(nistep_assets)
    assert all(r["机构观点等级"] == "作者讨论论文" for r in nistep_catalog if r["报告类型"] == "讨论论文")
    stepi_assets = rows(root / "60_STEPI韩文科技与中国专题增补台账.csv")
    assert len(stepi_assets) == 518, len(stepi_assets)
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in stepi_assets) == 476
    assert sum(r["本地状态"] == "官方PDF已保存并完成韩文OCR" for r in stepi_assets) == 5
    assert sum(r["本地状态"] == "官方目录无PDF" for r in stepi_assets) == 37
    assert not any(r["本地状态"] == "获取失败" for r in stepi_assets)
    assert sum(r["韩文报告类型"] == "정책연구" for r in stepi_assets) == 296
    assert sum(r["韩文报告类型"] == "조사연구" for r in stepi_assets) == 111
    assert sum(r["韩文报告类型"] == "정책자료" for r in stepi_assets) == 44
    assert sum(r["韩文报告类型"] == "기타연구" for r in stepi_assets) == 67
    assert sum(r["观察窗"] == "W1" for r in stepi_assets) == 139
    assert sum(r["观察窗"] == "W2" for r in stepi_assets) == 166
    assert sum(r["观察窗"] == "W3" for r in stepi_assets) == 213
    assert sum(r["科技关联层级"] == "核心科技直接材料" for r in stepi_assets) == 66
    assert sum("中国科技与国际比较" in r["主题标签"] for r in stepi_assets) == 104
    assert sum(r["文本质量"] == "可检索文本" for r in stepi_assets) == 476
    assert sum(r["文本质量"] == "韩文OCR可检索文本" for r in stepi_assets) == 5
    assert sum(r["文本质量"] == "图像型PDF，OCR待补" for r in stepi_assets) == 0
    assert sum(r["文本质量"] == "官方目录无PDF正文" for r in stepi_assets) == 37
    assert all(
        r["本地原始资产"] and Path(r["本地原始资产"]).exists()
        and r["本地文本"] and Path(r["本地文本"]).exists()
        and r["本地切片"] and Path(r["本地切片"]).exists()
        and len(r["SHA256"]) == 64 and int(r["PDF页数"]) > 0
        for r in stepi_assets
        if r["本地状态"] in {"官方PDF已保存并校验", "官方PDF已保存并完成韩文OCR"}
    )
    stepi_ocr = rows(root / "112_STEPI韩文扫描件OCR补全台账.csv")
    assert len(stepi_ocr) == 5
    assert {r["报告ID"] for r in stepi_ocr} == {
        r["报告ID"] for r in stepi_assets if r["文本质量"] == "韩文OCR可检索文本"
    }
    assert sum(int(r["PDF页数"]) for r in stepi_ocr) == 45
    assert sum(int(r["OCR字符数"]) for r in stepi_ocr) == 42085
    assert all(
        not r["本地原始资产"] and not r["SHA256"] and not r["官方PDF"]
        for r in stepi_assets if r["本地状态"] == "官方目录无PDF"
    )
    assert len(rows(root / "62_STEPI韩文科技与中国主题索引.csv")) == 2401
    assert len(rows(root / "63_STEPI韩文科技与中国复用矩阵.csv")) == 222
    stepi_series = rows(root / "73_STEPI中国先进技术连续序列附卷台账.csv")
    assert len(stepi_series) == 10
    assert sum(r["卷别"] == "主卷" for r in stepi_series) == 5
    assert sum(r["卷别"] == "附卷" for r in stepi_series) == 5
    assert {r["年份"] for r in stepi_series} == {"2017", "2018", "2019", "2020", "2021"}
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and len(r["SHA256"]) == 64
        and int(r["PDF页数"]) > 0 and r["文本质量"] == "可检索文本"
        for r in stepi_series
    )
    gap_matrix = rows(root / "69_机构节点主题覆盖缺口矩阵.csv")
    targeted_queue = rows(root / "70_定点补源优先队列.csv")
    catalog_queue = rows(root / "72_轻量目录扩展优先队列.csv")
    assert len(gap_matrix) == 720
    assert {r["战略主题"] for r in gap_matrix} == {
        "T1_科学体系与基础研究", "T2_技术创新与关键技术", "T3_创新政策与研发治理",
        "T4_人才大学与科研组织", "T5_产业创新转化与区域生态", "T6_国际合作开放科学与比较",
    }
    assert len(targeted_queue) == 11
    assert len(catalog_queue) == 0
    assert not any(r["战略主题"] == "T7_安全供应链与治理边界" for r in gap_matrix)
    assert not any(r["报告名称"] == "China’s Military AI Roadblocks" for r in targeted_queue)
    stepi_catalog = [r for r in catalog if r["报告ID"].startswith("C-STEPI-")]
    assert len(stepi_catalog) == len(stepi_assets)
    assert all(r["机构观点等级"] == "机构正式研究" for r in stepi_catalog)
    kistep_assets = rows(root / "64_KISTEP韩文正式报告总目录与重点附件台账.csv")
    assert len(kistep_assets) == 1174, len(kistep_assets)
    assert sum(bool(r["本地原始资产"]) for r in kistep_assets) == 61
    assert sum(r["文本质量"] == "可检索文本" for r in kistep_assets) == 55
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in kistep_assets) == 57
    assert sum(r["本地状态"] == "官方PDF已保存并完成韩文OCR" for r in kistep_assets) == 4
    assert sum(r["文本质量"] == "韩文OCR可检索文本" for r in kistep_assets) == 4
    assert sum(r["文本质量"] == "图像型PDF，OCR待补" for r in kistep_assets) == 2
    assert sum(r["文本质量"] == "官方目录无本地正文" for r in kistep_assets) == 1113
    assert sum(r["观察窗"] == "W1" for r in kistep_assets) == 36
    assert sum(r["观察窗"] == "W2" for r in kistep_assets) == 496
    assert sum(r["观察窗"] == "W3" for r in kistep_assets) == 642
    assert sum(r["科技关联层级"] == "核心科技直接材料" for r in kistep_assets) == 197
    assert sum("中国科技与国际比较" in r["主题标签"] for r in kistep_assets) == 24
    assert sum(r["下载优先级"] == "P0-China-tech" for r in kistep_assets) == 5
    assert sum(r["下载优先级"] == "P0-core-tech" for r in kistep_assets) == 194
    assert sum(r["下载优先级"] == "P1-global-STI" for r in kistep_assets) == 125
    assert sum(r["下载优先级"] == "P2-STI-baseline" for r in kistep_assets) == 850
    assert len(rows(root / "66_KISTEP韩文科技与中国主题索引.csv")) == 2091
    assert len(rows(root / "67_KISTEP韩文科技与中国复用矩阵.csv")) == 312
    assert all(
        r["本地原始资产"] and Path(r["本地原始资产"]).exists()
        and r["本地文本"] and Path(r["本地文本"]).exists()
        and r["本地切片"] and Path(r["本地切片"]).exists()
        and len(r["SHA256"]) == 64 and int(r["PDF页数"]) > 0
        for r in kistep_assets if r["本地原始资产"]
    )
    kistep_ocr = rows(root / "114_KISTEP高价值韩文扫描件OCR补全台账.csv")
    assert len(kistep_ocr) == 2
    assert sum(int(r["PDF页数"]) for r in kistep_ocr) == 282
    assert sum(int(r["OCR字符数"]) for r in kistep_ocr) == 231869
    assert {r["报告ID"] for r in kistep_ocr} == {
        "C-KISTEP-RES0220200140", "C-KISTEP-RES0220260109"
    }
    kistep_ocr_second = rows(root / "116_KISTEP科技政策与AI半导体扫描件OCR补全台账.csv")
    assert len(kistep_ocr_second) == 2
    assert sum(int(r["PDF页数"]) for r in kistep_ocr_second) == 624
    assert sum(int(r["OCR字符数"]) for r in kistep_ocr_second) == 512245
    assert {r["报告ID"] for r in kistep_ocr + kistep_ocr_second} == {
        r["报告ID"] for r in kistep_assets if r["文本质量"] == "韩文OCR可检索文本"
    }
    kistep_catalog = [r for r in catalog if r["报告ID"].startswith("C-KISTEP-")]
    assert len(kistep_catalog) == len(kistep_assets)
    assert all(r["机构观点等级"] == "机构正式研究" for r in kistep_catalog)
    cset_light = rows(root / "75_CSET_2023-2024正式报告轻量目录.csv")
    oecd_light = rows(root / "77_OECD_STI正式系列轻量目录.csv")
    itif_series_light = rows(root / "79_ITIF中国先进产业创新系列轻量目录.csv")
    itif_node_light = rows(root / "82_ITIF科学技术创新节点轻量目录.csv")
    fraunhofer_light = rows(root / "84_Fraunhofer_ISI创新系统政策分析轻量目录.csv")
    stanford_hai_light = rows(root / "86_Stanford_HAI科学技术创新轻量目录.csv")
    ostp_light = rows(root / "88_美国OSTP科学技术创新政策轻量目录.csv")
    belfer_merics_light = rows(root / "90_Belfer_MERICS科学技术创新缺口轻量目录.csv")
    assert len(cset_light) == 60
    assert len(oecd_light) == 445
    assert len({r["统一目录报告ID"] for r in oecd_light}) == 445
    assert len(itif_series_light) == 10
    assert len(itif_node_light) == 5
    assert len(fraunhofer_light) == 47
    assert sum(r["统一目录报告ID"].startswith("C-FRAUNHOFER-ISI-DP-") for r in fraunhofer_light) == 45
    assert len(stanford_hai_light) == 17
    assert sum("AI Index Report" in r["报告名称"] for r in stanford_hai_light) == 9
    assert len(ostp_light) == 66
    assert len(belfer_merics_light) == 3
    assert sum("正式" in r["资料层级"] for r in belfer_merics_light) == 2
    assert sum("机构评论" in r["资料层级"] for r in belfer_merics_light) == 1
    assert not any(re.search(r"national security|cybersecurity|nuclear defense|security and integrity|electromagnetic pulses", r["报告名称"], re.I) for r in ostp_light)
    assert all(r["全文策略"].startswith("不自动下载") for ledger in (cset_light, oecd_light, itif_series_light, itif_node_light, fraunhofer_light, stanford_hai_light, ostp_light, belfer_merics_light) for r in ledger)
    assert len(rows(root / "69_机构节点主题覆盖缺口矩阵.csv")) == 720
    assert len(rows(root / "70_定点补源优先队列.csv")) == 11
    assert len(rows(root / "72_轻量目录扩展优先队列.csv")) == 0
    review = rows(root / "92_定点全文候选证据增量复核台账.csv")
    assert len(review) == 43
    assert sum(r["复核结论"] == "本轮精选全文" for r in review) == 18
    assert sum(r["全文状态"] == "本地资产已保存" for r in review) == 18
    assert sum(r["中国关联"] == "是" and r["复核结论"] == "本轮精选全文" for r in review) == 10
    second_review = rows(root / "94_第二批定点全文候选证据增量复核台账.csv")
    assert len(second_review) == 36
    assert sum(r["复核结论"] == "第二批精选全文" for r in second_review) == 12
    assert sum(r["全文状态"] == "本地资产已保存" for r in second_review) == 12
    assert sum(r["中国关联"] == "是" and r["复核结论"] == "第二批精选全文" for r in second_review) == 3
    third_review = rows(root / "96_第三批定点全文候选证据增量复核台账.csv")
    assert len(third_review) == 30
    assert sum(r["复核结论"] == "第三批精选全文" for r in third_review) == 12
    assert sum(r["全文状态"] == "本地资产已保存" for r in third_review) == 12
    assert sum(r["中国关联"] == "是" and r["复核结论"] == "第三批精选全文" for r in third_review) == 4
    fourth_review = rows(root / "98_第四批定点全文候选证据增量复核台账.csv")
    assert len(fourth_review) == 20
    assert sum(r["复核结论"] == "第四批精选全文" for r in fourth_review) == 12
    assert sum(r["全文状态"] == "本地资产已保存" for r in fourth_review) == 12
    assert sum(r["中国关联"] == "是" and r["复核结论"] == "第四批精选全文" for r in fourth_review) == 1
    fifth_review = rows(root / "100_第五批定点全文候选证据增量复核台账.csv")
    assert len(fifth_review) == 15
    assert sum(r["复核结论"] == "第五批精选全文" for r in fifth_review) == 5
    assert sum(r["全文状态"] == "本地资产已保存" for r in fifth_review) == 5
    sixth_review = rows(root / "102_第六批定点全文候选证据增量复核台账.csv")
    assert len(sixth_review) == 15
    assert sum(r["复核结论"] == "第六批精选全文" for r in sixth_review) == 3
    assert sum(r["全文状态"] == "本地资产已保存" for r in sixth_review) == 3
    seventh_review = rows(root / "104_第七批中国科技创新全文候选复核台账.csv")
    assert len(seventh_review) == 32
    assert sum(r["复核结论"] == "第七批精选全文" for r in seventh_review) == 18
    assert sum(r["全文状态"] == "本地资产已保存" for r in seventh_review) == 18
    eighth_review = rows(root / "106_第八批科技创新与中国比较全文候选复核台账.csv")
    assert len(eighth_review) == 28
    assert sum(r["复核结论"] == "第八批精选全文" for r in eighth_review) == 16
    assert sum(r["全文状态"] == "本地资产已保存" for r in eighth_review) == 16
    ninth_review = rows(root / "108_第九批科学体系与创新政策纵向全文候选复核台账.csv")
    assert len(ninth_review) == 20
    assert sum(r["复核结论"] == "第九批精选全文" for r in ninth_review) == 14
    assert sum(r["全文状态"] == "本地资产已保存" for r in ninth_review) == 14
    tenth_review = rows(root / "110_第十批OECD科学体系与科研机制纵向全文候选复核台账.csv")
    assert len(tenth_review) == 28
    assert sum(r["复核结论"] == "第十批精选全文" for r in tenth_review) == 16
    assert sum(r["全文状态"] == "本地资产已保存" for r in tenth_review) == 16
    selected_light_asset_ids = {
        r["报告ID"] for ledger, decision in (
            (review, "本轮精选全文"),
            (second_review, "第二批精选全文"),
            (third_review, "第三批精选全文"),
            (fourth_review, "第四批精选全文"),
            (fifth_review, "第五批精选全文"),
            (sixth_review, "第六批精选全文"),
            (seventh_review, "第七批精选全文"),
            (eighth_review, "第八批精选全文"),
            (ninth_review, "第九批精选全文"),
            (tenth_review, "第十批精选全文"),
        )
        for r in ledger if r["复核结论"] == decision
    }
    assert selected_light_asset_ids <= {r["报告ID"] for r in catalog_assets}
    assert len(catalog) == expected_catalog_size(
        seed_count=len(seeds),
        catalog_asset_count=len(catalog_assets) - len(selected_light_asset_ids),
        early_asset_count=len(early_assets),
        cset_asset_count=len(cset_assets),
        atlantic_asset_count=len(atlantic_assets),
        belfer_asset_count=len(belfer_assets),
        nbr_asset_count=len(nbr_assets),
        merics_asset_count=len(merics_catalog),
        bruegel_asset_count=len(bruegel_catalog),
        crds_asset_count=len(crds_catalog),
        nistep_asset_count=len(nistep_catalog),
        stepi_asset_count=len(stepi_catalog),
        kistep_asset_count=len(kistep_catalog),
        light_catalog_count=60 + 443 + 10 + 5 + 45 + 17 + 66 + 2,
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
            (nbr_assets, ("本地原始资产",)),
            (merics_assets, ("本地原始资产",)),
            (bruegel_assets, ("本地原始资产",)),
            (crds_assets, ("本地原始资产",)),
            (nistep_assets, ("本地原始资产",)),
            (stepi_assets, ("本地原始资产",)),
            (stepi_series, ("本地原始资产",)),
            (kistep_assets, ("本地原始资产",)),
        )
        for row in ledger
        for field in fields
        for value in (row.get(field, ""),)
        if value and Path(value).suffix.lower() == ".pdf"
    }
    assert {pdf.resolve() for pdf in pdfs} == expected_pdf_paths
    pdf_hashes: set[str] = set()
    image_pdf_paths = {
        Path(r["本地原始资产"]).resolve()
        for r in stepi_assets if r["文本质量"] == "图像型PDF，OCR待补"
    } | {
        Path(r["本地原始资产"]).resolve()
        for r in kistep_assets if r["文本质量"] == "图像型PDF，OCR待补"
    }
    for pdf in pdfs:
        assert pdf.read_bytes()[:4] == b"%PDF", pdf
        digest = sha(pdf)
        assert digest not in pdf_hashes, f"duplicate PDF hash: {pdf}"
        pdf_hashes.add(digest)
        page_count = len(PdfReader(str(pdf)).pages)
        text_path = root / "03_证据底稿" / "文本" / f"{pdf.stem}.txt"
        assert page_count > 0
        density = len(text_path.read_text(encoding="utf-8")) / page_count
        if pdf.resolve() in image_pdf_paths:
            assert density < 200, pdf
        else:
            assert density >= 200, pdf
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
        ("39_NBR科技与中国专题增补台账.csv", "国际科技智库观点演变_NBR科技与中国专题增补台账.csv"),
        ("41_NBR科技与中国主题索引.csv", "国际科技智库观点演变_NBR科技与中国主题索引.csv"),
        ("42_NBR科技与中国复用矩阵.csv", "国际科技智库观点演变_NBR科技与中国复用矩阵.csv"),
        ("43_MERICS科技与中国专题增补台账.csv", "国际科技智库观点演变_MERICS科技与中国专题增补台账.csv"),
        ("45_MERICS科技与中国主题索引.csv", "国际科技智库观点演变_MERICS科技与中国主题索引.csv"),
        ("46_MERICS科技与中国复用矩阵.csv", "国际科技智库观点演变_MERICS科技与中国复用矩阵.csv"),
        ("47_Bruegel科技与中国专题增补台账.csv", "国际科技智库观点演变_Bruegel科技与中国专题增补台账.csv"),
        ("49_Bruegel科技与中国主题索引.csv", "国际科技智库观点演变_Bruegel科技与中国主题索引.csv"),
        ("50_Bruegel科技与中国复用矩阵.csv", "国际科技智库观点演变_Bruegel科技与中国复用矩阵.csv"),
        ("51_CRDS日文科技与中国专题增补台账.csv", "国际科技智库观点演变_CRDS日文科技与中国专题增补台账.csv"),
        ("53_CRDS日文科技与中国主题索引.csv", "国际科技智库观点演变_CRDS日文科技与中国主题索引.csv"),
        ("54_CRDS日文科技与中国复用矩阵.csv", "国际科技智库观点演变_CRDS日文科技与中国复用矩阵.csv"),
        ("55_NISTEP日文科技与中国专题增补台账.csv", "国际科技智库观点演变_NISTEP日文科技与中国专题增补台账.csv"),
        ("56_NISTEP日文科技与中国专题增补结果.md", "国际科技智库观点演变_NISTEP日文科技与中国专题增补结果.md"),
        ("57_NISTEP日文科技与中国主题索引.csv", "国际科技智库观点演变_NISTEP日文科技与中国主题索引.csv"),
        ("58_NISTEP日文科技与中国复用矩阵.csv", "国际科技智库观点演变_NISTEP日文科技与中国复用矩阵.csv"),
        ("59_CRDS_NISTEP科技主题与机构功能对照.csv", "国际科技智库观点演变_CRDS_NISTEP科技主题与机构功能对照.csv"),
        ("60_STEPI韩文科技与中国专题增补台账.csv", "国际科技智库观点演变_STEPI韩文科技与中国专题增补台账.csv"),
        ("61_STEPI韩文科技与中国专题增补结果.md", "国际科技智库观点演变_STEPI韩文科技与中国专题增补结果.md"),
        ("62_STEPI韩文科技与中国主题索引.csv", "国际科技智库观点演变_STEPI韩文科技与中国主题索引.csv"),
        ("63_STEPI韩文科技与中国复用矩阵.csv", "国际科技智库观点演变_STEPI韩文科技与中国复用矩阵.csv"),
        ("64_KISTEP韩文正式报告总目录与重点附件台账.csv", "国际科技智库观点演变_KISTEP韩文正式报告总目录与重点附件台账.csv"),
        ("65_KISTEP韩文正式报告总目录与重点附件结果.md", "国际科技智库观点演变_KISTEP韩文正式报告总目录与重点附件结果.md"),
        ("66_KISTEP韩文科技与中国主题索引.csv", "国际科技智库观点演变_KISTEP韩文科技与中国主题索引.csv"),
        ("67_KISTEP韩文科技与中国复用矩阵.csv", "国际科技智库观点演变_KISTEP韩文科技与中国复用矩阵.csv"),
        ("68_智库分层与转向节点采集矩阵.md", "国际科技智库观点演变_智库分层与转向节点采集矩阵.md"),
        ("69_机构节点主题覆盖缺口矩阵.csv", "国际科技智库观点演变_机构节点主题覆盖缺口矩阵.csv"),
        ("70_定点补源优先队列.csv", "国际科技智库观点演变_定点补源优先队列.csv"),
        ("71_覆盖缺口结果.md", "国际科技智库观点演变_覆盖缺口结果.md"),
        ("72_轻量目录扩展优先队列.csv", "国际科技智库观点演变_轻量目录扩展优先队列.csv"),
        ("73_STEPI中国先进技术连续序列附卷台账.csv", "国际科技智库观点演变_STEPI中国先进技术连续序列附卷台账.csv"),
        ("74_STEPI中国先进技术连续序列结果.md", "国际科技智库观点演变_STEPI中国先进技术连续序列结果.md"),
        ("75_CSET_2023-2024正式报告轻量目录.csv", "国际科技智库观点演变_CSET_2023-2024正式报告轻量目录.csv"),
        ("76_CSET_2023-2024正式报告轻量目录结果.md", "国际科技智库观点演变_CSET_2023-2024正式报告轻量目录结果.md"),
        ("77_OECD_STI正式系列轻量目录.csv", "国际科技智库观点演变_OECD_STI正式系列轻量目录.csv"),
        ("78_OECD_STI正式系列轻量目录结果.md", "国际科技智库观点演变_OECD_STI正式系列轻量目录结果.md"),
        ("79_ITIF中国先进产业创新系列轻量目录.csv", "国际科技智库观点演变_ITIF中国先进产业创新系列轻量目录.csv"),
        ("80_ITIF中国先进产业创新系列轻量目录结果.md", "国际科技智库观点演变_ITIF中国先进产业创新系列轻量目录结果.md"),
        ("81_科学技术创新主轴采集规则.md", "国际科技智库观点演变_科学技术创新主轴采集规则.md"),
        ("82_ITIF科学技术创新节点轻量目录.csv", "国际科技智库观点演变_ITIF科学技术创新节点轻量目录.csv"),
        ("83_ITIF科学技术创新节点轻量目录结果.md", "国际科技智库观点演变_ITIF科学技术创新节点轻量目录结果.md"),
        ("84_Fraunhofer_ISI创新系统政策分析轻量目录.csv", "国际科技智库观点演变_Fraunhofer_ISI创新系统政策分析轻量目录.csv"),
        ("85_Fraunhofer_ISI创新系统政策分析轻量目录结果.md", "国际科技智库观点演变_Fraunhofer_ISI创新系统政策分析轻量目录结果.md"),
        ("86_Stanford_HAI科学技术创新轻量目录.csv", "国际科技智库观点演变_Stanford_HAI科学技术创新轻量目录.csv"),
        ("87_Stanford_HAI科学技术创新轻量目录结果.md", "国际科技智库观点演变_Stanford_HAI科学技术创新轻量目录结果.md"),
        ("88_美国OSTP科学技术创新政策轻量目录.csv", "国际科技智库观点演变_美国OSTP科学技术创新政策轻量目录.csv"),
        ("89_美国OSTP科学技术创新政策轻量目录结果.md", "国际科技智库观点演变_美国OSTP科学技术创新政策轻量目录结果.md"),
        ("90_Belfer_MERICS科学技术创新缺口轻量目录.csv", "国际科技智库观点演变_Belfer_MERICS科学技术创新缺口轻量目录.csv"),
        ("91_Belfer_MERICS科学技术创新缺口轻量目录结果.md", "国际科技智库观点演变_Belfer_MERICS科学技术创新缺口轻量目录结果.md"),
        ("92_定点全文候选证据增量复核台账.csv", "国际科技智库观点演变_定点全文候选证据增量复核台账.csv"),
        ("93_定点全文候选证据增量复核结果.md", "国际科技智库观点演变_定点全文候选证据增量复核结果.md"),
        ("94_第二批定点全文候选证据增量复核台账.csv", "国际科技智库观点演变_第二批定点全文候选证据增量复核台账.csv"),
        ("95_第二批定点全文候选证据增量复核结果.md", "国际科技智库观点演变_第二批定点全文候选证据增量复核结果.md"),
        ("96_第三批定点全文候选证据增量复核台账.csv", "国际科技智库观点演变_第三批定点全文候选证据增量复核台账.csv"),
        ("97_第三批定点全文候选证据增量复核结果.md", "国际科技智库观点演变_第三批定点全文候选证据增量复核结果.md"),
        ("98_第四批定点全文候选证据增量复核台账.csv", "国际科技智库观点演变_第四批定点全文候选证据增量复核台账.csv"),
        ("99_第四批定点全文候选证据增量复核结果.md", "国际科技智库观点演变_第四批定点全文候选证据增量复核结果.md"),
        ("100_第五批定点全文候选证据增量复核台账.csv", "国际科技智库观点演变_第五批定点全文候选证据增量复核台账.csv"),
        ("101_第五批定点全文候选证据增量复核结果.md", "国际科技智库观点演变_第五批定点全文候选证据增量复核结果.md"),
        ("102_第六批定点全文候选证据增量复核台账.csv", "国际科技智库观点演变_第六批定点全文候选证据增量复核台账.csv"),
        ("103_第六批定点全文候选证据增量复核结果.md", "国际科技智库观点演变_第六批定点全文候选证据增量复核结果.md"),
        ("104_第七批中国科技创新全文候选复核台账.csv", "国际科技智库观点演变_第七批中国科技创新全文候选复核台账.csv"),
        ("105_第七批中国科技创新全文候选复核结果.md", "国际科技智库观点演变_第七批中国科技创新全文候选复核结果.md"),
        ("106_第八批科技创新与中国比较全文候选复核台账.csv", "国际科技智库观点演变_第八批科技创新与中国比较全文候选复核台账.csv"),
        ("107_第八批科技创新与中国比较全文候选复核结果.md", "国际科技智库观点演变_第八批科技创新与中国比较全文候选复核结果.md"),
        ("108_第九批科学体系与创新政策纵向全文候选复核台账.csv", "国际科技智库观点演变_第九批科学体系与创新政策纵向全文候选复核台账.csv"),
        ("109_第九批科学体系与创新政策纵向全文候选复核结果.md", "国际科技智库观点演变_第九批科学体系与创新政策纵向全文候选复核结果.md"),
        ("110_第十批OECD科学体系与科研机制纵向全文候选复核台账.csv", "国际科技智库观点演变_第十批OECD科学体系与科研机制纵向全文候选复核台账.csv"),
        ("111_第十批OECD科学体系与科研机制纵向全文候选复核结果.md", "国际科技智库观点演变_第十批OECD科学体系与科研机制纵向全文候选复核结果.md"),
        ("112_STEPI韩文扫描件OCR补全台账.csv", "国际科技智库观点演变_STEPI韩文扫描件OCR补全台账.csv"),
        ("113_STEPI韩文扫描件OCR补全结果.md", "国际科技智库观点演变_STEPI韩文扫描件OCR补全结果.md"),
        ("114_KISTEP高价值韩文扫描件OCR补全台账.csv", "国际科技智库观点演变_KISTEP高价值韩文扫描件OCR补全台账.csv"),
        ("115_KISTEP高价值韩文扫描件OCR补全结果.md", "国际科技智库观点演变_KISTEP高价值韩文扫描件OCR补全结果.md"),
        ("116_KISTEP科技政策与AI半导体扫描件OCR补全台账.csv", "国际科技智库观点演变_KISTEP科技政策与AI半导体扫描件OCR补全台账.csv"),
        ("117_KISTEP科技政策与AI半导体扫描件OCR补全结果.md", "国际科技智库观点演变_KISTEP科技政策与AI半导体扫描件OCR补全结果.md"),
    ):
        assert sha(root / source_name) == sha(kb / "06_数据资产" / kb_name)
    assert len(rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv")) >= 1
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv"))
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "06_数据资产" / "数据资产清单.csv"))
    print("viewpoint_research_validation=ok")
    print(f"official_seeds={len(seeds)} catalog={len(catalog)} evidence={len(evidence)} institution_cards=11 pdfs={len(pdfs)} non_anchor_assets={len(catalog_assets)} early_assets={len(early_assets)} cset_assets={len(cset_assets)} atlantic_assets={len(atlantic_assets)} belfer_assets={len(belfer_assets)} nbr_assets={len(nbr_assets)} merics_assets={len(merics_assets)} bruegel_assets={len(bruegel_assets)} crds_assets={len(crds_assets)} nistep_assets={len(nistep_assets)} stepi_assets={len(stepi_assets)} kistep_assets={len(kistep_assets)}")


if __name__ == "__main__":
    main()
