---
version: 1
default_provider: codex-cli
default_quality: 2k
default_aspect_ratio: "16:9"
default_image_size: null
default_image_api_dialect: null
default_model:
  codex-cli: codex-image-gen
batch:
  max_workers: 1
  provider_limits:
    codex-cli:
      concurrency: 1
      start_interval_ms: 2000
---

# baoyu-image-gen Preferences for Thinktank Weekly Briefs

Use Codex CLI image generation for weekly thinktank comic pages. This path uses the local Codex login and does not require project API keys.

Generate 16:9 comic pages suitable for embedding into PDF reports. The visual style should follow the project `baoyu-comic` preference: single-report explanatory viewpoint comics, with popular-science visual scenes, visible evidence objects, affected actors, and a clear core conclusion. The comic does not need to reconstruct the full report logic; it should make the article's main viewpoint legible. China/Shanghai reference points should appear only when the source material gives a concrete basis.

中文约束：漫画应科普化、可视化地呈现文章观点；如有证据配图线索，优先转译为漫画中的证据卡、屏幕、白板或背景装置；最后一格不强行落到中国或上海。
