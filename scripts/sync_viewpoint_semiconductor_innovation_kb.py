from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

try:
    from scripts.sync_viewpoint_clean_energy_innovation_kb import read_csv, write_csv
except ModuleNotFoundError:
    from sync_viewpoint_clean_energy_innovation_kb import read_csv, write_csv


COPIES = {
    "05_报告总目录.csv": "国际科技智库观点演变_官方报告目录_2016-2026.csv",
    "77_OECD_STI正式系列轻量目录.csv": "国际科技智库观点演变_OECD_STI正式系列轻量目录.csv",
    "88_美国OSTP科学技术创新政策轻量目录.csv": "国际科技智库观点演变_美国OSTP科学技术创新政策轻量目录.csv",
    "178_CSIS_RAI科技创新项目轻量总目录.csv": "国际科技智库观点演变_CSIS_RAI科技创新项目轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "202_acatech科学与技术创新正式成果轻量总目录.csv": "国际科技智库观点演变_acatech科学与技术创新正式成果轻量总目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "248_半导体微电子研发创新生态与中国比较定点增补台账.csv": "国际科技智库观点演变_半导体微电子研发创新生态与中国比较定点增补台账.csv",
    "249_半导体微电子研发创新生态与中国比较定点增补结果.md": "国际科技智库观点演变_半导体微电子研发创新生态与中国比较定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("战略转向专报", "10399条正式报告目录；2178条已有本地资产，8221条轻量保留", "按具体科技创新问题触发增补"),
    "国际科技智库观点演变_OECD_STI正式系列轻量目录.csv": ("OECD轻量目录", "新增半导体价值链结构、数据方法与中国位置全文节点", "按价值链测量和国际能力比较调用"),
    "国际科技智库观点演变_美国OSTP科学技术创新政策轻量目录.csv": ("OSTP轻量目录", "新增国家微电子研发战略全文节点", "按基础研究、科研设施、人才和成果转化调用"),
    "国际科技智库观点演变_CSIS_RAI科技创新项目轻量总目录.csv": ("CSIS RAI轻量目录", "新增imec预竞争协同研发平台正文", "按公共研发平台、中试设施和产业协作调用"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv": ("JRC轻量目录", "新增欧盟半导体价值链企业、贸易和所有权测量全文节点", "按半导体分工、能力位置和中国比较调用"),
    "国际科技智库观点演变_acatech科学与技术创新正式成果轻量总目录.csv": ("acatech轻量目录", "新增RISC-V与开源EDA、开放PDK两个全文节点", "按开放技术路线、工具链成熟度和人才生态调用"),
    "国际科技智库观点演变_半导体微电子研发创新生态与中国比较定点增补台账.csv": ("半导体与微电子", "6份正式材料、268页或网页、813418个清洗文本字符、175次中国词形命中", "推进基础研究、开放设计、协同研发平台和中国位置编码"),
    "国际科技智库观点演变_半导体微电子研发创新生态与中国比较定点增补结果.md": ("半导体与微电子", "JRC、acatech、OSTP、CSIS RAI与OECD的2022—2025技术创新机制链及选择边界", "按具体半导体研发、设计工具、科研设施和价值链问题调用"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("实时进度", "10399条目录、2178条本地资产、8221条轻量保留、0条失败与0条真实队列", "每个有界批次完成后刷新"),
    "国际科技智库观点演变_机构采集进度.csv": ("实时进度", "按机构记录目录、本地资产和轻量保留量", "用于判断存量，禁止机械全量下载"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, type=Path)
    parser.add_argument("--kb", required=True, type=Path)
    args = parser.parse_args()
    root, kb = args.research.resolve(), args.kb.resolve()
    asset_dir = kb / "06_数据资产"
    for source_name, kb_name in COPIES.items():
        shutil.copy2(root / source_name, asset_dir / kb_name)

    inventory_path = asset_dir / "数据资产清单.csv"
    inventory, fields = read_csv(inventory_path)
    by_name = {row.get("数据文件", ""): row for row in inventory if row.get("项目") == "国际主要科技智库观点演变研究"}
    for kb_name, (kind, purpose, next_step) in PURPOSES.items():
        target = asset_dir / kb_name
        row = by_name.get(kb_name)
        if row is None:
            row = {field: "" for field in fields}
            inventory.append(row)
        stat = target.stat()
        row.update({
            "项目": "国际主要科技智库观点演变研究",
            "项目类型": f"国际科技政策/智库观点演变/{kind}",
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
        "最新文件": "249_半导体微电子研发创新生态与中国比较定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科技创新覆盖单元；新增半导体价值链测量、RISC-V、开源EDA、微电子国家研发战略和imec协同研发平台证据链",
        "覆盖状态": "10399条目录中2178条具有本地资产、8221条轻量保留；中国关联目录748条、本地原文579条、可检索文本574条；显式失败0、真实队列0",
        "推进动作": "推进半导体基础研究、开放设计工具、共享科研设施、预竞争研发平台、人才与中国价值链位置编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
