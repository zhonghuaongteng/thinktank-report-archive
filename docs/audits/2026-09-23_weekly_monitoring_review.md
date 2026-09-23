# 每周任务审计与来源优化（2026-09-23）

## 判断

问题同时存在于来源、筛选、写作、排版和交付链。历史研究项目已有较广的商业观察材料，但周任务配置没有继承这层覆盖；“创新金融”等检索词存在，不代表相关机构与研究实际进入每周成果。扩大名单之外，需要避免关键词漏收、缩略呈现丢失内容及技术成功掩盖投递失败。

研究口径按当前用户要求调整为科技、经济与社会转型及企业创新实际问题。需求、成本、管理组织、劳动技能、竞争、资本配置、贸易与区域环境等均可构成有价值的问题，不硬性对应主题表，也不强求报告含“科技”字样。

## 最近五期实际成效

以下指标来自各期隔离工作树健康CSV、资料索引和会话完成记录；“机器可入选”是旧审计口径，不等于最后核准的重点数。

| 日期 | 健康表机构/配置 | 候选 | 详情失败/缺日期 | 机器可入选→最终重点 | 重点机构 | 最大/前二来源占比 | 官方战略 | 邮件 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 08-23 | 30/37 | 370 | 29/67 | 21→7 | 3 | 57.1%/85.7% | 0 | API受理，SENT未确认 |
| 08-30 | 30/37 | 348 | 24/72 | 25→17 | 8 | 41.2%/58.8% | 0 | SENT确认 |
| 09-06 | 30/37 | 351 | 26/74 | 28→17 | 6 | 47.1%/70.6% | 0 | 连接不可用，未发送 |
| 09-13 | 31/37 | 354 | 27/74 | 28→20 | 9 | 30.0%/45.0% | 1 | 连接不可用，未发送 |
| 09-20 | 30/37 | 343 | 19/63 | 30→15 | 5 | 53.3%/80.0% | 0 | 连接不可用，未发送 |

五期测试、原生漫画、PDF和远程推送均有完成证据；OneDrive同步五期均被脏副本保护阻断。只有一期间邮件确证成功，不能用“抓取运行成功”概括端到端成效。每期37源中近7日零可入选机构分别30、27、28、28、30；这混合了正常无新品、访问或解析问题和筛选排除，不能直接推断机构无研究发布。

证据根目录依次为：
- 08-23：C:/Users/WINDOWS/.codex/worktrees/cc79/智库信息爬虫
- 08-30：C:/Users/WINDOWS/.codex/worktrees/0250/智库信息爬虫
- 09-06：C:/Users/WINDOWS/.codex/worktrees/09fb/智库信息爬虫
- 09-13：C:/Users/WINDOWS/.codex/worktrees/92a8/智库信息爬虫
- 09-20：C:/Users/WINDOWS/.codex/worktrees/b87a/智库信息爬虫

每个根下核查 reports/<日期>_source_health.csv 和 briefs/weekly/2026/<日期>_国际科技智库周报_资料索引.md；投递状态另按会话记录核验。过程目录未纳入Git是证据保存弱点，本次规则要求每期另外保存受版本控制的阶段回执。

## 设计问题与处理

| 发现 | 判断及处理 |
|---|---|
| 原抓取含当日向前7天，实际8个日期；审计/周报使用7日期 | 周任务改为D-6至D，固定业务日期；日常原行为保持。周报读同日知识库后再过滤，防止混入日常历史项。 |
| 详情失败URL记“已见”，未来可能永久跳过；还会写入窗外失败 | 周任务失败不写已处理，旧失败且未归档可重试；日期门在周状态写入前。 |
| 健康表只按抓到的候选聚合，连续遗漏6—7家 | 按配置完整输出零候选行，并要求detail_ok才算机器可入选；零候选另查原因。 |
| Limit不是全局上限，而是每机构并受run_limit再次限制；日期核验前截断 | 不能把它当覆盖保证。定向补查旧项/导航占位来源；本次去除导航链接并修复BIS/CEPR/ZEW已核实URL家族。更深动态页面适配仍需逐源推进。 |
| 只增加词库仍会漏掉企业国际化等研究 | 在画像过滤前保存经济与企业来源待复核队列，关键词未命中也可原文判断；不自动将所有经济材料抬为重点。 |
| 来源集中度反复报警，改进目标只盯科技专业和战略轨道 | 补入经济与企业研究，并检查实际产出结构及访问漏采；不设每类必收配额。 |
| 只看字符数/句数便标“观点密度达标” | 字数仅排除占位；必须审查新增事实、机制、反直觉发现、证据与局限，不能据长度宣称内容优秀。 |
| 漫画与正文共用压缩摘要，主要论据最多取4句，正文还截到220/240/460字符 | 保留完整周报论据和正文；先写基于原文的独立解读，再从中提炼漫画一个判断，正文提供漫画之外的信息。 |
| 同篇漫画页与分析页都强制换页 | 调整为同篇连续、新篇分页，完整图文自然流动；用9/20既有15图与正文重排预览，不改历史原件。 |
| 商业/受限源的全文标记未实际约束源文写出 | 摘要生成前隔离detail_text，限制公开摘要写出，避免从正文自动回填而越界。 |
| 每篇生图429可阻断整期，下游邮箱连接仍可能缺失 | 保留当前逐篇真图要求，增加阶段复用/回执；启动早检投递能力，内容和投递分开报告。 |
| 运行成功掩盖同步/邮件失败 | 保留主副本保护，明确内容、PDF、远程、OneDrive、邮件各阶段；邮件需SENT确认。 |

## 新增16个每周监测来源

下表是已核实的官方入口与研究价值。网址核验不等于爬虫稳定接入；程序发现不足时，任务必须执行官方补查。2026-09-23入口探测原始记录见同目录 source_entry_probe.csv 日期版，记录了403/406、超时及零解析候选。禁止把这些状态写成“本周无发布”。

| 来源 | 主要入口 | 研究角色 |
|---|---|---|
| ZEW – Leibniz Centre for European Economic Research | [官方入口](https://www.zew.de/en/publications/zew-expertises-research-reports/research-reports) | 企业创新、竞争、数字经济、企业动态和经营条件。年度企业关闭不是创投退出；报告期与首次发布日期分别核实，同口径比较须检查追溯修订。稳定系列页只作发现入口。 |
| KfW Research | [官方入口](https://www.kfw.de/About-KfW/KfW-Research/Publikationen-thematisch/Innovationen-und-Gr%C3%BCndungen/) | 创新、创业、数字化、中小企业需求成本、投资、国际化、接班与人才；不以是否含科技词排除。PDF为主，列表无候选时按官方系列人工核验。 |
| European Investment Bank Research | [官方入口](https://www.eib.org/en/publications-research/economics/research/index) | Investment Report与EIB Investment Survey及专题论文；投资障碍、需求、技能、无形资产、生产率及绿色转型。区分报告发布日期、调查期和受访企业意见。 |
| ifo Institute | [官方入口](https://www.ifo.de/en/publications) | 企业经营、需求、成本、劳动技能、管理组织、竞争、产业与创新；调查和正式分析可纳入，一般活动和人员新闻排除。 |
| DIW Berlin | [官方入口](https://www.diw.de/en/diw_01.c.626639.en/search_publications) | DIW Weekly Report/Wochenbericht、Discussion Papers：产业、劳动、公共投资、能源转型和企业行为。英文为部分选译，发现不足补查德文。 |
| National Bureau of Economic Research | [官方入口](https://www.nber.org/research) | 企业行为、生产率、管理实践、技能与劳动、竞争和投资。工作论文是作者研究，不代表NBER立场；公开摘要与可访问正文分开，不绕过订阅限制。 |
| Centre for Economic Policy Research | [官方入口](https://cepr.org/publications/discussion-papers/search-discussion-papers) | 讨论论文覆盖生产率、创业、产业组织、组织经济、劳动、贸易与公司金融；只公开摘要时列线索，不冒充全文研究卡。署名作者不等于机构立场。 |
| Bank for International Settlements Research | [官方入口](https://www.bis.org/publications/working-paper) | 信贷、资源配置、生产率、企业韧性、国际冲击和技术采用；工作论文观点属作者，排除与创新经济及企业行为无实质关联的纯行情材料。 |
| McKinsey Global Institute | [官方入口](https://www.mckinsey.com/mgi/our-research/all-research) | 企业竞争、投资选址、生产率、人才技能、组织和全球价值链；保留模型假设、研究资助与方法边界，不只采技术趋势。 |
| Boston Consulting Group Research | [官方入口](https://www.bcg.com/bcg-institute) | 企业战略、组织、管理能力、人力规划、竞争和创新执行；保留BCG Institute与历史Henderson署名差异，排除播客/宣传及无方法短评。 |
| Deloitte Insights | [官方入口](https://www.deloitte.com/us/en/insights/topics/talent/human-capital-trends.html) | 组织管理、人才、消费需求、成本和经济环境；Global Human Capital Trends和ConsumerSignals。调查期、发布日期、样本与实际行为分开。 |
| PwC Research | [官方入口](https://www.pwc.com/gx/en/1/issues/c-suite-insights/ceo-survey.html) | CEO与消费者调查、创新回报、需求、竞争、组织能力与气候投资；同一全球报告地区版不得重复算首次发布。 |
| Bain & Company Research | [官方入口](https://www.bain.com/insights/topics/b2b-growth-agenda/) | B2B需求、价值主张、定价、产品创新、组织与不确定性；PE/VC区分，案例必须能核查，咨询推销和服务介绍不算研究。 |
| KPMG Venture Pulse | [官方入口](https://kpmg.com/xx/en/what-we-do/industries/private-enterprise/venture-pulse.html) | 季度创投资金流、地域分布、成长与投资退出；底层数据PitchBook，与NVCA不能算独立互证。稳定系列页需解析当期报告；无新品允许零新增。 |
| PitchBook–NVCA Venture Monitor | [官方入口](https://nvca.org/pitchbook-nvca-venture-monitor/) | 季度募资、投资、成长和创投退出；行业协会政策立场与数据分开，底层PitchBook。公开报告与付费数据库分开；IPO/并购不等于企业关闭。 |
| Dealroom Research | [官方入口](https://dealroom.co/reports) | 城市与区域生态、大学衍生、成长资本、企业成长和人才；逐篇核验赞助方、数据覆盖、估值与方法，不自动注册或填表。 |

MGI、BCG、Deloitte、PwC、Bain均列入首层企业研究监测，不局限创投或技术趋势。Startup Genome、EIF、IWH等保留按问题补充，OECD中小企业系列并入现有源，避免同一母机构重复堆数量。

## ZEW示例如何改变筛选判断

[企业关闭年度系列](https://www.zew.de/publikationen/zew-gutachten-und-forschungsberichte/forschungsberichte/unternehmungsschliessungen)与[2026-08-18发布说明](https://www.zew.de/en/press/latest-press-releases/a-significant-rise-in-firm-closures)说明，它有助于理解企业动态和经营环境，不需包装成技术报告才有价值。系列页期次标为2026年7月，消息发布日是8月18日；应保留这两个日期字段，不能用9月23日看到它的日期作为本周发布日。

[Creditreform联合发布方的方法说明](https://www.creditreform.de/bayreuth/aktuelles-wissen/pressemeldungen-fachbeitraege/show/schliessungszahlen-deutschland-verliert-zu-viele-gesunde-betriebe)说明新版本追溯修订时间序列，企业关闭也不等于破产。本轮将它用于来源与方法核验，不回填当期新报告。

## 本轮验收边界

修改、测试与预览在新隔离工作树进行，保留OneDrive主副本所有原有修改。没有运行本期真实抓取、增加历史归档或知识库条目、补发往期邮件。网络探测只验证入口与可见链接，单元测试/隔离回归不等于未来端到端已成功。未来实际内容和投递成效需要按下一次周任务的阶段回执核验。

## 本轮实际验证记录

- 2026-09-23：全套679项测试通过，差异空白检查通过。覆盖窗口一致性、同日旧索引隔离、失败可重试、日常兼容、零候选可见、关键词漏项待复核、商业摘要边界、作者归属和长正文保留。
- 未运行真实周抓取；archive、briefs、state无本轮变更。
- 9/20版式预览由34页变19页，15张原图、39个正文块完整，Skia/PDF m153。代表页实际渲染检查通过。预览沿用历史图文，封面已标明仅验证版式、不作修订版发布。
- 正文与漫画抽查发现两处事实漂移：Brookings参考文献误作涉华启示，RAND漫画增加了原报告未列的以色列。原历史产物未覆盖；详见[三篇来源核实与正文样稿](2026-09-23_editorial_samples.md)。
- 来源接入边界：官方入口已核实并纳入每周程序发现与官方补查；不声称16家全部稳定自动获取全文。
