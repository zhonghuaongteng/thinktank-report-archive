# 国际科技智库抓取系统实施说明

## 运行边界

- GitHub目标仓库：`thinktank-report-archive`，建议保持私有。
- 本地知识库：`C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库`。
- 默认抓取批次：第一批，覆盖 RAND、CSET、ITIF、Stanford HAI、Carnegie、Brookings、CNAS、MERICS、OECD.AI。
- 历史回填默认只追溯近三年；无可核验发布日期、早于回填窗口或晚于运行日的候选不进入归档。
- Gartner按商业研究处理，只保存元数据、公开摘要、链接和自有研判。
- “中国/上海相关”作为背景信号处理；只有同时命中科技创新、AI治理、半导体、先进制造、数字经济、科技治理或科技人才等实质主题，才进入P0/P1重点队列。单独涉华外交、活动或一般政策页面最高保留为P2索引。

## 命令

只读评估：

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --batch 1 --limit 3
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --institution carnegie-tech --limit 30 --backfill --lookback-years 3 --unseen-only
```

机构健康审计：

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli audit --batch 1 --limit 5
```

每日抓取：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_daily.ps1 -Batch 1 -Limit 20
```

首次回溯：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backfill_batch.ps1 -Batch 1 -Limit 5 -MinPriority P1 -WriteLimit 8 -LookbackYears 3
```

## 输出

- `archive/<机构>/<年份>/`：一篇文章一份Markdown，进入私有GitHub仓库。
- `briefs/daily/<年份>/`：每日Markdown、HTML与PDF简报，进入私有GitHub仓库。
- `state/articles.sqlite`：URL去重与抓取状态。
- `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际智库抓取索引.csv`：知识库索引。

## 质量控制

- 候选源URL默认限制在机构自有域名或子域名内；外部媒体链接只作为正文或PDF线索，不作为独立归档源。
- 活动、人物、播客、视频、网络研讨会和公告型页面在评分前过滤。
- 对只有PDF但页面缺日期的报告，使用PDF `Last-Modified` 作为日期兜底，并在后续人工复核中保留修正空间。
- 对全站 sitemap 较宽的机构，可配置 `sitemap_include_keywords`，先按URL技术主题词收窄，再进入评分。
