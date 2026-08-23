from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from datetime import date
from pathlib import Path

from extend_viewpoint_merics_technology import CATALOG_FIELDS, build_theme_rows, normalize_text_content, read_csv, write_csv
from extend_viewpoint_nbr_technology import fetch_jina
from extend_viewpoint_nistep_japanese import (
    COMPARISON_FIELDS,
    build_crds_nistep_comparison,
    nistep_status_summary,
)


REPORT_ID = "C-NISTEP-DP242-6EEE0740"
LANDING_URL = "http://hdl.handle.net/11035/0002000273"
RECORD_URL = "https://nistep.repo.nii.ac.jp/records/2000273"
FULL_PDF_URL = "https://nistep.repo.nii.ac.jp/record/2000273/files/NISTEP-DP242-FullJ.pdf"
SUMMARY_PDF_URL = "https://nistep.repo.nii.ac.jp/record/2000273/files/NISTEP-DP242-SummaryJ.pdf"
STATUS = "官方仓储概要PDF代理文本已保存"
COMPLETENESS = "NISTEP官方仓储概要PDF的Jina代理文本已保存；完整报告PDF入口已核验，精确引用须回查PDF"


def repair_rows(
    catalog: list[dict[str, str]],
    ledger: list[dict[str, str]],
    themes: list[dict[str, str]],
    local_asset: str,
    local_text: str,
    local_slice: str,
    byte_count: int,
    digest: str,
    char_count: int,
    acquired_on: str,
) -> None:
    catalog_rows = [row for row in catalog if row.get("报告ID") == REPORT_ID]
    ledger_rows = [row for row in ledger if row.get("报告ID") == REPORT_ID]
    theme_rows = [row for row in themes if row.get("报告ID") == REPORT_ID]
    if len(catalog_rows) != 1 or len(ledger_rows) != 1 or not theme_rows:
        raise RuntimeError(f"NISTEP DP242 row mismatch: catalog={len(catalog_rows)} ledger={len(ledger_rows)} themes={len(theme_rows)}")
    catalog_rows[0].update(
        {
            "本地路径": local_text,
            "正文完整度": COMPLETENESS,
            "本地原始资产路径": local_asset,
            "原始资产状态": STATUS,
        }
    )
    ledger_rows[0].update(
        {
            "官方PDF": FULL_PDF_URL,
            "页面来源": "NISTEP官方仓储概要PDF的Jina代理文本；完整报告PDF入口已核验",
            "本地原始资产": local_asset,
            "本地文本": local_text,
            "本地切片或转写": local_slice,
            "字节数": str(byte_count),
            "SHA256": digest,
            "PDF页数": "0",
            "提取文本字符数": str(char_count),
            "本地状态": STATUS,
            "错误": "",
            "获取日期": acquired_on,
        }
    )
    for row in theme_rows:
        row.update({"本地原始资产": local_asset, "本地文本": local_text, "本地状态": STATUS})


def rebuild_derivatives(root: Path, ledger: list[dict[str, str]]) -> None:
    theme_rows = build_theme_rows([{**row, "报告名称": row["日文题名"]} for row in ledger])
    write_csv(
        root / "57_NISTEP日文科技与中国主题索引.csv",
        theme_rows,
        ["主题标签", "科技关联层级", "报告ID", "发布日期", "观察窗", "报告名称", "资料角色", "本地原始资产", "本地文本", "官方落地页", "本地状态"],
    )
    matrix_counts = Counter(
        (theme, row["科技关联层级"], row["观察窗"], row["报告类型"], row["本地状态"])
        for row in ledger
        for theme in row["主题标签"].split("；")
    )
    matrix = [
        {"主题标签": key[0], "科技关联层级": key[1], "观察窗": key[2], "报告类型": key[3], "本地状态": key[4], "材料数": str(value)}
        for key, value in sorted(matrix_counts.items())
    ]
    write_csv(root / "58_NISTEP日文科技与中国复用矩阵.csv", matrix, ["主题标签", "科技关联层级", "观察窗", "报告类型", "本地状态", "材料数"])
    crds = read_csv(root / "51_CRDS日文科技与中国专题增补台账.csv")
    write_csv(root / "59_CRDS_NISTEP科技主题与机构功能对照.csv", build_crds_nistep_comparison(crds, ledger), COMPARISON_FIELDS)
    statuses = Counter(row["本地状态"] for row in ledger)
    result_path = root / "56_NISTEP日文科技与中国专题增补结果.md"
    lines = result_path.read_text(encoding="utf-8").splitlines()
    lines[4] = f"- {nistep_status_summary(statuses)}"
    lines[5] = f"- 报告总目录现为：{len(read_csv(root / '05_报告总目录.csv'))}项。"
    result_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    title = "令和５年度 博士（後期）課程1 年次における進路意識と経済状況に関する調査 －2024年2月～2024年4月実施調査－"
    summary = normalize_text_content(fetch_jina(f"https://r.jina.ai/{SUMMARY_PDF_URL}", timeout=180))
    snapshot = fetch_jina(f"https://r.jina.ai/{RECORD_URL}", timeout=120)
    if len(summary) < 4000 or "博士" not in summary or "2024" not in summary:
        raise RuntimeError(f"NISTEP DP242 summary proxy incomplete: {len(summary)}")
    if FULL_PDF_URL not in snapshot or "DP242" not in snapshot:
        raise RuntimeError("NISTEP DP242 repository page does not expose the expected full PDF")

    snapshot_dir = root / "03_证据底稿" / "网页快照"
    text_dir = root / "03_证据底稿" / "网页文本"
    transcript_dir = root / "03_证据底稿" / "网页转写"
    for directory in (snapshot_dir, text_dir, transcript_dir):
        directory.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / f"{REPORT_ID}.md"
    text_path = text_dir / f"{REPORT_ID}.txt"
    transcript_path = transcript_dir / f"{REPORT_ID}.md"
    snapshot_path.write_text(normalize_text_content(snapshot), encoding="utf-8", newline="\n")
    text_path.write_text(summary, encoding="utf-8", newline="\n")
    transcript_path.write_text(
        f"# {title}\n\n- 发布机构：National Institute of Science and Technology Policy\n"
        f"- 报告编号：DP:242\n- 发布日期：2025-11-01\n- 官方落地页：{LANDING_URL}\n"
        f"- 完整报告PDF：{FULL_PDF_URL}\n- 本地证据形态：官方概要PDF的Jina代理文本；完整报告须回查官方PDF\n\n{summary}\n",
        encoding="utf-8",
        newline="\n",
    )
    data = summary.encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    catalog = read_csv(root / "05_报告总目录.csv")
    ledger_path = root / "55_NISTEP日文科技与中国专题增补台账.csv"
    ledger = read_csv(ledger_path)
    themes = read_csv(root / "57_NISTEP日文科技与中国主题索引.csv")
    repair_rows(catalog, ledger, themes, str(text_path), str(text_path), str(transcript_path), len(data), digest, len(summary), date.today().isoformat())
    write_csv(root / "05_报告总目录.csv", catalog, CATALOG_FIELDS)
    write_csv(ledger_path, ledger, list(ledger[0]))
    rebuild_derivatives(root, ledger)
    print(f"nistep_dp242_status={STATUS} chars={len(summary)} sha256={digest}")


if __name__ == "__main__":
    main()
