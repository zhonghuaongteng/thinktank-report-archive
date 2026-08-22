# C-NESTA-2026-HDRS-DIGITAL-ECOSYSTEM-ANALYSIS 原文切片

- 原文：`03_证据底稿\原文PDF\C-NESTA-2026-HDRS-DIGITAL-ECOSYSTEM-ANALYSIS.pdf`
- PDF页数：65
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 2

Health Data Research Service (HDRS) Digital Ecosystem Analysis | 2
Contents
Scope of this report ......................................................................... 3
Executive summary .......................................................................... 4
Introduction ...................................................................................... 6
Methodology .................................................................................... 9
The current landscape ................................................................... 12
What capabilities are present? ..................................................... 28
What technologies are missing? .................................................. 33
What are the constraints? ............................................................. 36
From gaps to opportunities .......................................................... 39
Pilot initiatives ................................................................................ 52
Conclusion ...................................................................................... 55
Glossary .......................................................................................... 56
Acknowledgements and attributions ........................................... 58
About the authors .......................................................................... 60
References ...................................................................................... 61

### PDF页 4

Health Data Research Service (HDRS) Digital Ecosystem Analysis | 4
Executive summary
The UK health data ecosystem is at a critical juncture,
and the HDRS presents a once-in-a-generation
opportunity to harness data for the health and wealth of
the nations of the UK.
It is apparent that there is potential for enormous public
benefit from insights gained from routine treatment in one of
the world’s largest publicly-funded health systems.
Similarly, access to data from the UK’s diverse population
could attract research and development (R&D) investment
in the life sciences sector and speed the development of
new treatments with national and global applications.
However, the scale, richness and complexity of the data
environment also present a challenge – the heterogeneity
encountered in terms of data standards, infrastructure,
governance and quality mean it can be a daunting and
time-consuming task to link and analyse data on a
population scale or to track individual patients through their
treatment pathways.
All of the potential benefits from the HDRS depend on
building and preserving trust with the public. Recent data
breaches reveal the limits of contractual mechanisms to
prevent actors who seek to exploit data for commercial
gain. As a consequence an increased and necessary level
of scrutiny is being placed on security and privacy.
Technical controls that provide temporary access to secure
environments should exist alongside a culture where the
needs of researchers do not outweigh the responsibility of
organisations to keep data safe.
This independent review provides a comprehensive
assessment of the digital infrastructure underpinning the
UK’s health data assets – mapping what exists, what works,
and where critical gaps constrain our collective ability to
compete at the very highest level globally in health research
and life sciences.
In line with objectives of the HDRS, the review focused on
the unique technical considerations of scientific discovery
and research, rather than healthcare operational needs.
Findings were informed by: semi-structured interviews with
stakeholders across 36 organisations, validation
workshops, in-person sessions across the four nations, a
review of published and grey literature sources, and written
submissions from organisations spanning academia, NHS,
industry, and government. Findings were tested against six
concrete user stories representing communities the HDRS
must serve.
It shows that the HDRS could act as a force for improving
data value by building on proven capability, and a
coordinating layer that provides a reliable, professionally
operated, and accountable service to its users. Success will
require sustained attention on standardisation and
integration, creating true buy-in with stakeholders across all
four nations of a kind not previously achieved in the UK.
Summary of challenges
The UK has a wealth of health data that is too often trapped
in systems that are difficult to access, making it difficult for
researchers to benefit from the full breadth of data
‘available’. Researchers struggle to link data for an
individual, join up data that is hosted in separate
organisations or geographies, and find the compute needed
to analyse complex data. In practice, this fragmentation
slows down clinical trials and reduces global investment –
the lack of a joined-up system makes it harder for hospitals
to find and recruit the right patients as trial participants. Too
much valuable time is wasted attempting (and often failing)
to access our most valuable health data due to poorly
linked infrastructure and unpredictable processes.
Non-programmatic interventions
This report identifies a number of interventions that an
incoming HDRS team might consider when addressing
these challenges. They are not intended to be exhaustive or
directive.
Defining minimum information standards for what data
assets should contain, based on researcher needs and how
that data should be represented; and pairing this with
investment into accessing high-value data types that are
most frequently missing – including hospital prescribing
data, laboratory and pathology results, and clinical
information currently locked in unstructured text.
Building a UK-wide data integration layer to enable cross-
asset, cross-region, and cross-nation research. Different
architectural approaches (centralisation, federated
analytics, or a metadata-driven fabric) each carry distinct
trade-offs that should be evaluated against user
requirements and implementation timelines.
Establishing national data linkage services with agreed
methods and transparent quality metrics would address
one of the most frequently cited bottlenecks in the review.
Standardised linkage methods would de-risk project
delivery and underpin comprehensive longitudinal records
while published quality metrics would allow researchers to
account for linkage error.

### PDF页 9

Health Data Research Service (HDRS) Digital Ecosystem Analysis | 9
Methodology
This section describes how evidence was gathered,
analysed, and how recommendations were developed
and tested.
Evidence gathering
Evidence was gathered through three primary channels:
stakeholder interviews, literature review, and written
submissions. These sources served complementary
purposes. Interviews captured the current operational
reality and practitioner perspectives. The literature provided
technical details, international comparisons, and historical
context. Written submissions enabled organisations to
articulate strategic priorities in their own terms.
Stakeholder interviews
We conducted 39 semi-structured interviews with 78
stakeholders across 36 organisations, spanning: academic
institutions, NHS organisations, government bodies,
commercial data providers, life sciences companies,
technology vendors, and charities across all four UK
nations. Interviews followed a common structure but were
adapted to each stakeholder’s domain.
Interview topics included: current data assets and technical
infrastructure, data flows from source systems to research
environments, governance and access processes, user
experience and pain points, non-technical constraints,
commercial models and sustainability, and perceived gaps
and development priorities.
Interviews with industry stakeholders also explored
research considerations, including clinical trials, real-world
evidence studies, and AI development, and compared them
with international alternatives.
Workshops
We held two virtual stakeholder engagement workshops
with around ~45 attendees at each from the four nations
and three in-person workshops in Northern Ireland,
Scotland and Wales.
The first virtual workshop was meant as a validation workshop
to gather feedback from key stakeholders to validate, further
nuance or challenge our findings, and to ensure we were not
missing anything critical. The second workshop was focused
on the co-development and refinement of potential pilot
initiatives in the context of the technology archetypes and
access mechanisms we have identified.
The in-person workshops held in Northern Ireland, Scotland
and Wales were used to gain an in-depth understanding of the
technological and data landscape across the devolved nations.
Patient and public involvement and engagement
sessions (PPIE)
We held two online PPIE sessions in collaboration with
South West Analytics and Infrastructure Group in
Healthcare, who convened a diverse and informed group of
eight PPIE members. Participants provided feedback on the
review’s main findings and challenges, and discussed a
selection of pilot ideas to inform the landscape review’s
recommendations.
Academic and grey literature
We conducted a literature review of 248 pieces of published
research on health data infrastructure, UK policy
documents, technical documentation from major data
assets, and international comparisons with health data
systems in comparable nations. Academic sources were
identified through searches of Google Scholar, PubMed,
and Scopus. Grey literature included previous UK
government reviews4–7, DARE UK29 infrastructure landscape
assessments, technical documentation from major data
assets (Clinical Practice Research Datalink (CPRD), UK
Biobank, Genomics England, OpenSAFELY, SAIL), and
published strategies from England,2,30,31 devolved
administrations, and HDR UK. International comparisons
drew on documentation from comparable systems,
including those in Denmark, Finland, Israel, and the US.
Written submissions
We invited and reviewed submissions from key
stakeholders, detailing current capabilities, identified gaps,
and strategic priorities for infrastructure development.
Submissions were received from 22 organisations, including
major public research institutes, academic institutions, NHS
organisations and life sciences companies.
Synthesis and analysis
Evidence synthesis
Evidence synthesis was informed by realist principles,
seeking to understand specifics of what works, for whom,
and under what circumstances (rather than cataloguing
assets or assessing capability in the abstract)32,33.
To structure evidence and assess gaps systematically,
information was extracted using the ITPOSMO framework34,
which categorises system components across seven
dimensions:
• Information:
 Data types, sources, quality, and standards
• Technology: Software, hardware, networks, and
technical architectures

## T1_科学体系与基础研究

- PDF页6：focus on academic research rather than commercial research. This has shaped infrastructure investments. Initiatives such as NIHR Biomedical Research Centres (BRCs), the Administrative Data Research UK (ADR UK) network, and DARE UK have primarily funded academic groups to develop research infrastructure. These have understandably focused on developing the tools and systems that support academic research but have (with some notable exceptions) deprioritised integrations with live services, support for commercial researchers and clinical trial delivery. Investments also span multiple programmes operating without systematic coordination: NHS England’s Federated

- PDF页7：andards. However, it remains in early development with full access not expected until 2028 2. With a focus on direct patient care, it does not provide an immediate solution to the structural fragmentation of the research ecosystem. The UK has developed world class components for research infrastructure but not yet a coherent national capability. Building new infrastructure risks duplicating mature capabilities, disrupting established relationships, and consuming resources that could be better deployed scaling what already works. At the same time, the nature of health data research is changing with the advent of AI. It is, therefore, essential to understand not only what infrastructure currently exists but what will be required in the near future. The convergence of research use cases A critical shift informing i

- PDF页9：Finland, Israel, and the US. Written submissions We invited and reviewed submissions from key stakeholders, detailing current capabilities, identified gaps, and strategic priorities for infrastructure development. Submissions were received from 22 organisations, including major public research institutes, academic institutions, NHS organisations and life sciences companies. Synthesis and analysis Evidence synthesis Evidence synthesis was informed by realist principles, seeking to understand specifics of what works, for whom, and under what circumstances (rather than cataloguing assets or assessing capability in the abstract)32,33. To structure evidence and assess gaps systematically, information was extracted using the ITPOSMO framework34, which categorises system components across seven dimensions: • I

- PDF页29：onsistent access to data that reflects real-world clinical practice. Precision medicine researchers similarly require linkage between multiomics data and detailed clinical phenotyping to identify disease subtypes and validate biomarkers. Strengths Scotland has a national imaging research infrastructure. This national imaging archive has research access capabilities that cover all NHS boards, demonstrating that population-scale diagnostic imaging aggregation is technically achievable. PACS infrastructure is universal. The underlying imaging data is stored at source across acute trusts, adhering to common standards. The challenge is extraction, quality assurance, and linkage. Pockets of excellence at academic health science centres. Several major academic centres, particularly those with NIHR Biomedical Research C

- PDF页49：technical gaps in commercial, funding, governance, and public and patient trust that emerged from the review, and presents opportunities to bridge these gaps, drawn from existing practice and evidence. System Gap 1: Funding and service models that enable sustainable and scalable research infrastructure The current UK health data ecosystem produces innovation but struggles to sustain it or translate it into meaningful impact. Academic funding cycles prioritise novelty and publications, over service capabilities, maintenance, stability, and end-user support. NHS funding cycles prioritise strategic infrastructure, but rarely specify end-user and impact focused delivery objectives (i.e., an infrastructure is not a success by existing, but must generate measurable value). When projects end, teams disperse, code accum

- PDF页49：l prototypes, but without dedicated engineering pathways and product focused design, these do not scale into reliable national infrastructure. Supporting Opportunity 1: Transition the ecosystem from grant-funded projects to a professional service model Why this matters: Critical research infrastructure depends on short-term academic or NHS funding without clear service delivery objectives, resulting in fragility, lost institutional knowledge, and lack of clear impact when funding periods end. How this brings value: A professional service model creates stable, production-grade infrastructure with predictable performance, enabling HDRS to compete for commercial contracts and make credible service commitments. The opportunity is to separate core data infrastructure – ability to deliver to end-user requirements, rel

- PDF页50：cumenting, and maintaining datasets while navigating governance requirements. Many of these functions cannot be pushed downstream, so some costs and risks will inevitably remain local. Without clear returns, controllers rationally prioritise local operational needs over national research infrastructure. Supporting Opportunity 2: Establishing a value-return framework Why this matters: Local data controllers bear costs and risks of preparing research-ready data without reliable mechanisms to secure fair value in return, creating misaligned incentives. How this brings value: A value-return framework creates sustainable revenue streams for data controllers, incentivising participation in national infrastructure and enabling predictable pricing for users. The opportunity is to incentivise building towards HDRS infras

- PDF页62：ing UK supercomputing and data science excellence to the world. https://ww w.epcc.ed.ac.uk/ (2026). 83. University of Bristol . Bristol Centre for Supercomputing (BriCS) . https:// www.bristol.ac.uk/research/centres/bristol-supercomputing / (2026). 84. DARE UK. FRIDGE: Federated Research Infrastructure by Data Governance Extension . DARE UK https://dareuk.org.uk/how-we-work/ongoing - activities/dare-uk-early-adopters/fridge / (2026). 85. Gierend, K . et al. Provenance Information for Biomedical Data and Workflows: Scoping Review . J Med Internet Res e51(2024). 86. Government Digital Service, Department for Science, Innovation, and Technology. Guidelines and best practices for making government datasets ready for AI. GOV.UK https://ww w.gov.uk/government/publications/making - government-datasets-ready-for-ai/guid

## T2_技术创新与关键技术

- PDF页4：ften trapped in systems that are difficult to access, making it difficult for researchers to benefit from the full breadth of data ‘available’. Researchers struggle to link data for an individual, join up data that is hosted in separate organisations or geographies, and find the compute needed to analyse complex data. In practice, this fragmentation slows down clinical trials and reduces global investment – the lack of a joined-up system makes it harder for hospitals to find and recruit the right patients as trial participants. Too much valuable time is wasted attempting (and often failing) to access our most valuable health data due to poorly linked infrastructure and unpredictable processes. Non-programmatic interventions This report identifies a number of interventions that an incoming HDRS te

- PDF页5：Analysis | 5 Introducing Trusted Research Environment (TRE) accreditation standards that address usability alongside security would create accountability for the environments through which users access HDRS data and enable credible service level commitments. Addressing adequate compute capacity co-located with the data is essential for AI and computationally intensive workloads. Digitising the governance layer by incorporating portable researcher credentials, machine-readable agreement templates, and transparent project lifecycle tracking could replace fragmented, manual, and opaque access processes that undermine UK competitiveness. Researchers would apply once, track progress in a single environment, and carry recognised credentials across data controllers. Users and public would have guarante

- PDF页10：ongitudinal records, so I can identify disease subtypes, validate biomarkers, and support the design of targeted therapeutics." Opening up advanced diagnostics data “I am a medtech developing AI-based tools. I need access to representative and multimodal data on high-performance compute, with joined-up capabilities for testing my models in real clinical systems, so I can seamlessly move from early development to market.” Faster clinical trials “I am a clinical trial sponsor. I need integrated tools for feasibility assessment, site selection, and patient identification and recruitment, so I can deliver trials faster and more cost-effectively.” Simpler access “I am a pharma customer. I need rapid discovery, rapid feasibility, transparent pricing, and guaranteed 30-day access to conduct time-sensiti

- PDF页17：lue is generated52. TREs represent the accepted model for secure access: controlled workspaces where users analyse data without extraction, with restrictions on data export and audit trails of activity5. TRE maturity varies considerably. Some offer high-performance computing for machine learning, while others provide only basic desktop functionality with limited software customisation53. For AI workloads, compute capability is a particular constraint54. Training models on imaging or genomic data requires GPU clusters’ storage capacity and data throughput that most current TREs cannot provide. Despite policy direction toward TREs, anonymised data release to end-users remains common53. This offers flexibility but provides weaker security and limited auditability, and risks relinquishing the value of anonymi

- PDF页18：gins in structured administrative data. Cloud-based architectures (Databricks, Snowflake) are increasingly adopted by newer assets, offering scalability for diverse data types. Where requirements are predictable and volumes are high, hybrid infrastructure that include on premise compute and storage (as at Wellcome Sanger, Francis Crick) can be more cost-efficient. For the HDRS, architectural choices affect the feasibility of integration. Assets using common technologies integrate more readily than those with proprietary storage. Unstructured data and natural language processing (source data processing layer / data asset layer) Unstructured data (clinical notes, letters, reports) contains valuable clinical detail absent from coded fields. Natural language processing (NLP) using LLMs can extract st

- PDF页20：ederated analytics / learning infrastructure (asset integration layer) Federated analytics executes queries across distributed data assets, returning aggregated results without centralising raw data 55. This requires: data held to common specifications at each node, software and compute capability at each node, orchestration infrastructure for secure information transfer, and a hub for user interaction. OpenSAFELY operates as a production ‘eyes-off’ primary care platform 70. Beyond this, UK federated infrastructure remains largely at the demonstrator stage with open source approaches such as DataSHIELD 71 trialled in the SDE network. Reported barriers to success include a lack of transformed data at nodes, variable compute capability, and general technological immaturity in available platforms. F

- PDF页20：orted barriers to success include a lack of transformed data at nodes, variable compute capability, and general technological immaturity in available platforms. Federated learning is a type of federation where locally trained model weights are aggregated centralling to train new machine learning models. This requires a lower degree of standardisation at each node, but requires substantial compute capability, as smaller models are first trained locally. Fabric infrastructure (asset integration layer) Data fabrics provide orchestration across distributed assets, enabling discovery, access, and analysis through unified interfaces while keeping data in its native locations. Unlike federated analytics (which executes specific queries across nodes), a fabric layer coordinates the full research workflow: finding

- PDF页20：r ARCs, or the data platform team at SeRP , are examples of self-hosted TREs. TREs typically sit in separate organisations from data controllers and data assets. As richer data flows through automated pipelines, proximity to data and access speed become important considerations. Compute resource (research access layer) Compute infrastructure encompasses processing resources within research environments, from basic desktops to high-performance computing and GPU clusters. Capability varies substantially across TREs. Some offer only basic virtual desktops with limited memory. Others, particularly at academic institutions, provide high- performance computing access, including GPU clusters. Cloud environments offer scalability at a higher cost. UK supercomputers (Dawn81, Edinburgh Parallel Computing C

## T3_创新政策与研发治理

- PDF页4：wealth of the nations of the UK. It is apparent that there is potential for enormous public benefit from insights gained from routine treatment in one of the world’s largest publicly-funded health systems. Similarly, access to data from the UK’s diverse population could attract research and development (R&D) investment in the life sciences sector and speed the development of new treatments with national and global applications. However, the scale, richness and complexity of the data environment also present a challenge – the heterogeneity encountered in terms of data standards, infrastructure, governance and quality mean it can be a daunting and time-consuming task to link and analyse data on a population scale or to track individual patients through their treatment pathways. All of the potential benefits from t

- PDF页18：immature. Academic groups have developed disease-specific extraction tools. Some trust-level assets have implemented NLP pipelines. Genomics England employs NLP for data enrichment. Commercial technologies include John Snow Labs 60 , CogStack Ltd61, and Akrivia Health62. An NHS R&D project is funding the deployment of multi-site LLMs for cancer data enrichment 63. Primary care unstructured data remains largely inaccessible, locked behind per-project governance agreements with GP data controllers and stored in vendor environments that require substantial investment to unlock. For the HDRS, unstructured data represents a substantial untapped resource. Scalable processing capability is essential to support user stories that require clinical depth beyond coded fields.

- PDF页49：sets such as CPRD and SAIL have demonstrated success through this approach: dedicated engineering teams treating data provision as a long-term service rather than a temporary research output. There is also the option to capture and protect intellectual property developed through public investment, ensuring foreground IP (code, algorithms, validated pipelines) remains available as national assets rather than being lost or locked into proprietary platforms. The risks of this approach include tension with academic institutions whose incentives differ, and the challenge of building engineering capacity in a competitive labour market. The risks of not pursuing it include the inability to offer the predictable service that commercial users require, continued fragility, and repeated loss of capability when grant

## T4_人才大学与科研组织

- PDF页3：ifies what enables or constrains delivery of the six core Health Data Research Service (HDRS) capabilities and suggests where interventions might have the most impact. The scope encompasses the full data flow from source systems through to the service provision layer accessed by researchers, covering both technical components and real-world legal, organisational and operational constraints. The review does not: • comprehensively catalogue all UK health data assets • replicate existing stakeholder engagement already completed elsewhere • analyse the interplay between the HDRS and other government schemes • attempt to create a blueprint for the HDRS. This review represents the independent findings of a specialist team and is not intended to represent the views or intentions of the HDRS team. It highli

- PDF页4：actors who seek to exploit data for commercial gain. As a consequence an increased and necessary level of scrutiny is being placed on security and privacy. Technical controls that provide temporary access to secure environments should exist alongside a culture where the needs of researchers do not outweigh the responsibility of organisations to keep data safe. This independent review provides a comprehensive assessment of the digital infrastructure underpinning the UK’s health data assets – mapping what exists, what works, and where critical gaps constrain our collective ability to compete at the very highest level globally in health research and life sciences. In line with objectives of the HDRS, the review focused on the unique technical considerations of scientific discovery and research, rather

- PDF页4：sation and integration, creating true buy-in with stakeholders across all four nations of a kind not previously achieved in the UK. Summary of challenges The UK has a wealth of health data that is too often trapped in systems that are difficult to access, making it difficult for researchers to benefit from the full breadth of data ‘available’. Researchers struggle to link data for an individual, join up data that is hosted in separate organisations or geographies, and find the compute needed to analyse complex data. In practice, this fragmentation slows down clinical trials and reduces global investment – the lack of a joined-up system makes it harder for hospitals to find and recruit the right patients as trial participants. Too much valuable time is wasted attempting (and often failing) to access

- PDF页4：ic interventions This report identifies a number of interventions that an incoming HDRS team might consider when addressing these challenges. They are not intended to be exhaustive or directive. Defining minimum information standards for what data assets should contain, based on researcher needs and how that data should be represented; and pairing this with investment into accessing high-value data types that are most frequently missing – including hospital prescribing data, laboratory and pathology results, and clinical information currently locked in unstructured text. Building a UK-wide data integration layer to enable cross- asset, cross-region, and cross-nation research. Different architectural approaches (centralisation, federated analytics, or a metadata-driven fabric) each carry distinct tra

- PDF页5：e environments through which users access HDRS data and enable credible service level commitments. Addressing adequate compute capacity co-located with the data is essential for AI and computationally intensive workloads. Digitising the governance layer by incorporating portable researcher credentials, machine-readable agreement templates, and transparent project lifecycle tracking could replace fragmented, manual, and opaque access processes that undermine UK competitiveness. Researchers would apply once, track progress in a single environment, and carry recognised credentials across data controllers. Users and public would have guaranteed visibility into how NHS data is being used, and to what effect. Alongside these interventions, the review identifies system- level enablers that are also depende

- PDF页6：ding where strategic interventions can yield the greatest impact. The scope encompasses the full data flow from source systems where data originates, through processing pipelines and research data assets, to integration layers, TREs, and the service provision layer through which researchers access the system. It addresses both technical components and the real-world constraints (legal, organisational, and operational) within which technology must function. This analysis deliberately excludes several areas that, whilst important, fall outside its primary remit. It does not produce a comprehensive catalogue of all UK health data assets (numerous such catalogues already exist, and replicating this work would add limited value). The review does not replicate existing engagement work or stakeholder consu

- PDF页6：ng beyond a high-level assessment of the commercial research value of potential initiatives. Background This section examines how the UK health data ecosystem reached its present state and the strategic context shaping infrastructure requirements. Diversity of infrastructure and academic focus The UK health data landscape has developed organically rather than through coordinated national planning. Over the past two decades, multiple reviews have diagnosed similar problems whilst successive investments have created pockets of excellence without resolving fundamental fragmentation. The Wachter Review (2016) analysed the failure of the National Programme for IT and examined digital maturity in secondary care6. The Goldacre Review (2022)5 made extensive recommendations for England on efficient and saf

- PDF页6：eproducible analytical pipelines. The Sudlow Review recognised the need for a UK-wide strategic approach to overcome bottlenecks and break down siloes4. However, with the notable exception of the O’Shaughnessy (2023)7 review of clinical trials, reviews have maintained a focus on academic research rather than commercial research. This has shaped infrastructure investments. Initiatives such as NIHR Biomedical Research Centres (BRCs), the Administrative Data Research UK (ADR UK) network, and DARE UK have primarily funded academic groups to develop research infrastructure. These have understandably focused on developing the tools and systems that support academic research but have (with some notable exceptions) deprioritised integrations with live services, support for commercial researchers and clini

## T5_产业创新与成果转化

- PDF页4：indings were informed by: semi-structured interviews with stakeholders across 36 organisations, validation workshops, in-person sessions across the four nations, a review of published and grey literature sources, and written submissions from organisations spanning academia, NHS, industry, and government. Findings were tested against six concrete user stories representing communities the HDRS must serve. It shows that the HDRS could act as a force for improving data value by building on proven capability, and a coordinating layer that provides a reliable, professionally operated, and accountable service to its users. Success will require sustained attention on standardisation and integration, creating true buy-in with stakeholders across all four nations of a kind not previously achieved in the UK.

- PDF页7：hted that UK data landscape fragmentation and uncertain access timelines compromises ability to deliver research studies at scale. The O’Shaughnessy Review (2023)7 identified the UK’s clinical trials environment as slow and failing to capitalise on the NHS’s inherent advantages. Industry stakeholders describe the UK as “an unreliable and unpredictable partner”, reporting the UK as the second slowest of 18 European countries for trial setup. Performance data confirms these concerns. Industry-sponsored trial enrolment fell to just over 19,000 participants in 2024/25 – a seven-year low 27. The

- PDF页9：nd technical infrastructure, data flows from source systems to research environments, governance and access processes, user experience and pain points, non-technical constraints, commercial models and sustainability, and perceived gaps and development priorities. Interviews with industry stakeholders also explored research considerations, including clinical trials, real-world evidence studies, and AI development, and compared them with international alternatives. Workshops We held two virtual stakeholder engagement workshops with around ~45 attendees at each from the four nations and three in-person workshops in Northern Ireland, Scotland and Wales. The first virtual workshop was meant as a validation workshop to gather feedback from key stakeholders to validate, further nuance or challenge our fi

- PDF页10：ffectively whilst failing others. The gap analysis identified where the current landscape falls short, but equally importantly, where existing capability works well and can be built upon. Validation workshop A validation workshop was conducted with data leaders, researchers, and industry representatives. This was attended by 38 participants. The review team presented preliminary results from the evidence synthesis and the gap analysis. Participants were tasked with challenging assumptions, identifying gaps in the evidence base, and validating the initial findings. Developing and evaluating initiatives Opportunities analysis Gap analysis findings informed an opportunities analysis that explored different technological options. These are specifications for infrastructure, standards, and/or other tec

- PDF页11：utputs directly informed the final pilot proposals. Initial testing with patients and the public Two initial workshops with patient representatives and members of the public explored attitudes toward health data use, priorities for system development, and concerns about privacy, commercialisation, and equity. These sessions tested the proposed capabilities, pilot selection criteria, and pilots against public expectations. Feedback from these sessions was incorporated directly into the findings of this report.

- PDF页20：locations. Unlike federated analytics (which executes specific queries across nodes), a fabric layer coordinates the full research workflow: finding data, requesting access, and conducting analysis, regardless of where data physically resides 76,77. Although relatively common in industry settings, no comprehensive data fabric currently operates across UK health data assets. However, increasing numbers of data assets, including English SDEs, NHS trusts, and SAIL/SeRP are hosted in fabric-compatible cloud technologies. TREs (research access layer) TREs provide secure workspaces where approved researchers can access and analyse data without extracting it 78. They typically offer virtual desktops, analytics software, access controls, audit logging, and data disclosure controls. As discussed in ‘resear

- PDF页31：ilities. NDRS data is incomplete, especially for biomarkers and there can be 18 months of delay before records are available for analysis. There is no platform for biomarker-driven patient identification. Feasibility queries are limited by data depth. Clinical records often lack industry-grade outcomes, are frequently missing key socio-demographic information, in general are broad and shallow, rather than deep, and often lack sufficient linkage for commercial trial precision130. This risks high pre-screening failures, delays in recruitment, and increases in cost69. Simpler access with a single entry point A single entry point to disparate research environments with streamlined agreements and approval processes is primarily a service and governance challenge rather than a technology pr oblem. Howev

- PDF页36：ata assets, the current landscape requires greater structural cohesion to realise its full economic and clinical potential. At present, high operational friction and inconsistent pricing models create hurdles that can inadvertently direct investment toward international markets. Industry stakeholders often describe the UK research environment as “unreliable and unpredictable.” This perception has damaged the UK’s global standing, shown by its drop in Phase III clinical trial rankings from fourth in 2017 to eighth in 202327. The UK is the second slowest among 18 European countries for trial setup, while competitors like Spain have expedited regulatory targets and consistently achieve top rankings.

## T6_国际合作开放科学与比较

- PDF页5：sable technical components as dependencies. (See page 52 for details). 1. UK-wide Real-W orld Evidence asset linking GP , hospital, and prescribing data 2. UK-scale biomarker-enriched pan-cancer cohort for clinical trials 3. UK population epidemiology asset with cross-sector and cross-border linkage 4. Sovereign AI foundation model with linked digital pathology 5. HDRS digital governance and transaction management platform 6. Near-real time device surveillance platform Conclusion For the UK public to benefit fully from the rich health datasets we hold, there is an urgent need to change the way the nations’ health data is collected, stored and accessed. Moreover, without this the UK risks being able to fully realise the economic, research and health potential of advances in data science, AI and computa

- PDF页9：The in-person workshops held in Northern Ireland, Scotland and Wales were used to gain an in-depth understanding of the technological and data landscape across the devolved nations. Patient and public involvement and engagement sessions (PPIE) We held two online PPIE sessions in collaboration with South West Analytics and Infrastructure Group in Healthcare, who convened a diverse and informed group of eight PPIE members. Participants provided feedback on the review’s main findings and challenges, and discussed a selection of pilot ideas to inform the landscape review’s recommendations. Academic and grey literature We conducted a literature review of 248 pieces of published research on health data infrastructure, UK policy documents, technical documentation from major data assets, and international comp

- PDF页14：) manages patient care through 14 health boards, 200+ hospitals and 900+ GP practices. In 2001, the Scottish Care Information (SCI) programme was set up to develop online clinical information stores. This included a store (SCI store) for clinical documents, a specialist diabetes collaboration and gateway and a format for transferring data (SCI XML). This, combined with a universal Community Health Index (CHI) number (equivalent to an NHS number in England, but also used for social care) has allowed Scotland to accumulate nearly 25 years’ worth of referrals, discharge letters, laboratory results and GP summaries, with convergence towards a single provider of secondary care EHR software (TrakCare) and a single GP provider (Vision). Wales (3.1 million population) has a centralised approach to health data

- PDF页15：hin those formats – what fields exist, how they relate, and what each represents. FHIR, as a messaging protocol, also defines data structures for information exchange38. OpenEHR provides an archetype-based approach to clinical data modelling39. The Observational Medical Outcomes Partnership Common Data Model (OMOP CDM) is an example of a standard framework for observational research40. The NHS Federated Data Platform uses its own common data model8. Vocabularies specify a language for clinical concepts within these structures. SNOMED CT provides comprehensive clinical terminology41. ICD-10 classifies diagnoses and causes of death42. OPCS-4 codes surgical procedures43. The NHS Dictionary of Medicines and Devices (dm+d) standardises medication and device references44. Shared vocabularies are vital for

- PDF页24：ta extraction and validation service places responsibility on individual research teams, creating friction for both academic and commercial studies. Stakeholders consistently identified this gap as a primary barrier to participation in large-scale trials and to forming sustained partnerships with life sciences companies. Biobank/longitudinal cohorts (e.g., UK Biobank, Genomics England, Our Future Health, UK Longitudinal Linkage Collaboration (UK LLC), NIHR BioResource) Longitudinal cohort studies and biobanks represent a distinct asset type characterised by deep, multimodal data on consented participants, typically including genomic, imaging, and lifestyle data alongside linked health records.

- PDF页25：nkage. Dementia Platform UK (DPUK) is built on top of SeRP infrastructure providing global access to over 100 multimodal data assets on 3.5 million individuals and supporting 36 ongoing studies and over 50 academic papers per year. DPUK is developing federated capability through partnership with the Alzheimer’s Disease Data Initiative (ADDI). Insight is an ophthalmic imaging bioresource holding over 30 million images across nearly 2 million patients based at Moorfields Eye Hospital NHS Foundation Trust. Through the Alzeye project they have linked routinely held data on patients with Alzheimer’s to retinal images and used this to develop foundational AI models. Place-based integrations Over the last twenty years, there have been examples of local initiatives that have developed infrastructure and data

- PDF页25：ion in North West London. It demonstrated that local data sharing agreements could be agreed and the integrated dataset that links primary and secondary care is still the most comprehensive population dataset in London. NIHR Biomedical Research Centres (BRCs) NIHR BRCs represent collaborations between NHS trusts and universities. The NIHR has allocated nearly £800 million to 20 BRCs across England. Their role is to bridge the gap between early-stage scientific breakthroughs and their translation into practical new treatments. Through these investments infrastructure has been developed that has demonstrated capabilities useful to an HDRS. Data extraction for epidemiological research (Dexter) developed by the Birmingham BRC is software used to

- PDF页26：ir own on-premise network and computing structure. The technology bottleneck for their infrastructure is the throughput of data rather than compute, with limitations on reading and writing data more significant than vRAM of GPUs. The volume of data produced causes challenges for collaboration and limits the utility of cloud providers. Disease registries and audits Disease registries and audits span from national collections to small groups of academic clinicians. They are a critical resource for understanding the different data fields required for research for a given disease. The National Disease Registration Service (NDRS) acts as the primary authority for disease registration in England, managing the collection and quality assurance of data concerning cancer (NCRAS), and congenital anomalies and rar

## T7_中国科技横向维度

未自动命中；需人工按目录复核。
