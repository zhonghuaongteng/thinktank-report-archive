# L-0EB658CE1E 原文切片

- 原文：`03_证据底稿\原文PDF\L-0EB658CE1E.pdf`
- PDF页数：78
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 5

v
Summary
In this report, we present a vulnerability-centric framework for analyzing the security of generative
artificial intelligence (AI) systems. We systematically map where and how weaknesses arise within the
architecture of large models, from training data and tokenization to transformer layers and
deployment interfaces. Using structured threat and impact metrics, we characterize risk and reveal
that the greatest vulnerabilities occur during data ingestion and at user interaction boundaries.
Specifically, we address the following research questions:
• What are the vulnerability types in AI systems?
• What are the features of those vulnerabilities that would increase the probability of
exploitation, the magnitude of impact to the AI system, and therefore the overall risk to the AI
system?
• What practical mitigations could be applied to reduce the risk of malicious exploitation of
these vulnerabilities?
Key Findings
Several key findings emerged from our analysis:
• First, many of the vulnerabilities in generative AI systems arise from fundamental properties
of data, model architecture, and optimization objectives. Like certain architectural weaknesses
in traditional computing systems, these vulnerabilities can persist across model versions and
deployments and may be difficult to fully eliminate. However, unlike many conventional
software vulnerabilities, AI vulnerabilities often emerge from statistical learning processes and
model behavior rather than discrete implementation errors, making them more difficult to
characterize, detect, and remediate.
• Second, among the AI system components examined, vulnerabilities associated with training
data present the greatest overall risk. Poisoned or unverified training data can embed
persistent weaknesses during model development that propagate across deployments and
influence downstream behavior over time.
• Third, user-facing inference interfaces represent major points of exposure. Components such
as the context window, retrieval-augmented generation pipelines, and prompt boundaries
provide opportunities for adversaries to manipulate model behavior through carefully crafted
inputs or injected contextual information.
These findings suggest that traditional software security approaches, particularly patch-and-fix
remediation models, are insufficient for addressing many AI vulnerabilities. Because many weaknesses
arise from stochastic model behavior or architectural design, mitigating risk requires a deeper

### PDF页 8

viii
Contents
About This Report ........................................................................................................................................................... iii
Summary .............................................................................................................................................................................. v
Figures and Tables .............................................................................................................................................................. x
CHAPTER 1 ........................................................................................................................................................................................ 1
Introduction ....................................................................................................................................................................... 1
CHAPTER 2 ........................................................................................................................................................................................ 4
Research Approach ........................................................................................................................................................... 4
Methodology ................................................................................................................................................................. 4
Limitations .................................................................................................................................................................... 6
CHAPTER 3 ........................................................................................................................................................................................ 8
Attacks Against AI Systems ............................................................................................................................................. 8
Evasion ........................................................................................................................................................................... 8
Extraction ...................................................................................................................................................................... 8
Poisoning ....................................................................................................................................................................... 9
Misalignment ................................................................................................................................................................ 9
Efficiency ........................................................................................................................................................................ 9
CHAPTER 4 ...................................................................................................................................................................................... 11
Enumerating AI Vulnerabilities .................................................................................................................................... 11
Schematic of the AI System ...................................................................................................................................... 11
AI Vulnerabilities ....................................................................................................................................................... 12
CHAPTER 5 ...................................................................................................................................................................................... 15
Characterizing the Risk of AI Vulnerabilities ............................................................................................................. 15
Threat .......................................................................................................................................................................... 16
Impact .......................................................................................................................................................................... 18
Risk ............................................................................................................................................................................... 20
CHAPTER 6 ...................................................................................................................................................................................... 25
Mitigations for AI Vulnerabilities ................................................................................................................................. 25
Training and Fine-Tuning Data Mitigations .......................................................................................................... 25
Tokenizer and Embedding Mitigations ................................................................................................................... 26
Transformer Mitigations ........................................................................................................................................... 26
Reward Function Mitigations ................................................................................................................................... 27
Context Window and RAG Mitigations ................................................................................................................. 27
CHAPTER 7 ...................................................................................................................................................................................... 29
Recommendations ...................................................................................................

## T1_国家研发与方向设定

- PDF页11：1 Chapter 1 Introduction The pace of development in artificial intelligence (AI) capabilities, coupled with the rapid adoption of these systems across consumer, enterprise, and government applications, has been unprecedented. Large language models (LLMs) and other generative AI systems are now widely integrated into search engines, productivity software, coding tools, customer support platforms, and scientific research workflows. This rapid diffusion of AI technologies has been accompanied by significant optimism regarding their potential economic and societal benefits. However, the speed of deployment has also outpaced our collective understanding of the risks that these systems introduce and the

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

未自动命中；需人工按目录复核。

## T5_供应链与技术依赖

- PDF页15：ng AI tools but rather just vulnerabilities in AI systems. In our analysis of threats and impacts, we considered direct impacts to the AI model and did not include indirect impacts to external systems. Consequently, we did not examine vulnerabilities in computing, networking, or supply chain components. We need to highlight two important notes. First, this list represents vulnerability types, or classes of vulnerabilities, not specific vulnerabilities in specific AI systems. Just as the CWE schema defines classes of regular software vulnerabilities (with CVEs being specific instantiations of a vulnerability class in a specific product version), the AI vulnerability types we discuss in this report are types or classes. With a working list of vulnerability types, we next sought to characterize the featu

- PDF页17：qually defensible depending on analytical objectives. Additionally, the analysis is limited to vulnerabilities that arise from the architecture and operation of AI systems themselves. It does not address risks originating from external factors, such as supporting infrastructure, supply chains, hardware platforms, organizational processes, or broader governance failures. Consequently, the risk landscape presented here reflects only the subset of risks that are intrinsic to AI system components and their interactions. Despite these limitations, the vulnerability-centric approach presented in this report produces a structured framework for analyzing AI vulnerabilities by linking architectural components, vulnerability classes, risk characteristics, and mitigation strategies within a common analytical str

- PDF页26：API). This metric can distinguish between high-barrier attacks (e.g., gradient- based model inversion) and low-barrier exploits (e.g., basic prompt injection). • Exploitability. Exploitability approximates the engineering sophistication needed to elicit failure modes (including dependence on specialized prompting, data placement, trial and error, or model-specific variations). While some flaws can be exploited with simple natural language (e.g., direct prompt injection), others require a deep understanding of tokenization irregularities or the ability to craft sophisticated adversarial perturbations in the embedding space. Higher exploitability scores indicate that the vulnerability’s characteristics lower the

- PDF页31：lnerabilities at inference interfaces, such as the context window or retrieval systems, tend to dominate the practical threat landscape, whereas vulnerabilities in internal components (e.g., tokenizer, embedding, transformer weights) are primarily relevant in scenarios involving supply chain compromise or privileged access. With the exception of two components, the accessibility and exploitability scores are nearly identical, suggesting that many successful attacks on generative AI systems arise from the presence of externally accessible interfaces that allow adversaries to interact with vulnerable components. A second notable finding is that vulnerabilities associated with approximately half of the system components score medium on patchability, meaning that remediation would generally require retrai

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页3：iii About This Report In this report, we present a vulnerability-centric framework for analyzing the security of generative artificial intelligence (AI) systems. Moving beyond lists of attacks or incidents, we systematically map where and how weaknesses arise within the architecture of large models: from training data and tokenization to transformer layers and deployment interfaces. We identify 31 classes of AI vulnerabilities, most of which differ from traditional software flaws, often emerging from probabilistic learning dynamics and optimization trade-offs rather than deterministic code errors. Using structured threat and impact metrics, we characterize ri

- PDF页3：nce validation, architectural safeguards, and continuous monitoring. By reframing AI security around structural weaknesses rather than adversarial techniques, we offer a foundation for integrating AI-specific vulnerabilities into global standards and for shaping future policy on trustworthy AI deployment. Center on AI, Security, and Technology RAND Global and Emerging Risks is a division of RAND that delivers rigorous and objective public policy research on the most consequential challenges to civilization and global security. This work was undertaken by the division’s Center on AI, Security, and Technology, which aims to examine the opportunities and risks of rapid technological change, focusing on artificial intelligence, security, and biotechnology. For more information, contact cast@rand.or

- PDF页3：ective public policy research on the most consequential challenges to civilization and global security. This work was undertaken by the division’s Center on AI, Security, and Technology, which aims to examine the opportunities and risks of rapid technological change, focusing on artificial intelligence, security, and biotechnology. For more information, contact cast@rand.org. Funding This research was independently initiated and conducted within the Center on AI, Security, and Technology using income from operations and gifts and grants from philanthropic supporters. A complete list of donors and funders is available at www.rand.org/CAST. RAND clients, donors, and grantors have no influence over research findings or recommendations. Acknowledgments We would like to acknowledge colleagues who reviewed this report

- PDF页4：iv organizers of the Institute for Trustworthy AI in Law and Society (TRAILS) conference (TRAILSCon) at George Washington University.

- PDF页5：v Summary In this report, we present a vulnerability-centric framework for analyzing the security of generative artificial intelligence (AI) systems. We systematically map where and how weaknesses arise within the architecture of large models, from training data and tokenization to transformer layers and deployment interfaces. Using structured threat and impact metrics, we characterize risk and reveal that the greatest vulnerabilities occur during data ingestion and at user interaction boundaries. Specifically, we address the following research questions: • What are the vulnerability types in AI systems? • What are the features of those vulnerabil

- PDF页11：1 Chapter 1 Introduction The pace of development in artificial intelligence (AI) capabilities, coupled with the rapid adoption of these systems across consumer, enterprise, and government applications, has been unprecedented. Large language models (LLMs) and other generative AI systems are now widely integrated into search engines, productivity software, coding tools, customer support platforms, and scientific research workflows. This rapid diffusion of AI technologies has been accompanied by significant optimism regarding their potential economic and societal benefits. However, the speed

- PDF页24：rge from stakeholder intent. Context Window and RAG Vulnerabilities Finally, vulnerabilities emerge at the system boundary. These include lack of segmentation between system and user prompts, context overflow susceptibility, absence of provenance checks on contextual input, weak trust boundaries in RAG systems, and insufficient transparency regarding retrieved content (Lin and Mohaisen, 2024). These weaknesses are often exploited through evasion or manipulation techniques but are fundamentally architectural in nature. They arise from the lack of architectural separation between instructions and data.

- PDF页28：sing more standard cybersecurity measures. Indeed, our impact metrics intentionally borrow the familiar confidentiality, integrity, and availability (CIA) triad from conventional vulnerability scoring—e.g., the disclosure of sensitive user data (confidentiality), corruption or untrusted modification of outputs and downstream decisions (integrity), and disruption or degradation of service through resource exhaustion or denial- of-service behaviors (availability). Where our approach departs from the CIA triad is by explicitly adding scope, because of its usefulness given that generative AI vulnerabilities can facilitate the propagation of exploits across boundaries, and detectability (Cohen, Bitton, and Nassi, 2025). The impact metrics are detailed in Table 5.3. They are not intended to be fully

## T10_预见与优先领域

- PDF页28：that would affect the severity of impact of exploitation to the AI model. We recognize that there may well be variation in impact from the successful exploitation of different vulnerabilities in a class, so when considering impact, we sought to capture the most likely worst-case scenario in the event the vulnerability was exploited. Characterizing impact in foundation models is inherently more difficult than in classical computing (Kapoor et al., 2024), given the evolving internal states of neural networks and the expanding ecosystem of interconnected systems. AI failure modes stem from novel vulnerability classes, such as semantic sensitivity or behavioral drift, rather than a binary system crash (Huang et al., 2025; Li, Kreuzwieser, and Peters, 2025; Rando et al., 2025; Yu et al., 2026). However

- PDF页31：ons. As a result, vulnerabilities at inference interfaces, such as the context window or retrieval systems, tend to dominate the practical threat landscape, whereas vulnerabilities in internal components (e.g., tokenizer, embedding, transformer weights) are primarily relevant in scenarios involving supply chain compromise or privileged access. With the exception of two components, the accessibility and exploitability scores are nearly identical, suggesting that many successful attacks on generative AI systems arise from the presence of externally accessible interfaces that allow adversaries to interact with vulnerable components. A second notable finding is that vulnerabilities associated with approximately half of the system components score medium on patchability, meaning that remediation would

- PDF页35：yali et al., 2024). Because data are foundational to model behavior, these mitigations operate upstream and shape the statistical properties of the learned system itself. In terms of effectiveness, data-level controls meaningfully reduce exploitability for poisoning and backdoor scenarios by increasing attacker effort and decreasing deterministic trigger reliability. They also materially reduce confidentiality risk, where memorization stems from identifiable data artifacts. However, they do not eliminate emergent correlations, distributional blind spots, or hallucination behaviors that arise from generalization dynamics rather than explicit data flaws (Pal et al., 2024). Feasibility is uneven. Deduplication and personally identifiable information filtering are mature and widely deployable. In cont
