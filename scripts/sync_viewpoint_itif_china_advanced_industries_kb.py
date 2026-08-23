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
    "79_ITIF中国先进产业创新系列轻量目录.csv": "国际科技智库观点演变_ITIF中国先进产业创新系列轻量目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "234_ITIF中国先进产业技术创新能力精选全文台账.csv": "国际科技智库观点演变_ITIF中国先进产业技术创新能力精选全文台账.csv",
    "235_ITIF中国先进产业技术创新能力精选全文结果.md": "国际科技智库观点演变_ITIF中国先进产业技术创新能力精选全文结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("战略转向专报", "10399条正式报告目录；2136条已有本地资产，8263条轻量保留", "按具体科技创新问题触发增补"),
    "国际科技智库观点演变_ITIF中国先进产业创新系列轻量目录.csv": ("ITIF中国先进产业", "10份正式报告均已有官方PDF；6份增加官方Markdown和切片", "按技术领域与跨行业比较调用"),
    "国际科技智库观点演变_ITIF中国先进产业技术创新能力精选全文台账.csv": ("ITIF中国先进产业", "复核10份PDF完整性并记录6份网页正文增强资产", "推进机器人、电池、生物技术、半导体、量子及综合比较编码"),
    "国际科技智库观点演变_ITIF中国先进产业技术创新能力精选全文结果.md": ("ITIF中国先进产业", "本系列未抓取全文为0；区分已有PDF与新增检索格式", "不再扩展抓取，按项目问题调用"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("实时进度", "10399条目录、2136条本地资产、8263条轻量保留、0条失败与0条真实队列", "每个有界批次完成后刷新"),
    "国际科技智库观点演变_机构采集进度.csv": ("实时进度", "按机构记录目录、本地资产和轻量保留量", "用于判断存量，禁止机械全量下载"),
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
        "最新文件": "235_ITIF中国先进产业技术创新能力精选全文结果.md",
        "沉淀判断": "43个机构家族、1290个科技创新覆盖单元；ITIF中国先进产业系列10份官方PDF齐备，6份另有网页正文增强",
        "覆盖状态": "10399条目录中2136条具有本地资产、8263条轻量保留；显式失败0、真实队列0",
        "推进动作": "停止该系列追加抓取；按机器人、电池、生物技术、半导体、量子及跨行业比较问题调用和编码",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
