# L-F9DDAD8CD2 原文切片

- 原文：`03_证据底稿\原文PDF\L-F9DDAD8CD2.pdf`
- PDF页数：99
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 5

v
Summary
Algorithmic insights—the novel techniques, methods, and design know-how that materially improve artifi -
cial intelligence (AI) systems—are among the most strategically valuable assets in the AI ecosystem. Across
language models evaluated from 2012 to 2023, the compute required to reach a fixed performance threshold
fell by half approximately every eight months due to algorithmic efficiency improvements, which is equiva -
lent to roughly a threefold annual gain in effective compute. Theft or leakage of these insights could compress
years of AI progress for adversaries, and some insights might also lower barriers to dangerous capabilities,
making their protection a matter not only of commercial interest but of national security.
Unlike model weights, which can be centralized on secured servers, algorithmic insights resist centraliza -
tion: They exist as part of code, documentation, communications, and human knowledge, and the insights
can leak through low-bandwidth channels, such as conversations or observable screens. Although insights’
distributed nature makes them harder to protect than weights, the challenge is not intractable. Organizations
can take concrete, practical steps to substantially reduce the risk of unauthorized access to such insights. Fur-
thermore, the measures required at lower security levels (SLs) align closely with industry best practices that
most frontier AI developers might already be implementing.
In this report, we extend a framework from the RAND report Securing AI Model Weights (SMW) to pro -
vide the first systematic roadmap for protecting algorithmic insights.
2 We define five insight security levels
(ISLs) aligned with five adversary operational capacities (OCs), identify 44 attack vectors, and provide bench-
mark security systems for each level. The framework is intentionally descriptive rather than prescriptive: It
provides a tool for answering the conditional question, “If an organization wishes to—or is expected
to—secure insight X against an adversary with capability level Y, what security posture would likely be
required?” After answering this question, organizations can make informed decisions about which insights
warrant security investments using their own assessments, priorities, and cost-benefit analyses.
Key Findings
• Some properties that make insights valuable also make them difficult to secure. A lgorithmic insights
are often conceptually compact, broadly applicable, and easily transferable, which means that they can
leak through a wide variety of channels. Unauthorized proliferation could erase competitive or strategic
advantages that took years and billions of dollars to establish, and overcoming this challenge requires a
comprehensive security approach rather than protections of a few obvious assets.
•
 Th
e attack surface is broad and extends well beyond cyberthreats. The attack vectors that we identi -
fied reflect the diversity of technical, organizational, and human pathways through which insights can
leak. Participants whom we engaged with as part of our study rated human intelligence threats and
other risks that are not cyberthreats, especially risks related to personnel and process weaknesses on the
defender’s side, as highly feasible across all adversary capability levels (OC1 through OC5). Employees
who inadvertently share sensitive information through casual conversations, conference presentations,
or social interactions represent major risks that technical controls alone cannot address.
•
 Co
mpartmentalization is the central organizing principle for insight security. Because transforma -
tive insights are often easily shared, organizations might not be able to rely on protecting just a few
2 Sella Nevo, Dan Lahav, Ajay Karpur, Yogev Bar-On, Henry Alexander Bradley, and Jeff Alstott, Securing AI Model Weights:
Preventing Theft and Misuse of Frontier Models , RAND Corporation, RR-A2849-1, 2024.

### PDF页 7

vii
Contents
About This Report .......................................................................................................... iii
Summary ...................................................................................................................... v
CHAPTER 1
The Case for Securing Algorithmic Insights ............................................................................ 1
CHAPTER 2
Defining the Security Object .............................................................................................. 3
Defining Algorithmic Insights ........................................................................................... 4
Key Security Characteristics of Algorithmic Insights ................................................................ 5
The Strategic Importance of Securing Algorithmic Insights ........................................................ 6
CHAPTER 3
Research Approach and Expert Engagement ........................................................................... 9
Research Design and Data Collection ................................................................................... 9
Analytical Framework and Synthesis .................................................................................. 10
CHAPTER 4
How Adversaries Acquire Algorithmic Insights ...................................................................... 13
Landscape of Attack Vectors ............................................................................................ 13
Key Findings on Attack Vectors ......................................................................................... 16
CHAPTER 5
Calibrating Defenses Across Five Security Levels ..................................................................... 19
Insight Security Level 1 .................................................................................................. 19
Insight Security Level 2 .................................................................................................. 21
Insight Security Level 3 .................................................................................................. 22
Insight Security Level 4 .................................................................................................. 23
Insight Security Level 5 .................................................................................................. 25
Securing Insights Versus Securing Weights ........................................................................... 26
Notable Areas of Consensus and Disagreement ...................................................................... 27
CHAPTER 6
Implications and a Path Forward ........................................................................................ 29
APPENDIXES
A. Methods for Eliciting Expert Judgments on Securing AI Algorithmic Insights ............................. 31
B. Detailed List of Attack Vectors ........................................................................................ 37
C. Detailed Benchmark Systems for Insight Security Levels ........................................................ 53
D. Progressive Compartmentalization Across Insight Security Levels ........................................... 69
E. Detailed Examples of Algorithmic Insights ........................................................................ 75
Abbreviations ................................................................................................................ 81
References .................................................................................................................... 83
About the Authors .......................................................................................................... 89

## T1_国家研发与方向设定

- PDF页6：on’s specific threat model. • Ac hieving ISL4 or ISL5 protection requires significant organizational trade-offs and might require support from the national security community. At ISL4 or ISL5, security measures (e.g., isolated com- partmented facilities with emanation shielding, government-standard personnel vetting, supply chain compartmentalizing, restricting researcher travel and communication) are likely to reshape how orga - nizations operate. Because insights are more diffuse and easier to transport than model weights, the ten- sion between security and productivity at these ISLs is likely to be more acute than for weight security: Protecting assets that exist across people, conversations, and documents requires broader restrictions on daily work than protecting a centralized digital artifact.

- PDF页6：likely to be more acute than for weight security: Protecting assets that exist across people, conversations, and documents requires broader restrictions on daily work than protecting a centralized digital artifact. Some of these security measures might not be achievable without governmental assistance or involvement. Organizations that believe they might eventually need these levels of protection should identify and develop plans for long-lead items—which can include physical infrastructure, personnel security programs, and supply chain verification—now, even if full implementation might be years away. Implications Organizations developing frontier AI systems can use our framework to evaluate their current security pos - tures, identify gaps, and prioritize investments. At the lower ISLs, the path

- PDF页20：Securing AI Algorithmic Insights 10 Targeted Literature Scan We consulted literature from academic, commercial, and governmental sources that address AI security, algorithmic innovation, and historical cases of IP compromise. Key references included analyses of algo - rithmic efficiency improvements, case studies of major AI breakthroughs, and documented espionage and supply chain incidents. Beyond SMW, we did not use another framework to structure our analysis, which allowed us to focus specifically on protecting algorithmic insights without anchoring to prior terminology or assumptions. The literature scan informed the taxonomy of attac

- PDF页35：pproved access from easily moving data between compartments. • IS L5 security measures require the longest lead times of any ISL. The isolated, physically hardened facilities required at this level demand specialized construction, stringent accreditation processes, and potential government coordination, all of which can take years to complete. Cleared-personnel pipelines, supply chain compartmentalization across separate procurement channels, and the orga - nizational restructuring needed to eliminate cross-compartment personnel each require sustained

- PDF页39：urity-conscious organizations in defense contracting and other sensitive and regulated industries already maintain. Beyond ISL3, the trade-offs become more pronounced. The measures associated with ISL4 and ISL5, such as isolated compartmented facilities with emanation shielding, government-standard personnel vetting, supply chain compartmentalization, and restrictions on researcher travel and communication, rep - resent a fundamentally different mode of operation. Whether these trade-offs are warranted depends on the value of the specific insights an organization aims to protect and the capabilities of adversaries the organization expects to face. Organizations considering ISL4 or ISL5 protections would likely need to explore partnerships with the national security community. Several categories of s

- PDF页56：The gift concealed a passive listen- ing device that could be externally energized by RF, enabling years-long room audio collection before U.S. intelligence discovered the device in 1952. 16 • In 2004, Australian Secret Intelligence Service agents posed as aid workers renovating government o ffices in Dili, East Timor, and planted listening devices in the government’s cabinet room during oil treaty negotiations, gaining an unfair advantage in securing maritime boundary agreements worth bil - lions of dollars in resource revenues.17 Surveillance via Access to Other Devices This vector covers any surveillance that is enabled once an adversary gains access to a device that is colocated with (or logically adjacent to) insight work (the device could belong to a target organization, an employee, a vendor,

- PDF页63：zation over all possible trade-offs • emp hasize defense-in-depth; many measures overlap or partially substitute for each other, but the over- all posture becomes substantially stronger when multiple independent controls are in place. We note the relevant reference when existing government standards or authoritative guidance directly addresses a measure. These references serve two purposes: helping implementers locate detailed technical specifications and grounding our recommendations in established security frameworks. We include external references only when the cited document directly addresses the measure in question. We do not include refer- ences that are merely conceptually aligned or that address adjacent topics. Finally, as previously discussed, this appendix focuses on measures that are di

- PDF页72：t-check results are tracked over time to identify recurring issues, inform targeted training, and refine security policies. • Ne w-hire screening: Relevant roles (e.g., those working on insight-heavy research, security personnel) undergo background screenings using commercial or government services to surface potential insider threats or other risks. 31 • UEBA: U EBA techniques are used to build behavioral baselines for users, service accounts, and critical systems that interact with algorithmic insights. Significant deviations, such as new access paths into insight compartments, spikes in data access, or anomalous administrative actions will generate priori - tized alerts for an investigation and will complement traditional rule- and signature-based monitoring. Physical and Environmental Security •

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

- PDF页11：enges that differ substantively from the challenges of model weight protection. Unlike model weights, which can be isolated as discrete digital artifacts, algorithmic insights resist centralization . AI researchers’ code exists on developers’ hard drives and in documentation and collaboration tools; findings might be shared via diverse communication channels; and critical knowl - edge resides in the minds of researchers, executives, and a wide variety of other personnel. 1 Ben Buchanan, The AI Triad and What It Means for National Security Strategy , Center for Security and Emerging Technol- ogy, August 2020. 2 Sella Nevo, Dan Lahav, Ajay Karpur, Yogev Bar-On, Henry Alexander Bradley, and Jeff Alstott, Securing AI Model Weights: Preventing Theft and Misuse of Frontier Models , RAND Corporation, RR-A2849

- PDF页29：ons that align with industry best practices and impose minimal notable operational constraints. As security requirements increase, however, organizations face progressively more-difficult choices: Measures that effectively defend against sophisticated adversaries often constrain collaboration, slow development velocity, limit work flexibility, and increase operational overhead. At ISL3, these constraints become noticeable; at ISL4 and ISL5, the constraints are likely to fundamentally reshape how organizations operate. Throughout this chapter, we note when and how security measures begin to impose significant operational costs. We describe a benchmark system for each ISL, listing concrete measures and policies that represent the esti- mated minimum requirements of a system that conforms to that level’s

- PDF页36：Securing AI Algorithmic Insights 26 investment well before they become operationally necessary. Organizations that think that ISL5 might eventually be warranted should begin exploring partnerships with the national security community and initiating planning as early as possible. • Is olated, physically hardened compartmented facilities with emanation shielding and stringent access controls are fundamental architectural requirements at this level. Multiple such facilities might be required, which would be a substantial investment. • Th e personnel exclusivity requirement (i.e., no cross-compartment personnel) is particu- larly challenging with AI research because researchers often need to integrate insights

- PDF页37：lding), while experts with backgrounds in the intelligence community mostly considered these measures to be essential for protecting against nation-state adversaries. • Pr oductivity versus security trade-offs: Measures expected to result in significant costs to productiv - ity, collaboration, and organizational culture were highly controversial. The disagreement centered less on whether high-level security measures are necessary or whether they impose significant costs and more on whether the security benefits justify those costs in specific organizational contexts. Experts who emphasized the necessity of strong security did not generally dispute the high costs involved; those who emphasized the costs did not generally dispute the security need. The practical consideration is whether the value of the

- PDF页39：f operation. Whether these trade-offs are warranted depends on the value of the specific insights an organization aims to protect and the capabilities of adversaries the organization expects to face. Organizations considering ISL4 or ISL5 protections would likely need to explore partnerships with the national security community. Several categories of security measures require significant lead time and are unlikely to be quickly spun up when circumstances change. Organizations that might need to operate at ISL3 or higher within the next several years should consider preparing in at least three areas: physical infrastructure (including secure facil- ities, environmental controls, and access systems), personnel security programs (including screening pipe - lines, behavioral monitoring, and structured of

- PDF页48：MW provides extensive examples, including the Spectre and Meltdown vulnerabilities and various virtual private network (VPN)–secure sockets layer flaws. For insights security, this vector is particularly concerning because research environments often prioritize functionality and collaboration over aggres - sive patching cycles, and the broad diversity of software in ML development stacks creates numerous potential gaps. The Finding and Exploitation of Individual Zero-Days Zero-days are vulnerabilities that a vendor or the broader cybersecurity community has not yet identified. Therefore, patches do not exist, and it is harder to detect their exploitation. As documented in SMW, individual zero-days can be bought in markets for prices between $10,000 and $2.5 million depending on the platform. According

- PDF页49：schemes (phish - ing at scale), more-targeted schemes (spear phishing, whaling), and sophisticated approaches that can bypass MFA. For algorithmic insights specifically, additional considerations apply. Insight-Specific Considerations • Researchers operate in cultures that value openness and collaboration, making them potentially more s usceptible to requests that are framed as legitimate professional interest. • Co nference and academic settings create natural opportunities for targeted social engineering. • Th e complexity of AI systems means that plausible pretexts for requesting technical information are readily available. • Re mote work environments reduce informal verification methods that might catch social engineering attempts (e.g., “Did you really send me that email?”). Exploitation of E

- PDF页54：ethods (conferences, social events, professional networking) or digital channels (technical forums, social media, chat groups). This vector is particularly significant for algorithmic insights because of the following: • Th e culture of AI research emphasizes open discussion and collaboration, making researchers more receptive to technical discussions. • Re searchers might not recognize which technical details constitute protected insights versus publish - able knowledge. 10 Office of Public Affairs, “Superseding Indictment Charges Chinese National in Relation to Alleged Plan to Steal Propri - etary AI Technology,” press release, U.S. Department of Justice, February 4, 2025. 11 Center for Development of Security Excellence, Accidental Conversations: Elicitation Techniques and the Science Behind Them, j

## T5_供应链与技术依赖

- PDF页6：mprovements are achievable at every ISL. ISL1 and ISL2 align with security fundamentals and industry best practices that impose a minimal operational burden. ISL3 is more sub - stantial and introduces formal data classification, insider-threat programs, network segmentation, and supply chain assurance measures. These levels represent concrete, actionable steps that frontier AI orga- nizations can likely begin implementing today, independent of an organization’s specific threat model. • Ac hieving ISL4 or ISL5 protection requires significant organizational trade-offs and might require support from the national security community. At ISL4 or ISL5, security measures (e.g., isolated com- partmented facilities with emanation shielding, government-standard personnel vetting, supply chain compartmentalizing,

- PDF页6：g ISL4 or ISL5 protection requires significant organizational trade-offs and might require support from the national security community. At ISL4 or ISL5, security measures (e.g., isolated com- partmented facilities with emanation shielding, government-standard personnel vetting, supply chain compartmentalizing, restricting researcher travel and communication) are likely to reshape how orga - nizations operate. Because insights are more diffuse and easier to transport than model weights, the ten- sion between security and productivity at these ISLs is likely to be more acute than for weight security: Protecting assets that exist across people, conversations, and documents requires broader restrictions on daily work than protecting a centralized digital artifact. Some of these security measures might no

- PDF页6：ht not be achievable without governmental assistance or involvement. Organizations that believe they might eventually need these levels of protection should identify and develop plans for long-lead items—which can include physical infrastructure, personnel security programs, and supply chain verification—now, even if full implementation might be years away. Implications Organizations developing frontier AI systems can use our framework to evaluate their current security pos - tures, identify gaps, and prioritize investments. At the lower ISLs, the path forward is clear: Security mea - sures for ISL1 and ISL2 represent “security hygiene” that most organizations handling sensitive AI techniques could implement quickly. ISL3 adds meaningful protection against insider threats and organized cybercrime whil

- PDF页20：cademic, commercial, and governmental sources that address AI security, algorithmic innovation, and historical cases of IP compromise. Key references included analyses of algo - rithmic efficiency improvements, case studies of major AI breakthroughs, and documented espionage and supply chain incidents. Beyond SMW, we did not use another framework to structure our analysis, which allowed us to focus specifically on protecting algorithmic insights without anchoring to prior terminology or assumptions. The literature scan informed the taxonomy of attack vectors and mitigations and provided empirical validation for the experts’ assessments. In Appendix A, w e describe the methods that we used to elicit and analyze the experts’ judgments, and in subsequent appendixes, we provide detailed descriptions of th

- PDF页20：nal capacity levels are shared, but the spe - cific controls differ to reflect the distinct characteristics of each asset type. Algorithmic insights differ from model weights in their heterogeneity and exposure pathways, which necessitated deeper treatment of such disciplines as supply chain security, human intelligence (HUMINT), and physical surveillance. Algorithmic insights share some vulnerabilities with model weights, and in those cases, we carried the corresponding SMW measures into the ISL framework and adapted their application as needed. We developed new mea - sures to address any of the algorithmic insights’ distinct vulnerabilities. Defining Algorithmic Insights The targeted literature scan and expert input helped us develop a working definition and taxonomy of algo - rithmic insights. The

- PDF页25：evices in other locations • Ma licious placement of portable device implants • Di rect physical access • Re moval of devices and storage • Ev asion of physical access control systems • Ar med break-in • Mi litary takeover • Pe netration of hardware security • Shou lder surfing a Supply chain attacks • Se rvices and equipment the organization uses • Ve ndors with access to information • Fr ont operations and ruses • Co de and infrastructure incorporated into the codebase a These vectors are our new contributions that are specific to algorithmic insight security, which we identified in consultation with experts who called for defensive measures with no direct analogue in the weight security context. Several existing vectors also take on distinctive forms in the algorithmic insights context; we discuss t

- PDF页26：k vectors were assessed by experts as feasible for adversaries at all capability levels, even for the least capable adversary class (OC1). These universally exploitable vectors (e.g., exposed credentials, misconfigurations, former employee risks, social engineering, and software supply chain compromises) succeed primarily because of human and process failures on the defender’s side rather than because they require technical sophistication from the attacker’s side. This finding underscores that securing algorithmic insights requires robust baseline security practices even before addressing more-sophisticated threats. • So ftware and ML supply chain attacks represent a near-universal threat surface. Software-centric supply chain vectors (including dependency confusion and the poisoning of open-source ML

- PDF页26：n the defender’s side rather than because they require technical sophistication from the attacker’s side. This finding underscores that securing algorithmic insights requires robust baseline security practices even before addressing more-sophisticated threats. • So ftware and ML supply chain attacks represent a near-universal threat surface. Software-centric supply chain vectors (including dependency confusion and the poisoning of open-source ML compo - nents) scored highly across all capability levels, reflecting the low barrier to exploiting the open-source software ecosystem that underpins most AI development. Hardware supply chain compromise, by con- trast, was assessed as substantially more difficult to achieve for lower-capability actors (those with OC1 or OC2) because it requires physical acces

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页3：iii About This Report This report extends the framework from the RAND report Securing AI Model Weights to address the chal - lenge of protecting algorithmic insights —that is, the techniques and design know-how that drive artificial intelligence (AI) progress.1 Unlike model weights, which can be centralized and secured, insights are distrib - uted across code, documentation, communications, and human expertise, making them far harder to contain. Using expert engagements, a targeted literature review, and a gap analysis, we define five insight security levels that are aligned with five adversary operational capacities. The framework is descriptive rather than prescriptive, offering a structured way to assess what level of protection would be required to de

- PDF页3：public policy research on the most consequential challenges to civilization and global security. This work was undertaken by the division’s Center on AI, Security, and Technology (CAST), which aims to examine the opportunities and risks of rapid technological change, focusing on artificial intelligence, security, and biotechnology. For more information, contact cast@rand.org. Funding This research was independently initiated and conducted within the Center on AI, Security, and Technology using income from operations and gifts and grants from philanthropic supporters. A complete list of donors and funders is available at www.rand.org/CAST. RAND clients, donors, and grantors have no influence over research findings or recommendations. Acknowledgments We are grateful to the many individuals who contributed to this

- PDF页11：1 CHAPTER 1 The Case for Securing Algorithmic Insights As frontier artificial intelligence (AI) systems continue to demonstrate increasingly sophisticated capabili - ties, securing the key assets that enable these advancements becomes critically important. These assets rep - resent proprietary intellectual property (IP) that underpins technological leadership, and responsibly man - aging the assets’ security is essential for both competitive positioning and the broader goal of ensuring that dual-use capabilities are developed and deployed safely. Modern AI capabilities are largely a product of three key

- PDF页17：e adversary’s own infrastructure. This makes certain algorithmic insights, in some respects, more strategically valuable than any single model. Insights represent the capacity to build frontier AI, not merely to use a particular instance of it. 12 National Security Commission on Artificial Intelligence, “Emerging Threats in the AI Era,” in Final Report , 2021; White House, National Security Strategy of the United States of America , November 2025. 13 See Aixin Liu, Bei Feng, Bing Xue, Bingxuan Wang, Bochao Wu, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, et al., “DeepSeek-V3 Technical Report,” arXiv, arXiv:2412.19437v2, February 18, 2025. DeepSeek reported $5.6 million in training compute for the final production run but noted that this excluded “prior research and abla - tion experiments

- PDF页35：s Across Five Security Levels 25 screening procedures). Starting these efforts ahead of when the need arises preserves optionality even if precise timelines remain uncertain. • Fo r security-critical junctions, software assurances and general-purpose hardware should no longer be trusted. Critical security assumptions must be enforced in hardware, which could require funda - mental changes to development environments, corporate offices, and data centers. Such changes include short hardware time-to-life cycles, biometric access controls, one-time programmable media for sensi - tive data, and independent verification of the integrity of the hardware supply chain. • Ke rnel-level enforcement of compartment boundaries represents a major technical escalation specific to insight security. At this ISL,

- PDF页68：nt environments that are used to ac cess or handle insights are isolated from general web browsing through separate browser profiles, virtualized environments, or dedicated devices. Access to external sites is controlled through centrally managed allow-lists limiting exposure to trusted, necessary domains. Browser hardening that is appro - priate to an organization’s threat models has been implemented; browser hardening could include the following: disabling unnecessary extensions and plugins, enforcing content security policies, using isolated browser containers, deploying browser-specific security monitoring, or restricting JavaScript execution on untrusted external sites while allowing it for approved development tools and platforms. 21 • Clipboard and screen-capture controls: E ndpoints and

- PDF页68：els has been implemented; browser hardening could include the following: disabling unnecessary extensions and plugins, enforcing content security policies, using isolated browser containers, deploying browser-specific security monitoring, or restricting JavaScript execution on untrusted external sites while allowing it for approved development tools and platforms. 21 • Clipboard and screen-capture controls: E ndpoints and remote-access environments that are used to work with algorithmic insights are enforced by policies that limit or block screen capturing, printing, and clipboard exporting to unmanaged applications or devices; any approved exceptions are explicitly authorized and monitored. • De vice and port hardening: Endpoints that access insight systems are hardened by disabling unnec - es

- PDF页68：ary services and physical ports (e.g., unused USB, FireWire, external storage), removing default 18 Hu et al., 2014. 19 For principles related to reduced-standing privilege and context-aware access decisions, see Scott Rose, Oliver Borchert, Stu Mitchell, and Sean Connelly, Zero Trust Architecture, National Institute of Standards and Technology, U.S. Department of Commerce, NIST Special Publication 800-207, August 2020. 20 See Rose et al., 2020. 21 Cybersecurity and Infrastructure Security Agency, Capacity Enhancement Guide: Securing Web Browsers and Defending Against Malvertising for Federal Agencies , U.S. Department of Homeland Security, undated-a.

## T10_预见与优先领域

- PDF页43：on and discussion of security risks resulting from incorrect system, network, or software configurations Remote code execution Vulnerabilities or attacks enabling unauthorized parties to run code on targeted systems or infrastructure remotely Running unauthorized code Threats or scenarios in which unauthorized code (including exploits, malware, or unvalidated scripts) is executed within a protected environment Supply chain Risks and attack vectors associated with the compromise or manipulation of third-party hardware, software, or service providers in the supply chain Breaking encryption algorithms Concerns about or methods of defeating cryptographic protections to access protected data or models

- PDF页44：Securing AI Algorithmic Insights 34 Code Definition Military takeover References to low-probability, high-impact scenarios involving state or military actors overtaking or seizing physical or digital assets Misaligned AI exfiltration Scenarios in which an AI system, because of misalignment or unintended behavior, leads to the unauthorized exfiltration of data or insights Agentic-based attacks Attacks in which autonomous or agent-based systems are used, intentionally or unintentionally, to further compromise, leak, or exploit algorithmic insights Brute-forcing passwords Attacks that rely on systematically guessing passwords or cryptog

- PDF页44：l attacks via electromagnetic (EM) or other physical emanations to extract information from hardware devices HUMINT Threats and risks arising from HUMINT operations, such as social engineering, insider threats, surveillance, or coercion of personnel OC level OC1 Refers to attack scenarios or capacities associated with an OC level of 1 (e.g., amateur attempts) OC2 Refers to attack scenarios or capacities associated with an OC level of 2 (e.g., professional, opportunistic attacks) OC3 Refers to attack scenarios or capacities associated with an OC level of 3 (e.g., targeted attacks, persistent actors) OC4 Refers to attack scenarios or capacities associated with an OC level of 4 (e.g., state-supported or advanced actors) OC5 Refers to attack scenarios or capacities associated with an OC level of 5 (e.

- PDF页44：teur attempts) OC2 Refers to attack scenarios or capacities associated with an OC level of 2 (e.g., professional, opportunistic attacks) OC3 Refers to attack scenarios or capacities associated with an OC level of 3 (e.g., targeted attacks, persistent actors) OC4 Refers to attack scenarios or capacities associated with an OC level of 4 (e.g., state-supported or advanced actors) OC5 Refers to attack scenarios or capacities associated with an OC level of 5 (e.g., nation-state attacks, attacks with a large resource commitment) SLs SL1 References to or an evaluation of SL1, the baseline or minimal set of recommended security controls and benchmarks SL2 References to or evaluation of SL2, building on SL1 with increased controls and benchmarks SL3 References to or evaluation of SL3, building on SL2 with

- PDF页62：of “front” supplier or contractor entities for the purposes of gaining access and information over time. This could also occur in more-limited, one-off cases, such as conference solicitations for events run as an information-gathering exercise. For algorithmic insights, relevant scenarios include the following: • fa ke research collaborations or joint ventures designed to extract technical knowledge • fi ctitious academic institutions or researchers seeking collaboration • fr ont companies offering consulting services, supplies, investments, or acquisition discussions. Code and Infrastructure Incorporated into the Codebase Adversaries might compromise development and build infrastructure to gain access to source code, intro - duce backdoors, or extract insights from the AI-development process itse

- PDF页81：measures across all SLs. The effectiveness of compartmentalization depends not only on the specific compartment boundaries and enforcement mechanisms but also on an organization’s comprehensive implementation of security measures that are appropriate to each level. Illustrative Scenarios of Compartmentalization in Practice The following scenarios illustrate how compartmentalization operates at each ISL. Each scenario traces the same moment at a hypothetical frontier AI company (“FrontierOrg”): the training-process team has devel - oped a proprietary training recipe (a specific combination of techniques and configurations) that allows the lab to train models to a given capability level using substantially less compute than what competitors use. This recipe resides in the Training Process compartme
