from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path


COPIES = {
    "05_报告总目录.csv": "国际科技智库观点演变_官方报告目录_2016-2026.csv",
    "69_机构节点主题覆盖缺口矩阵.csv": "国际科技智库观点演变_机构节点主题覆盖缺口矩阵.csv",
    "70_定点补源优先队列.csv": "国际科技智库观点演变_定点补源优先队列.csv",
    "71_覆盖缺口结果.md": "国际科技智库观点演变_覆盖缺口结果.md",
    "72_轻量目录扩展优先队列.csv": "国际科技智库观点演变_轻量目录扩展优先队列.csv",
    "88_美国OSTP科学技术创新政策轻量目录.csv": "国际科技智库观点演变_美国OSTP科学技术创新政策轻量目录.csv",
    "198_英国皇家学会科学技术创新专题轻量总目录.csv": "国际科技智库观点演变_英国皇家学会科学技术创新专题轻量总目录.csv",
    "199_英国皇家学会科学技术创新专题轻量总目录结果.md": "国际科技智库观点演变_英国皇家学会科学技术创新专题轻量总目录结果.md",
    "206_NASEM科学技术创新政策近十年轻量总目录.csv": "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录.csv",
    "207_NASEM科学技术创新政策近十年轻量总目录结果.md": "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录结果.md",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "224_科学外交开放科研合作与中国参与机制定点增补台账.csv": "国际科技智库观点演变_科学外交开放科研合作与中国参与机制定点增补台账.csv",
    "225_科学外交开放科研合作与中国参与机制定点增补结果.md": "国际科技智库观点演变_科学外交开放科研合作与中国参与机制定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("国际科技政策/智库观点演变/战略转向专报", "10399条正式报告轻量总目录；2113条具有本地原始资产或官方网页转换资产，8286条轻量保留", "按科学技术创新与中国比较机制定点补充全文"),
    "国际科技智库观点演变_美国OSTP科学技术创新政策轻量目录.csv": ("国际科技政策/智库观点演变/OSTP轻量目录", "66项OSTP正式科技政策文件；科学外交与国际科技合作节点已有定点全文", "按联邦研发、开放科学、国际科技合作与中国参与机制调用"),
    "国际科技智库观点演变_英国皇家学会科学技术创新专题轻量总目录.csv": ("国际科技政策/智库观点演变/英国皇家学会轻量目录", "42项英国皇家学会科学技术创新成果；12项已有本地全文或官方全文转写", "按科学体系、科研人才、国际科学战略及中国合作机制调用"),
    "国际科技智库观点演变_英国皇家学会科学技术创新专题轻量总目录结果.md": ("国际科技政策/智库观点演变/英国皇家学会轻量目录", "42项正式成果，其中3项具有中国直接信号；记录科技创新专题范围与全文选择边界", "维护轻量目录，按科学体系和中国科研合作机制精选全文"),
    "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录.csv": ("国际科技政策/智库观点演变/NASEM轻量总目录", "253项NASEM科学技术创新政策成果；22项已有本地官方全文转写", "按科研制度、开放科学、数据基础设施、国际合作及中国比较机制调用"),
    "国际科技智库观点演变_NASEM科学技术创新政策近十年轻量总目录结果.md": ("国际科技政策/智库观点演变/NASEM轻量总目录", "253项成果的科技创新分层、范围边界及19项中国直接信号", "维护轻量目录，按科学体系与国际合作机制精选全文"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("国际科技政策/智库观点演变/实时进度", "10399条目录、2113条本地资产、8286条轻量保留、0条显式失败；中国关联目录743条、本地原文569条、可检索文本564条", "每次有界资料批次完成后重新生成"),
    "国际科技智库观点演变_机构采集进度.csv": ("国际科技政策/智库观点演变/实时进度", "各机构目录量、本地资产量和轻量保留量；NASEM为253/22/231，英国皇家学会为42/12/30，OSTP为67/10/57", "用于项目启动时判断存量，不生成机械全文任务"),
    "国际科技智库观点演变_科学外交开放科研合作与中国参与机制定点增补台账.csv": ("国际科技政策/智库观点演变/科学外交与开放科研合作", "5项正式材料、2份官方PDF、2项NASEM官方逐章网页全文、1项英国皇家学会官方PDF全文转写、57页或章、277367个清洗文本字符和33次中国词形命中", "推进科研数据开放、跨国科研基础设施、科学外交、国际科学战略及中国参与机制编码"),
    "国际科技智库观点演变_科学外交开放科研合作与中国参与机制定点增补结果.md": ("国际科技政策/智库观点演变/科学外交与开放科研合作", "OSTP、NASEM与英国皇家学会科学外交和国际科研合作定点增补结果及资产边界", "按具体项目调用官方PDF或章节、全文文本和科技创新切片"),
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
        "文件数": "6836",
        "文档数": "4949",
        "PDF数": "1727",
        "表格数": "125",
        "最近30天活跃文件": "6836",
        "最新文件": "225_科学外交开放科研合作与中国参与机制定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科学技术创新覆盖单元；中国为横向维度；安全题名不自动触发全文",
        "覆盖状态": "10399条轻量总目录中2113条具有本地原始资产或官方网页转换资产；NASEM为22/253、英国皇家学会为12/42、OSTP为10/67，显式失败为0",
        "推进动作": "推进科学外交、开放科研合作及中国参与机制编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
