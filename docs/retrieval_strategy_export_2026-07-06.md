# 国际科技智库检索策略核验版

导出日期：2026-07-06  
仓库：`zhonghuaongteng/thinktank-report-archive`  
本地工作区：`C:\Users\WINDOWS\OneDrive\知识库\智库信息爬虫`  
知识库根路径：`C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库`

本文件用于人工核验当前国际科技智库抓取系统的完整检索策略。可执行配置仍以 `config/`、`scripts/` 和 `thinktank_watch/` 代码为准；本文件把分散在策略文档、配置文件、覆盖审计和多 agent 协议中的规则合并为一份核验材料。

## 一、目标边界

检索目标以“支撑科技创新发展”为主轴，优先保留能够解释研发体系、创新能力、产业化路径、技术基础设施、科技人才、战略性产业、技术扩散、产业链供应链、创新金融、标准计量测试体系、国防创新和涉华科技竞争的报告、论文、政策简报和高质量分析。

AI 治理仍保留专题价值，但默认检索画像不让纯治理材料挤占主要写入与周报展开位置。需要集中观察 AI 治理时，单独使用 `ai_governance_watch` 专题画像。

当前不继续筛选、不回填、不运行日报或周报。恢复筛选、周报运行或历史回填，必须有用户新的明确指令。

## 二、已暴露问题与策略修正

| 问题 | 风险 | 当前策略 |
| --- | --- | --- |
| 来源结构偏向 AI 治理 | GovAI、OECD.AI、Stanford HAI 等源会自然推高治理材料占比 | 默认画像改为 `broad_innovation_support`，把研发、产业、人才、基础设施、供应链和创新金融纳入重点 |
| P1 识别偏窄 | 创新支撑型报告因缺少治理词或只命中单一主题而落入 P2/P3 | 报告、论文、政策简报只要命中实质科技创新支撑主题，即可进入重点候选 |
| 纯治理噪音 | 模型问责、一般监管流程占据 P0/P1 展开区 | `exclude_governance_only: true`，纯治理进入专题观察而非默认重点 |
| 弱词误报 | 单个 `AI`、`technology`、`regulation` 等词抬高弱相关页面 | 单弱词命中保持 P3；需主题组合、页面类型和来源质量共同支持 |
| 日期误判 | sitemap `lastmod` 被误当作报告发布日期 | 详情页日期优先；无可靠发布日期不得进入近三年回填 |
| 页面类型噪音 | 活动、播客、人物、公告、图书发布、索引页污染候选 | 评分前过滤；非报告类内容最高 P2 |
| 商业版权风险 | Gartner 等付费研究不适合全文归档 | `commercial_research` 与 `metadata_summary_only` 边界，只保存元数据、公开摘要、链接和自有研判 |
| 访问限制 | 403、超时、PDF 不可用导致流程中断 | 失败写入状态或审计，不阻断周报；CEPS、NBR 允许受限 `text_proxy_fallback` |
| 中文补写反向污染评分 | 中文摘要中的“上海参考”被误当作原文涉沪信号 | 评分只基于原始标题、英文摘要、关键词、主题和可信元数据 |
| 摘要过短 | 无法支撑后续知识库调用 | P0/P1 中文摘要固定为“核心观点、建议、中国/上海参考”三段 |
| 周报过短 | 周频抓取沿用日报容量，重点被截断 | 周报 P0/P1、创新支撑、涉华涉沪和索引上限单独放宽 |
| 漫画导读失焦 | 图片看不出议题关键点 | 当前采用 v7 “单篇报告证据链式政策漫画”，并配套 `读图说明` |
| 优化过程无止境 | 策略修正不断扩展范围 | 增加本轮优化停止机制，达到边界后停止派发 agent、停止扩展规则、进入提交与记录 |

## 三、检索画像

### 默认画像：`broad_innovation_support`

用途：每周监测、后续历史回填、一般科技智库检索。

保留范围：

- 科技创新：研发体系、科研基础设施、创新体系、技术扩散、成果转化、元科研、科研评价、创新平台、科技指标、公共研发预算、创新金融。
- 半导体：先进芯片、GPU、HBM、硬件瓶颈、半导体设备、集成电路、AI 硬件供应链。
- 先进制造：产业政策、工业能力、供应链韧性、清洁技术、生物制造、能源基础设施、电网、核能、聚变、关键矿产、空间产业。
- 数字经济：数字基础设施、公共算力、AI 基础设施、数据中心、数据互操作、云服务、数据空间、数字公共基础设施。
- 科技人才：STEM、科研人才、AI 技能、高技能人才流动、技能升级、博士教育、科研队伍和人才政策。
- 国防 AI 与国防创新：国防工业基础、军事 AI、DOD AI、技术采购、军民两用创新。
- 创新支撑型科技治理：技术政策、促进创新的监管、监管沙盒、创新采购、标准/计量/质量基础设施、测试验证。

排除原则：

- 只命中 AI 治理或缺少创新支撑信号的科技治理候选，不进入默认画像重点。
- 活动、人物、播客、视频、项目索引、订阅页、泛主题页优先排除。
- 弱相关新闻、博客和评论即使出现科技词，也不得直接抬升为 P0/P1。

### 专题画像：`ai_governance_watch`

用途：需要集中复核 AI 治理、科技治理、国防 AI 和涉华 AI 政策材料时使用。

该画像允许纯治理材料进入观察池，但不能替代默认检索画像。

## 四、主题与优先级规则

主题配置：`config/topics.yaml`  
检索画像配置：`config/search_profiles.yaml`  
优先级配置：`config/priorities.yaml`

| 主题 | 权重 | 核验重点 |
| --- | ---: | --- |
| AI治理 | 4 | 只在专题画像或与创新支撑结合时作为重点 |
| 科技创新 | 3 | 默认主轴，覆盖研发、创新体系、科技金融、技术扩散、科研组织等 |
| 科技治理 | 3 | 需判断是否具有创新支撑属性，纯治理降权 |
| 国防AI | 4 | 视为创新支撑主题，不再简单归为治理噪音 |
| 半导体 | 3 | 芯片、先进计算、硬件供应链和出口管制重点关注 |
| 先进制造 | 3 | 产业能力、能源基础设施、供应链、清洁产业、空间与关键矿产 |
| 数字经济 | 2 | 算力、数据、云、数字基础设施等强信号才优先进入重点 |
| 科技人才 | 3 | 人才链、技能、科研劳动力和高技能流动 |
| 中国与上海相关 | 4 | 背景信号，必须与实质科技主题共同出现才进入 P0/P1 |

优先级阈值：

- P0：总分不低于 9。
- P1：总分不低于 5。
- P2：总分不低于 2。
- 报告类材料加 1 分。
- P0/P1 翻译层级为全文或长摘要；P2 为中文摘要；P3 只入索引。

写入排序：

- 同一优先级内，优先保留创新支撑材料，再保留纯治理材料。
- 有 `write-limit` 时，若候选池中存在足够创新支撑材料，至少一半写入名额留给创新支撑条目。
- 涉华/涉沪只作为背景信号；单独涉华外交、活动或一般政策页面最高 P2。

## 五、机构清单与版权边界

入口数格式：`Feed/List/Topic/Sitemap`。

| 批次 | 优先级 | 机构 | slug | 类型 | 解析器 | 版权边界 | 入口数 | 受限代理 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | P1 | 艾伦图灵研究所 / The Alan Turing Institute | `alan-turing` | research_institute | generic | private_archive | 1/2/1/0 | false |
| 1 | P0 | 澳大利亚战略政策研究所 / Australian Strategic Policy Institute | `aspi` | think_tank | generic | private_archive | 2/2/1/0 | false |
| 1 | P0 | 大西洋理事会GeoTech与网络治国项目 / Atlantic Council GeoTech Center and Cyber Statecraft Initiative | `atlantic-council-geotech` | think_tank | generic | private_archive | 0/2/1/1 | false |
| 1 | P1 | 哈佛贝尔弗中心科技与公共政策项目 / Harvard Belfer Center Science, Technology, and Public Policy | `belfer` | university_research_center | generic | private_archive | 0/1/2/1 | false |
| 1 | P0 | 布鲁金斯技术创新中心 / Brookings Center for Technology Innovation | `brookings-cti` | think_tank | generic | private_archive | 1/2/5/0 | false |
| 1 | P1 | 布鲁盖尔研究所 / Bruegel | `bruegel` | think_tank | generic | private_archive | 1/1/3/1 | false |
| 1 | P0 | 卡内基科技与国际事务项目 / Carnegie Technology and International Affairs Program | `carnegie-tech` | think_tank | generic | private_archive | 0/1/1/1 | false |
| 1 | P0 | 欧洲政策研究中心 / Centre for European Policy Studies | `ceps` | think_tank | generic | private_archive | 0/0/3/0 | true |
| 1 | P0 | 新美国安全中心技术与国家安全项目 / CNAS Technology and National Security | `cnas-tech` | think_tank | generic | private_archive | 1/1/5/0 | false |
| 1 | P0 | 乔治城安全与新兴技术中心 / Center for Security and Emerging Technology | `cset` | university_research_center | generic | private_archive | 1/1/6/1 | false |
| 1 | P0 | 战略与国际研究中心 / Center for Strategic and International Studies | `csis` | think_tank | generic | private_archive | 1/1/2/1 | false |
| 1 | P1 | 欧洲国际政治经济中心 / European Centre for International Political Economy | `ecipe` | think_tank | generic | private_archive | 1/1/1/1 | false |
| 1 | P1 | 胡佛技术政策加速器 / Hoover Technology Policy Accelerator | `hoover-tpa` | university_research_center | generic | private_archive | 0/3/5/0 | false |
| 1 | P1 | IDA科学技术政策研究所 / IDA Science and Technology Policy Institute | `ida-stpi` | federally_funded_research_center | generic | private_archive | 0/2/1/0 | false |
| 1 | P0 | 信息技术与创新基金会 / Information Technology and Innovation Foundation | `itif` | think_tank | generic | private_archive | 1/2/6/0 | false |
| 1 | P0 | 墨卡托中国研究中心产业政策与技术 / MERICS Industrial Policy and Technology | `merics` | think_tank | generic | private_archive | 1/1/1/1 | false |
| 1 | P1 | 美国国家亚洲研究局技术与地缘经济事务项目 / National Bureau of Asian Research Technology and Geoeconomic Affairs | `nbr` | think_tank | generic | private_archive | 0/2/1/0 | true |
| 1 | P1 | 日本科学技术与学术政策研究所 / National Institute of Science and Technology Policy Japan | `nistep` | government_research_institute | generic | private_archive | 0/2/1/0 | false |
| 1 | P0 | 经合组织人工智能政策观察站 / OECD.AI Policy Observatory | `oecd-ai` | intergovernmental | generic | metadata_summary_archive | 0/2/1/0 | false |
| 1 | P1 | ORF美国技术政策项目 / ORF America Technology Policy | `orf-america` | think_tank | generic | private_archive | 0/2/1/1 | false |
| 1 | P0 | 兰德公司 / RAND Corporation | `rand` | think_tank | rand | private_fulltext_archive | 2/2/2/1 | false |
| 1 | P0 | 斯坦福以人为本人工智能研究院 / Stanford Institute for Human-Centered Artificial Intelligence | `stanford-hai` | university_research_center | generic | private_archive | 0/2/1/1 | false |
| 1 | P1 | 韩国科学技术政策研究院 / Science and Technology Policy Institute Korea | `stepi` | government_research_institute | generic | private_archive | 0/1/0/0 | false |
| 2 | P0 | 艾达洛夫莱斯研究所 / Ada Lovelace Institute | `ada-lovelace` | think_tank | generic | private_archive | 1/3/2/0 | false |
| 2 | P0 | AI治理研究所 / Institute for AI Policy and Strategy | `govai` | think_tank | generic | private_archive | 0/2/1/0 | false |
| 2 | P0 | interface欧洲科技政策智库 / interface | `interface` | think_tank | generic | private_archive | 0/2/1/0 | false |
| 3 | P0 | 高德纳 / Gartner | `gartner` | commercial_research | generic | metadata_summary_only | 0/2/1/0 | false |
| 3 | P1 | 国际战略研究所 / International Institute for Strategic Studies | `iiss` | think_tank | generic | metadata_summary_archive | 0/2/1/1 | false |
| 3 | P1 | 皇家联合军种研究所人工智能与国家安全 / RUSI Artificial Intelligence and National Security | `rusi` | think_tank | generic | private_archive | 1/2/1/1 | false |

机构覆盖状态基线来自 `docs/backfill_coverage_audit.md`：

- 当前归档 Markdown：401 条。
- 研究知识库索引：415 条。
- 本地状态库：406 条，其中 401 条有归档路径，5 条为详情失败去重记录。
- 零归档源：Alan Turing、IDA STPI、Gartner。
- 低覆盖源：CEPS、NBR、Bruegel、ECIPE、NISTEP、ASPI、Atlantic Council、Ada Lovelace、Brookings、CSIS。

## 六、抓取与回填边界

### 历史回填

- 默认只追溯近三年。
- 回填窗口以运行日向前 3 年为硬边界。
- 无可靠发布日期、早于回填窗口或晚于运行日的候选不得进入归档。
- 已有早期试抓旧文暂不重洗；若未来清理，必须单独建立“近三年边界清理”任务，同步处理 `archive/`、`state/articles.sqlite` 和知识库索引。

### 每周增量

- 自动运行时间：北京时间每周日 14:00。
- 默认回看窗口：近 14 天。
- 去重依据：URL 状态库。
- 旧 sitemap 条目或聚合页不得进入当周简报；更早但未入库材料进入显式回填流程。

### 暂停态

当前用户指令为“不需要再做筛选和回填，只需要优化策略”。因此：

- 不运行 `evaluate`、`backfill`、`run_daily`、`run_weekly`。
- 不启动来源评估 agent。
- 不新增归档、知识库 CSV 行、周报候选或状态库记录。
- 允许修改策略文档、规则说明、测试、只读脚本和质量闸门。

### 恢复条件

恢复筛选、周报运行或回填必须满足：

1. 用户明确要求恢复。
2. 重新阅读 `docs/retrieval_strategy.md`、`docs/backfill_coverage_audit.md` 和 `docs/multi_agent_execution.md`。
3. 确认 Git 工作区干净。
4. 先做单机构只读评估，优先零归档和低覆盖源，不做全批次大扫描。

## 七、输出与归档格式

### Markdown 归档

位置：`archive/<机构>/<年份>/`

规则：

- 一篇文章一份 Markdown。
- 文件名使用中文标题、发布日期和机构或 hash 后缀。
- frontmatter 至少保存：机构、机构类型、国家地区、英文标题、中文标题、作者、发布日期、原始链接、PDF 链接、关键词、主题标签、优先级、版权边界、抓取状态、翻译层级。
- 正文采用“中文摘要与研判 + 英文材料”的结构。
- P0/P1 采用全文或长摘要中英对照；P2 写中文摘要；P3 只入索引。

### 知识库索引

位置：`C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际智库抓取索引.csv`

要求：

- 新增归档条目必须同步进入知识库索引。
- 索引字段应包含中文题名、英文题名、发布日期、原始链接、PDF 链接、翻译层级、版权边界和抓取状态。
- 当前索引数高于归档数，后续需要单独做索引一致性核验。

### 周报

位置：`briefs/weekly/<年份>/`

内容：

- 新增概览。
- P0/P1 重点条目。
- 科技创新与 AI 治理。
- 涉华/涉沪判断。
- 后续推进清单。
- 漫画导读与 `读图说明`。

周报容量：

- P0/P1 重点条目最多展示 18 条。
- 科技创新支撑条目最多展示 12 条。
- 广义创新支撑条目最多展示 18 条。
- 涉华/涉沪条目最多展示 12 条。
- 索引最多展示 160 条。

## 八、摘要、翻译与漫画导读

### 摘要结构

单篇 Markdown 的 `中文摘要与研判` 固定为三段：

1. `核心观点`：说明作者中心判断、问题定义和关键证据。
2. `建议`：抽取对政府、企业、科研机构、国际合作或治理工具的行动主张；若原文没有明确建议，写明“未检出明确政策建议”。
3. `中国/上海参考`：区分直接涉华/涉沪判断与一般比较参照；没有直接信号时不得强行生成涉沪结论。

### 漫画导读

当前候选风格：v7 “单篇报告证据链式政策漫画”。  
位置：`comic/weekly-tech-watch-v7/`

原则：

- 周报正文前保留 1-3 页漫画导读。
- 每页只表达一个主判断。
- 结构为“单篇报告 -> 机制变化 -> 风险/机会传导 -> 政策建议 -> 上海参考”。
- 机构名称只作为来源条，视觉重心放在证据链、政策取舍和上海参考。
- 图片后必须配套 `读图说明`，用文本锚定报告、核心观点、建议和中国/上海参考。
- v2-v6 和旧四格样张只作对照，不作为默认生成风格。

## 九、多 agent 协作边界

来源：`docs/multi_agent_execution.md`

### 角色

- 主控 agent：读取知识库入口、项目审计、Git 状态和用户约束；独占写入、质量闸门、提交、推送和记忆记录。
- 来源评估 agent：只读评估机构，输出候选证据包，不修改文件，不运行 `backfill`。
- 写入 worker：仅在主控授权时串行写入；不得并发写 `state/articles.sqlite` 或知识库 CSV。
- 质量审计 agent：写入后只读复核，不直接修复。

### 写入租约

- 一次只允许一个机构或一个互斥批次进入写入阶段。
- 租约期间不得启动第二个写入 worker。
- 评估 agent 不需要租约，因为只读。

### 禁止事项

- 不得让多个 agent 并发写 `state/articles.sqlite`。
- 不得让评估 agent 运行 `backfill` 或修改配置。
- 不得把 `--refresh` 当作常规回填参数。
- 不得为扩大数量降低全局 P1 阈值。
- 不得把 Gartner 等商业研究源纳入全文抓取。
- 不得把中文摘要中的“上海参考”反向作为原文涉沪信号重新评分。
- 不得用 sitemap `lastmod` 替代详情页发布日期。
- 不得在未做只读评估时对零覆盖源直接回填。

## 十、本轮优化停止机制

本轮只处理已经暴露的问题、识别规则和协作协议，不再新增智库源、不再扩展检索词、不再启动来源评估 agent、不再生成新的筛选样本。

完成条件：

- 策略文档覆盖目标边界、AI 治理偏置、创新支撑扩口、页面噪音、日期误判、摘要深度、周报篇幅、漫画导读和多 agent 边界。
- `scripts\run_strategy_review.ps1` 通过。
- `archive_count`、`state_total`、`state_archived` 和知识库索引行数相对本轮开始未增加。

测试失败处理：

- 最多允许一次针对失败点的修正和补测。
- 第二次仍失败时停止并报告阻塞点，不进入新的规则迭代。

当前基线：

- `archive_count=401`
- `state_total=406`
- `state_archived=401`
- `kb_rows=415`

## 十一、恢复后建议推进顺序

若用户明确要求恢复筛选或回填，建议按以下顺序推进：

1. 优先只读评估零归档源：Alan Turing、IDA STPI；Gartner 保持 metadata-only。
2. 其次处理低覆盖源：Bruegel、NISTEP、ASPI、Atlantic Council、Ada Lovelace、Brookings、CSIS、CEPS、NBR、ECIPE。
3. 对高覆盖源只做主题缺口式精选：科研体系、创新金融、标准计量测试、科技人才、公共算力、能源基础设施、国防工业基础、数字公共基础设施。
4. 对旧失败记录使用 `evaluate --unarchived-only` 判断是否可修复。
5. 只在字段完整、日期可靠、版权边界可控、去重状态清楚时进入 `backfill`。

## 十二、核验清单

### 配置核验

- `config/institutions/*.yaml` 是否覆盖 29 个机构。
- `config/search_profiles.yaml` 是否仍以 `broad_innovation_support` 为默认宽口径。
- `config/topics.yaml` 是否保留八类主题及“中国与上海相关”背景信号。
- `config/priorities.yaml` 是否保持 P0/P1/P2 阈值和翻译层级。
- Gartner 是否保持 `metadata_summary_only`。
- CEPS 与 NBR 的 `text_proxy_fallback` 是否仍为受限入口。

### 运行核验

- 策略暂停态不得运行 `evaluate`、`backfill`、`run_daily`、`run_weekly`。
- `scripts\run_strategy_review.ps1` 只运行策略测试、空白检查和计数检查。
- 任何恢复回填前必须先做单机构只读评估。
- 周报运行应写入 `briefs/weekly/<年份>/`。

### 质量核验

- 单元测试通过。
- `git diff --check` 无空白错误。
- 归档重复 URL 为 0。
- 中文题名不得与英文题名完全相同。
- H1 与 frontmatter `chinese_title` 一致。
- SQLite 中所有非空 `archive_path` 均存在。
- 知识库索引新增行字段完整。
- 周报 Markdown/HTML/PDF 同步更新；若有漫画导读，PDF 前三页应检测到图片对象。

## 十三、权威文件索引

- 总策略：`docs/retrieval_strategy.md`
- 多 agent 协议：`docs/multi_agent_execution.md`
- 覆盖审计：`docs/backfill_coverage_audit.md`
- 实施说明：`docs/implementation_plan.md`
- 机构配置：`config/institutions/*.yaml`
- 主题配置：`config/topics.yaml`
- 检索画像：`config/search_profiles.yaml`
- 优先级规则：`config/priorities.yaml`
- 策略核验脚本：`scripts/run_strategy_review.ps1`
- 周报入口：`scripts/run_weekly.ps1`
- 只读评估入口：`scripts/run_evaluate_sources.ps1`
- 回填入口：`scripts/run_backfill_batch.ps1`

