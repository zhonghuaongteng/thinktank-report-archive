import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.build_viewpoint_collection_progress import build_progress, render_markdown


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class ViewpointCollectionProgressTests(unittest.TestCase):
    def test_progress_separates_light_catalog_from_true_backlog(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            write_csv(
                root / "05_报告总目录.csv",
                ["报告ID", "机构英文名", "本地原始资产路径", "原始资产状态"],
                [
                    {"报告ID": "A", "机构英文名": "Alpha", "本地原始资产路径": "a.pdf", "原始资产状态": "官方PDF已保存"},
                    {"报告ID": "B", "机构英文名": "Alpha", "本地原始资产路径": "", "原始资产状态": "精选已完成；其余保留轻量目录"},
                    {"报告ID": "C", "机构英文名": "Beta", "本地原始资产路径": "", "原始资产状态": "获取失败"},
                ],
            )
            write_csv(root / "70_定点补源优先队列.csv", ["报告ID"], [])
            write_csv(root / "72_轻量目录扩展优先队列.csv", ["机构ID"], [])

            progress = build_progress(root)

            self.assertEqual(progress["catalog_total"], 3)
            self.assertEqual(progress["local_assets"], 1)
            self.assertEqual(progress["light_only"], 2)
            self.assertEqual(progress["explicit_failures"], 1)
            self.assertEqual(progress["fulltext_queue"], 0)
            self.assertEqual(progress["catalog_queue"], 0)
            self.assertEqual(progress["institutions"][0], {"institution": "Alpha", "catalog": 2, "local_assets": 1, "light_only": 1})

    def test_markdown_states_that_asset_density_is_not_completion_rate(self):
        progress = {
            "catalog_total": 10,
            "local_assets": 2,
            "light_only": 8,
            "explicit_failures": 0,
            "fulltext_queue": 0,
            "catalog_queue": 0,
            "institutions": [],
        }
        output = render_markdown(progress, "2026-08-23 10:00:00")
        self.assertIn("资产密度：20.00%", output)
        self.assertIn("不等同于任务完成率", output)
        self.assertIn("真实待补队列：0", output)


if __name__ == "__main__":
    unittest.main()
