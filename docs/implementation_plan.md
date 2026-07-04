# 国际科技智库抓取系统实施说明

## 运行边界

- GitHub目标仓库：`thinktank-report-archive`，建议保持私有。
- 本地知识库：`C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库`。
- 默认抓取批次：第一批，覆盖 RAND、CSET、ITIF、Stanford HAI、Carnegie、Brookings、CNAS、MERICS、OECD.AI。
- Gartner按商业研究处理，只保存元数据、公开摘要、链接和自有研判。

## 命令

只读评估：

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --batch 1 --limit 3
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
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli backfill --batch 1 --limit 200
```

## 输出

- `archive/<机构>/<年份>/`：一篇文章一份Markdown。
- `briefs/daily/<年份>/`：每日Markdown与HTML简报。
- `state/articles.sqlite`：URL去重与抓取状态。
- `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际智库抓取索引.csv`：知识库索引。
