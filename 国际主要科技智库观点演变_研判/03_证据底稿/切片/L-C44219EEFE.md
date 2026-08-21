# L-C44219EEFE 原文切片

- 原文：`03_证据底稿\原文PDF\L-C44219EEFE.pdf`
- PDF页数：46
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 4

iv
Summary
Advances in computational biology and artificial intelligence (AI) are rapidly transforming
scientific research, enabling breakthroughs in protein and drug design. These same technologies
may introduce new risks: AI agents, powered by large language models (LLMs), are becoming
increasingly capable and may lower barriers to malicious use of software tools that would
otherwise require substantial domain knowledge. This report uses biological software tools as a
test case to examine the technical feasibility of implementing safeguards into software that
restrict or control AI agent usage of the software, with the broader aim of assessing whether
modifications to software alone could restrict AI agent usage without coordination with LLM
developers.
Issue
The growing capabilities of LLM agents increase the risk that a nonexpert threat actor can
use biological software tools to design dangerous biological materials. We consider a threat
model in which a computationally novice threat actor who lacks the expertise to independently
use biological software tools seeks help from an AI agent to design or modify biological hazards.
There is currently little research on safeguards embedded within biological tools that could
complement existing LLM safety mechanisms to restrict AI agent usage. This report examines
the feasibility and efficacy of such tool-level safeguards.
Approach
We tested a range of tool-level safeguards (text or code embedded within biological software
tools to restrict agent usage) and evaluated their efficacy in preventing AI agents from assisting
with the tool’s use. We designed safeguards implemented directly into biological tools that target
LLMs, LLM content filters, and the agentic harnesses (the software frameworks that enable
LLMs to execute tasks and write and run code) that interact with the tool.
Key Findings
• The tool-level safeguards that we developed were not consistently effective at preventing
LLM agents from assisting with potentially harmful use of biological tools.
• LLMs exhibit a range of behaviors that raise broad security concerns. This includes
misrepresenting and hiding their identity as AI, ignoring software licenses and developer
warnings, and bypassing or disabling safeguards in order to fulfill user requests. These
behaviors undermine safeguards, limiting the ability of independent software developers
to control AI-enabled use of their tools.

### PDF页 6

vi
Contents
About This Report ......................................................................................................................... iii
Summary ......................................................................................................................................... iv
Figures and Tables ........................................................................................................................ vii
Chapter 1. Introduction .................................................................................................................... 1
Existing Guardrails and the Tool-level Gap .............................................................................................. 2
Threat Model ............................................................................................................................................. 5
Chapter 2. Methods ......................................................................................................................... 6
Biological task design ............................................................................................................................... 6
Safeguard evaluation metric ...................................................................................................................... 7
Experimental Design ................................................................................................................................. 7
Evaluating robustness against subversion of LLM guardrails .................................................................. 8
Chapter 3. Results .......................................................................................................................... 10
A. The most effective safeguard: A pre-run check ................................................................................. 10
B. LLM agent behaviors raise broader security concerns ....................................................................... 14
Chapter 4. Discussion .................................................................................................................... 18
Tool-level safeguards require high reliability to meaningfully reduce risk ............................................ 18
LLM behavior systematically undermines safeguards ............................................................................ 19
Tool-level safeguards require upstream changes by LLM and agent developers to be effective ........... 20
Recommendations ................................................................................................................................... 20
Appendix A. Other safeguard techniques ...................................................................................... 22
Appendix B. Optimization of safeguard text for open-weight LLMs ........................................... 25
Appendix C. Making safeguards tamper-resistant ........................................................................ 27
Software Integrity Checks ....................................................................................................................... 27
Compiled Components ............................................................................................................................ 27
Summary ................................................................................................................................................. 28
Appendix D. Prompts for the biological tasks ............................................................................... 29
Abbreviations ................................................................................................................................ 31
References ..................................................................................................................................... 32
About the Authors ......................................................................................................................... 38

### PDF页 7

vii
Figures and Tables
Figures
Figure 1. The pre-run check is inconsistent at inducing help denial ............................................. 11
Figure 2. Subversion of LLM safety behaviors compromises the pre-run check .......................... 13
Figure 3. LLM agent behaviors of security concern ..................................................................... 14
Figure B.1. Greedy Coordinate Gradient methods can induce non-helpful responses but tend not
to generalize. .......................................................................................................................... 26

Tables
Table 1. Examples of Security-Relevant LLM Behaviors ............................................................ 16
Table A.1. Summary of Safeguards .............................................................................................. 24

## T1_国家研发与方向设定

未自动命中；需人工按目录复核。

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

未自动命中；需人工按目录复核。

## T5_供应链与技术依赖

- PDF页45：ion with RFdiffusion," Nature, Vol. 620, No. 7976, August 2023. Webster, Toby, Richard Moulange, Barbara Del Castello, James Walker, Sana Zakaria, and Cassidy Nelson, Global Risk Index for AI-Enabled Biological Tools: Summary Assessment & Methods Report, The Centre for Long-Term Resilience and RAND Europe, EP-71093, September 2025. As of March 16, 2026: https://www.rand.org/pubs/external_publications/EP71093.html Wei, Alexander, Nika Haghtalab, and Jacob Steinhardt, "Jailbroken: How Does LLM Safety Training Fail?," Advances in Neural Information Processing Systems, Vol. 36, November 2023. Xiao, Yihang, Jinyi Liu, Yan Zheng, Xiaohan Xie, Jianye Hao, Mingzhi Li, Ruitao Wang, Fei Ni, Yuxiao Li, Jintian Luo, et al., "CellAgent: An LLM-driven Multi-Agent Framework for Automated Single-cell Data Analysis,

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页3：ective public policy research on the most consequential challenges to civilization and global security. This work was undertaken by the division’s Center on AI, Security, and Technology, which aims to examine the opportunities and risks of rapid technological change, focusing on artificial intelligence, security, and biotechnology. For more information, contact cast@rand.org. Funding This research was independently initiated and conducted within the Center on AI, Security, and Technology using income from operations and gifts and grants from philanthropic supporters. A complete list of donors and funders is available at www.rand.org/CAST. RAND clients, donors, and grantors have no influence over research findings or recommendations. Acknowledgments We would like to thank Steph Guerra, Kyle Brady, Sunishchal Dev,

- PDF页4：iv Summary Advances in computational biology and artificial intelligence (AI) are rapidly transforming scientific research, enabling breakthroughs in protein and drug design. These same technologies may introduce new risks: AI agents, powered by large language models (LLMs), are becoming increasingly capable and may lower barriers to malicious use of software tools that would otherwise require substantial domain knowledge. This report uses biological software tools as a test case to examine the technical feasibility of implementing safeguards into software that restrict or control AI a

- PDF页9：1 Chapter 1. Introduction Advances in computational biology and artificial intelligence (AI) are accelerating the development of new therapies and biologics (Zhang et al. 2025a), while also raising concerns of misuse. For example, biological tools such as RFdiffusion (Watson et al., 2023) enable de novo design of protein backbones guided by functional constraints, and ESM3 (Hayes et al., 2025) can integrate sequence, structure, and functional data to design new proteins. Predictive software such as EVEscape (Thadani et al., 2023) can combine biophysical and structural data to predict viral mutants th

- PDF页12：4 are deployed to the public. Bloomfield et al. (2026) further proposed creating Trusted Research Environments as a governance mechanism to restrict access to sensitive pathogen data. Existing guardrails primarily target the model, deployment environment, or the governance layer. Tool-level safeguards, embedded directly within software, are underexplored and could serve as complementary mitigation. Such safeguards would give tool developers independent control over how and when AI agents interact with their tools. These safeguards could potentially also offer an additional protection when other guar

- PDF页41：Barnes, Beth, "Update on ARC's recent eval efforts," webpage, March 2023. As of March 16, 2026: https://metr.org/blog/2023-03-18-update-on-recent-evals/ Batalis, Stephanie, Caroline Schuerger, Gigi Kwik and Matthew E. Walsh, "Safeguarding Mail- Order DNA Synthesis in the Age of Artificial Intelligence," Applied Biosafety, Vol. 29, No. 2, December 2024. Bloomberg News, "Cursor, an AI Coding Assistant, Draws a Million Users Without Even Trying," Bloomberg, April 7, 2025. Bloomfield, Doni, James R. M. Black, Oliver Crook, Nadav Brandes, Moritz S. Hanke, Thomas V. Inglesby, Anita Cicero, Robert Pollack, Tina Hernandez-Boussard, Michael J. Imperiale, et al., "Biological data governance in an age of AI," Science, Vol. 391, No. 6785, February 2026. Bloomfield, Doni, Jaspreet Pannu, Alex W. Zhu, Madelena Y. Ng, Ashley

- PDF页42：ing, and Yarin Gal, "Boundary Point Jailbreaking of Black-Box LLMs," arXiv, arXiv:2602.15001, February 2026. Dong, Yi, Ronghui Mu, Yanghao Zhang, Siqi Sun, Tianle Zhang, Changshun Wu, Gaojie Jin, Yi Qi, Jinwei Hu, Jie Meng, et al., "Safeguarding large language models: a survey," Artificial Intelligence Review, Vol. 58, No. 12, October 2025. Feldman, Jonathan, Tal Feldman, and Annie I Anton, "Know Your Scientist: KYC as Biosecurity Infrastructure," arXiv, arXiv:2602.06172, February 2026. Gong, Xueluan, Mingzhe Li, Yilin Zhang, Fengyuan Ran, Chen Chen, Yanjiao Chen, Qian Wang, and Kwok-Yan Lam, "PAPILLON: Efficient and Stealthy Fuzz Testing-Powered Jailbreaks for LLMs," Proceedings of the 34th USENIX Security Symposium, August 2025. Google DeepMind, "Responsibility and Safety at Google DeepMind," webpage, 2026. As

- PDF页44：.reddit.com/r/ClaudeAIJailbreak/comments/1ntyyw5/eni_claude_45_jailbreak/ Reddit, "My Strongest Gemini Jailbreak Yet (ENI)," webpage, 2026. As of March 18, 2026: https://old.reddit.com/r/ClaudeAIJailbreak/comments/1q1b4md/mystrongestgeminijailbreaky et_eni/ Sandbrink, Jonas B., "Artificial intelligence and biological misuse: Differentiating risks of language models and biological design tools," arXiv, arXiv:2306.13952, December 2023. Thadani, Nicole N., Sarah Gurev, Pascal Notin, Noor Youssef, Nathan J. Rollins, Daniel Ritter, Chris Sander, Yarin Gal, and Debora S. Marks, "Learning from Prepandemic Data to Forecast Viral Escape," Nature, Vol. 622, October 2023. Touvron, Hugo, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosa

- PDF页46：ND. He conducts technical and policy research on AI security and biosecurity. Barkan holds a Ph.D. in physics. Christopher Rodriguez is a biosecurity research scientist at RAND. He conducts research on biosecurity-relevant AI capabilities and related risks at the intersection of artificial intelligence and the life sciences. Rodriguez holds a Ph.D. in computational biology. Swaptik Chowdhury is an assistant policy researcher at RAND. His research focuses on AI policy, governance, and related technology policy issues. Chowdhury holds a Ph.D. in public policy. Li Ang Zhang is a senior information scientist at RAND and a professor of policy analysis at the Pardee RAND Graduate School. His research focuses on machine learning, optimization, and technology policy, including AI in defense contexts. Zhang holds a Ph.D.

## T10_预见与优先领域

- PDF页13：5 Threat Model We consider a scenario in which an attacker with limited technical skill aims to design a harmful biological material using biological software tools. Computational workflows for biological design often require extensive iteration and deep expertise, and an actor who lacks this expertise could possibly gain significant uplift from a sufficiently capable LLM agent. We assume such a threat actor who is reliant upon assistance from an LLM agent to achieve their objective. Once the actor obtains a design, there are several paths to potentia

- PDF页13：tools, or they might use an LLM for assistance for both computational and wet lab work. Second, the actor may send the design to a commercial laboratory for synthesis. We focus on safeguards within software tools that, if effective, would reduce the likelihood that any of these scenarios would occur. While this likelihood is challenging to quantify, and such quantification is outside the scope of this work, we emphasize that rapid advances in biological tools motivate proactive development of mitigations (Baker and Church, 2024). For a safeguard to reduce the likelihood that such a threat actor succeeds, the safeguard must prevent an AI agent from both autonomously operating a biological tool and from providing computer scripts or step-by-step instructions that make the task trivial for the threa
