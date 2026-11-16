# 2026-11-15 官方补查与可用编选

固定正式窗口：2026-11-09—15。核查完成于2026-11-16，未将11/16材料纳入。本文为人工补查，与默认53个配置源分开统计；已尝试22机构入口不代表22家稳定自动抓取，也不保证穷尽全部通知。未恢复程序采集。

## 七地区22机构入口核查

| 地区/机构 | 实际入口 | 本轮结果与处置 |
|---|---|---|
|美国 OSTP|https://www.whitehouse.gov/ostp/news/|可读目录最新可见10/29；本入口未发现窗口内候选，不外推为机构无发布。|
|美国 NSF|https://www.nsf.gov/news|最新可见11/2播客；本入口未发现窗口内合格材料。|
|美国 NIH|https://www.nih.gov/news-events/news-releases|11/12脑细胞图谱新闻为研究成果类，未发现本期需采用的资助/组织机制新信息，不收入。|
|美国 DOE|https://www.energy.gov/listings/recent-funding-opportunities-announcements|最新可见10/8资金/奖学金；本入口未发现窗口内新项目。|
|美国 DARPA|https://www.darpa.mil/news；https://www.darpa.mil/rss.xml|新闻只解析出动态筛选壳；RSS工具不支持text/xml；官方域名11月检索出现旧文件中的活动日程，未确认新品。记访问/解析受限，不能记零发布。|
|欧盟 DG RTD|https://research-and-innovation.ec.europa.eu/news/news-alerts_en|11/13气候健康联盟正文通过；目录摘要错配ERC招聘，已回源纠正。|
|欧盟 ERC|https://erc.europa.eu/news-events/news|11/12 Synergy结果及项目例子合并一项；11/13理事人员任命不采用。|
|欧盟 EIC|https://eic.ec.europa.eu/news_en|11/10 Pathfinder申请进展及组合机制可写简讯；11/5工作计划窗外。|
|英国 UKRI|https://www.ukri.org/news/|11/12电池、11/10 DUNE通过；任命消息不采用，11/9周年庆未优先选用。|
|英国 ARIA|https://aria.org.uk/insights/all-insights|最新可见10/29；本入口未发现窗口内候选。|
|德国 DFG|https://www.dfg.de/en/service/press/press-releases|NAM英文稿11/10，追溯德文首次9/10，排除；不能作为本期新研究。|
|德国 Fraunhofer|https://www.fraunhofer.de/en/press-newsroom.html|最新研究新闻11/2，均窗外；目录页尾11/12是网页时间非条目发表日。|
|法国 ANR|https://anr.fr/fr/actualites-de-lanr/|法文目录最新11/6地区合作，窗外；通过DG RTD发现ANR参与联盟，不重复拆篇。|
|法国 CNRS|https://www.cnrs.fr/fr/newsroom|英站不及时，切回法站。11/9气候数据分析通过；11/12野火页嵌入11/5视频，首次日期不清且正文不足，未采。|
|日本 MEXT|https://www.mext.go.jp/b_menu/houdou/index.htm|11/9—13主要会议预告、获奖、认证；未采用。11/16大学群材料窗外，不收入。|
|日本 JST/CRDS|https://www.jst.go.jp/crds/news/index.html|目录11/13转载第360篇，正文报纸首发11/6，排除；11/6 AI4S窗外。|
|日本 JSPS|https://www.jsps.go.jp/j-press-releases/|日文最新11/6诺贝尔对话网站，窗外；未采用。|
|日本 NEDO|https://www.nedo.go.jp/news/index.html|11/9氢燃机官方稿通过，事件11/6与发表11/9分别记录。|
|韩国 MSIT|https://www.msit.go.kr/index.do；https://msit.go.kr/|韩文首页超时、备用域名无可读行；官方域名搜索可见11/13公告但细节未核，访问受限。没有写成无发布。|
|韩国 NRF|https://eng.nrf.re.kr/page/62a7fecb-959a-4dcb-80ff-11dcd9913d1e；https://www.nrf.re.kr/main|英文征集最新11/5窗外；韩文转到SSO不可访问。未采，不称全面零发布。|
|韩国 KISTEP|https://www.kistep.re.kr/board.es?mid=a10306010000&bid=0031|韩文11/11人形机器人投资策略通过；PDF27页已核摘要、国内投入、结论。|
|韩国 NST|https://www.nst.re.kr/www/selectBbsNttList.do?bbsNo=34&key=64；https://www.nst.re.kr/www/selectBbsNttList.do?bbsNo=14&key=55|政策研究目录最新10/27；公告见11/12—13规划研究，详情和附件入口已查，HWPX下载SSL握手超时，未形成可采用机制分析。|

## 必须保留的日期纠偏与受限线索

- DFG：英文 https://www.dfg.de/en/service/press/press-releases/2026/press-release-no-34 为11/10；德文 https://www.dfg.de/de/aktuelles/neuigkeiten-themen/pressemitteilungen/2026/pressemitteilung-nr-34 明确9/10，且英文称now available in English。判为窗外原研究翻译，不入本期。
- CRDS：https://www.jst.go.jp/crds/column/choryu/360.html 正文与报纸首发均11/6，目录转载11/13，不入本期。
- NST拟议研究线索：AI科学家独立验证与复现基础设施规划（11/12，nttNo=52737）；PD主导国家任务型研发的法律制度完善（11/12，nttNo=52736）；新药AI训练/基准数据规划（11/13，nttNo=52743）。均仅征集规划研究，不能写成设施已建成或制度已实施。附件12038、12033、12053在web返回不支持application/x-msdownload，本机请求再次SSL握手超时，保留受限状态。
- NEDO首发11/9，报道11/6开所式，按正式发布日入窗；项目2021年获选仅背景。

## 重点与简讯

原始程序评分：人工补查无程序分数，记not_scored，不补造机械分。最终建议：CNRS作为重点（长期数据责任与科研经费矛盾有清晰证据），七则其余为简讯；由主编辑结合全期最终确定。KISTEP实质涉及AI研发组织，阅读优先得到提高，但没有因此自动升P0/P1。

### 项目结束以后，谁来守住几十年的气候观测数据？

法国国家科学研究中心11月9日的分析，把气候数据保护落到一个具体矛盾：观测要持续几十年，资助却常按三至五年的项目安排。测量中断后，扩充硬盘也补不回缺失的记录；数据保存因此关系到海岸、冰川和城市风险的长期判断。

### 让长期责任有明确承担者

文中讨论的法国法案于2月提出、仍在议会审议，拟把地球、气候和环境数据的收集、传播与保存纳入公共科研使命。受访研究者期待相应经费保障；文章没有证明法案已通过，也没有把机构当前自愿承担的维护工作写成稳定保障。

### 存得下，还要找得到、用得起来

Data Terra提供了可依托的基础。CNRS此前的背景介绍说明，它连接地球系统的五类数据资源，通过共同目录、数据描述和处理服务，使不同实验室的数据能够相互关联。34家机构与大学共同参与，逾200名全职人员从事相关工作。这解释了为何数据保护不能简化为购买存储设备：还需要持续的整理、质量检查和面向研究者的服务。[背景来源：CNRS，2025年4月25日](https://www.cnrs.fr/fr/actualite/federation-eosc-top-depart-pour-le-cloud-europeen-de-la-science-ouverte)。

本期文章援引CNRS地球与宇宙研究部门的估算：将Data Terra可用容量从100扩至600拍字节，约需1700万欧元，可为受威胁的外国气候数据提供接纳空间。这是扩容设想及估算，不是已经获批的投资。

### 保护数据，也必须作出取舍

保存能力和环境成本都有边界。文章主张由科学委员会选择有长期价值的数据，并保持其可查找、可访问、可互操作和可复用。面向三十年后的使用者，需要同时保证观测不中断、资料不丢失、数据还能被理解。

来源：https://www.cnrs.fr/fr/actualite/la-france-future-terre-dasile-des-donnees-scientifiques-sur-le-climat

内部定位：当期CNRS正文第50-64行（长期观测、法案与项目经费）、70-90行（FAIR、Data Terra扩容设想及取舍）；全文已读。背景为2025-04-25 CNRS EOSC文章第55-60行，仅解释既有组织能力，不作为当期新发布或新增条目。正文资料属性为公共研究组织分析报道，非已生效法律。

### 英国电池资助把回收工艺、维修判断和技能培训一起推进

英国电池创新计划公布向27个项目提供2860万英镑，覆盖技术开发、可行性研究和技能培训。Reclaim由企业牵头，把莱斯特大学以少量植物油和水分离电池材料的工艺放大到中试；Hyperbat则拟建立逐块检查电池、决定维修、再用、储能再利用或回收的流程。另有15项为期6至12个月的可行性研究，以及三项地区培训。资金已授予，工艺放大、材料再用和减少报废仍须验证，不能把目标写成已经节约的成本。

来源：UKRI／Innovate UK｜2026-11-12｜https://www.ukri.org/news/charging-towards-the-battery-electric-future/

内部定位：官方正文开头、Recycling batteries、Reducing waste、Feasibility studies、Investment in skills；Further information分项9+15+3=27，资金18.74+6.23+3.6=28.57m，头条四舍五入28.6m。

### DUNE低温容器进入建设，英国以大学和国家实验室分工参与

地下中微子实验DUNE开始建设大型低温容器，由费米实验室、欧洲核子研究中心和桑福德地下研究设施团队共同推进。英国参与由科学与技术设施理事会牵头，组织15所大学及两个国家实验室，分别提供探测器部件、数据采集、软件、计算和加速器技术。实验拟在相距1300公里的两端比较中微子信号。此次新增进展是容器建设，尚未取得目标物理发现；英国7900万英镑投入为2017年的承诺，不能列成本周新拨款。

来源：UKRI／STFC｜2026-11-10｜https://www.ukri.org/news/construction-begins-on-giant-underground-neutrino-experiment/

内部定位：官方正文Construction、DUNE-UK、What DUNE could discover、Investing in UK science and technology；发布日期11/10，主要事实第9-16、34、45-62行。

### 气候与健康资助联盟拟用共同秘书处协调分散投资

欧委会与Wellcome及多个公共资助机构启动气候与健康研究资助多边倡议，试图协调研究重点和资金安排，减少各方各做各的情况。联盟将向相关资助组织开放，并与研究机构、智库及产业合作。其常设秘书处拟于2027年1月运行，由法国ANR、荷兰ZonMw、加拿大IDRC和罗马尼亚UEFISCDI组成的联合体承担，欧委会协调与支持行动资助持续至2029年12月。组织框架已公布，减少重复资助和改善健康结果仍属于目标。

来源：欧盟委员会研究与创新总司｜2026-11-13｜https://research-and-innovation.ec.europa.eu/news/all-research-and-innovation-news/commission-launches-first-global-alliance-climate-and-health-research-funding-cop31-2026-11-13_en

内部定位：官方正文第38-48行与Background第54-56行；不沿用目录错配摘要，发布日期11/13；秘书处开始2027-01，资金截止2029-12。

### ERC把5亿欧元交给48个互补团队攻克单人难题

ERC公布2026年Synergy资助结果：957项申请中选出48个团队，总额5亿欧元。每组由两至四名专长互补的研究者组成，自主选择单人难以处理的问题；约35%的入选项目包含欧盟及关联国之外的研究者。项目案例中，SKUA将结合水下自主航行器、钻孔传感器和卫星分析，研究南极冰架下方与内部难以观测的变化。机制的重点是把测量和分析能力组合起来；资金获选不等于研究假设已经得到证实。

来源：欧洲研究理事会（ERC）｜2026-11-12｜https://erc.europa.eu/news-events/news/erc-2026-synergy-grants-results

内部定位：主公告开头和Facts and figures；项目例子https://erc.europa.eu/news-events/news/synergy-grants-2026-examples-projects 的SKUA段。两页均11/12，同一资助事项合并，不将48重复计数。

### EIC挑战型早期研究收到1138项申请，评审尚未完成

EIC公布Pathfinder Challenges申请情况：截至10月28日收到1138项提案，来自58国的5107个参与方，涉及能量采集材料、健康老龄化生物技术以及认知AI三个方向。本轮指示性预算为9600万欧元，拟大致平均分配。计划支持从早期探索到概念验证或实验室验证，并由项目经理推动项目间交流、探索成果应用与组合协作。11月10日发布的是申请和评审进展，结果预计2027年春公布；申请增多本身不能证明技术更成熟或资助有效。

来源：欧洲创新理事会（EIC）｜2026-11-10｜https://eic.ec.europa.eu/news/2026-eic-pathfinder-challenges-call-attracts-record-interest-breakthrough-innovators-2026-11-10_en

内部定位：官方全文第11-27行，发布日期第34-37行；1138为提案、5107为参与方、58为国家，均非已获资助数。

### 日德纯氢燃机示范转向现场验证，制造与电站整合分工明确

NEDO、川崎重工和德国RWE公布30兆瓦级氢燃气轮机示范进展。川崎在日本制造燃机，欧洲子公司组装并安装，RWE负责电站总体规划和配套设施。设备可调整氢与天然气的混合比例，适应氢供应逐步增长的阶段。现场后续将检验排放要求、燃烧稳定性、耐久性及运行表现。官方稿11月9日发表，开所式为11月6日；这是跨国现场验证的新进展，不能把它写成已证实商业经济性或已完成全部验证。

来源：日本NEDO（公共研发资助机构）｜2026-11-09｜https://www.nedo.go.jp/news/press/AA5_101978.html

内部定位：日文官方稿第31-41、46-62行，尤其2.今回の成果与3.今後の予定。2021年项目获选为背景，本次新闻首次发表11/9。

### KISTEP建议用数据积累和再训练速度衡量人形机器人投入

KISTEP的投资策略简报认为，韩国已有较强硬件与制造能力，短板在机器人基础模型、行为数据和计算资源。报告建议，在开发本国机器人之外，建设企业与研究机构共同使用的数据、仿真和算力条件，并围绕制造、物流、照护等具体任务反复验证，让现场数据进入下一轮训练。评价不应只看造出多少机器人，也应观察数据积累量、再训练周期与性能改善速度。这是政策研究建议，尚不是已经实施并证明有效的新评价制度。

来源：韩国科学技术企划评价院（KISTEP）｜2026-11-11｜https://www.kistep.re.kr/board.es?act=view&bid=0031&list_no=94918&mid=a10306010000

内部定位：韩文页面注册日11/11；官方27页PDF https://www.kistep.re.kr/boardDownload.es?bid=0031&list_no=94918&seq=1 。已核物理2-3、20-27页，摘要及第5节（物理25页）支持本简讯；表中各项目预算未写入简讯。
