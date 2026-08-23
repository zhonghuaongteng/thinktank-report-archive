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
    "162_Rathenau英文正式报告近十年轻量总目录.csv": "国际科技智库观点演变_Rathenau英文正式报告近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv": "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "187_欧委会JRC科技创新政策近十年轻量总目录结果.md": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录结果.md",
    "206_NASEM科学技术创新政策近十年轻量总目录.csv": "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "230_开放科学科研基础设施与技术平台定点增补台账.csv": "国际科技智库观点演变_开放科学科研基础设施与技术平台定点增补台账.csv",
    "231_开放科学科研基础设施与技术平台定点增补结果.md": "国际科技智库观点演变_开放科学科研基础设施与技术平台定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("国际科技政策/智库观点演变/战略转向专报", "10399条正式报告轻量总目录；2131条具有本地原始资产或官方网页转换资产，8268条轻量保留", "按科学技术创新与中国比较机制定点补充全文"),
    "国际科技智库观点演变_Rathenau英文正式报告近十年轻量总目录.csv": ("国际科技政策/智库观点演变/Rathenau轻量目录", "75项英文正式报告；14项已有本地资产，包含开放科学协同节点", "按科学体系、技术评估与创新机制调用"),
    "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv": ("国际科技政策/智库观点演变/FAS轻量目录", "625项正式成果；27项已有本地资产，包含开放科学硬件节点", "按科研能力、研发组织和技术扩散机制调用"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv": ("国际科技政策/智库观点演变/JRC轻量总目录", "3743项科技创新成果；57项已有本地资产，100项具有直接中国信号", "按科研体系、技术路线、研发投入和中国比较机制精选正文"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录结果.md": ("国际科技政策/智库观点演变/JRC轻量总目录", "JRC科技创新目录范围、分层及100项中国直接信号说明", "维护轻量目录，正文按机制缺口触发"),
    "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录.csv": ("国际科技政策/智库观点演变/NASEM轻量总目录", "253项正式成果；25项已有本地官方全文转写", "按科研制度、开放科学、资助机制和中国比较问题调用"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("国际科技政策/智库观点演变/实时进度", "10399条目录、2131条本地资产、8268条轻量保留、0条显式失败；中国关联目录747条、本地原文575条、可检索文本570条", "每次有界资料批次完成后重新生成"),
    "国际科技智库观点演变_机构采集进度.csv": ("国际科技政策/智库观点演变/实时进度", "各机构目录量、本地资产量和轻量保留量；JRC 57/3743、NASEM 25/253、FAS 27/625、Rathenau 14/75", "用于项目启动时判断存量，不生成机械全文任务"),
    "国际科技智库观点演变_开放科学科研基础设施与技术平台定点增补台账.csv": ("国际科技政策/智库观点演变/开放科学与技术平台", "6项正式材料、3份官方PDF、2项NASEM官方逐章全文、1项FAS官方网页正文、135页或章和615159个清洗文本字符", "推进开放科学激励、实践工具、技术基础设施和开放硬件机制编码"),
    "国际科技智库观点演变_开放科学科研基础设施与技术平台定点增补结果.md": ("国际科技政策/智库观点演变/开放科学与技术平台", "JRC、NASEM、Rathenau和FAS开放科学及科研技术平台证据", "按具体项目调用官方原始资产、全文文本和科技创新切片"),
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
        "文件数": "6896",
        "文档数": "5000",
        "PDF数": "1741",
        "表格数": "128",
        "最近30天活跃文件": "6896",
        "最新文件": "231_开放科学科研基础设施与技术平台定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科学技术创新覆盖单元；中国为横向维度；安全题名不自动触发全文",
        "覆盖状态": "10399条轻量总目录中2131条具有本地原始资产或官方网页转换资产；JRC 57/3743、NASEM 25/253、FAS 27/625、Rathenau 14/75，显式失败为0",
        "推进动作": "推进开放科学激励、科研技术平台、开放硬件和创新扩散机制编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
