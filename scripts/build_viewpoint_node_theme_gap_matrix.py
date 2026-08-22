from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


NODE_LABELS = {
    "N1": "2016—2018 科学体系与开放创新基线",
    "N2": "2019—2020 使命导向与技术创新能力",
    "N3": "2021—2022 科研体系与产业转化能力强化",
    "N4": "2023—2024 战略技术、AI与创新政策重组",
    "N5": "2025—2026 科学能力、技术应用与全球协作重构",
}

CHINA_PATTERN = re.compile(
    r"中国|中國|China|Chinese|\bPRC\b|People['’]s Republic of China|중국|미중|한중|中美|中欧|中歐|对华|對華|涉华|涉華",
    re.I,
)

STRATEGIC_THEMES = {
    "T1_科学体系与基础研究": re.compile(
        r"基础研究|基礎研究|basic research|기초연구|基础科学|基礎科學|基礎科学|기초과학|"
        r"科学体系|科學體系|science system|과학체계|科研基础|研究基盤|연구기반|研究设施|研究施設|"
        r"연구시설|research infrastructure|大科学|大型研究|학술연구|学术研究|學術研究|研究生态|研究生態",
        re.I,
    ),
    "T2_技术创新与关键技术": re.compile(
        r"人工智能|인공지능|人工知能|\bAI\b|半导体|半導体|반도체|芯片|量子|양자|quantum|"
        r"战略技术|戰略技術|전략기술|关键技术|關鍵技術|核心技术|新兴技术|新興技術|"
        r"바이오|生物技术|生命科学|机器人|ロボット|로봇|算力|compute|先进材料|先端技術|첨단기술|"
        r"数字技术|數字技術|디지털기술|技術革新|技术创新|기술혁신|technology innovation",
        re.I,
    ),
    "T3_创新政策与研发治理": re.compile(
        r"创新政策|創新政策|innovation policy|科技政策|科學技術政策|과학기술정책|science policy|"
        r"使命导向|使命導向|mission[- ]oriented|国家创新体系|國家創新體系|national innovation system|"
        r"研究开发|研究開発|研发|研發|연구개발|\bR&D\b|研发投入|研究費|연구비|资助|資助|funding|"
        r"评价|評價|평가|科技指标|指標|indicator|前瞻|foresight|未来预测|未来予測|미래예측|"
        r"政策组合|政策組合|policy mix|国家能力|國家能力|국가역량",
        re.I,
    ),
    "T4_人才大学与科研组织": re.compile(
        r"科技人才|人才|人材|인재|博士|박사|"
        r"大学|大學|大学院|대학|researcher|研究者|연구자|知识流动|知識流動|职业流动|職業流動|"
        r"科研组织|科研組織|研究機関|연구기관|research organization|实验室|實驗室|研究所|科学院|科學院|"
        r"学术职业|學術職業|academic career|流动性|流動性|mobility",
        re.I,
    ),
    "T5_产业创新转化与区域生态": re.compile(
        r"产业创新|產業創新|산업혁신|industrial innovation|企业研发|企業研發|기업연구|企业创新|企業創新|"
        r"创业|創業|창업|startup|商业化|商業化|사업화|commerciali[sz]|技术转移|技術移転|기술이전|"
        r"产学合作|産学連携|산학협력|区域创新|地域革新|지역혁신|cluster|集群|클러스터|"
        r"先进制造|先進製造|첨단제조|manufactur|产业政策|產業政策|산업정책|industrial policy",
        re.I,
    ),
    "T6_国际合作开放科学与比较": re.compile(
        r"国际合作|國際合作|국제협력|国際協力|international cooperation|科技外交|기술외교|science diplomacy|"
        r"开放科学|開放科學|open science|国际比较|國際比較|국제비교|国際比較|international comparison|"
        r"全球科研|全球科学|全球科技|全球创新|global research|global science|global technolog|global innovation|"
        r"科学交流|科學交流|研究交流|合作网络|協力ネットワーク|共同研究|공동연구|"
        r"跨国|跨國|transnational|多边|多邊|multilateral",
        re.I,
    ),
    "T7_安全供应链与治理边界": re.compile(
        r"研究安全|科研安全|연구안보|보안정책|research security|供应链|供應鏈|공급망|サプライチェーン|supply chain|"
        r"经济安全|經濟安全|경제안보|economic security|export control|出口管制|輸出管理|수출통제|"
        r"韧性|韌性|resilien|脱钩|脫鉤|decoupl|디커플링|投资审查|投資審査|"
        r"军民融合|軍民融合|민군|国防|國防|국방|防衛|defen[cs]e|military|双用途|兩用|dual[- ]use|"
        r"数字治理|數字治理|digital governance|网络安全|網絡安全|cyber|사이버|サイバー|"
        r"标准|標準|표준|standard|规制|規制|regulation|治理边界|governance boundary",
        re.I,
    ),
}

# 安全、供应链与治理只保留为解释创新条件变化的语境标签，不构成独立覆盖目标。
COVERAGE_THEMES = tuple(theme for theme in STRATEGIC_THEMES if not theme.startswith("T7_"))
SECURITY_CONTEXT_THEME = "T7_安全供应链与治理边界"
SCIENCE_INNOVATION_MECHANISM = re.compile(
    r"基础研究|基礎研究|기초연구|basic research|fundamental research|科学体系|科學體系|science system|"
    r"research ecosystem|research infrastructure|研究开发|研究開発|研发|研發|연구개발|(?<![A-Za-z])R&D(?![A-Za-z])|"
    r"innovation|创新|創新|혁신|technology development|technological development|"
    r"科研组织|科研組織|research organization|大学|大學|university|talent|人才|人材|인재|"
    r"funding|资助|資助|产业创新|產業創新|industrial innovation|commerciali[sz]|技术转移|技術移転",
    re.I,
)

FAMILY_ALIASES = {"merics-tech": "merics"}

TIER_A = {
    "oecd-sti", "cset", "merics", "jst-crds", "nistep", "stepi", "kistep", "fraunhofer-isi",
}
TIER_B = {
    "belfer",
    "itif",
    "bruegel",
    "ifp",
    "stanford-hai",
    "us-ostp",
}

TIER_LABEL = {
    "A": "战略主轴",
    "B": "议题验证",
    "C": "边界与反证",
}

THEME_WEIGHT = {
    "T1_科学体系与基础研究": 5,
    "T2_技术创新与关键技术": 5,
    "T3_创新政策与研发治理": 4,
    "T4_人才大学与科研组织": 3,
    "T5_产业创新转化与区域生态": 3,
    "T6_国际合作开放科学与比较": 3,
    "T7_安全供应链与治理边界": 1,
}

NODE_WEIGHT = {"N1": 2, "N2": 4, "N3": 4, "N4": 4, "N5": 3}
TIER_WEIGHT = {"A": 5, "B": 3, "C": 0}
NODE_END_YEAR = {"N1": 2018, "N2": 2020, "N3": 2022, "N4": 2024, "N5": 2026}
KNOWN_PROJECT_START = {
    "cset": 2019,
    "atlantic-council-geotech": 2020,
    "ifp": 2021,
    "stanford-hai": 2019,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def node_for_date(published: str) -> str:
    year = int(published[:4])
    if year <= 2018:
        return "N1"
    if year <= 2020:
        return "N2"
    if year <= 2022:
        return "N3"
    if year <= 2024:
        return "N4"
    return "N5"


def family_id(institution_id: str) -> str:
    return FAMILY_ALIASES.get(institution_id, institution_id)


def tier_for(institution_id: str) -> str:
    institution_id = family_id(institution_id)
    if institution_id in TIER_A:
        return "A"
    if institution_id in TIER_B:
        return "B"
    return "C"


def classify_themes(row: dict[str, str], index_tags: set[str] | None = None) -> set[str]:
    text = " ".join(
        [
            row.get("报告名称", ""),
            row.get("示踪问题", ""),
            " ".join(sorted(index_tags or set())),
        ]
    )
    return {theme for theme, pattern in STRATEGIC_THEMES.items() if pattern.search(text)}


def china_relevance(row: dict[str, str], index_tags: set[str] | None = None) -> bool:
    text = " ".join(
        [
            row.get("报告名称", ""),
            row.get("示踪问题", ""),
            " ".join(sorted(index_tags or set())),
        ]
    )
    return bool(CHINA_PATTERN.search(text))


def is_security_dominant(themes: set[str]) -> bool:
    return SECURITY_CONTEXT_THEME in themes and not bool(themes & set(COVERAGE_THEMES))


def fulltext_axis_eligible(title: str, themes: set[str]) -> bool:
    """Keep security-led titles in the light catalog unless they expose an STI mechanism."""
    if not themes.intersection(COVERAGE_THEMES):
        return False
    if SECURITY_CONTEXT_THEME not in themes:
        return True
    return bool(SCIENCE_INNOVATION_MECHANISM.search(title))


def evidence_status(catalog_count: int, asset_count: int, searchable_count: int, tier: str) -> str:
    threshold = {"A": 3, "B": 2, "C": 1}[tier]
    if searchable_count >= threshold:
        return "充分"
    if searchable_count:
        return "可用"
    if asset_count:
        return "原文待文本化"
    if catalog_count:
        return "仅目录候选"
    return "空白"


def priority_score(
    tier: str,
    node: str,
    theme: str,
    catalog_count: int,
    asset_count: int,
    searchable_count: int,
    china_count: int = 0,
) -> int:
    if not catalog_count or asset_count or searchable_count or tier == "C":
        return 0
    china_bonus = 4 if china_count else 0
    return TIER_WEIGHT[tier] + NODE_WEIGHT[node] + THEME_WEIGHT[theme] + china_bonus + min(3, int(math.log2(catalog_count + 1)))


def existing_path(raw: str, research_root: Path) -> bool:
    if not raw:
        return False
    path = Path(raw)
    if not path.is_absolute():
        path = research_root / path
    return path.exists() and path.is_file()


@dataclass
class IndexEvidence:
    tags: set[str]
    asset_paths: set[str]
    text_paths: set[str]


def load_index_evidence(research_root: Path) -> dict[str, IndexEvidence]:
    evidence: dict[str, IndexEvidence] = defaultdict(lambda: IndexEvidence(set(), set(), set()))
    for path in sorted(research_root.glob("*主题索引.csv")):
        for row in read_csv(path):
            report_id = row.get("报告ID", "").strip()
            if not report_id:
                continue
            theme = (row.get("主题标签") or row.get("主题线索") or "").strip()
            if theme:
                evidence[report_id].tags.add(theme)
            for key in ("本地原始资产", "本地PDF"):
                value = row.get(key, "").strip()
                if value:
                    evidence[report_id].asset_paths.add(value)
            for key in ("本地文本", "逐页文本"):
                value = row.get(key, "").strip()
                if value:
                    evidence[report_id].text_paths.add(value)
    return evidence


def report_has_asset(row: dict[str, str], index: IndexEvidence, research_root: Path) -> bool:
    paths = {
        row.get("本地路径", "").strip(),
        row.get("本地原始资产路径", "").strip(),
        *index.asset_paths,
    }
    return any(existing_path(path, research_root) for path in paths if path)


def report_has_text(row: dict[str, str], index: IndexEvidence, research_root: Path) -> bool:
    report_id = row["报告ID"]
    expected = research_root / "03_证据底稿" / "文本" / f"{report_id}.txt"
    if expected.exists() and expected.stat().st_size > 0:
        return True
    return any(existing_path(path, research_root) for path in index.text_paths)


def report_rank(row: dict[str, str], themes: set[str]) -> tuple[int, str, str]:
    priority = row.get("优先级", "")
    priority_points = 6 if priority.startswith("P0") else 3 if priority.startswith("P1") else 0
    role_points = 3 if "锚点" in row.get("样本角色", "") else 0
    theme_points = max((THEME_WEIGHT[t] for t in themes), default=0)
    return (priority_points + role_points + theme_points + min(3, len(themes)), row.get("发布日期", ""), row["报告ID"])


def candidate_priority_score(
    tier: str,
    node: str,
    themes: set[str],
    china: bool,
    priority: str,
    cell_scores: list[int],
    security_context: bool = False,
) -> int:
    score = max(cell_scores, default=0)
    if china:
        priority_points = 5 if priority.startswith("P0") else 2 if priority.startswith("P1") else 0
        direct_score = (
            TIER_WEIGHT[tier]
            + NODE_WEIGHT[node]
            + max((THEME_WEIGHT[theme] for theme in themes), default=0)
            + 4
            + priority_points
            + min(2, len(themes))
        )
        score = max(score, direct_score)
    if security_context:
        score -= 6
        if score < 14:
            return 0
    return score


def build_outputs(
    research_root: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], str]:
    catalog = read_csv(research_root / "05_报告总目录.csv")
    index_map = load_index_evidence(research_root)
    empty_index = IndexEvidence(set(), set(), set())

    families: dict[str, str] = {}
    reports: list[dict[str, object]] = []
    for row in catalog:
        family = family_id(row["机构ID"])
        families.setdefault(family, row.get("机构英文名", family))
        index = index_map.get(row["报告ID"], empty_index)
        themes = classify_themes(row, index.tags)
        if not themes:
            continue
        reports.append(
            {
                "row": row,
                "family": family,
                "node": node_for_date(row["发布日期"]),
                "themes": themes,
                "china": china_relevance(row, index.tags),
                "asset": report_has_asset(row, index, research_root),
                "text": report_has_text(row, index, research_root),
            }
        )

    buckets: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for report in reports:
        for theme in report["themes"]:
            buckets[(report["family"], report["node"], theme)].append(report)

    matrix: list[dict[str, object]] = []
    for family in sorted(families):
        tier = tier_for(family)
        for node, node_label in NODE_LABELS.items():
            for theme in COVERAGE_THEMES:
                items = buckets.get((family, node, theme), [])
                catalog_ids = {item["row"]["报告ID"] for item in items}
                asset_ids = {item["row"]["报告ID"] for item in items if item["asset"]}
                text_ids = {item["row"]["报告ID"] for item in items if item["text"]}
                china_ids = {item["row"]["报告ID"] for item in items if item["china"]}
                candidates = sorted(
                    (item for item in items if not item["asset"]),
                    key=lambda item: report_rank(item["row"], item["themes"]),
                    reverse=True,
                )
                score = priority_score(tier, node, theme, len(catalog_ids), len(asset_ids), len(text_ids), len(china_ids))
                status = evidence_status(len(catalog_ids), len(asset_ids), len(text_ids), tier)
                if status == "仅目录候选" and score >= 14:
                    action = "P0定点补取1—2份"
                elif status == "仅目录候选" and score:
                    action = "P1候选复核"
                elif status == "原文待文本化":
                    action = "推进文本化或OCR"
                elif status == "空白" and tier in {"A", "B"}:
                    action = "先补轻量目录"
                else:
                    action = "停止扩张，转入编码"
                matrix.append(
                    {
                        "机构层级": f"{tier}_{TIER_LABEL[tier]}",
                        "机构ID": family,
                        "机构英文名": families[family],
                        "转向节点": node,
                        "节点说明": node_label,
                        "战略主题": theme,
                        "目录命中报告数": len(catalog_ids),
                        "本地原文报告数": len(asset_ids),
                        "可检索文本报告数": len(text_ids),
                        "其中中国关联报告数": len(china_ids),
                        "证据状态": status,
                        "补源优先分": score,
                        "推进动作": action,
                        "目录候选报告ID": ";".join(item["row"]["报告ID"] for item in candidates[:3]),
                    }
                )

    queue_candidates: list[dict[str, object]] = []
    for report in reports:
        row = report["row"]
        family = report["family"]
        tier = tier_for(family)
        if tier == "C" or report["asset"]:
            continue
        themes = report["themes"]
        title_themes = classify_themes(
            {"报告名称": row["报告名称"], "示踪问题": ""},
            set(),
        )
        if is_security_dominant(title_themes) or not fulltext_axis_eligible(row["报告名称"], title_themes):
            continue
        cell_scores = [
            priority_score(
                tier,
                report["node"],
                theme,
                len({item["row"]["报告ID"] for item in buckets[(family, report["node"], theme)]}),
                len({item["row"]["报告ID"] for item in buckets[(family, report["node"], theme)] if item["asset"]}),
                len({item["row"]["报告ID"] for item in buckets[(family, report["node"], theme)] if item["text"]}),
                len({item["row"]["报告ID"] for item in buckets[(family, report["node"], theme)] if item["china"]}),
            )
            for theme in themes
            if theme in COVERAGE_THEMES
        ]
        score = candidate_priority_score(
            tier,
            report["node"],
            themes,
            bool(report["china"]),
            row.get("优先级", ""),
            cell_scores,
            SECURITY_CONTEXT_THEME in title_themes,
        )
        if not score:
            continue
        queue_candidates.append(
            {
                "补源优先分": score,
                "机构层级": f"{tier}_{TIER_LABEL[tier]}",
                "机构ID": family,
                "转向节点": report["node"],
                "战略主题": ";".join(sorted(themes)),
                "中国关联": "是" if report["china"] else "否",
                "报告ID": row["报告ID"],
                "发布日期": row["发布日期"],
                "报告名称": row["报告名称"],
                "报告类型": row.get("报告类型", ""),
                "优先级": row.get("优先级", ""),
                "官方链接": row.get("原文链接", ""),
                "推进动作": "先核落地页与附件类型；通过6分阈值后最多补取1份",
            }
        )

    queue_candidates.sort(
        key=lambda row: (int(row["补源优先分"]), row["优先级"].startswith("P0"), row["发布日期"], row["报告ID"]),
        reverse=True,
    )
    queue: list[dict[str, object]] = []
    institution_counts: dict[str, int] = defaultdict(int)
    node_counts: dict[tuple[str, str], int] = defaultdict(int)
    seen: set[str] = set()
    for item in queue_candidates:
        if item["报告ID"] in seen:
            continue
        family = str(item["机构ID"])
        node = str(item["转向节点"])
        if institution_counts[family] >= 8 or node_counts[(family, node)] >= 3:
            continue
        seen.add(str(item["报告ID"]))
        institution_counts[family] += 1
        node_counts[(family, node)] += 1
        queue.append(item)
        if len(queue) >= 60:
            break

    family_node_counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in catalog:
        family_node_counts[(family_id(row["机构ID"]), node_for_date(row["发布日期"]))] += 1
    catalog_queue: list[dict[str, object]] = []
    for family in sorted(families):
        tier = tier_for(family)
        if tier == "C":
            continue
        minimum = 5 if tier == "A" else 3
        for node, label in NODE_LABELS.items():
            start_year = KNOWN_PROJECT_START.get(family, 0)
            if start_year and NODE_END_YEAR[node] < start_year:
                continue
            current = family_node_counts[(family, node)]
            if current >= minimum:
                continue
            gap = minimum - current
            score = TIER_WEIGHT[tier] + NODE_WEIGHT[node] + gap
            catalog_queue.append(
                {
                    "目录扩展优先分": score,
                    "机构层级": f"{tier}_{TIER_LABEL[tier]}",
                    "机构ID": family,
                    "机构英文名": families[family],
                    "转向节点": node,
                    "节点说明": label,
                    "现有目录数": current,
                    "最低观察目标": minimum,
                    "目录缺口数": gap,
                    "采集主题边界": "science;technology;innovation;China；安全议题仅在改变创新条件时纳入",
                    "全文策略": "仅补官方元数据和附件入口；全文待覆盖矩阵触发",
                }
            )
    catalog_queue.sort(
        key=lambda row: (int(row["目录扩展优先分"]), row["机构层级"], row["机构ID"], row["转向节点"]),
        reverse=True,
    )

    status_counts: dict[str, int] = defaultdict(int)
    for row in matrix:
        status_counts[str(row["证据状态"])] += 1
    queue_by_institution: dict[str, int] = defaultdict(int)
    for row in queue:
        queue_by_institution[str(row["机构ID"])] += 1
    china_reports = [report for report in reports if report["china"]]
    china_assets = [report for report in china_reports if report["asset"]]
    china_texts = [report for report in china_reports if report["text"]]
    summary_lines = [
        "# 机构—转向节点—战略主题覆盖缺口结果",
        "",
        f"- 统一总目录：{len(catalog)}条。",
        f"- 纳入矩阵的机构家族：{len(families)}个；节点：{len(NODE_LABELS)}个；科学技术创新主轴：{len(COVERAGE_THEMES)}条。",
        f"- 覆盖矩阵单元：{len(matrix)}个。",
        f"- 证据状态：充分{status_counts['充分']}个、可用{status_counts['可用']}个、原文待文本化{status_counts['原文待文本化']}个、仅目录候选{status_counts['仅目录候选']}个、空白{status_counts['空白']}个。",
        f"- 定点补源候选：{len(queue)}份；每机构最多8份、每机构每节点最多3份。",
        f"- 队列中的中国关联候选：{sum(1 for row in queue if row['中国关联'] == '是')}份。",
        f"- 中国关联目录材料：{len(china_reports)}份；已有本地原文{len(china_assets)}份、可检索文本{len(china_texts)}份。",
        f"- 轻量目录扩展单元：{len(catalog_queue)}个；只补官方元数据和附件入口。",
        "",
        "## 队列分布",
        "",
    ]
    if queue_by_institution:
        for institution, count in sorted(queue_by_institution.items(), key=lambda item: (-item[1], item[0])):
            summary_lines.append(f"- {institution}：{count}份。")
    else:
        summary_lines.append("- 当前没有满足阈值的全文补源候选。")
    summary_lines.extend(
        [
            "",
            "## 使用边界",
            "",
            "矩阵只计算科学体系与基础研究、技术创新与关键技术、创新政策与研发治理、人才大学与科研组织、产业创新转化与区域生态、国际合作开放科学与比较六条主轴。安全、供应链与治理仅保留为语境标签，不生成独立覆盖缺口，也不单独触发全文补取；只有题名明确涉及科研投入、创新体系、人才组织、技术开发或成果转化机制时，相关材料才可进入全文候选。中国关联作为独立交叉维度统计。目录命中只表示题名、关键词或既有主题索引显示该机构关注相关议题。机构立场、因果解释和政策主张必须回查本地全文、原句与页码。‘空白’优先触发轻量目录扩展；‘仅目录候选’才可能触发精选全文补取；‘充分’单元停止扩张并转入观点编码。",
            "",
            "定点队列是下载前复核清单。候选仍须检查官方落地页、附件类型、重复度和对战略转向证据链的增量，不能把队列自动解释为必须全部下载。",
        ]
    )
    return matrix, queue, catalog_queue, "\n".join(summary_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    matrix, queue, catalog_queue, summary = build_outputs(root)
    write_csv(
        root / "69_机构节点主题覆盖缺口矩阵.csv",
        matrix,
        [
            "机构层级",
            "机构ID",
            "机构英文名",
            "转向节点",
            "节点说明",
            "战略主题",
            "目录命中报告数",
            "本地原文报告数",
            "可检索文本报告数",
            "其中中国关联报告数",
            "证据状态",
            "补源优先分",
            "推进动作",
            "目录候选报告ID",
        ],
    )
    write_csv(
        root / "70_定点补源优先队列.csv",
        queue,
        [
            "补源优先分",
            "机构层级",
            "机构ID",
            "转向节点",
            "战略主题",
            "中国关联",
            "报告ID",
            "发布日期",
            "报告名称",
            "报告类型",
            "优先级",
            "官方链接",
            "推进动作",
        ],
    )
    write_csv(
        root / "72_轻量目录扩展优先队列.csv",
        catalog_queue,
        [
            "目录扩展优先分",
            "机构层级",
            "机构ID",
            "机构英文名",
            "转向节点",
            "节点说明",
            "现有目录数",
            "最低观察目标",
            "目录缺口数",
            "采集主题边界",
            "全文策略",
        ],
    )
    (root / "71_覆盖缺口结果.md").write_text(summary, encoding="utf-8")
    print(f"matrix_rows={len(matrix)} queue_rows={len(queue)} catalog_queue_rows={len(catalog_queue)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
