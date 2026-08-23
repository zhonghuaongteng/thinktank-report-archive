from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path


COPIES = {
    "05_报告总目录.csv": "国际科技智库观点演变_官方报告目录_2016-2026.csv",
    "69_机构节点主题覆盖缺口矩阵.csv": "国际科技智库观点演变_机构节点主题覆盖缺口矩阵.csv",
    "71_覆盖缺口结果.md": "国际科技智库观点演变_覆盖缺口结果.md",
    "130_NSF_NSB科学与工程指标近十年轻量目录.csv": "国际科技智库观点演变_NSF_NSB科学与工程指标近十年轻量目录.csv",
    "131_NSF_NSB科学与工程指标近十年轻量目录结果.md": "国际科技智库观点演变_NSF_NSB科学与工程指标近十年轻量目录结果.md",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "187_欧委会JRC科技创新政策近十年轻量总目录结果.md": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录结果.md",
    "190_德国EFI研究创新近十年轻量总目录.csv": "国际科技智库观点演变_德国EFI研究创新近十年轻量总目录.csv",
    "194_RIETI科技创新与中国近十年轻量总目录.csv": "国际科技智库观点演变_RIETI科技创新与中国近十年轻量总目录.csv",
    "206_NASEM科学技术创新政策近十年轻量总目录.csv": "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "226_基础研究资助科研评价与创新联系定点增补台账.csv": "国际科技智库观点演变_基础研究资助科研评价与创新联系定点增补台账.csv",
    "227_基础研究资助科研评价与创新联系定点增补结果.md": "国际科技智库观点演变_基础研究资助科研评价与创新联系定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("国际科技政策/智库观点演变/战略转向专报", "10399条正式报告轻量总目录；2119条具有本地原始资产或官方网页转换资产，8280条轻量保留", "按科学技术创新与中国比较机制定点补充全文"),
    "国际科技智库观点演变_NSF_NSB科学与工程指标近十年轻量目录.csv": ("国际科技政策/智库观点演变/NSF与NSB指标目录", "2016—2026六期科学与工程指标节点均已有本地全文；覆盖科研投入、人才、论文、专利、产业创新及中国比较", "按统计口径和专题分卷执行跨期比较"),
    "国际科技智库观点演变_NSF_NSB科学与工程指标近十年轻量目录结果.md": ("国际科技政策/智库观点演变/NSF与NSB指标目录", "六期官方节点的目录范围、产品结构变化及全文覆盖说明", "调用时处理2018综合卷与2020年后专题套系的结构差异"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv": ("国际科技政策/智库观点演变/JRC轻量总目录", "3743项科技创新成果；51项已有本地资产，96项具有中国直接信号", "按科研体系、研发投入、创新测量和中国比较机制精选正文"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录结果.md": ("国际科技政策/智库观点演变/JRC轻量总目录", "JRC科技创新目录范围、分层、96项中国直接信号及安全语境边界", "维护轻量目录，正文按机制缺口触发"),
    "国际科技智库观点演变_德国EFI研究创新近十年轻量总目录.csv": ("国际科技政策/智库观点演变/EFI轻量目录", "152项年度总报告和分章；12项已有本地全文", "按科学体系、研究资助和创新政策机制调用"),
    "国际科技智库观点演变_RIETI科技创新与中国近十年轻量总目录.csv": ("国际科技政策/智库观点演变/RIETI轻量目录", "224项讨论论文；23项已有本地全文，覆盖研发、技术扩散、产业政策及中国比较", "按作者归因调用科研—创新联系和中国比较证据"),
    "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录.csv": ("国际科技政策/智库观点演变/NASEM轻量总目录", "253项成果；23项已有本地官方全文转写", "按科研制度、开放科学、资助机制及中国比较问题调用"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("国际科技政策/智库观点演变/实时进度", "10399条目录、2119条本地资产、8280条轻量保留、0条显式失败；中国关联目录743条、本地原文571条、可检索文本566条", "每次有界资料批次完成后重新生成"),
    "国际科技智库观点演变_机构采集进度.csv": ("国际科技政策/智库观点演变/实时进度", "各机构目录量、本地资产量和轻量保留量；NSF/NSB指标27/27、JRC 51/3743、NASEM 23/253、RIETI 23/224、EFI 12/152", "用于项目启动时判断存量，不生成机械全文任务"),
    "国际科技智库观点演变_基础研究资助科研评价与创新联系定点增补台账.csv": ("国际科技政策/智库观点演变/基础研究资助与科研评价", "6项正式材料、5份官方PDF、1项NASEM官方逐章全文、1255页或章、3057703个清洗文本字符和894次中国词形命中", "推进科研拨款、科学政策、全球能力统计、论文—专利联系和资助机制实验编码"),
    "国际科技智库观点演变_基础研究资助科研评价与创新联系定点增补结果.md": ("国际科技政策/智库观点演变/基础研究资助与科研评价", "JRC、NSF/NSB、EFI、RIETI和NASEM基础研究投入与科研评价机制证据", "按具体项目调用官方PDF或章节、全文文本和科技创新切片"),
}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--kb", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    kb = args.kb.resolve()
    asset_dir = kb / "06_数据资产"
    for source_name, kb_name in COPIES.items():
        shutil.copy2(root / source_name, asset_dir / kb_name)

    inventory_path = asset_dir / "数据资产清单.csv"
    inventory, fields = read_csv(inventory_path)
    by_name = {row.get("数据文件", ""): row for row in inventory if row.get("项目") == "国际主要科技智库观点演变研究"}
    for kb_name, (project_type, purpose, next_step) in PURPOSES.items():
        target = asset_dir / kb_name
        row = by_name.get(kb_name)
        if row is None:
            row = {field: "" for field in fields}
            inventory.append(row)
        stat = target.stat()
        row.update({
            "项目": "国际主要科技智库观点演变研究",
            "项目类型": project_type,
            "数据文件": kb_name,
            "相对路径": f"06_数据资产\\{kb_name}",
            "原始路径": str(target),
            "格式": target.suffix,
            "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime("%Y/%m/%d %H:%M:%S"),
            "大小MB": f"{stat.st_size / 1024 / 1024:.2f}",
            "研究用途": purpose,
            "下一步": next_step,
        })
    write_csv(inventory_path, inventory, fields)

    matrix_path = kb / "09_覆盖核验" / "项目覆盖矩阵.csv"
    matrix, matrix_fields = read_csv(matrix_path)
    row = next(item for item in matrix if item.get("项目") == "国际主要科技智库观点演变研究")
    row.update({
        "文件数": "6856",
        "文档数": "4963",
        "PDF数": "1732",
        "表格数": "126",
        "最近30天活跃文件": "6856",
        "最新文件": "227_基础研究资助科研评价与创新联系定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科学技术创新覆盖单元；中国为横向维度；安全题名不自动触发全文",
        "覆盖状态": "10399条轻量总目录中2119条具有本地原始资产或官方网页转换资产；NSF/NSB指标27/27、JRC 51/3743、NASEM 23/253、RIETI 23/224、EFI 12/152，显式失败为0",
        "推进动作": "推进基础研究资助、科研绩效评价、知识产出与创新联系编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
