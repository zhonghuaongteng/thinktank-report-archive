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
    "170_ITIF正式报告与简报近十年轻量总目录.csv": "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv": "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv",
    "182_欧洲议会STOA科技评估近十年轻量总目录.csv": "国际科技智库观点演变_欧洲议会STOA科技评估近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "244_先进核能聚变技术创新与中国比较定点增补台账.csv": "国际科技智库观点演变_先进核能聚变技术创新与中国比较定点增补台账.csv",
    "245_先进核能聚变技术创新与中国比较定点增补结果.md": "国际科技智库观点演变_先进核能聚变技术创新与中国比较定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("战略转向专报", "10399条正式报告目录；2166条已有本地资产，8233条轻量保留", "按具体科技创新问题触发增补"),
    "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录.csv": ("ITIF轻量目录", "新增SMR成本、性能、示范和规模制造全文节点", "按先进核能商业化和中国比较调用"),
    "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv": ("FAS轻量目录", "新增聚变氚燃料公共生产能力正文", "按聚变工程瓶颈和商业示范调用"),
    "国际科技智库观点演变_欧洲议会STOA科技评估近十年轻量总目录.csv": ("STOA轻量目录", "新增聚变技术路线、工程里程碑和商业化条件报告", "按欧洲聚变前瞻和中国比较调用"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv": ("JRC轻量目录", "新增先进核材料、熔盐堆标准和SMR生态3个全文节点", "按研发议程、标准化和创新生态调用"),
    "国际科技智库观点演变_先进核能聚变技术创新与中国比较定点增补台账.csv": ("先进核能与聚变", "6份正式材料、273页或网页、697186个清洗文本字符、73次中国词形命中", "推进先进核材料、反应堆、聚变工程和中国比较编码"),
    "国际科技智库观点演变_先进核能聚变技术创新与中国比较定点增补结果.md": ("先进核能与聚变", "JRC、FAS、ITIF和STOA的2019—2025技术创新机制链及选择边界", "按具体先进核能、聚变技术和创新生态问题调用"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("实时进度", "10399条目录、2166条本地资产、8233条轻量保留、0条失败与0条真实队列", "每个有界批次完成后刷新"),
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
            "项目": "国际主要科技智库观点演变研究", "项目类型": f"国际科技政策/智库观点演变/{kind}",
            "数据文件": kb_name, "相对路径": f"06_数据资产\\{kb_name}", "原始路径": str(target),
            "格式": target.suffix, "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime("%Y/%m/%d %H:%M:%S"),
            "大小MB": f"{stat.st_size / 1024 / 1024:.2f}", "研究用途": purpose, "下一步": next_step,
        })
    write_csv(inventory_path, inventory, fields)

    matrix_path = kb / "09_覆盖核验" / "项目覆盖矩阵.csv"
    matrix, matrix_fields = read_csv(matrix_path)
    row = next(item for item in matrix if item.get("项目") == "国际主要科技智库观点演变研究")
    row.update({
        "最新文件": "245_先进核能聚变技术创新与中国比较定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科技创新覆盖单元；新增先进核材料、熔盐堆标准化、SMR创新生态、聚变氚燃料和商业化条件证据链",
        "覆盖状态": "10399条目录中2166条具有本地资产、8233条轻量保留；中国关联目录748条、本地原文579条、可检索文本574条；显式失败0、真实队列0",
        "推进动作": "推进研发议程、科研共同体参与标准、反应堆创新生态、聚变工程瓶颈和中国比较编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
