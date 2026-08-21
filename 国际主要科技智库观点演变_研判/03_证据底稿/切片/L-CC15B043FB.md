# L-CC15B043FB 原文切片

- 原文：`03_证据底稿\原文PDF\L-CC15B043FB.pdf`
- PDF页数：47
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 3

ii
© Royal United Services Institute
Contents
iv Disclaimer
vi Key Terms and Concepts
vii Acknowledgements
1 Executive Summary
1 Core Contributions
3 Introduction
3 Creating a Shared Understanding of
How to Secure Access to Frontier AI
4 The Multistakeholder Landscape of Frontier AI Evaluations
6 The Challenge: Managing Access and Security Risks
8 Strengthening Assessments: Why Third-Party Access Matters
8 What Do Third-Party Evaluators Do?
9 The Importance of Access
13 Associated Threats
14 Security Risk Categories
19 Operationalising the Security Risks Taxonomy for Third-Party Access
22 The Access–Risk Matrix
22 Methodology Note
29 Key Patterns
30 Security Controls to Strengthen Access

### PDF页 9

1
© Royal United Services Institute
Executive Summary
A
s frontier AI models expand in their capability and application, their evolution
 must remain grounded in safety and security safeguards.
Third-party evaluation of frontier AI models is increasingly recognised as essential to
supporting their safety and security by developers, governments and regulators alike.
Yet, enabling meaningful external evaluation requires granting access to some of the
most sensitive intellectual property in the tech/AI sector. The security risks associated
with this access – from intellectual property (IP) leakage to model compromise to
exploitation by state-sponsored actors – remain poorly mapped and inadequately
standardised. This gap stifles the evaluation ecosystem, making it one where developers
restrict access out of security concerns, while evaluators lack the information they need
to conduct effective assessments.
Drawing on the work of the SAFA-TF, this paper proposes a shared framework for
understanding and managing these risks. The aim is to move the conversation beyond
the current tension between openness and security, or security and innovation,
towards a practical, shared understanding of how to enable secure and effective third-
party evaluation at scale.
Core Contributions
1. This paper develops a threat taxonomy of seven security risk categories specific to
the context of third-party evaluation: Model Theft, Capability Reconstruction, Model
Manipulation, Jailbreak/Safety Bypass, Accidental Exposure, Credential
Compromise and Access Persistence, with Weaponisation as a potential resultant
outcome. Each category is defined, illustrated with real-world examples and
research evidence, and situated within a risk hierarchy organised by access depth
and actor sophistication.
2. The paper proposes an Access–Risk Matrix that maps six types of evaluator access
ranging from query-level inference to model internals, training data, evaluation data
and compute infrastructure, against each risk category. The matrix assigns
indicative severity ratings for each access-related risk, thus providing a structured
basis for identifying the best-suited security mitigations based on the threat model.

## T1_国家研发与方向设定

- PDF页6：erts. Overall, the paper reflects engagement with 39 experts. Held virtually from October to December 2025, the workshops brought together leading international AI engineers, evaluators, red teamers, cybersecurity specialists and policy and governance experts from civil society, government and the private sector (including frontier labs). The workshops were divided into three themes: conceptualising third-party evaluation risk, charting evaluation and access-type risks, and identifying pathways towards mitigating risk. The Access–Risk Matrix and the mitigation strategies outlined in this paper were developed throughout the course of the workshops, and through requests for input on earlier versions of both in between the sessions. In January and February 2026, SAFA-TF participants and additional subj

- PDF页6：paper and workshops do not centre on specific evaluation methodologies, but rather on the broader ecosystem in which the range of tests is conducted. The evaluation and access types considered are strictly by third-party evaluation companies or independent researchers and not by government regulators or law enforcement. The authors acknowledge that the risks, severity levels and controls are not exhaustive. The existing gap between risks that have been publicly identified and potential risks is also worth bearing in mind, as it means the Access–Risk Matrix is a living, evolving contribution to the debate. Moreover, as identified during the discussions, the authors believe (and highlight in the final chapter) that further dialogues and collaboration between evaluators and cybersecurity researchers ar

- PDF页9：A s frontier AI models expand in their capability and application, their evolution must remain grounded in safety and security safeguards. Third-party evaluation of frontier AI models is increasingly recognised as essential to supporting their safety and security by developers, governments and regulators alike. Yet, enabling meaningful external evaluation requires granting access to some of the most sensitive intellectual property in the tech/AI sector. The security risks associated with this access – from intellectual property (IP) leakage to model compromise to exploitation by state-sponsored actors – remain poorly mapped and inadequately standardised. This gap stifles the evaluation ecosystem, making it one where developers restrict access out of security concerns, while evaluators lack the info

- PDF页13：rnal processes: A confirming the soundness of developer-led evaluations; A applying independent methods to test the robustness and safety claims of developer- conducted evaluations; A supplementing internal capabilities and capacity of developers to perform internal assessments. Governments have also responded by creating AI safety and security institutes and a network of such organisations with the aim of facilitating AI safety and security evaluations.12 The UK’s AI Security Institute (AISI) assessed 30 models over a period of two years (2023–25) across several security-critical domains.13 The US Center for AI Standards and Innovation conducted pre-deployment evaluations and established voluntary testing agreements with frontier developers. In 2025, their mandate was refocused on national security

- PDF页13：would, among other things, lead evaluations and assessments ‘of potential security vulnerabilities and malign foreign influence arising from use of adversaries’ AI systems, including the possibility of backdoors and other covert, malicious behavior’.14 Regulatory frameworks and governmental policy papers have only begun to attempt to codify these expectations, to varying degrees of detail and success. The Bletchley Summit declaration in 2023 acknowledged that evaluations and assessments of the capabilities and risks of AI systems (such as model evaluations and/or red teaming) should be key components of AI governance regimes.15 But beyond aspiration and the AISI network, such national or third-party metrics and methodologies for evaluations are socialised but not always shared among stakeholders. E

- PDF页15：certain forms of access. The absence of a shared framework has practical consequences for both evaluators and developers and, most importantly, highlights the need for a collective effort to map risks linked to access with the aim of devising shared mitigation strategies. The UK government’s ‘Roadmap to Trusted Third-Party AI Assurance’ paper, published in September 2025, notes that evaluators ‘struggle to access the information they need to conduct effective assurance of AI systems’ due to a range of challenges: concerns about sharing commercially sensitive information, security and privacy risks deriving from access; and lack of established practices from AI labs to make information accessible to evaluators.21 The EU’s AI Act acknowledges that the third-party evaluation ecosystem is still maturing

- PDF页15：g AI Companies’, arXiv preprint arXiv:2601.11699, 16 January 2026, <https://arxiv.org/abs/2601.11699>, accessed 5 February 2026. 21. Department for Science, Innovation and Technology, ‘Trusted Third-Party AI Assurance Roadmap’, policy paper, 3 September 2025, <https://www.gov.uk/government/publications/trusted-third-party-ai-assurance- roadmap/trusted-third-party-ai-assurance-roadmap>, accessed 5 February 2026. 22. EU AI Act, 12 July 2024, < https://artificialintelligenceact.eu/>, accessed 6 May 2026. 23. Shayne Longpre et al., ‘Position: A Safe Harbor for AI Evaluation and Red Teaming’, in Proceedings of the 41st International Conference on Machine Learning (ICML’24) (PMLR, 2024, Vol. 235). 24. Edward Kembery, Ben Bucknall and Morgan Simpson, ‘Position Paper: Model Access Should be a Key Concern in

- PDF页18：systems represents a significant vulnerability to the AI assurance ecosystem.38 29. Kembery, Bucknall and Simpson, ‘Position Paper’. 30. Department for Science, Innovation and Technology (DSIT), ‘AI Safety Institute Approach to Evaluations’, 9 February 2024, <https://www.gov.uk/government/publications/ai-safety-institute-approach-to- evaluations/ai-safety-institute-approach-to-evaluations>, accessed 2 February 2026. 31. Irregular, ‘Evaluating GPT-5.2 Thinking: Cryptographic Challenge Case Study’, 11 December 2025, <https://www.irregular.com/publications/spell-bound-technical-case-study>, accessed 20 February 2026. 32. Schoen et al., ‘Stress Testing Deliberative Alignment for Anti-Scheming Training’. 33. Alexander Meinke et al., ‘Frontier Models are Capable of In-context Scheming’, arXiv preprint ar

## T2_市场与产业政策边界

- PDF页6：paper reflects engagement with 39 experts. Held virtually from October to December 2025, the workshops brought together leading international AI engineers, evaluators, red teamers, cybersecurity specialists and policy and governance experts from civil society, government and the private sector (including frontier labs). The workshops were divided into three themes: conceptualising third-party evaluation risk, charting evaluation and access-type risks, and identifying pathways towards mitigating risk. The Access–Risk Matrix and the mitigation strategies outlined in this paper were developed throughout the course of the workshops, and through requests for input on earlier versions of both in between the sessions. In January and February 2026, SAFA-TF participants and additional subject-matter experts peer

## T4_国际合作与开放

- PDF页6：identified and potential risks is also worth bearing in mind, as it means the Access–Risk Matrix is a living, evolving contribution to the debate. Moreover, as identified during the discussions, the authors believe (and highlight in the final chapter) that further dialogues and collaboration between evaluators and cybersecurity researchers are needed to ensure benchmarking methodologies are ever more attuned to the changing threat landscape and the tactics, techniques and procedures of adversaries. Note that an AI language model was used to support early literature review and proofreading, and provided suggestions on how to illustrate the data collected for the ‘Exploitation Pathways’ section, the Access–Risk Matrix in an image and table, and in the development of the Key Terms and Concepts in a langu

- PDF页9：ncerns, while evaluators lack the information they need to conduct effective assessments. Drawing on the work of the SAFA-TF, this paper proposes a shared framework for understanding and managing these risks. The aim is to move the conversation beyond the current tension between openness and security, or security and innovation, towards a practical, shared understanding of how to enable secure and effective third- party evaluation at scale. Core Contributions 1. This paper develops a threat taxonomy of seven security risk categories specific to the context of third-party evaluation: Model Theft, Capability Reconstruction, Model Manipulation, Jailbreak/Safety Bypass, Accidental Exposure, Credential Compromise and Access Persistence, with Weaponisation as a potential resultant outcome. Each category

- PDF页42：nd more standardised access frameworks, which can then be tailored to the various access requirements while ensuring an adequate security and safety baseline. Facilitating the development of standardised and recognised secure access frameworks requires maintaining and supporting partnership forums dedicated to supporting secure access. To ensure balanced perspectives and potential sponsor or evaluation- specific requirements, all initiatives should encompass representatives from across the AI developers, deployers and evaluators from the assurance sector. Though not due to regulatory requirements at present, conveners should consider including regulators and government governance specialists in relevant discussions. Fortunately, a range of forums exist, encompassing evaluation-specific organisations

- PDF页46：Communications. She has an MSc in Media and Communications (Data and Society) from the LSE and a BA in International Relations from the Pontifical Catholic University of Rio de Janeiro. She is an advisory board member of the Global Forum of Cyber Expertise, Carnegie Endowment’s Partnership for Countering Influence Operations’ and the Centre for Information Resilience. Elijah Glantz is a Research Fellow in the Organised Crime and Policing research group (OCP) at RUSI. His research at RUSI focuses on criminal networks structures, illicit finance and law enforcement responses around the world. Specific projects include illicit finance and law enforcement capacity in sub-Saharan Africa, state involvement in organised crime and narcotics, and trends in UK organised acquisitive crime. He is the Co-Project

## T5_供应链与技术依赖

- PDF页12：6, <https://internationalaisafetyreport. org/publication/international-ai-safety-report-2026>, accessed 15 February 2026. 3. Google, ‘Secure AI Framework (SAIF)’, <https://safety.google/intl/en_ca/safety/saif/>, accessed 10 January 2026. 4. Open AI, ‘Open AI, Strengthening Cyber Resilience as AI Capabilities Advance’, 10 December 2025, <https://openai.com/index/strengthening-cyber-resilience>, accessed 16 April 2026. 5. Nicholas Carlini et al., ‘Evaluating and Mitigating the Growing Risk of LLM-Discovered 0-Days’, Red Anthropic, 5 February 2026, <https://red.anthropic.com/2026/zero-days/>, accessed 6 February 2026. 6. Google DeepMind, ‘Evals: Explore our Comprehensive Evaluations Across AI Capabilities’, <https://deepmind.google/research/evals/>, accessed 2 February 2026. 7. Bronson Schoen et al., ‘

- PDF页46：rom the LSE and a BA in International Relations from the Pontifical Catholic University of Rio de Janeiro. She is an advisory board member of the Global Forum of Cyber Expertise, Carnegie Endowment’s Partnership for Countering Influence Operations’ and the Centre for Information Resilience. Elijah Glantz is a Research Fellow in the Organised Crime and Policing research group (OCP) at RUSI. His research at RUSI focuses on criminal networks structures, illicit finance and law enforcement responses around the world. Specific projects include illicit finance and law enforcement capacity in sub-Saharan Africa, state involvement in organised crime and narcotics, and trends in UK organised acquisitive crime. He is the Co-Project Manager and Lead Editor for the Strategic Hub for Organised Crime Research (SH

- PDF页47：ing independent, practical and innovative analysis to address today’s complex challenges. Since its foundation in 1831, RUSI has relied on its members to support its activities. Together with revenue from research, publications and conferences, RUSI has sustained its political independence for 195 years. © The Royal United Services Institue for Defence and Security Studies RUSI is registered as a charity in England and Wales Charity number: 210639 VAT number: GB752275038

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页2：or unforeseeable (including, without limitation, in defamation) arising from or in connection with the reproduction, reliance on or use of the publication or any of the information contained in the publication by you or any third party. References to RUSI include its directors, trustees and employees. © 2026 The Royal United Services Institute for Defence and Security Studies This work is licensed under a Creative Commons Attribution – Non- Commercial – No-Derivatives 4.0 International Licence. For more information, see <http://creativecommons.org/licenses/by-nc- nd/4.0/>. RUSI Research Papers, May 2026 ISSN 2977-960X Get in touch www.rusi.org enquiries@rusi.org +44 (0)207 747 2600 The Royal United Services Institute for Defence and Security 61 Whitehall, London SW1A 2ET United Kingdom Publica

- PDF页15：The absence of a shared framework has practical consequences for both evaluators and developers and, most importantly, highlights the need for a collective effort to map risks linked to access with the aim of devising shared mitigation strategies. The UK government’s ‘Roadmap to Trusted Third-Party AI Assurance’ paper, published in September 2025, notes that evaluators ‘struggle to access the information they need to conduct effective assurance of AI systems’ due to a range of challenges: concerns about sharing commercially sensitive information, security and privacy risks deriving from access; and lack of established practices from AI labs to make information accessible to evaluators.21 The EU’s AI Act acknowledges that the third-party evaluation ecosystem is still maturing, recognising the ne

- PDF页15：AI Auditing: Toward Rigorous Third-Party Assessment of Safety and Security Practices at Leading AI Companies’, arXiv preprint arXiv:2601.11699, 16 January 2026, <https://arxiv.org/abs/2601.11699>, accessed 5 February 2026. 21. Department for Science, Innovation and Technology, ‘Trusted Third-Party AI Assurance Roadmap’, policy paper, 3 September 2025, <https://www.gov.uk/government/publications/trusted-third-party-ai-assurance- roadmap/trusted-third-party-ai-assurance-roadmap>, accessed 5 February 2026. 22. EU AI Act, 12 July 2024, < https://artificialintelligenceact.eu/>, accessed 6 May 2026. 23. Shayne Longpre et al., ‘Position: A Safe Harbor for AI Evaluation and Red Teaming’, in Proceedings of the 41st International Conference on Machine Learning (ICML’24) (PMLR, 2024, Vol. 235). 24. Edwar

- PDF页15：ion Paper: Model Access Should be a Key Concern in AI Governance’, arXiv preprint arXiv:2412.00836, 1 December 2024, <https://arxiv.org/ abs/2412.00836>, accessed 5 February 2026. 25. Kevin Klyman et al., ‘Safeguarding Third-Party AI Research’, Stanford University Human-Centered Artificial Intelligence, February 2025, <https://hai.stanford.edu/assets/files/hai-policy-brief-safeguarding- third-party-ai-research.pdf>, accessed 5 February 2026.

- PDF页18：I Governance’, arXiv preprint arXiv:2412.00836, 1 December 2024, <https://arxiv.org/abs/2412.00836>, accessed 13 April 2026. 38. Inioluwa Deborah Raji et al., ‘Outsider Oversight: Designing a Third Party Audit Ecosystem for AI Governance’, presented at the 5th Annual ACM/AAAI AI Ethics and Society (AIES) Conference, August 2022, <https://arxiv.org/abs/2206.04737>, accessed 13 April 2026.

- PDF页20：Developing a Framework for Secure Third-Party Access to Frontier AI Louise Marie Hurel, Elijah Glantz and Daniel Cuthbert 12 © Royal United Services Institute skew, the authors argue that white-box and out-of-the-box access may be required to conduct rigorous and trustworthy external assessments. This expanded access includes models’ white box, inclusive of more discrete features such as model architecture, decision tree logic, training processes and safety and control filters. Each progression in access level enables more rigorous evaluation but carries greater security risk – a trade-off that the Access–Risk Matrix in the fourth chapter addresses directly. Table 1: Types of Access Required to Conduct Evaluations Access Type Description Required/Relevant Data Points Access Leve

- PDF页25：wing them to escalate privileges). A Primary Threat Actors: State-sponsored or criminal groups/actors. A Examples: In August 2025, Google’s Threat Intelligence Group reported threat actors had successfully stolen ‘OAuth’ and refresh tokens used by Salesloft’s Drift AI Chatbot, a trusted third-party application integrated into Salesforce customer- specific environments.54 These tokens served as credentials by which the threat actors were able to gain unauthorised access to private company data via the AI chatbot, and exfiltrate ‘large volumes’ of Salesforce customer data. According to Salesloft, the attackers’ objective was credentials, ‘focusing on sensitive information like AWS access keys, passwords and Snowflake-related access tokens’. 55 54. Austin Larsen et al., ‘Widespread Data Theft Targ

- PDF页39：ss to Frontier AI Louise Marie Hurel, Elijah Glantz and Daniel Cuthbert 31 © Royal United Services Institute Table 4: Security Mitigation Actions for Third-Party Access Technical Controls Procedural Controls Contractual Controls Model Theft Output watermarking; security enclaves/Trusted Execution Environments (TEEs) for weight access; confidential inference systems; no-export environments Evaluation-scoped access; session logging and review; evaluators should have policies for secure storage, transit and retention of completions/transcripts; limiting API access; security screening of personnel IP protection clauses; data destruction requirements RESPONSIBILITY: D RESPONSIBILITY: J RESPONSIBILITY: J Capability Reconstruction Compartmentalised architecture; differential privacy for data; scoped A

## T10_预见与优先领域

未自动命中；需人工按目录复核。
