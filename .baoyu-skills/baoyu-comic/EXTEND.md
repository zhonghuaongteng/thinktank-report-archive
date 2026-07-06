---
version: 2
watermark:
  enabled: false
  content: ""
  position: bottom-right
  opacity: 0.5
preferred_art: ligne-claire
preferred_tone: neutral
preferred_layout: mixed
preferred_aspect: "16:9"
language: zh
preferred_image_backend: auto
generation_batch_size: 2
character_presets: []
---

# baoyu-comic Preferences for Thinktank Weekly Briefs

Weekly topic comics are generated through Codex image generation, with `baoyu-image-gen` pinned to the `codex-cli` provider for scripted runs.

This project uses concise editorial knowledge comics inside weekly brief topic pages. The default visual direction is clear-line, mixed-layout, 16:9 landscape pages with restrained explanatory tone.

Generated pages should foreground the report's core idea in a popular-science visual language: concrete scenes, legible metaphors, visible evidence objects, affected actors, and the main consequence. Include China/Shanghai reference points only when the source material gives a concrete basis. Avoid entertainment-first caricature, dense speech bubbles, decorative scenes unrelated to the weekly research signal, or rigid policy-flow diagrams.

After sample review, future weekly brief comics should use a single-thesis evidence-chain structure when the topic is policy research. Each page should make one explicit analytical claim, then show report signals as compact evidence cards, a dominant policy bottleneck, and the report's central policy implication. Source institution names should be secondary. Visual hierarchy should prioritize concrete policy tradeoffs, resource allocation, cost attribution, supply-chain choke points, and boundary-management questions over generic topic maps, character scenes, or decorative report covers.

Rejected direction: the v2 issue-diagnostic map was readable but still too abstract. It showed themes and chains, yet did not make the report-specific policy conflicts visible enough.

Rejected direction: the v3 policy-conflict grid improved readability but still distributed attention across four equal themes. It did not force the viewer to see one decisive weekly issue before reading the labels.

Rejected direction: the v4 single-thesis evidence-chain page improved hierarchy, but still looked like a generalized topic map. It did not expose the decisive claim, evidence chain, recommendations, and China/Shanghai reference of a specific report.

Current direction: future weekly brief comics should use a single-report issue-diagnosis format when the weekly material contains one strong anchor report. The page should show the report's core mechanism, not a broad theme summary. Use concrete analytical objects such as technology stacks, migration bridges, supply-chain chokepoints, policy ledgers, access tiers, and implementation pipelines. The comic must remain visually engaging, but every panel must answer one of four questions: what changed, what evidence supports it, what policy recommendation follows, and what conclusion matters most. China/Shanghai should appear only when the report gives a concrete reference point.

Rejected direction: the v5 two-page report-diagnosis sample was visually polished but still read too much like a static policy diagram. It identified the technical-stack issue, yet did not make the decisive blockage and consequence visible enough at first glance.

Current priority: use failure-diagnosis or conflict-site comics for weekly topic pages. A strong page should show an input, a blockage, an affected actor, and a policy repair path in one visual chain. The first screen must make the key issue visible before the reader parses labels. Prefer hard gates, broken bridges, jammed pipelines, warning ledgers, testing benches, adaptation workshops, and decision dashboards over balanced module grids. For China/Shanghai references, show concrete policy tools only when the source supports them.

Rejected direction: the v6 failure-diagnosis page had visual conflict, but the key issue still required too much interpretation. It also made the report anchor secondary and allowed the source label to drift from the current weekly evidence base. Future comics must make the anchor report, central mechanism, recommendation, and core conclusion visible in the composition or immediately adjacent reading note.

Current direction: use a single-report explanatory viewpoint comic for weekly briefs. The comic should help a reader understand the article's central idea without requiring a complete reconstruction of the report's argument. Organize the page around four reader questions: what the article is about, what viewpoint should be remembered, what visual scene or evidence object can make it legible, and what consequence or policy implication matters most. If the article contains charts, maps, evidence images, technical architecture diagrams, data curves, supply-chain figures, or photos, translate those cues into comic screens, report pages, whiteboards, evidence cards, or background devices; use real source images as references only when the automation explicitly provides them. Do not force the final panel toward China or Shanghai; include that angle only when the report provides a concrete basis. For topic choice, prefer reports with concrete mechanisms such as export controls, critical materials, industrial AI adoption, technology diffusion, public R&D infrastructure, testing fields, standards sandboxes, talent pipelines, or supply-chain resilience.

中文约束：漫画不要求逻辑完整复刻，重点是科普化、可视化地呈现文章观点；如有证据配图线索，优先转译为漫画中的证据卡、屏幕、白板或背景装置；最后一格或最后一页不强行落到中国或上海；没有明确参照时，突出报告核心观点即可。
