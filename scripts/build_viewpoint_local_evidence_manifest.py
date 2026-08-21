from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import date
from pathlib import Path

from pypdf import PdfReader


DIRECT_URLS = {
    "S-ASPI-2020-01": "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2020-09/Ensuring%20a%20trusted%205G%20ecosystem.pdf?VersionId=PqDDm8FpWzHXLT0A6bUBbuVdDCw2m.DI",
    "S-ASPI-2021-01": "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2021-11/Benchmarking%20critical%20technologies-v2.pdf?VersionId=ynft3BR4FDbu66jNM4v7y4AtBmELkA_d",
    "S-ASPI-2023-01": "https://ad-aspi.s3.ap-southeast-2.amazonaws.com/2023-08/ASPIs%20Critical%20Technology%20Tracker.pdf?VersionId=nVmWySgLSX2FMaS1U.uQVgQvvd_W427G",
    "S-CEIP-2016-01": "https://assets.carnegieendowment.org/static/files/Brief-Sinan-Cyberspace.pdf",
    "S-CEIP-2022-01": "https://assets.carnegieendowment.org/static/files/Bateman_US-China_Decoupling_final.pdf",
    "S-CEIP-2025-01": "https://assets.carnegieendowment.org/static/files/CETF_How%20to%20Stop%20Losing_final-2.pdf",
    "S-CH-2019-01": "https://www.chathamhouse.org/sites/default/files/CHHJ7480-US-China-Competition-RP-WEB.pdf",
    "S-CRDS-2017-01": "https://www.jst.go.jp/crds/pdf/2016/FR/CRDS-FY2016-FR-04.pdf",
    "S-CRDS-2019-01": "https://www.jst.go.jp/crds/pdf/2019/FR/CRDS-FY2019-FR-01.pdf",
    "S-CRDS-2021-01": "https://www.jst.go.jp/crds/pdf/2020/SP/CRDS-FY2020-SP-06.pdf",
    "S-CRDS-2023-01": "https://www.jst.go.jp/crds/pdf/2023/SP/CRDS-FY2023-SP-01.pdf",
    "S-CRDS-2024-01": "https://www.jst.go.jp/crds/pdf/2023/RR/CRDS-FY2023-RR-07.pdf",
    "S-CSIS-2017-01": "https://csis-website-prod.s3.amazonaws.com/s3fs-public/publication/170818_Rice_InnovationLedEconGrowth_Web.pdf",
    "S-CSIS-2018-01": "https://csis-website-prod.s3.amazonaws.com/s3fs-public/publication/180227_Carter_MachineIntelligence_Web.PDF",
    "S-CSIS-2020-01": "https://csis-website-prod.s3.amazonaws.com/s3fs-public/publication/200901_Gerstel_InnovationStrategy_FullReport_FINAL_0.pdf",
    "S-CSIS-2020-02": "https://csis-website-prod.s3.amazonaws.com/s3fs-public/publication/201015_GoodmanGerstel_AmericasInnovativeEdge_Report%20%28002%29.pdf",
    "S-CSIS-2026-01": "https://csis-website-prod.s3.amazonaws.com/s3fs-public/2026-03/260302_Kennedy_Innovation_Drive.pdf?VersionId=5YpqvRvpo5tBkcubWn8aIE9K0CoIxU16",
    "S-FISI-2016-01": "https://www.isi.fraunhofer.de/content/dam/isi/dokumente/ccp/thesenpapiere/Position_Paper_Innovation_System.pdf",
    "S-FISI-2020-01": "https://www.isi.fraunhofer.de/content/dam/isi/dokumente/policy-briefs/policy_brief_technologiesouveraenitaet.pdf",
    "S-FISI-2021-01": "https://www.isi.fraunhofer.de/content/dam/isi/dokumente/policy-briefs/policy_brief_missionsorientierung.pdf",
    "S-ITIF-2016-01": "https://cdn.sanity.io/files/03hnmfyj/production/a4f5cc2a01c67c167de0c8e72d204028e7085bcd.pdf",
    "S-ITIF-2020-01": "https://www2.itif.org/2020-case-counter-national-industrial-strategy-china-technological-rise.pdf",
    "S-ITIF-2026-01": "https://cdn.sanity.io/files/03hnmfyj/production/d63dff0999362598252472e8861f239b595883c5.pdf",
    "S-NISTEP-2016-01": "https://www.nistep.go.jp/wp/wp-content/uploads/NISTEP-RM251-Full_J.pdf",
    "S-NISTEP-2019-01": "https://nistep.repo.nii.ac.jp/record/6657/files/NISTEP-NR183-SummaryE.pdf",
    "S-NISTEP-2021-01": "https://nistep.repo.nii.ac.jp/record/6735/files/NISTEP-RM309-FullJ.pdf",
    "S-NISTEP-2025-01": "https://www.nistep.go.jp/en/wp-content/uploads/NISTEP-RM349-SummaryE.pdf",
    "S-OECD-2018-01": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/11/oecd-science-technology-and-innovation-outlook-2018_g1g98de3/sti_in_outlook-2018-en.pdf",
    "S-OECD-2021-01": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/01/oecd-science-technology-and-innovation-outlook-2021_3f424d14/75f79015-en.pdf",
    "S-OECD-2023-01": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2023/03/oecd-science-technology-and-innovation-outlook-2023_fb6e6c20/0b55736e-en.pdf",
    "S-OECD-2025-01": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/10/oecd-science-technology-and-innovation-outlook-2025_bae3698d/5fe57b90-en.pdf",
    "S-RAND-2022-01": "https://www.rand.org/content/dam/rand/pubs/research_reports/RRA1400/RRA1417-1/RAND_RRA1417-1.pdf",
    "S-RAND-2023-01": "https://www.rand.org/content/dam/rand/pubs/research_reports/RRA2800/RRA2850-1/RAND_RRA2850-1.pdf",
    "S-RAND-2024-01": "https://www.rand.org/content/dam/rand/pubs/research_reports/RRA3000/RRA3055-1/RAND_RRA3055-1.pdf",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    root = args.research.resolve()
    pdf_dir = root / "03_证据底稿" / "原文PDF"
    text_dir = root / "03_证据底稿" / "文本"
    seed_path = root / "05_官方锚点种子.csv"
    catalog_path = root / "05_报告总目录.csv"
    seeds = read_rows(seed_path)
    seed_by_id = {row["种子ID"]: row for row in seeds}

    assets: list[dict[str, str]] = []
    for seed_id, seed in seed_by_id.items():
        pdf = pdf_dir / f"{seed_id}.pdf"
        text = text_dir / f"{seed_id}.txt"
        if not pdf.exists():
            assets.append({
                "种子ID": seed_id, "机构ID": seed["机构ID"], "日期": seed["日期"],
                "观察窗": seed["观察窗"], "报告名称": seed["报告名称"],
                "官方落地页": seed["官方页面或PDF"], "直接下载地址": "",
                "本地PDF": "", "字节数": "0", "SHA256": "", "PDF页数": "0",
                "提取文本字符数": "0", "本地状态": "无独立PDF，保留官方网页全文或待发布",
                "获取日期": date.today().isoformat(),
            })
            continue
        if pdf.read_bytes()[:4] != b"%PDF":
            raise ValueError(f"invalid PDF signature: {pdf}")
        reader = PdfReader(str(pdf))
        text_chars = len(text.read_text(encoding="utf-8")) if text.exists() else 0
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        assets.append({
            "种子ID": seed_id, "机构ID": seed["机构ID"], "日期": seed["日期"],
            "观察窗": seed["观察窗"], "报告名称": seed["报告名称"],
            "官方落地页": seed["官方页面或PDF"],
            "直接下载地址": DIRECT_URLS.get(seed_id, seed["官方页面或PDF"]),
            "本地PDF": str(pdf), "字节数": str(pdf.stat().st_size), "SHA256": digest,
            "PDF页数": str(len(reader.pages)), "提取文本字符数": str(text_chars),
            "本地状态": "官方PDF已保存并校验", "获取日期": date.today().isoformat(),
        })
        seed["获取状态"] = "官方PDF已保存并校验"

    fields = list(assets[0])
    write_rows(root / "19_本地全文资产台账.csv", assets, fields)
    write_rows(seed_path, seeds, list(seeds[0]))

    catalog = read_rows(catalog_path)
    for row in catalog:
        pdf = pdf_dir / f"{row['报告ID']}.pdf"
        if pdf.exists():
            row["本地路径"] = str(pdf)
            row["正文完整度"] = "官方PDF全文已保存"
    write_rows(catalog_path, catalog, list(catalog[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
