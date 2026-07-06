# 多agent团队执行协议

## 适用目标

本协议用于国际科技智库历史回填、来源接入优化和周报质量复核。目标是把“来源发现、规则诊断、写入归档、质量审计”拆开，降低单一上下文承载压力，并避免多个执行者同时写入同一状态资产。

## 角色分工

### 主控agent

- 读取知识库入口、项目审计、当前 Git 状态和用户最新约束。
- 分配只读评估任务，决定是否接纳评估结论。
- 独占写入以下资产：`archive/`、`state/articles.sqlite`、研究知识库 CSV、`briefs/`、配置文件、测试文件和 Git 提交。
- 负责最终质量闸门、提交、推送和长期记忆记录。

### 来源评估agent

- 只读评估一个机构或一组互不相关机构。
- 使用 `evaluate`、配置文件、覆盖审计和网页字段证据判断候选质量。
- 不修改文件，不运行 `backfill`，不写知识库，不提交。
- 输出结构化评估表：入口、候选、字段完整度、误报风险、版权边界、建议写入数量、必要规则改动。

### 写入worker

- 仅在主控明确授权时使用。
- 每次只负责一个机构或一个互斥批次。
- 不与其他写入worker并发写 `state/articles.sqlite` 或知识库 CSV。
- 写入后必须返回新增文件、状态变化、知识库行数和异常记录。

### 质量审计agent

- 在主控完成写入后只读复核。
- 检查重复 URL、中文题名、H1、frontmatter、状态库坏路径、知识库索引、周报图片和测试覆盖。
- 不直接修复；发现问题后交回主控或指定写入worker处理。

## 执行节奏

1. 主控读取 `docs/backfill_coverage_audit.md` 和最新用户约束，选择零覆盖或低覆盖源。
2. 主控并行派发 2-4 个来源评估agent。每个 agent 的机构集合应互不重叠。
3. 主控在等待评估期间处理非重叠任务：文档、脚本、测试、已有规则审阅。
4. 主控汇总评估结果，只选择字段完整、日期可靠、版权边界可控、去重状态清楚的候选。
5. 写入阶段串行执行。一次只运行一个 `backfill`，并保留 `--write-limit`。
6. 写入后重建周报和覆盖审计，再运行质量闸门。
7. 提交前检查工作区差异，确认没有无关文件或状态库误入仓库。

## 机构租约

- 任何写入前，主控必须明确当前机构租约：一次只允许一个机构或一个互斥批次进入写入阶段。
- 租约期间不得启动第二个写入worker，也不得手动运行另一个 `backfill`。
- 来源评估agent不需要租约，因为其任务只读。
- 租约结束条件是：新增归档、SQLite、知识库 CSV、周报和质量闸门均已核验，或写入失败并完成一致性修复。

## 来源评估交接模板

```text
机构：
当前归档数：
只读命令：
候选结果：
- 标题｜日期｜优先级｜主题｜PDF/详情状态｜是否未归档
字段完整度：
误报风险：
版权边界：
建议：
需要主控修改：
```

## 主控写入命令模板

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli backfill `
  --institution <slug> `
  --limit 10 `
  --lookback-years 3 `
  --min-priority P1 `
  --write-limit 4 `
  --brief-cadence weekly `
  --search-profile broad_innovation_support
```

写入前必须确认该机构的评估结果中有未归档候选。默认不使用 `--refresh`；只有在主控确认是在修复已有错误记录、重取同一 URL 或刷新已知字段时才可使用。写入后必须核验 `candidates_written`、新增 Markdown、知识库 CSV 行、SQLite 归档路径和周报候选数。

## 只读评估命令模板

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_evaluate_sources.ps1 `
  -Institutions bruegel,ecipe,nistep `
  -Limit 10 `
  -LookbackYears 3 `
  -UnarchivedOnly
```

该脚本只调用 `evaluate`，不得替代写入流程。`evaluate` 不支持 `--min-priority`；评估agent应在输出表中标记 P0/P1/P2/P3，并由主控决定后续 `backfill --min-priority`。

`-UnseenOnly` 只保留状态库从未见过的 URL；`-UnarchivedOnly` 还会保留此前已记录失败但没有 `archive_path` 的 URL，适合 ECIPE 这类旧失败记录的修复前评估。

## 质量闸门

- `python -m unittest discover -s tests -v` 通过。
- `git diff --check -- . ':!briefs/**/*.pdf' ':!briefs/daily/**/*.pdf' ':!briefs/weekly/**/*.pdf'` 无空白错误。
- `archive/` 所有 Markdown 可由 `parse_archive_markdown` 解析。
- 归档重复 URL 为 0。
- 中文题名不得与英文题名完全相同。
- H1 与 frontmatter `chinese_title` 一致。
- SQLite 中所有非空 `archive_path` 均存在。
- 知识库索引新增行包含中文题名、英文题名、发布日期、原始链接、PDF链接、翻译层级、版权边界和抓取状态。
- 周报 Markdown/HTML/PDF 同步更新；如有漫画导读，PDF 前三页至少检测到图片对象。

## 禁止事项

- 不得让多个 agent 并发写 `state/articles.sqlite`。
- 不得让评估agent运行 `backfill` 或修改配置。
- 不得把 `--refresh` 当作常规回填参数。
- 不得为扩大数量降低全局 P1 阈值。
- 不得把 Gartner 等商业研究源纳入全文抓取。
- 不得把中文摘要中的“上海参考”反向作为原文涉沪信号重新评分。
- 不得用 sitemap `lastmod` 替代详情页发布日期。
- 不得在未做只读评估时对零覆盖源直接回填。

## 失败处理

- 403、超时、PDF不可访问、外部跳转和付费墙应记录为评估结论或状态记录，不阻断周报生成。
- 若评估结果只有弱元数据，先更新覆盖审计，不写归档。
- 若写入后发现错误标题、短摘要或坏路径，主控应先修复归档、SQLite 和知识库 CSV 的一致性，再重建周报。
- 若两个 agent 结论冲突，以主控本地复核和测试结果为准。
