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
    "77_OECD_STI正式系列轻量目录.csv": "国际科技智库观点演变_OECD_STI正式系列轻量目录.csv",
    "84_Fraunhofer_ISI创新系统政策分析轻量目录.csv": "国际科技智库观点演变_Fraunhofer_ISI创新系统政策分析轻量目录.csv",
    "166_IFP科技创新正式成果轻量总目录.csv": "国际科技智库观点演变_IFP科技创新正式成果轻量总目录.csv",
    "170_ITIF正式报告与简报近十年轻量总目录.csv": "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv": "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "232_使命导向创新重大研发计划与组织机制定点增补台账.csv": "国际科技智库观点演变_使命导向创新重大研发计划与组织机制定点增补台账.csv",
    "233_使命导向创新重大研发计划与组织机制定点增补结果.md": "国际科技智库观点演变_使命导向创新重大研发计划与组织机制定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("国际科技政策/智库观点演变/战略转向专报", "10399条正式报告轻量总目录；2136条具有本地原始资产或官方网页转换资产，8263条轻量保留", "按科学技术创新与中国比较机制定点补充全文"),
    "国际科技智库观点演变_OECD_STI正式系列轻量目录.csv": ("国际科技政策/智库观点演变/OECD STI轻量目录", "445项正式系列成果；新增使命导向创新评价方法全文节点", "按科研制度、研发治理和任务评价机制调用"),
    "国际科技智库观点演变_Fraunhofer_ISI创新系统政策分析轻量目录.csv": ("国际科技政策/智库观点演变/Fraunhofer ISI轻量目录", "47项创新系统政策分析成果；使命导向政策执行锚点已补可检索文本", "按创新政策执行、政策组合和组织机制调用"),
    "国际科技智库观点演变_IFP科技创新正式成果轻量总目录.csv": ("国际科技政策/智库观点演变/IFP轻量目录", "155项正式成果；17项已有本地资产，新增半导体任务型研发平台节点", "按科研组织、前沿技术和中国能力比较调用"),
    "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录.csv": ("国际科技政策/智库观点演变/ITIF轻量目录", "669项正式成果；新增ARPA-E技术转化组织机制全文", "按公共研发机构、能源技术创新和成果转化调用"),
    "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv": ("国际科技政策/智库观点演变/FAS轻量目录", "625项正式成果；28项已有本地资产，新增ARPA组织设计节点", "按高风险研发、项目经理制和研发组合管理调用"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv": ("国际科技政策/智库观点演变/JRC轻量目录", "3743项科技创新成果；58项已有本地资产，100项具有直接中国信号", "按科研体系、技术路线、使命政策和中国比较机制精选正文"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("国际科技政策/智库观点演变/实时进度", "10399条目录、2136条本地资产、8263条轻量保留、0条显式失败；中国关联目录748条、本地原文576条、可检索文本571条", "每次有界资料批次完成后重新生成"),
    "国际科技智库观点演变_机构采集进度.csv": ("国际科技政策/智库观点演变/实时进度", "各机构目录量、本地资产量和轻量保留量；JRC 58/3743、ITIF 58/670、OECD 51/453、Fraunhofer ISI 34/50、FAS 28/625、IFP 17/155", "用于项目启动时判断存量，不生成机械全文任务"),
    "国际科技智库观点演变_使命导向创新重大研发计划与组织机制定点增补台账.csv": ("国际科技政策/智库观点演变/使命导向创新与重大研发组织", "6项正式材料、3份官方PDF、3项官方网页正文、94页或网页和319662个清洗文本字符", "推进ARPA型机构、使命政策组合、任务评价和半导体研发平台机制编码"),
    "国际科技智库观点演变_使命导向创新重大研发计划与组织机制定点增补结果.md": ("国际科技政策/智库观点演变/使命导向创新与重大研发组织", "ITIF、FAS、Fraunhofer ISI、IFP、OECD和JRC使命导向研发组织证据", "按具体项目调用官方原始资产、全文文本和科技创新切片"),
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
        "文件数": "6913",
        "文档数": "5006",
        "PDF数": "1743",
        "表格数": "129",
        "最近30天活跃文件": "6913",
        "最新文件": "233_使命导向创新重大研发计划与组织机制定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科学技术创新覆盖单元；中国为横向维度；安全题名不自动触发全文",
        "覆盖状态": "10399条轻量总目录中2136条具有本地原始资产或官方网页转换资产；JRC 58/3743、ITIF 58/670、OECD 51/453、Fraunhofer ISI 34/50、FAS 28/625、IFP 17/155，显式失败为0",
        "推进动作": "推进使命导向创新、重大研发机构、任务评价和中国半导体研发平台机制编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
