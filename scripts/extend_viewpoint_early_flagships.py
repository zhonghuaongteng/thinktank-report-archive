from __future__ import annotations

import argparse
import csv
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from pypdf import PdfReader

from backfill_viewpoint_catalog_assets import acquire, request
from extract_viewpoint_pdf_slices import process_pdf


CANDIDATES = [
    # JST/CRDS panoramic-view continuity. These reports include international comparisons,
    # including China, and supply the technology baseline for policy interpretation.
    ("E-CRDS-2017-ENERGY", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2017-03-01", "Panoramic View of the Energy Field (2017)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2016-FR-02.html", "https://www.jst.go.jp/crds/pdf/2016/FR/CRDS-FY2016-FR-02.pdf", "关键技术国际比较；能源技术路线"),
    ("E-CRDS-2017-ENV", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2017-03-01", "Panoramic View of the Environment Field (2017)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2016-FR-03.html", "https://www.jst.go.jp/crds/pdf/2016/FR/CRDS-FY2016-FR-03.pdf", "关键技术国际比较；环境技术路线"),
    ("E-CRDS-2017-NANO", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2017-03-01", "Panoramic View of the Nanotechnology / Materials Research Field (2017)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2016-FR-05.html", "https://www.jst.go.jp/crds/pdf/2016/FR/CRDS-FY2016-FR-05.pdf", "关键技术国际比较；先进材料"),
    ("E-CRDS-2017-LIFE", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2017-03-01", "Panoramic View of the Life Science and Clinical Research Field (2017)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2016-FR-06.html", "https://www.jst.go.jp/crds/pdf/2016/FR/CRDS-FY2016-FR-06.pdf", "关键技术国际比较；生命科学"),
    ("E-CRDS-2019-ENVENERGY", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2019-03-01", "Panoramic View of the Environment and Energy Field (2019)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2018-FR-01.html", "https://www.jst.go.jp/crds/pdf/2018/FR/CRDS-FY2018-FR-01.pdf", "关键技术国际比较；绿色转型"),
    ("E-CRDS-2019-SYSTEMS", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2019-03-01", "Panoramic View of the Systems and Information Science and Technology Field (2019)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2018-FR-02.html", "https://www.jst.go.jp/crds/pdf/2018/FR/CRDS-FY2018-FR-02.pdf", "AI与数字技术；国际比较"),
    ("E-CRDS-2019-NANO", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2019-03-01", "Panoramic View of the Nanotechnology / Materials Research Field (2019)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2018-FR-03.html", "https://www.jst.go.jp/crds/pdf/2018/FR/CRDS-FY2018-FR-03.pdf", "关键技术国际比较；先进材料"),
    ("E-CRDS-2019-LIFE", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2019-03-01", "Panoramic View of the Life Science and Clinical Research Field (2019)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2018-FR-04.html", "https://www.jst.go.jp/crds/pdf/2018/FR/CRDS-FY2018-FR-04.pdf", "关键技术国际比较；生命科学"),
    ("E-CRDS-2021-ENVENERGY", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2021-03-01", "Panoramic View Report: Environment and Energy Field (2021)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2020-FR-01.html", "https://www.jst.go.jp/crds/pdf/2020/FR/CRDS-FY2020-FR-01.pdf", "关键技术国际比较；绿色转型"),
    ("E-CRDS-2021-SYSTEMS", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2021-03-01", "Panoramic View Report: Systems and Information Science and Technology Field (2021)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2020-FR-02.html", "https://www.jst.go.jp/crds/pdf/2020/FR/CRDS-FY2020-FR-02.pdf", "AI与数字技术；国际比较"),
    ("E-CRDS-2021-NANO", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2021-03-01", "Panoramic View Report: Nanotechnology/Materials Research Field (2021)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2020-FR-03.html", "https://www.jst.go.jp/crds/pdf/2020/FR/CRDS-FY2020-FR-03.pdf", "关键技术国际比较；先进材料"),
    ("E-CRDS-2021-LIFE", "jst-crds", "JST Center for Research and Development Strategy", "日本", "2021-03-01", "Panoramic View Report: Life Science and Clinical Research Field (2021)", "https://www.jst.go.jp/crds/en/publications/CRDS-FY2020-FR-04.html", "https://www.jst.go.jp/crds/pdf/2020/FR/CRDS-FY2020-FR-04.pdf", "关键技术国际比较；生命科学"),

    # NISTEP annual indicator series.
    ("E-NISTEP-2017-IND", "nistep", "National Institute of Science and Technology Policy", "日本", "2017-08-01", "Digest of Japanese Science and Technology Indicators 2017", "https://www.nistep.go.jp/en/?p=4248", "https://www.nistep.go.jp/wp/wp-content/uploads/NISTEP-RM261-Summary_E.pdf", "科技实力指标；中国国际比较"),
    ("E-NISTEP-2018-IND", "nistep", "National Institute of Science and Technology Policy", "日本", "2018-10-01", "Digest of Japanese Science and Technology Indicators 2018", "https://www.nistep.go.jp/en/?page_id=52", "https://www.nistep.go.jp/wp/wp-content/uploads/NISTEP-RM274-SummaryE.pdf", "科技实力指标；中国国际比较"),
    ("E-NISTEP-2019-IND", "nistep", "National Institute of Science and Technology Policy", "日本", "2019-11-01", "Digest of Japanese Science and Technology Indicators 2019", "https://www.nistep.go.jp/en/?page_id=52", "https://www.nistep.go.jp/wp/wp-content/uploads/NISTEP-RM283-SummaryE.pdf", "科技实力指标；中国国际比较"),
    ("E-NISTEP-2020-IND", "nistep", "National Institute of Science and Technology Policy", "日本", "2020-11-01", "Digest of Japanese Science and Technology Indicators 2020", "https://www.nistep.go.jp/en/?page_id=52", "https://www.nistep.go.jp/wp/wp-content/uploads/NISTEP-RM295-SummaryE.pdf", "科技实力指标；中国国际比较"),
    ("E-NISTEP-2021-IND", "nistep", "National Institute of Science and Technology Policy", "日本", "2021-11-01", "Digest of Japanese Science and Technology Indicators 2021", "https://www.nistep.go.jp/en/?page_id=52", "https://www.nistep.go.jp/wp/wp-content/uploads/NISTEP-RM311-SummaryE.pdf", "科技实力指标；中国国际比较"),

    # OECD digital-policy flagship sequence.
    ("E-OECD-2017-DEO", "oecd-sti", "OECD", "国际组织", "2017-10-11", "OECD Digital Economy Outlook 2017", "https://www.oecd.org/en/publications/oecd-digital-economy-outlook-2017_9789264276284-en.html", "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/10/oecd-digital-economy-outlook-2017_g1g7aa8d/9789264276284-en.pdf", "数字转型；开放与治理"),
    ("E-OECD-2019-GOING", "oecd-sti", "OECD", "国际组织", "2019-03-11", "Going Digital: Shaping Policies, Improving Lives", "https://www.oecd.org/en/publications/going-digital-shaping-policies-improving-lives_9789264312012-en.html", "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/03/going-digital-shaping-policies-improving-lives_g1g9f091/9789264312012-en.pdf", "数字转型；综合政策框架"),
    ("E-OECD-2019-MEASURE", "oecd-sti", "OECD", "国际组织", "2019-03-11", "Measuring the Digital Transformation: A Roadmap for the Future", "https://www.oecd.org/en/publications/measuring-the-digital-transformation_9789264311992-en.html", "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/03/measuring-the-digital-transformation_g1g9f08f/9789264311992-en.pdf", "数字转型；指标体系"),
    ("E-OECD-2019-AI", "oecd-sti", "OECD", "国际组织", "2019-06-11", "Artificial Intelligence in Society", "https://www.oecd.org/en/publications/2019/06/artificial-intelligence-in-society_c0054fa1.html", "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/06/artificial-intelligence-in-society_c0054fa1/eedfee77-en.pdf", "人工智能；可信治理"),
    ("E-OECD-2020-DEO", "oecd-sti", "OECD", "国际组织", "2020-11-27", "OECD Digital Economy Outlook 2020", "https://www.oecd.org/en/publications/oecd-digital-economy-outlook-2020_bb167041-en.html", "https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/11/oecd-digital-economy-outlook-2020_3f7b7e58/bb167041-en.pdf", "数字转型；疫情冲击；数据治理"),

    # MERICS China technology and industrial-policy sequence.
    ("E-MERICS-2016-MIC", "merics-tech", "MERICS Industrial Policy and Technology", "德国", "2016-08-12", "Made in China 2025: The Making of a High-Tech Superpower and Consequences for Industrial Countries", "https://merics.org/en/report/made-china-2025", "https://merics.org/sites/default/files/2020-04/Made%20in%20China%202025.pdf", "中国制造2025；产业政策"),
    ("E-MERICS-2018-SERVE", "merics-tech", "MERICS Industrial Policy and Technology", "德国", "2018-10-18", "Serve the People: Innovation and IT in China’s Social Development Agenda", "https://merics.org/report/serve-people", "", "中国数字治理；社会应用"),
    ("E-MERICS-2019-DIGITAL", "merics-tech", "MERICS Industrial Policy and Technology", "德国", "2019-04-08", "China's Digital Rise: Challenges for Europe", "https://merics.org/en/report/chinas-digital-rise", "", "中国数字崛起；欧洲应对"),
    ("E-MERICS-2019-MIC", "merics-tech", "MERICS Industrial Policy and Technology", "德国", "2019-07-02", "Evolving Made in China 2025: China’s Industrial Policy in the Quest for Global Tech Leadership", "https://merics.org/en/report/evolving-made-china-2025", "", "中国制造2025；技术领导力"),
    ("E-MERICS-2020-DECOUPLING", "merics-tech", "MERICS Industrial Policy and Technology", "德国", "2020-08-20", "Resilience and Decoupling in the Era of Great Power Competition", "https://merics.org/en/report/resilience-and-decoupling-era-great-power-competition", "", "中美科技竞争；脱钩；韧性"),
    ("E-MERICS-2021-DECOUPLING", "merics-tech", "MERICS Industrial Policy and Technology", "德国", "2021-01-14", "Decoupling: Severed Ties and Patchwork Globalisation", "https://merics.org/en/report/decoupling-severed-ties-and-patchwork-globalisation", "https://merics.org/sites/default/files/2021-01/Decoupling_EN.pdf", "技术脱钩；供应链；数据治理"),

    # ASPI China-tech sequence.
    ("E-ASPI-2018-BIGDATA", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2018-06-22", "Big Data in China and the Battle for Privacy", "https://www.aspi.org.au/report/big-data-china-and-battle-privacy", "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2018-06/Winner%20takes%20it%20all_0.pdf?VersionId=r0DDh71qxQgqwHtX8z8tmScoz55JQVyc", "中国大数据；隐私；治理"),
    ("E-ASPI-2018-ENTANGLE", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2018-06-28", "Technological Entanglement: Cooperation, Competition and the Dual-Use Dilemma in Artificial Intelligence", "https://www.aspi.org.au/report/technological-entanglement", "https://s3-ap-southeast-2.amazonaws.com/ad-aspi/2018-07/Tech-Entanglemen_PolicyBrief_20180702-v2.pdf", "中美AI合作；双用途风险"),
    ("E-ASPI-2018-HACKING", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2018-09-25", "Hacking for Ca$h", "https://www.aspi.org.au/report/hacking-cash/", "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2018-09/Hacking%20for%20cash_0.pdf?VersionId=FHTEXSif5qZDfwPoxnAAhTliEw45dMR1", "中国网络活动；技术安全"),
    ("E-ASPI-2019-MAP", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2019-04-18", "Mapping China's Tech Giants", "https://www.aspi.org.au/report/mapping-chinas-tech-giants/", "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2019-05/Mapping%20China%27s%20technology%20giants.pdf?VersionId=EINwiNpste_FojtgOPriHtlFSD2OD2tL", "中国科技企业；全球扩张"),
    ("E-ASPI-2019-MAP2", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2019-11-28", "Mapping More of China's Tech Giants: AI and Surveillance", "https://www.aspi.org.au/report/mapping-more-chinas-tech-giants/", "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2019-12/Mapping%20more%20of%20Chinas%20tech%20giants.pdf?VersionId=wpDVHlKgXJHzeK8rZ.kmy0Ei63RxXMO.", "中国AI企业；监控技术"),
    ("E-ASPI-2020-TIKTOK", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2020-09-08", "TikTok and WeChat: Curating and Controlling Global Information Flows", "https://www.aspi.org.au/report/tiktok-wechat/", "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2020-09/TikTok%20and%20WeChat.pdf?VersionId=7BNJWaoHImPVE.6KKcBP1JRD5fRnAVTZ", "中国平台企业；信息治理"),
    ("E-ASPI-2021-SUPPLY", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2021-06-08", "Mapping China's Tech Giants: Supply Chains and the Global Data Collection Ecosystem", "https://www.aspi.org.au/report/mapping-chinas-tech-giants-supply-chains-and-global-data-collection-ecosystem/", "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2021-06/Supply%20chains.pdf?VersionId=56J_tt8xYXYvsMuhriQt5dSsr92ADaZH", "数字供应链；全球数据生态"),
    ("E-ASPI-2021-REINING", "aspi", "Australian Strategic Policy Institute", "澳大利亚", "2021-06-08", "Mapping China's Technology Giants: Reining in China’s Technology Giants", "https://www.aspi.org.au/report/mapping-chinas-technology-giants-reining-chinas-technology-giants/", "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2021-06/Reining%20in%20Chinas%20technology%20giants_0.pdf?VersionId=JUkREMWd6.9bWQuN_W9oXPIq2y4zHl2R", "中国科技企业；技术自立"),

    # CSIS China innovation and selective-decoupling sequence.
    ("E-CSIS-2018-DISRUPT", "csis", "Center for Strategic and International Studies", "美国", "2018-01-08", "Disruptors, Innovators, and Thieves: Assessing Innovation in China’s Digital Economy", "https://www.csis.org/analysis/disruptors-innovators-and-thieves", "", "中国数字创新；产业竞争"),
    ("E-CSIS-2019-TRANSFER", "csis", "Center for Strategic and International Studies", "美国", "2019-09-04", "Emerging Technologies and Managing the Risk of Tech Transfer to China", "https://www.csis.org/analysis/emerging-technologies-and-managing-risk-tech-transfer-china", "", "技术转移；开放边界"),
    ("E-CSIS-2020-DRIVE", "csis", "Center for Strategic and International Studies", "美国", "2020-02-27", "China’s Uneven High-Tech Drive: Implications for the United States", "https://www.csis.org/analysis/chinas-uneven-high-tech-drive-implications-united-states", "", "中国高技术产业；竞争力"),
    ("E-CSIS-2020-301", "csis", "Center for Strategic and International Studies", "美国", "2020-04-10", "Section 301 Investigation: China’s Acts, Policies and Practices Related to Technology Transfer, Intellectual Property, and Innovation", "https://www.csis.org/analysis/section-301-investigation", "", "技术转移；知识产权；产业政策"),
    ("E-CSIS-2021-DEGREES", "csis", "Center for Strategic and International Studies", "美国", "2021-10-21", "Degrees of Separation: A Targeted Approach to U.S.-China Decoupling", "https://www.csis.org/analysis/degrees-separation-targeted-approach-us-china-decoupling-final-report", "", "选择性脱钩；AI；生物技术"),

    # ITIF China innovation-mercantilism and technology-race sequence.
    ("E-ITIF-2017-MERC", "itif", "Information Technology and Innovation Foundation", "美国", "2017-03-16", "Stopping China’s Mercantilism: A Doctrine of Constructive, Alliance-Backed Confrontation", "https://itif.org/publications/2017/03/16/stopping-chinas-mercantilism-doctrine-constructive-alliance-backed/", "", "创新重商主义；联盟政策"),
    ("E-ITIF-2018-TARIFF", "itif", "Information Technology and Innovation Foundation", "美国", "2018-03-16", "The Impact of Broad Tariffs on Chinese ICT Imports", "https://itif.org/publications/2018/03/16/broad-tariffs-chinese-ict-products-would-impose-significant-costs-us-economy/", "https://www2.itif.org/2018-ict-tariffs-china.pdf", "ICT供应链；关税；竞争政策"),
    ("E-ITIF-2019-CATCHUP", "itif", "Information Technology and Innovation Foundation", "美国", "2019-04-08", "Is China Catching Up to the United States in Innovation?", "https://itif.org/publications/2019/04/08/china-catching-united-states-innovation/", "", "中美创新能力比较"),
    ("E-ITIF-2019-AIRACE", "itif", "Information Technology and Innovation Foundation", "美国", "2019-08-19", "Who Is Winning the AI Race: China, the EU or the United States?", "https://itif.org/publications/2019/08/19/who-winning-ai-race-china-eu-or-united-states/", "https://s3.amazonaws.com/www2.datainnovation.org/2019-china-eu-us-ai.pdf", "人工智能；中欧美竞争"),
    ("E-ITIF-2021-MOORE", "itif", "Information Technology and Innovation Foundation", "美国", "2021-02-18", "Moore’s Law Under Attack: The Impact of China’s Policies on Global Semiconductor Innovation", "https://itif.org/publications/2021/02/18/moores-law-under-attack-impact-chinas-policies-global-semiconductor/", "", "半导体；中国产业政策"),
    ("E-ITIF-2021-INDUSTRY", "itif", "Information Technology and Innovation Foundation", "美国", "2021-05-10", "Industry by Industry: More Chinese Mercantilism, Less Global Innovation", "https://itif.org/publications/2021/05/10/industry-industry-more-chinese-mercantilism-less-global-innovation/", "", "先进产业；创新重商主义"),
]


FIELDS = [
    "报告ID", "机构ID", "机构英文名", "国家或地区", "发布日期", "观察窗", "报告名称",
    "报告类型", "原文链接", "本地路径", "正文完整度", "优先级", "示踪问题",
    "机构观点等级", "样本角色", "编码状态", "预期用途", "本地原始资产路径", "原始资产状态",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def acquire_candidate(item: tuple[str, ...]):
    report_id, _, _, _, _, title, landing, direct, _ = item
    if direct:
        try:
            data, final_url, _ = request(direct, referer=landing)
            if data.startswith(b"%PDF"):
                return report_id, data, final_url, "官方PDF已获取", ""
        except Exception as exc:  # generic landing-page acquisition remains available
            direct_error = f"direct:{type(exc).__name__}:{exc}"
        else:
            direct_error = "direct:非PDF"
    else:
        direct_error = ""
    result = acquire({"报告ID": report_id, "原文链接": landing, "报告名称": title})
    if result.pdf_data:
        return report_id, result.pdf_data, result.download_url, result.status, result.error
    return report_id, b"", result.final_landing_url, result.status, " | ".join(filter(None, [direct_error, result.error]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()

    root = args.research.resolve()
    catalog_path = root / "05_报告总目录.csv"
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    slice_dir.mkdir(parents=True, exist_ok=True)

    catalog = read_csv(catalog_path)
    existing_ids = {row["报告ID"] for row in catalog}
    existing_by_id = {row["报告ID"]: row for row in catalog}
    existing_titles = {re.sub(r"\W+", "", row["报告名称"].lower()) for row in catalog}
    targets = [
        item for item in CANDIDATES
        if (
            item[0] not in existing_ids
            and re.sub(r"\W+", "", item[5].lower()) not in existing_titles
        ) or (
            item[0] in existing_by_id
            and existing_by_id[item[0]]["原始资产状态"] != "官方PDF已保存并校验"
        )
    ]

    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(acquire_candidate, item): item[0] for item in targets}
        for future in as_completed(futures):
            report_id = futures[future]
            try:
                results[report_id] = future.result()
            except Exception as exc:
                results[report_id] = (report_id, b"", "", "获取失败", f"{type(exc).__name__}: {exc}")

    ledger_path = root / "23_早期旗舰报告增补台账.csv"
    ledger = read_csv(ledger_path) if ledger_path.exists() else []
    ledger_by_id = {row["报告ID"]: row for row in ledger}
    new_rows = []
    for item in CANDIDATES:
        report_id, institution_id, institution, country, published, title, landing, direct, tracer = item
        if report_id not in results:
            continue
        _, data, download_url, status, error = results[report_id]
        pdf_path = pdf_dir / f"{report_id}.pdf"
        pages = 0
        chars = 0
        digest = ""
        local_asset = ""
        asset_status = "获取失败"
        if data.startswith(b"%PDF"):
            pdf_path.write_bytes(data)
            digest = sha256(pdf_path)
            reader = PdfReader(str(pdf_path))
            pages = len(reader.pages)
            process_pdf(pdf_path, text_dir, slice_dir)
            text_path = text_dir / f"{report_id}.txt"
            chars = len(text_path.read_text(encoding="utf-8"))
            local_asset = str(pdf_path)
            asset_status = "官方PDF已保存并校验"

        window = "W1" if published[:4] in {"2016", "2017", "2018"} else "W2"
        report_type = "旗舰系列报告" if institution_id in {"jst-crds", "nistep", "oecd-sti"} else "涉华科技专题报告"
        catalog_row = {
            "报告ID": report_id,
            "机构ID": institution_id,
            "机构英文名": institution,
            "国家或地区": country,
            "发布日期": published,
            "观察窗": window,
            "报告名称": title,
            "报告类型": report_type,
            "原文链接": landing,
            "本地路径": "",
            "正文完整度": "本地原文已保存" if local_asset else "获取失败",
            "优先级": "P1-early-series",
            "示踪问题": tracer,
            "机构观点等级": "机构正式观点",
            "样本角色": "目录外早期增补",
            "编码状态": "待编码",
            "预期用途": "补足2016—2021连续序列与战略转向早期证据",
            "本地原始资产路径": local_asset,
            "原始资产状态": asset_status,
        }
        if report_id in existing_by_id:
            existing_by_id[report_id].update(catalog_row)
        else:
            new_rows.append(catalog_row)
        ledger_row = {
            "报告ID": report_id,
            "机构ID": institution_id,
            "发布日期": published,
            "观察窗": window,
            "报告名称": title,
            "主题线索": tracer,
            "官方落地页": landing,
            "直接下载地址": download_url or direct,
            "本地PDF": local_asset,
            "字节数": str(len(data)) if data else "0",
            "SHA256": digest,
            "PDF页数": str(pages),
            "提取文本字符数": str(chars),
            "本地状态": asset_status,
            "错误": error,
            "获取日期": date.today().isoformat(),
        }
        ledger_by_id[report_id] = ledger_row

    merged = catalog + new_rows
    merged.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, merged, FIELDS)
    ledger_fields = [
        "报告ID", "机构ID", "发布日期", "观察窗", "报告名称", "主题线索", "官方落地页",
        "直接下载地址", "本地PDF", "字节数", "SHA256", "PDF页数", "提取文本字符数",
        "本地状态", "错误", "获取日期",
    ]
    ledger = [ledger_by_id[item[0]] for item in CANDIDATES if item[0] in ledger_by_id]
    write_csv(ledger_path, ledger, ledger_fields)

    matrix_rows = []
    for institution_id in sorted({row["机构ID"] for row in merged}):
        institution_rows = [row for row in merged if row["机构ID"] == institution_id]
        early_rows = [row for row in institution_rows if row["观察窗"] in {"W1", "W2"}]
        if not early_rows:
            continue
        matrix_rows.append({
            "机构ID": institution_id,
            "机构英文名": institution_rows[0]["机构英文名"],
            "W1_2016_2018": str(sum(row["观察窗"] == "W1" for row in institution_rows)),
            "W2_2019_2021": str(sum(row["观察窗"] == "W2" for row in institution_rows)),
            "W3_2022_2026": str(sum(row["观察窗"] == "W3" for row in institution_rows)),
            "早期合计": str(len(early_rows)),
            "最早年份": min(row["发布日期"][:4] for row in early_rows),
            "早期本地原文": str(sum(bool(row["本地原始资产路径"]) for row in early_rows)),
            "连续性判断": "W1/W2均有样本" if {row["观察窗"] for row in early_rows} == {"W1", "W2"} else "仍有观察窗缺口",
        })
    write_csv(
        root / "25_早期连续覆盖矩阵.csv",
        matrix_rows,
        ["机构ID", "机构英文名", "W1_2016_2018", "W2_2019_2021", "W3_2022_2026", "早期合计", "最早年份", "早期本地原文", "连续性判断"],
    )

    direct_china_ids = {"merics-tech", "aspi", "csis", "itif"}
    topic_rows = []
    for row in ledger:
        report_id = row["报告ID"]
        topic_rows.append({
            "报告ID": report_id,
            "机构ID": row["机构ID"],
            "发布日期": row["发布日期"],
            "观察窗": row["观察窗"],
            "报告名称": row["报告名称"],
            "资料角色": "涉华科技直接分析" if row["机构ID"] in direct_china_ids else "全球科技基线与中国比较",
            "主题线索": row["主题线索"],
            "本地PDF": row["本地PDF"],
            "逐页文本": str(text_dir / f"{report_id}.txt"),
            "示踪切片": str(slice_dir / f"{report_id}.md"),
            "官方落地页": row["官方落地页"],
        })
    write_csv(
        root / "26_早期材料主题索引.csv",
        topic_rows,
        ["报告ID", "机构ID", "发布日期", "观察窗", "报告名称", "资料角色", "主题线索", "本地PDF", "逐页文本", "示踪切片", "官方落地页"],
    )

    ok = [row for row in ledger if row["本地状态"] == "官方PDF已保存并校验"]
    failed = [row for row in ledger if row["本地状态"] != "官方PDF已保存并校验"]
    by_inst = {}
    for row in ledger:
        by_inst[row["机构ID"]] = by_inst.get(row["机构ID"], 0) + 1
    base_catalog_count = len(merged) - len(ledger)
    lines = [
        "# 2016—2021年早期旗舰报告增补结果",
        "",
        f"- 目录外候选：{len(ledger)}项。",
        f"- 官方PDF成功：{len(ok)}项；失败：{len(failed)}项。",
        f"- 新增PDF字节数：{sum(int(row['字节数']) for row in ok):,}。",
        f"- 新增PDF物理页数：{sum(int(row['PDF页数']) for row in ok):,}。",
        f"- 报告总目录：{base_catalog_count}项扩展至{len(merged)}项。",
        "",
        "## 机构分布",
        "",
    ]
    lines.extend(f"- {key}：{value}项。" for key, value in sorted(by_inst.items()))
    lines.extend(["", "## 未完成项", ""])
    if failed:
        lines.extend(f"- `{row['报告ID']}`：{row['错误'] or row['本地状态']}" for row in failed)
    else:
        lines.append("无。")
    lines.extend([
        "",
        "## 使用边界",
        "",
        "本轮只扩展本地证据资产与目录，不据此改写专报。新增条目尚未完成人工观点编码；正式引用时应回到逐页文本和PDF原文复核。",
        "跨项目调用优先使用`25_早期连续覆盖矩阵.csv`和`26_早期材料主题索引.csv`定位材料。",
        "",
    ])
    (root / "24_早期旗舰报告增补结果.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"early_candidates={len(ledger)} pdf_ok={len(ok)} failed={len(failed)} catalog={len(merged)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
