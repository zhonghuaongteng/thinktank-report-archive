# C-OECD-DOI-4889F5F2-EN 原文切片

- 原文：`03_证据底稿\原文PDF\C-OECD-DOI-4889F5F2-EN.pdf`
- PDF页数：67
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 5

MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19  5
OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

Table of contents
Measuring governments’ R&D funding response to COVID-19 ................................ ........ 3
Acknowledgements................................ ................................ ................................ .............. 4
Executive summary................................ ................................ ................................ .............. 8
1 Introduction and background ................................ ................................ ......................... 10
1.1. The COVID-19 pandemic and the R&D funding response ................................ .......... 10
1.2. Understanding the R&D COVID-19 response through project analysis: a motivation
for conducting a proof of concept for the OECD Fundstat initiative ................................ .... 11
1.3. Aim and outline of this study................................ ................................ ....................... 11
2 Data and methodology ................................ ................................ ................................ .... 13
2.1. Project funding data from the Fundstat infrastructure ................................ ................. 13
2.2. COVID-19 R&D analysis methodology ................................ ................................ ....... 17
2.2.1. Retrieval of COVID-19 R&D projects ................................ ................................ .... 17
2.2.2. Topic modelling analysis of COVID-19 R&D projects ................................ ........... 20
3 Features of COVID-19 R&D funding ................................ ................................ ............... 21
3.1. Aggregate estimates of COVID-19 R&D project funding ................................ ............. 21
3.1.1. COVID-19 R&D project counts and funding ................................ ......................... 21
3.1.2. COVID-19 R&D funding in the broader landscape ................................ ............... 21
3.2. Directionality of COVID-19 R&D funding ................................ ................................ .... 25
3.2.1. Funding analysis by machine-generated topic and topic cluster ........................... 25
3.2.2. Funding analysis by agency/data source ................................ .............................. 33
3.2.3. Funding analysis by geographical area ................................ ................................ 36
3.2.4. Analysis of market orientation in COVID-19 R&D funding ................................ .... 38
4 Comparing Fundstat COVID-19 R&D with alternative data sources and expert
classifications ................................ ................................ ................................ .................... 41
4.1. Mapping Fundstat results to the WHO classification of COVID-19 research priorities. 41
4.1.1. Comparing COVID-19 R&D funding estimates from different sources .................. 41
4.1.2. Mapping machine-based topics to WHO research priority areas .......................... 44
4.2. R&D funding and scientific publications on COVID-19................................ ................ 48
4.2.1. Identification of COVID-19 publications in the Scopus database .......................... 48
4.2.2. Comparison with COVID-19 R&D project data ................................ ..................... 50
5 Concluding remarks ................................ ................................ ................................ ........ 52
References ................................ ................................ ................................ .......................... 55
Annex A. Features of the OECD Fundstat database ................................ ........................ 59
Annex B. Bias analysis and robustness checks ................................ .............................. 60

### PDF页 7

MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19  7
OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

Figure B.1. Distribution of length (in number of words) in projects’ combined title and abstract 60
Figure B.2. Relationship of original vs. post-processing length (in number of words) 60
Figure B.3. Sensitivity analysis on the length (number of meaningful words) of post-processed project text
(combined title and abstract) by project topic classification 62
Figure B.4. COVID-19 R&D projects by C34 and other non-specific topics for each country 63
Figure B.5. COVID-19 R&D projects by C34 and non-specific topics by model type and language 63
Figure C.1. COVID-19 R&D projects and funding per year by funding agency/data source 67

### PDF页 8

8  MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19
OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

Executive summary
The COVID-19 pandemic presented the world with a unique and major global public health emergency not
seen in generations. Rising to the challenge, science, technology, and innovation (STI) systems have
played a key role in containing the virus's spread, developing, and deploying vaccines and treatments in
record time, and providing tools and knowledge to help combat the pandemic, mitigating against its
negative impacts. Government support for research and development (R&D) in both public and private
sectors has been instrumental.
Monitoring the governmental R&D funding response is a major priority to help inform collective action both
while a crisis is ongoing and afterwards, to build an evidence base to foster increased resilience against
future pandemics or shocks. Understanding the size and direction of government R&D funding response
in cris es like the COVID-19 pandemi c and having the appropriate data infrastructures to do so are
necessary condition s for realising that vision . The OECD Fundstat initiative emerged to fill this gap ,
prompted by the 2015 OECD Daejeon ministerial declaration and the 2016 OECD Blue Sky Foru m, to
pursue the creation of a flexible international analytical infrastructure to study government R&D funding
directionality. By using data on publicly funded R&D projects, combining both quantitative and qualitative
information, it enables a detailed, granular, and timely analysis of specific policy priorities.
The work presented in this document deployed a range of tools for the integrated analysis of project funding
data to identify government financial support for COVID-19 R&D as an experimental study of R&D funding
directionality. This project set out to: (i) help provide evidence on the composition of COVID -19 R&D
funding provided by government agencies; (ii) demonstrate the use of natural language processing (NLP)
methods to measure directionality fo r policy analysis; and (iii) provide a basis for scaling up the OECD
Fundstat infrastructure and encourage country engagement, collaboration, and mutual learning.
This study provides an in -depth analysis of R&D support portfolios using data from 27 funding sources
from 13 OECD countries and the European Commission (EC) and retrieving funding for COVID -19 R&D
projects approved in 2019 -21. The 11,886 projects identified add up to total government funding of USD
12.59 billion and average funding per project around USD 1.20 million. This represents 4% of R&D project
funding registered in the Fundstat database over that period and 2 % of projects. The application of topic
modelling analysis of the corpus of COVID-19 R&D projects identified 34 distinct topics, grouped into 8
higher level topic clusters which have been labelled as follows: ‘Coronavirus understanding, therapeutics,
and vaccine development', ‘Platforms and capabilities’, ‘Epidemiology and social intervention’, ‘Digital
access and online education’, ‘Cancer (screening and treatment)’, ‘Public healthcare and other groups at
risk’, ‘Mental health and addictions’, and ‘Environmental detection, transmission, and protection’.
While biomedical ( including R&D on virus understanding, development of diagnostics, vaccines, and
treatments) and social science -oriented topics are generally balanced in terms of numbers of projects,
government funding for COVID -19 R&D is primarily focuse d on the former. There is evidence that on
average biomedical projects are larger in terms of funding awards relative to social science-oriented topics.
Funding for R&D platforms and capabilities is significant, and co -occurrence patterns indicate that this
topic plays a pivotal r ole across different areas of COVID -19 R&D. This is particularly relevant as health
and R&D systems seek to build resilience capacity towards future pandemics or attempt to find ways to
apply COVID-19 based discoveries and technologies to other pressing health challenges.

### PDF页 11

MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19  11
OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

1.2. Understanding the R&D COVID-19 response through project analysis: a
motivation for conducting a proof of concept for the OECD Fundstat initiative
When responding to STI systems and policy monitoring, evaluation and appraisal needs, it is important to
note that different types of data are best suited to different purposes. Official statistics on government R&D
budgets are designed from a top -down perspective to capture from high -level administrative finance
documents, on a regular and longitudinally consistent basis, the full range of high-level government policy
priorities to which R&D funds are allocated . Government R&D budget statistics collected by national
authorities and compiled by the OECD apply a mutually exclusive allocation of R&D funding to
socioeconomic objectives that reflects top -level priority setting (OECD, 2015 [17]). One downside is that
these statistics are not designed to capture funding allocations on a granular basis and are therefore not
suited to track funding directed to tackle the COVID -19 pandemic or other specific , context-contingent
subjects.
Echoing discussions at the OECD meeting of science ministers held in Dae jeon in 2015, the OECD Blue
Sky Forum held in 2016 on the future of science and innovation data and indicators posited the possibility
of developing complementary , micro -based pathways focused on the analysis of project -level data to
complement more established means of statistical analysis of R&D funding (OECD, 2015 [18]; OECD,
2018[19]). The notion of an ‘R&D project’ as unit of analysis had already been explicitly introduced in the
2015 edition of the Frascati Manual with the aim of facilitating the reporting of R&D data for R&D statistics
(OECD, 2015[20]). Data about R&D projects can be extremely rich sources of information for policy analysis.
The proposals at the OECD Blue Sky Forum compelled the OECD to promote the active and coordinated
use of data about R&D projects (funding, metadata, and textual descriptions in abstracts), under what
came to be described as the “Fundstat” initiative for a brand new analytical data infrastructure (OECD,
2018[21]).
In contrast with the approach of building ad hoc trackers to address one measurement priority at a time, a
key part of the concept behind Fundstat is the aim to develop a standing but flexible infrastructure suitable
for use as soon as such priorities arise. The semantic context of text-based project descriptions is a critical
element for the implementation of this concept, in combination with the use of machine-supported methods
of classification for projects and the allocated funding amounts to each one of those. This bottom -up,
machine-guided, approach presents unique challenges of its own. These relate to the difficulties in building
up an underlying international database to ensure that it provides an adequately representative basis for
measurement, as well as ensuring that the machine -based or human-assisted methods of classification
are fit for purpose, particularly in context where there is no pre-established consensus on what should be
measured.
The OECD Fundstat infrastructure was first piloted through an analysis of government funding for R&D
projects related to Artificial Intelligence (Yamashita et al., 2021[22]). Direct responsibility for this initiative of
the OECD Working Party of National Experts on Science and Technology Indicators (NESTI) has been
assigned to the recently established OECD Expert Group on the Measurement and Analysis of R&D and
innovation administrative data (MARIAD), which was been created to assist in the pursuit of and quality
assessment of statistical analysis based on administrative data . MARIAD included this initiative within its
action plan going up to 2024 , contributing to the overarching work of the Committee of Scientific and
Technological Policy (CSTP) on science and innovation for resilience and transitions.
1.3. Aim and outline of this study
In this study, quantitative and qualitative tools have been used to identify government funding of COVID-
19 R&D in the Fundstat database , an analytical data infrastructure under continuous development . The
main objectives are to illustrate the level and composition of COVID -19 funding by government agencies,

### PDF页 12

12  MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19
OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS

characterise and address the methodological challenges of identifying COVID -19 relevant R&D projects
from heterogeneous text -based data, and motivate the process of R&D project data sharing at an
international scale. This provides additional motivation for the extension and consolidation of the Fundstat
data infrastructure, helping assess the extent to which R&D project databases represent government R&D
funding and providing the basis for future analysis of other topics . Furthermore, this study aims to
demonstrate the potential of AI methods for the analysis of funding administrative data, as complementary
detection, and classification tools for statistical measurement, enabling greater analysis uniformity and
replicability, providing a tangible milestone in the scaling up of the OECD Fundstat infrastructure and the
development of NLP methods to measure directionality.
The remainder of this paper is thus structured as follows.
• Section 2 provides a brief description of the R&D funding data used for the analysis and the
methodology applied . It describes the pre -identification of R&D projects using key -terms, the
automated machine-based procedure to eliminate projects whose abstracts only make contextual
references to COVID-19 terms, and the topic modelling analysis using natural language processing
(NLP) methods to infer relevant funded COVID-19 R&D topics.
• Section 3 presents the analysis of directionality of COVID-19 funding by topic, cluster, country/area,
funding agency and market/commercial orientation.
• Section 4 compares the results on funding data and the machine-based classification to those of
the COVID-19 Research Project Tracker by UKCDR & GloPID -R, which has been mapped by
experts in global health research against the priorities identified in the WHO Coordinated Global
Research Roadmap for COVID -19 (Bucher et al., 2023 [14]; UKCDR & GloPID -R, 2023 [15]). The
expert classification data are used to train a model that enables the classification of Fundstat data
according to WHO priorities as well as an in -depth analysis of machine and expert classification
patterns. Furthermore, the results are also compared to scientific publications, accounting for the
different factors that underpin differences between R&D input and publication output data.
• Section 5 concludes by outlining the key messages, limitations, and future work.

## T1_国家研发与方向设定

- PDF页1：OECD Science, Technology and Industry Working Papers 2023/06 Measuring governments’ R&D funding response to COVID-19: An application of the OECD Fundstat infrastructure to the analysis of R&D directionality Leonidas Aristodemou, Fernando Galindo- Rueda, Kuniko Matsumoto, Akiyoshi Murakami https://dx.doi.org/10.1787/4889f5f2-en

- PDF页2：2  MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS OECD Science, Technology and Industry Working Papers OECD Working Papers should not be reported as representing the official views of the OECD or of its member countries. The opinions expressed and arguments employed are those of the authors. Working Papers describe preliminary results or research in progress by the author(s) and are published to stimulate discussion on a broad range of issues on which the OECD works. Comments

- PDF页3：MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19  3 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Measuring governments’ R&D funding response to COVID-19 An application of the OECD Fundstat infrastructure to the analysis of R&D directionality This paper presents new evidence on the size and direction of governments’ R&D funding response to the COVID-19 pandemic through the exploration of a novel data infrastructure, the OECD Fundstat initiative for the analysis of government -funded R&D projects . The document reports o

- PDF页3：t topics and classify and allocate project funding according to priorities in the WHO COVID -19 R&D Blueprint, as well as comparing results with similar analysis of scientific publication output data. The results provide new insights on which areas of enquiry were prioritised by governmental R&D funding bodies. Authors: Leonidas Aristodemou, Fernando Galindo-Rueda, Kuniko Matsumoto, and Akiyoshi Murakami Keywords: COVID-19, Government funding, Research and Development (R&D), directionality, topic modelling, classification, large language models JEL codes: C38, C45, O32, O38

- PDF页4：4  MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Acknowledgements This report has been prepared by Leonidas Aristodemou , Fernando Galindo-Rueda, Akiyoshi Murakami, and Kuniko Matsumoto at the Science an d Technology Policy Division in the OECD Directorate for Science, Technology, and Innovation (DSTI). Brigitte van Beuzekom facilitated the use of bibliometric data to complement the analysis. This study has been conducted as part of the Programme of Work and Budget 2021-2022

- PDF页5：MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19  5 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS Table of contents Measuring governments’ R&D funding response to COVID-19 ................................ ........ 3 Acknowledgements................................ ................................ ................................ .............. 4 Executive summary................................ ................................ ................................ .............. 8 1 Introduction and background ..............

- PDF页5：ct funding ................................ ............. 21 3.1.1. COVID-19 R&D project counts and funding ................................ ......................... 21 3.1.2. COVID-19 R&D funding in the broader landscape ................................ ............... 21 3.2. Directionality of COVID-19 R&D funding ................................ ................................ .... 25 3.2.1. Funding analysis by machine-generated topic and topic cluster ........................... 25 3.2.2. Funding analysis by agency/data source ................................ .............................. 33 3.2.3. Funding analysis by geographical area ................................ ................................ 36 3.2.4. Analysis of market orientation in COVID-19 R&D funding ................................

- PDF页6：6  MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS B.1. Length (number of words) of original and processing text fields ................................ . 60 B.2. Sensitivity analysis on the meaningful length ................................ ............................. 62 B.3. Sensitivity analysis on handling multiple languages ................................ ................... 62 B.5. Sense-check of cluster labels using ChatGPT ................................ ............

## T2_市场与产业政策边界

- PDF页8：le in containing the virus's spread, developing, and deploying vaccines and treatments in record time, and providing tools and knowledge to help combat the pandemic, mitigating against its negative impacts. Government support for research and development (R&D) in both public and private sectors has been instrumental. Monitoring the governmental R&D funding response is a major priority to help inform collective action both while a crisis is ongoing and afterwards, to build an evidence base to foster increased resilience against future pandemics or shocks. Understanding the size and direction of government R&D funding response in cris es like the COVID-19 pandemi c and having the appropriate data infrastructures to do so are necessary condition s for realising that vision . The OECD Fundstat initiative em

- PDF页10：HO, 2023 [3]). The pandemic has underscored the importance of science and innova tion to societal capacity to both proactive prepare and reactive ly responds to future crises (WHO, 2020[6]; OECD, 2023[4]). Government financial and non-financial support for R&D in both public and private sectors has been pivotal to the rapid development of tools (e.g., vaccines, therapeutics, and diagnostics) and knowledge (e.g., virus understanding, epidemiological monitoring, and social behavioural insights). This response would not have been possible without a solid foundation of scientific and technical knowledge built over decades and also supported by government funding programmes. All this combined has been crucial in helping the world to overcome the several challenges posed by the COVID-19 pandemic (Tietze et al

- PDF页26：d by the topic model, corresponding to a total funding amount of approximately USD 11 billion out of 12.59 billion. Examination of projects with a high residual content that cannot be categorized into the 34 topics generated by the model indicates a high incidence of support for business R&D for economic and technological resilience (see section 3.2.4 and Figure 15) at the boundaries of the COVID -19 relevance definition operationalised in this study. Because of differences in the average project award across documents with different residual content, on a fractional calculation basis, COVID-19 R&D project content assigned to the core body of 34 well-defined COVID-19 topics displays a slightly higher average funding amount per project than content allocated to other non-specific topics. Table 8. COVID

- PDF页33：n agencies within a country can often match similar comparisons within other countries in terms of their specialisation patterns. This for instance the case of Japanese agencies JPN_AMED and JPN_KAKEN (data source principally covering JSPS funding) vis a vis USA_NIH and USA_NSF. Business R&D and innovation -funding agencies such as covered under GBR_GtR_Innovate_UK and SWE_SWECRIS_Vinnova exhibit a broad spectrum of project topic allocations as well as somewhat significant shares of non -specific content. The EU -EC CORDIS source, which com bines research and experimental development funding, presents a more balanced distribution across topics. It also displays a rather significant share of Topic B funding. Social science-oriented agencies such as CAN_SSHRC, allocate higher project and funding towards

- PDF页38：The key-terms are then used to search within the projects’ processed text that combines the title and abstract and are shown in Table 11. Table 11. Business and market-oriented experimental vocabulary of key-terms Set1 Number of key terms Key terms2,3 Base 33 adoption, business, commercialisation, competitive, consumer, corporate, corporation, diffusion, enterprise, entrepreneurship, expenditure, feasibility study, firm, industry, innovation, intellectual property, investment, IPR, joint venture, license, management, manufacture, market, model, process, product, production, service, spinoff, start-up, strategy, technology, technology transfer Extension 13 adjustment, clause, condition, deliverable, delivery, extension, external, issue, platform, procure, purchase, requirement, transaction Total 46 Notes: 1

- PDF页40：‘Epidemiology and social interventions’, and cluster B ‘Platforms and capabilities’ for both the share of business -oriented R&D projects and funding. In both these clusters, the share of business-oriented R&D is higher than the average, which potentially signal a drive towards business R&D. It is also interesting to note that clusters D ‘Digital access and online education’, G ‘Mental health and addictions’, H ‘E nvironmental detection transmission and protection’ also have a relatively high share of business -oriented R&D projects and funding within cluster. This also applies to projects classified in other non-specific topics. Figure 15. Business-oriented COVID-19 R&D by C8 cluster Notes: 1 Analysis limited to the retained COVID-19 R&D projects. Data are based on Table 10 and Figure 8. 2 The calcu

## T4_国际合作与开放

- PDF页8：OVID -19 R&D funding provided by government agencies; (ii) demonstrate the use of natural language processing (NLP) methods to measure directionality fo r policy analysis; and (iii) provide a basis for scaling up the OECD Fundstat infrastructure and encourage country engagement, collaboration, and mutual learning. This study provides an in -depth analysis of R&D support portfolios using data from 27 funding sources from 13 OECD countries and the European Commission (EC) and retrieving funding for COVID -19 R&D projects approved in 2019 -21. The 11,886 projects identified add up to total government funding of USD 12.59 billion and average funding per project around USD 1.20 million. This represents 4% of R&D project funding registered in the Fundstat database over that period and 2 % of projects. The ap

- PDF页9：h expert labelling can facilitate a more comprehensive understanding of the government R&D funding landscape. • In light of reported c overage limitations and missing information, there would be major analytical benefits from encouraging funding agencies to converge towards data openness and, whenever possible, use of common core metadata, for accountability and analysis purposes. The experience of using large language models for processing text data in this study showcases pivotal advancements in statistical and pol icy analysis as well as several implementation and interpretation challenges. This methodology opens the possibility of application to other R&D policy challenges . The careful integration of generative artificial intelligence (AI) tools can help monitor trends swiftly and anticipate

- PDF页10：ing towards ensuring preparedness and resilience of health systems, with specific emphasis on the health science and innovation subsystem. For example, the Japan-hosted G7 Science and Technology Ministers’ Communique of May 2023 alluded to the possibility “[through international collaboration in research and innovation]…to collectively address urgent global health issues such as the need to develop safe and effective medical countermeasures (MCMs) in the event of a future pandemic as promoted through the 100 Days Mission, including vaccines, diagnostics, and therapeutics, to combat infectious disease threats, as well as tools to address other shared health bu rdens like cancer ” (G7, 2023[16]). Given the plethora of policy questions about how best to deploy and direct R&D funding in response to and ant

- PDF页52：spects of governments’ response to the pandemic; (ii) help demonstrate the use of natural language processing (NLP) methods to measure directionality for policy analysis; and (iii) pr ovide a basis for scaling up the OECD Fundstat infrastructure and encourage country engagement, collaboration, and mutual learning. This study has provided an in-depth analysis of funding for COVID-19 R&D projects approved in 2019-21 representing total funding in the order of about USD 12.59 billion and average funding per project of ca USD 1.20 million. While several of the results presented confirm existing literature and public debate , particularly in relation to the broad understanding of the allocation of COVID-19 R&D resources between biomedical and other topics, there are many findings in this report that call for

- PDF页52：ely concerned with addressing a particular societal challenge such as COVID -19. One implication is that there would be major analytical benefits from having funding agencies converging towards better harmonised project summary descriptions while progressing towards greater data openness for accountability and analysis. The use of large language models to process text data has provided several valuable lessons on the conduct of such type of work for statistical and policy analysis . With the rising awareness of the challenges and opportunities of generative AI tools, it is imperative to develop and adopt a set of good practices in relation to the production and use of intelligence that draws upo n these techniques. The work on the underlying data and methodological infrastructure that has underpin

- PDF页61：asierten COVID-19-Impfstoffs (BNT162) 11 infektion covid -19 vaccine beschleunigte entwicklung bereitstellung basierten impfstoffs 8 USA NIH 393.95 HVTN 405/HPTN 1901 Charact erizing SARS-CoV-2-specific immunity in convalescent individuals… HIV Vaccine Trials Network (HVTN), the collaboration of physician scientists at 64 clinical trial sites in 15 countries on 4 continents dedicated to developing globally effective vaccines fo r HIV, tuberculosis and now SARS -CoV-2. The HVTN has led HIV prevention science for over 20 years through robust phase 1 and 2 clinical development trials and currently has 2 vector based vaccines… 238 characterize sars -cov-2 immunity convalescent outline scientific agenda vaccine trial physician scientist clinical trial continent dedicate globally vaccine tuberculosis prevent

## T5_供应链与技术依赖

- PDF页8：arch and development (R&D) in both public and private sectors has been instrumental. Monitoring the governmental R&D funding response is a major priority to help inform collective action both while a crisis is ongoing and afterwards, to build an evidence base to foster increased resilience against future pandemics or shocks. Understanding the size and direction of government R&D funding response in cris es like the COVID-19 pandemi c and having the appropriate data infrastructures to do so are necessary condition s for realising that vision . The OECD Fundstat initiative emerged to fill this gap , prompted by the 2015 OECD Daejeon ministerial declaration and the 2016 OECD Blue Sky Foru m, to pursue the creation of a flexible international analytical infrastructure to study government R&D funding dir

- PDF页8：to social science-oriented topics. Funding for R&D platforms and capabilities is significant, and co -occurrence patterns indicate that this topic plays a pivotal r ole across different areas of COVID -19 R&D. This is particularly relevant as health and R&D systems seek to build resilience capacity towards future pandemics or attempt to find ways to apply COVID-19 based discoveries and technologies to other pressing health challenges.

- PDF页10：ines (EU/OECD, 2022[11]; Policy Cures Research, 2020 [12]; INGSA, 2020[13]; Bucher et al., 2023[14]; UKCDR & GloPID-R, 2023[15]). Looking ahead, while there are many concrete lessons to be drawn from the COVID-19 experience, the focus is turning towards ensuring preparedness and resilience of health systems, with specific emphasis on the health science and innovation subsystem. For example, the Japan-hosted G7 Science and Technology Ministers’ Communique of May 2023 alluded to the possibility “[through international collaboration in research and innovation]…to collectively address urgent global health issues such as the need to develop safe and effective medical countermeasures (MCMs) in the event of a future pandemic as promoted through the 100 Days Mission, including vaccines, diagnostics, and the

- PDF页11：d quality assessment of statistical analysis based on administrative data . MARIAD included this initiative within its action plan going up to 2024 , contributing to the overarching work of the Committee of Scientific and Technological Policy (CSTP) on science and innovation for resilience and transitions. 1.3. Aim and outline of this study In this study, quantitative and qualitative tools have been used to identify government funding of COVID- 19 R&D in the Fundstat database , an analytical data infrastructure under continuous development . The main objectives are to illustrate the level and composition of COVID -19 funding by government agencies,

- PDF页26：al funding amount of approximately USD 11 billion out of 12.59 billion. Examination of projects with a high residual content that cannot be categorized into the 34 topics generated by the model indicates a high incidence of support for business R&D for economic and technological resilience (see section 3.2.4 and Figure 15) at the boundaries of the COVID -19 relevance definition operationalised in this study. Because of differences in the average project award across documents with different residual content, on a fractional calculation basis, COVID-19 R&D project content assigned to the core body of 34 well-defined COVID-19 topics displays a slightly higher average funding amount per project than content allocated to other non-specific topics. Table 8. COVID-19 R&D into defined (C34) and non-specifi

- PDF页52：of the funding awards . Another important insight concerns the saliency and economic significance of R&D projects that seek to build platforms and infrastructures for work on different pandemic R&D priorities. This is particularly relevant as health and R&D systems seek to build resilience towards future pandemics or attempt to find ways to apply and r epurpose COVID-19 based discoveries and technologies to address other pressing health challenges. This study has also provided several methodological insights, from addressing the challenges of defining and implementing studies that seek to capture R&D related to specific policy interest, reconciling evidence from multiple data sources (e.g., funding databases and publications , different agencies, and countries, and implementing and reconciling machi

- PDF页55：for analysing intellectual property (IP) data”, World Patent Information, Vol. 55, pp. 37-51, https://doi.org/10.1016/j.wpi.2018.07.002. [26] Astorga-Pinto, S., E. Hewlett and P. Haywood (2023), “Protecting mental health”, in Ready for the Next Crisis? Investing in Health System Resilience, OECD Publishing, Paris, https://doi.org/10.1787/0f76c6be-en. [40] Baden, L. et al. (2021), “Efficacy and Safety of the mRNA-1273 SARS-CoV-2 Vaccine”, New England Journal of Medicine, Vol. 384/5, pp. 403-416, https://doi.org/10.1056/nejmoa2035389. [35] Berchet, C., E. Barrenho and K. de Bienassis (2023), “Preserving continuity of care”, in Ready for the Next Crisis? Investing in Health System Resilience, OECD Publishing, Paris, https://doi.org/10.1787/5d015a71-en. [39] Bucher, A. et al. (2023), “A living mapping r

- PDF页55：the mRNA-1273 SARS-CoV-2 Vaccine”, New England Journal of Medicine, Vol. 384/5, pp. 403-416, https://doi.org/10.1056/nejmoa2035389. [35] Berchet, C., E. Barrenho and K. de Bienassis (2023), “Preserving continuity of care”, in Ready for the Next Crisis? Investing in Health System Resilience, OECD Publishing, Paris, https://doi.org/10.1787/5d015a71-en. [39] Bucher, A. et al. (2023), “A living mapping review for COVID-19 funded research projects: two year update”, Wellcome Open Research, Vol. 5, p. 209, https://doi.org/10.12688/wellcomeopenres.16259.9. [14] EU/OECD (2022), STIP Compass COVID-19 Watch, https://stip.oecd.org/covid/ (accessed on 1 May 2023). [11] Florio, M., S. Gamba and C. Pancotti (2023), “Mapping of long-term public and private investments in the development of Covid-19 vaccines, publi

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页4：to complement the analysis. This study has been conducted as part of the Programme of Work and Budget 2021-2022 of the Committee for Scientific and Technological Policy (CSTP) under aegis of the Working Party of National Experts on Science and Technology Indicators (NESTI) and entrusted to the Expert Group on the Management and Analysis of R&D a nd Innovation Administrative Data (MARIAD). Earlier versions of the document were presented for discussion in the September 2022 NESTI meeting, November 2022 MARIAD meeting, March 2023 OECD-MABIS project workshop and March 2023 CSTP meeting. The authors would like to express their gratitude towards MARIAD and NESTI delegates and to their respective Bureaus for their feedback. In addition, some of the analysis in this study would not have been possible w

- PDF页9：ext data in this study showcases pivotal advancements in statistical and pol icy analysis as well as several implementation and interpretation challenges. This methodology opens the possibility of application to other R&D policy challenges . The careful integration of generative artificial intelligence (AI) tools can help monitor trends swiftly and anticipate R&D needs in other urgent areas . The work on Fundstat by the NESTI MARIAD group will continue to foster the responsible development of the underlyin g data infrastructure and application of these methodologies.

- PDF页11：human-assisted methods of classification are fit for purpose, particularly in context where there is no pre-established consensus on what should be measured. The OECD Fundstat infrastructure was first piloted through an analysis of government funding for R&D projects related to Artificial Intelligence (Yamashita et al., 2021[22]). Direct responsibility for this initiative of the OECD Working Party of National Experts on Science and Technology Indicators (NESTI) has been assigned to the recently established OECD Expert Group on the Measurement and Analysis of R&D and innovation administrative data (MARIAD), which was been created to assist in the pursuit of and quality assessment of statistical analysis based on administrative data . MARIAD included this initiative within its action plan going up to 2024 , contr

- PDF页44：oriented R&D projects to total R&D projects, which could also be driven by its broad definition (WHO, 2020[6]). In terms of market orientation intensity within topics, WHO 5 ‘Infection, prevention and control’ has the highest share of market-oriented R&D projects, whereas WHO 8 ‘Ethics’ has the highest share of market-oriented R&D funding, albeit based on rathe r small body of project content. Vaccines exhibits the highest market orientation intensity among the priorities accounting for a significant share of the funding. It is important to note that this analysis does not use a predictive model to identify and d istinguish contextual appearances of the market-oriented keyterms. Figure 17. Business-oriented COVID-19 R&D by WHO priority topic Notes: 1 Analysis limited to the retained Fundstat COV

- PDF页55：MEASURING GOVERNMENTS’ R&D FUNDING RESPONSE TO COVID-19  55 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS References Abadi, H., Z. He and M. Pecht (2020), “Artificial Intelligence-Related Research Funding by the U.S. National Science Foundation and the National Natural Science Foundation of China”, IEEE Access, Vol. 8, pp. 183448-183459, https://doi.org/10.1109/access.2020.3029231. [28] Agarwal, R. and P. Gaule (2022), “What drives innovation? Lessons from COVID-19 R&D”, Journal of Health Economics, Vol. 82, p. 102591, https://doi.org/10.1016/j.jhealeco.2022.102591. [9] Annapureddy, A. et al. (2020), “The National Institutes of Health funding for clinical research applying machine learning

- PDF页55：istodemou, L. (2020), Identifying Valuable Patents: A Deep Learning Approach, University of Cambridge, Cambridge, https://doi.org/10.17863/CAM.69403. [48] Aristodemou, L. and F. Tietze (2018), “The state-of-the-art on Intellectual Property Analytics (IPA): A literature review on artificial intelligence, machine learning and deep learning methods for analysing intellectual property (IP) data”, World Patent Information, Vol. 55, pp. 37-51, https://doi.org/10.1016/j.wpi.2018.07.002. [26] Astorga-Pinto, S., E. Hewlett and P. Haywood (2023), “Protecting mental health”, in Ready for the Next Crisis? Investing in Health System Resilience, OECD Publishing, Paris, https://doi.org/10.1787/0f76c6be-en. [40] Baden, L. et al. (2021), “Efficacy and Safety of the mRNA-1273 SARS-CoV-2 Vaccine”, New England Journal of Medicine,

## T10_预见与优先领域

- PDF页11：nge of high-level government policy priorities to which R&D funds are allocated . Government R&D budget statistics collected by national authorities and compiled by the OECD apply a mutually exclusive allocation of R&D funding to socioeconomic objectives that reflects top -level priority setting (OECD, 2015 [17]). One downside is that these statistics are not designed to capture funding allocations on a granular basis and are therefore not suited to track funding directed to tackle the COVID -19 pandemic or other specific , context-contingent subjects. Echoing discussions at the OECD meeting of science ministers held in Dae jeon in 2015, the OECD Blue Sky Forum held in 2016 on the future of science and innovation data and indicators posited the possibility of developing complementary , micro -based pathwa

- PDF页13：g of projects by applicants or administrators is potentially subject to error and inconsistent applications of definitions, a problem that can impact indicators based on administrative data, particularly those that rely on machine -learning based analysis procedures. In an ideal scenario, project descriptions would be available in full and not just limited to abstracts, but confidentiality restrictions apply. In the same scenario, project a bstracts should provide sufficient and standardised information allowing managers and analysts to discern at least the foundations, methods and key expected findings of a given project. The Fundstat infrastructure of government R&D funding projects is an entity under continuous development within the OECD Directorate for Science, Technology, and Innovation unde
