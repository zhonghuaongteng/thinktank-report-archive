# C-NESTA-2019-SEMANTIC-ANALYSIS-RECENT-EVOLUTION-AI-RESEARCH 原文切片

- 原文：`03_证据底稿\原文PDF\C-NESTA-2019-SEMANTIC-ANALYSIS-RECENT-EVOLUTION-AI-RESEARCH.pdf`
- PDF页数：29
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 1

A Semantic Analysis of the Recent Evolution of AI Research
1
A Semantic Analysis
of the Recent Evolution
of AI Research
Juan Mateos-Garcia, Joel Klinger, Konstantinos Stathoulopoulos and Russell Winch
November 2019
Executive summary
Fast-improving Artificial Intelligence (AI) systems are being applied in a growing number
of areas, from internet search and social media to the analysis of health scans and
management of power grids. Economists are hailing AI as a general purpose technology
that will revolutionise our economy and policymakers are putting in place national
strategies to spur its development and diffusion.
Powerful deep learning networks that identify patterns in vast datasets and reinforcement
learning algorithms that learn through trial and error in synthetic environments, have
overtaken previous AI approaches that programmed logic into computers and taught them
from experts. Although these new methods have achieved sensational breakthroughs, they
also have important limitations that could restrict their applicability and benefits, and/
or create risks when they are deployed, for example in terms of discrimination against
vulnerable groups, manipulation by malicious actors and unexpected outcomes when they

### PDF页 4

A Semantic Analysis of the Recent Evolution of AI Research
4
In the shorter term, there are increasing concerns about the risks of AI systems that
could entrench inequality if they learn the biases in historical data or make mistakes that
disproportionately impact minorities and vulnerable groups (Bostrom 2017; Noble 2018;
Eubanks 2018; Buolamwini and Gebru 2018), be gamed by malicious actors (Brundage et
al. 2018), turned into weapons or tools of surveillance that abuse personal data to monitor
and exploit users and citizens (Zuboff 2019), or create barriers for entry in increasingly
concentrated markets (Furman and Seamans 2018). AI systems could also behave in unsafe
ways if the metrics they seek to optimise are not well aligned with human goals (Amodei et
al. 2016), or if they create dangerous emergent phenomena when they interact with each
other in complex environments, like high frequency trading algorithms did during the ‘flash
crash’ of the New York Stock Exchange in 2010.
Some of these risks stem from modern AI systems’ reliance on deep learning algorithms
that learn increasingly abstract patterns from large amounts of unstructured data, such as
video or text (we will sometimes use the term ‘connectionism’ to refer to this programme
of research). Although deep learning systems have strong predictive power inside the
domains where they are trained, they lack robustness, interpretability and common sense.
This tends to break down when exposed to new situations, including strategic behaviours
by users seeking to manipulate them. It can also be difficult to understand their internal
operation and outputs. Further, they can create safety issues when they greedily optimise
performance metrics independently of the actual goals of their programmers, users and
wider society (Mateos-Garcia 2018; Marcus and Davis 2019). Their reliance on large datasets
and computational power could make them anti-competitive, privacy-infringing and
environmentally unsustainable (Amodei and Hernandez 2018). Some have argued that these
limitations require new approaches to AI that combine modern connectionism with ideas
from previous (symbolic and rule-based) AI eras (Marcus and Davis 2019; Marcus 2018).
Third-wave research, development and innovation policies for AI
There is increasing recognition of the need for policy action to manage the processes
through which AI systems are developed and deployed, leading to a proliferation of `AI
strategies’ around the world (Stilgoe et al. 2013; Jobin et al. 2019).1 These Strategies generally
seek to nurture national high-growth AI industries, and encourage the diffusion of AI systems
into other sectors in ways that are safe and consistent with ethical and political values.
Meanwhile, private sector organisations, non-governmental organisations and the research
community are creating ethical charters and guidelines to encourage responsible innovation
(Jobin, Ienca, and Vayena 2019), and fairness, accountability and transparency, and safety
research groups, are exploring technical and institutional solutions to various AI risks.
Together, these activities represent an example of what we have described in previous work
as a ‘third wave’ research, development and innovation (R&D&I) policy framework (Nesta
2019). Differently from older (first wave) approaches that focused on increasing research
and development investment levels without paying attention to its purpose (first wave),
and (second wave) models aimed at increasing the transfer of knowledge from university
to industry, the third wave of R&D&I policy is directional: it seeks to steer the development
and diffusion of new technologies mindful of their purposes and impacts (Stirling 2009,

### PDF页 10

A Semantic Analysis of the Recent Evolution of AI Research
10
The core dataset we use in our analysis is arXiv, an open pre-prints website with 1.6 million
papers that is widely used by various Science, Technology, Engineering and Mathematics
research communities.4 In recent years, arXiv has become an important channel for the
dissemination of AI research in academia and the private sector. As an example, almost
all research papers by DeepMind and OpenAI, two leading AI research labs, are available
from arXiv.5 Just under 60 per cent of the documents referenced in import ai, an influential
newsletter monitoring AI research trends, are in arXiv.6
We collect data from arXiv and enrich it with information about the institutional affiliation
of AI researchers and their location. Klinger et al (2018) and Stathoulopoulos et al (2019)
provide a detailed account of the methodology used for this. Here we summarise.
The institutional and geographical analysis involves two fuzzy matching steps. We match
arXiv papers with the Microsoft Academic Graph (MAG), a publications database, on
titles. This gives us access to additional information about the papers in arXiv, such as the
outlet where they were published, if they were published through an outlet (this includes
conference proceedings, an important dissemination channel in computer science), their
citation counts, authors, and in particular their institutional affiliation. We then match
institutional affiliations with the Global Research Identifier Database (GRID), an open
database of research institutions with information about their location and character (e.g.
whether they are an educational, government or third-sector organisation, or a private
sector company).7 This matching process leaves us with 2.7 million unique paper-author
pairs with detailed institutional and geographical information (including the geographical
coordinates of each institution).
Semantic analysis
We undertake four streams of semantic analysis with the abstracts available in the arXiv
data.
First, we use an expanded keyword search to identify AI and AI-related papers in the arXiv
corpus. Full details of this analysis are available in Stathoulopoulos and Mateos-Garcia
(2019). In summary, we expand an initial seed list of keywords related to AI with those that
are semantically close (.ie. appear in similar contexts) in a vector space estimated with the
word2vec algorithm (Mikolov, Yih, and Zweig 2013). We then tag as ‘ AI’ those papers where
those keywords appear after removing uninformative keywords (i.e. those that appear
frequently in the whole corpus). This way, we identify just over 72,000 AI papers in the
corpus. Manual validation of a random sample of observations suggests good classification
performance, with 90 per cent precision and 90 per cent recall.

## T1_科学体系与基础研究

- PDF页3：ms, voice assistants and (partially) self-driving cars (Brynjolfsson and McAfee 2014; McAfee and Brynjolfsson 2017). AI impacts and risks It is widely believed that AI systems could transform many domains beyond the technology sector including health, manufacturing, transport or scientific research (McAfee and Brynjolfsson 2017). They could also help tackle some of society’s biggest challenges, such as the prevention and treatment of chronic diseases, environmental sustainability and the decline in productivity in scientific research, to name a few (Topol 2019; Rolnick et al. 2019; Agrawal, McHale, and Oettl 2018). The broad relevance of the capability that AI systems promise to deliver (‘to behave appropriately in many different situations’) has led economists to herald AI as the latest example of a general

- PDF页12：rch We begin our analysis by studying the presence and evolution of AI activity in arXiv and its diffusion into other scientific fields beyond computer science and statistics (thus testing the idea that AI is an ‘invention in the methods of invention’ with broad applicability to scientific research and development (R&D) problems). We also want to measure qualitative changes: how has the composition of the AI field changed with the arrival of deep learning? Do we see evidence of a ‘paradigm shift’ as AI researchers and developers adopt new techniques able to solve problems that previous (symbolic and statistical) approaches were less suitable for? And how has disruption in the thematic content of AI research been associated with disruption in its geography? Evolution of activity Figure 2 confirms the idea of

## T2_技术创新与关键技术

- PDF页1：A Semantic Analysis of the Recent Evolution of AI Research 1 A Semantic Analysis of the Recent Evolution of AI Research Juan Mateos-Garcia, Joel Klinger, Konstantinos Stathoulopoulos and Russell Winch November 2019 Executive summary Fast-improving Artificial Intelligence (AI) systems are being applied in a growing number of areas, from internet search and social media to the analysis of health scans and management of power grids. Economists are hailing AI as a general purpose technology that will revolutionise our economy and policymakers are putting in place national strategies to spur its development and diffusion. Powerful deep learning networks that identify patterns in vast datasets and reinforcement learning algorithms that learn through trial and error in synthetic environm

- PDF页1：ies to spur its development and diffusion. Powerful deep learning networks that identify patterns in vast datasets and reinforcement learning algorithms that learn through trial and error in synthetic environments, have overtaken previous AI approaches that programmed logic into computers and taught them from experts. Although these new methods have achieved sensational breakthroughs, they also have important limitations that could restrict their applicability and benefits, and/ or create risks when they are deployed, for example in terms of discrimination against vulnerable groups, manipulation by malicious actors and unexpected outcomes when they

- PDF页2：vel data sources and methods can inform novel policy frameworks to steer AI in societally-beneficial directions. Our analysis shows that AI research has grown rapidly in recent years: 77 per cent of AI papers in arXiv were published in the last five years. This is not just about computer science: other fields have also experienced fast increases in the number of papers that use AI methods to tackle important scientific challenges. Growth in activity has been accompanied by shifts in its composition, with deep learning algorithms and applications such as computer vision overtaking symbolic and statistical methods: the share of papers about deep learning has multiplied four-fold since 2012, while the share of papers using statistical methods has halved. These thematic changes have been accompanied

- PDF页3：Introduction An AI revolution (again) Building intelligent machines has been one of the driving ambitions of computer science since the days of Alan Turing and significant efforts have been devoted to this purpose in the decades since (Dyson 2012). Previous strategies to achieve Artificial Intelligence (AI) had limited success, however. Symbolic approaches to program logic into computers in the 1950s, and expert systems that learn rules of behaviour from human experts in the 1980s were too difficult to scale to the variety of situations where an AI system might be expected to operate (Markoff 2016). Important aspects of our intelligence and how we perceive and behave in the world were found to be too hard to codify and therefore implement in AI systems (Russell 2019). Machine learning approaches that bypass the

- PDF页3：icult to scale to the variety of situations where an AI system might be expected to operate (Markoff 2016). Important aspects of our intelligence and how we perceive and behave in the world were found to be too hard to codify and therefore implement in AI systems (Russell 2019). Machine learning approaches that bypass the challenge of programming intelligence in machines by, instead, training them from examples or letting them learn through trial and error in synthetic environments, have overcome some of these challenges and delivered AI systems that are able to function effectively in a variety of situations; in some cases even outperforming humans (Russell 2019; Goodfellow, Bengio, and Courville 2016; LeCun, Bengio, and Hinton 2015; AI Index 2017). Some domains where AI systems have experienced rapid im

- PDF页6：enrich them with additional information about the identities of participants, their locations, affiliations, goals and networks can help capture the micro-dynamics of AI R&D&I and its drivers (Bakhshi and Mateos-Garcia 2016). This illustrates how AI and allied techniques such as machine learning and natural language processing can recursively transform its own analysis. However, like in other domains where AI is being applied, these methods also come with challenges. In particular, there is the risk that complex analytical methods to map AI may yield results that are difficult to explain, interpret or use to make policy decisions, or that the size and proprietary nature of the data sources they rely on and their technical sophistication create barriers for their replication and expansion. We believe that

- PDF页6：dation with better known and understood data sources and domain experts, and the use of qualitative methods to make new results interpretable, meaningful and actionable. It is also vital that the results of AI mapping efforts based on new methods are reproducible. The results of machine learning, natural language processing and clustering analyses can be sensitive to the datasets used for training, and the selection of parameters by the analyst (or the algorithm). Understanding the robustness of experimental results to different contexts, assumptions and model specifications is critical for determining where and how they can be used to make decisions. • Open: The best way to build trust in new data and methods is by making them openly available (while subject to constraints around the release of sensitive

- PDF页10：MAG), a publications database, on titles. This gives us access to additional information about the papers in arXiv, such as the outlet where they were published, if they were published through an outlet (this includes conference proceedings, an important dissemination channel in computer science), their citation counts, authors, and in particular their institutional affiliation. We then match institutional affiliations with the Global Research Identifier Database (GRID), an open database of research institutions with information about their location and character (e.g. whether they are an educational, government or third-sector organisation, or a private sector company).7 This matching process leaves us with 2.7 million unique paper-author pairs with detailed institutional and geographical inform

## T3_创新政策与研发治理

- PDF页2：and in hand with research on fairness, accountability, transparency and safety, regulatory changes and a proliferation of ethical charters to encourage responsible innovation. Taken together, these efforts amount to what we call a third-wave Research, Development and Innovation (R&D&I) policy, concerned not just with the levels of AI activity but also its direction. This policy programme needs to be informed by relevant, inclusive, trusted and open data and indicators, which go beyond aggregate measures of the volume of AI research and how it is evolving, to consider its composition, inclusion, diffusion, geography and purposes: we need smarter data about smarter machines. We have collected and enriched data from arXiv, an open repository of research widely used by the AI community. We combin

- PDF页2：ctors such as gender diversity, corporate participation, regional clustering and the involvement of countries with different political values in AI research are shaping its trajectories. This analysis will illustrate how smarter data about smarter machines can inform activist AI R&D&I policies to steer AI in a direction where its benefits are more widely shared and its risks more wisely managed.

- PDF页4：to various AI risks. Together, these activities represent an example of what we have described in previous work as a ‘third wave’ research, development and innovation (R&D&I) policy framework (Nesta 2019). Differently from older (first wave) approaches that focused on increasing research and development investment levels without paying attention to its purpose (first wave), and (second wave) models aimed at increasing the transfer of knowledge from university to industry, the third wave of R&D&I policy is directional: it seeks to steer the development and diffusion of new technologies mindful of their purposes and impacts (Stirling 2009,

- PDF页5：erior in the longer run. An implication of this is that the emergence and deployment of new technologies does not have a single equilibrium. Instead, we could imagine a collection of parallel universes, each of which is dominated by a qualitatively different technology. Activist R&D&I policymakers try to identify, among all these technological universes, which is more societally desirable and put in place interventions to bring it about (Mazzucato 2015, 2018; Kattel and Mazzucato 2018; Cantner and Vannuccini 2018). Some examples include: • Stronger levels of public engagement during the development of R&D&I policies. • Policies to increase inclusion in the R&D&I workforce. • Mission-oriented innovation policies to support R&D&I activities to tackle specific social challenges. • Developing nor

- PDF页5：se technological universes, which is more societally desirable and put in place interventions to bring it about (Mazzucato 2015, 2018; Kattel and Mazzucato 2018; Cantner and Vannuccini 2018). Some examples include: • Stronger levels of public engagement during the development of R&D&I policies. • Policies to increase inclusion in the R&D&I workforce. • Mission-oriented innovation policies to support R&D&I activities to tackle specific social challenges. • Developing norms and practices to incorporate ethical considerations into technology development. Smarter data about smarter machines We argue that in order to be effective, third-wave R&D&I policies to steer AI in societally- beneficial trajectories need to be informed by new, ‘smarter’ data (Bakhshi and Mateos- Garcia 2016; Nesta 2019). By

- PDF页5：iented innovation policies to support R&D&I activities to tackle specific social challenges. • Developing norms and practices to incorporate ethical considerations into technology development. Smarter data about smarter machines We argue that in order to be effective, third-wave R&D&I policies to steer AI in societally- beneficial trajectories need to be informed by new, ‘smarter’ data (Bakhshi and Mateos- Garcia 2016; Nesta 2019). By this, we mean data that is: • Relevant: Smarter data for AI policies should capture AI R&D&I activity with high timeliness and resolution, helping to measure not only aggregate levels of AI activity but also their composition in terms of the technological trajectories that are being pursued and deployed (Teece 2008; Dosi 1982). It should also capture geographica

- PDF页6：rs based on publication and patent counts, number of AI businesses or university graduates with AI skills are insufficient to deliver the relevant and inclusive evidence that AI policymakers need. New data sources that capture the creative and collaborative mechanisms used in AI R&D&I – crucially including open source, data and dissemination channels as well as conventional Intellectual Property Rights – and its diffusion have much to contribute. Data science methods that extract quantitative patterns from text descriptions of AI R&D&I activities and enrich them with additional information about the identities of participants, their locations, affiliations, goals and networks can help capture the micro-dynamics of AI R&D&I and its drivers (Bakhshi and Mateos-Garcia 2016). This illustrates how

- PDF页6：te. Data science methods that extract quantitative patterns from text descriptions of AI R&D&I activities and enrich them with additional information about the identities of participants, their locations, affiliations, goals and networks can help capture the micro-dynamics of AI R&D&I and its drivers (Bakhshi and Mateos-Garcia 2016). This illustrates how AI and allied techniques such as machine learning and natural language processing can recursively transform its own analysis. However, like in other domains where AI is being applied, these methods also come with challenges. In particular, there is the risk that complex analytical methods to map AI may yield results that are difficult to explain, interpret or use to make policy decisions, or that the size and proprietary nature of the data so

## T4_人才大学与科研组织

- PDF页4：) policy framework (Nesta 2019). Differently from older (first wave) approaches that focused on increasing research and development investment levels without paying attention to its purpose (first wave), and (second wave) models aimed at increasing the transfer of knowledge from university to industry, the third wave of R&D&I policy is directional: it seeks to steer the development and diffusion of new technologies mindful of their purposes and impacts (Stirling 2009,

- PDF页5：and put in place interventions to bring it about (Mazzucato 2015, 2018; Kattel and Mazzucato 2018; Cantner and Vannuccini 2018). Some examples include: • Stronger levels of public engagement during the development of R&D&I policies. • Policies to increase inclusion in the R&D&I workforce. • Mission-oriented innovation policies to support R&D&I activities to tackle specific social challenges. • Developing norms and practices to incorporate ethical considerations into technology development. Smarter data about smarter machines We argue that in order to be effective, third-wave R&D&I policies to steer AI in societally- beneficial trajectories need to be informed by new, ‘smarter’ data (Bakhshi and Mateos- Garcia 2016; Nesta 2019). By this, we mean data that is: • Relevant: Smarter data for AI policie

- PDF页6：A Semantic Analysis of the Recent Evolution of AI Research 6 Traditional data sources and indicators based on publication and patent counts, number of AI businesses or university graduates with AI skills are insufficient to deliver the relevant and inclusive evidence that AI policymakers need. New data sources that capture the creative and collaborative mechanisms used in AI R&D&I – crucially including open source, data and dissemination channels as well as conventional Intellectual Property Rights – and its diffusion have much to contribute. Data science methods that extract quantitative patterns from text descriptions of AI R&D&I activities and enrich them with additional information abo

- PDF页6：ritical for determining where and how they can be used to make decisions. • Open: The best way to build trust in new data and methods is by making them openly available (while subject to constraints around the release of sensitive information such as personal data) so that other researchers can review, validate and build on them (Peng 2011; Burgess et al. 2016). This strategy makes it easier to improve methods, detect errors and combine sources to triangulate findings and explore new questions. It also reduces inefficiency in research and lowers barriers to the adoption of new techniques, making the field of AI mapping more inclusive too. In this report, we present a pipeline for data collection, processing and analysis of data about AI research that fulfils these features of relevance, inclusivenes

- PDF页7：1982; Kuhn 2012; W. Brian Arthur 1994; W. B. Arthur 1999; Garud and KarnÃže 2001). It acknowledges that historical phenomena are path-dependent and sometimes irreversible, potentially leading to sub-optimal outcomes (David 1985). Some of these ideas are echoed in the work of AI researchers and practitioners who have described the evolution of AI as a collection of parallel trajectories involving various technologies and markets that are integrated and interact as ‘Comprehensive AI Systems’ (David 1985; Drexler 2019). Others have called for better models of AI progress that measure the links between inputs (computation, data and skilled workers) and outputs (advances in AI capabilities) in order to inform technology foresight (Brundage 2016; Prediger 2017), and expressed concerns about how discrimin

- PDF页7：better models of AI progress that measure the links between inputs (computation, data and skilled workers) and outputs (advances in AI capabilities) in order to inform technology foresight (Brundage 2016; Prediger 2017), and expressed concerns about how discrimination in the AI workforce may embed discrimination in the (path-dependent) AI systems that are deployed (Stathoulopoulos and Mateos-Garcia 2019; Myers West, Whittaker, and Crawford 2019). The majority of these analyses have until now remained conceptual and qualitative. Parallel to them, we have started to see a growing number of studies that use novel methodologies to measure AI R&D&I activity. Some examples include maps of the AI research and development landscape using publications and patents (Elsevier 2018; Intellectual Property Offic

- PDF页7：rement of AI R&D&I using a variety of indicators that also capture skills supply and improvements in AI performance metrics among other factors (Index 2017, n.d.). Most of these analyses are descriptive, capturing the evolution of activity in AI R&D&I, its diffusion in different academic fields and its geography. Although several of them use natural language processing methods, such as topic modelling or keyword co-occurrence analysis to create topical maps of AI research and the trajectories that different countries specialise on, so far there has been limited effort to understand the reasons for the patterns that are identified and their theoretical or policy implications. There is a lack of standardisation in the strategies used to define and operationalise AI, creating the risk of contradictor

- PDF页8：18), and a study focusing on gender diversity in AI research, helping build the evidence base about (lack of) inclusion in the field (Stathoulopoulos and Mateos-Garcia 2019). In addition to publishing our results, we have released the data and code for our analysis so that other researchers can reproduce and build on our efforts.2 Here, we present new results of our analysis of AI activity in arXiv data with a particular focus on the research trajectories followed in ‘open’ AI R&D and their drivers. Our goal is to provide a detailed account of the recent evolution of the field – in particular, how it has been transformed by the advent of deep learning – and to illustrate opportunities to generate policy-relevant, smarter data about smarter machines, using data science methods and new combinations of

## T5_产业创新与成果转化

- PDF页3：networks, translation systems, voice assistants and (partially) self-driving cars (Brynjolfsson and McAfee 2014; McAfee and Brynjolfsson 2017). AI impacts and risks It is widely believed that AI systems could transform many domains beyond the technology sector including health, manufacturing, transport or scientific research (McAfee and Brynjolfsson 2017). They could also help tackle some of society’s biggest challenges, such as the prevention and treatment of chronic diseases, environmental sustainability and the decline in productivity in scientific research, to name a few (Topol 2019; Rolnick et al. 2019; Agrawal, McHale, and Oettl 2018). The broad relevance of the capability that AI systems promise to deliver (‘to behave appropriately in many different situations’) has led economists to herald AI

- PDF页4：und the world (Stilgoe et al. 2013; Jobin et al. 2019).1 These Strategies generally seek to nurture national high-growth AI industries, and encourage the diffusion of AI systems into other sectors in ways that are safe and consistent with ethical and political values. Meanwhile, private sector organisations, non-governmental organisations and the research community are creating ethical charters and guidelines to encourage responsible innovation (Jobin, Ienca, and Vayena 2019), and fairness, accountability and transparency, and safety research groups, are exploring technical and institutional solutions to various AI risks. Together, these activities represent an example of what we have described in previous work as a ‘third wave’ research, development and innovation (R&D&I) policy framework (Nesta 2019).

- PDF页4：work (Nesta 2019). Differently from older (first wave) approaches that focused on increasing research and development investment levels without paying attention to its purpose (first wave), and (second wave) models aimed at increasing the transfer of knowledge from university to industry, the third wave of R&D&I policy is directional: it seeks to steer the development and diffusion of new technologies mindful of their purposes and impacts (Stirling 2009,

- PDF页5：d, and Foray 2009; W. Brian Arthur 1994; David 1985). There are many potential reasons for this including random events, strategic behaviours (e.g. investments on marketing or lobbying) and the preferences of lead developers and adopters early in the lifecycle of a technology or industry (Brian Arthur 2014; Garud and KarnÃže 2001). Once a technology gains an early advantage against its competitors, network effects and sunk investments in complementary assets such as infrastructure and skills could make its success irreversible even if it is inferior in the longer run. An implication of this is that the emergence and deployment of new technologies does not have a single equilibrium. Instead, we could imagine a collection of parallel universes, each of which is dominated by a qualitatively different

- PDF页7：Relevant work and our contribution The notion of technological trajectory was put forward by evolutionary economists in the 1990s as a challenge to mainstream economics’ aggregate, undifferentiated ‘black box’ view of technological change, where innovation is conceptualised as a productivity-enhancing investment in knowledge, disregarding the fact that this could take many different forms and bring out wildly-varying outcomes in terms of economic structures, distributions of benefits and costs, technological risks etc (Dosi 1982). Influenced by economic history, sociology of science and complexity science, the analysis of technological trajectories pays strong attention to the historical process through which new technologies emerge and evolve, and the preferences, worldviews and goals of those involv

- PDF页8：ut the evolution of the field, providing a rationale for directional AI R&D&I policies. This report will be followed by a collection of case studies focusing on: • The connection between AI technological trajectories and gender diversity in research teams. • Participation of the private sector in AI research and its link with the research trajectories that are pursued. • Regional concentration of AI research and its links with the geography of automation (with a focus on England). • Participation of illiberal countries in AI research with a particular focus on their involvement in the development of controversial visual surveillance AI technologies. Together with the report, we have also published arXlive, an open-source, real-time tool to monitor AI research trends found in the arXiv repository, provid

- PDF页10：sis is arXiv, an open pre-prints website with 1.6 million papers that is widely used by various Science, Technology, Engineering and Mathematics research communities.4 In recent years, arXiv has become an important channel for the dissemination of AI research in academia and the private sector. As an example, almost all research papers by DeepMind and OpenAI, two leading AI research labs, are available from arXiv.5 Just under 60 per cent of the documents referenced in import ai, an influential newsletter monitoring AI research trends, are in arXiv.6 We collect data from arXiv and enrich it with information about the institutional affiliation of AI researchers and their location. Klinger et al (2018) and Stathoulopoulos et al (2019) provide a detailed account of the methodology used for this. Here we sum

- PDF页10：ation. We then match institutional affiliations with the Global Research Identifier Database (GRID), an open database of research institutions with information about their location and character (e.g. whether they are an educational, government or third-sector organisation, or a private sector company).7 This matching process leaves us with 2.7 million unique paper-author pairs with detailed institutional and geographical information (including the geographical coordinates of each institution). Semantic analysis We undertake four streams of semantic analysis with the abstracts available in the arXiv data. First, we use an expanded keyword search to identify AI and AI-related papers in the arXiv corpus. Full details of this analysis are available in Stathoulopoulos and Mateos-Garcia (2019). In summary, w

## T6_国际合作开放科学与比较

- PDF页6：d lowers barriers to the adoption of new techniques, making the field of AI mapping more inclusive too. In this report, we present a pipeline for data collection, processing and analysis of data about AI research that fulfils these features of relevance, inclusiveness, trust and openness with the goal informing directional AI policies. Before describing its pipeline, we summarise relevant work.

- PDF页9：key components of our analysis. Data sources and processing Our analysis involves a complex assemblage of data sources and methods. Figure 1 represents this pipeline. Figure 1: Data sources and process /uni00A0 arXiv Citations Places Titles Microsoft Academic Graph Institutions Global Research Identifier DatabasearXiv enriched Analysis AI detection Field classification Topic modelling

- PDF页10：ublished, if they were published through an outlet (this includes conference proceedings, an important dissemination channel in computer science), their citation counts, authors, and in particular their institutional affiliation. We then match institutional affiliations with the Global Research Identifier Database (GRID), an open database of research institutions with information about their location and character (e.g. whether they are an educational, government or third-sector organisation, or a private sector company).7 This matching process leaves us with 2.7 million unique paper-author pairs with detailed institutional and geographical information (including the geographical coordinates of each institution). Semantic analysis We undertake four streams of semantic analysis with the abstracts availabl

- PDF页23：da did when it continued supporting research in neural networks in the 1980s, when many other countries abandoned it, disappointed by its lack of progress. This provided the foundation for the deep learning revolution that we are witnessing today. Funding programmes to encourage collaboration between research communities working with connectionist methods and other techniques that are less data hungry, more explainable and more robust, could also help build AI systems bringing together the best of both worlds.

- PDF页29：as a charity in Scotland number SCO42833. Registered office: 58 Victoria Embankment, London, EC4Y 0DS. About Nesta Nesta is a global innovation foundation. We back new ideas to tackle the big challenges of our time. We use our knowledge, networks, funding and skills – working in partnership with others, including governments, businesses and charities. We are a UK charity but work all over the world, supported by a financial endowment. To find out more visit www.nesta.org.uk If you’d like this publication in an alternative format such as Braille, large print, please contact us at: information@nesta.org.uk

## T7_中国科技横向维度

- PDF页2：on overtaking symbolic and statistical methods: the share of papers about deep learning has multiplied four-fold since 2012, while the share of papers using statistical methods has halved. These thematic changes have been accompanied by shifts in the geography of the field, with China trebling its share of global AI research since 2012 and some European countries falling behind, especially in cutting edge methods. In forthcoming work, we will explore how various factors such as gender diversity, corporate participation, regional clustering and the involvement of countries with different political values in AI research are shaping its trajectories. This analysis will illustrate how smarter data about smarter machines can inform activist AI R&D&I policies to steer AI in a direction where its bene

- PDF页20：ps in Figure 10 show the level of AI research activity in ‘classical’ topics related to symbolic and statistical methods (in the top) and topics related to deep learning (in the bottom). Its results are consistent with findings of previous research where we provided evidence for China’s comparative advantage in AI research. By comparison, European Union (EU) countries appear relatively specialised in classical and symbolic methods. Figure 10: National research activity in various AI topics Bar depth/colour represents specialisation in symbolic and statistics topics Number of papers in deep learning topics Number of papers in symbolic and statistics topics Bar depth/colour represents relative specialisation in deep learning topics 1400 1200 1000 800 600 400 200 0 2500 2000 1500 1000 500 0

- PDF页21：A Semantic Analysis of the Recent Evolution of AI Research 21 The results in figure 11 could be partly explained by compositional changes (i.e. the fact that China joined the AI research field more recently, when the focus of activity had shifted to deep learning related topics). In Figure 12 we try to account for this by comparing a country’s share of activity in all of arXiv, all AI research and State of the Art (SotA) AI topics in the period before 2012 and the period after 2015, focusing on the top ten countries by total levels of AI activity. We want to measure changes in countries’ importance in each of these fields and compare volatility across fields. Figure 11: Chan

- PDF页21：es The figure shows that the US is dominant in the three fields. While its relative importance in the overall arXiv corpus has declined as other countries start publishing more research there, its importance in AI research and in SotA topics in this area has increased over time. China has experienced rapid growth in recent years, almost trebling its participation in AI research – especially in SotA (deep learning) topics. We do not observe a comparable increase in China’s arXiv general activity, supporting the idea that it has a strategic focus (or revealed comparative advantage) in AI and especially SotA AI topics. Percentage of all activity with presence United States China United Kingdom Germany Australia France Canada Italy Japan Switzerland 40 35 30 25 20 15 10 5 0 All arXiv before 2012 Al

- PDF页21：tA (deep learning) topics. We do not observe a comparable increase in China’s arXiv general activity, supporting the idea that it has a strategic focus (or revealed comparative advantage) in AI and especially SotA AI topics. Percentage of all activity with presence United States China United Kingdom Germany Australia France Canada Italy Japan Switzerland 40 35 30 25 20 15 10 5 0 All arXiv before 2012 All AI before 2012 All SotA before 2012 All arXiv after 2015 All AI after 2015 All SotA after 2015

- PDF页28：5. See https:/ /openai.com/progress/#papers and https:/ /deepmind.com/research 6. https:/ /jack-clark.net/ 7. https:/ /www.grid.ac/ 8. This approach has been inspired by an analysis of about structural change in the biofuel industry (Parraguez [forthcoming]). 9. When we exclude China from the analysis, the variances in change rates between AI and arXiv overall become quite similar, but the geography of SotA topics remains more volatile, suggesting that the geography of modern AI methods is being more strongly disrupted than older topics for AI research.
