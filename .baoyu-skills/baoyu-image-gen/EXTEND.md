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

Generate 16:9 comic pages suitable for embedding into PDF reports. The visual style should follow the project `baoyu-comic` preference: single-report evidence-chain policy comics, with concrete scenes, conflict, action tools, and a clear core conclusion. China/Shanghai reference points should appear only when the source material gives a concrete basis.
