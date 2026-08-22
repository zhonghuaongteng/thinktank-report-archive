# C-STANFORD-HAI-WHITE-PAPER-BUILDING-NATIONAL-AI-RESEARCH-RESOURCE 原文切片

- 原文：`03_证据底稿\原文PDF\C-STANFORD-HAI-WHITE-PAPER-BUILDING-NATIONAL-AI-RESEARCH-RESOURCE.pdf`
- PDF页数：109
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 3

Contributors
Many dedicated individuals contributed to this White Paper. To acknowledge these contributions,
we list here the contributors for each chapter and section.

Executive Summary and Introduction
Daniel E. Ho, Tina Huang, Jennifer King, Marisa Lowe, Diego Núñez, Russell Wald, Christopher Wan,
Daniel Zhang

The Theory for a National Research Cloud
Nathan Calvin, Shushman Choudhury, Tina Huang, Daniel E. Ho, Kanishka Narayan, Diego Núñez,
Frieda Rong, Russell Wald, Christopher Wan

Eligibility, Allocation, and Infrastructure for Computing
Daniel E. Ho, Krithika Iyer, Tyler Robbins, Jasmine Shao, Russell Wald, Daniel Zhang

Securing Data Access
Nathan Calvin, Shushman Choudhury, Daniel E. Ho, Ananya Karthik, Jennifer King, Christopher Wan

Organizational Design
Sabina Beleuz, Drew Edwards, Daniel E. Ho, Jennifer King, Christopher Wan

Data Privacy Compliance
Simran Arora, Neel Guha, Jennifer King, Sahaana Suri, Sadiki Wiltshire, Christopher Wan

Technical Privacy and Virtual Data Safe Rooms
Neel Guha, Jennifer King, Christopher Wan

Safeguards for Ethical Research
Daniel E. Ho, Jennifer King, Diego Núñez, Russell Wald, Daniel Zhang

Managing Cybersecurity Risks
Neel Guha, Diego Núñez, Frieda Rong, Russell Wald

Intellectual Property
Sabina Beleuz, Daniel E. Ho, Ananya Karthik, Diego Núñez, Christopher Wan

Case Studies
Daniel E. Ho, Krithika Iyer, Jennifer King, Marisa Lowe, Kanishka Narayan, Tyler Robbins

We also would like to thank Jeanina Casusi, Celia Clark, Shana Lynch, Kaci Peel, Stacy Peña,
Mike Sellitto, Eun Sze, and Michi Turner for their help in preparing this White Paper.

3

### PDF页 7

Building a National AI Research Resource:
A Blueprint for the National Research Cloud
7
Table of Contents
EXECUTIVE SUMMARY: Creating a National Research Cloud 9
INTRODUCTION 15
CHAPTER 1: A Theory for a National Research Cloud 17
CHAPTER 2: Eligibility, Allocation, and Infrastructure for Computing 22
CHAPTER 3: Securing Data Access 35
CHAPTER 4: Organizational Design 48
CHAPTER 5: Data Privacy Compliance 53
CHAPTER 6: Technical Privacy and Virtual Data Safe Rooms 61
CHAPTER 7: Safeguards for Ethical Research 66
CHAPTER 8: Managing Cybersecurity Risks 70
CHAPTER 9: Intellectual Property 76
GLOSSARY OF ACRONYMS 82
APPENDIX 84
ENDNOTES 90

### PDF页 9

Building a National AI Research Resource:
A Blueprint for the National Research Cloud
9
Artificial intelligence (AI) appears poised to transform the economy across sectors ranging from healthcare and finance,
to retail and education. What some have coined the “Fourth Industrial Revolution”1 is driven by three key trends: greater
availability of data, increases in computing power, and improvements to algorithm design. First, increasingly large amounts
of data have fueled the ability for computers to learn, such as by training an algorithmic language model on all of Wikipedia.2
Second, better computational capacity (often termed “compute”) and compute capability have enabled researchers to build
models that were unimaginable merely 10 years ago, sometimes spanning billions of parameters (an exponential increase
in scope from previous models).3 Third, basic innovations in algorithms are helping scientists to drive forward AI, such as the
reinforcement learning techniques that enabled a computer to defeat the world champion in the board game Go.4
Historically, partnerships between government(s), universities, and industries have anchored the U.S. innovation
ecosystem. The federal government played a critical role in subsidizing basic research, enabling universities to undertake
high-risk research that can take decades to commercialize. This approach catalyzed radar technology, the internet, and
GPS devices. As the economists Ben Jones and Larry Summers put it, “[e]ven under very conservative assumptions, it is
difficult to find an average return below $4 per $1 spent” on innovation, and the social returns might be closer to $20 for
every dollar spent.5 Industry in turn, scales and commercializes applications.
CHALLENGES TO THE AI INNOVATION ECOSYSTEM
Yet this innovation ecosystem faces serious potential challenges. Computing power has become critical for the
advancement of AI, but the high cost of compute has placed cutting edge AI research in a position accessible only to key
industry players and a handful of elite universities.6 Access to data—the raw ingredients used to train most AI models—is
increasingly limited to the private sector and large platforms7, since government data sources remain largely inaccessible
to the AI research community.8 As the National Security Commission on AI (NSCAI) has determined, “[t]he consolidation
of the AI industry threatens U.S. technological competitiveness. ”9
Four interrelated challenges illustrate this finding: First, we are seeing a significant brain drain of researchers
departing universities.10 In 2011, AI Ph.D.s were roughly equally likely to go into industry vs. academia.11 Ten years later,
two- thirds of AI Ph.D.s go to industry, and less than one quarter go into academia.12 Second, these trends indicate that
many university researchers struggle to engage in cutting-edge science, draining the field of the diverse set of research
voices that it needs. Third, the fundamental research that would guarantee the United States stays at the helm of AI
innovation is being crowded out. By one estimate, 82 percent of algorithms used today originated from federally funded
nonprofits and universities, but “U.S. leadership has faded in recent decades. ”13 Fourth, government agencies have faced
challenges in building compute infrastructure,14 and there are societal benefits to reducing the cost of core governance
functions and improving government’s internal capacity to develop, test, and hold AI systems accountable.15 In short,
a growing imbalance in AI innovation tilts towards industry, leaving academic and non-commercial research behind.
Given the longstanding role of academic and non-commercial research in innovation, this shift has substantial negative
consequences for the American research ecosystem.
Executive Summary:
Creating a National Research Cloud

## T1_国家研发与方向设定

- PDF页2：Information. Prior to joining HAI, Dr. King was the Director of Consumer Privacy at the Center for Internet and Society at Stanford Law School from 2018 to 2020. Russell C. Wald is the Director of Policy for the Stanford HAI, leading the team that advances HAI’s engagement with governments and civil society organizations. Since 2013, Wald has held various government affair roles representing Stanford University. He is a Term Member with the Council on Foreign Relations, Visiting Fellow with the National Security Institute at George Mason University, and a Partner with the Truman National Security Project. Wald is a graduate of UCLA. Christopher Wan is a JD/MBA candidate at Stanford University and was Teaching Assistant for the Stanford Policy Practicum: Creating a National Research Cloud. He also s

- PDF页5：Taka Ariga Government Accountability Office Kathy Baxter Salesforce Leisel Bogan Belfer Center Harvard University Jeffrey Brown IBM Miles Brundage Open AI L. Jean Camp University of Indiana at Bloomington Dakota Cary Center for Security and Emerging Technology Georgetown University Shikai Chern Veritas Technologies Isabella Chu Population Health Sciences Stanford University Jack Clark Anthropic Meaghan English Patrick J. McGovern Foundation Cyrus Hodes The Future Society Sara Jordan The Future of Privacy Forum Vince Kellen U.C. San Die

- PDF页5：Force Organisation for Economic Co-operation and Development (OECD) Lee Tiedrich Covington & Burling LLP Evan White California Policy Lab U.C. Berkeley On August 5, 2021, the co-authors hosted a feedback session to hear from a variety of stakeholders in academia, civil society, government, and industry. We are thankful for the time and helpful advice participants offered. Workshop attendee affiliations are listed for identification purposes only. Individuals from Microsoft and AI Now also attended the workshop but did not want to be personally identified. Workshop Participants 5

- PDF页9：crease in scope from previous models).3 Third, basic innovations in algorithms are helping scientists to drive forward AI, such as the reinforcement learning techniques that enabled a computer to defeat the world champion in the board game Go.4 Historically, partnerships between government(s), universities, and industries have anchored the U.S. innovation ecosystem. The federal government played a critical role in subsidizing basic research, enabling universities to undertake high-risk research that can take decades to commercialize. This approach catalyzed radar technology, the internet, and GPS devices. As the economists Ben Jones and Larry Summers put it, “[e]ven under very conservative assumptions, it is difficult to find an average return below $4 per $1 spent” on innovation, and the social ret

- PDF页9：st of compute has placed cutting edge AI research in a position accessible only to key industry players and a handful of elite universities.6 Access to data—the raw ingredients used to train most AI models—is increasingly limited to the private sector and large platforms7, since government data sources remain largely inaccessible to the AI research community.8 As the National Security Commission on AI (NSCAI) has determined, “[t]he consolidation of the AI industry threatens U.S. technological competitiveness. ”9 Four interrelated challenges illustrate this finding: First, we are seeing a significant brain drain of researchers departing universities.10 In 2011, AI Ph.D.s were roughly equally likely to go into industry vs. academia.11 Ten years later, two- thirds of AI Ph.D.s go to industry, and less

- PDF页9：search that would guarantee the United States stays at the helm of AI innovation is being crowded out. By one estimate, 82 percent of algorithms used today originated from federally funded nonprofits and universities, but “U.S. leadership has faded in recent decades. ”13 Fourth, government agencies have faced challenges in building compute infrastructure,14 and there are societal benefits to reducing the cost of core governance functions and improving government’s internal capacity to develop, test, and hold AI systems accountable.15 In short, a growing imbalance in AI innovation tilts towards industry, leaving academic and non-commercial research behind. Given the longstanding role of academic and non-commercial research in innovation, this shift has substantial negative consequences for the Americ

- PDF页10：implementation of a “National Artificial Intelligence Research Resource, ” (NAIRR) namely “a system that provides researchers and students across scientific fields and disciplines with access to compute resources, co-located with publicly available, artificial intelligence-ready government and non-government data sets. ”18 This research resource has also been referred to as the National Research Cloud (NRC) and was strongly endorsed by the NSCAI, which wrote that the NRC “will strengthen the foundation of American AI innovation by supporting more equitable growth of the field, expanding AI expertise across the country, and applying AI to a broader range of fields. ”19 While other initiatives have sought to improve access to compute or data in isolation,20 the NRC will generate distinct positive exte

- PDF页10：ccess to compute or data in isolation,20 the NRC will generate distinct positive externalities by integrating compute and data, the two bottlenecks for high-quality AI research. Specifically, the NRC will provide affordable access to high-end computational resources, large-scale government datasets in a secure cloud environment, and the necessary expertise to benefit from this resource through a close partnership between academia, government, and industry. By expanding access to these critical resources in AI research, the NRC will support basic scientific AI research, the democratization of AI innovation, and the promotion of U.S. leadership in AI. THEMES Stanford Law School’s Policy Lab program convened a multidisciplinary research team of graduate students, staff, and faculty drawn from Stanford’

## T2_市场与产业政策边界

- PDF页9：for the advancement of AI, but the high cost of compute has placed cutting edge AI research in a position accessible only to key industry players and a handful of elite universities.6 Access to data—the raw ingredients used to train most AI models—is increasingly limited to the private sector and large platforms7, since government data sources remain largely inaccessible to the AI research community.8 As the National Security Commission on AI (NSCAI) has determined, “[t]he consolidation of the AI industry threatens U.S. technological competitiveness. ”9 Four interrelated challenges illustrate this finding: First, we are seeing a significant brain drain of researchers departing universities.10 In 2011, AI Ph.D.s were roughly equally likely to go into industry vs. academia.11 Ten years later, two- thirds

- PDF页10：e observed was a decoupling of compute resources from data infrastructures. The NRC directs more resources toward AI development in the public interest and helps ensure long-term leadership by the United States in the field by supporting the kind of pure, basic research that the private sector cannot undertake alone.

- PDF页11：sharing, particularly for high-value government data, lies in requirements for a secure, privacy- protecting computing environment. • Rebalancing AI research toward long-term, academic, and non-commercial research. Presently, AI innovation is disproportionately dependent on the private sector. Public investment in basic AI infrastructure can both support innovation in the public interest and complement private innovation efforts. The NRC directs more resources toward AI development in the public interest and helps ensure long-term leadership by the United States in the field by supporting the kind of pure, basic research that the private sector cannot undertake alone. • Coordinating short-term and long-term approaches to creating the NRC. Our research considers many near-term pathways for standing up a

- PDF页11：nnovation in the public interest and complement private innovation efforts. The NRC directs more resources toward AI development in the public interest and helps ensure long-term leadership by the United States in the field by supporting the kind of pure, basic research that the private sector cannot undertake alone. • Coordinating short-term and long-term approaches to creating the NRC. Our research considers many near-term pathways for standing up a working version of the NRC by spelling out how to work within existing constraints. We also identify the structural, legal, and policy challenges to be addressed in the long term for executing the full vision of the NRC. We summarize our main recommendations here. COMPUTE MODEL • The “Make or Buy” Decision. The main policy choice will be whether to build p

- PDF页12：standards. • Strategic Investment for Data Sources. In the short term, we recommend that the NRC focus its efforts on making available non-sensitive, low- to moderate-risk government datasets, rather than sensitive government data (e.g., data about individuals) or data from the private sector, due to data privacy and intellectual property concerns. Researchers can still use NRC compute resources on private data, but should rely on existing mechanisms to acquire data for their own private buckets on the NRC. For example, images taken from Earth observation satellites, such as

- PDF页17：17 A Blueprint for the National Research Cloud CHAPTER 1 This chapter articulates a theory of impact for the NRC. In conventional policy analytic terms,1 what problem (or market failure) does the NRC address? From one perspective, AI innovation is vibrant in the United States, with major advances occurring in language, vision, and structured data and applications developing across all sectors. Yet from another perspective, current commercialization of past innovation masks systematic underinvestment in basic, non-commercial AI research that could ensure the long-term health of technological innovation in this country. Chapter 1: The Theory for a National Research Cloud KEY TAKEAWAYS The federal g

- PDF页17：Cloud KEY TAKEAWAYS The federal government will play a central role in shaping, coordinating, and enabling the development of AI. AI research and development is increasingly dependent on access to large-scale compute and data, causing migration of AI talent from the academic to private sector and limiting the range of voices able to contribute to AI research. Noncommercial and basic AI research is critical to the long-term health of the innovation ecosystem. An NRC that provides data and compute access will help to promote the long- term, national health of the AI ecosystem and mitigate the risks of widening inequalities in the nation’s AI landscape. Current commercialization of past innovation masks systematic underinvestment in basic, non-commercial AI research that could ensure the long-term health

- PDF页17：I research is critical to the long-term health of the innovation ecosystem. An NRC that provides data and compute access will help to promote the long- term, national health of the AI ecosystem and mitigate the risks of widening inequalities in the nation’s AI landscape. Current commercialization of past innovation masks systematic underinvestment in basic, non-commercial AI research that could ensure the long-term health of technological innovation in this country. Our case for the NRC is grounded in both efficiency and distributive rationales. First, the NRC may yield positive externalities, particularly over time, by supporting investments in basic research that may be commercialized decades later. Second, it may help to level the playing field by broadening researcher access to both compute and data, e

## T4_国际合作与开放

- PDF页8：for the National Research Cloud 8 COMPUTE MODELS NSF CloudBank 27 NSF XSEDE 29 Fugaku 32 Compute Canada 34 DATA MODELS Coleridge Initiative 42 Stanford Population Health Sciences 43 The Evidence Act 46 ORGANIZATIONAL MODELS Science and Technology Policy Institute 50 Alberta Data Partnerships 51 OTHER MODELS Administrative Data Research UK 58 California Policy Lab 64 Case Studies

- PDF页9：rs (an exponential increase in scope from previous models).3 Third, basic innovations in algorithms are helping scientists to drive forward AI, such as the reinforcement learning techniques that enabled a computer to defeat the world champion in the board game Go.4 Historically, partnerships between government(s), universities, and industries have anchored the U.S. innovation ecosystem. The federal government played a critical role in subsidizing basic research, enabling universities to undertake high-risk research that can take decades to commercialize. This approach catalyzed radar technology, the internet, and GPS devices. As the economists Ben Jones and Larry Summers put it, “[e]ven under very conservative assumptions, it is difficult to find an average return below $4 per $1 spent” on innovation

- PDF页10：a, the two bottlenecks for high-quality AI research. Specifically, the NRC will provide affordable access to high-end computational resources, large-scale government datasets in a secure cloud environment, and the necessary expertise to benefit from this resource through a close partnership between academia, government, and industry. By expanding access to these critical resources in AI research, the NRC will support basic scientific AI research, the democratization of AI innovation, and the promotion of U.S. leadership in AI. THEMES Stanford Law School’s Policy Lab program convened a multidisciplinary research team of graduate students, staff, and faculty drawn from Stanford’s business, law, and engineering schools to study the feasibility of, and considerations for designing the NRC. Over the past

- PDF页10：nge of government, computer science, and policy experts, and examined the technical, business, legal, and policy requirements. This White Paper was commissioned by Stanford’s Institute for Human-Centered Artificial Intelligence (HAI), which originated the proposal for the NRC in partnership with 21 other research universities.21 Throughout our research, we observed three primary themes that cut across all areas of our investigation. We have integrated these themes into each section of our White Paper and drawn on them to explain our findings. • Complementarity between compute and data. As we evaluated the existing computing and data-sharing ecosystems, one of the systemic challenges we observed was a decoupling of compute resources from data infrastructures. The NRC directs more resources toward AI d

- PDF页13：ng Act of 2018, have proven to be among the most daunting challenges of government modernization.31 Building on those insights, we ultimately recommend that the NRC be instituted as a Federally Funded Research and Development Center (FFRDC) in the short run, and a public-private partnership (PPP) in the long run. • FFRDC. FFRDCs at Affiliated Government Agencies would reduce the significant costs of securing data from those host agencies. This approach will also cohere with the greater reliance on commercial cloud credits in the short run, making compute and data coordination less central. In the long run, however, streamlined coordination between data and compute may be more difficult with FFRDCs hosted at specific agencies when (1) the NRC moves away from commercial cloud credits and towards its ow

- PDF页18：may be the COVID-19 HPC consortium which quickly provisioned compute of 50K GPUs and 6.8 million cores for close to 100 projects across 43 academic, industry, and federal government consortium members united by the common goal of combating the COVID-19 pandemic.16 Historically, partnerships between government, universities, and industry have anchored the U.S. innovation ecosystem. The federal government played critical roles in subsidizing basic research, enabling universities to undertake high-risk research that can take decades to commercialize. This approach catalyzed radar technology,17 the internet, 18 and GPS devices.19 This history informed the NSCAI’s recommendation for substantial new investments in AI R&D by establishing a national AI research infrastructure that democratizes access to the

- PDF页21：search trajectories—that is, the specific questions, topics, and problems researchers choose to investigate—has become more constrained in recent years and that private sector AI research is less diverse than academic research.50 Smaller academic groups with lower private sector collaboration appear to bolster the diversity of AI research.51 From the standpoint of underdeveloped avenues of research, such as ethics and accountability in AI, increasing the range of research topics and methods in the field raises the likelihood of finding breakthroughs that make additional progress possible in the long term possible.52 Recent evidence suggests that just five metro areas in the U.S. shared 90 percent of the growth in innovation sector jobs, between 2005 and 2017.53 According to Stanford economist Erik Bryn

- PDF页27：allocation models. Accessible through a portal, CloudBank aids researchers in using cloud resources fully by facilitating the process of “managing costs, translating and upgrading computing environments to the cloud, and learning about cloud-based technologies.”25 CloudBank is a collaboration project established via an NSF Cooperative Agreement with the San Diego Supercomputer Center (SDSC) and the Information Technology Services Division at UC San Diego, the University of Washington eScience Institute, and UC Berkeley’s Division of Data Science and Information.26 Each of these institutions handles an area, according to its comparative advantage.27 For example, SDSC is responsible for building the online portal, and UC San Diego is in charge of managing the accounts of the users.28 CloudBank also aims

## T5_供应链与技术依赖

- PDF页6：Stanford faculty and researchers. Directed by former SLS Dean Paul Brest, the Policy Lab reflects the school’s belief that systematic examination of societal problems, informed by rigorous research, can generate solutions to society’s most challenging public problems. Academic Independence This White Paper was developed independently by the research team. While we solicited feedback from a wide range of stakeholders, no HAI donors, corporations, or other stakeholders had any involvement with the research and production of this White Paper. Per HAI policy, “Donors cannot dictate research topics pursued by HAI researchers” nor “control permission to publish research results.” For more information, please see HAI’s policy: https:/ /hai.stanford.edu/about/fundraising-policy. 6

- PDF页99：tatistics and Evidence Building (2020). 5 Id. at 26. 6 Id. at 26-27, 29-30. 7 U.S. Gov’t Accountability Office, supra note 3, at 6. Note that while the FFRDC must operate to serve its sponsors, in establishing an FFRDC, the sponsor must ensure that it operates with substantial independence; the FFRDC must be “operated, managed, or administered by an autonomous or- ganization or as an identifiably separate operating unit of a parent organization. ” See Federal Acquisition Regulations [hereinafter “FAR”] § 35.017(a)(2). 8 One example of this is the Science & Technology Policy Institute, which we discuss in a case study below. 9 U.S. Dep’t of Energy, The State of the DOE National Laboratories 11-13 (2020). 10 See, e.g., More Federal Agencies Head to the Cloud With Azure Government, Applied Info. Sci. (

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页2：conomic Policy Research at Stanford University. He directs the Regulation, Evaluation, and Governance Lab (RegLab) at Stanford, and is a Faculty Fellow at the Center for Advanced Study in the Behavioral Sciences and Associate Director of the Stanford Institute for Human-Centered Artificial Intelligence (HAI). He received his J.D. from Yale Law School and Ph.D. from Harvard University and clerked for Judge Stephen F. Williams on the U.S. Court of Appeals for the District of Columbia Circuit. Jennifer King, Ph.D., is the Privacy and Data Policy Fellow at the Stanford HAI. Dr. King completed her doctorate in Information Management and Systems (information science) at the University of California, Berkeley School of Information. Prior to joining HAI, Dr. King was the Director of Consumer Privacy at the Center for In

- PDF页2：nt for the Stanford HAI and as an investor at Bessemer Venture Partners. He received his B.S. in Computer Science from Yale University and worked as a software engineer at Facebook and as a venture investor at In-Q-Tel and Tusk Ventures. The Stanford Institute for Human-Centered Artificial Intelligence Cordura Hall, 210 Panama Street, Stanford, CA 94305-4101 October 2021, V1.0 2

- PDF页5：Taka Ariga Government Accountability Office Kathy Baxter Salesforce Leisel Bogan Belfer Center Harvard University Jeffrey Brown IBM Miles Brundage Open AI L. Jean Camp University of Indiana at Bloomington Dakota Cary Center for Security and Emerging Technology Georgetown University Shikai Chern Veritas Technologies Isabella Chu Population Health Sciences Stanford University Jack Clark Anthropic Meaghan English Patrick J. McGovern Foundation Cyrus Hodes The Future Society Sara Jordan The Future of Privacy Forum Vince Kellen U.C. San Diego, CloudBank Michael Kratsios Scale AI Samantha Lai Brookings Institution Brenda Leong The Future of Privacy Forum Ruth Marinshaw Stanford Research Computing Center Joshua Meltzer Brookings Institution Sam Mulopulous U.S. Senate Dewey Mu

- PDF页5：U.C. San Diego, CloudBank Michael Kratsios Scale AI Samantha Lai Brookings Institution Brenda Leong The Future of Privacy Forum Ruth Marinshaw Stanford Research Computing Center Joshua Meltzer Brookings Institution Sam Mulopulous U.S. Senate Dewey Murdick Center for Security and Emerging Technology Georgetown University Hodan Omaar Center for Data Innovation Calton Pu Georgia Tech Asad Ramzanali U.S. House of Representatives David Robinson Upturn Saiph Savage Northeastern University Michael Sellitto Stanford HAI Ishan Sharma Federation of American Scientists John Smith IBM Brittany Smith Data and Society Victor Storchan JP Morgan Chase Keith Strier AI Compute Task Force Organisation for Economic Co-operation and Development (OECD) Lee Tiedrich Covington & Burling LLP Evan White California Policy Lab U.C. Be

- PDF页6：Disclosures Stanford University actively engaged with Congress and lobbied for the National Artificial Intelligence Research Resource Task Force Act. Co-author Russell Wald built a coalition of academic, civil society, and industry stakeholders and lobbied Congress to pass the National Artificial Intelligence Research Resource Task Force Act. HAI Co-Director Fei-Fei Li, who served as a guest lecturer in the class, was an early supporter of a task force to study the National Research Cloud. Dr. Li has been appointed to serve as a member of the National Artificial Intelligence Research Resource (NAIRR) Task Force. Co-author Danie

- PDF页6：nt program; and Google’s Cloud credit grant for COVID-19 research. Co-author Jennifer King received unrestricted gift funding for research from Mozilla, Facebook, and Accenture in her previous role at the Center for Internet and Society. The Stanford Institute for Human-Centered Artificial Intelligence (HAI) receives financial and cloud computing support from A121 Labs, Amazon Web Services, Google, IBM, Microsoft, and OpenAI. About HAI About the SLS Policy Lab Stanford University’s Institute for Human-Centered Artificial Intelligence (HAI) applies rigorous analysis and research to pressing policy questions on artificial intelligence. A pillar of HAI is to inform policymakers, industry leaders, and civil society by disseminating scholarship to a wide audience. HAI is a nonpartisan research institute, representing

- PDF页6：d computing support from A121 Labs, Amazon Web Services, Google, IBM, Microsoft, and OpenAI. About HAI About the SLS Policy Lab Stanford University’s Institute for Human-Centered Artificial Intelligence (HAI) applies rigorous analysis and research to pressing policy questions on artificial intelligence. A pillar of HAI is to inform policymakers, industry leaders, and civil society by disseminating scholarship to a wide audience. HAI is a nonpartisan research institute, representing a range of voices. The views expressed in this White Paper reflect the views of the authors. The Policy Lab at Stanford Law School offers students an immersive experience in finding solutions to some of the world’s most pressing issues under the direction of Stanford faculty and researchers. Directed by former SLS Dean Paul Brest, the

- PDF页9：Building a National AI Research Resource: A Blueprint for the National Research Cloud 9 Artificial intelligence (AI) appears poised to transform the economy across sectors ranging from healthcare and finance, to retail and education. What some have coined the “Fourth Industrial Revolution”1 is driven by three key trends: greater availability of data, increases in computing power, and improvements to algorithm design. First, increasingly large amounts of data have fueled the ability for computers to learn, such as by training an algorithmic language model on all of Wikipedia.2 Second, better computational capacity (often ter

## T10_预见与优先领域

- PDF页33：re. We use a 10 percent discount that was negotiated by a major research university with a commercial cloud provider. In contrast, the government would need to negotiate an 88 percent discount for AWS to be cost-competitive with a dedicated HPC cluster in the long run. Even in a scenario where NRC usage fluctuates dramatically, commercial cloud computing could cost 2.8 times Summit’s estimated cost. (While variability in usage factors heavily into these estimates, the use of schedulers can contribute to a smoothening out of demand.93) These cost estimates have important limitations. First, government may be able to negotiate the cost down. We have used as a benchmark one major university’s enterprise agreement with AWS, which provides a 10 percent discount, relative to market rates. But, unless th

- PDF页55：gement of such rights such free speech, by enabling persecution across the many areas in which a U.S. citizen or resident interacts with the federal system.19 Because the restriction on data linkages applies to linkages between agencies, the restriction applies in two particular scenarios for the NRC. First, if the NRC is instituted as a federal agency, then agency data-sharing with the NRC would run against the data linkages limitation of the Privacy Act. Second, federal agency staff access to the NRC could raise questions about inter- agency data linkage under the Privacy Act. However, the recommendation in Chapter Three is focused on granting agencies streamlined access to the computing resources on the NRC and their own agency data, not to any multi- agency data hosted on the NRC. If the NRC i

- PDF页75：, without sharing outright. Federated learning addresses this situation, for example, demonstrating how users’ mobile phones can send information—possibly differentially private—to central servers without exposing the precise details of any one individual’s information. A second scenario more relevant to the large-scale decentralized nature of the NRC is distributed computing— in which many institutions collectively share compute, akin in some respects to crowd-sourced computing. These approaches enable multiple parties to leverage existing computational infrastructure, while retaining some guarantees on privacy. CRYPTOGRAPHY-BASED MEASURES Finally, there are two types of cryptography-based measures worth noting. Cryptography researchers have developed ways of computing mathematical operations ove

- PDF页78：whether AI-generated creative works like music from OpenAI’s Jukebox,28 can or should receive copyright protection.29 However, the technology and copyright community has hardly reached a consensus on whether the public interest in AI research requires granting copyright in these scenarios. On one hand, in a survey of AI scientists, tech policy experts, and copyright scholars, roughly 54 percent of respondents agreed that copyright protection is an important incentive for authors to make their work commercially available, and 63 percent agreed that an increase in the number of commercially available AI-produced works would stimulate further AI growth and research.30 On the other hand, in the same survey approximately 56 percent of respondents agreed that the U.S. Copyright Office should deny copyri

- PDF页79：data rights under the Uniform Guidance. However, we also reiterate that the Uniform Guidance serves merely as a helpful framework, not as an immutable rule. Where the Uniform Guidance IP allocation would dissuade researchers from using the NRC or hinder AI innovation in specific scenarios, the government can and should explicitly modify its rights and contract separately with researchers on what rights the government retains, if any.
