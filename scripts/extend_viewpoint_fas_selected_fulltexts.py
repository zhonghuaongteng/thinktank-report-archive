from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

try:
    from scripts.extend_viewpoint_fas_light_catalog import CATALOG_FIELDS, _browser_json, report_id
except ModuleNotFoundError:
    from extend_viewpoint_fas_light_catalog import CATALOG_FIELDS, _browser_json, report_id


SERIES_ROLE = "FAS科技创新机制与中国比较跨期精选全文"


def _item(published: str, wp_id: int, landing: str, title: str, axes: tuple[str, ...], role: str, china: bool = False) -> dict[str, object]:
    slug = landing.rstrip("/").split("/")[-1]
    return {
        "id": report_id(published, slug), "date": published, "wp_id": wp_id, "title": title,
        "landing": landing, "api_url": f"https://fas.org/wp-json/wp/v2/publications/{wp_id}?_fields=id,date,slug,link,title,content,excerpt,publication-type",
        "axes": axes, "role": role, "china": china,
    }


SELECTED_ITEMS = (
    _item("2020-04-23", 17155, "https://fas.org/publication/closing-critical-gaps/", "Closing Critical Gaps from Lab to Market", ("科技人才与科研职业", "技术创新与产业转化"), "博士后、早期创业者与科技投资者共同跨越实验室到市场缺口"),
    _item("2020-04-25", 17145, "https://fas.org/publication/ambitious-achievable-and-sustainable/", "Ambitious, Achievable, and Sustainable: A Blueprint for Reclaiming American Research Leadership", ("科学体系与基础研究", "研发治理与科研组织"), "以GDP占比和学科结构重建联邦基础与应用研究投入"),
    _item("2020-09-24", 17109, "https://fas.org/publication/focused-research-organizations-to-accelerate-science-technology-and-medicine/", "Focused Research Organizations to Accelerate Science, Technology, and Medicine", ("研发治理与科研组织", "技术创新与产业转化"), "用聚焦研究组织填补学术项目和企业研发之间的组织空档"),
    _item("2020-12-09", 17023, "https://fas.org/publication/a-convergence-directorate-at-the-national-science-foundation/", "A Convergence Directorate at the National Science Foundation", ("科学体系与基础研究", "研发治理与科研组织"), "NSF跨学科会聚研究与多部门伙伴关系的组织设计"),
    _item("2021-01-26", 16955, "https://fas.org/publication/creating-a-national-deeptech-capital-fund/", "Creating a National DeepTech Capital Fund", ("关键与通用技术", "技术创新与产业转化"), "以政府耐心资本弥补深科技市场化资金缺口", True),
    _item("2021-03-04", 16917, "https://fas.org/publication/forging-1-000-venture-scientists-to-transform-the-innovation-economy/", "Forging 1,000 Venture Scientists to Transform the Innovation Economy", ("科技人才与科研职业", "技术创新与产业转化"), "创业科学家培养、区域创新与中国产业竞争比较", True),
    _item("2021-09-30", 4675, "https://fas.org/publication/industrial-policy-memo/", "Industrial Policy Memo", ("研发治理与科研组织", "技术创新与产业转化"), "产业政策复兴、公共能力与先进产业投资框架"),
    _item("2022-02-04", 17169, "https://fas.org/publication/improving-research-funding-efficiencies-and-proposal-diversity-through-nsf-science-lottery-grants/", "Piloting and Evaluating NSF Science Lottery Grants: A Roadmap to Improving Research Funding Efficiencies and Proposal Diversity", ("科学体系与基础研究", "研发治理与科研组织"), "科研资助同行评议、部分随机化与提案多样性实验"),
    _item("2022-06-01", 17216, "https://fas.org/publication/expanding-pathways-for-career-research-scientists-in-academia/", "Expanding Pathways for Career Research Scientists in Academia", ("科学体系与基础研究", "科技人才与科研职业"), "学术科研职业分工与非PI研究人员制度"),
    _item("2022-10-12", 17225, "https://fas.org/publication/unlocking-federal-grant-data-to-inform-evidence-based-science-funding/", "Unlocking Federal Grant Data To Inform Evidence-Based Science Funding", ("科学体系与基础研究", "研发治理与科研组织"), "开放联邦资助数据以支持元科学和循证科研政策"),
    _item("2023-01-12", 4677, "https://fas.org/publication/118th-congress/", "Science and Innovation in the 118th Congress", ("科学体系与基础研究", "研发治理与科研组织"), "国会科学创新议程、科研投入与创新制度组合"),
    _item("2023-01-12", 4678, "https://fas.org/publication/118th-congress-emerging-tech-competitiveness/", "118th Congress: Emerging Tech & Competitiveness", ("关键与通用技术", "技术创新与产业转化"), "先进技术、产业竞争力与中国科技竞争议程", True),
    _item("2023-06-06", 22228, "https://fas.org/publication/applying-arpa-i-a-proven-model-for-transportation-infrastructure/", "Applying ARPA-I: A Proven Model for Transportation Infrastructure", ("研发治理与科研组织", "技术创新与产业转化"), "把ARPA型高风险研发机制移植到交通基础设施"),
    _item("2024-03-18", 28975, "https://fas.org/publication/predicting-progress-utility-forecasting/", "Predicting Progress: A Pilot of Expected Utility Forecasting in Science Funding", ("科学体系与基础研究", "研发治理与科研组织"), "以预期效用预测改善科研资助决策"),
    _item("2024-07-16", 31722, "https://fas.org/publication/agency-perspectives-bioeconomy/", "Understanding the U.S. Bioeconomy: Agency Perspectives", ("关键与通用技术", "研发治理与科研组织"), "跨部门生物经济定义、任务分工与政策协调"),
    _item("2024-12-09", 34583, "https://fas.org/publication/micro-arpa/", "Micro-ARPAs: Enhancing Scientific Innovation Through Small Grant Programs", ("科学体系与基础研究", "研发治理与科研组织"), "小额快速拨款与分布式ARPA式科学创新"),
    _item("2024-12-16", 34761, "https://fas.org/publication/creating-a-science-and-technology-hub-in-congress/", "Creating a Science and Technology Hub in Congress", ("研发治理与科研组织", "科技人才与科研职业"), "增强立法机构科技评估和科学政策能力"),
    _item("2025-02-06", 35848, "https://fas.org/publication/contain-china-on-legacy-chips/", "Taking on the World’s Factory: A Path to Contain China on Legacy Chips", ("关键与通用技术", "技术创新与产业转化"), "成熟制程芯片产能、产业政策与中国制造竞争", True),
    _item("2025-07-02", 38266, "https://fas.org/publication/fueling-the-bioeconomy-clean-energy/", "Fueling the Bioeconomy: Clean Energy Policies Driving Biotechnology Innovation", ("关键与通用技术", "技术创新与产业转化"), "清洁能源政策如何形成生物技术创新需求和市场"),
    _item("2025-07-07", 38282, "https://fas.org/publication/measuring-research-bureaucracy/", "Measuring Research Bureaucracy to Boost Scientific Efficiency and Innovation", ("科学体系与基础研究", "研发治理与科研组织"), "测量行政负担并提高科研人员有效研究时间"),
    _item("2025-07-09", 38303, "https://fas.org/publication/rebuild-corporate-research/", "Rebuild Corporate Research for a Stronger American Future", ("科学体系与基础研究", "技术创新与产业转化"), "企业研究实验室衰退与长期产业创新能力重建"),
    _item("2025-07-23", 38563, "https://fas.org/publication/national-institute-for-high-reward-research/", "A National Institute for High-Reward Research", ("科学体系与基础研究", "研发治理与科研组织"), "高风险高回报研究的专门资助机构设计"),
    _item("2026-02-05", 41156, "https://fas.org/publication/national-ai-laboratory-at-commerce/", "A National AI Laboratory to Support the Administration’s AI Agenda at the Department of Commerce", ("关键与通用技术", "研发治理与科研组织"), "国家AI实验室、算力数据基础设施与公共任务"),
    _item("2026-04-13", 42094, "https://fas.org/publication/sustaining-scientific-collections-in-the-age-of-ai/", "Sustaining Scientific Collections in the Age of AI", ("科学体系与基础研究", "关键与通用技术"), "科学标本与数据基础设施在AI科研中的再定位"),
    _item("2026-04-23", 42214, "https://fas.org/publication/revitalizing-us-auto-industry/", "A Plan for Revitalizing the U.S. Auto Industry", ("关键与通用技术", "技术创新与产业转化"), "汽车技术、制造能力与中国竞争压力", True),
    _item("2026-06-26", 46393, "https://fas.org/publication/roi-of-rd/", "Research Agenda: Estimating the U.S. Government’s Return-on-Investment on Scientific Research & Development", ("科学体系与基础研究", "研发治理与科研组织"), "政府科学R&D回报率的估计框架与研究议程"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def clean_html(source: str) -> str:
    soup = BeautifulSoup(source, "html.parser")
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(part.strip() for part in soup.stripped_strings if part.strip())).strip() + "\n"


def selected_slice(item: dict[str, object], text: str) -> str:
    keywords = ("science", "research", "innovation", "r&d", "technology", "scientist", "funding", "commercial", "industry", "china", "chinese", "talent", "workforce", "laboratory")
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if len(part.strip()) >= 70]
    hits = [part for part in paragraphs if any(word in part.lower() for word in keywords)][:140]
    return (
        f"# {item['title']}\n\n- 报告ID：{item['id']}\n- 官方页面：{item['landing']}\n"
        f"- 科技创新复用角色：{item['role']}\n- 主轴：{'；'.join(item['axes'])}\n\n"
        "## 科技创新与中国定向摘录\n\n" + "\n\n".join(hits) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Save a selective FAS science and technology innovation full-text layer from the official WordPress API.")
    parser.add_argument("--research", required=True, type=Path)
    args = parser.parse_args()
    root = args.research.resolve()
    web_dir = root / "03_证据底稿" / "网页原文"
    text_dir = root / "03_证据底稿" / "文本"
    slice_dir = root / "03_证据底稿" / "切片"
    for directory in (web_dir, text_dir, slice_dir):
        directory.mkdir(parents=True, exist_ok=True)
    catalog_path = root / "05_报告总目录.csv"
    light_path = root / "174_FAS报告与政策备忘录近十年轻量总目录.csv"
    catalog = read_csv(catalog_path)
    light = read_csv(light_path)
    by_id = {row["报告ID"]: row for row in catalog}
    light_by_id = {row["报告ID"]: row for row in light}
    missing = {str(item["id"]) for item in SELECTED_ITEMS} - set(by_id)
    if missing:
        raise RuntimeError(f"selected FAS items missing from light catalog: {sorted(missing)}")
    ledger: list[dict[str, str]] = []
    for item in SELECTED_ITEMS:
        rid = str(item["id"])
        asset_path = web_dir / f"{rid}.html"
        text_path = text_dir / f"{rid}.txt"
        slice_path = slice_dir / f"{rid}.md"
        if asset_path.exists():
            content_html = asset_path.read_text(encoding="utf-8", errors="replace")
        else:
            payload, _ = _browser_json(str(item["api_url"]))
            if not isinstance(payload, dict) or int(payload.get("id", 0)) != int(item["wp_id"]):
                raise RuntimeError(f"unexpected FAS API record: {rid}")
            content = payload.get("content") or {}
            content_html = str(content.get("rendered", "")) if isinstance(content, dict) else str(content)
        text = clean_html(content_html)
        if len(text) < 300:
            raise RuntimeError(f"official FAS publication text too short: {rid} {len(text)}")
        if not asset_path.exists():
            asset_path.write_text(content_html, encoding="utf-8", newline="\n")
        text_path.write_text(text, encoding="utf-8", newline="\n")
        slice_path.write_text(selected_slice(item, text), encoding="utf-8", newline="\n")
        payload_bytes = content_html.encode("utf-8")
        lower = text.lower()
        china_hits = lower.count("china") + lower.count("chinese") + lower.count("prc")
        row = by_id[rid]
        row["本地路径"] = str(text_path)
        row["正文完整度"] = "FAS官方WordPress页面正文已保存；早期迁移页面按官网现存正文边界使用"
        row["优先级"] = "P0-China-STI-node" if item["china"] else "P1-STI-node"
        row["样本角色"] = SERIES_ROLE
        row["编码状态"] = "全文待观点编码"
        row["预期用途"] = str(item["role"])
        row["本地原始资产路径"] = str(asset_path)
        row["原始资产状态"] = "FAS官方WordPress正文原始资产已获取；已生成清洗文本与科技创新定向切片"
        light_by_id[rid]["中国直接信号"] = "是" if item["china"] else light_by_id[rid]["中国直接信号"]
        light_by_id[rid]["全文策略"] = "已进入精选全文；按本地官方HTML正文、清洗文本和切片调用"
        ledger.append({
            "报告ID": rid, "发布日期": str(item["date"]), "报告名称": str(item["title"]),
            "WordPress记录ID": str(item["wp_id"]), "官方落地页": str(item["landing"]), "官方API入口": str(item["api_url"]),
            "本地原始资产": str(asset_path), "本地文本": str(text_path), "本地切片": str(slice_path),
            "字节数": str(len(payload_bytes)), "字符数": str(len(content_html)), "清洗文本字符数": str(len(text)),
            "China词形命中数": str(china_hits), "SHA256": hashlib.sha256(payload_bytes).hexdigest(),
            "中国直接信号": "是" if item["china"] else "否", "科技创新主轴": "；".join(item["axes"]),
            "科技创新复用角色": str(item["role"]), "选择理由": "跨期节点；直接解释科学、技术与创新机制；安全议题仅在改变创新能力时纳入",
            "获取日期": date.today().isoformat(),
        })
    selected_ids = {str(item["id"]) for item in SELECTED_ITEMS}
    marker = "FAS跨期精选已完成；其余报告与政策备忘录保留轻量目录"
    for row in catalog:
        if row.get("机构ID") == "fas" and row.get("报告ID") not in selected_ids and not row.get("本地原始资产路径"):
            if marker not in row.get("原始资产状态", ""):
                row["原始资产状态"] = (row.get("原始资产状态", "").rstrip("；") + "；" + marker).lstrip("；")
    catalog.sort(key=lambda row: (row["发布日期"], row["报告ID"]))
    write_csv(catalog_path, catalog, CATALOG_FIELDS)
    write_csv(light_path, light, list(light[0]))
    write_csv(root / "176_FAS科技创新机制与中国比较跨期精选全文台账.csv", ledger, list(ledger[0]))
    totals = {
        "bytes": sum(int(row["字节数"]) for row in ledger), "chars": sum(int(row["字符数"]) for row in ledger),
        "text_chars": sum(int(row["清洗文本字符数"]) for row in ledger),
        "china": sum(int(row["China词形命中数"]) for row in ledger), "direct": sum(row["中国直接信号"] == "是" for row in ledger),
    }
    (root / "177_FAS科技创新机制与中国比较跨期精选全文结果.md").write_text(
        "# FAS科技创新机制与中国比较跨期精选全文结果\n\n"
        f"- 从625项正式出版轻量目录中选择{len(ledger)}项，保存FAS官方WordPress正文、清洗文本和科技创新切片，共{totals['bytes']:,}字节、{totals['text_chars']:,}个清洗文本字符。\n"
        f"- 直接中国比较节点{totals['direct']}项，全文China/Chinese/PRC词形命中{totals['china']}次；中国维度限于深科技资本、创业科学家、先进技术竞争、芯片制造和汽车产业创新。\n"
        "- 跨期机制覆盖科研投入、聚焦研究组织、NSF会聚研究、深科技资本、科研职业、资助试验、ARPA型机构、立法科技能力、生物经济、企业研究、国家AI实验室和R&D回报评价。\n"
        "- 核武、导弹、军控和一般国家安全报告未进入精选；相关题名与摘要继续保留于轻量目录。\n"
        "- 2020—2021年部分迁移页面仅保留官网现存正文，台账按实际字符数界定证据边界，不补写缺失内容。\n",
        encoding="utf-8",
    )
    print(f"assets={len(ledger)} bytes={totals['bytes']} chars={totals['chars']} text_chars={totals['text_chars']} direct_china={totals['direct']} china_hits={totals['china']} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
