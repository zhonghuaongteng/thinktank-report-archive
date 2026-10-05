"""Preserve prior editions; write the user-corrected expanded reading edition."""
from pathlib import Path
import csv,json,sys,dataclasses,copy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from thinktank_watch.models import ArticleCandidate
from thinktank_watch.brief import write_weekly_comic_prompts,weekly_priority_items,weekly_comic_basename
BASE=ROOT/'briefs/revisions/2026-10-05-expanded'
BASE.mkdir(parents=True,exist_ok=True)
prev=json.loads((ROOT/'briefs/revisions/2026-10-05/items.json').read_text(encoding='utf-8'))['items']
original=json.loads((ROOT/'docs/run_receipts/2026-10-05_highlights_drafts.json').read_text(encoding='utf-8'))['items']
rows=list(csv.DictReader((ROOT/'docs/run_receipts/2026-10-05_revision_editorial_review.csv').open(encoding='utf-8-sig')))
byurl={x['URL']:x for x in rows}
def old(url):return copy.deepcopy(next(x for x in original if x['url']==url))
def core(x,text):x['chinese_summary']='### 核心观点\n\n'+text

ukri=old('https://www.ukri.org/opportunity/collaboration-for-a-sustainable-future-pilots-uk-seed-funding/')
ukri.update(institution_name='英国研究与创新署（UKRI）/ Research England',priority='P1',highlights_title='报告解读',selection_reason='用户明确肯定高校协作资金的研究价值；机构合作与科研体系的制度设计值得重点展开。')
core(ukri,'Research England将高校合作支持分为障碍诊断、机构试点与跨区域创新伙伴关系。资金不仅支持提出合作意向，还支持验证多校共同提供研究和创新服务的方式，并把不同地区的互补能力连接起来。')
ukri['highlights_markdown']='''英国研究与创新署（UKRI）下属Research England于2026年10月1日公布“面向可持续未来的协作”计划相关资金。面对高校持续承受的运行压力，计划希望通过机构之间的合作，改善研究和创新体系的成本效益。这里的“可持续”主要指机构和体系的长期运行能力，资助对象是新的协作方式。

### 一、辨认合作障碍与开展试点分别获得支持

计划为协调组安排约75万英镑，每组可申请1万至10万英镑、期限最长一年。协调组需要公开识别高校合作面临的制度障碍，并提出可能的解决办法，使其他机构也能使用这些成果。这条路径强调形成共同认识，为之后的实际协作提供条件。

英格兰高校实施试点另有400万英镑，要求至少两家高校参与，单项10万至100万英镑、最长两年。公告列举联合提供专业服务、尝试中等规模设施的共同管理，以及为企业和投资者建立更清晰的合作入口等方向。支持重点是检验新的跨机构安排如何运作，包括责任、服务与资源如何组织。

### 二、种子资金把不同地区的创新优势连接起来

英国范围的跨区域创新伙伴关系安排1500万英镑种子资金，单项100万至500万英镑、最长三年。申请须连接至少两个地域创新生态，参与者除高校外，还可包括地方政府、企业与投资机构。

这类合作需要说明不同地区的能力怎样互补、共同工作能带来什么额外作用。公告强调探索新模式，要求项目回应各地区的经济特点和发展需要；地域范围可由申请方依据实际联系界定。因而，多机构参加和伙伴数量本身不足以说明合作价值，资金设计要求申请者交代协作的具体理由。

### 三、协作资金围绕研究体系的组织条件配置

公告明确，普通联合科研项目、楼宇或设备购置、研究人员资助，以及仅为削减支出而进行的重组均不在支持范围内。它希望试验的是研究和创新活动的组织条件，例如跨校提供服务、建立共同能力和连接区域生态，而非给既有项目换一个合作名称。

两项主要资金合计1900万英镑，另有协调组支持。当前仍处申请阶段，后续能否改善成本效益和协作能力，要看试点的实施与公开成果；公告也没有保证项目能获得后续追加资助。

来源：[试点与跨区域种子资金](https://www.ukri.org/opportunity/collaboration-for-a-sustainable-future-pilots-uk-seed-funding/)；[协调组资金](https://www.ukri.org/opportunity/collaboration-for-a-sustainable-future-coordinating-groups/)。'''

bruegel=old('https://www.bruegel.org/first-glance/finance-its-future-europe-needs-bigger-more-targeted-budget')
bruegel.update(institution_name='布鲁盖尔研究所（Bruegel）',priority='P1',highlights_title='报告解读',selection_reason='用户明确肯定欧洲共同投资的研究价值；讨论公共投资、创新与跨境基础条件的资金配置机制。')
bruegel['highlights_markdown']='''布鲁盖尔研究所（Bruegel）于2026年9月30日发布兹索尔特·达尔瓦什（Zsolt Darvas）等人的政策解读《为未来融资，欧洲需要更大且更有针对性的预算》。文章结合对欧盟2028—2034年预算提案的研究，分析欧盟层面的资金能在多大程度上填补投资缺口。作者认为，预算规模不足与支出方向延续旧有格局，会共同限制欧洲的长期投资能力。

### 一、先区分哪些投资需要共同承担

欧洲的绿色转型、数字技术、创新和安全韧性都需要增加投资，但并非所有需求都应由欧盟预算承担。文章以“欧洲公共产品”界定共同投资范围：有些项目存在跨境收益和外溢效应，或由欧盟统一投入比成员国各自行动更有效，例如跨境能源网络、研究和气候行动。

这一划分决定预算评估的分母。衡量共同预算是否有效，需要先考察它对共同任务的贡献；包括私人投资在内的全部投资需求则是更大的范围。混用两个口径，会夸大或低估预算的实际作用。

### 二、同一份预算在不同支出情景下作用不同

研究比较了三种配置情景：大体延续现有支出结构、优先投入欧洲公共产品，以及尽量带动总体投资。在作者的假设下，预算提案可填补欧洲公共产品投资缺口的12%—22%；若以公共和私人部门的全部投资需求为分母，则只能覆盖4%—8%。这些比例是提案情景的估算。

作者认为，问题既在规模，也在用途。欧盟预算仅略高于成员国国民总收入的1%，且相当部分继续用于农业和地区再分配，留给创新、气候和数字化的增量空间有限。赋予成员国更大的支出自主权，也不保证资金会自动流向跨境共同任务，原有分配方式可能继续延续。

### 三、担保工具的作用受项目回报结构约束

公共担保和公私合作可以吸引私人投入，但研究、气候减缓和跨境基础设施仍需要持续的直接公共投资。具有共同收益的项目，未必能提供足以吸引商业资金的回报；仅改变融资工具，无法替代公共预算承担相应成本。

因此，文章主张同时扩大预算并调整用途，把新增空间优先配置到长期共同投资。对国防等受到重视、却仍缺少清晰共同投资需求数据的领域，作者还要求先改善分析依据。其政策判断是，欧洲应把资金规模、共同任务和支出结构放在一起讨论，不能将填补投资缺口的责任主要交给金融工具。

来源：[Bruegel政策解读](https://www.bruegel.org/first-glance/finance-its-future-europe-needs-bigger-more-targeted-budget)。'''

nedo=old('https://www.nedo.go.jp/news/press/AA5_101968.html')
nedo.update(institution_name='日本新能源产业技术综合开发机构（NEDO）',priority='P1',selection_reason='用户明确肯定化学研发AI；大学衍生企业与高校依托公共研发项目连接方法研发、验证与服务，恢复重点。')
core(nedo,'NEDO于9月30日介绍TS Technology与奈良先端科学技术大学院大学开发的AMATERUS AI。系统将知识数据库、合成路线探索、反应预测验证与工艺概念设计连接起来，并结合AI和量子化学计算，筛选和评价大量可能的化学合成路线。发布说明中的药物合成评估案例，人员投入由64人周降至12人周；这一单位衡量人员工作量，不能直接读成日历工期缩短相同比例。研究成果当日开始作为服务提供，为观察AI如何进入科学路线设计与验证提供了具体案例，其效果仍需在不同化学体系中检验。')

oecd=old('https://oecd.ai/en/wonk/bridging-frameworks-how-haip-2-0-supports-interoperability-with-the-eu-ai-act')
oecd.update(institution_name='OECD.AI政策观察平台',priority='P2',chinese_title='OECD.AI刊文比较广岛AI报告框架与欧盟监管的信息衔接',highlights_markdown='',selection_reason='国际AI治理制度之间的衔接及公开透明机制有研究价值，不因含具体报告安排排除。')
core(oecd,'OECD.AI于9月30日刊登研究者评论，将广岛AI进程（HAIP）第二版报告框架的31项问题与欧盟《人工智能法案》及通用AI实践准则逐项比较。作者认为，模型风险、能力评估和控制措施等证据可以部分复用，减少不同制度之间的信息割裂。但两类披露服务于不同目标：HAIP强调自愿、公开和国际可比性，欧盟相关机制则包含面向监管和下游使用者的非公开材料。自愿报告不能替代法定义务；文章提出的是作者对制度互补关系的分析，未将其认定为OECD或欧盟的官方合规结论。')

ecipe=old('https://ecipe.org/insights/the-injunction-divide/')
ecipe.update(institution_name='欧洲国际政治经济研究中心（ECIPE）',priority='P2',chinese_title='专利权能否有效执行，影响技术许可与创新资产价值',highlights_markdown='',selection_reason='专利救济制度影响创新者与技术使用者的激励及知识产权融资价值，适合作制度研究简讯。')
core(ecipe,'ECIPE于9月29日刊文比较美欧专利禁令争论。作者认为，限制禁令可以减轻权利人以整件产品停止销售相要挟的空间，却也可能增加技术使用者拖延许可、继续使用专利的动机。争论因而关系到创新者与实施者之间的利益分配。文章以欧洲案件说明，法院可针对特殊情形调整救济范围，例如允许特定患者继续使用唯一适用的心脏瓣膜，而不普遍削弱排他权。作者进一步将执行能力与专利估值、创新企业融资联系起来；美国恢复更强禁令推定的立法建议，仍未取代现行判例标准。')

def rand_brief(url,title,text,reason):
 r=byurl[url]
 x={'institution_slug':'rand','institution_name':'兰德公司（RAND）','institution_type':'think_tank','title':r['标题'],'url':url,'published_date':r['发布日期'],'priority':'P2','raw_priority':r['原始优先级'],'score':int(r['原始得分'] or 0),'content_type':'report','copyright_boundary':'metadata_summary_only','source_completeness':'summary_only','fetch_status':'official_summary_verified','chinese_title':title,'highlights_markdown':'','evidence_locator':'官方发布页简介、Key Takeaways和Recommendations；仅据这些已核内容写简讯，未声称读过PDF全文。','selection_reason':reason,'reading_scope':'official_summary'}
 core(x,text);return x
competition=rand_brief('https://www.rand.org/pubs/research_reports/RRA4254-2.html','兰德将科技与国内经济视为中美竞争的基础领域','兰德9月29日发布《中美竞争的范围与性质》。报告官方摘要将科学技术和国内经济列为七个竞争领域中具有基础作用的两项，并把全球网络关系、社会与治理能力作为跨领域条件。作者认为，中国实力变化不能简单视作直线式的权力转移，第三方选择和国家韧性都会影响竞争走向。建议包括增强本国社会经济基础、改进治理，以及重视全球数字和AI网络中的影响力。这一框架把竞争能力与国内发展、技术体系和国际联系放在一起考察，提供了超出单项技术领先或贸易摩擦的观察视角。','国家竞争框架有独立价值；官方摘要已明确给出主要发现，以简讯呈现，保留PDF未取得的记录。')
adversarial=rand_brief('https://www.rand.org/pubs/research_reports/RRA4734-2.html','军事AI遭到干扰后，技术故障可能演变为战略误判','兰德9月29日发布关于对抗性AI与战略稳定的研究，讨论军事及关键基础设施中的AI被干扰、欺骗或阻断后可能产生的影响。官方摘要指出，决策者可能难以区分模型自身失效与蓄意攻击，也难以确认行为方，进而增加误判和不信任；常规与核指挥、控制、通信系统之间的关联还可能放大升级风险。作者据五种情景提出，提高系统韧性、保留恢复与备用方案，并建立事件信息分享和沟通渠道。研究关注的是攻击带来的战略后果与治理条件，未将这些情景写成已经发生的事故。','前沿技术安全与战略稳定研究；以核准官方摘要写出具体机制，不扩写未核情景细节。')

nedo['highlights_markdown']='''日本新能源产业技术综合开发机构（NEDO）于2026年9月30日介绍化学合成程序AMATERUS AI。山口大学衍生企业TS Technology与奈良先端科学技术大学院大学共同开发该程序，把AI设计合成路线与量子化学计算评价反应结合起来。TS Technology当日开始提供相关服务，使公共研发项目中的计算方法成为可供化学研发使用的工具。

### 一、把分散的路线探索与验证连接起来

功能性化学品包括医药、农药、香料和电子材料等产品。确定从什么原料出发、采用哪些反应和条件，往往依赖文献、研究人员经验、个别计算工具及实验试错；候选路线数量庞大，逐一探索耗费大量时间和人力。

AMATERUS AI连接知识数据库、合成路线探索、反应预测与验证、工艺概念设计四类方法。AI提出候选方案，量子化学计算参与反应评价，再根据目标筛选路径。其价值在于将不同研究环节组合起来，支持研究人员比较路线的可行性。

### 二、公共项目支持高校与衍生企业共同开发

这项成果来自NEDO于2019至2025年度实施的功能性化学品连续精密生产过程技术项目。总项目覆盖催化与反应、分离与精制、计算化学三个方向。TS Technology及其再委托合作方奈良先端大学在2022至2025年度推进路线搜索、候选验证和反应模拟。

公开材料展示了公共项目、大学衍生企业和高校研究团队的具体分工：项目提供研发载体，企业与高校共同开发和验证方法，随后由企业提供服务。服务开始意味着成果已有面向使用者的提供渠道，能否持续扩展还需观察不同化学体系中的应用。

### 三、案例中的效率数字衡量人员工作量

发布说明给出一项药物合成研究评估，工作量从64人周降至12人周。“人周”是投入人数与工作周数的乘积，因此它反映人员投入变化，不能直接换算为日历工期减少相同比例。

这一结果支持继续观察AI与计算化学协同筛选路线的效果，但单个案例尚不足以代表所有功能性化学品。后续应用需要在目标化合物、反应条件和实际工艺要求下继续验证。

来源：[NEDO项目成果说明](https://www.nedo.go.jp/news/press/AA5_101968.html)。'''

def added_brief(url,slug,institution,title,date,text,locator,reason):
    r=byurl[url]
    x={'institution_slug':slug,'institution_name':institution,'institution_type':'research_funder' if slug in ('anr','nedo') else 'think_tank','title':r['标题'],'url':url,'published_date':date,'priority':'P2','raw_priority':r.get('原始优先级',''),'score':int(r.get('原始得分') or 0),'content_type':'analysis','copyright_boundary':'metadata_summary_only','source_completeness':'full_text','fetch_status':'official_text_verified','chinese_title':title,'highlights_markdown':'','evidence_locator':locator,'selection_reason':reason,'reading_scope':'selected_original_sections'}
    core(x,text); return x

policy=added_brief('https://www.rand.org/pubs/perspectives/PEA5282-1.html','rand','兰德公司（RAND）','政策研究机构可同时推进快速响应与组织重构','2026-10-01','兰德10月1日发布政策分析未来研究，提出机构可采用双轨方式：一条轨道让决策者参与分析，通过较快反馈改进现有项目；另一条轨道试验机构角色、资助模式和人才培养的更深变化。作者建议建设专门的AI审计与验证能力，把与决策者共同研究纳入项目设计，并由资助方支持难以仅靠项目合同维持的培训、共同规范及跨领域工作。这些属于面对AI发展与公众信任变化提出的组织改革建议，尚非已验证的统一模式。','PDF实体第12、14—15页，Meso: The Organization及An Agenda for Institutional Leadership。','研究机构的组织分工、双轨改革与资助基础，有明确的新做法，简讯恢复。')
brook=added_brief('https://www.brookings.edu/articles/ai-community-problem-solving-data-centers/','brookings-cti','布鲁金斯学会（Brookings）','社区协作试验让参与者核准信息并共同探索行动方案','2026-09-30','布鲁金斯学会9月30日介绍一次围绕数据中心建设的社区协作模拟。研究者设定经济发展、环境和公共服务可负担性三个居民小组，先逐人访谈，由AI整理记录并交本人核准，再比较各组目标、形成共同策略和可交互的政策导航工具。设计强调由社区掌握数据和治理决定，并把意见收集延伸到实施与反馈。它提供了多方协商的组织试验，但研究使用虚构县域和模拟参与者，不能视为实际社区项目已经取得治理成效。','网页A test in a fictional Michigan county、Results及治理讨论段落。','多参与者共同决策的明确组织试验；与被排除的企业通用智能体经营建议不同。')
cmp=added_brief('https://www.nedo.go.jp/news/press/AA5_101969.html','nedo','日本新能源产业技术综合开发机构（NEDO）','行业联盟与平台开发者分工建设跨企业数据协作基础','2026-10-01','NEDO于10月1日公布化学物质与资源循环信息平台CMP开始服务。行业联盟与NTT DATA共同推进，公共项目支持基础开发，信息处理推进机构提供架构建议，应用开发者面向各行业提供服务。平台把交易关系与物质信息关联起来，仅向指定伙伴传递必要数据，回应企业间协作与商业保密的矛盾。发布方称，500多家企业参与了此前的大规模验证；2028年扩大至数千家仍是目标。这一案例值得关注的，是行业组织、公共支持、技术平台和应用提供者之间的分工。','官方发布页背景、成果(1)(2)、今后计划与注4。','跨行业联盟、数据治理和公共平台的组织模式，保留实际试验与目标的区别。')
anr=added_brief('https://anr.fr/fr/actus/details/news/france-2030-le-cnrs-et-lird-lancent-un-programme-national-de-recherche-sur-lhabitabilite-de-la-t/','anr','法国国家科研署（ANR）/ CNRS / IRD','法国将地方居民纳入研究问题提出与成果讨论','2026-09-29','法国9月29日启动TRANSFORM研究计划，由国家科学研究中心与发展研究院共同牵头、ANR组织实施，计划在十年内配置5000万欧元。研究场域设在法国及其他国家，连接社会科学、生态学和地球科学，并让居民、地方政府、社会组织及经济主体从问题提出到成果讨论参与研究。计划还将考察地方试验怎样扩散并进入公共政策，借助文化机构促进成果理解。新的组织安排在于把地方知识与公众参与嵌入研究过程；当前公布的是启动与设计，效果仍待实施检验。','ANR发布页日期29/09/2026、导语启动日期及Des terrains de recherche等正文。','联合牵头、跨学科与地方共同研究，直接符合用户关注组织新模式；本条报道当周启动，不把旧研究重标新日期。')
pfas=added_brief('https://www.nedo.go.jp/library/ZZNA_100129.html','nedo','日本新能源产业技术综合开发机构（NEDO）','PFAS技术路线需连接材料分类、回收技术与追溯安排','2026-09-30','NEDO于9月30日发布含氟化合物PFAS技术动向报告，将低分子物质与高分子材料分开分析。报告指出，针对低分子物质，分离回收还需与后续分解处理衔接；针对含氟聚合物，生产中来源清楚的边角料与使用后混合废物，所需技术条件不同。扩大循环利用不仅依赖清洗、分选和化学回收，还需要掌握材料来源、树脂种类、添加剂和使用环境。报告据此提出分阶段拓展回收对象的路线，为组合技术研发与追溯机制提供依据。','PDF印刷第1、8—10页；第9页表4及结论。','保留有依据的技术路线研究，侧重技术与追溯机制共同条件，不延伸为用户不关心的加工利润主题。')
energy=rand_brief('https://www.rand.org/pubs/research_reports/RRA5050-1.html','数据中心公私合作需事先明确能源与建设责任','兰德10月2日发布联邦土地上AI数据中心选址研究，比较31个候选地点，并通过政府和行业参与的研讨分析合作安排。作者建议，在招租之前核查能源成本、并网可行性和基础设施条件，把供能与土建列为并行工作；公私合作指引则应事先明确各方风险、安全和退役责任。研究发现，地点排序会随规模和融资假设变化，开放土地本身不足以形成可用算力。这里提出的是基础设施合作的决策与责任安排，研讨情景不代表实际项目已成功运行。','算力公共基础设施的公私协作与责任配置，内容独立于Brookings社区参与模拟，以官方摘要写简讯。')
items=prev[:3]+[ukri,bruegel,nedo,prev[3],policy,cmp,brook,oecd,ecipe,energy,competition,adversarial,pfas]
assert len(items)==16 and sum(x['priority'] in ('P0','P1') for x in items)==6
for x in items:
 x.setdefault('reading_scope','selected_original_sections')
 x['highlights_title']='报告解读'
fields={f.name for f in dataclasses.fields(ArticleCandidate)}
candidates=[ArticleCandidate(**{k:v for k,v in x.items() if k in fields}) for x in items]
editorial={
 'date':'2026-10-05','headline':'科研合作、共同投资与AI治理：本周研究选读',
 'lead':'本期包括六篇重点解读和十则简讯，优先关注组织模式的新做法。英国试验高校间的协作安排，日本探索高校、企业与公共项目之间的成果应用分工，兰德讨论政策研究机构如何兼顾快速响应和组织重构。共同投资、科学数据、国际治理及科技竞争等研究提供更广的政策背景。',
 'discoveries':[
 {'title':'协作资金支持研究体系的组织试验','text':'英国把合作障碍诊断、英格兰高校试点和跨区域创新伙伴关系分别配置资金，要求说明机构与地区之间如何形成互补能力。','source_url':ukri['url'],'article_url':ukri['url'],'source_locator':'UKRI资金公告：范围与支持方式'},
 {'title':'欧洲投资缺口同时涉及规模与用途','text':'Bruegel认为，担保工具能够吸引私人资金，但研究、气候和跨境基础设施仍需要直接公共投入；扩大预算还须调整支出方向。','source_url':bruegel['url'],'article_url':bruegel['url'],'source_locator':'Bruegel预算政策解读'},
 {'title':'AI开始连接化学路线设计与反应验证','text':'AMATERUS AI将AI与量子化学计算结合，从大量候选合成路径中筛选和验证方案；特定药物评估案例的人员投入由64人周降至12人周。','source_url':nedo['url'],'article_url':nedo['url'],'source_locator':'NEDO发布说明与注3'}
 ],'connections':[],'review':{'completed':True,'note':'用户肯定的三项已恢复；6重点10简讯，10个来源主体slug；组织模式优先，RAND三条简讯据官方摘要，其余按所写范围核读原文。ANR稿件原始PDF为9月28日，排除当期。'}
}
(BASE/'items.json').write_text(json.dumps({'date':'2026-10-05','version':'扩充修订版','items':items},ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'2026-10-05_editorial.json').write_text(json.dumps(editorial,ensure_ascii=False,indent=2),encoding='utf-8')
selected={x['url']:x for x in items};changes=[]
for r in rows:
 before=r['最终处置'];r['前次修订处置']=before;r['本次阅读范围']='继承前次记录并复查题意与摘要'
 if r['URL'] in selected:
  x=selected[r['URL']];summary=x['reading_scope']=='official_summary'
  r.update({'最终处置':'重点' if x['priority']=='P1' else '简讯','全文状态':'不需全文' if summary else '已核读','正文定位':x['evidence_locator'],'取舍理由':x['selection_reason'],'写作复核':'通过','复核状态':'官方摘要核读完成，限简讯' if summary else '已核原文与写作完成','本次阅读范围':x['reading_scope']})
  r['本轮复核依据']='用户纠正过度收紧，要求至少6重点10简讯，并进一步优先组织模式等新做法。'
  r['发布日期']=x['published_date'];r['机构slug']=x['institution_slug']
  if not summary:r['全文获取记录']='本轮核读官方原文，定位见正文定位；未声称覆盖未读章节。'
  if summary:r['全文获取记录']='本轮网页工具成功读取官方简介、关键发现与建议。'+x['url']+'；历史PDF尝试：'+r.get('全文获取记录','未下载，不用于本条简讯。')
 elif r['URL']==anr['url']:
  r.update({'发布日期':'2026-09-28','最终处置':'排除','全文状态':'已核读','取舍理由':'ANR网页9月29日，但所附原始新闻稿第一页标注9月28日。按首次发布日期在本期窗口外；组织安排有价值，日期门不放宽。','正文定位':'官方PDF第一页页眉；https://anr.fr/fileadmin/documents/2026/CP-France2030-PEPR-Transform-28092026.pdf','全文获取记录':'本轮网页工具成功核读官方3页PDF。'})
 elif r['机构slug']=='stepi':
  r['取舍理由']='官方详情本轮仍读取失败，无法核准日期与正文；撤销仅凭paper/系列标签认定学术论文的旧理由，保持真实获取受阻记录。'
 elif r['机构slug']=='nedo' or r['URL'].endswith('PEA5282-1.html'):
  r['取舍理由']='当期按议题和篇幅作取舍，未收录；撤销按具体工艺/制度/服务类型自动排除的旧理由。材料本身不列入长期黑名单。'
 elif r['URL'].endswith('RRA5195-1.html'):
  r['取舍理由']='本条围绕关键矿产供给的支持工具；本期未收，避免回到用户明确排除的加工盈利选题。关键资源政策研究方向仍保留。'
 elif r['最终处置']=='排除' and '本期' in r['取舍理由']:
  r['本轮复核依据']='本次重新浏览题意与公开摘要，按研究价值取舍；既有日期、无关内容、重复及资料类型证据继续适用，旧篇幅选择不作为长期黑名单。'
 if before!=r['最终处置']:changes.append({'url':r['URL'],'title':r['标题'],'before':before,'after':r['最终处置'],'reason':r['取舍理由']})
out=ROOT/'docs/run_receipts/2026-10-05_expanded_editorial_review.csv'
with out.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(BASE/'selection_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
write_weekly_comic_prompts('2026-10-05',candidates,BASE/'comic')
sys.stdout.reconfigure(encoding='utf-8')
print(json.dumps({'selected':len(items),'features':[(i,x.title,weekly_comic_basename(i,x)) for i,x in enumerate(weekly_priority_items(candidates),1)]},ensure_ascii=False))
