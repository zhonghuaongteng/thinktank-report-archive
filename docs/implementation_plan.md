# 国际科技智库抓取系统实施说明

## 运行边界

- GitHub目标仓库：`thinktank-report-archive`，建议保持私有。
- 本地知识库：`C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库`。
- 默认抓取批次：第一批，覆盖 RAND、CSET、ITIF、Stanford HAI、Carnegie、Brookings、CNAS、MERICS、OECD.AI、Belfer STPP、IDA STPI、NISTEP、STEPI、CSIS、Bruegel、ECIPE、ASPI、ORF America、CEPS、Atlantic Council GeoTech、Alan Turing Institute、Hoover TPA、NBR。
- 历史回填默认只追溯近三年；无可核验发布日期、早于回填窗口或晚于运行日的候选不进入归档。
- 每周增量抓取默认只接受近14天内发布的候选；更早但尚未入库的材料进入显式回填流程，避免旧 sitemap 条目或聚合页进入当周简报。
- Gartner按商业研究处理，只保存元数据、公开摘要、链接和自有研判。
- CEPS 与 NBR 对静态请求存在阻断或页面噪音，配置中显式启用 `text_proxy_fallback` 作为受限补救入口。该入口只在静态抓取失败或无候选时触发，仍需机构同域、出版详情页、可靠发布日期和去重状态校验；不得作为全局默认抓取方式。
- P1口径以“支撑科技创新发展”为主轴，覆盖范围宽于AI治理：公共与私人R&D、创新体系、技术扩散与采用、科研基础设施、成果转化、产业竞争力、先进制造、数字化转型、科技人才、生产率和相关政策工具均可进入重点候选。报告、论文或政策简报只要命中实质性科技主题，即按至少P1处理，不要求出现AI治理表述。
- 2026年7月口径更新：后续检索进一步放宽到科技创新发展支撑体系，新增覆盖科技指标、公共研发预算、战略公共投资、科研组织、创新平台、元科研、科研产出与评价、技术转移办公室、大学衍生企业、国际科研合作、产业链价值链、生产能力、供应链韧性、公共算力、数据共享、技能升级、人力资本、高技能人才流动、创新税收激励、无形资本、标准/计量/质量基础设施、测试验证基础设施、产业公地、国防AI和国防创新等报告语言。已完成的历史回填暂不重洗；新增每周抓取和后续批量回填按扩展口径评分与排序。
- 同一优先级内，写入队列和周报重点区优先保存/展示命中“科技创新、半导体、先进制造、数字经济、科技人才、国防AI、创新支撑型科技治理”的候选，再保存/展示纯AI治理候选，以减少小批量写入和简报展开区被治理类材料挤占。周报将纯AI治理或科技治理条目移入单独观察区，创新支撑区只展示研发体系、产业化、数字基础设施、人才、供应链、先进制造等实质支撑材料。
- 当每周抓取或回填命令设置 `write-limit` 时，若候选池中存在足够的创新支撑材料，有限写入批次至少保留一半名额给创新支撑条目；纯治理专门源保留监测，但不应挤占产业、科研、人才、技术扩散和创新金融等支撑科技创新发展的材料。
- `config/search_profiles.yaml` 提供可审计检索画像。`broad_innovation_support` 作为后续展开检索、每周监测和批量回填的默认画像，保留科技创新、半导体、先进制造、数字经济、科技人才、国防AI和创新支撑型科技治理等条目，具体覆盖产业链供应链、清洁技术、生物技术、量子与空间技术、电网与能源基础设施、AI算力和数据中心底座、创新金融、公共算力、科技指标、研发预算、科研组织、标准/计量/质量基础设施、测试验证、产业公地、研发税收激励、高技能人才流动等支撑科技创新发展的材料，并排除只命中AI治理或缺少创新支撑信号的科技治理候选；`ai_governance_watch` 仅用于需要集中观察治理议题的专题运行。周报在有创新支撑条目时限制纯治理条目占据P0/P1展开位，避免专题治理材料挤出产业、能源、基础设施和科研体系材料。
- 日常第一批源池新增 Belfer STPP、IDA STPI、NISTEP、STEPI、CSIS、Bruegel、ECIPE、ASPI、ORF America、CEPS、Atlantic Council GeoTech、Alan Turing Institute、Hoover TPA、NBR 等科技政策、STI指标、产业政策、经济安全、供应链、技术竞争、科研机构、数据科学与技术经济来源，增强创新体系、科研投入、科技人才、产业化能力和区域政策比较材料。
- “中国/上海相关”作为背景信号处理；只有同时命中科技创新、AI治理、半导体、先进制造、数字经济、科技治理或科技人才等实质主题，才进入P0/P1重点队列。单独涉华外交、活动或一般政策页面最高保留为P2索引。
- 质量过滤继续排除活动、人物、播客、项目页、专题索引、视频、网络研讨会、获奖新闻等非研究页面；非报告类新书公告即使提及技术竞争，也最高保留为P2背景索引。

## 命令

只读评估：

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --batch 1 --limit 3
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --institution carnegie-tech --limit 30 --backfill --lookback-years 3 --unseen-only --search-profile broad_innovation_support
```

机构健康审计：

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli audit --batch 1 --limit 5
```

每周抓取：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_weekly.ps1 -Batch 1 -Limit 30
powershell -ExecutionPolicy Bypass -File scripts\prepare_weekly_comics.ps1 -Date <YYYY-MM-DD>
# 对 comic/weekly-topic-comics-<YYYY-MM-DD>/prompts/*.md 逐条调用 Codex 图片生成，输出到 pages/*.jpg。
powershell -ExecutionPolicy Bypass -File scripts\render_weekly_brief.ps1 -Date <YYYY-MM-DD>
powershell -ExecutionPolicy Bypass -File scripts\check_weekly_comics.ps1 -Date <YYYY-MM-DD>
```

首次回溯：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backfill_batch.ps1 -Batch 1 -Limit 5 -MinPriority P1 -WriteLimit 8 -LookbackYears 3 -SearchProfile broad_innovation_support
```

## 输出

- `archive/<机构>/<年份>/`：一篇文章一份Markdown，进入私有GitHub仓库。
- `briefs/weekly/<年份>/`：每周Markdown、HTML与PDF简报，进入私有GitHub仓库。
- `briefs/daily/<年份>/`：历史每日简报保留兼容。
- `comic/weekly-topic-comics-<日期>/`：每周 P0/P1 逐主题 Codex 漫画提示词、图片和生成清单。
- `state/articles.sqlite`：URL去重与抓取状态。
- `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际智库抓取索引.csv`：知识库索引。

## 质量控制

- 候选源URL默认限制在机构自有域名或子域名内；外部媒体链接只作为正文或PDF线索，不作为独立归档源。
- 活动、人物、播客、视频、网络研讨会和公告型页面在评分前过滤。
- 对只有PDF但页面缺日期的报告，使用PDF `Last-Modified` 作为日期兜底，并在后续人工复核中保留修正空间。
- 对全站 sitemap 较宽的机构，可配置 `sitemap_include_keywords`，先按URL技术主题词收窄，再进入评分。
- 对使用 `text_proxy_fallback` 的机构，必须补充单元测试覆盖：列表页 fallback、详情页 fallback、图片链接过滤、集合页排除、缓存日期误用排除和阻断页状态记录。
