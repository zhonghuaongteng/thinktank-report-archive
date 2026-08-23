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


def expected_rathenau_selected_ids() -> set[str]:
    return {
        "C-RATHENAU-2015-RD-GOES-GLOBAL",
        "C-RATHENAU-2016-PUBLIC-KNOWLEDGE-ORGANISATIONS-NETHERLANDS",
        "C-RATHENAU-2016-SHAPING-INNOVATION-THROUGH-POLICY",
        "C-RATHENAU-2018-REGIONAL-INNOVATION",
        "C-RATHENAU-2018-INDUSTRY-SEEKING-UNIVERSITY",
        "C-RATHENAU-2020-EUROPEAN-RESEARCH-AND-INNOVATION-NEW-GEOPOLITICAL-ARENA",
        "C-RATHENAU-2021-PERSPECTIVES-FUTURE-OPEN-SCIENCE",
        "C-RATHENAU-2022-RESEARCH-PROGRAMMES-MISSION",
        "C-RATHENAU-2022-TOTAL-INVESTMENT-RESEARCH-AND-INNOVATION-2020-2026",
        "C-RATHENAU-2024-NWO-PROGRAMMES-CURIOSITY-DRIVEN-RESEARCH",
        "C-RATHENAU-2024-KNOWLEDGE-FUTURE",
        "C-RATHENAU-2025-CHINA-SCIENTIFIC-SUPERPOWER",
        "C-RATHENAU-2026-GEOPOLITICS-SCIENCE-POLICY",
    }


def expected_ifp_selected_ids() -> set[str]:
    return {
        "C-IFP-2022-FUND-ORGANIZATIONS-NOT-PROJECTS-DIVERSIFYING-AMERICAS-INNOVATION-ECOSYSTEM-WITH-A-",
        "C-IFP-2022-PILOTING-AND-EVALUATING-NSF-SCIENCE-LOTTERY-GRANTS",
        "C-IFP-2022-SEMICONDUCTOR-INVESTMENTS-WONT-PAY-OFF-IF-CONGRESS-DOESNT-FIX-THE-TALENT-BOTTLENEC",
        "C-IFP-2022-HOW-DO-WE-MAKE-AN-ENTREPRENEURIAL-STATE",
        "C-IFP-2023-BUILDING-A-BETTER-NIH",
        "C-IFP-2023-TO-SPEED-UP-SCIENTIFIC-PROGRESS-WE-NEED-TO-UNDERSTAND-SCIENCE-POLICY",
        "C-IFP-2023-WHERE-CAN-FEDERAL-AI-RD-FUNDING-GO-THE-FURTHEST",
        "C-IFP-2024-COMPUTE-IN-AMERICA",
        "C-IFP-2024-NIST-FOUNDATION",
        "C-IFP-2024-MAXIMIZING-THE-SCIENTIFIC-ROI-FROM-INTERNATIONAL-PHDS",
        "C-IFP-2025-CATALYZING-A-GOLDEN-AGE",
        "C-IFP-2025-INDIRECT-COST-RECOVERY-AND-AMERICAN-INNOVATION",
        "C-IFP-2025-SCALING-MATERIALS-DISCOVERY-WITH-SELF-DRIVING-LABS",
        "C-IFP-2025-AMERICAN-SCIENCE-SHOULD-TAKE-A-LOT-MORE-RISKS",
        "C-IFP-2026-SCIENCE-AGENCIES-NEED-METASCIENCE-UNITS",
        "C-IFP-2026-PREPARING-FOR-AI-RESEARCH-AUTOMATION",
    }


def expected_itif_selected_ids() -> set[str]:
    return {
        "C-ITIF-RB-2016-LOCALIZING-ECONOMIC-IMPACT-RESEARCH-AND-DEVELOPMENT-POLICY-PROPOSALS-TRUMP",
        "C-ITIF-RB-2017-INVESTING-INNOVATION-INFRASTRUCTURE-RESTORE-US-GROWTH",
        "C-ITIF-RB-2017-ACROSS-SECOND-VALLEY-DEATH-DESIGNING-SUCCESSFUL-ENERGY-DEMONSTRATION",
        "C-ITIF-RB-2018-INDUSTRY-FUNDING-UNIVERSITY-RESEARCH-WHICH-STATES-LEAD",
        "C-ITIF-RB-2018-WHY-US-BUSINESS-RD-NOT-STRONG-IT-APPEARS",
        "C-ITIF-RB-2019-WHY-FEDERAL-RD-POLICY-NEEDS-PRIORITIZE-PRODUCTIVITY-DRIVE-GROWTH-AND-REDUCE",
        "C-ITIF-RB-2020-INNOVATION-DRAG-CHINAS-ECONOMIC-IMPACT-DEVELOPED-NATIONS",
        "C-ITIF-RB-2020-IMPACT-CHINAS-POLICIES-GLOBAL-BIOPHARMACEUTICAL-INDUSTRY-INNOVATION",
        "C-ITIF-RB-2020-IMPACT-CHINAS-PRODUCTION-SURGE-INNOVATION-GLOBAL-SOLAR-PHOTOVOLTAICS",
        "C-ITIF-RB-2020-UNDERSTANDING-US-NATIONAL-INNOVATION-SYSTEM-2020",
        "C-ITIF-RB-2020-CHINESE-COMPETITIVENESS-INTERNATIONAL-DIGITAL-ECONOMY",
        "C-ITIF-RB-2020-HOW-UNITED-STATES-CAN-INCREASE-ACCESS-SUPERCOMPUTING",
        "C-ITIF-RB-2021-FIVE-FREE-MARKET-MYTHS-ABOUT-INCREASING-FEDERAL-RESEARCH-FUNDING",
        "C-ITIF-RB-2021-WHO-WINNING-AI-RACE-CHINA-EU-OR-UNITED-STATES-2021-UPDATE",
        "C-ITIF-RB-2021-2021-GLOBAL-ENERGY-INNOVATION-INDEX-NATIONAL-CONTRIBUTIONS-GLOBAL-CLEAN",
        "C-ITIF-RB-2022-INDUSTRY-UNIVERSITY-PARTNERSHIPS-TO-CREATE-AI-UNIVERSITIES",
        "C-ITIF-RB-2022-FOUNDATION-FOR-ENERGY-SECURITY-AND-INNOVATION",
        "C-ITIF-RB-2023-INNOVATION-WARS-HOW-CHINA-IS-GAINING-ON-THE-UNITED-STATES-IN-CORPORATE-RD",
        "C-ITIF-RB-2023-2023-HAMILTON-INDEX",
        "C-ITIF-RB-2024-FEDERAL-FUNDING-FOR-BASIC-RESEARCH-SPURS-CLEAN-ENERGY-DISCOVERIES-EIGHT-CASE-STUDIES",
        "C-ITIF-RB-2025-CONGRESS-SHOULD-FULLY-FUND-NSF-TIP-DIRECTORATE",
        "C-ITIF-RB-2025-HOW-NIH-FUNDED-SCIENCE-SUPPORTS-US-BIOPHARMACEUTICAL-INNOVATION",
        "C-ITIF-RB-2026-TRACKING-RD-LEADERSHIP-US-ADVANTAGE-NARROWING-AS-CHINA-GAINS-GROUND",
        "C-ITIF-RB-2026-PAYING-FOR-OUTCOMES-TYING-UNIVERSITY-FUNDING-TO-COMMERCIAL-RESULTS",
        "C-ITIF-RB-2019-CHINAS-BIOPHARMACEUTICAL-STRATEGY-CHALLENGE-OR-COMPLEMENT-US-INDUSTRY",
        "C-ITIF-RB-2024-HOW-EXPERTS-CHINA-UNITED-KINGDOM-VIEW-AI-RISKS-COLLABORATION",
        "C-ITIF-RB-2025-FROM-FAST-FOLLOWER-TO-INNOVATION-LEADER-RESTRUCTURING-SOUTH-KOREAS-TECHNOLOGY-REGULATION",
        "C-ITIF-RB-2026-US-TECHNOLOGY-COMPANIES-SHOULD-KEEP-OPERATING-IN-CHINA",
        "C-ITIF-RB-2026-HOW-INNOVATIVE-IS-CHINAS-SPACE-INDUSTRY",
        "C-ITIF-RB-2026-CHINAS-BURGEONING-BIOPHARMACEUTICAL-COMPETITIVENESS-DEMANDS-US-RESPONSE",
        "C-ITIF-RB-2020-HOW-CHINAS-MERCANTILIST-POLICIES-HAVE-UNDERMINED-GLOBAL-INNOVATION-TELECOM",
        "C-ITIF-RB-2021-HEADING-TRACK-IMPACT-CHINAS-MERCANTILIST-POLICIES-GLOBAL-HIGH-SPEED-RAIL",
        "C-ITIF-RB-2025-CHINA-PLANS-TO-DOMINATE-A-KEY-SEMICONDUCTOR-MATERIAL",
        "C-ITIF-RB-2026-COMAC-CHINAS-LOOMING-THREAT-TO-GLOBAL-AVIATION-INDUSTRY",
    }


def expected_fas_selected_ids() -> set[str]:
    return {
        "C-FAS-2020-A-CONVERGENCE-DIRECTORATE-AT-THE-NATIONAL-SCIENCE-FOUNDATION",
        "C-FAS-2020-AMBITIOUS-ACHIEVABLE-AND-SUSTAINABLE",
        "C-FAS-2020-CLOSING-CRITICAL-GAPS",
        "C-FAS-2020-FOCUSED-RESEARCH-ORGANIZATIONS-TO-ACCELERATE-SCIENCE-TECHNOLOGY-AND-MEDICINE",
        "C-FAS-2021-CREATING-A-NATIONAL-DEEPTECH-CAPITAL-FUND",
        "C-FAS-2021-FORGING-1-000-VENTURE-SCIENTISTS-TO-TRANSFORM-THE-INNOVATION-ECONOMY",
        "C-FAS-2021-INDUSTRIAL-POLICY-MEMO",
        "C-FAS-2022-EXPANDING-PATHWAYS-FOR-CAREER-RESEARCH-SCIENTISTS-IN-ACADEMIA",
        "C-FAS-2022-IMPROVING-RESEARCH-FUNDING-EFFICIENCIES-AND-PROPOSAL-DIVERSITY-THROUGH-NSF-SCIENCE-LOTTERY-GRANTS",
        "C-FAS-2022-UNLOCKING-FEDERAL-GRANT-DATA-TO-INFORM-EVIDENCE-BASED-SCIENCE-FUNDING",
        "C-FAS-2023-118TH-CONGRESS", "C-FAS-2023-118TH-CONGRESS-EMERGING-TECH-COMPETITIVENESS",
        "C-FAS-2023-APPLYING-ARPA-I-A-PROVEN-MODEL-FOR-TRANSPORTATION-INFRASTRUCTURE",
        "C-FAS-2024-AGENCY-PERSPECTIVES-BIOECONOMY",
        "C-FAS-2024-CREATING-A-SCIENCE-AND-TECHNOLOGY-HUB-IN-CONGRESS",
        "C-FAS-2024-MICRO-ARPA", "C-FAS-2024-PREDICTING-PROGRESS-UTILITY-FORECASTING",
        "C-FAS-2025-CONTAIN-CHINA-ON-LEGACY-CHIPS", "C-FAS-2025-FUELING-THE-BIOECONOMY-CLEAN-ENERGY",
        "C-FAS-2025-MEASURING-RESEARCH-BUREAUCRACY", "C-FAS-2025-NATIONAL-INSTITUTE-FOR-HIGH-REWARD-RESEARCH",
        "C-FAS-2025-REBUILD-CORPORATE-RESEARCH", "C-FAS-2026-NATIONAL-AI-LABORATORY-AT-COMMERCE",
        "C-FAS-2026-REVITALIZING-US-AUTO-INDUSTRY", "C-FAS-2026-ROI-OF-RD",
        "C-FAS-2026-SUSTAINING-SCIENTIFIC-COLLECTIONS-IN-THE-AGE-OF-AI",
    }


def expected_csis_rai_selected_ids() -> set[str]:
    return {
        "C-CSIS-RAI-2021-WHY-RENEWING-AMERICAN-INNOVATION-ENDLESS-FRONTIER-ACT-AND-BIDENS-BID-MAINTAINING-US-GLOBAL",
        "C-CSIS-RAI-2021-US-COMPETITIVENESS-WHERE-DO-WE-STAND-WHAT-DO-WE-DO-NOW",
        "C-CSIS-RAI-2021-WINNING-TECH-TALENT-COMPETITION",
        "C-CSIS-RAI-2022-WILL-AMERICA-SQUANDER-ITS-NEW-SPUTNIK-MOMENT",
        "C-CSIS-RAI-2022-UNTAPPED-INNOVATION",
        "C-CSIS-RAI-2023-CHINAS-DRIVE-LEADERSHIP-GLOBAL-RESEARCH-AND-DEVELOPMENT",
        "C-CSIS-RAI-2023-IMPLEMENTING-CHIPS-ACT-SEMATECHS-LESSONS-NATIONAL-SEMICONDUCTOR-TECHNOLOGY-CENTER",
        "C-CSIS-RAI-2023-INCLUSIVE-INNOVATION-US-ECONOMIC-GROWTH-AND-RESILIENCY",
        "C-CSIS-RAI-2023-QUANTUM-CANT-BE-BUSINESS-USUAL-ISSUES-REAUTHORIZATION-NATIONAL-QUANTUM-INITIATIVE-ACT",
        "C-CSIS-RAI-2024-FRENCH-MODEL-COOPERATIVE-SEMICONDUCTOR-RESEARCH-LESSONS-CEA-LETI",
        "C-CSIS-RAI-2024-INVESTING-SCIENCE-AND-TECHNOLOGY",
        "C-CSIS-RAI-2024-UNDERSTANDING-US-BIOPHARMACEUTICAL-INNOVATION-ECOSYSTEM",
        "C-CSIS-RAI-2024-IMEC-WORLD-LEADING-COOPERATIVE-RESEARCH-CENTER-MICROELECTRONICS",
        "C-CSIS-RAI-2025-ALBANY-NANOTECHS-POTENTIAL-SUPPORT-NATIONAL-SEMICONDUCTOR-TECHNOLOGY-CENTER",
        "C-CSIS-RAI-2025-NETHERLANDS-INNOVATION-LANDSCAPE",
        "C-CSIS-RAI-2025-INNOVATION-LIGHTBULB-EXAMINING-CHINAS-STRATEGIC-REGIONAL-INNOVATION-AND-RD-DISTRIBUTION",
        "C-CSIS-RAI-2025-PUBLIC-AND-PRIVATE-RD-ARE-COMPLEMENTS-NOT-SUBSTITUTES",
        "C-CSIS-RAI-2025-COMPETING-CHINAS-PUBLIC-RD-MODEL-LESSONS-AND-RISKS-US-INNOVATION-STRATEGY",
        "C-CSIS-RAI-2026-UNDERSTANDING-CHINAS-QUEST-QUANTUM-ADVANCEMENT",
        "C-CSIS-RAI-2026-LEVERAGING-SBIR-QUANTUM-COMMERCIALIZATION-AND-SUPPLY-CHAIN-GROWTH",
        "C-CSIS-RAI-2026-POWERING-INNOVATION-DATA-CENTERS-COMPUTE-AND-US-COMPETITIVENESS",
        "C-CSIS-RAI-2022-WHAT-CAN-PATENT-DATA-REVEAL-ABOUT-US-CHINA-TECHNOLOGY-COMPETITION",
        "C-CSIS-RAI-2022-CHINA-INNOVATION-CHALLENGE-CONVERSATION-PROFESSOR-JONATHAN-BARNETT",
        "C-CSIS-RAI-2024-INTELLECTUAL-PROPERTY-RIGHTS-US-CHINA-INNOVATION-COMPETITION",
        "C-CSIS-RAI-2024-WHAT-RISC-V-MEANS-FUTURE-CHIP-DEVELOPMENT",
        "C-CSIS-RAI-2025-INNOVATION-LIGHTBULB-INNOVATION-COMPETITION-CHIP-DESIGN-BETWEEN-US-AND-CHINA",
        "C-CSIS-RAI-2025-UNITED-STATES-CANNOT-AFFORD-DISARRAY-CHINA-STRENGTHENS-ITS-BIOPHARMACEUTICAL-INDUSTRY",
    }


def expected_eu_stoa_selected_ids() -> set[str]:
    return {
        "C-EU-STOA-EPRS-STU-2016-563501", "C-EU-STOA-EPRS-STU-2017-603183",
        "C-EU-STOA-EPRS-STU-2017-614531", "C-EU-STOA-EPRS-STU-2018-614537",
        "C-EU-STOA-EPRS-STU-2018-614546", "C-EU-STOA-EPRS-STU-2019-634444",
        "C-EU-STOA-EPRS-STU-2019-634447", "C-EU-STOA-EPRS-IDA-2020-641542",
        "C-EU-STOA-EPRS-IDA-2020-641543", "C-EU-STOA-EPRS-STU-2021-690029",
        "C-EU-STOA-EPRS-STU-2021-697184", "C-EU-STOA-EPRS-STU-2021-697197",
        "C-EU-STOA-EPRS-STU-2022-697218", "C-EU-STOA-EPRS-STU-2022-737114",
        "C-EU-STOA-EPRS-STU-2023-740259", "C-EU-STOA-EPRS-STU-2023-753166",
        "C-EU-STOA-EPRS-STU-2024-757813", "C-EU-STOA-EPRS-STU-2024-762848",
        "C-EU-STOA-EPRS-STU-2025-765780", "C-EU-STOA-EPRS-STU-2026-774682",
    }


def expected_eu_jrc_selected_ids() -> set[str]:
    return {
        "C-EU-JRC-JRC100825", "C-EU-JRC-JRC101970", "C-EU-JRC-JRC102148", "C-EU-JRC-JRC103716", "C-EU-JRC-JRC107386", "C-EU-JRC-JRC108520",
        "C-EU-JRC-JRC113807", "C-EU-JRC-JRC113826", "C-EU-JRC-JRC116516", "C-EU-JRC-JRC118614",
        "C-EU-JRC-JRC119974", "C-EU-JRC-JRC121184", "C-EU-JRC-JRC121318", "C-EU-JRC-JRC124072", "C-EU-JRC-JRC125613",
        "C-EU-JRC-JRC129967", "C-EU-JRC-JRC131882", "C-EU-JRC-JRC133613", "C-EU-JRC-JRC134319", "C-EU-JRC-JRC134544",
        "C-EU-JRC-JRC137266", "C-EU-JRC-JRC137811", "C-EU-JRC-JRC138601", "C-EU-JRC-JRC142093", "C-EU-JRC-JRC142637", "C-EU-JRC-JRC144638",
        "C-EU-JRC-JRC145507", "C-EU-JRC-JRC147828",
        "C-EU-JRC-JRC111622", "C-EU-JRC-JRC115449", "C-EU-JRC-JRC128744",
        "C-EU-JRC-JRC137550", "C-EU-JRC-JRC140126", "C-EU-JRC-JRC142609",
    }


def expected_efi_selected_ids() -> set[str]:
    return {
        "C-DE-EFI-2016-B1", "C-DE-EFI-2017-B2-1", "C-DE-EFI-2018-B3", "C-DE-EFI-2019-A3",
        "C-DE-EFI-2020-B3", "C-DE-EFI-2021-B1", "C-DE-EFI-2022-B1", "C-DE-EFI-2023-B2",
        "C-DE-EFI-2024-B2", "C-DE-EFI-2025-B2", "C-DE-EFI-2026-B3",
    }


def expected_rieti_selected_ids() -> set[str]:
    return {
        "C-JP-RIETI-16-E-041", "C-JP-RIETI-17-E-056", "C-JP-RIETI-17-E-111",
        "C-JP-RIETI-17-E-126", "C-JP-RIETI-18-P-012",
        "C-JP-RIETI-19-E-095", "C-JP-RIETI-20-E-045", "C-JP-RIETI-20-E-058",
        "C-JP-RIETI-21-E-026", "C-JP-RIETI-21-J-052", "C-JP-RIETI-22-E-030",
        "C-JP-RIETI-23-E-053", "C-JP-RIETI-23-J-015", "C-JP-RIETI-23-J-020",
        "C-JP-RIETI-24-E-013", "C-JP-RIETI-24-E-075", "C-JP-RIETI-25-E-089",
        "C-JP-RIETI-25-J-005",
        "C-JP-RIETI-26-E-021",
    }


def expected_royal_society_selected_ids() -> set[str]:
    return {
        "C-UK-RS-2017-MACHINE-LEARNING-THE-POWER-AND-PROMISE-OF-CO-311EB7",
        "C-UK-RS-2018-RESEARCH-CULTURE-EMBEDDING-INCLUSIVE-EXCELLE-661D64",
        "C-UK-RS-2019-DYNAMICS-OF-DATA-SCIENCE-SKILLS-BCA1BB",
        "C-UK-RS-2020-THE-ROLE-OF-PUBLIC-AND-NON-PROFIT-RESEARCH-O-A0FA33",
        "C-UK-RS-2021-THE-RESEARCH-AND-TECHNICAL-WORKFORCE-IN-THE--8FF6F1",
        "C-UK-RS-2022-REGIONAL-ABSORPTIVE-CAPACITY-THE-SKILLS-DIME-BB5B95",
        "C-UK-RS-2023-TRANSFORMING-UK-TRANSLATION-SIX-YEARS-IN-1A8BFB",
        "C-UK-RS-2024-SCIENCE-IN-THE-AGE-OF-AI-788E10",
        "C-UK-RS-2024-SCIENCE-AND-THE-ECONOMY-6436B2",
        "C-UK-RS-2025-SCIENCE-2040-INTERIM-REPORT-CEF6AF",
        "C-UK-RS-2026-2026-CHINA-UK-SCIENCE-POLICY-DIALOGUE-ON-FOO-3F4631",
    }


def expected_acatech_selected_ids() -> set[str]:
    return {
        "C-DE-ACATECH-2791", "C-DE-ACATECH-2786", "C-DE-ACATECH-2739", "C-DE-ACATECH-2638",
        "C-DE-ACATECH-18133", "C-DE-ACATECH-21040", "C-DE-ACATECH-27003", "C-DE-ACATECH-37012",
        "C-DE-ACATECH-44304", "C-DE-ACATECH-51945", "C-DE-ACATECH-54254", "C-DE-ACATECH-60073",
    }


def expected_nasem_selected_ids() -> set[str]:
    return {
        "C-US-NASEM-21824", "C-US-NASEM-24905", "C-US-NASEM-23472", "C-US-NASEM-25116",
        "C-US-NASEM-25303", "C-US-NASEM-25384", "C-US-NASEM-25729", "C-US-NASEM-26006",
        "C-US-NASEM-26290", "C-US-NASEM-26830", "C-US-NASEM-26647", "C-US-NASEM-27042",
        "C-US-NASEM-27091", "C-US-NASEM-27190", "C-US-NASEM-27787", "C-US-NASEM-27873",
        "C-US-NASEM-29212", "C-US-NASEM-29063",
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
        "162_Rathenau英文正式报告近十年轻量总目录.csv", "163_Rathenau英文正式报告近十年轻量总目录结果.md",
        "164_Rathenau科技创新与中国比较跨期精选全文台账.csv", "165_Rathenau科技创新与中国比较跨期精选全文结果.md",
        "166_IFP科技创新正式成果轻量总目录.csv", "167_IFP科技创新正式成果轻量总目录结果.md",
        "168_IFP科技创新机制与中国比较精选全文台账.csv", "169_IFP科技创新机制与中国比较精选全文结果.md",
        "170_ITIF正式报告与简报近十年轻量总目录.csv", "171_ITIF正式报告与简报近十年轻量总目录结果.md",
        "172_ITIF科技创新机制与中国比较跨期精选全文台账.csv", "173_ITIF科技创新机制与中国比较跨期精选全文结果.md",
        "174_FAS报告与政策备忘录近十年轻量总目录.csv", "175_FAS报告与政策备忘录近十年轻量总目录结果.md",
        "176_FAS科技创新机制与中国比较跨期精选全文台账.csv", "177_FAS科技创新机制与中国比较跨期精选全文结果.md",
        "178_CSIS_RAI科技创新项目轻量总目录.csv", "179_CSIS_RAI科技创新项目轻量总目录结果.md",
        "180_CSIS_RAI科学技术创新机制与中国比较跨期精选全文台账.csv", "181_CSIS_RAI科学技术创新机制与中国比较跨期精选全文结果.md",
        "182_欧洲议会STOA科技评估近十年轻量总目录.csv", "183_欧洲议会STOA科技评估近十年轻量总目录结果.md",
        "184_欧洲议会STOA科技创新与技术评估跨期精选全文台账.csv", "185_欧洲议会STOA科技创新与技术评估跨期精选全文结果.md",
        "186_欧委会JRC科技创新政策近十年轻量总目录.csv", "187_欧委会JRC科技创新政策近十年轻量总目录结果.md",
        "188_欧委会JRC科学技术创新政策跨期精选全文台账.csv", "189_欧委会JRC科学技术创新政策跨期精选全文结果.md",
        "190_德国EFI研究创新近十年轻量总目录.csv", "191_德国EFI研究创新近十年轻量总目录结果.md",
        "192_德国EFI研究创新跨期精选全文台账.csv", "193_德国EFI研究创新跨期精选全文结果.md",
        "194_RIETI科技创新与中国近十年轻量总目录.csv", "195_RIETI科技创新与中国近十年轻量总目录结果.md",
        "196_RIETI科学技术创新机制与中国比较跨期精选全文台账.csv", "197_RIETI科学技术创新机制与中国比较跨期精选全文结果.md",
        "198_英国皇家学会科学技术创新专题轻量总目录.csv", "199_英国皇家学会科学技术创新专题轻量总目录结果.md",
        "200_英国皇家学会科学体系与技术创新跨期精选全文台账.csv", "201_英国皇家学会科学体系与技术创新跨期精选全文结果.md",
        "202_acatech科学与技术创新正式成果轻量总目录.csv", "203_acatech科学与技术创新正式成果轻量总目录结果.md",
        "204_acatech工程科学与技术创新跨期精选全文台账.csv", "205_acatech工程科学与技术创新跨期精选全文结果.md",
        "206_NASEM科学技术创新政策近十年轻量总目录.csv", "207_NASEM科学技术创新政策近十年轻量总目录结果.md",
        "208_NASEM科学技术创新机制与中国比较跨期精选全文台账.csv", "209_NASEM科学技术创新机制与中国比较跨期精选全文结果.md",
        "210_本地资料库实时进度看板.md", "211_机构采集进度.csv",
        "212_Fraunhofer_ISI科技创新机制跨期增补全文台账.csv", "213_Fraunhofer_ISI科技创新机制跨期增补全文结果.md",
        "222_AI_for_Science与公共科研基础设施定点增补台账.csv", "223_AI_for_Science与公共科研基础设施定点增补结果.md",
        "224_科学外交开放科研合作与中国参与机制定点增补台账.csv", "225_科学外交开放科研合作与中国参与机制定点增补结果.md",
        "226_基础研究资助科研评价与创新联系定点增补台账.csv", "227_基础研究资助科研评价与创新联系定点增补结果.md",
        "228_技术前瞻公共研发优先级与中国比较定点增补台账.csv", "229_技术前瞻公共研发优先级与中国比较定点增补结果.md",
        "230_开放科学科研基础设施与技术平台定点增补台账.csv", "231_开放科学科研基础设施与技术平台定点增补结果.md",
        "232_使命导向创新重大研发计划与组织机制定点增补台账.csv", "233_使命导向创新重大研发计划与组织机制定点增补结果.md",
        "234_ITIF中国先进产业技术创新能力精选全文台账.csv", "235_ITIF中国先进产业技术创新能力精选全文结果.md",
        "236_清洁能源技术路线创新政策与中国比较定点增补台账.csv", "237_清洁能源技术路线创新政策与中国比较定点增补结果.md",
        "238_生物技术生物制造创新机制与中国比较定点增补台账.csv", "239_生物技术生物制造创新机制与中国比较定点增补结果.md",
        "240_先进材料技术创新平台与中国比较定点增补台账.csv", "241_先进材料技术创新平台与中国比较定点增补结果.md",
        "242_先进计算科研算力基础设施与中国比较定点增补台账.csv", "243_先进计算科研算力基础设施与中国比较定点增补结果.md",
        "244_先进核能聚变技术创新与中国比较定点增补台账.csv", "245_先进核能聚变技术创新与中国比较定点增补结果.md",
        "从开放创新到受控互赖_国际科技智库十年战略转向专报_2026-08-21.docx",
    ]
    missing = [name for name in required if not (root / name).exists()]
    assert not missing, f"missing={missing}"

    seeds = rows(root / "05_官方锚点种子.csv")
    catalog = rows(root / "05_报告总目录.csv")
    evidence = rows(root / "09_观点变化证据表.csv")
    assert len(seeds) == 49, len(seeds)
    assert len(evidence) == 24, len(evidence)
    assert len(list((root / "02_机构轨迹卡").glob("*.md"))) == 21
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
    assert sum(r["本地状态"] == "官方仓储概要PDF代理文本已保存" for r in nistep_assets) == 1
    assert sum(r["本地状态"] == "官方HTML版报告已保存" for r in nistep_assets) == 6
    assert sum(r["本地状态"] == "官方发布页摘要已保存" for r in nistep_assets) == 26
    assert sum(r["本地状态"] == "获取失败" for r in nistep_assets) == 0
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
    dp242 = next(r for r in nistep_assets if r["报告ID"] == "C-NISTEP-DP242-6EEE0740")
    assert dp242["本地状态"] == "官方仓储概要PDF代理文本已保存"
    assert dp242["官方PDF"] == "https://nistep.repo.nii.ac.jp/record/2000273/files/NISTEP-DP242-FullJ.pdf"
    assert dp242["提取文本字符数"] == "15308"
    assert dp242["SHA256"] == "6f23ae64b4283a1757a5eafa204d85632ec9b7de690c14c4726088f4680b6eb7"
    assert (root / "03_证据底稿" / "网页快照" / "C-NISTEP-DP242-6EEE0740.md").exists()
    assert (root / "03_证据底稿" / "网页文本" / "C-NISTEP-DP242-6EEE0740.txt").exists()
    assert (root / "03_证据底稿" / "网页转写" / "C-NISTEP-DP242-6EEE0740.md").exists()
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
    assert sum(r["全文策略"].startswith("已进入基础研究资助") for r in nsf_nsb_light) == 2
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
    rathenau_light = rows(root / "162_Rathenau英文正式报告近十年轻量总目录.csv")
    assert len(rathenau_light) == 75
    assert sum(r["报告类型"] == "Report" for r in rathenau_light) == 74
    assert sum(r["报告类型"] == "Factsheet" for r in rathenau_light) == 1
    assert sum(r["科技创新相关度"] == "核心" for r in rathenau_light) == 40
    assert sum(r["科技创新相关度"] == "支撑" for r in rathenau_light) == 17
    assert sum(r["科技创新相关度"] == "语境" for r in rathenau_light) == 18
    assert sum(r["中国关联"] == "是" for r in rathenau_light) == 5
    assert all(r["官方落地页"].startswith("https://www.rathenau.nl/") for r in rathenau_light)
    rathenau_selected = rows(root / "164_Rathenau科技创新与中国比较跨期精选全文台账.csv")
    assert {r["报告ID"] for r in rathenau_selected} == expected_rathenau_selected_ids()
    assert sum(r["原始资产类型"] == "PDF" for r in rathenau_selected) == 12
    assert sum(r["原始资产类型"] == "WEB" for r in rathenau_selected) == 1
    assert sum(r["中国关联"] == "是" for r in rathenau_selected) == 5
    assert sum(int(r["PDF页数"]) for r in rathenau_selected) == 666
    assert sum(int(r["字节数"]) for r in rathenau_selected) == 14097105
    assert sum(int(r["提取文本字符数"]) for r in rathenau_selected) == 1604122
    assert sum(int(r["China词形命中数"]) for r in rathenau_selected) == 401
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in rathenau_selected
    )
    ifp_light = rows(root / "166_IFP科技创新正式成果轻量总目录.csv")
    assert len(ifp_light) == 155
    assert sum(r["科技创新相关度"] == "核心" for r in ifp_light) == 106
    assert sum(r["科技创新相关度"] == "支撑" for r in ifp_light) == 39
    assert sum(r["科技创新相关度"] == "语境" for r in ifp_light) == 10
    assert sum(r["中国关联"].startswith("是") for r in ifp_light) == 55
    assert all(r["官方落地页"].startswith("https://ifp.org/") for r in ifp_light)
    ifp_selected = rows(root / "168_IFP科技创新机制与中国比较精选全文台账.csv")
    assert {r["报告ID"] for r in ifp_selected} == expected_ifp_selected_ids()
    assert sum(r["原始资产类型"] == "PDF" for r in ifp_selected) == 1
    assert sum(r["原始资产类型"] == "WEB" for r in ifp_selected) == 15
    assert sum(r["中国关联"] == "是" for r in ifp_selected) == 8
    assert sum(int(r["PDF页数"]) for r in ifp_selected) == 5
    assert sum(int(r["字节数"]) for r in ifp_selected) == 7859215
    assert sum(int(r["提取文本字符数"]) for r in ifp_selected) == 409705
    assert sum(int(r["China词形命中数"]) for r in ifp_selected) == 87
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in ifp_selected
    )
    itif_light = rows(root / "170_ITIF正式报告与简报近十年轻量总目录.csv")
    assert len(itif_light) == 669
    assert {year: sum(r["发布日期"].startswith(str(year)) for r in itif_light) for year in range(2016, 2027)} == {
        2016: 45, 2017: 39, 2018: 43, 2019: 60, 2020: 67, 2021: 96,
        2022: 73, 2023: 68, 2024: 67, 2025: 58, 2026: 53,
    }
    assert sum(r["科技创新相关度"] == "核心" for r in itif_light) == 329
    assert sum(r["科技创新相关度"] == "支撑" for r in itif_light) == 77
    assert sum(r["科技创新相关度"] == "语境" for r in itif_light) == 263
    assert sum(r["中国直接信号"] == "是" for r in itif_light) == 98
    assert len({r["官方落地页"] for r in itif_light}) == 669
    assert all(r["官方落地页"].startswith("https://itif.org/publications/") for r in itif_light)
    itif_selected = rows(root / "172_ITIF科技创新机制与中国比较跨期精选全文台账.csv")
    assert {r["报告ID"] for r in itif_selected} == expected_itif_selected_ids()
    assert sum(r["中国直接信号"] == "是" for r in itif_selected) == 21
    assert sum(int(r["字节数"]) for r in itif_selected) == 3486984
    assert sum(int(r["字符数"]) for r in itif_selected) == 2171157
    assert sum(int(r["China词形命中数"]) for r in itif_selected) == 3322
    assert sum(r["资产类型"] == "ITIF官方PDF全文" for r in itif_selected) == 1
    assert sum(int(r["PDF页数"]) for r in itif_selected) == 102
    assert all(not r["本地页面概要"] or Path(r["本地页面概要"]).exists() for r in itif_selected)
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in itif_selected
    )
    cross_china_innovation = rows(root / "214_跨机构中国科技创新机制定点增补台账.csv")
    assert len(cross_china_innovation) == 5
    assert len({r["机构ID"] for r in cross_china_innovation}) == 4
    assert sum(r["资产类型"] == "官方PDF" for r in cross_china_innovation) == 4
    assert sum(r["资产类型"] == "官方网页HTML" for r in cross_china_innovation) == 1
    assert sum(int(r["PDF页数"]) for r in cross_china_innovation) == 282
    assert sum(int(r["字节数"]) for r in cross_china_innovation) == 17238926
    assert sum(int(r["清洗文本字符数"]) for r in cross_china_innovation) == 755515
    assert sum(int(r["China词形命中数"]) for r in cross_china_innovation) == 1850
    assert not any(
        re.search(r"military|export control|export restriction|espionage|national security|trade war", r["报告名称"], re.I)
        for r in cross_china_innovation
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in cross_china_innovation
    )
    china_research_system = rows(root / "216_中国科研体系与企业研发投入定点增补台账.csv")
    assert len(china_research_system) == 6
    assert {r["机构ID"] for r in china_research_system} == {"cset", "eu-jrc"}
    assert sum(int(r["PDF页数"]) for r in china_research_system) == 665
    assert sum(int(r["字节数"]) for r in china_research_system) == 26400702
    assert sum(int(r["清洗文本字符数"]) for r in china_research_system) == 1794638
    assert sum(int(r["China词形命中数"]) for r in china_research_system) == 1548
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in china_research_system
    )
    china_innovation_measurement = rows(root / "218_中国科技创新测量与技术生态定点增补台账.csv")
    assert len(china_innovation_measurement) == 6
    assert {r["机构ID"] for r in china_innovation_measurement} == {"eu-jrc", "csis-rai"}
    assert sum(r["资产类型"] == "官方PDF" for r in china_innovation_measurement) == 5
    assert sum(r["资产类型"] == "官方网页HTML" for r in china_innovation_measurement) == 1
    assert sum(int(r["PDF页数"]) for r in china_innovation_measurement) == 238
    assert sum(int(r["字节数"]) for r in china_innovation_measurement) == 10701364
    assert sum(int(r["清洗文本字符数"]) for r in china_innovation_measurement) == 566209
    assert sum(int(r["China词形命中数"]) for r in china_innovation_measurement) == 172
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in china_innovation_measurement
    )
    science_mobility_transfer = rows(root / "220_科研人才知识转移与创新商业化定点增补台账.csv")
    assert len(science_mobility_transfer) == 6
    assert {r["机构ID"] for r in science_mobility_transfer} == {"eu-jrc", "jp-rieti"}
    assert sum(int(r["PDF页数"]) for r in science_mobility_transfer) == 256
    assert sum(int(r["字节数"]) for r in science_mobility_transfer) == 16647805
    assert sum(int(r["清洗文本字符数"]) for r in science_mobility_transfer) == 689584
    assert sum(int(r["China词形命中数"]) for r in science_mobility_transfer) == 71
    assert not any(
        re.search(r"military|export control|national security|supply chain", r["报告名称"], re.I)
        for r in science_mobility_transfer
    )
    assert all(
        Path(r["本地原始PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始PDF"])) == r["SHA256"]
        for r in science_mobility_transfer
    )
    ai_science_infrastructure = rows(root / "222_AI_for_Science与公共科研基础设施定点增补台账.csv")
    assert len(ai_science_infrastructure) == 5
    assert {r["机构ID"] for r in ai_science_infrastructure} == {"oecd-sti", "us-nasem", "eu-jrc"}
    assert sum(r["资产类型"] == "官方PDF" for r in ai_science_infrastructure) == 3
    assert sum(r["资产类型"] == "官方逐章网页Markdown转写" for r in ai_science_infrastructure) == 2
    assert sum(int(r["页数或章节数"]) for r in ai_science_infrastructure) == 124
    assert sum(int(r["字节数"]) for r in ai_science_infrastructure) == 13103038
    assert sum(int(r["清洗文本字符数"]) for r in ai_science_infrastructure) == 504007
    assert sum(int(r["China词形命中数"]) for r in ai_science_infrastructure) == 6
    assert not any(
        re.search(r"military|export control|supply chain", r["报告名称"], re.I)
        for r in ai_science_infrastructure
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in ai_science_infrastructure
    )
    science_diplomacy = rows(root / "224_科学外交开放科研合作与中国参与机制定点增补台账.csv")
    assert len(science_diplomacy) == 5
    assert {r["机构ID"] for r in science_diplomacy} == {"us-ostp", "us-nasem", "uk-royal-society"}
    assert sum(r["资产类型"] == "官方PDF" for r in science_diplomacy) == 2
    assert sum(r["资产类型"] == "官方逐章网页Markdown转写" for r in science_diplomacy) == 2
    assert sum(r["资产类型"] == "官方PDF的Markdown转写" for r in science_diplomacy) == 1
    assert sum(int(r["页数或章节数"]) for r in science_diplomacy) == 57
    assert sum(int(r["字节数"]) for r in science_diplomacy) == 1097490
    assert sum(int(r["清洗文本字符数"]) for r in science_diplomacy) == 277367
    assert sum(int(r["China词形命中数"]) for r in science_diplomacy) == 33
    assert not any(re.search(r"military|export control|supply chain", r["报告名称"], re.I) for r in science_diplomacy)
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in science_diplomacy
    )
    research_funding_evaluation = rows(root / "226_基础研究资助科研评价与创新联系定点增补台账.csv")
    assert len(research_funding_evaluation) == 6
    assert {r["机构ID"] for r in research_funding_evaluation} == {
        "eu-jrc", "nsf-nsb-sei", "de-efi", "jp-rieti", "us-nasem"
    }
    assert sum(r["资产类型"] == "官方PDF" for r in research_funding_evaluation) == 5
    assert sum(r["资产类型"] == "官方逐章网页Markdown转写" for r in research_funding_evaluation) == 1
    assert sum(int(r["页数或章节数"]) for r in research_funding_evaluation) == 1255
    assert sum(int(r["字节数"]) for r in research_funding_evaluation) == 30970310
    assert sum(int(r["清洗文本字符数"]) for r in research_funding_evaluation) == 3057703
    assert sum(int(r["China词形命中数"]) for r in research_funding_evaluation) == 894
    assert not any(
        re.search(r"military|export control|supply chain|national security", r["报告名称"], re.I)
        for r in research_funding_evaluation
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in research_funding_evaluation
    )
    technology_foresight_priorities = rows(root / "228_技术前瞻公共研发优先级与中国比较定点增补台账.csv")
    assert len(technology_foresight_priorities) == 6
    assert {r["机构ID"] for r in technology_foresight_priorities} == {"eu-stoa", "eu-jrc"}
    assert all(r["资产类型"] == "官方PDF" for r in technology_foresight_priorities)
    assert sum(int(r["页数"]) for r in technology_foresight_priorities) == 368
    assert sum(int(r["字节数"]) for r in technology_foresight_priorities) == 19230368
    assert sum(int(r["清洗文本字符数"]) for r in technology_foresight_priorities) == 832221
    assert sum(int(r["China词形命中数"]) for r in technology_foresight_priorities) == 87
    assert sum(int(r["China词形命中数"]) > 0 for r in technology_foresight_priorities) == 4
    assert not any(
        re.search(r"military|export control|supply chain|national security", r["报告名称"], re.I)
        for r in technology_foresight_priorities
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in technology_foresight_priorities
    )
    open_science_infrastructure = rows(root / "230_开放科学科研基础设施与技术平台定点增补台账.csv")
    assert len(open_science_infrastructure) == 6
    assert {r["机构ID"] for r in open_science_infrastructure} == {"eu-jrc", "us-nasem", "rathenau", "fas"}
    assert sum(r["资产类型"] == "官方PDF" for r in open_science_infrastructure) == 3
    assert sum(r["资产类型"] == "官方逐章网页Markdown转写" for r in open_science_infrastructure) == 2
    assert sum(r["资产类型"] == "官方WordPress网页正文" for r in open_science_infrastructure) == 1
    assert sum(int(r["页数或章节数"]) for r in open_science_infrastructure) == 135
    assert sum(int(r["字节数"]) for r in open_science_infrastructure) == 5147271
    assert sum(int(r["清洗文本字符数"]) for r in open_science_infrastructure) == 615159
    assert sum(int(r["China词形命中数"]) for r in open_science_infrastructure) == 1
    assert not any(
        re.search(r"military|export control|supply chain|national security", r["报告名称"], re.I)
        for r in open_science_infrastructure
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in open_science_infrastructure
    )
    mission_oriented_rd = rows(root / "232_使命导向创新重大研发计划与组织机制定点增补台账.csv")
    assert len(mission_oriented_rd) == 6
    assert {r["机构ID"] for r in mission_oriented_rd} == {"itif", "fas", "fraunhofer-isi", "ifp", "oecd-sti", "eu-jrc"}
    assert sum(r["资产类型"] == "官方PDF" for r in mission_oriented_rd) == 3
    assert sum(r["资产类型"] == "官方Markdown网页正文" for r in mission_oriented_rd) == 1
    assert sum(r["资产类型"] == "官方WordPress网页正文" for r in mission_oriented_rd) == 2
    assert sum(int(r["页数或网页数"]) for r in mission_oriented_rd) == 94
    assert sum(int(r["字节数"]) for r in mission_oriented_rd) == 3744281
    assert sum(int(r["清洗文本字符数"]) for r in mission_oriented_rd) == 319662
    assert sum(int(r["China词形命中数"]) for r in mission_oriented_rd) == 8
    assert sum(int(r["China词形命中数"]) > 0 for r in mission_oriented_rd) == 1
    assert not any(
        re.search(r"military|export control|supply chain|national security", r["报告名称"], re.I)
        for r in mission_oriented_rd
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in mission_oriented_rd
    )
    itif_china_industries = rows(root / "234_ITIF中国先进产业技术创新能力精选全文台账.csv")
    assert len(itif_china_industries) == 6
    assert {r["技术领域"] for r in itif_china_industries} == {"机器人", "电动车与电池", "生物技术", "半导体", "量子技术", "先进产业综合"}
    assert sum(int(r["网页数"]) for r in itif_china_industries) == 6
    assert sum(int(r["字节数"]) for r in itif_china_industries) == 242338
    assert sum(int(r["清洗文本字符数"]) for r in itif_china_industries) == 240377
    assert sum(int(r["China词形命中数"]) for r in itif_china_industries) == 1014
    assert all(
        Path(r["既有官方PDF"]).exists() and Path(r["新增网页正文"]).exists()
        and Path(r["本地文本"]).exists() and Path(r["本地切片"]).exists()
        and sha(Path(r["既有官方PDF"])) == r["既有PDF_SHA256"]
        and sha(Path(r["新增网页正文"])) == r["SHA256"]
        for r in itif_china_industries
    )
    itif_china_light = rows(root / "79_ITIF中国先进产业创新系列轻量目录.csv")
    assert len(itif_china_light) == 10
    assert all("既有官方PDF已复核" in r["全文策略"] for r in itif_china_light)
    clean_energy = rows(root / "236_清洁能源技术路线创新政策与中国比较定点增补台账.csv")
    assert len(clean_energy) == 6
    assert {r["机构ID"] for r in clean_energy} == {"eu-jrc", "oecd-sti", "itif", "fas"}
    assert sum(r["资产类型"] == "官方PDF" for r in clean_energy) == 4
    assert sum(r["资产类型"] == "官方Markdown网页正文" for r in clean_energy) == 1
    assert sum(r["资产类型"] == "官方WordPress网页正文" for r in clean_energy) == 1
    assert sum(int(r["页数或网页数"]) for r in clean_energy) == 307
    assert sum(int(r["字节数"]) for r in clean_energy) == 29705679
    assert sum(int(r["清洗文本字符数"]) for r in clean_energy) == 746103
    assert sum(int(r["China词形命中数"]) for r in clean_energy) == 192
    assert sum(int(r["China词形命中数"]) > 0 for r in clean_energy) == 5
    assert not any(re.search(r"military|export control|national security|supply chain resilience", r["报告名称"], re.I) for r in clean_energy)
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in clean_energy
    )
    biotech = rows(root / "238_生物技术生物制造创新机制与中国比较定点增补台账.csv")
    assert len(biotech) == 6
    assert {r["机构ID"] for r in biotech} == {"de-acatech", "oecd-sti", "fas", "eu-jrc"}
    assert sum(r["资产类型"] == "官方PDF" for r in biotech) == 4
    assert sum(r["资产类型"] == "官方WordPress网页正文" for r in biotech) == 2
    assert sum(int(r["页数或网页数"]) for r in biotech) == 266
    assert sum(int(r["字节数"]) for r in biotech) == 8243607
    assert sum(int(r["清洗文本字符数"]) for r in biotech) == 792685
    assert sum(int(r["China词形命中数"]) for r in biotech) == 56
    assert sum(int(r["China词形命中数"]) > 0 for r in biotech) == 5
    assert not any(re.search(r"biosecurity|military|defen[cs]e|national security|drug pricing", r["报告名称"], re.I) for r in biotech)
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in biotech
    )
    advanced_materials = rows(root / "240_先进材料技术创新平台与中国比较定点增补台账.csv")
    assert len(advanced_materials) == 6
    assert {r["机构ID"] for r in advanced_materials} == {"us-ostp", "eu-jrc", "oecd-sti", "fas"}
    assert sum(r["资产类型"] == "官方PDF" for r in advanced_materials) == 5
    assert sum(r["资产类型"] == "官方WordPress网页正文" for r in advanced_materials) == 1
    assert sum(int(r["页数或网页数"]) for r in advanced_materials) == 291
    assert sum(int(r["字节数"]) for r in advanced_materials) == 12405617
    assert sum(int(r["清洗文本字符数"]) for r in advanced_materials) == 843665
    assert sum(int(r["China词形命中数"]) for r in advanced_materials) == 3
    assert sum(int(r["China词形命中数"]) > 0 for r in advanced_materials) == 1
    assert not any(
        re.search(r"critical minerals|supply chain resilience|materials safety|military|defen[cs]e", r["报告名称"], re.I)
        for r in advanced_materials
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in advanced_materials
    )
    advanced_computing = rows(root / "242_先进计算科研算力基础设施与中国比较定点增补台账.csv")
    assert len(advanced_computing) == 6
    assert {r["机构ID"] for r in advanced_computing} == {"itif", "us-ostp", "fas"}
    assert sum(r["资产类型"] == "官方PDF" for r in advanced_computing) == 3
    assert sum(r["资产类型"] == "ITIF官方Markdown全文" for r in advanced_computing) == 2
    assert sum(r["资产类型"] == "官方WordPress网页正文" for r in advanced_computing) == 1
    assert sum(int(r["页数或网页数"]) for r in advanced_computing) == 58
    assert sum(int(r["字节数"]) for r in advanced_computing) == 1474490
    assert sum(int(r["清洗文本字符数"]) for r in advanced_computing) == 173590
    assert sum(int(r["China词形命中数"]) for r in advanced_computing) == 3
    assert sum(int(r["China词形命中数"]) > 0 for r in advanced_computing) == 2
    assert not any(
        re.search(r"export control|military|defen[cs]e|national security|cloud governance", r["报告名称"], re.I)
        for r in advanced_computing
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in advanced_computing
    )
    advanced_nuclear = rows(root / "244_先进核能聚变技术创新与中国比较定点增补台账.csv")
    assert len(advanced_nuclear) == 6
    assert {r["机构ID"] for r in advanced_nuclear} == {"eu-jrc", "fas", "itif", "eu-stoa"}
    assert sum(r["资产类型"] == "官方PDF" for r in advanced_nuclear) == 4
    assert sum(r["资产类型"] == "ITIF官方Markdown全文" for r in advanced_nuclear) == 1
    assert sum(r["资产类型"] == "官方WordPress网页正文" for r in advanced_nuclear) == 1
    assert sum(int(r["页数或网页数"]) for r in advanced_nuclear) == 273
    assert sum(int(r["字节数"]) for r in advanced_nuclear) == 7079969
    assert sum(int(r["清洗文本字符数"]) for r in advanced_nuclear) == 697186
    assert sum(int(r["China词形命中数"]) for r in advanced_nuclear) == 73
    assert sum(int(r["China词形命中数"]) > 0 for r in advanced_nuclear) == 6
    assert not any(
        re.search(r"weapon|deterrent|arms|missile|military|naval|security|safeguard|decommission|radiation protection|waste", r["报告名称"], re.I)
        for r in advanced_nuclear
    )
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in advanced_nuclear
    )
    fas_light = rows(root / "174_FAS报告与政策备忘录近十年轻量总目录.csv")
    assert len(fas_light) == 625
    assert {year: sum(r["发布日期"].startswith(str(year)) for r in fas_light) for year in range(2016, 2027)} == {
        2016: 20, 2017: 4, 2018: 0, 2019: 3, 2020: 86, 2021: 103,
        2022: 46, 2023: 67, 2024: 154, 2025: 96, 2026: 46,
    }
    assert sum(r["科技创新相关度"] == "核心" for r in fas_light) == 176
    assert sum(r["科技创新相关度"] == "支撑" for r in fas_light) == 127
    assert sum(r["科技创新相关度"] == "语境" for r in fas_light) == 322
    assert sum(r["中国直接信号"] == "是" for r in fas_light) == 16
    assert sum(r["官方类型"] == "Report" for r in fas_light) == 109
    assert sum(r["官方类型"] == "Policy Memo" for r in fas_light) == 502
    assert sum(r["官方类型"] == "Report + Policy Memo" for r in fas_light) == 14
    assert len({r["WordPress记录ID"] for r in fas_light}) == 625
    assert all(r["官方落地页"].startswith("https://fas.org/publication/") for r in fas_light)
    assert sum(r["全文策略"].startswith("已进入生物技术与生物制造创新") for r in fas_light) == 2
    assert sum(r["全文策略"].startswith("已进入先进材料技术创新平台") for r in fas_light) == 1
    assert sum(r["全文策略"].startswith("已进入先进计算科研算力基础设施") for r in fas_light) == 1
    assert sum(r["全文策略"].startswith("已进入先进核能聚变技术创新") for r in fas_light) == 1
    assert sum(r["全文策略"].startswith("总目录保留") for r in fas_light) == 591
    fas_selected = rows(root / "176_FAS科技创新机制与中国比较跨期精选全文台账.csv")
    assert {r["报告ID"] for r in fas_selected} == expected_fas_selected_ids()
    assert sum(r["中国直接信号"] == "是" for r in fas_selected) == 5
    assert sum(int(r["字节数"]) for r in fas_selected) == 515684
    assert sum(int(r["字符数"]) for r in fas_selected) == 514001
    assert sum(int(r["清洗文本字符数"]) for r in fas_selected) == 382801
    assert sum(int(r["China词形命中数"]) for r in fas_selected) == 133
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in fas_selected
    )
    csis_rai_light = rows(root / "178_CSIS_RAI科技创新项目轻量总目录.csv")
    assert len(csis_rai_light) == 176
    assert {year: sum(r["发布日期"].startswith(str(year)) for r in csis_rai_light) for year in range(2021, 2027)} == {
        2021: 16, 2022: 35, 2023: 32, 2024: 36, 2025: 35, 2026: 22,
    }
    assert sum(r["官方内容类型"] == "Report" for r in csis_rai_light) == 43
    assert sum(r["官方内容类型"] == "Article" for r in csis_rai_light) == 133
    assert sum(r["科技创新相关度"] == "核心" for r in csis_rai_light) == 156
    assert sum(r["科技创新相关度"] == "支撑" for r in csis_rai_light) == 6
    assert sum(r["科技创新相关度"] == "语境" for r in csis_rai_light) == 14
    assert sum(r["中国直接信号"] == "是" for r in csis_rai_light) == 35
    assert len({r["官方落地页"].rstrip("/") for r in csis_rai_light}) == 176
    assert all(r["官方落地页"].startswith(("https://www.csis.org/", "https://features.csis.org/")) for r in csis_rai_light)
    csis_rai_selected = rows(root / "180_CSIS_RAI科学技术创新机制与中国比较跨期精选全文台账.csv")
    assert {r["报告ID"] for r in csis_rai_selected} == expected_csis_rai_selected_ids()
    assert sum(r["资产类型"] == "官方PDF" for r in csis_rai_selected) == 17
    assert sum(r["资产类型"] == "官方网页正文" for r in csis_rai_selected) == 10
    assert sum(r["中国直接信号"] == "是" for r in csis_rai_selected) == 16
    assert sum(int(r["页数"]) for r in csis_rai_selected) == 280
    assert sum(int(r["字节数"]) for r in csis_rai_selected) == 15550563
    assert sum(int(r["清洗文本字符数"]) for r in csis_rai_selected) == 812948
    assert sum(int(r["China词形命中数"]) for r in csis_rai_selected) == 854
    assert all(
        Path(r["本地原始资产"]).exists() and Path(r["本地页面HTML"]).exists()
        and Path(r["本地文本"]).exists() and Path(r["本地切片"]).exists()
        and sha(Path(r["本地原始资产"])) == r["SHA256"]
        for r in csis_rai_selected
    )
    eu_stoa_light = rows(root / "182_欧洲议会STOA科技评估近十年轻量总目录.csv")
    assert len(eu_stoa_light) == 243
    assert sum(r["科技创新相关度"] == "核心" for r in eu_stoa_light) == 182
    assert sum(r["科技创新相关度"] == "支撑" for r in eu_stoa_light) == 39
    assert sum(r["科技创新相关度"] == "语境" for r in eu_stoa_light) == 22
    assert sum(r["中国直接信号"].startswith("是") for r in eu_stoa_light) == 2
    assert {r["发布日期"][:4] for r in eu_stoa_light} == {str(year) for year in range(2016, 2027)}
    assert sum(r["全文策略"].startswith("已进入先进核能聚变技术创新") for r in eu_stoa_light) == 1
    assert sum(r["全文策略"].startswith("按科技创新机制") for r in eu_stoa_light) == 220
    eu_stoa_selected = rows(root / "184_欧洲议会STOA科技创新与技术评估跨期精选全文台账.csv")
    assert {r["报告ID"] for r in eu_stoa_selected} == expected_eu_stoa_selected_ids()
    assert sum(int(r["页数"]) for r in eu_stoa_selected) == 1609
    assert sum(int(r["字节数"]) for r in eu_stoa_selected) == 45648866
    assert sum(int(r["清洗文本字符数"]) for r in eu_stoa_selected) == 3994298
    assert sum(int(r["China词形命中数"]) for r in eu_stoa_selected) == 401
    assert sum(int(r["China词形命中数"]) > 0 for r in eu_stoa_selected) == 14
    assert all(
        Path(r["本地原始PDF"]).exists() and Path(r["本地页面HTML"]).exists()
        and Path(r["本地文本"]).exists() and Path(r["本地切片"]).exists()
        and sha(Path(r["本地原始PDF"])) == r["SHA256"]
        for r in eu_stoa_selected
    )
    eu_jrc_light = rows(root / "186_欧委会JRC科技创新政策近十年轻量总目录.csv")
    assert len(eu_jrc_light) == 3743
    assert sum(r["科技创新相关度"] == "核心" for r in eu_jrc_light) == 2381
    assert sum(r["科技创新相关度"] == "支撑" for r in eu_jrc_light) == 1335
    assert sum(r["科技创新相关度"] == "语境" for r in eu_jrc_light) == 27
    assert sum(r["中国直接信号"].startswith("是") for r in eu_jrc_light) == 100
    assert all(r["官方PDF入口"].startswith("https://publications.jrc.ec.europa.eu/repository/bitstream/") for r in eu_jrc_light)
    assert not any("%2520" in r["官方PDF入口"] for r in eu_jrc_light)
    assert {r["发布日期"][:4] for r in eu_jrc_light} == {str(year) for year in range(2016, 2027)}
    assert sum(r["全文策略"].startswith("已进入生物技术与生物制造创新") for r in eu_jrc_light) == 1
    assert sum(r["全文策略"].startswith("已进入先进材料技术创新平台") for r in eu_jrc_light) == 2
    assert sum(r["全文策略"].startswith("已进入先进核能聚变技术创新") for r in eu_jrc_light) == 3
    assert sum(r["全文策略"].startswith("总目录保留") for r in eu_jrc_light) == 3676
    eu_jrc_selected = rows(root / "188_欧委会JRC科学技术创新政策跨期精选全文台账.csv")
    assert {r["报告ID"] for r in eu_jrc_selected} == expected_eu_jrc_selected_ids()
    assert sum(int(r["页数"]) for r in eu_jrc_selected) == 2133
    assert sum(int(r["字节数"]) for r in eu_jrc_selected) == 104781564
    assert sum(int(r["清洗文本字符数"]) for r in eu_jrc_selected) == 5404371
    assert sum(int(r["China词形命中数"]) for r in eu_jrc_selected) == 3878
    assert sum(int(r["China词形命中数"]) > 0 for r in eu_jrc_selected) == 28
    assert sum(r["中国直接信号"] == "是" for r in eu_jrc_selected) == 23
    assert all(
        Path(r["本地原始PDF"]).exists() and Path(r["本地页面HTML"]).exists()
        and Path(r["本地文本"]).exists() and Path(r["本地切片"]).exists()
        and sha(Path(r["本地原始PDF"])) == r["SHA256"]
        for r in eu_jrc_selected
    )
    efi_light = rows(root / "190_德国EFI研究创新近十年轻量总目录.csv")
    assert len(efi_light) == 152
    assert sum(r["官方文类"] == "EFI年度总报告" for r in efi_light) == 11
    assert sum(r["官方文类"] == "EFI年度报告分章" for r in efi_light) == 141
    assert sum(r["科技创新相关度"] == "核心" for r in efi_light) == 108
    assert sum(r["科技创新相关度"] == "支撑" for r in efi_light) == 42
    assert sum(r["科技创新相关度"] == "语境" for r in efi_light) == 2
    assert sum(r["中国直接信号"] == "是" for r in efi_light) == 3
    assert {r["发布日期"][:4] for r in efi_light} == {str(year) for year in range(2016, 2027)}
    efi_selected = rows(root / "192_德国EFI研究创新跨期精选全文台账.csv")
    assert {r["报告ID"] for r in efi_selected} == expected_efi_selected_ids()
    assert sum(int(r["页数"]) for r in efi_selected) == 174
    assert sum(int(r["字节数"]) for r in efi_selected) == 10673353
    assert sum(int(r["清洗文本字符数"]) for r in efi_selected) == 544850
    assert sum(int(r["China词形命中数"]) for r in efi_selected) == 365
    assert sum(int(r["China词形命中数"]) > 0 for r in efi_selected) == 7
    assert all(
        Path(r["本地原始PDF"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists() and sha(Path(r["本地原始PDF"])) == r["SHA256"]
        for r in efi_selected
    )
    rieti_light = rows(root / "194_RIETI科技创新与中国近十年轻量总目录.csv")
    assert len(rieti_light) == 224
    assert sum(r["科技创新相关度"] == "核心" for r in rieti_light) == 217
    assert sum(r["科技创新相关度"] == "支撑" for r in rieti_light) == 3
    assert sum(r["科技创新相关度"] == "语境" for r in rieti_light) == 4
    assert sum(r["中国直接信号"] == "是" for r in rieti_light) == 13
    assert sum(r["语言"] == "English" for r in rieti_light) == 148
    assert sum(r["语言"] == "Japanese" for r in rieti_light) == 76
    assert {r["发布日期"][:4] for r in rieti_light} == {str(year) for year in range(2016, 2027)}
    assert not any(
        re.search(r"supply chain resilience|wolf warrior diplomacy|fiscal system reform in china", r["报告名称"], re.I)
        for r in rieti_light
    )
    rieti_selected = rows(root / "196_RIETI科学技术创新机制与中国比较跨期精选全文台账.csv")
    assert {r["报告ID"] for r in rieti_selected} == expected_rieti_selected_ids()
    assert sum(int(r["页数"]) for r in rieti_selected) == 606
    assert sum(int(r["字节数"]) for r in rieti_selected) == 24232401
    assert sum(int(r["清洗文本字符数"]) for r in rieti_selected) == 1155837
    assert sum(int(r["China词形命中数"]) for r in rieti_selected) == 407
    assert sum(int(r["China词形命中数"]) > 0 for r in rieti_selected) == 12
    assert not any(re.search(r"security exception|export restriction|export control|decoupling|trade war", r["报告名称"], re.I) for r in rieti_selected)
    assert all(
        Path(r["本地原始PDF"]).exists() and Path(r["本地页面HTML"]).exists()
        and Path(r["本地文本"]).exists() and Path(r["本地切片"]).exists()
        and sha(Path(r["本地原始PDF"])) == r["SHA256"]
        for r in rieti_selected
    )
    royal_society_light = rows(root / "198_英国皇家学会科学技术创新专题轻量总目录.csv")
    assert len(royal_society_light) == 42
    assert sum(r["科技创新相关度"] == "核心" for r in royal_society_light) == 40
    assert sum(r["科技创新相关度"] == "支撑" for r in royal_society_light) == 2
    assert sum(r["科技创新相关度"] == "语境" for r in royal_society_light) == 0
    assert sum(r["中国直接信号"] == "是" for r in royal_society_light) == 2
    assert not any(re.search(r"national security|export control|state threats|cybersecurity", r["报告名称"], re.I) for r in royal_society_light)
    royal_society_selected = rows(root / "200_英国皇家学会科学体系与技术创新跨期精选全文台账.csv")
    assert {r["报告ID"] for r in royal_society_selected} == expected_royal_society_selected_ids()
    assert sum(int(r["全文代理字符数"]) for r in royal_society_selected) == 1521339
    assert sum(int(r["清洗文本字符数"]) for r in royal_society_selected) == 1520724
    assert sum(int(r["China词形命中数"]) > 0 for r in royal_society_selected) == 8
    assert not any(re.search(r"national security|export control|state threats|cybersecurity", r["报告名称"], re.I) for r in royal_society_selected)
    assert all(
        Path(r["本地全文代理"]).exists() and Path(r["本地文本"]).exists()
        and Path(r["本地切片"]).exists()
        and hashlib.sha256(Path(r["本地全文代理"]).read_text(encoding="utf-8").encode("utf-8")).hexdigest() == r["SHA256"]
        for r in royal_society_selected
    )
    acatech_light = rows(root / "202_acatech科学与技术创新正式成果轻量总目录.csv")
    assert len(acatech_light) == 416
    assert sum(r["科技创新相关度"] == "核心" for r in acatech_light) == 166
    assert sum(r["科技创新相关度"] == "支撑" for r in acatech_light) == 221
    assert sum(r["科技创新相关度"] == "语境" for r in acatech_light) == 29
    assert sum(r["中国直接信号"] == "是" for r in acatech_light) == 1
    assert sum(r["全文策略"].startswith("已进入生物技术与生物制造创新") for r in acatech_light) == 1
    assert sum(r["全文策略"].startswith("轻量目录保留") for r in acatech_light) == 403
    acatech_selected = rows(root / "204_acatech工程科学与技术创新跨期精选全文台账.csv")
    assert {r["报告ID"] for r in acatech_selected} == expected_acatech_selected_ids()
    assert sum(int(r["页数"]) for r in acatech_selected) == 799
    assert sum(int(r["字节数"]) for r in acatech_selected) == 34202051
    assert sum(int(r["清洗文本字符数"]) for r in acatech_selected) == 2627140
    assert sum(int(r["China词形命中数"]) > 0 for r in acatech_selected) == 7
    assert not any(re.search(r"sicherheit|militär|verteidigung|souveränität|resilienz", r["报告名称"], re.I) for r in acatech_selected)
    assert all(
        Path(r["本地原始PDF"]).exists() and Path(r["本地文本"]).exists() and Path(r["本地切片"]).exists()
        and sha(Path(r["本地原始PDF"])) == r["SHA256"]
        for r in acatech_selected
    )
    nasem_light = rows(root / "206_NASEM科学技术创新政策近十年轻量总目录.csv")
    assert len(nasem_light) == 253
    assert sum(r["科技创新相关度"] == "核心" for r in nasem_light) == 165
    assert sum(r["科技创新相关度"] == "支撑" for r in nasem_light) == 67
    assert sum(r["科技创新相关度"] == "语境" for r in nasem_light) == 21
    assert sum(r["中国直接信号"].startswith("是") for r in nasem_light) == 19
    nasem_selected = rows(root / "208_NASEM科学技术创新机制与中国比较跨期精选全文台账.csv")
    assert {r["报告ID"] for r in nasem_selected} == expected_nasem_selected_ids()
    assert sum(int(r["章节数"]) for r in nasem_selected) == 161
    assert sum(int(r["网页归档字节数"]) for r in nasem_selected) == 7243099
    assert sum(int(r["清洗文本字符数"]) for r in nasem_selected) == 6132897
    progress_text = (root / "210_本地资料库实时进度看板.md").read_text(encoding="utf-8")
    for marker in ("轻量总目录：10399条", "本地原始资产或官方网页转换资产：2166条", "仅目录与官方入口：8233条", "真实待补队列：0", "明确获取失败：0条", "仅摘要或概要资产：27条", "中国关联目录材料：748条", "已有本地原文579条、可检索文本574条"):
        assert marker in progress_text
    institution_progress = rows(root / "211_机构采集进度.csv")
    assert len(institution_progress) == 46
    nasem_progress = next(r for r in institution_progress if r["institution"] == "National Academies of Sciences, Engineering, and Medicine")
    assert (nasem_progress["catalog"], nasem_progress["local_assets"], nasem_progress["light_only"]) == ("253", "25", "228")
    jrc_progress = next(r for r in institution_progress if r["institution"] == "European Commission Joint Research Centre (JRC)")
    assert (jrc_progress["catalog"], jrc_progress["local_assets"], jrc_progress["light_only"]) == ("3743", "67", "3676")
    stoa_progress = next(r for r in institution_progress if r["institution"] == "European Parliament Panel for the Future of Science and Technology (STOA)")
    assert (stoa_progress["catalog"], stoa_progress["local_assets"], stoa_progress["light_only"]) == ("243", "23", "220")
    fas_progress = next(r for r in institution_progress if r["institution"] == "Federation of American Scientists")
    assert (fas_progress["catalog"], fas_progress["local_assets"], fas_progress["light_only"]) == ("625", "34", "591")
    itif_progress = next(r for r in institution_progress if r["institution"] == "Information Technology and Innovation Foundation")
    assert (itif_progress["catalog"], itif_progress["local_assets"], itif_progress["light_only"]) == ("670", "62", "608")
    oecd_progress = next(r for r in institution_progress if r["institution"] == "OECD")
    assert (oecd_progress["catalog"], oecd_progress["local_assets"], oecd_progress["light_only"]) == ("453", "56", "397")
    ostp_progress = next(r for r in institution_progress if r["institution"] == "White House Office of Science and Technology Policy")
    assert (ostp_progress["catalog"], ostp_progress["local_assets"], ostp_progress["light_only"]) == ("67", "14", "53")
    acatech_progress = next(r for r in institution_progress if r["institution"] == "acatech")
    assert (acatech_progress["catalog"], acatech_progress["local_assets"], acatech_progress["light_only"]) == ("416", "13", "403")
    ifp_progress = next(r for r in institution_progress if r["institution"] == "Institute for Progress")
    assert (ifp_progress["catalog"], ifp_progress["local_assets"], ifp_progress["light_only"]) == ("155", "17", "138")
    fraunhofer_progress = next(r for r in institution_progress if r["institution"] == "Fraunhofer Institute for Systems and Innovation Research ISI")
    assert (fraunhofer_progress["catalog"], fraunhofer_progress["local_assets"], fraunhofer_progress["light_only"]) == ("50", "34", "16")
    rathenau_progress = next(r for r in institution_progress if r["institution"] == "Rathenau Instituut")
    assert (rathenau_progress["catalog"], rathenau_progress["local_assets"], rathenau_progress["light_only"]) == ("75", "14", "61")
    rieti_progress = next(r for r in institution_progress if r["institution"] == "Research Institute of Economy, Trade and Industry (RIETI)")
    assert (rieti_progress["catalog"], rieti_progress["local_assets"], rieti_progress["light_only"]) == ("224", "23", "201")
    assert sum(int(r["China词形命中数"]) for r in nasem_selected) == 1491
    assert sum(int(r["China词形命中数"]) > 0 for r in nasem_selected) == 17
    assert sum("Protecting U.S. Technological Advantage" == r["报告名称"] for r in nasem_selected) == 1
    assert not any(re.search(r"\bmilitary\b|\bdefen[cs]e\b|\barmy\b|\bnavy\b|\bair force\b", r["报告名称"], re.I) for r in nasem_selected)
    assert all(
        Path(r["本地网页转写"]).exists() and Path(r["本地文本"]).exists() and Path(r["本地切片"]).exists()
        and sha(Path(r["本地网页转写"])) == r["SHA256"]
        and "collection-complete: chapter-probe-v2" in Path(r["本地网页转写"]).read_text(encoding="utf-8")
        for r in nasem_selected
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
    assert len(gap_matrix) == 1290
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
    fraunhofer_selected_fulltexts = rows(root / "212_Fraunhofer_ISI科技创新机制跨期增补全文台账.csv")
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
    cset_research_system_ids = {"C-CSET-15208", "C-CSET-15209"}
    assert {r["报告ID"] for r in cset_light if r["全文策略"].startswith("已进入中国科研体系")} == cset_research_system_ids
    assert all(r["全文策略"].startswith("不自动下载") for r in cset_light if r["报告ID"] not in cset_research_system_ids)
    assert all(r["全文策略"].startswith("既有官方PDF已复核") for r in itif_series_light)
    assert all(r["全文策略"].startswith("不自动下载") for r in itif_node_light)
    science_diplomacy_ostp_ids = {
        "C-US-OSTP-2016-IWGODSP-PRINCIPLES-0",
        "C-US-OSTP-2024-2024-BIENNIAL-REPORT-TO-CONGRESS-ON-INTERNATIONAL-SCIENCE-TECHNOLOGY-COOPERATION",
    }
    advanced_materials_ostp_id = "C-US-OSTP-2016-2016-NNI-STRATEGIC-PLAN"
    advanced_computing_ostp_ids = {
        "C-US-OSTP-2019-NATIONAL-STRATEGIC-COMPUTING-INITIATIVE-UPDATE-2019",
        "C-US-OSTP-2020-RECOMMENDATIONS-CLOUD-AI-RD-NOV2020",
        "C-US-OSTP-2020-FUTURE-ADVANCED-COMPUTING-ECOSYSTEM-STRATEGIC-PLAN-NOV-2020",
    }
    assert {r["报告ID"] for r in ostp_light if r["全文策略"].startswith("已进入科学外交")} == science_diplomacy_ostp_ids
    assert {r["报告ID"] for r in ostp_light if r["全文策略"].startswith("已进入先进材料技术创新平台")} == {advanced_materials_ostp_id}
    assert {r["报告ID"] for r in ostp_light if r["全文策略"].startswith("已进入先进计算科研算力基础设施")} == advanced_computing_ostp_ids
    assert all(r["全文策略"].startswith("不自动下载") for r in ostp_light if r["报告ID"] not in science_diplomacy_ostp_ids | {advanced_materials_ostp_id} | advanced_computing_ostp_ids)
    assert sum(r["全文策略"].startswith("已进入跨机构中国科技创新机制定点全文") for r in belfer_merics_light) == 1
    assert sum(r["全文策略"].startswith("不自动下载") for r in belfer_merics_light) == 2
    fraunhofer_selected = {
        "C-FRAUNHOFER-ISI-DP-51",
        "C-FRAUNHOFER-ISI-DP-53",
        "C-FRAUNHOFER-ISI-DP-65",
        "C-FRAUNHOFER-ISI-DP-83",
    }
    assert {r["统一目录报告ID"] for r in fraunhofer_light if r["全文策略"] == "已按科技创新机制跨期增量定点下载"} == fraunhofer_selected
    assert sum(r["全文策略"].startswith("已进入使命导向创新") for r in fraunhofer_light) == 1
    assert all(r["全文策略"].startswith("不自动下载") for r in fraunhofer_light if r["统一目录报告ID"] not in fraunhofer_selected | {"S-FISI-2022-01"})
    assert {r["报告ID"] for r in fraunhofer_selected_fulltexts} == fraunhofer_selected
    assert sum(int(r["页数"]) for r in fraunhofer_selected_fulltexts) == 130
    assert sum(int(r["字节数"]) for r in fraunhofer_selected_fulltexts) == 2482710
    assert sum(int(r["清洗文本字符数"]) for r in fraunhofer_selected_fulltexts) == 306567
    assert sum(r["全文策略"] == "已按真实科技创新机制缺口定点下载" for r in oecd_light) == 2
    assert sum(r["全文策略"].startswith("已进入跨机构中国科技创新机制定点全文") for r in oecd_light) == 1
    assert sum(r["全文策略"].startswith("已进入AI for Science与公共科研基础设施定点全文") for r in oecd_light) == 2
    assert sum(r["全文策略"].startswith("已进入使命导向创新") for r in oecd_light) == 1
    assert sum(r["全文策略"].startswith("已进入清洁能源技术路线") for r in oecd_light) == 1
    assert sum(r["全文策略"].startswith("已进入生物技术与生物制造创新") for r in oecd_light) == 2
    assert sum(r["全文策略"].startswith("已进入先进材料技术创新平台") for r in oecd_light) == 2
    assert sum(r["全文策略"].startswith("不自动下载") for r in oecd_light) == 434
    assert sum(r["全文策略"].startswith("已按连续序列缺口定点下载") for r in stanford_hai_light) == 3
    assert sum(r["全文策略"].startswith("不自动下载") for r in stanford_hai_light) == 14
    assert len(nesta_light) == 118
    assert all(r["全文策略"].startswith("不自动下载") for r in nesta_light)
    assert len(rathenau_light) == 75
    assert sum(r["全文策略"].startswith("已进入精选全文") for r in rathenau_light) == 13
    assert sum(r["全文策略"].startswith("总目录保留") for r in rathenau_light) == 61
    assert sum(r["全文策略"].startswith("已进入开放科学") for r in rathenau_light) == 1
    assert len(ifp_light) == 155
    assert sum(r["全文策略"].startswith("已进入精选全文") for r in ifp_light) == 16
    assert sum(r["全文策略"].startswith("已进入使命导向创新") for r in ifp_light) == 1
    assert sum(r["全文策略"].startswith("总目录保留") for r in ifp_light) == 138
    assert sum(r["全文策略"].startswith("已进入精选全文") for r in itif_light) == 34
    assert sum(r["全文策略"].startswith("已进入使命导向创新") for r in itif_light) == 1
    assert sum(r["全文策略"].startswith("已进入清洁能源技术路线") for r in itif_light) == 1
    assert sum(r["全文策略"].startswith("已进入先进计算科研算力基础设施") for r in itif_light) == 2
    assert sum(r["全文策略"].startswith("已进入先进核能聚变技术创新") for r in itif_light) == 1
    assert sum(r["全文策略"].startswith("总目录保留") for r in itif_light) == 630
    assert sum(r["全文策略"].startswith(("已进入精选全文", "已进入中国科技创新测量")) for r in csis_rai_light) == 28
    assert sum(r["全文策略"].startswith("总目录保留") for r in csis_rai_light) == 148
    assert len(rows(root / "69_机构节点主题覆盖缺口矩阵.csv")) == 1290
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
        light_catalog_count=60 + 443 + 10 + 5 + 45 + 17 + 66 + 2 + 11 + 6 + 5 + 11 + 5 + 5 + 6 + 6 + 15 + 118 + 75 + 155 + 646 + 625 + 176 + 243 + 3743 + 152 + 224 + 42 + 416 + 253,
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
            (rathenau_selected, ("本地原始资产",)),
            (ifp_selected, ("本地原始资产",)),
            (itif_selected, ("本地原始资产",)),
            (csis_rai_selected, ("本地原始资产",)),
            (eu_stoa_selected, ("本地原始PDF",)),
            (eu_jrc_selected, ("本地原始PDF",)),
            (efi_selected, ("本地原始PDF",)),
            (rieti_selected, ("本地原始PDF",)),
            (cross_china_innovation, ("本地原始资产",)),
            (china_research_system, ("本地原始资产",)),
            (china_innovation_measurement, ("本地原始资产",)),
            (science_mobility_transfer, ("本地原始PDF",)),
            (ai_science_infrastructure, ("本地原始资产",)),
            (science_diplomacy, ("本地原始资产",)),
            (research_funding_evaluation, ("本地原始资产",)),
            (technology_foresight_priorities, ("本地原始资产",)),
            (open_science_infrastructure, ("本地原始资产",)),
            (mission_oriented_rd, ("本地原始资产",)),
            (clean_energy, ("本地原始资产",)),
            (biotech, ("本地原始资产",)),
            (advanced_materials, ("本地原始资产",)),
            (advanced_computing, ("本地原始资产",)),
            (advanced_nuclear, ("本地原始资产",)),
            (acatech_selected, ("本地原始PDF",)),
            (fraunhofer_selected_fulltexts, ("本地原始PDF",)),
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
        ("162_Rathenau英文正式报告近十年轻量总目录.csv", "国际科技智库观点演变_Rathenau英文正式报告近十年轻量总目录.csv"),
        ("163_Rathenau英文正式报告近十年轻量总目录结果.md", "国际科技智库观点演变_Rathenau英文正式报告近十年轻量总目录结果.md"),
        ("164_Rathenau科技创新与中国比较跨期精选全文台账.csv", "国际科技智库观点演变_Rathenau科技创新与中国比较跨期精选全文台账.csv"),
        ("165_Rathenau科技创新与中国比较跨期精选全文结果.md", "国际科技智库观点演变_Rathenau科技创新与中国比较跨期精选全文结果.md"),
        ("166_IFP科技创新正式成果轻量总目录.csv", "国际科技智库观点演变_IFP科技创新正式成果轻量总目录.csv"),
        ("167_IFP科技创新正式成果轻量总目录结果.md", "国际科技智库观点演变_IFP科技创新正式成果轻量总目录结果.md"),
        ("168_IFP科技创新机制与中国比较精选全文台账.csv", "国际科技智库观点演变_IFP科技创新机制与中国比较精选全文台账.csv"),
        ("169_IFP科技创新机制与中国比较精选全文结果.md", "国际科技智库观点演变_IFP科技创新机制与中国比较精选全文结果.md"),
        ("170_ITIF正式报告与简报近十年轻量总目录.csv", "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录.csv"),
        ("171_ITIF正式报告与简报近十年轻量总目录结果.md", "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录结果.md"),
        ("172_ITIF科技创新机制与中国比较跨期精选全文台账.csv", "国际科技智库观点演变_ITIF科技创新机制与中国比较跨期精选全文台账.csv"),
        ("173_ITIF科技创新机制与中国比较跨期精选全文结果.md", "国际科技智库观点演变_ITIF科技创新机制与中国比较跨期精选全文结果.md"),
        ("174_FAS报告与政策备忘录近十年轻量总目录.csv", "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv"),
        ("175_FAS报告与政策备忘录近十年轻量总目录结果.md", "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录结果.md"),
        ("176_FAS科技创新机制与中国比较跨期精选全文台账.csv", "国际科技智库观点演变_FAS科技创新机制与中国比较跨期精选全文台账.csv"),
        ("177_FAS科技创新机制与中国比较跨期精选全文结果.md", "国际科技智库观点演变_FAS科技创新机制与中国比较跨期精选全文结果.md"),
        ("178_CSIS_RAI科技创新项目轻量总目录.csv", "国际科技智库观点演变_CSIS_RAI科技创新项目轻量总目录.csv"),
        ("179_CSIS_RAI科技创新项目轻量总目录结果.md", "国际科技智库观点演变_CSIS_RAI科技创新项目轻量总目录结果.md"),
        ("180_CSIS_RAI科学技术创新机制与中国比较跨期精选全文台账.csv", "国际科技智库观点演变_CSIS_RAI科学技术创新机制与中国比较跨期精选全文台账.csv"),
        ("181_CSIS_RAI科学技术创新机制与中国比较跨期精选全文结果.md", "国际科技智库观点演变_CSIS_RAI科学技术创新机制与中国比较跨期精选全文结果.md"),
        ("182_欧洲议会STOA科技评估近十年轻量总目录.csv", "国际科技智库观点演变_欧洲议会STOA科技评估近十年轻量总目录.csv"),
        ("183_欧洲议会STOA科技评估近十年轻量总目录结果.md", "国际科技智库观点演变_欧洲议会STOA科技评估近十年轻量总目录结果.md"),
        ("184_欧洲议会STOA科技创新与技术评估跨期精选全文台账.csv", "国际科技智库观点演变_欧洲议会STOA科技创新与技术评估跨期精选全文台账.csv"),
        ("185_欧洲议会STOA科技创新与技术评估跨期精选全文结果.md", "国际科技智库观点演变_欧洲议会STOA科技创新与技术评估跨期精选全文结果.md"),
        ("186_欧委会JRC科技创新政策近十年轻量总目录.csv", "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv"),
        ("187_欧委会JRC科技创新政策近十年轻量总目录结果.md", "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录结果.md"),
        ("188_欧委会JRC科学技术创新政策跨期精选全文台账.csv", "国际科技智库观点演变_欧委会JRC科学技术创新政策跨期精选全文台账.csv"),
        ("189_欧委会JRC科学技术创新政策跨期精选全文结果.md", "国际科技智库观点演变_欧委会JRC科学技术创新政策跨期精选全文结果.md"),
        ("190_德国EFI研究创新近十年轻量总目录.csv", "国际科技智库观点演变_德国EFI研究创新近十年轻量总目录.csv"),
        ("191_德国EFI研究创新近十年轻量总目录结果.md", "国际科技智库观点演变_德国EFI研究创新近十年轻量总目录结果.md"),
        ("192_德国EFI研究创新跨期精选全文台账.csv", "国际科技智库观点演变_德国EFI研究创新跨期精选全文台账.csv"),
        ("193_德国EFI研究创新跨期精选全文结果.md", "国际科技智库观点演变_德国EFI研究创新跨期精选全文结果.md"),
        ("194_RIETI科技创新与中国近十年轻量总目录.csv", "国际科技智库观点演变_RIETI科技创新与中国近十年轻量总目录.csv"),
        ("195_RIETI科技创新与中国近十年轻量总目录结果.md", "国际科技智库观点演变_RIETI科技创新与中国近十年轻量总目录结果.md"),
        ("196_RIETI科学技术创新机制与中国比较跨期精选全文台账.csv", "国际科技智库观点演变_RIETI科学技术创新机制与中国比较跨期精选全文台账.csv"),
        ("197_RIETI科学技术创新机制与中国比较跨期精选全文结果.md", "国际科技智库观点演变_RIETI科学技术创新机制与中国比较跨期精选全文结果.md"),
        ("198_英国皇家学会科学技术创新专题轻量总目录.csv", "国际科技智库观点演变_英国皇家学会科学技术创新专题轻量总目录.csv"),
        ("199_英国皇家学会科学技术创新专题轻量总目录结果.md", "国际科技智库观点演变_英国皇家学会科学技术创新专题轻量总目录结果.md"),
        ("200_英国皇家学会科学体系与技术创新跨期精选全文台账.csv", "国际科技智库观点演变_英国皇家学会科学体系与技术创新跨期精选全文台账.csv"),
        ("201_英国皇家学会科学体系与技术创新跨期精选全文结果.md", "国际科技智库观点演变_英国皇家学会科学体系与技术创新跨期精选全文结果.md"),
        ("202_acatech科学与技术创新正式成果轻量总目录.csv", "国际科技智库观点演变_acatech科学与技术创新正式成果轻量总目录.csv"),
        ("203_acatech科学与技术创新正式成果轻量总目录结果.md", "国际科技智库观点演变_acatech科学与技术创新正式成果轻量总目录结果.md"),
        ("204_acatech工程科学与技术创新跨期精选全文台账.csv", "国际科技智库观点演变_acatech工程科学与技术创新跨期精选全文台账.csv"),
        ("205_acatech工程科学与技术创新跨期精选全文结果.md", "国际科技智库观点演变_acatech工程科学与技术创新跨期精选全文结果.md"),
        ("206_NASEM科学技术创新政策近十年轻量总目录.csv", "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录.csv"),
        ("207_NASEM科学技术创新政策近十年轻量总目录结果.md", "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录结果.md"),
        ("208_NASEM科学技术创新机制与中国比较跨期精选全文台账.csv", "国际科技智库观点演变_NASEM科学技术创新机制与中国比较跨期精选全文台账.csv"),
        ("209_NASEM科学技术创新机制与中国比较跨期精选全文结果.md", "国际科技智库观点演变_NASEM科学技术创新机制与中国比较跨期精选全文结果.md"),
        ("210_本地资料库实时进度看板.md", "国际科技智库观点演变_本地资料库实时进度看板.md"),
        ("211_机构采集进度.csv", "国际科技智库观点演变_机构采集进度.csv"),
        ("212_Fraunhofer_ISI科技创新机制跨期增补全文台账.csv", "国际科技智库观点演变_Fraunhofer_ISI科技创新机制跨期增补全文台账.csv"),
        ("213_Fraunhofer_ISI科技创新机制跨期增补全文结果.md", "国际科技智库观点演变_Fraunhofer_ISI科技创新机制跨期增补全文结果.md"),
        ("214_跨机构中国科技创新机制定点增补台账.csv", "国际科技智库观点演变_跨机构中国科技创新机制定点增补台账.csv"),
        ("215_跨机构中国科技创新机制定点增补结果.md", "国际科技智库观点演变_跨机构中国科技创新机制定点增补结果.md"),
        ("216_中国科研体系与企业研发投入定点增补台账.csv", "国际科技智库观点演变_中国科研体系与企业研发投入定点增补台账.csv"),
        ("217_中国科研体系与企业研发投入定点增补结果.md", "国际科技智库观点演变_中国科研体系与企业研发投入定点增补结果.md"),
        ("218_中国科技创新测量与技术生态定点增补台账.csv", "国际科技智库观点演变_中国科技创新测量与技术生态定点增补台账.csv"),
        ("219_中国科技创新测量与技术生态定点增补结果.md", "国际科技智库观点演变_中国科技创新测量与技术生态定点增补结果.md"),
        ("220_科研人才知识转移与创新商业化定点增补台账.csv", "国际科技智库观点演变_科研人才知识转移与创新商业化定点增补台账.csv"),
        ("221_科研人才知识转移与创新商业化定点增补结果.md", "国际科技智库观点演变_科研人才知识转移与创新商业化定点增补结果.md"),
        ("222_AI_for_Science与公共科研基础设施定点增补台账.csv", "国际科技智库观点演变_AI_for_Science与公共科研基础设施定点增补台账.csv"),
        ("223_AI_for_Science与公共科研基础设施定点增补结果.md", "国际科技智库观点演变_AI_for_Science与公共科研基础设施定点增补结果.md"),
        ("224_科学外交开放科研合作与中国参与机制定点增补台账.csv", "国际科技智库观点演变_科学外交开放科研合作与中国参与机制定点增补台账.csv"),
        ("225_科学外交开放科研合作与中国参与机制定点增补结果.md", "国际科技智库观点演变_科学外交开放科研合作与中国参与机制定点增补结果.md"),
        ("226_基础研究资助科研评价与创新联系定点增补台账.csv", "国际科技智库观点演变_基础研究资助科研评价与创新联系定点增补台账.csv"),
        ("227_基础研究资助科研评价与创新联系定点增补结果.md", "国际科技智库观点演变_基础研究资助科研评价与创新联系定点增补结果.md"),
        ("228_技术前瞻公共研发优先级与中国比较定点增补台账.csv", "国际科技智库观点演变_技术前瞻公共研发优先级与中国比较定点增补台账.csv"),
        ("229_技术前瞻公共研发优先级与中国比较定点增补结果.md", "国际科技智库观点演变_技术前瞻公共研发优先级与中国比较定点增补结果.md"),
        ("230_开放科学科研基础设施与技术平台定点增补台账.csv", "国际科技智库观点演变_开放科学科研基础设施与技术平台定点增补台账.csv"),
        ("231_开放科学科研基础设施与技术平台定点增补结果.md", "国际科技智库观点演变_开放科学科研基础设施与技术平台定点增补结果.md"),
        ("232_使命导向创新重大研发计划与组织机制定点增补台账.csv", "国际科技智库观点演变_使命导向创新重大研发计划与组织机制定点增补台账.csv"),
        ("233_使命导向创新重大研发计划与组织机制定点增补结果.md", "国际科技智库观点演变_使命导向创新重大研发计划与组织机制定点增补结果.md"),
        ("234_ITIF中国先进产业技术创新能力精选全文台账.csv", "国际科技智库观点演变_ITIF中国先进产业技术创新能力精选全文台账.csv"),
        ("235_ITIF中国先进产业技术创新能力精选全文结果.md", "国际科技智库观点演变_ITIF中国先进产业技术创新能力精选全文结果.md"),
        ("236_清洁能源技术路线创新政策与中国比较定点增补台账.csv", "国际科技智库观点演变_清洁能源技术路线创新政策与中国比较定点增补台账.csv"),
        ("237_清洁能源技术路线创新政策与中国比较定点增补结果.md", "国际科技智库观点演变_清洁能源技术路线创新政策与中国比较定点增补结果.md"),
        ("238_生物技术生物制造创新机制与中国比较定点增补台账.csv", "国际科技智库观点演变_生物技术生物制造创新机制与中国比较定点增补台账.csv"),
        ("239_生物技术生物制造创新机制与中国比较定点增补结果.md", "国际科技智库观点演变_生物技术生物制造创新机制与中国比较定点增补结果.md"),
        ("240_先进材料技术创新平台与中国比较定点增补台账.csv", "国际科技智库观点演变_先进材料技术创新平台与中国比较定点增补台账.csv"),
        ("241_先进材料技术创新平台与中国比较定点增补结果.md", "国际科技智库观点演变_先进材料技术创新平台与中国比较定点增补结果.md"),
        ("242_先进计算科研算力基础设施与中国比较定点增补台账.csv", "国际科技智库观点演变_先进计算科研算力基础设施与中国比较定点增补台账.csv"),
        ("243_先进计算科研算力基础设施与中国比较定点增补结果.md", "国际科技智库观点演变_先进计算科研算力基础设施与中国比较定点增补结果.md"),
        ("244_先进核能聚变技术创新与中国比较定点增补台账.csv", "国际科技智库观点演变_先进核能聚变技术创新与中国比较定点增补台账.csv"),
        ("245_先进核能聚变技术创新与中国比较定点增补结果.md", "国际科技智库观点演变_先进核能聚变技术创新与中国比较定点增补结果.md"),
    ):
        assert sha(root / source_name) == sha(kb / "06_数据资产" / kb_name), source_name
    assert len(rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv")) >= 1
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "09_覆盖核验" / "项目覆盖矩阵.csv"))
    assert any(r.get("项目") == "国际主要科技智库观点演变研究" for r in rows(kb / "06_数据资产" / "数据资产清单.csv"))
    print("viewpoint_research_validation=ok")
    print(f"official_seeds={len(seeds)} catalog={len(catalog)} evidence={len(evidence)} institution_cards=21 pdfs={len(pdfs)} non_anchor_assets={len(catalog_assets)} early_assets={len(early_assets)} cset_assets={len(cset_assets)} atlantic_assets={len(atlantic_assets)} belfer_assets={len(belfer_assets)} nbr_assets={len(nbr_assets)} merics_assets={len(merics_assets)} bruegel_assets={len(bruegel_assets)} crds_assets={len(crds_assets)} nistep_assets={len(nistep_assets)} stepi_assets={len(stepi_assets)} kistep_assets={len(kistep_assets)}")


if __name__ == "__main__":
    main()
