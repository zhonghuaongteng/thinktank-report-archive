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
    "174_FAS报告与政策备忘录近十年轻量总目录.csv": "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "202_acatech科学与技术创新正式成果轻量总目录.csv": "国际科技智库观点演变_acatech科学与技术创新正式成果轻量总目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "238_生物技术生物制造创新机制与中国比较定点增补台账.csv": "国际科技智库观点演变_生物技术生物制造创新机制与中国比较定点增补台账.csv",
    "239_生物技术生物制造创新机制与中国比较定点增补结果.md": "国际科技智库观点演变_生物技术生物制造创新机制与中国比较定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("战略转向专报", "10399条正式报告目录；2148条已有本地资产，8251条轻量保留", "按具体科技创新问题触发增补"),
    "国际科技智库观点演变_OECD_STI正式系列轻量目录.csv": ("OECD STI轻量目录", "新增2019生物经济创新生态和2025合成生物学全文节点", "按创新生态、技术融合和研发政策调用"),
    "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv": ("FAS轻量目录", "新增2020生物制造倡议和2023放大测试设施网络正文", "按制造创新机构、设施和转化机制调用"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv": ("JRC轻量目录", "新增工业生物技术专利格局和中国比较节点", "按技术热点、创新主体和中国位置调用"),
    "国际科技智库观点演变_acatech科学与技术创新正式成果轻量总目录.csv": ("acatech轻量目录", "新增2017生物技术创新潜力早期节点", "按组学、基因编辑和产业转化调用"),
    "国际科技智库观点演变_生物技术生物制造创新机制与中国比较定点增补台账.csv": ("生物技术与生物制造", "6份正式材料、266页或网页、792685个清洗文本字符", "推进技术融合、制造放大、专利格局和中国能力比较编码"),
    "国际科技智库观点演变_生物技术生物制造创新机制与中国比较定点增补结果.md": ("生物技术与生物制造", "acatech、OECD、FAS、JRC的2017—2025跨期证据链及选择边界", "按具体生物技术与生物制造问题调用"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("实时进度", "10399条目录、2148条本地资产、8251条轻量保留、0条失败与0条真实队列", "每个有界批次完成后刷新"),
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
        "最新文件": "239_生物技术生物制造创新机制与中国比较定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科技创新覆盖单元；新增生物技术关键能力、生物经济创新生态、生物制造组织、试验设施、工业生物技术专利及合成生物学证据链",
        "覆盖状态": "10399条目录中2148条具有本地资产、8251条轻量保留；中国关联目录748条、本地原文579条、可检索文本574条；显式失败0、真实队列0",
        "推进动作": "推进生物技术路线、生物制造放大、创新生态、专利格局和中国能力比较编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
