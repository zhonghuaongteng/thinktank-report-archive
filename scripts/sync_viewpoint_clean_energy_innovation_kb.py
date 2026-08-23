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
    "170_ITIF正式报告与简报近十年轻量总目录.csv": "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录.csv",
    "174_FAS报告与政策备忘录近十年轻量总目录.csv": "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv",
    "186_欧委会JRC科技创新政策近十年轻量总目录.csv": "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv",
    "210_本地资料库实时进度看板.md": "国际科技智库观点演变_本地资料库实时进度看板.md",
    "211_机构采集进度.csv": "国际科技智库观点演变_机构采集进度.csv",
    "236_清洁能源技术路线创新政策与中国比较定点增补台账.csv": "国际科技智库观点演变_清洁能源技术路线创新政策与中国比较定点增补台账.csv",
    "237_清洁能源技术路线创新政策与中国比较定点增补结果.md": "国际科技智库观点演变_清洁能源技术路线创新政策与中国比较定点增补结果.md",
}

PURPOSES = {
    "国际科技智库观点演变_官方报告目录_2016-2026.csv": ("战略转向专报", "10399条正式报告目录；2142条已有本地资产，8257条轻量保留", "按具体科技创新问题触发增补"),
    "国际科技智库观点演变_OECD_STI正式系列轻量目录.csv": ("OECD STI轻量目录", "绿色氢能创新与产业政策全文节点已补", "按研发示范、标准和基础设施机制调用"),
    "国际科技智库观点演变_ITIF正式报告与简报近十年轻量总目录.csv": ("ITIF轻量目录", "新增清洁能源价格性能平价全文节点", "按研发示范和市场采用政策调用"),
    "国际科技智库观点演变_FAS报告与政策备忘录近十年轻量总目录.csv": ("FAS轻量目录", "新增DOE清洁能源项目设计全文节点", "按项目设计、验证和成果转化调用"),
    "国际科技智库观点演变_欧委会JRC科技创新政策近十年轻量总目录.csv": ("JRC轻量目录", "新增光伏、CCUS、核能三个技术状态和中国比较节点", "按技术路线、研发投入和中国位置调用"),
    "国际科技智库观点演变_清洁能源技术路线创新政策与中国比较定点增补台账.csv": ("清洁能源技术路线", "6份正式材料、307页或网页、746103个清洗文本字符", "推进绿色氢能、光伏、CCUS、核能及创新政策编码"),
    "国际科技智库观点演变_清洁能源技术路线创新政策与中国比较定点增补结果.md": ("清洁能源技术路线", "JRC、OECD、ITIF、FAS跨机构证据链及选择边界", "按具体能源技术项目调用"),
    "国际科技智库观点演变_本地资料库实时进度看板.md": ("实时进度", "10399条目录、2142条本地资产、8257条轻量保留、0条失败与0条真实队列", "每个有界批次完成后刷新"),
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
        "最新文件": "237_清洁能源技术路线创新政策与中国比较定点增补结果.md",
        "沉淀判断": "43个机构家族、1290个科技创新覆盖单元；新增绿色氢能、光伏、CCUS、核能及清洁能源研发政策证据链",
        "覆盖状态": "10399条目录中2142条具有本地资产、8257条轻量保留；中国关联目录748条、本地原文579条、可检索文本574条；显式失败0、真实队列0",
        "推进动作": "推进清洁能源技术路线、研发示范、价格性能平价、项目设计和中国能力比较编码；其他正文按项目问题触发",
    })
    write_csv(matrix_path, matrix, matrix_fields)
    print(f"copied={len(COPIES)} inventory_updated={len(PURPOSES)} matrix_updated=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
