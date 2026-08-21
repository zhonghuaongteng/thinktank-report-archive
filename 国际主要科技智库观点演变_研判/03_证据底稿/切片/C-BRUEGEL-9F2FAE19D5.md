# C-BRUEGEL-9F2FAE19D5 原文切片

- 原文：`03_证据底稿\原文PDF\C-BRUEGEL-9F2FAE19D5.pdf`
- PDF页数：39
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 7

6
(2023) proposed a text-based patent novelty measure using natural language processing (NLP)
techniques, applying it to patents within the same classification to derive novelty-value profiles. Their
approach provides an alternative to citation-based novelty assessments and highlights the potential
of NLP in refining patent landscaping and innovation evaluation. These studies reinforce the
importance of LLMs in patent evaluation, as they enable more nuanced assessments of technological
novelty and patent significance.
Finally, we also contribute to the literature of classifying patents into technology categories. This is
particularly difficult for emerging technologies since no readily available taxonomies exist. Patent
registries usually use pre-defined categories to delimit technologies. The two most common
classifications are the International Patent Classification (IPC) system used by the World Intellectual
Property Organization (WIPO) and the Cooperative Patent Classification (CPC) system, a more specific
version of the IPC which was adopted by the USPTO. While this is the easiest way to classify patents, it
comes with the caveat that they are primarily designed for patent examiners and are based on
techniques rather than an economic understanding of technology (Griliches, 1990).
In a seminal paper, Trajtenberg (1990) manually delimited US patents, but manual methods alone are
now considered too time consuming and subject to human error and bias, especially since the usage
of the patent system has become increasingly common since the 1990s. With the advancement in
machine learning and NLP, the academic literature has offered several workarounds. Bergeaud et al
(2017) used network analysis techniques to classify technologies based on common keywords.
Abood and Feltenberger (2018) proposed a method of automated patent to technology matching
based on a small group of manually matched ‘seed’ patents. Li et al (2018) proposed a deep learning
algorithm based on convolutional neural network (CNN) and word vector embedding. Lee and Hsiang
(2020) used Google’s BERT model to generate patent classifications.
Recent advancements in large language models and generative AI offer new possibilities, not only in
the extraction of patent novelties, but equally in the classification of patented technologies. This is the
path we follow but we add our own supervision to the classification obtained through LLM models. In
particular, we obtain subfields for each of the three critical technologies by LLM which we then confirm
manually using industry expertise.
4 Data and methodology
4.1 Using large language models (LLMs) for patent analysis
Our methodology builds on prior work using NLP to quantify technological novelty across jurisdictions.
Unlike and Arts et al (2021) and Kelly et al (2021) who relied on high frequency textual analysis and
keywords respectively, we opt for using an LLM model, following the mo st recent literature. Our
choice is LLAMA3 for the classification of patents and to extract their novelty. LLAMA-3 is a state-of-the-
art LLM that can extract novel concepts embedded in patent abstracts.

### PDF页 8

7
A similar approach was used by Boeing et al (2024), who applied LLMs to vectorise patent abstracts
a
nd computed semantic distances to identify high-impact patents. Our methodology extends theirs by
not only measuring semantic novelty but also identifying radical innovation concepts, defined as
previously unseen technological descriptors with demonstrated influence on subsequent filings.
Finally, our definition of radical novelty, following Arts et al (2021), requires two criteria to be fulfilled,
Firstly, for a patent to be considered relevant enough, its key innovation should not have appeared in
the description of any patent since 1979. Secondly, the key concept should appear in at least 5
subsequent patents in any jurisdiction, which should ensure its relevance. Appendix I offers more
details about the methodology used.
4.2 Data
T
he basis for our analysis consists of the merger of two datasets. First, we use a dataset covering the
universe of PCT patent grants from 1979 to 2023 which we acquired from WIPO2 to have a full account
of all pre-existing innovations. This will provide the basis to determine whether any of the patents in
critical technologies thereafter are novel enough. We then scrap all the patents from WIPO Patentscope
that were made available publicly from 2019 to 2023 whether filed in the USPTO, the EU patent office
(EPO) or the Chinese patent office (CNIPA), which resulted in a PCT application. We also include US and
EU domestic filings in these critical technologies, namely USPTO and EPO, respectively. We do not
include China’s domestic patents filed at CNIPA to avoid artificially inflating the number of patents to be
reviewed without much hope that they will constitute radical technologies.
It is well-established that subsidy programs are behind, at least partially, the massive increase in
patenting in China (Li, 2012). As patents surge, reviewers at the CNIPA are swamped with applications
leading to a reduction in the degree of scrutiny regarding the technical content of these patents.
Patents might thus fit our definition of radical novelty but might be technically irrelevant, and hence,
artificially inflate China’s radical novelty count. Furthermore, we believe that since the three
technologies under observation are essential to international competition, Chinese firms will prefer to
file patents in these fields through internationally recognised systems. This is evidenced by the
extensive use of the PCT patent system by Chinese firms
3. In fact, the number of radical novelties in
Chinese patents might still be inflated as Chinese applicants also receive subsidies for international
applications.
US and EU domestic filings, namely USPTO and EPO, are included because they serve as an alternative
to the PCT system. This is particularly the case for the USPTO since the US consumer market is one of
the largest and most competitive globally with very strict legal protection of intellectual property rights.
If a foreign firm infringes on a USPTO patent the patent holder can seek redress at the US International
Trade Commission to obtain an exclusion order, blocking the imports of goods of the infringer to the US.
2 Speciﬁcally, the dataset consists of the PCT backﬁles in Asian and non-Asian languages; see
https://www.wipo.int/patentscope/en/data/.
3 Aaron Wininger, ‘China Remains Top Patent Cooperation Treaty Filer in 2021’, China IP Law Update, 11 February 2022,
https://www.chinaiplawupdate.com/2022/02/china-remains-top-patent-cooperation-treaty-ﬁler-in-2021/.

## T1_国家研发与方向设定

- PDF页4：ing economies have grasped the potential importance of advancement in this sector and have started to invest. In China, quantum computing has been identified as a strategic priority in five-year plans since 2015, and by 2021, the equivalent of $15.3 billion had been earmarked as government investment (McKinsey, 2022). The city of Hefei is the centre of quantum computing, home to Origin Quantum Computing and the National Laboratory for Quantum Information Science. In the US, quantum computing is driven by large incumbent technology firms. In 2019, Google’s quantum AI lab announced the creation of ‘Sycamore’ a 53-qubit processor called. The same year, IBM introduced the 127-qubit IBM Q System One. In Europe, a group of major German industrial companies have formed a consortium to develop industry-rela

- PDF页18：ina, the data generated by large- scale deployment of surveillance technology and the widespread usage of Douyin (the Chinese version of TikTok) has led to a spring of inventions regarding the processing of image and video, including computer vision (Scharre, 2024). Often, local governments collect and share this data with private suppliers of AI applications which then use the data for further commercial innovation (Beraja et al, 2023). The US has the advantage of a fairly unregulated internet, and internet services (ie social media applications, search engines, e-commerce) that are used across the globe. The collected data forms the basis of natural language processing and machine learning algorithms, and now, generative AI, the fields of comparative advantage for the US. Semiconductors Fig ure 11

- PDF页19：ughly o n par. China dom inates in memory technology, while the US leads innovation on semiconductor design, sensor technology and imaging technology. Figure 11: Share of radical novelties in semiconductors by subfield and entity origin Sou rce: Bruegel based on WIPO. Given the government’s decisive push for the development of a domestic chip ecosystem, it is not surprising that the composition of China’s radical novelties across subfields has changed substantially (Figure 12). Until 2021, Chinese semiconductor firms were largely focused on display technology which made up 46.05 percent of all radical novelties in 2019, and 33.14 percent in 2021. This aligns well with China’s general strength in consumer electronics manufacturing. However, a significant shift has taken place since 2021. Semiconduct

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

未自动命中；需人工按目录复核。

## T5_供应链与技术依赖

- PDF页2：include inbound investment screening, export controls and, more recently, outbound investment screening. While the European Union has been less assertive in its overall policy towards China, it developed its own economic security strategy in January 2024 with an eye to reducing dependence on China for some critical raw materials and avoiding losing control of key technologies. In this Working Paper, we analyse the evolution of frontier innovation in quantum computing, semiconductors and artificial intelligence (AI) in China, the US and the EU by drawing on a measurement of patent novelty based on a large language model (LLM). Specifically, we aim at answering two research questions: (1) How far has China moved in innovating in these three critical technologies compared to the US and the EU? (2) How

- PDF页4：3 somewhat the direct relation between advanced semiconductors and AI power, it does not fully discard the need for advanced semiconductors. More generally, the semiconductor industry is characterised by a highly globalised supply chain and is therefore particularly subject to geopolitical volatility. There are three important steps in the chip value chain. During the design phase the structure and technical details of the integrated circuit are defined. Different requirements exist for the design of different types of chips (eg logic, analogue or memory chips) and firms engaged in this step often coordinate with manufacturers or ‘fabs’ in the process. There has been a trend among original equipment manufacturers to build up capacity for the desi

- PDF页5：but growing literature studying the US-China technology rivalry. Fang et al (2023) investigated patent quality based on citations and new keywords. Their findings confirm the rising quality of Chinese patents vis-à-vis US patenting. On the issue of spillovers and potential interdependence between the quantum computing, semiconductors and AI, Han et al (2024) examined cross-national citations, concluding that innovative activity between the US and China has become more intertwined. From the 2010s, the propensity of Chinese innovators to cite US patents relative to US innovators to Chinese patents has decreased, indicating a decline in dependency of China on the US. However, the analysis by Mueller and Boeing (2024) showed that China remains highly dependent on global innovations for its own inventio

- PDF页5：xamined cross-national citations, concluding that innovative activity between the US and China has become more intertwined. From the 2010s, the propensity of Chinese innovators to cite US patents relative to US innovators to Chinese patents has decreased, indicating a decline in dependency of China on the US. However, the analysis by Mueller and Boeing (2024) showed that China remains highly dependent on global innovations for its own inventions. This Working Paper contributes to the methods for measuring the impact of patented innovation. To estimate the economic value of an invention researchers have commonly used the number of times a patent is cited by subsequent patents (Trajtenberg, 1990; Jaffe et al, 2003). However, over the years substantial issues with citation-based indicators have been no

- PDF页12：th th e U S chip ecosystem compared to the Chinese chip ecosystem. This is an interesting re search question but goes beyond the scope of this paper. Figure 4: Evolution of radical novelties in Figure 5: Radical novelties in semiconductors, in semiconductors (2019-2023) extended supply chain (2019-2023) Source: Bruegel based on WIPO. Finally, for AI, the US dominates, accounting for a significantly higher number of radical innovations than the EU and China (Figure 6). In 2019, US firms were published 250 radical novelties, a share of 46.13 percent of total novelties in China and the EU. In 2023, the number of US radical novelties almost doubled to 502, while its share increased to 59.48 percent, an absolute as well as relative increase in AI innovation in the US over our period under observation. Chin

- PDF页34：systems’, Working Paper 2010/03, Bruegel, available at https://www.bruegel.org/working-paper/quality-factor-patent-systems Varadarajan, R., I. Koch-Weser, C. Richard, J. Fitzgerald, J. Singh, M. Thornton, R. Casanova and D. Isaacs (2024) Emerging Resilience in the Semiconductor Supply Chain, SIA and BCG, available at https://www.semiconductors.org/wp-content/uploads/2024/05/Report_Emerging-Resilience-in-the- Semiconductor-Supply-Chain.pdf Yassine, A. and C. Lipizzi (2023) ‘Measuring Patent Novelty using Natural Language Processing’, Proceedings of the Design Society 3: 2605–2614, available at https://doi.org/10.1017/pds.2023.261

## T7_管制与研究安全

- PDF页2：strategic competition between the United States and China. Defensive measures have been created by multiple US administrations to control the transfer of critical technologies to China, mainly on grounds of national security. These measures include inbound investment screening, export controls and, more recently, outbound investment screening. While the European Union has been less assertive in its overall policy towards China, it developed its own economic security strategy in January 2024 with an eye to reducing dependence on China for some critical raw materials and avoiding losing control of key technologies. In this Working Paper, we analyse the evolution of frontier innovation in quantum computing, semiconductors and artificial intelligence (AI) in China, the US and the EU by drawing on a measure

- PDF页2：nologies similar to a given radical novelty to appear in another region. This measures the speed at which radical novelties are transferred from one country/region to another and is particularly relevant to gauge how much strategic technologies may be delayed in its transfer for economic security reasons. This is particularly relevant considering the US-China technology rivalry. When looking at the overall share of radical novelties in the three critical technologies analysed, we note China’s increased ability to innovate at the technology frontier, especially in semiconductors.

- PDF页31：is offers some clues as to the winners in specific subsectors. Their innovation ecosystems are far more integrated with one another than they are with the EU when measured by the speed of spillovers (or technology replication) in critical technologies, despite US introduction of export controls in critical technologies.

## T8_新兴技术治理

- PDF页1：RADICAL NOVELTIES IN CRITICAL TECHNOLOGIES AND SPILLOVERS: HOW DO CHINA, THE US AND THE EU FARE? ALICIA GARCÍA-HERRERO, MICHAL KRYSTYANCZUK AND ROBIN SCHINDOWSKI Critical technologies including artificial intelligence, semiconductors and quantum computing are attracting attention because of their indispensable nature and their role in national security strategies. We compare China, the United States and the European Union in these technologies and their subfields. We use large language models (LLMs) to identify which patents in these technologies can be considered most groundbreaking (not patented before) and worth replicating. These are ‘radical novelties.’ We find that the US clearly dominates quantum. Chinese and EU progress

- PDF页2：economic security strategy in January 2024 with an eye to reducing dependence on China for some critical raw materials and avoiding losing control of key technologies. In this Working Paper, we analyse the evolution of frontier innovation in quantum computing, semiconductors and artificial intelligence (AI) in China, the US and the EU by drawing on a measurement of patent novelty based on a large language model (LLM). Specifically, we aim at answering two research questions: (1) How far has China moved in innovating in these three critical technologies compared to the US and the EU? (2) How long does it take for an innovation in one region to appear in another region? In other words, how long do technology spillovers take between these three? To answer these two questions, we use an LLM model to extract the majo

- PDF页4：r as its ultimate goal is to increase computing power. The economic implications are potentially huge since, once matured, quantum computing could potentially render traditional semiconductor chips redundant, ending the age of silicon. In addition, it may enable breakthroughs in artificial intelligence, biotechnology, agricultural technology, material sciences, encryption and cybersecurity (Kaku, 2023). This is why the leading economies have grasped the potential importance of advancement in this sector and have started to invest. In China, quantum computing has been identified as a strategic priority in five-year plans since 2015, and by 2021, the equivalent of $15.3 billion had been earmarked as government investment (McKinsey, 2022). The city of Hefei is the centre of quantum computing, home to Origin Quantum

- PDF页6：d cannot consider the context. High frequency textual analysis is more flexible than keyword search, as it captures word relationships and latent topics, but it still struggles with deep contextual meaning, as it only captures surface-level similarities and may not work well for emerging technologies that lack historical references. Since 2021, the literature has started to introduce LLMs to evaluate the significance of patents as an improvement relative to key words and high frequency textual analysis. Deep learning is better at capturing semantic meaning and relationships in patent text, not just word similarity. This is particularly important for emerging concepts, which are prevalent in critical technologies. The disadvantage is the computational cost. Some key references, also using LLMs to classify pa

- PDF页7：es reinforce the importance of LLMs in patent evaluation, as they enable more nuanced assessments of technological novelty and patent significance. Finally, we also contribute to the literature of classifying patents into technology categories. This is particularly difficult for emerging technologies since no readily available taxonomies exist. Patent registries usually use pre-defined categories to delimit technologies. The two most common classifications are the International Patent Classification (IPC) system used by the World Intellectual Property Organization (WIPO) and the Cooperative Patent Classification (CPC) system, a more specific version of the IPC which was adopted by the USPTO. While this is the easiest way to classify patents, it comes with the caveat that they are primarily designed for pate

- PDF页32：31 References Abood, A. and D. Feltenberger (2018) ‘Automated patent landscaping’, Artificial Intelligence and Law 26(2): 103–125, available at https://doi.org/10.1007/s10506-018-9222-4 Aghion, P. and P. Howitt (1992) ‘A Model of Growth Through Creative Destruction’, Econometrica 60(2): 323–351, available at https://doi.org/10.2307/2951599 Agrawal, A., J.S. Gans and A. Goldfarb (2018) ‘Human Judgment and AI Pricing’, AEA Papers and Proceedings 108: 58–63, available at https://doi.org/10.1257/pandp.20181022 Arts, S., J. Hou and J.C. Gomez (2021) ‘Natural language processing to identify the creation and impact of new tec

- PDF页32：2 Arts, S., J. Hou and J.C. Gomez (2021) ‘Natural language processing to identify the creation and impact of new technologies in patent text: Code, data, and new measures’, Research Policy 50(2), available at https://doi.org/10.1016/j.respol.2020.104144 Barnett, J.M. (2023) ‘Antitrust Mercantilism: The Strategic Devaluation of Intellectual Property Rights in Wireless Markets’, Berkeley Technology Law Journal 38: 259, available at https://lawcat.berkeley.edu/record/1275404?v=pdf Beraja, M., D.Y. Yang and N. Yuchtman (2020) ‘Data-intensive Innovation and the State: Evidence from AI Firms in China’, NBER Working Paper 27723, National Bureau of Economic Research, available at https://www.nber.org/papers/w27723 Bergeaud, A., Y. Potiron and J. Raimbault (2018) ‘Classifying Patents Based on Their Sema

- PDF页34：y Destroying Patent Pairs’, mimeo, available at https://arxiv.org/abs/2407.12193 Romer, P.M. (1990) ‘Endogenous Technological Change’, Journal of Political Economy 98(5), available at https://www.jstor.org/stable/2937632 Scharre, P. (2024) Four Battlegrounds: Power in the Age of Artificial Intelligence, W.W. Norton & Company Schmitt, V.J. and N.M. Denter (2024) ‘Modeling an indicator for statutory patent novelty’, World Patent Information 78, available at https://doi.org/10.1016/j.wpi.2024.102283 Trajtenberg, M. (1990) ‘A Penny for Your Quotes: Patent Citations and the Value of Innovations’, The RAND Journal of Economics 21(1): 172–187, available at https://doi.org/10.2307/2555502 Van Pottelsberghe de la Potterie, B. (2010) ‘The quality factor in patent systems’, Working Paper 2010/03, Bruegel, available at http

## T10_预见与优先领域

- PDF页1：RADICAL NOVELTIES IN CRITICAL TECHNOLOGIES AND SPILLOVERS: HOW DO CHINA, THE US AND THE EU FARE? ALICIA GARCÍA-HERRERO, MICHAL KRYSTYANCZUK AND ROBIN SCHINDOWSKI Critical technologies including artificial intelligence, semiconductors and quantum computing are attracting attention because of their indispensable nature and their role in national security strategies. We compare China, the United States and the European Union in these technologies and their subfields. We use large language models (LLMs) to identify which patents in these technologies can be

- PDF页1：far the slowest in replicating radical novelties from the US and China, while the US and China tend to replicate European novel patents relatively quickly. Radical novelties are also replicated quickly between China and the US which is surprising given US controls on exports of critical technologies to China. Our findings are concerning for Europe because it does not produce enough critical patents in these technologies and because it is slower in replicating patents from the US and China. JEL: O30, O33, F52 Key words: critical technologies, patents, innovation, AI, quantum computer, semiconductors Alicia García-Herrero (alicia.garcia-herrero@bruegel.org) is a Senior Fellow at Bruegel. Michal Krystyanczuk (michal.krystyanczuk@bruegel. org) is a Data Scientist at Bruegel. Robin Schindowski is a Research Fel

- PDF页1：.org) is a Senior Fellow at Bruegel. Michal Krystyanczuk (michal.krystyanczuk@bruegel. org) is a Data Scientist at Bruegel. Robin Schindowski is a Research Fellow at MERICS. Recommended citation: García-Herrero, A., M. Krystyanczuk and R. Schindowski (2025) ‘Radical novelties in critical technologies and spillovers: how do China, the US and the EU fare?’, Working Paper 07/2025, Bruegel WORKING PAPER | ISSUE 07/2025 | 20 MAY 2025

- PDF页2：when qualitative measures are taken into consideration. China’s rise as a technological power is increasingly central to the strategic competition between the United States and China. Defensive measures have been created by multiple US administrations to control the transfer of critical technologies to China, mainly on grounds of national security. These measures include inbound investment screening, export controls and, more recently, outbound investment screening. While the European Union has been less assertive in its overall policy towards China, it developed its own economic security strategy in January 2024 with an eye to reducing dependence on China for some critical raw materials and avoiding losing control of key technologies. In this Working Paper, we analyse the evolution of frontier innovation

- PDF页2：investment screening. While the European Union has been less assertive in its overall policy towards China, it developed its own economic security strategy in January 2024 with an eye to reducing dependence on China for some critical raw materials and avoiding losing control of key technologies. In this Working Paper, we analyse the evolution of frontier innovation in quantum computing, semiconductors and artificial intelligence (AI) in China, the US and the EU by drawing on a measurement of patent novelty based on a large language model (LLM). Specifically, we aim at answering two research questions: (1) How far has China moved in innovating in these three critical technologies compared to the US and the EU? (2) How long does it take for an innovation in one region to appear in another region? In oth

- PDF页2：ng, semiconductors and artificial intelligence (AI) in China, the US and the EU by drawing on a measurement of patent novelty based on a large language model (LLM). Specifically, we aim at answering two research questions: (1) How far has China moved in innovating in these three critical technologies compared to the US and the EU? (2) How long does it take for an innovation in one region to appear in another region? In other words, how long do technology spillovers take between these three? To answer these two questions, we use an LLM model to extract the major innovation from all PCT, USPTO and EPO patents between 2019 and 2023. Innovations within the three technologies (AI, quantum and semiconductors) that appear for the first time in a published patent since the start of our dataset in 1979 and are repli

- PDF页3：2 Still, the US dominates innovation in AI and quantum computing. The EU lags behind China and the US in all three technologies, although it is almost on par with China in quantum computing even if well behind the US. Beyond these general trends, we classify these three critical technologies into subfields which will help us find specialisation patterns across the three blocks analysed, which will be covered later. Finally, we assess the speed at which technologies in radically novel patents appear in regions other than their origin. The EU takes the longest to replicate key patents from the US or China in all three critical technologies. The EU’s most relevant patents quickly appear in China and the US. The spillover time for radically novel technologies from China to the US is relatively small, i

- PDF页3：on patterns across the three blocks analysed, which will be covered later. Finally, we assess the speed at which technologies in radically novel patents appear in regions other than their origin. The EU takes the longest to replicate key patents from the US or China in all three critical technologies. The EU’s most relevant patents quickly appear in China and the US. The spillover time for radically novel technologies from China to the US is relatively small, indicating that Chinese firms are in a head-to-head race in independent innovation with their US competitors or that the technology is frequently leaked or copied upon invention. The spillover time from the US to the China is similarly small. AI patents are transferred the fastest, compared to quantum and semiconductors. In section 2, we describe the t
