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


def expected_nsf_science_innovation_ids() -> set[str]:
    return {
        "C-NSF-NSB-ARD-2020", "C-NSF-NSB-ARD-2022", "C-NSF-NSB-ARD-2024",
        "C-NSF-NSB-WF-2020", "C-NSF-NSB-WF-2022", "C-NSF-NSB-WF-2024",
        "C-NSF-NSB-INV-2020", "C-NSF-NSB-INV-2022", "C-NSF-NSB-INV-2024",
        "C-NSF-NSB-KTI-2020", "C-NSF-NSB-KTI-2022", "C-NSF-NSB-KTI-2024",
        "C-NSF-NSB-DISC-2026", "C-NSF-NSB-TALENT-2026", "C-NSF-NSB-IMPACT-2026",
    }


def expected_nesta_selected_ids() -> set[str]:
    return {
        "C-NESTA-2016-MADE-IN-CHINA-MAKERSPACES-AND-THE-SEARCH-FOR-MASS-INNOVATION",
        "C-NESTA-2016-INNOVATION-ANALYTICS-A-GUIDE-TO-NEW-DATA-AND-MEASUREMENT-IN-INNOVATION-P",
        "C-NESTA-2016-HOW-INNOVATION-AGENCIES-WORK",
        "C-NESTA-2017-NESTA-RESPONSE-TO-BUILDING-OUR-INDUSTRIAL-STRATEGY-GREEN-PAPER-2017",
        "C-NESTA-2018-SCIENCE-OF-USING-SCIENCE-LEARNING-REPORT",
        "C-NESTA-2019-INVISIBLE-DRAG-CORPORATE-INCENTIVES",
        "C-NESTA-2019-SEMANTIC-ANALYSIS-RECENT-EVOLUTION-AI-RESEARCH",
        "C-NESTA-2020-INNOVATING-UK-INNOVATION-POLICY",
        "C-NESTA-2020-INTRODUCING-AI-POWERED-STATE",
        "C-NESTA-2026-HDRS-DIGITAL-ECOSYSTEM-ANALYSIS",
    }


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
        "118_KISTEP全球健康与先进生物合作扫描件OCR补全台账.csv", "119_KISTEP全球健康与先进生物合作扫描件OCR补全结果.md",
        "120_NISTEP科技创新主轴补充证据台账.csv", "121_NISTEP科技创新主轴补充证据结果.md",
        "122_Stanford_HAI_AI_Index连续序列定点全文台账.csv", "123_Stanford_HAI_AI_Index连续序列定点全文结果.md",
        "124_WIPO全球创新指数近十年轻量目录.csv", "125_WIPO全球创新指数近十年轻量目录结果.md",
        "126_WIPO全球创新指数跨期节点全文台账.csv", "127_WIPO全球创新指数跨期节点全文结果.md",
        "128_OECD科研基础设施与全球创新网络定点全文台账.csv", "129_OECD科研基础设施与全球创新网络定点全文结果.md",
        "130_NSF_NSB科学与工程指标近十年轻量目录.csv", "131_NSF_NSB科学与工程指标近十年轻量目录结果.md",
        "132_NSF_NSB科学与工程指标跨期节点全文台账.csv", "133_NSF_NSB科学与工程指标跨期节点全文结果.md",
        "134_欧盟SRIP科研创新绩效近十年轻量目录.csv", "135_欧盟SRIP科研创新绩效近十年轻量目录结果.md",
        "136_欧盟SRIP科研创新绩效跨期节点全文台账.csv", "137_欧盟SRIP科研创新绩效跨期节点全文结果.md",
        "138_欧盟EIS创新记分牌近十年轻量目录.csv", "139_欧盟EIS创新记分牌近十年轻量目录结果.md",
        "140_欧盟EIS创新记分牌跨期节点全文台账.csv", "141_欧盟EIS创新记分牌跨期节点全文结果.md",
        "142_UNESCO全球科学体系近十年轻量目录.csv", "143_UNESCO全球科学体系近十年轻量目录结果.md",
        "144_UNESCO全球科学体系跨期节点全文台账.csv", "145_UNESCO全球科学体系跨期节点全文结果.md",
        "146_UNCTAD技术与创新报告近十年轻量目录.csv", "147_UNCTAD技术与创新报告近十年轻量目录结果.md",
        "148_UNCTAD技术与创新报告跨期节点全文台账.csv", "149_UNCTAD技术与创新报告跨期节点全文结果.md",
        "150_WIPO世界知识产权报告近十年轻量目录.csv", "151_WIPO世界知识产权报告近十年轻量目录结果.md",
        "152_WIPO世界知识产权报告跨期节点全文台账.csv", "153_WIPO世界知识产权报告跨期节点全文结果.md",
        "154_NSF_NSB研发与科学论文跨期专题全文台账.csv", "155_NSF_NSB研发与科学论文跨期专题全文结果.md",
        "156_NSF_NSB科学体系人才转化跨期专题全文台账.csv", "157_NSF_NSB科学体系人才转化跨期专题全文结果.md",
        "158_Nesta科技创新报告近十年轻量目录.csv", "159_Nesta科技创新报告近十年轻量目录结果.md",
        "160_Nesta科技创新与中国比较跨期精选全文台账.csv", "161_Nesta科技创新与中国比较跨期精选全文结果.md",
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
    nistep_support = rows(root / "120_NISTEP科技创新主轴补充证据台账.csv")
    assert len(nistep_support) == 3
    assert sum(r["资产类型"] == "正式PDF补充证据" for r in nistep_support) == 2
    assert sum(int(r["PDF页数"]) for r in nistep_support) == 25
    assert sum(int(r["提取文本字符数"]) for r in nistep_support) == 47919
    assert {r["关联正式报告"] for r in nistep_support} == {"NR:187；NR:196", "RM:348", "DP:192"}
    assert all(
        Path(r["本地原始资产"]).exists()
        and Path(r["本地文本"]).exists()
        and Path(r["本地切片或转写"]).exists()
        and len(r["SHA256"]) == 64
        for r in nistep_support
    )
    stanford_series = rows(root / "122_Stanford_HAI_AI_Index连续序列定点全文台账.csv")
    assert len(stanford_series) == 3
    assert {r["年份"] for r in stanford_series} == {"2018", "2022", "2025"}
    assert sum(int(r["PDF页数"]) for r in stanford_series) == 781
    assert sum(int(r["提取文本字符数"]) for r in stanford_series) == 1356077
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and len(r["SHA256"]) == 64
        and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in stanford_series
    )
    wipo_light = rows(root / "124_WIPO全球创新指数近十年轻量目录.csv")
    assert len(wipo_light) == 10
    assert {r["发布日期"][:4] for r in wipo_light} == {str(year) for year in range(2016, 2026)}
    assert sum(r["全文策略"] == "已定点下载" for r in wipo_light) == 3
    assert sum("连续系列已完成跨期抽样" in r["全文策略"] for r in wipo_light) == 7
    wipo_fulltext = rows(root / "126_WIPO全球创新指数跨期节点全文台账.csv")
    assert len(wipo_fulltext) == 4
    assert {r["报告ID"] for r in wipo_fulltext} == {
        "C-WIPO-GII-2016", "C-WIPO-GII-2020", "C-WIPO-GII-2024", "C-WIPO-GII-CHINA-2025",
    }
    assert sum(int(r["PDF页数"]) for r in wipo_fulltext) == 1242
    assert sum(int(r["提取文本字符数"]) for r in wipo_fulltext) == 6921163
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in wipo_fulltext
    )
    oecd_networks = rows(root / "128_OECD科研基础设施与全球创新网络定点全文台账.csv")
    assert len(oecd_networks) == 2
    assert {r["报告ID"] for r in oecd_networks} == {"C-OECD-DOI-FA11A0E0-EN", "C-OECD-DOI-76D78FBB-EN"}
    assert sum(int(r["PDF页数"]) for r in oecd_networks) == 141
    assert sum(int(r["提取文本字符数"]) for r in oecd_networks) == 298282
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in oecd_networks
    )
    nsf_nsb_light = rows(root / "130_NSF_NSB科学与工程指标近十年轻量目录.csv")
    assert len(nsf_nsb_light) == 6
    assert {r["发布日期"][:4] for r in nsf_nsb_light} == {"2016", "2018", "2020", "2022", "2024", "2026"}
    assert sum(r["全文策略"] == "已定点下载" for r in nsf_nsb_light) == 4
    assert sum("连续系列已完成跨期抽样" in r["全文策略"] for r in nsf_nsb_light) == 2
    nsf_nsb_fulltext = rows(root / "132_NSF_NSB科学与工程指标跨期节点全文台账.csv")
    assert len(nsf_nsb_fulltext) == 4
    assert {r["报告ID"] for r in nsf_nsb_fulltext} == {
        "C-NSF-NSB-SEI-2016", "C-NSF-NSB-SEI-2020", "C-NSF-NSB-SEI-2024", "C-NSF-NSB-SEI-2026",
    }
    assert sum(int(r["PDF页数"]) for r in nsf_nsb_fulltext) == 210
    assert sum(int(r["提取文本字符数"]) for r in nsf_nsb_fulltext) == 482831
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in nsf_nsb_fulltext
    )
    eu_srip_light = rows(root / "134_欧盟SRIP科研创新绩效近十年轻量目录.csv")
    assert len(eu_srip_light) == 5
    assert {r["发布日期"][:4] for r in eu_srip_light} == {"2016", "2018", "2020", "2022", "2024"}
    assert sum(r["全文策略"] == "已定点下载" for r in eu_srip_light) == 3
    assert sum("连续系列已完成跨期抽样" in r["全文策略"] for r in eu_srip_light) == 2
    eu_srip_fulltext = rows(root / "136_欧盟SRIP科研创新绩效跨期节点全文台账.csv")
    assert len(eu_srip_fulltext) == 3
    assert {r["报告ID"] for r in eu_srip_fulltext} == {
        "C-EU-SRIP-2016", "C-EU-SRIP-2020", "C-EU-SRIP-2024",
    }
    assert sum(int(r["PDF页数"]) for r in eu_srip_fulltext) == 1642
    assert sum(int(r["提取文本字符数"]) for r in eu_srip_fulltext) == 3834795
    assert sum(int(r["China词形命中数"]) for r in eu_srip_fulltext) == 826
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in eu_srip_fulltext
    )
    eu_eis_light = rows(root / "138_欧盟EIS创新记分牌近十年轻量目录.csv")
    assert len(eu_eis_light) == 11
    assert {r["发布日期"][:4] for r in eu_eis_light} == {str(year) for year in range(2016, 2027)}
    assert sum(r["全文策略"] == "已定点下载" for r in eu_eis_light) == 4
    assert sum("连续系列已完成跨期抽样" in r["全文策略"] for r in eu_eis_light) == 7
    eu_eis_fulltext = rows(root / "140_欧盟EIS创新记分牌跨期节点全文台账.csv")
    assert len(eu_eis_fulltext) == 4
    assert {r["报告ID"] for r in eu_eis_fulltext} == {
        "C-EU-EIS-2016", "C-EU-EIS-2020", "C-EU-EIS-2024", "C-EU-EIS-2026",
    }
    assert sum(int(r["PDF页数"]) for r in eu_eis_fulltext) == 540
    assert sum(int(r["提取文本字符数"]) for r in eu_eis_fulltext) == 1564700
    assert sum(int(r["China词形命中数"]) for r in eu_eis_fulltext) == 138
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in eu_eis_fulltext
    )
    unesco_light = rows(root / "142_UNESCO全球科学体系近十年轻量目录.csv")
    assert len(unesco_light) == 5
    assert {r["发布日期"][:4] for r in unesco_light} == {"2015", "2020", "2021", "2023", "2026"}
    assert sum(r["全文策略"] == "边界目录" for r in unesco_light) == 1
    assert sum("全文节点" in r["全文策略"] or r["全文策略"] == "当代桥接节点" for r in unesco_light) == 3
    unesco_fulltext = rows(root / "144_UNESCO全球科学体系跨期节点全文台账.csv")
    assert len(unesco_fulltext) == 3
    assert {r["报告ID"] for r in unesco_fulltext} == {
        "C-UNESCO-SCIENCE-2021", "C-UNESCO-SCIENCE-2023", "C-UNESCO-SCIENCE-2026",
    }
    assert sum(int(r["PDF页数"]) for r in unesco_fulltext) == 941
    assert sum(int(r["提取文本字符数"]) for r in unesco_fulltext) == 5822910
    assert sum(int(r["China词形命中数"]) for r in unesco_fulltext) == 1001
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in unesco_fulltext
    )
    unctad_light = rows(root / "146_UNCTAD技术与创新报告近十年轻量目录.csv")
    assert len(unctad_light) == 5
    assert {r["发布日期"][:4] for r in unctad_light} == {"2015", "2018", "2021", "2023", "2025"}
    assert sum(r["全文策略"] == "边界目录" for r in unctad_light) == 1
    assert sum("全文节点" in r["全文策略"] for r in unctad_light) == 4
    unctad_fulltext = rows(root / "148_UNCTAD技术与创新报告跨期节点全文台账.csv")
    assert len(unctad_fulltext) == 4
    assert {r["报告ID"] for r in unctad_fulltext} == {
        "C-UNCTAD-TIR-2018", "C-UNCTAD-TIR-2021", "C-UNCTAD-TIR-2023", "C-UNCTAD-TIR-2025",
    }
    assert sum(int(r["PDF页数"]) for r in unctad_fulltext) == 749
    assert sum(int(r["字节数"]) for r in unctad_fulltext) == 30813413
    assert sum(int(r["提取文本字符数"]) for r in unctad_fulltext) == 2297750
    assert sum(int(r["China词形命中数"]) for r in unctad_fulltext) == 769
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in unctad_fulltext
    )
    wipr_light = rows(root / "150_WIPO世界知识产权报告近十年轻量目录.csv")
    assert len(wipr_light) == 6
    assert {r["发布日期"][:4] for r in wipr_light} == {"2015", "2017", "2019", "2022", "2024", "2026"}
    assert sum(r["全文策略"] == "边界目录" for r in wipr_light) == 1
    assert sum("全文节点" in r["全文策略"] for r in wipr_light) == 5
    assert all("安全" not in r["科学技术创新主题"] for r in wipr_light)
    wipr_fulltext = rows(root / "152_WIPO世界知识产权报告跨期节点全文台账.csv")
    assert len(wipr_fulltext) == 5
    assert {r["报告ID"] for r in wipr_fulltext} == {
        "C-WIPO-WIPR-2017", "C-WIPO-WIPR-2019", "C-WIPO-WIPR-2022",
        "C-WIPO-WIPR-2024", "C-WIPO-WIPR-2026",
    }
    assert sum(int(r["PDF页数"]) for r in wipr_fulltext) == 645
    assert sum(int(r["字节数"]) for r in wipr_fulltext) == 34670159
    assert sum(int(r["提取文本字符数"]) for r in wipr_fulltext) == 2202252
    assert sum(int(r["China词形命中数"]) for r in wipr_fulltext) == 613
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in wipr_fulltext
    )
    nsf_topic_fulltext = rows(root / "154_NSF_NSB研发与科学论文跨期专题全文台账.csv")
    assert len(nsf_topic_fulltext) == 6
    assert {r["报告ID"] for r in nsf_topic_fulltext} == {
        "C-NSF-NSB-RD-2020", "C-NSF-NSB-RD-2022", "C-NSF-NSB-RD-2024",
        "C-NSF-NSB-PUB-2020", "C-NSF-NSB-PUB-2022", "C-NSF-NSB-PUB-2024",
    }
    assert sum(int(r["PDF页数"]) for r in nsf_topic_fulltext) == 329
    assert sum(int(r["字节数"]) for r in nsf_topic_fulltext) == 7326262
    assert sum(int(r["提取文本字符数"]) for r in nsf_topic_fulltext) == 812951
    assert sum(int(r["China词形命中数"]) for r in nsf_topic_fulltext) == 294
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in nsf_topic_fulltext
    )
    nsf_science_innovation = rows(root / "156_NSF_NSB科学体系人才转化跨期专题全文台账.csv")
    assert len(nsf_science_innovation) == 15
    assert {r["报告ID"] for r in nsf_science_innovation} == expected_nsf_science_innovation_ids()
    assert sum(int(r["PDF页数"]) for r in nsf_science_innovation) == 1053
    assert sum(int(r["字节数"]) for r in nsf_science_innovation) == 29822223
    assert sum(int(r["提取文本字符数"]) for r in nsf_science_innovation) == 2321170
    assert sum(int(r["China词形命中数"]) for r in nsf_science_innovation) == 683
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in nsf_science_innovation
    )
    nesta_light = rows(root / "158_Nesta科技创新报告近十年轻量目录.csv")
    assert len(nesta_light) == 118, len(nesta_light)
    assert sum(r["中国关联"] == "是" for r in nesta_light) == 6
    assert all(r["官方落地页"].startswith("https://www.nesta.org.uk/report/") for r in nesta_light)
    nesta_selected = rows(root / "160_Nesta科技创新与中国比较跨期精选全文台账.csv")
    assert {r["报告ID"] for r in nesta_selected} == expected_nesta_selected_ids()
    assert sum(r["中国关联"] == "是" for r in nesta_selected) == 2
    assert sum(int(r["PDF页数"]) for r in nesta_selected) == 393
    assert sum(int(r["字节数"]) for r in nesta_selected) == 16002436
    assert sum(int(r["提取文本字符数"]) for r in nesta_selected) == 1130217
    assert sum(int(r["China词形命中数"]) for r in nesta_selected) == 1041
    assert all(
        Path(r["本地PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地PDF"])) == r["SHA256"]
        for r in nesta_selected
    )
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
    assert len(gap_matrix) == 960
    assert {r["战略主题"] for r in gap_matrix} == {
        "T1_科学体系与基础研究", "T2_技术创新与关键技术", "T3_创新政策与研发治理",
        "T4_人才大学与科研组织", "T5_产业创新转化与区域生态", "T6_国际合作开放科学与比较",
    }
    assert len(targeted_queue) == 0
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
    assert sum(r["本地状态"] == "官方PDF已保存并校验" for r in kistep_assets) == 55
    assert sum(r["本地状态"] == "官方PDF已保存并完成韩文OCR" for r in kistep_assets) == 6
    assert sum(r["文本质量"] == "韩文OCR可检索文本" for r in kistep_assets) == 6
    assert sum(r["文本质量"] == "图像型PDF，OCR待补" for r in kistep_assets) == 0
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
        "C-KISTEP-RES0220200140", "C-KISTEP-RES0220240126",
        "C-KISTEP-RES0220260004", "C-KISTEP-RES0220260109",
    }
    kistep_ocr_final = rows(root / "118_KISTEP全球健康与先进生物合作扫描件OCR补全台账.csv")
    assert len(kistep_ocr_final) == 2
    assert sum(int(r["PDF页数"]) for r in kistep_ocr_final) == 357
    assert sum(int(r["OCR字符数"]) for r in kistep_ocr_final) == 356812
    assert {r["报告ID"] for r in kistep_ocr + kistep_ocr_second + kistep_ocr_final} == {
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
    assert all(r["全文策略"].startswith("不自动下载") for ledger in (cset_light, itif_series_light, itif_node_light, fraunhofer_light, ostp_light, belfer_merics_light) for r in ledger)
    assert sum(r["全文策略"] == "已按真实科技创新机制缺口定点下载" for r in oecd_light) == 2
    assert sum(r["全文策略"].startswith("不自动下载") for r in oecd_light) == 443
    assert sum(r["全文策略"].startswith("已按连续序列缺口定点下载") for r in stanford_hai_light) == 3
    assert sum(r["全文策略"].startswith("不自动下载") for r in stanford_hai_light) == 14
    assert len(nesta_light) == 118
    assert all(r["全文策略"].startswith("不自动下载") for r in nesta_light)
    assert len(rows(root / "69_机构节点主题覆盖缺口矩阵.csv")) == 960
    assert len(rows(root / "70_定点补源优先队列.csv")) == 0
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
        light_catalog_count=60 + 443 + 10 + 5 + 45 + 17 + 66 + 2 + 11 + 6 + 5 + 11 + 5 + 5 + 6 + 6 + 15 + 118,
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
            (nistep_support, ("本地原始资产",)),
            (stanford_series, ("本地PDF",)),
            (wipo_fulltext, ("本地PDF",)),
            (oecd_networks, ("本地PDF",)),
            (nsf_nsb_fulltext, ("本地PDF",)),
            (eu_srip_fulltext, ("本地PDF",)),
            (eu_eis_fulltext, ("本地PDF",)),
            (unesco_fulltext, ("本地PDF",)),
            (unctad_fulltext, ("本地PDF",)),
            (wipr_fulltext, ("本地PDF",)),
            (nsf_topic_fulltext, ("本地PDF",)),
            (nsf_science_innovation, ("本地PDF",)),
            (nesta_selected, ("本地PDF",)),
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
        ("118_KISTEP全球健康与先进生物合作扫描件OCR补全台账.csv", "国际科技智库观点演变_KISTEP全球健康与先进生物合作扫描件OCR补全台账.csv"),
        ("119_KISTEP全球健康与先进生物合作扫描件OCR补全结果.md", "国际科技智库观点演变_KISTEP全球健康与先进生物合作扫描件OCR补全结果.md"),
        ("120_NISTEP科技创新主轴补充证据台账.csv", "国际科技智库观点演变_NISTEP科技创新主轴补充证据台账.csv"),
        ("121_NISTEP科技创新主轴补充证据结果.md", "国际科技智库观点演变_NISTEP科技创新主轴补充证据结果.md"),
        ("122_Stanford_HAI_AI_Index连续序列定点全文台账.csv", "国际科技智库观点演变_Stanford_HAI_AI_Index连续序列定点全文台账.csv"),
        ("123_Stanford_HAI_AI_Index连续序列定点全文结果.md", "国际科技智库观点演变_Stanford_HAI_AI_Index连续序列定点全文结果.md"),
        ("124_WIPO全球创新指数近十年轻量目录.csv", "国际科技智库观点演变_WIPO全球创新指数近十年轻量目录.csv"),
        ("125_WIPO全球创新指数近十年轻量目录结果.md", "国际科技智库观点演变_WIPO全球创新指数近十年轻量目录结果.md"),
        ("126_WIPO全球创新指数跨期节点全文台账.csv", "国际科技智库观点演变_WIPO全球创新指数跨期节点全文台账.csv"),
        ("127_WIPO全球创新指数跨期节点全文结果.md", "国际科技智库观点演变_WIPO全球创新指数跨期节点全文结果.md"),
        ("128_OECD科研基础设施与全球创新网络定点全文台账.csv", "国际科技智库观点演变_OECD科研基础设施与全球创新网络定点全文台账.csv"),
        ("129_OECD科研基础设施与全球创新网络定点全文结果.md", "国际科技智库观点演变_OECD科研基础设施与全球创新网络定点全文结果.md"),
        ("130_NSF_NSB科学与工程指标近十年轻量目录.csv", "国际科技智库观点演变_NSF_NSB科学与工程指标近十年轻量目录.csv"),
        ("131_NSF_NSB科学与工程指标近十年轻量目录结果.md", "国际科技智库观点演变_NSF_NSB科学与工程指标近十年轻量目录结果.md"),
        ("132_NSF_NSB科学与工程指标跨期节点全文台账.csv", "国际科技智库观点演变_NSF_NSB科学与工程指标跨期节点全文台账.csv"),
        ("133_NSF_NSB科学与工程指标跨期节点全文结果.md", "国际科技智库观点演变_NSF_NSB科学与工程指标跨期节点全文结果.md"),
        ("134_欧盟SRIP科研创新绩效近十年轻量目录.csv", "国际科技智库观点演变_欧盟SRIP科研创新绩效近十年轻量目录.csv"),
        ("135_欧盟SRIP科研创新绩效近十年轻量目录结果.md", "国际科技智库观点演变_欧盟SRIP科研创新绩效近十年轻量目录结果.md"),
        ("136_欧盟SRIP科研创新绩效跨期节点全文台账.csv", "国际科技智库观点演变_欧盟SRIP科研创新绩效跨期节点全文台账.csv"),
        ("137_欧盟SRIP科研创新绩效跨期节点全文结果.md", "国际科技智库观点演变_欧盟SRIP科研创新绩效跨期节点全文结果.md"),
        ("138_欧盟EIS创新记分牌近十年轻量目录.csv", "国际科技智库观点演变_欧盟EIS创新记分牌近十年轻量目录.csv"),
        ("139_欧盟EIS创新记分牌近十年轻量目录结果.md", "国际科技智库观点演变_欧盟EIS创新记分牌近十年轻量目录结果.md"),
        ("140_欧盟EIS创新记分牌跨期节点全文台账.csv", "国际科技智库观点演变_欧盟EIS创新记分牌跨期节点全文台账.csv"),
        ("141_欧盟EIS创新记分牌跨期节点全文结果.md", "国际科技智库观点演变_欧盟EIS创新记分牌跨期节点全文结果.md"),
        ("142_UNESCO全球科学体系近十年轻量目录.csv", "国际科技智库观点演变_UNESCO全球科学体系近十年轻量目录.csv"),
        ("143_UNESCO全球科学体系近十年轻量目录结果.md", "国际科技智库观点演变_UNESCO全球科学体系近十年轻量目录结果.md"),
        ("144_UNESCO全球科学体系跨期节点全文台账.csv", "国际科技智库观点演变_UNESCO全球科学体系跨期节点全文台账.csv"),
        ("145_UNESCO全球科学体系跨期节点全文结果.md", "国际科技智库观点演变_UNESCO全球科学体系跨期节点全文结果.md"),
        ("146_UNCTAD技术与创新报告近十年轻量目录.csv", "国际科技智库观点演变_UNCTAD技术与创新报告近十年轻量目录.csv"),
        ("147_UNCTAD技术与创新报告近十年轻量目录结果.md", "国际科技智库观点演变_UNCTAD技术与创新报告近十年轻量目录结果.md"),
        ("148_UNCTAD技术与创新报告跨期节点全文台账.csv", "国际科技智库观点演变_UNCTAD技术与创新报告跨期节点全文台账.csv"),
        ("149_UNCTAD技术与创新报告跨期节点全文结果.md", "国际科技智库观点演变_UNCTAD技术与创新报告跨期节点全文结果.md"),
        ("150_WIPO世界知识产权报告近十年轻量目录.csv", "国际科技智库观点演变_WIPO世界知识产权报告近十年轻量目录.csv"),
        ("151_WIPO世界知识产权报告近十年轻量目录结果.md", "国际科技智库观点演变_WIPO世界知识产权报告近十年轻量目录结果.md"),
        ("152_WIPO世界知识产权报告跨期节点全文台账.csv", "国际科技智库观点演变_WIPO世界知识产权报告跨期节点全文台账.csv"),
        ("153_WIPO世界知识产权报告跨期节点全文结果.md", "国际科技智库观点演变_WIPO世界知识产权报告跨期节点全文结果.md"),
        ("154_NSF_NSB研发与科学论文跨期专题全文台账.csv", "国际科技智库观点演变_NSF_NSB研发与科学论文跨期专题全文台账.csv"),
        ("155_NSF_NSB研发与科学论文跨期专题全文结果.md", "国际科技智库观点演变_NSF_NSB研发与科学论文跨期专题全文结果.md"),
        ("156_NSF_NSB科学体系人才转化跨期专题全文台账.csv", "国际科技智库观点演变_NSF_NSB科学体系人才转化跨期专题全文台账.csv"),
        ("157_NSF_NSB科学体系人才转化跨期专题全文结果.md", "国际科技智库观点演变_NSF_NSB科学体系人才转化跨期专题全文结果.md"),
        ("158_Nesta科技创新报告近十年轻量目录.csv", "国际科技智库观点演变_Nesta科技创新报告近十年轻量目录.csv"),
        ("159_Nesta科技创新报告近十年轻量目录结果.md", "国际科技智库观点演变_Nesta科技创新报告近十年轻量目录结果.md"),
        ("160_Nesta科技创新与中国比较跨期精选全文台账.csv", "国际科技智库观点演变_Nesta科技创新与中国比较跨期精选全文台账.csv"),
        ("161_Nesta科技创新与中国比较跨期精选全文结果.md", "国际科技智库观点演变_Nesta科技创新与中国比较跨期精选全文结果.md"),
    ):
        assert sha(root / source_name) == sha(kb / "06_数据资产" / kb_name)
    assert len(rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv")) >= 1
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv"))
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "06_数据资产" / "数据资产清单.csv"))
    print("viewpoint_research_validation=ok")
    print(f"official_seeds={len(seeds)} catalog={len(catalog)} evidence={len(evidence)} institution_cards=11 pdfs={len(pdfs)} non_anchor_assets={len(catalog_assets)} early_assets={len(early_assets)} cset_assets={len(cset_assets)} atlantic_assets={len(atlantic_assets)} belfer_assets={len(belfer_assets)} nbr_assets={len(nbr_assets)} merics_assets={len(merics_assets)} bruegel_assets={len(bruegel_assets)} crds_assets={len(crds_assets)} nistep_assets={len(nistep_assets)} stepi_assets={len(stepi_assets)} kistep_assets={len(kistep_assets)}")


if __name__ == "__main__":
    main()
