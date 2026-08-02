---
institution: RAND
institution_slug: rand
institution_type: think_tank
content_type: rand_report
source_completeness: full_text
english_title: "A Structured Approach to Identifying and Characterizing AI Vulnerabilities"
chinese_title: "识别与刻画AI漏洞的结构化方法"
published_date: 2026-07-30
source_url: https://www.rand.org/pubs/research_reports/RRA4983-1.html
pdf_url: https://www.rand.org/content/dam/rand/pubs/research_reports/RRA4900/RRA4983-1/RAND_RRA4983-1.pdf
pdf_status: 200 application/pdf
external_source_url:
authors: ["Alhajjar, Elie", "Romanosky, Sasha", "Kilian, Kyle A.", "Uchill, Joe"]
keywords: ["Cybersecurity", "Artificial Intelligence"]
subjects: ["Research", "Cybersecurity", "Artificial Intelligence", "RAND-Initiated"]
topic_tags: ["AI治理", "数字经济"]
priority: P1
score: 8
translation_level: full_or_long
copyright_boundary: private_fulltext_archive
fetch_status: detail_ok
---

# A Structured Approach to Identifying and Characterizing AI Vulnerabilities

## 中文摘要与研判

### 核心观点

报告面向生成式AI系统安全，提出以系统组件和结构弱点为中心的漏洞识别框架，替代主要按攻击手法分类的传统思路。RAND认为许多AI漏洞源于训练数据、模型架构、概率学习和优化目标，具有跨版本持续、难以彻底修补的结构性特征，因此对仅靠常规软件补丁的治理方式持明确怀疑态度。研究从训练数据、分词、Transformer层到部署接口逐层分解架构，共识别31类漏洞，其中训练数据相关漏洞的总体风险最高。报告还将上下文窗口、检索增强生成管线和提示边界确定为主要暴露面，指出恶意输入和注入式上下文可操纵模型行为。其方法把威胁严重性、可利用性和组件位置结合起来，用于确定数据治理、来源验证、架构防护与持续监测的优先级。报告没有否认补丁和测试的作用，但强调部分风险只能通过补偿性控制降低，无法完全消除，这构成其与传统漏洞管理思路的主要分歧。

### 建议

RAND建议优先保护训练数据、上下文窗口和检索系统，建立数据集治理、来源追踪以及对检索内容和上下文输入的控制。工程与标准体系还应纳入组件级风险评估、利用行为检测、日志与异常监测、随机性攻击测试，并制定把AI特有弱点纳入全球漏洞目录和风险管理框架的分类标准。

## 元数据

- 原始标题：A Structured Approach to Identifying and Characterizing AI Vulnerabilities
- 发布日期：2026-07-30
- 来源链接：https://www.rand.org/pubs/research_reports/RRA4983-1.html
- PDF链接：https://www.rand.org/content/dam/rand/pubs/research_reports/RRA4900/RRA4983-1/RAND_RRA4983-1.pdf
- 关键词：Cybersecurity, Artificial Intelligence
- 主题标签：AI治理, 数字经济
- 优先级：P1

## English Source Material

RAND researchers present a structured framework for identifying and characterizing security weaknesses in generative artificial intelligence (AI) systems. They identify 31 distinct classes of AI vulnerabilities and offer practical mitigation strategies. By reframing AI security around structural weaknesses rather than adversarial techniques, this work provides a foundation for trustworthy AI deployment policy and engineering efforts. A Structured Approach to Identifying and Characterizing AI Vulnerabilities Elie Alhajjar , Sasha Romanosky , Kyle A. Kilian , Joe Uchill Research Published Jul 30, 2026 Download PDF Share on LinkedIn Share on X Share on Facebook Email In this report, RAND researchers present a structured vulnerability-centric framework for identifying and characterizing security weaknesses in generative artificial intelligence (AI) systems. Moving beyond attack taxonomies, the analysis systematically decomposes AI architectures—from training data and tokenization through transformer layers and deployment interfaces—to map where and how vulnerabilities arise. The authors identify 31 distinct classes of AI vulnerabilities, most of which differ fundamentally from traditional software flaws, often emerging from probabilistic learning dynamics, data composition, and optimization trade-offs rather than deterministic code errors. The findings demonstrate that many AI vulnerabilities are only partially patchable, requiring architectural safeguards, provenance validation, and continuous monitoring rather than conventional software updates. The authors offer practical mitigation strategies and recommend integrating AI-specific vulnerabilities into global standards to support systematic risk management. By reframing AI security around structural weaknesses rather than adversarial techniques, this work provides a foundation for future policy and engineering efforts aimed at trustworthy AI deployment. Key Takeaways Many of the vulnerabilities in generative AI systems arise from fundamental properties of data, model architecture, and optimization objectives. Like certain architectural weaknesses in traditional computing systems, these vulnerabilities can persist across model versions and deployments and may be difficult to fully eliminate. However, unlike many conventional software vulnerabilities, AI vulnerabilities often emerge from statistical learning processes and model behavior rather than discrete implementation errors, making them more difficult to characterize, detect, and remediate. Among the AI system components examined, vulnerabilities associated with training data present the greatest overall risk. Poisoned or unverified training data can embed persistent weaknesses during model development that propagate across deployments and influence downstream behavior over time. User-facing inference interfaces represent major points of exposure. Components such as the context window, retrieval-augmented generation pipelines, and prompt boundaries provide opportunities for adversaries to manipulate model behavior through carefully crafted inputs or injected contextual information. Recommendations Prioritize security controls at the data layers. Security efforts should prioritize training data, context windows, and retrieval systems, in which the highest-threat vulnerabilities are concentrated. Strong dataset governance, provenance tracking, and controls on contextual and retrieved inputs are critical. Treat certain AI vulnerabilities as structural risks rather than patchable bugs. Because several weaknesses arise from inherent properties of machine learning systems rather than discrete implementation flaws, they often cannot be fully eliminated through conventional patching. Instead, risk must be managed through architectural safeguards, operational constraints, monitoring, and other compensating controls, which may reduce but not entirely remove the underlying vulnerability. Incorporate component-level risk assessments into AI system design. Evaluating vulnerabilities at the architectural component level helps identify where risks cluster and allows engineering teams to prioritize mitigations during system development. Develop advanced exploitation detection and monitoring capabilities for AI systems. Many exploitation pathways are difficult to detect with existing tools, making improved logging, anomaly detection, and behavioral monitoring essential for identifying adversarial activity. Develop evaluation methods that reflect stochastic exploitation. Security testing should incorporate stochastic simulations, adversarial prompting, and large-scale behavioral assessments to better capture how vulnerabilities may manifest under variable conditions. Establish criteria for cataloging AI vulnerabilities. While existing initiatives provide valuable frameworks for documenting adversarial behaviors, clear standards are needed to determine how AI-specific weaknesses should be classified and integrated into existing vulnerability management frameworks. Subscribe to the Policy Currents newsletter Topics Artificial Intelligence Cybersecurity Document Details Copyright: RAND Corporation Availability: Web-Only Year: 2026 Pages: 78 DOI: https://doi.org/10.7249/RRA4983-1 Document Number: RR-A4983-1 Citation RAND Style Manual Alhajjar, Elie, Sasha Romanosky, Kyle A. Kilian, and Joe Uchill, A Structured Approach to Identifying and Characterizing AI Vulnerabilities, RAND Corporation, RR-A4983-1, 2026. As of July 30, 2026: https://www.rand.org/pubs/research_reports/RRA4983-1.html Copy Text Chicago Manual of Style Alhajjar, Elie, Sasha Romanosky, Kyle A. Kilian, and Joe Uchill, A Structured Approach to Identifying and Characterizing AI Vulnerabilities. Santa Monica, CA: RAND Corporation, 2026. https://www.rand.org/pubs/research_reports/RRA4983-1.html. Copy Text BibTeX RIS Research conducted by RAND Global and Emerging Risks This research was independently initiated and conducted by the Center on AI, Security, and Technology within RAND Global and Emerging Risks using income from operations and gifts and grants from philanthropic supporters. This publication is part of the RAND research report series. Research reports present research findings and objective analysis that address the challenges facing the public and private sectors. All RAND research reports undergo rigorous peer review to ensure high standards for research quality and objectivity. This document and trademark(s) contained herein are protected by law. This representation of RAND intellectual property is provided for noncommercial use only. Unauthorized posting of this publication online is prohibited; linking directly to this product page is encouraged. Permission is required from RAND to reproduce, or reuse in another form, any of its research documents for commercial purposes. For information on reprint and reuse permissions, please visit www.rand.org/pubs/permissions . RAND is a nonprofit institution that helps improve policy and decisionmaking through research and analysis. RAND's publications do not necessarily reflect the opinions of its research clients and sponsors.
