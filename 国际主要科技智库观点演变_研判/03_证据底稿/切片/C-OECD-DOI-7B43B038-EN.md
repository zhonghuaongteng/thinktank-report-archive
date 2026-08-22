# C-OECD-DOI-7B43B038-EN 原文切片

- 原文：`03_证据底稿\原文PDF\C-OECD-DOI-7B43B038-EN.pdf`
- PDF页数：106
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 4

4 | MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS

OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

Table of contents
Acknowledgements .................................................................................................................... 3
Abstract ...................................................................................................................................... 8
Synthèse ...................................................................................................................................... 8
Executive summary ................................................................................................................... 9
Résumé ..................................................................................................................................... 11
Measuring the AI content of government funded R&D projects: A proof of concept for
the OECD Fundstat initiative ................................................................................................. 14
1. Introduction and background ............................................................................................ 14
2. AI-related project retrieval methodology.......................................................................... 18
2.1. Project funding data ........................................................................................................ 18
2.2. Operational definition of AI ............................................................................................ 21
2.3. AI-related project retrieval methodology ........................................................................ 23
2.3.1. Selecting key AI terms ............................................................................................. 26
2.3.2. Tagging documents with the list of key AI terms .................................................... 36
2.3.3. Topic modelling analysis of selected AI-related documents .................................... 37
2.3.4. Analysis under different data access regimes ........................................................... 37
2.3.5. Analysing data in different languages ...................................................................... 38
3. Results................................................................................................................................... 39
3.1. Key AI terms across funding databases .......................................................................... 39
3.2. Estimates of AI-related R&D funding volumes .............................................................. 40
3.3. AI topics in R&D funded projects .................................................................................. 42
4. Conclusions and next steps ................................................................................................. 49
References ................................................................................................................................ 52
Annex A. Overview of R&D funders and databases ............................................................ 55
ARC (AUS) ........................................................................................................................ 55
CIHR (CAN) ...................................................................................................................... 55
NSERC (CAN) ................................................................................................................... 55
PlanEst (ESP) ..................................................................................................................... 55
ANR (FRA) ........................................................................................................................ 55
GtR (GBR) ......................................................................................................................... 56
AMED (JPN) ...................................................................................................................... 56
KAKEN (JPN) ................................................................................................................... 56
NWO (NLD) ...................................................................................................................... 56

### PDF页 8

8 | MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS

OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

Abstract
This report presents the results of a proof of concept for a new analytical infrastructure
(“Fundstat”) for analysing government funding of research and development (R&D)
at the project level, exploiting the wealth of text- based information about funded
projects. Re flecting the growth in popularity of artificial intelligence (AI) and the
OECD Council Recommendation on AI’s emphasis on R&D investment, the report
focuses on analysing government investments into AI-related R&D. Using text mining
tools, it documents the creation of a list of key terms used to identify AI-related R&D
projects contained in 13 funding databases from eight OECD countries and the EU,
provides estimates for the total number and volume of government R&D funding, and
characterises their AI fundin g portfolio. The methods and findings developed in this
study, also serve as a prototype for a new expanded, distributed mechanism capable
of measuring and analysing government R&D support across key priority areas and
topics for the OECD and its member countries.
Keywords: Research and development, government funding, artificial intelligence
Synthèse
Ce document présente les résultats d'une preuve de concept pour une nouvelle
infrastructure analytique (« Fundstat ») pour analyser le financement gouvernemental
de la recherche et développement (R&D) au niveau des projets, en exploitant la
richesse des informations textuelles sur les projets financés. Reflétant la popularité
croissante de l'intelligence artificielle (IA) et l'accent mis par la Recommandation du
Conseil de l'OCDE sur les investissements en R&D, il se concentre sur l'analyse des
investissements gouvernementaux dans la R&D liée à l'IA. À l'aide d'outils
d'exploration de texte, le rapport documente la création d'une liste de termes clés
utilisés pour identifier les projets de R&D liés à l'IA contenus dans 13 bases de
données de financement de huit pays de l'OCDE et de l'UE, fournit des estimations du
nombre total et du volume de financement public de la R&D, et car actérise le ur
portefeuille de financement de l'IA. Les méthodes et les résultats développés dans cette
étude servent également de prototype à un nouvel mécanisme étendu et distribué
capable de mesurer et d'analyser le soutien gouvernemental à la R&D sur divers sujets
prioritaires pour l’OCDE et ses pays membres.
Mots-clés : recherche et développement, financement public, intelligence artificielle

### PDF页 9

MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS | 9

OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

Executive summary
This document reports on the procedures and findings from an experimental text-based
analysis of project -level research and development ( R&D) funding data, focused on
measuring the extent and features of government R&D support for Artificial
Intelligence (AI -related R&D). The field of AI research has undergone a radical
transformation in the past two decades, morphing from a small, relatively niche
domain into a sprawling web of ground-breaking innovations. Mapping and measuring
this research explosion – and the funding underlying its ignition – is of prime
importance to policy makers and experts, as is encouraging its further development
towards the common good. The 2019 OECD Council Recommendation on Artificial
Intelligence states that governments “should consider long -term public investment,
and encourage private investment, in research and development, including
interdisciplinary efforts, to spur innovation in trustworthy AI” . Tracking government
investments into R&D is therefore of particular importance. While attempts have been
made to assess government spending on AI -related R&D, mostly throu gh proxy
approaches, no comprehensive method exists by which to track and compare AI R&D
funding across countries and agencies.
The study has used a quantitative case study approach, applying a set of text mining
tools to specific project funding databases to identify AI -related R&D. The project -
level funding data of 13 databases from eight OECD countries (Australia, Canada,
France, Japan, the Netherlands, Spain, the United Kingdom and the United States) and
the European Union provided useful and relevant ground for demonstration purposes.
R&D project funding databases, while not indicative of total government R&D
funding, can be used to trace and estimate a sizeable part of total government funding
of AI-related R&D, thereby helping support implementation of the OECD Council
Recommendation.
This study has adopted a “key terms” selection and matching approach for the
identification of AI-related R&D projects by each organisation within the text corpus
of their funded R&D projects. The task was to predict, using project titles and abstracts,
whether or not a project was AI -related. Key term selection aimed to deliver a
comprehensive list of AI-relevant key terms for document matching. A baseline set of
potential key terms was enriched by means of text analysis applied first to a separate
relevant body of scientific publication abstracts and then to the project funding text
corpora that were the object of this study. A document was categorised as AI -related
depending on the presence of key terms within it.
The total volume of AI -related government R&D funding identified through this
exercise grew from USD 207 million in 2001 to almost USD 3.6 billion in 2019, a
seventeen-fold increase. While this represents a very large amount, it may be dwarfed
by business R&D investment if one considers that a single heavily AI-reliant company
like Alphabet reported USD 20 billion worth of total R&D expenses in 2018, and the
United States National Center for Science and Engineering Statistics provided a
conservative estimate of business AI R&D investment in the order of USD 9 billion
out of over USD 160 billion worth of total software R&D . Much of this surge in
government funding is concentrated in recent years, with EU funding doubling in
2019. This pattern has had some ups and downs, however, reflecting the lumpiness of
some large projects sponsored by R&D funding agencies and showing the importance
of considering monetary measures as well as counts-based indicators.

### PDF页 10

10 | MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS

OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

When comparing sheer amounts of AI -related R&D funding by these agencies or
bodies, the funding mechanisms covered by the EU’s Community Research and
Development Information Service (CORDIS) have very recently become the single
largest source, followed closely by the US’s National Institutes of Health ( NIH) and
its National Science Foundation (NSF). These two US agencies account for over three
quarters of the cumulative AI R&D funding documented in this e xercise. A different
hierarchy emerges when examining the percentage of each agency’s total R&D
spending that is accorded to AI research, an indicator of AI R&D funding intensity.
By this measure, the leading agencies are NSF, the UK Research Councils, the Dutch
Research Council (NWO), and Innovate UK, each of which dedicated in 2019 between
10% and 15% of total R&D funding to AI-related projects.
The results clearly show that AI is not exclusively of interest to computer science and
engineering funding agencies. To illustrate this point, the paper uses a statistical topic
modelling technique to identify common topics (and group documents by these topics)
on each database. The topics correspond to five broad themes: general AI techniques,
AI prerequisites and impact (such as education and training and social impact), AI
fields (such as computer vision and natural language processing), medical AI
applications, and non- medical AI applica tion areas (such as business and the social
sciences). A round half of the funding streams for AI R&D projects focused most
frequently on particular fields or techniques (e.g. computer vision), while the other half
were principally concerned with particular applications of AI, either of a
health/medical nature in the case of the three medical agencies covered and the funding
streams incorporating support for business R&D and innovation.
This work also represents a pilot exercise in assessing the feasibility of constructing a
multi-country infrastructure on R&D project funding for analytical purposes .
Identifying emerging R&D domains and application areas is key in light of heightened
interest in the directionality of R&D support by governments. The study has shown
that decentralised, collaborative distributed approaches are possible and can deal with
confidentiality considerations. Advances in data harmonisation are nonetheless
necessary in order to enable future longitudinal and cross -country analysis. Different
and evolving patterns of reporting and describing projects in application abstracts can
lead to marked differences in results of text mining approaches. All these issues will
be part of the remit of future OECD work on analysis of administrative STI financing
data, in fulfilment of the OECD Blue Sky agenda for indicators.
AI is far from being the only research field that evades easy definitions but whose
emergence remains critical to track. This pilot study will serve as a prototype for taking
on the development of broader analysis mechanisms capable of assessing government
contributions to a myriad of fields and applications, including pandemic resilience
objectives and outcomes connected with the UN Sustainable Development Goals.

## T1_国家研发与方向设定

- PDF页1：OECD Science, Technology and Industry Working Papers 2021/09 Measuring the AI content of government-funded R&D projects: A proof of concept for the OECD Fundstat initiative Izumi Yamashita, Akiyoshi Murakami, Stephanie Cairns, Fernando Galindo-Rueda https://dx.doi.org/10.1787/7b43b038-en

- PDF页2：2 | MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS OECD Working Papers should not be reported as representing the official views of the OECD or of its member countries. The opinions expressed and arguments employed are those of the authors. Working Papers describe preliminary results or research in progress by the author(s) and are published to stimulate discussion on a broad range of issues on which the OECD works. Comments on Working Papers are welcomed, and may be sent to Director ate for

- PDF页3：MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS | 3 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Acknowledgements This report was prepared by Izumi Yamashita, Akiyoshi Murakami, Stephanie Cairns and Fernando Galindo-Rueda while they were based at the Science and Technology Policy (STP) Division in the OECD Directorate for Science, Technology and Innovation (DSTI). Brigitte van Beuzekom facilitated the use of bibliometric data to complement the analysis. This study has been part of the Programme of Work and Budget of the Committee for

- PDF页4：4 | MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Table of contents Acknowledgements .................................................................................................................... 3 Abstract ...................................................................................................................................... 8 Synthèse ...................................................................................................................................... 8

- PDF页4：......................................................................................................... 9 Résumé ..................................................................................................................................... 11 Measuring the AI content of government funded R&D projects: A proof of concept for the OECD Fundstat initiative ................................................................................................. 14 1. Introduction and background ............................................................................................ 14 2. AI-related project retrieval methodology.......................................................................... 18 2.1. Project funding data .......................................................................

- PDF页5：MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS | 5 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS NIH (USA) ......................................................................................................................... 57 NSF (USA) ......................................................................................................................... 57 CORDIS (EU) .................................................................................................................... 57 Annex B. Key terms selection ...........

- PDF页6：6 | MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Table D.1. Precision analysis of AI detection results in NIH and NSF data ........................... 101 Table D.2. False omission analysis of AI detection results in NIH and NSF data .................. 103 Figures Figure 2.1. Outline of Key AI term identification and tagging procedure ................................ 29 Figure 2.2. Cluster representation of base key AI terms from M- and C-lists .......................... 30 Figure 2.3. Clus

- PDF页7：MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS | 7 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Figure C.18. Topics from the AI-related documents of KAKEN with relative topic prominence in different periods, 2001-2018 ......................................................................................... 89 Figure C.19. Estimates of AI-related NWO funding ................................................................. 90 Figure C.20. Topics from the AI-related documents of NWO with relative topic prominence, 2016-2019 ..........

## T2_市场与产业政策边界

- PDF页9：resence of key terms within it. The total volume of AI -related government R&D funding identified through this exercise grew from USD 207 million in 2001 to almost USD 3.6 billion in 2019, a seventeen-fold increase. While this represents a very large amount, it may be dwarfed by business R&D investment if one considers that a single heavily AI-reliant company like Alphabet reported USD 20 billion worth of total R&D expenses in 2018, and the United States National Center for Science and Engineering Statistics provided a conservative estimate of business AI R&D investment in the order of USD 9 billion out of over USD 160 billion worth of total software R&D . Much of this surge in government funding is concentrated in recent years, with EU funding doubling in 2019. This pattern has had some ups and downs

- PDF页10：ly on particular fields or techniques (e.g. computer vision), while the other half were principally concerned with particular applications of AI, either of a health/medical nature in the case of the three medical agencies covered and the funding streams incorporating support for business R&D and innovation. This work also represents a pilot exercise in assessing the feasibility of constructing a multi-country infrastructure on R&D project funding for analytical purposes . Identifying emerging R&D domains and application areas is key in light of heightened interest in the directionality of R&D support by governments. The study has shown that decentralised, collaborative distributed approaches are possible and can deal with confidentiality considerations. Advances in data harmonisation are nonetheless n

- PDF页14：onal and international levels owing to its combined transformational and disruptive effects. Government support for R&D has been central to the development of AI capabilities. According to the US National Research Council (NRC, 1999[2]), while the concept of AI originated in the private sector, its growth depended largely on public investments, from fundamental, long-term research into cognition to shorter-term efforts to develop operational systems. Leading government agencies included the Defense Advanced Research Projects Agency (DARPA), the National Institutes of Health (NIH), the National Science Foundation (NSF), and the National Aeronautics and Space Administration (NASA), which have pursued AI applications of particular relevance to their missions. From the 1960s through to the 1990s, DARPA prov

- PDF页15：ure than government expenditure. It might appear that this is due to the fact that individual government agencies may themselves lack the admin istrative data infrastructure and mandate that allows them 2 A number of countries have experimented with AI related questions in their business R&D and i nnovation surveys, using different definitions . There is at present no international consensus on how such data should be collected. At the 2019 NESTI workshop on innovation surveys and the implementation of the 2018 Oslo Manual, participants consistently highlighted this topic as a high priority for addressing recommendations on measuring “digital innovation”. Different examples for business ICT surveys have been documented in OECD (2021), “AI Measurement In ICT Usage Surveys: A Review”, OECD Digital Econo

- PDF页19：, most of the organisations operate primarily in the basic and applied research space of the R&D spectrum, fostering advances in fundamental knowledge and research into potential applications while refraining from funding the experimental development of products or processes for commercialisation. A number of projects may include activities that do not fully qualify as R&D, such as other types of S&T or innovation activities. For the selected agencies, this may be particularly the case of S&T infrastructure projects, but as such projects are primarily intended to contribute to R&D activities, no attempt was made to identify and remove them. • All of the organisations provide financial support in the form of grants, cooperative agreements, and contracts, making extensive use of peer review as a resource all

- PDF页46：and JPN AMED are grouped on the left end of the horizontal axis , which reflects their status as medical agencies. It can also be construed that USA NSF funds projects related to “ AI in society ”, while GBR GtR Innovate UK focuses on AI applications, especially those related to business R&D and innovation. AUS CAN CAN ESP FRA GBR GBR JPN JPN NLD USA USA EU ARC CIHR NSERC PlanEst ANR GtR_Inno GtR_RC AMED KAKEN NWO NIH NSF CORDIS 1. General AI techniques 1.1 General AI techniques 31% 0% 14% 7% 16% 0% 14% 0% 14% 9% 0% 14% 9% 2. AI prerequisites and impact 2.1 Education and training 0% 0% 0% 0% 0% 0% 9% 0% 10% 0% 8% 16% 8% 2.2 Social impact 0% 16% 0% 0% 0% 0% 9% 0% 0% 11% 0% 5% 0% 2.3 Cost/production/monitoring 0% 0% 7% 0% 0% 8% 0% 0% 0% 0% 0% 0% 8% 2.4 Software development 0% 0% 6% 0% 0% 0% 0% 0% 0% 14%

- PDF页47：) Robots/devices (med) JPN AMED FRA ANR AUS ARC CAN CIHR EU CORDIS GBR GtR_Inno GBR GtR_RC JPN KAKEN USA NIH CAN NSERC USA NSF NLD NWO EPS PlanEst -2.5 -2 -1.5 -1 -0.5 0 0.5 1 1.5 -2 -1.5 -1 -0.5 0 0.5 1 1.5 2 Dimension 2 (23.4%) Dimension 1 (41.1%) Health agencies Agencies with business R&D / innovation focus Agencies with AI in society focus

- PDF页49：7 million in 2001 to almost USD 3.6 billion in 2019, a seventeen-fold increase. While this might appear to represent a very large amount, and it does i ndeed represent a significant fraction of the funding streams that have analysed, this sum may be dwarfed by the sheer level of business R&D investment that appears to be taking place in parallel. This is the case if one considers that a single heavily AI-reliant company like Alphabet reported USD 20 billion worth of total R&D expenses in 2018, and the United States National Center for Science and Engineering Statistics has recently provided a conservative estimate of business AI R&D investment in the order of USD 9 billion out of its official estimate of over USD 160 billion worth of R&D on software products and software embedding technologies (NCSES,

## T4_国际合作与开放

- PDF页18：ial exchange of information subject to predefined disclosure rules. Under a universal fully open access model, OECD’s role in this space would be limited, as research groups would be well equipped to analyse such data. However, while there is a widespread shift towards increased openness of R&D funding project microdata, it has become clear that not all agencies are willing to place all potentially relevant data in the public domain. In light of the growing need for the coordination of data exchanges and analysis, the OECD is well positioned to assist in this role, as its experience with national statistical agencies and confidential business survey data through the microBeRD project (OECD, 2020 [16]) shows that distributed analysis mechanisms represent a feasible second-best solution when data co

- PDF页55：d USD 22 256 million between 2004 and 2016. ANR (FRA) The ANR (Agence Nationale de la Recherche) is a French funding organisation founded in 2005, providing funding to R&D projects on basic and targeted research, technological innovation, technology transfer, and public -private partnerships. The 28 The four funding organisations are: State Research Agency, Centre for the Development of Industrial Technology, Institute of Health Carlos III, and Secretariat of State for Digitisation and Artificial Intelligence.

## T5_供应链与技术依赖

- PDF页10：evades easy definitions but whose emergence remains critical to track. This pilot study will serve as a prototype for taking on the development of broader analysis mechanisms capable of assessing government contributions to a myriad of fields and applications, including pandemic resilience objectives and outcomes connected with the UN Sustainable Development Goals.

- PDF页17：ication areas, in light of heightened interest in the directionality of R&D support by gov ernments (OECD, 2021 [14]). There is particularly high interest in measuring the contribution of government R&D funding to narrowly defined Sustainable Development Goals (SDGs) or pandemic resilience. Therefore, beyond the concrete application to AI as the area subject to exploration, this work seeks to address the widespread demand for data resources, tools, and methods that help identify features of R&D funding in thematic areas that are not easily captured by pre -defined and difficult -to-change taxonomies. This exercise is furthermore a demonstration of the possibilities of AI methods for text analysis as complementary detection and classification tools for statistical measurement that enable greater anal

- PDF页22：rary of Medicine). The definition includes a list of potential application tasks and makes explicit reference to the concept of intelligence without defining it. The reference to “normally require HI (human intelligence)” is indicative of the potential subjectivity and context - dependence of the concept. Over time and with growing levels of automation, a number of tasks will ultimately cease to be considered AI depending on who makes the judgement. The OECD Advisory Expert Group on Artificial Intelligence (AIGO) has defined AI not as a standalone concept but by reference to AI systems, namely as “machine- based systems that can, for a given set of human-defined objectives, make predictions, recommendations, or decisions influencing real or virtual environments […]by using machine and/or human-based

- PDF页51：hose emergence remains critical to track. This pilot study will serve as a prototype for this new OECD expert group to take on the development of broader analysis mechanisms capable of assessing government contributions to a myriad of fields and applications, including pandemi c resilience objectives and outcomes connected with the UN Sustainable Development Goals. Last but not least, it is worth noting the potential contributions of this line of work in informing and assisting survey-based measurements. For instance, mixed methods can be deployed that combine data-driven solutions with surveys. The two approaches complement each other: for example, surveys can allow for the construction of better text mining algorithms . Compared to data -driven approaches, surveys can also be more easily modified

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页3：irectorate for Science, Technology and Innovation (DSTI). Brigitte van Beuzekom facilitated the use of bibliometric data to complement the analysis. This study has been part of the Programme of Work and Budget of the Committee for Scientific and Technological Policy (CSTP) and entrusted to the Working Party of Na tional Experts on Science and Technology Indicators (NESTI). The authors would like to express their gratitude towards Cecilia Cabello and Joseba Sanmartín (The Spanish Foundation for Science and Technology, Spain) and Jerónimo Arenas (University Carlos I II of Madrid, Spain) for their support in analysing the Spanish and the European Commission CORDIS data; Alexandra Vennekens, Margot Schel, and Iris Glas (Rathenau Institute, Netherlands) for their support in analysing the Dutch data;

- PDF页5：... 101 Results are fairly robust to the use of alternative lists of key terms ................................. 105 Tables Table 2.1. Main features of the databases analysed .................................................................. 20 Table 2.2. MeSH tree structure for Artificial Intelligence ........................................................ 26 Table 2.3. AI term list from Cockburn et al. (2018) .................................................................. 27 Table 3.1. Classification of agency-specific topics into common themes and topics ............... 44 Table 3.2. Percentage of documents by common AI themes and topics within selected agencies ............................................................................................................................. 46 Table 3.3. Perce

- PDF页8：results of a proof of concept for a new analytical infrastructure (“Fundstat”) for analysing government funding of research and development (R&D) at the project level, exploiting the wealth of text- based information about funded projects. Re flecting the growth in popularity of artificial intelligence (AI) and the OECD Council Recommendation on AI’s emphasis on R&D investment, the report focuses on analysing government investments into AI-related R&D. Using text mining tools, it documents the creation of a list of key terms used to identify AI-related R&D projects contained in 13 funding databases from eight OECD countries and the EU, provides estimates for the total number and volume of government R&D funding, and characterises their AI fundin g portfolio. The methods and findings developed in this study, also

- PDF页8：eloped in this study, also serve as a prototype for a new expanded, distributed mechanism capable of measuring and analysing government R&D support across key priority areas and topics for the OECD and its member countries. Keywords: Research and development, government funding, artificial intelligence Synthèse Ce document présente les résultats d'une preuve de concept pour une nouvelle infrastructure analytique (« Fundstat ») pour analyser le financement gouvernemental de la recherche et développement (R&D) au niveau des projets, en exploitant la richesse des informations textuelles sur les projets financés. Reflétant la popularité croissante de l'intelligence artificielle (IA) et l'accent mis par la Recommandation du Conseil de l'OCDE sur les investissements en R&D, il se concentre sur l'analyse des investisse

- PDF页9：AND INDUSTRY WORKING PAPERS Executive summary This document reports on the procedures and findings from an experimental text-based analysis of project -level research and development ( R&D) funding data, focused on measuring the extent and features of government R&D support for Artificial Intelligence (AI -related R&D). The field of AI research has undergone a radical transformation in the past two decades, morphing from a small, relatively niche domain into a sprawling web of ground-breaking innovations. Mapping and measuring this research explosion – and the funding underlying its ignition – is of prime importance to policy makers and experts, as is encouraging its further development towards the common good. The 2019 OECD Council Recommendation on Artificial Intelligence states that governments “should consi

- PDF页9：ground-breaking innovations. Mapping and measuring this research explosion – and the funding underlying its ignition – is of prime importance to policy makers and experts, as is encouraging its further development towards the common good. The 2019 OECD Council Recommendation on Artificial Intelligence states that governments “should consider long -term public investment, and encourage private investment, in research and development, including interdisciplinary efforts, to spur innovation in trustworthy AI” . Tracking government investments into R&D is therefore of particular importance. While attempts have been made to assess government spending on AI -related R&D, mostly throu gh proxy approaches, no comprehensive method exists by which to track and compare AI R&D funding across countries and agencies. The stu

- PDF页14：14 | MEASURING THE AI CONTENT OF GOVERNMENT FUNDED R&D PROJECTS OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Measuring the AI content of government funded R&D projects: A proof of concept for the OECD Fundstat initiative 1. Introduction and background Artificial intelligence (AI) is transforming many aspects of our lives and influencing many decisions and processes. Rapid advances have resulted from research and development (R&D) efforts and from the widespread adoption of novel AI solutions, which in turn is generating expectations of further transformation and disruption to the way in which societies operate and address their current and future challenges. As reflected in the recent OECD Council Recommendation on Artificial Intelligence (OECD, 2019 [1]), AI is a high priority in pol

- PDF页14：from the widespread adoption of novel AI solutions, which in turn is generating expectations of further transformation and disruption to the way in which societies operate and address their current and future challenges. As reflected in the recent OECD Council Recommendation on Artificial Intelligence (OECD, 2019 [1]), AI is a high priority in policy agendas 1 at both the national and international levels owing to its combined transformational and disruptive effects. Government support for R&D has been central to the development of AI capabilities. According to the US National Research Council (NRC, 1999[2]), while the concept of AI originated in the private sector, its growth depended largely on public investments, from fundamental, long-term research into cognition to shorter-term efforts to develop operation

## T10_预见与优先领域

未自动命中；需人工按目录复核。
