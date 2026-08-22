# C-OECD-DOI-BAFCDC7B-EN 原文切片

- 原文：`03_证据底稿\原文PDF\C-OECD-DOI-BAFCDC7B-EN.pdf`
- PDF页数：63
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 3

ASSESSING THE RELEVANCE OF R&D FUNDING TOWARDS SOCIETAL GOALS  3

 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS © OECD 2025

Abstract
This paper presents and demonstrates a novel approach for assessing the
relevance of public R&D funding towards societal goals. The approach relies
on the development of a new machine learning classification model for R&D
activity descriptions , trained on researchers’ self-assessments about the
relevance of their R&D activity towards Sustainable Development Goals
(SDGs). Applied to R&D project descriptions in the OECD Fundstat
database, the model shows how funding , including for basic research,
contributes towards societal goals. The analysis allows to compare funding
portfolios and provides evidence of the interdependencies between societal
goals served by R&D funding and its potential to contribute to multiple goals.

Authors: Leonidas Aristodemou, Silvia Appelt, Brigitte van Beuzekom, Fernando Galindo-Rueda
Keywords: Research and Development (R&D), Government R&D funding, Machine Learning, Language
Models, Sustainable Development Goals (SDGs), Survey data, Classification, Directionality
JEL codes: O38, O32, C38, C45, Q55

### PDF页 5

ASSESSING THE RELEVANCE OF R&D FUNDING TOWARDS SOCIETAL GOALS  5

 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS © OECD 2025

Table of contents
Abstract 3
Acknowledgements 4
Table of contents 5
Executive summary 7
1 Introduction 9
2 Mapping the contribution of science, technology and innovation to societal goals 11
2.1. Perspectives for assessing the directionality and relevance of STI towards societal goals 11
2.2. SDGs and related work on SDG classification for STI activity 12
2.2.1. Using SDGs to measure societal goals of R&D 12
2.2.2. General SDG mapping approaches for STI efforts 13
2.2.3. Keyword and AI assisted classification approaches 14
3 Data sources for assessing relevance 16
3.1. Classification training data 16
3.1.1. OECD International Survey of Science (ISSA) 16
3.1.2. Scopus bibliometric database on scientific publications 16
3.2. Classification evaluation data 17
3.2.1. OpenAlex database on scholarly metadata 17
3.2.2. OSDG community dataset on SDG-labelled text excerpts 18
3.3. Analysis data 18
3.3.1. OECD Fundstat database on R&D funding awards 18
3.3.2. Scopus bibliometric database on scientific publications 20
4 Developing a new classifier for the relevance of R&D to goals 21
4.1. Model development 21
4.2. Model evaluation 23
4.2.1. Alignment of self-assessed with other science SDG classifiers 23
4.2.2. Evaluation with generic SDGs tagged content 24
5 Results 25
5.1. Relevance of R&D funding and scientific publications towards goals 25
5.1.1. Results across funding sources 25
5.1.2. Mapping the R&D funding landscape according to societal goals 27
5.1.3. Profiling of funding sources by societal goals 28
5.1.4. Experimental results by geographical areas 31
5.1.5. Relevance trends for R&D funding and scientific publications 33
5.2. SDG R&D topics and interdependencies 38
5.2.1. Topic modelling of R&D projects relevant to Energy and Planet SDGs 38
5.2.2. Interdependencies in R&D funding between SDGs 40

### PDF页 7

ASSESSING THE RELEVANCE OF R&D FUNDING TOWARDS SOCIETAL GOALS  7

 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS © OECD 2025

Executive summary
What do billions of government investment in research and development (R&D) across OECD countries
contribute to? Traditionally, such question was only addressed through the prism of established
classifications at a high level of aggregation . Available statistics, whilst providing a comprehensive
benchmark, leave unanswered several questions about the relevance of R&D funding towards specific and
evolving societal goals.
To respond to such needs, the OECD has developed the Fundstat analytical infrastructure to develop and
demonstrate approaches for working with administrative R&D microdata and AI tools for analysis of
quantitative and qualitative dat a in conjunction with traditional methods. This paper presents a decisive
step in the Fundstat initiative towards developing tools that can help provide evidence on the directionality
and relevance of R&D funding.
Evidence on the potential contribution of R&D to different societal goals is crucial for assessing the balance
and orientation of R&D and innovation policies. Yet, providing informative indicators remains challenging
because support for R&D can influence the attainment of such goals through multi ple and often indirect
channels. AI-based classification methods applied to administrative data, while promising, are often reliant
on superficial text features and tend to equate lexical similarity with relevance. Moreover, the widespread
absence of expli cit “goal” language in R&D activity descriptions leads to low measured rates of SDG
relevance. Such approaches may understate the relevance of R&D, particularly basic and some forms of
applied research, to outcomes that indirectly advance societal objectives.
To overcome these limitations, this study introduces a n AI-based approach that is trained on effective
domain-informed assessments of goal relevance for R&D. Close to 2 000 participants in the 2021 OECD
International Survey of Science (ISSA2021) reported which Sustainable Development Goal ( SDG), or
none, they contributed to with their research. As it touches on virtually all areas of government policy, the
UN SDG framework provides a convenient and relevant use case in the classification of unstructured R&D
activity by goals. The survey data helped label a corpus of over 1 1 000 academic publications , which
served in turn as the training dataset for fine -tuning SciBERT, a pre-trained domain-specific transformer-
based language model (trained on a large corpus of scientific literature), into predicting goal relevance
probability for a given text description. This yield ed a model capturing relationships between research
content and relevance towards the 17 SDG objectives, as well as the absence of SDG relevance.
The classifier, deployed on the Scopus custom database of scientific publications and the latest version of
the OECD Fundstat , provides a basemap for the R&D landscape comprising approximately 2.1 million
government-funded R&D project awards across 19 OECD countries and the European Union (EU)
programmes implemented by the European Commission (EC ), accounting for approximately USD 1.5
trillion in public R&D funding, between 2015-2023.
The results indicate that over half of total R&D funding between 2015 -2023 is estimated to be relevant to
two Sustainable Development Goals: SDG 9 (Industry, innovation and infrastructure: 30%) and SDG 3
(Good health and well -being: 23%). These goals dominate both in terms of funding volume and project
counts. SDG 4 (Quality education: 8%), SDG 7 (Affordable and clean energy: 5%), and SDG 13 (Climate

### PDF页 9

ASSESSING THE RELEVANCE OF R&D FUNDING TOWARDS SOCIETAL GOALS  9

 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS © OECD 2025

Science, technology, and innovation (STI) play a pivotal role in addressing global challenges by
documenting their nature, scale and features, as well as by facilitating new solutions that overcome critical
and hard to accept trade -offs under the state of the art of knowledge and technology . Evidence on the
contribution of research and development (R&D) , i.e., activity aiming to create and develop brand new
knowledge and solutions (OECD, 2015[1]), to a wide range of societal goals is crucial for assessing the
balance and orientation of STI policies. It also plays a key part in communicating the return to public
investments in R&D. Yet providing informative indicators and analysis on the goals of R&D is challenging
because of the multiple channels through which support for R&D is intended to and ultimately impacts on
the attainment of such goals.
OECD’s long-standing work on classifying government budgets for R&D across societal goals focuses on
assessing government’s overarching aims as the result of the political process of setting the national
budget. National experts report data to the OECD according to internationally agreed standards, matching
budgetary lines to a defined range of “socioeconomic” objectives that closely match government functions
like defence and health, and which include public goods such as the general advancement of knowledge
(OECD, 2015[1]). However, several policy questions require identifying what publicly funded R&D can be
ultimately relevant for, regardless of the high -level stated aims and independently of any given
classification framework. This requires having flexible allocation and classification mechanisms as well as
data enabling granular analysis to serve different user needs . The OECD has recently developed the
Fundstat analytical infrastructure with such an objective, working with R&D project award level microdata
and using AI tools for analysing unstructured text descriptions of such awards . Examples of recent
applications of Fundstat include studies that focus on both content , relevance and directionality of R&D
funding, such as artificial intelligence (AI) development (Yamashita et al., 2021 [2]) and COVID-19
(Aristodemou et al., 2023[3]).
In the absence of formal requirements for disclosing in a structured fashion what STI activities are relevant
for, the key conceptual and practical measurement challenge is identifying goals from information available
about STI activities, such as data on inputs from R&D project funding awards, or outputs such as scientific
publications. This stands in contrast with patented inventions, where requests for protection must disclose
their potential applications, claims which are further assessed by expert independent patent examiners.
AI-based analysis of text descriptions needs to be adequately guided (i.e., trained) to reflect not only on
the content of the STI activity but also consider how knowledge outputs can be key inputs for other STI
activities that ultimately contribute to societal goals. For example, a summary description of research into
properties of new materials may not necessarily disclose that such properties may play a critical for
applications in areas such as health, defence or energy. An appropriate degree of domain expertise is thus
a necessary input into the training of reliable AI-based classification methods.
This paper uses the United Nations (UN) Sustainable Development Goals (SDGs) framework as a
demonstration use case for a n ovel classification approach for R&D goals . The SDGs were adopted in
2015 to focus action towards addressing the world’s most urgent economic, social, and environmental
challenges. The 2015 OECD Daejeon Declaration on Science, Technology and Innovation (STI) Policies
for the Global and Digital Age (OECD, 2015[4]) underscored the importance of Science, technology, and
innovation in achieving sustainable development , emphasising that STI is not just an engine of economic
1 Introduction

### PDF页 10

10  ASSESSING THE RELEVANCE OF R&D FUNDING TOWARDS SOCIETAL GOALS

 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS © OECD 2025

growth but also a powerful tool for fostering sustainability and social well-being. Nearly a decade later, the
2024 OECD Declaration on Transformative Science, Technology, and Innovation Policies for a Sustainable
and Inclusive Future (OECD, 2024[5]) reinforced the necessity of transformative STI policies to address the
SDGs, urging countries to reorient their STI policies to better address systemic issues like climate change,
inequality, and resource depletion (OECD, 2024[6]; OECD, 2024[7]).
SDG allocation and classification methods used to date, typically based on keyword -matching or natural
language processing (NLP), rely heavily on surface -level text features and equate lexical similarity with
conceptual alignment. Recent studies have mapped the contribution of STI to the SDGs (Kashnitsky et al.,
2024[8]), by applying transformer-based SDG classifiers to scientific publications . As they have been
applied to indicators of STI activity such as scientific publications’ abstracts, the widespread lack of explicit
“SDG” language in R&D activity descriptions tends to result in low rates of SDG relevance which understate
the potential contribution of R&D, especially basic research and research applied to outcomes that may
indirectly contribute to the goals.
This study introduces an AI-based probabilistic classification approach that is trained on effective domain-
informed assessments of goal relevance for research. The applied model captures relationships between
research content and relevance towards the 17 SDG objectives, as well as the absence of SDG relevance.
The classifier has been deployed on the Scopus custom database of scientific publications (v.1.2024) and
the latest version of the OECD Fundstat database (v.2024), which compri ses approximately 2.1 million
government-funded R&D project awards across 19 OECD countries and the European Union (EU)
programmes implemented by the European Commission (EC) , between 2015 and 2023. These awards
accounted for approximately USD 1.5 trillion in government R&D funding over this period . This dual
application to scientific publications and R&D awards data provides a view of R&D relevance towards
societal goals, proxied using the SDG framework.
The remainder of the paper is organised as follows:
• Section 2 introduces the conceptual and empirical approaches adopted in mapping the
contributions of science, technology and innovation (STI) to societal goals, taking the Sustainable
Development Goals (SDGs) as reference framework. This is followed by a review of existing SDG
classification methods, including keyword-based and AI-assisted approaches.
• Section 3 presents the data sources used for model development, evaluation, and analysis.
• Section 4 details the methodology for developing the SDG relevance classifier applied to R&D -
related text. It discusses model training and evaluation, including validation with external SDG -
labelled content and alignment with existing classification systems.
• Section 5 applies the SDG classifier to the Fundstat and Scopus databases to assess the relevance
of R&D funding awards and scientific publication output. It also provides exploratory evidence on
the thematic structures and interdependencies in R&D funding across different societal goals.
• Section 6 concludes with some potential implications and suggestions for future work.

## T1_国家研发与方向设定

- PDF页3：os and provides evidence of the interdependencies between societal goals served by R&D funding and its potential to contribute to multiple goals. Authors: Leonidas Aristodemou, Silvia Appelt, Brigitte van Beuzekom, Fernando Galindo-Rueda Keywords: Research and Development (R&D), Government R&D funding, Machine Learning, Language Models, Sustainable Development Goals (SDGs), Survey data, Classification, Directionality JEL codes: O38, O32, C38, C45, Q55

- PDF页5：, TECHNOLOGY AND INDUSTRY WORKING PAPERS © OECD 2025 Table of contents Abstract 3 Acknowledgements 4 Table of contents 5 Executive summary 7 1 Introduction 9 2 Mapping the contribution of science, technology and innovation to societal goals 11 2.1. Perspectives for assessing the directionality and relevance of STI towards societal goals 11 2.2. SDGs and related work on SDG classification for STI activity 12 2.2.1. Using SDGs to measure societal goals of R&D 12 2.2.2. General SDG mapping approaches for STI efforts 13 2.2.3. Keyword and AI assisted classification approaches 14 3 Data sources for assessing relevance 16 3.1. Classification training data 16 3.1.1. OECD International Survey of Science (ISSA) 16 3.1.2. Scopus bibliometric database on scientific publications 16 3.2. Classification evaluation da

- PDF页6：es of R&D funding, awards and publications by SDG group, 2015-2023 37 Figure 5.10. Topics in R&D projects relevant to Energy and Planet related SDGs, 2020-2023 39 Figure 5.11. SDG relevance of R&D funding, by dominant SDG group in R&D awards, 2010-2023 40 Figure A.1. Coverage of government R&D funding in the 2024 OECD Fundstat database, 2010-2023 52 Figure A.2. Share of R&D funding by theme in Fundstat and GBARD for 19 OECD countries, 2021 54 Figure B.1. Out-of-sample SDG label classifier prediction on the OSDG dataset (n=8 768) 57 Figure C.1. SDG distribution of R&D projects, R&D funding and scientific publications, 2015-2023 58 Figure C.2. Distribution of R&D funding and R&D projects by SDG, 2015-2023 59 Figure C.3. Distribution of R&D funding and projects by SDG & data source, 2015-2023 60 Figure

- PDF页7：ASSESSING THE RELEVANCE OF R&D FUNDING TOWARDS SOCIETAL GOALS  7 OECD SCIENCE, TECHNOLOGY AND INDUSTRY WORKING PAPERS © OECD 2025 Executive summary What do billions of government investment in research and development (R&D) across OECD countries contribute to? Traditionally, such question was only addressed through the prism of established classifications at a high level of aggregation . Available statistics, whilst providing a comprehensive benchmark, leave unanswered several questions about the relevance of R&D funding towards specific and evolving societal goals. To respond to such needs, the OECD has developed the Fundstat analytical infrastructure to develop and demonstrate approaches

- PDF页7：es for working with administrative R&D microdata and AI tools for analysis of quantitative and qualitative dat a in conjunction with traditional methods. This paper presents a decisive step in the Fundstat initiative towards developing tools that can help provide evidence on the directionality and relevance of R&D funding. Evidence on the potential contribution of R&D to different societal goals is crucial for assessing the balance and orientation of R&D and innovation policies. Yet, providing informative indicators remains challenging because support for R&D can influence the attainment of such goals through multi ple and often indirect channels. AI-based classification methods applied to administrative data, while promising, are often reliant on superficial text features and tend to equate lexical sim

- PDF页7：n-informed assessments of goal relevance for R&D. Close to 2 000 participants in the 2021 OECD International Survey of Science (ISSA2021) reported which Sustainable Development Goal ( SDG), or none, they contributed to with their research. As it touches on virtually all areas of government policy, the UN SDG framework provides a convenient and relevant use case in the classification of unstructured R&D activity by goals. The survey data helped label a corpus of over 1 1 000 academic publications , which served in turn as the training dataset for fine -tuning SciBERT, a pre-trained domain-specific transformer- based language model (trained on a large corpus of scientific literature), into predicting goal relevance probability for a given text description. This yield ed a model capturing relationships

- PDF页8：hree dimensions together helps to account for differences in cost structures across research domains, where some areas, such as health or infrastructure, are typically more capital -intensive than others. Viewed jointly, these measures provide a more comprehensive picture of the directionality of R&D funding and its alignment with societal goals. Recent trends also point to a shift towards fewe r but larger R&D awards, as well as modest realignments in priorities in response to the COVID-19 crisis. This paper also explores the advantages of granular data and AI tools to examine the R&D topics being funded within projects that score highly on envi ronmental and energy goals. An unsupervised topic modelling exercise reveals research themes attracting public investment, with the topic structure is consiste

- PDF页8：to the COVID-19 crisis. This paper also explores the advantages of granular data and AI tools to examine the R&D topics being funded within projects that score highly on envi ronmental and energy goals. An unsupervised topic modelling exercise reveals research themes attracting public investment, with the topic structure is consistent with the selected goals (projects exhibit combinations of energy and environmental topics) and the types of project descriptions that underpin projects relevant to such goals (project descriptions exhibit different combinations of topics that describe the nature of the R&D, such as scientific topics and technology domains, on the one hand, and application areas that relate to goals, on the other). The results also shed light on the synergies between different goals. Awards t

## T2_市场与产业政策边界

- PDF页12：nable to observe the counterfactual directly, the best alternative is to compare R&D performers that receive support with those that do not but are otherwise as similar as possible , a strategy also adopted in related OECD distributed analysis on the impact of public support for business R&D (OECD, 2023[13]; OECD, 2020[14]). 2.2. SDGs and related work on SDG classification for STI activity 2.2.1. Using SDGs to measure societal goals of R&D The sustainable development goals (SDGs) were adopted by the United Nations (UN) in 2015 as a comprehensive framework designed to address the world’s most urgent economic, social, and environmental challenges, setting a broader, more inclusive vision for sustainable development. The framework comprises 17 interrelated goals that cover areas ranging from poverty, edu

## T4_国际合作与开放

- PDF页14：t, telecommunication and other infrastructures', 'Environment', 'Energy', 'Agriculture', and 'General advancement of knowledge: R&D related to Agricultural and veterinary sciences' (NABS 01-05, 08, 124 and 134) Security • SDG 16 (Peace, justice and strong institutions) • SDG 17 (Partnerships for the goals) Defence (NABS 14) Note: Mapping of the c lassification of socio-economic objectives (SEOs) based on NABS 2007 onto SDG groups . For some countries, field- based subcategories of 'General advancement of knowledge' (NABS12) are not reported, preventing potential alignment with SDG groups other than “Industry and knowledge”, which includes under SDG 9 the target of increasing R&D investment. Source: OECD (2025[26]). 2.2.3. Keyword and AI assisted classification approaches Several methodologies have be

- PDF页17：Life below water 84 2.9 73 3.4 6 Clean water and sanitation 59 2.0 54 2.5 2 Zero hunger 60 2.1 51 2.3 10 Reduced inequalities 67 2.3 41 1.9 8 Decent work and economic growth 72 2.5 36 1.7 16 Peace, justice, and strong institutions 69 2.4 30 1.4 5 Gender equality 57 1.9 26 1.2 17 Partnership for development 27 0.9 16 0.7 1 No poverty 20 0.7 7 0.3 0 Not relevant to any SDG 240 8.2 164 7.6 Total 2 911 100.0 2 171 100.0 Note: The table shows the SDG relevance distribution (profiles across the 18 SDG relevance options - 17 SDGs and none) among ISSA2021 respondents to the SDG item (94% of all respondents), and among those, those who were successfully matched as publication authors to their respective Scopus Author (75% of the total response). Source: OECD analysis of the 2021 OECD International Survey of S

- PDF页18：ta available for the analysis through either open and restricted channels. Coverage varies widely across countries and sectors, depending on factors such as: • The relative share of funding allocated via competitive projects vs. institutional block grants. • The availability and openness of administrative R&D and innovation funding data from national and regional agencies and organisations. • The extent of project data/metadata completeness (e.g., funding amount, project description).

- PDF页34：.75 1 069 786 11 11. Sustainable cities and communities 67 123 46 323 0.58 750 876 15 15. Life on land 84 142 44 810 0.69 794 655 2 2. Zero hunger 55 699 35 441 0.53 663 097 5 5. Gender equality 42 548 30 765 0.64 476 363 14 14. Life below water 43 439 30 724 0.72 489 816 17 17. Partnerships for the goals 40 856 30 164 0.71 473 294 10 10. Reduced inequalities 40 698 26 331 0.74 453 046 16 16. Peace, justice and strong institutions 38 320 24 726 0.65 421 181 8 8. Decent work and economic growth 43 653 23 093 0.65 491 365 1 1. No poverty 29 431 20 158 0.53 311 569 6 6. Clean water and sanitation 30 052 18 646 0.68 548 173 0 No SDG relevance 81 233 47 012 0.62 1 429 712 SDG group D Prosperity (SDGs 8, 9, 10, 11) 462 056 542 407 1.17 5 501 131 C Health (SDGs 1, 2, 3, 5) 795 413 428 548 0.54 8 994 026 A P

## T5_供应链与技术依赖

未自动命中；需人工按目录复核。

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页8：ure work include extending the application of this SDG classifier to other scientific data sources and exploring its use in mapping policy -relevant research portfolios, su ch as in health, climate, or energy domains , and assessing in more detail the orientations of support for emerging technologies .

- PDF页9：bjective, working with R&D project award level microdata and using AI tools for analysing unstructured text descriptions of such awards . Examples of recent applications of Fundstat include studies that focus on both content , relevance and directionality of R&D funding, such as artificial intelligence (AI) development (Yamashita et al., 2021 [2]) and COVID-19 (Aristodemou et al., 2023[3]). In the absence of formal requirements for disclosing in a structured fashion what STI activities are relevant for, the key conceptual and practical measurement challenge is identifying goals from information available about STI activities, such as data on inputs from R&D project funding awards, or outputs such as scientific publications. This stands in contrast with patented inventions, where requests for protection must disc

- PDF页14：contribution of scientific research (Confraria, Ciarli and Noyons, 2024 [27]), technologies (Massucci and Seri, 2022 [28]; WIPO, 2024[29]; Hajikhani and Suominen, 2022 [30]) and polic y documents (Wincott, 2024 [31]) to the UN SDGs . Approaches have centred on keyword -based and artificial intelligence (AI) methodologies, each offering distinct advantages and limitations (Kashnitsky et al., 2024[8]). Benchmarking studies comparing various SDG classification approaches, including those developed by Aurora and Elsevier, have shed light on the strengths and weaknesses of each method (Armitage, Lorenz and Mikki, 2020 [32]; Kashnitsky et al., 2024[8]). While keyword-driven models generally excel in precision, they underperform in recall, i.e., they fail to capture the full spectrum of research contributions. In contr

- PDF页21：the R&D activities also need disentangling . The SDG classification developed in this study relies on transformer-based language models, which underpin many of today’s large language models (LLMs ) and constitute an integral part of natural language processing (NLP), a branch of artificial intelligence (AI) that focuses on the interaction between computers and human languages (Jurafsky and Martin, 2023[60]). NLP enables machines to process, analyse, and generate human language in a manner that is meaningful (Box 4.1). Model development involved two main steps: training and validation. Training a model requires “teaching” it to recognise patterns in labelled data so it can make predictions on unseen data. Once the model was trained, its performance and generalisability were assessed based on an unseen (validation

- PDF页44：0.1016/j.respol.2023.104950. [27] Cui, Y. et al. (2019), “Class-Balanced Loss Based on Effective Number of Samples”, 2019 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) , pp. 9260-9269, https://doi.org/10.1109/cvpr.2019.00949. [70] Dan Clark et al. (2023), Artificial Intelligence: Generative AI exists because of the transformer (by the visual storytelling team), Financial-Times, https://ig.ft.com/generative-ai/ (accessed on 26 September 2024). [59] Devlin, J. et al. (2019), BERT: Pre-training of deep bidirectional transformers for language understanding, https://doi.org/10.48550/arXiv.1810.04805. [67] Elsevier (2022), Times Higher Education Impact Rankings, Scopus and SciVal, https://www.elsevier.com/academic-and-government/impact-rankings-data (accessed on 25 September 2024). [44] Hajikha

- PDF页49：easuring the AI content of government-funded R&D projects: A proof of concept for the OECD Fundstat initiative”, OECD Science, Technology and Industry Working Papers, No. 2021/09, OECD Publishing, Paris, https://doi.org/10.1787/7b43b038-en. [2] Yin, H. et al. (2023), “Leveraging Artificial Intelligence Technology for Mapping Research to Sustainable Development Goals: A Case Study”, https://doi.org/10.48550/arXiv.2311.16162. [46]

## T10_预见与优先领域

- PDF页12：made in the scale and scope of measurement and analytical efforts with a view to addressing the key policy questions at hand. To gauge the causal impact of R&D on the policy goal, the outcomes of interest would ideally be directly compared with their level in the counterfactual scenario in which no R&D support is provided . A fundamental estimation challenge arises as it is not possible to observe the “counterfactual”, i.e., how much R&D would R&D support recipients have performed had they not received this support. Being unable to observe the counterfactual directly, the best alternative is to compare R&D performers that receive support with those that do not but are otherwise as similar as possible , a strategy also adopted in related OECD distributed analysis on the impact of public support fo
