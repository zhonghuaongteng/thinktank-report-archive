---
institution: Information Technology and Innovation Foundation
institution_slug: itif
institution_type: think_tank
source_group: core_technology
content_type: article
source_completeness: full_text
english_title: "Congress Can Bring Clarity to AI Shutdown Authority"
chinese_title: "美国国会应明确AI模型停服权限"
published_date: 2026-08-03
source_url: https://itif.org/publications/2026/08/03/congress-can-bring-clarity-to-ai-shutdown-authority/
pdf_url:
pdf_status: none
external_source_url:
authors: ["Michelle Lopes Maldonado"]
keywords: ["AI治理", "科技创新"]
subjects: []
topic_tags: ["AI治理", "科技创新"]
priority: P0
score: 10
translation_level: full_or_long
copyright_boundary: private_archive
fetch_status: detail_ok
---

# Congress Can Bring Clarity to AI Shutdown Authority

## 中文摘要与研判

### 核心观点

ITIF以美国商务部因越狱风险要求Anthropic全球停用两款模型的事件为例，主张国会建立透明、可预期且比例适当的AI停服权限框架。文章并不否认严重模型漏洞可能需要政府干预，但强烈反对依赖口头证据、无公开标准和无程序保障的全球召回。两款模型停服约两周半后恢复，其中一款仅向约100家经审查美国机构开放，说明分级访问等窄化措施原本可用。突然停服使医院、企业和研究机构把美国模型视为可被随时切断的依赖，进而增加冗余成本、抑制关键业务采用，并给无法被美国召回的中国开放权重模型创造竞争空间。作者警示，若企业因披露漏洞而面临不透明召回，合作和安全信息共享都会下降。其同时区分闭源托管模型、开放权重模型和境外模型，强调停服权对后两类的实际约束能力明显更弱。

### 建议

国会应把行政命令固化为法律，明确书面通知、回应与修复期限、申诉渠道和保密保护；建立类似CVE的AI越狱分级披露体系，优先采用行为门控、分级访问和协调修复，并为善意安全研究设置安全港。

## 元数据

- 原始标题：Congress Can Bring Clarity to AI Shutdown Authority
- 发布日期：2026-08-03
- 来源链接：https://itif.org/publications/2026/08/03/congress-can-bring-clarity-to-ai-shutdown-authority/
- PDF链接：无
- 关键词：AI治理, 科技创新
- 主题标签：AI治理, 科技创新
- 优先级：P0

## English Source Material

Congress Can Bring Clarity to AI Shutdown Authority By Michelle Lopes Maldonado | August 3, 2026 Three days after Anthropic launched Claude Fable 5 and Mythos 5 last month, the Commerce Department issued an export control directive barring any foreign national from accessing the models. Because Anthropic could not verify users’ nationality in real time, complying meant taking both models offline for everyone, everywhere . The administration issued the order after learning of a jailbreak—a prompting technique that circumvents the model’s built-in guardrails—that would allow Fable 5 to identify software vulnerabilities and produce exploit code . Anthropic countered that jailbreak was narrow and replicable on other deployed models , and after two and a half weeks of negotiation, Commerce lifted the controls on June 30 . Fable 5 returned globally on July 1 , with Mythos 5 restored to roughly 100 vetted U.S. institutions . Users of these models experienced whiplash, as the shutdown came suddenly and without warning. British lawmakers noted that hospitals, companies, and researchers were using Fable 5 when it went dark. Prudent buyers will now price this risk into adoption, building redundancy, splitting workloads across vendors, hesitating before wiring the most capable American models into critical operations. That is a real tax on productivity, and it falls hardest on the organizations trying to deploy AI most seriously. For governments and businesses abroad, the lesson was clear: American AI is a revocable dependency that Washington can cut off without warning. That is a gift to Chinese open-weight developers, whose models no U.S. authority can recall, a point American investors and executives made while criticizing the shutdown for handing rivals catch-up time . A country whose AI leadership depends on the rest of the world choosing its models should think carefully before demonstrating that it is not a reliable partner. There is also uncertainty, as there are no clear and transparent rules of engagement. Outside of those in the negotiating room, the rules are ambiguous at best, and unknown at worst. The government’s evidence was presented verbally, and the public accounts conflict. Reports claim that White House adviser David Sacks asserted that Anthropic refused to fix the jailbreak , while Anthropic said it never received disclosure of a jailbreak that produced a harmful result . The reinstatement did not resolve these issues because it was a negotiated settlement conducted through private letters , producing no published standard for what triggered the action or what satisfied the government’s concern. The off switch is now confirmed. The conditions for flipping it back on, however, are not. This ambiguity functions as a standing risk premium on frontier AI. If cooperation and transparency about vulnerabilities are met with recalls, companies may, ultimately, offer less of both. Congress is not the only body that can act in this instance. The administration can adopt clear protocols to convert this confusion and uncertainty into clarity and consistency for businesses and governments alike. Clear protocols would establish uniform rules, evidentiary standards, and an understanding of actions to take in the event of genuinely dangerous deployments. For hosted U.S. models, it would help guarantee due process, including written notice, an opportunity to respond and remediate, defined timelines, and an appeals path so companies are not switched off on verbal claims. Any protocols would favor targeted and proportionate remedies over blunt global recalls. In this case, a proportionate response would have looked less like an export-control order and more like a coordinated vulnerability disclosure process that already governs software security: the government discloses the jailbreak to the company under confidentiality, the company receives a defined window to patch its safeguards and verify the fix, and regulators escalate only if remediation fails. Escalation itself should have gradations short of a blackout, such as gating the specific exploit-generation behavior behind additional safeguards while a fix is underway or applying tiered access for the most capable model class. The proof that narrower options existed is the settlement itself. Mythos 5 returned under a tiered arrangement, with access restricted to roughly 100 vetted U.S. institutions . Absent a credible risk of catastrophic harm, this is the type of remedy the government should employ before imposing a global shutdown. In the event that Congress takes action on a parallel and complementary path, it should codify the provisions of the June 2, 2026, Executive Order , “ Promoting Advanced Artificial Intelligence Innovation and Security ,” to provide a durable statutory framework that cannot be easily reversed by future administrations and that gives developers, researchers, and regulators greater certainty about compliance expectations. Any legislation should include strong confidentiality protections to encourage responsible reporting and information sharing without exposing developers’ proprietary models, trade secrets, or sensitive security vulnerabilities. Specifically, disclosures made to designated federal agencies concerning severe AI vulnerabilities or jailbreaks should be protected from unnecessary public release and shared only with authorized personnel under appropriate cybersecurity and classified-information handling standards where applicable. Congress also should establish a standardized Common Vulnerabilities and Exposures (CVE)-style system for rating and disclosing AI jailbreaks so that the term “severe risk” has a consistent technical meaning for regulators, developers, and independent researchers. The events of Fable 5 also are a good reminder that cyber capability is inherently dual-use: the same vulnerability-discovery techniques that are exploited by malicious actors are also essential for defenders to identify and remediate weaknesses before they are weaponized. Accordingly, the statutory framework should provide carefully tailored exemptions and safe harbors for legitimate research and development conducted by academic institutions, small language model developers, and small business enterprises, modeled in part on CISA’s Coordinated Vulnerability Disclosure framework, which encourages good-faith security research while providing structured processes for responsible disclosure and remediation. This type of approach would help ensure that security research and innovation are not unnecessarily burdened while maintaining appropriate safeguards against misuse. Finally, policymakers should be clear about the reach of any regulatory or legislative requirement. A switch-off authority, however well designed, applies fully only to hosted, closed-weight models, i.e., deployments where a vendor can patch, gate, and, if necessary, revoke access. Open-weight models cannot be recalled once released, so the most meaningful intervention point is before publication, which is where any evaluation requirements for them should reside. Non-U.S. models located outside U.S. jurisdiction altogether are much more difficult to apply these protocols to and may need sanctions or other remedies available under international law. This asymmetry is why the evidentiary bar for action matters. Before restricting a U.S. closed-weight model, there should be a demonstration that the capability at issue is not already available in open-weight or foreign systems. In the recent incident with Fable 5, Anthropic argued the jailbreak was replicable on other deployed models . If that claim is true, then restriction delivers no security gain but does have the effect of pushing users toward models no U.S. authority can patch, monitor, or switch off. The dispute lasted nineteen days; the consequences, however, may last far longer. The central lesson is that the United States should not govern frontier AI by ad-hoc ultimatum. Congress should enact clear statutory authority with defined capability thresholds, due process, and proportionate remedies, so that companies, customers, and allies know the rules before the next capability threat arrives. Image credit for social media preview: Canva
