---
institution: RAND
institution_slug: rand
institution_type: think_tank
source_group: core_technology
content_type: rand_report
source_completeness: full_text
english_title: "Secure Inference Data Centers: A Vertically Integrated Strategy for Security Engineering"
chinese_title: "安全推理数据中心的纵向一体化工程方案"
published_date: 2026-08-04
source_url: https://www.rand.org/pubs/research_reports/RRA4827-1.html
pdf_url: https://www.rand.org/content/dam/rand/pubs/research_reports/RRA4800/RRA4827-1/RAND_RRA4827-1.pdf
pdf_status: 200 application/pdf
external_source_url:
authors: ["Comer, Steven F.", "Pavela, Hunter", "Gandhi, Varun", "Siler-Evans, Kyle", "Devendorf, Erich", "Kelley, Ben", "Gimbi, James", "Aguirre, Jair", "Kulp, Gabriel", "Stalczynski, Mark", "Malone, Matthew J."]
keywords: ["Data Privacy", "Cybersecurity", "Artificial Intelligence", "National Security"]
subjects: ["Data Privacy", "Research", "Cybersecurity", "RAND-Initiated", "Artificial Intelligence", "National Security"]
topic_tags: ["AI治理", "数字经济"]
priority: P1
score: 8
translation_level: full_or_long
copyright_boundary: private_fulltext_archive
fetch_status: detail_ok
---

# Secure Inference Data Centers: A Vertically Integrated Strategy for Security Engineering

## 中文摘要与研判

### 核心观点

RAND提出安全等级5的专用推理数据中心，用于在五年运行期内保护模型权重、算法和推理数据免受高能力国家级对手窃取、篡改和滥用。报告明确支持在国家安全、应急响应和试点场景部署此类设施，认为所需技术已经成熟，无须等待基础研究突破。其“从概念到电路”方法先确定必须阻止的战略后果，再向下推导分区、单向数据二极管、跨安全域协议和形式化验证等设计，反对在通用基础设施外围事后叠加安全控制。方案刻意限制连接、软件变更和物理访问，因为多余功能和容量会扩大攻击面。成本估算为概念验证设施3700万至5000万美元，企业级版本2.77亿至3.45亿美元；在紧急或国家优先条件下，最短约14个月可完成建设部署。报告也承认高隔离和固定功能会限制通用性，因此其主张是面向高价值推理工作负载的专用工程路径，而非替代所有数据中心。

### 建议

AI实验室、云服务商、政府机构或公益组织应尽快确定实施主体和集成商，提前选址，并在土建启动前原型验证形式化协议、单向数据流等关键部件；利用既有政府设施可进一步压缩工期。

## 元数据

- 原始标题：Secure Inference Data Centers: A Vertically Integrated Strategy for Security Engineering
- 发布日期：2026-08-04
- 来源链接：https://www.rand.org/pubs/research_reports/RRA4827-1.html
- PDF链接：https://www.rand.org/content/dam/rand/pubs/research_reports/RRA4800/RRA4827-1/RAND_RRA4827-1.pdf
- 关键词：Data Privacy, Cybersecurity, Artificial Intelligence, National Security
- 主题标签：AI治理, 数字经济
- 优先级：P1

## English Source Material

This report presents a strategy for deployment of secure inference data centers (SIDCs)—purpose-built facilities designed to protect artificial intelligence models from advanced nation-state adversaries. SIDCs use rigorous partitioning, unidirectional data diodes, and formal methods to ensure confidentiality and integrity. Recommended for national security and emergency response, SIDCs can be built today with proven technologies. Secure Inference Data Centers A Vertically Integrated Strategy for Security Engineering Steven F. Comer , Hunter Pavela , Varun Gandhi , Kyle Siler-Evans , Erich Devendorf , Ben Kelley , James Gimbi , Jair Aguirre , Gabriel Kulp , Mark Stalczynski , et al. Research Published Aug 4, 2026 Download PDF Share on LinkedIn Share on X Share on Facebook Email As artificial intelligence (AI) systems become increasingly critical to national security and other high-stakes domains, the risk of model theft, manipulation, and misuse by sophisticated adversaries grows. In this report, the authors present a vertically integrated security strategy for secure inference data centers (SIDCs): purpose-built, Security Level 5 facilities designed to protect trained AI models against the most-advanced nation-state adversaries. The authors’ proposed SIDC architecture employs rigorous system partitioning, unidirectional data diodes, and formally verified cross-realm protocols to ensure the confidentiality and integrity of model weights, algorithms, and inference data. The report details a concept-to-circuit methodology, emphasizing minimal, purpose-built features and the use of formal methods for high-assurance components. While operational constraints—such as limited connectivity, fixed software, and restricted physical access—limit general applicability, SIDCs are recommended for national security, emergency response, and pilot deployments. SIDCs can be implemented today using proven technologies. The authors recommend that stakeholders initiate detailed design and prototyping to accelerate deployment. Key Takeaways The SIDC strategy is designed to defend against highly capable nation-state adversaries An SIDC built in accordance with the proposed security strategy can preserve the confidentiality and integrity of model weights, algorithms, and inference data over a five-year operational period. The SIDC security strategy follows a concept-to-circuit approach: Security-critical design choices are derived from the strategic outcomes the system must prevent, rather than being added later as controls around general-purpose infrastructure. This approach favors minimal, purpose-built features because excess capacity introduces unnecessary risk. For the most security-critical elements, the SIDC strategy requires high trustworthiness, including formal methods and other rigorous assurance techniques, to demonstrate that components satisfy their required security properties. An SIDC can be implemented today using proven, off-the-shelf compute hardware No fundamental research breakthroughs are required. Estimated costs are $37 million to $50 million for a proof-of-concept facility and $277 million to $345 million for a larger, enterprise-scale version. Construction and deployment activities can be completed rapidly, in as few as 14 months, under emergency or national priority conditions. Recommendations Identify an implementing entity and begin detailed engineering. An AI laboratory, cloud provider, U.S. government agency, or public-interest organization should step forward, engage a system integrator, and initiate detailed design. Select a site early. Because major construction phases are largely sequential, early site selection is critical to minimizing the total project duration. For rapid deployment, housing the SIDC within an existing government facility can bypass or significantly shorten key development steps. Prototype key security features and integration now. Critical security components, including formally verified protocols and unidirectional dataflows, can be tested on short timescales, independent of facility construction. Doing so is a low-cost opportunity to reduce technical risk and prevent downstream delays. Subscribe to the Policy Currents newsletter Related Content Research Securing AI Model Weights: Preventing Theft and Misuse of Frontier Models May 30, 2024 Research Securing AI Algorithmic Insights Jul 20, 2026 Topics Artificial Intelligence Cybersecurity Data Privacy National Security Document Details Copyright: RAND Corporation Availability: Web-Only Year: 2026 Pages: 51 DOI: https://doi.org/10.7249/RRA4827-1 Document Number: RR-A4827-1 Citation RAND Style Manual Comer, Steven F., Hunter Pavela, Varun Gandhi, Kyle Siler-Evans, Erich Devendorf, Ben Kelley, James Gimbi, Jair Aguirre, Gabriel Kulp, Mark Stalczynski, and Matthew J. Malone, Secure Inference Data Centers: A Vertically Integrated Strategy for Security Engineering, RAND Corporation, RR-A4827-1, 2026. As of August 9, 2026: https://www.rand.org/pubs/research_reports/RRA4827-1.html Copy Text Chicago Manual of Style Comer, Steven F., Hunter Pavela, Varun Gandhi, Kyle Siler-Evans, Erich Devendorf, Ben Kelley, James Gimbi, Jair Aguirre, Gabriel Kulp, Mark Stalczynski, and Matthew J. Malone, Secure Inference Data Centers: A Vertically Integrated Strategy for Security Engineering. Santa Monica, CA: RAND Corporation, 2026. https://www.rand.org/pubs/research_reports/RRA4827-1.html. Copy Text BibTeX RIS Research conducted by RAND Global and Emerging Risks This research was independently initiated and conducted by the Center on AI, Security, and Technology within RAND Global and Emerging Risks using income from operations and gifts and grants from philanthropic supporters. This publication is part of the RAND research report series. Research reports present research findings and objective analysis that address the challenges facing the public and private sectors. All RAND research reports undergo rigorous peer review to ensure high standards for research quality and objectivity. This document and trademark(s) contained herein are protected by law. This representation of RAND intellectual property is provided for noncommercial use only. Unauthorized posting of this publication online is prohibited; linking directly to this product page is encouraged. Permission is required from RAND to reproduce, or reuse in another form, any of its research documents for commercial purposes. For information on reprint and reuse permissions, please visit www.rand.org/pubs/permissions . RAND is a nonprofit institution that helps improve policy and decisionmaking through research and analysis. RAND's publications do not necessarily reflect the opinions of its research clients and sponsors.
