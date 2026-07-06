# thinktank-report-archive

International technology think-tank monitoring workflow.

This repository tracks public research outputs from selected international think tanks and policy research organizations. It is designed for a private GitHub repository and a local research knowledge base.

## Scope

- Technology innovation
- Science, R&D, innovation systems, research infrastructure, and technology diffusion
- AI governance
- Science and technology governance
- Defense AI and cyber
- Digital economy and digital trade
- Industrial policy
- Semiconductors and advanced manufacturing
- STEM talent, innovation workforce, productivity, and industrial competitiveness
- China and Shanghai relevance

P1 is intentionally broader than AI governance. The default priority queue covers reports that support technology innovation and development: technology innovation capacity, public or private R&D, innovation systems, technology adoption and diffusion, research infrastructure, commercialization, industrial competitiveness, advanced manufacturing, digital transformation, STEM talent, productivity, and related policy instruments. A report, paper, or policy brief with any substantive technology topic is treated as at least P1 even when it does not contain AI governance language.

The July 2026 scope update widens future retrieval further toward technology-innovation support systems. Science and technology indicators, public R&D budgets, strategic public investment, research organizations, innovation platforms, metascience, research productivity, technology transfer offices, university spinouts, international research collaboration, industrial value chains, production capacity, supply-chain resilience, public compute, data sharing, skills development, human capital, high-skilled mobility, defense AI, and defense innovation are all treated as substantive innovation-support signals. Additional signals include technology policy, tech policy, pro-innovation regulation, innovation-friendly regulation, innovation policy instruments, pre-commercial procurement, regulatory sandboxes, technology accelerators, research and technology organizations, clean industry, industrial modernization, data interoperability, enterprise digitalization, workforce development, innovation tax incentives, intangible investment, standards and quality infrastructure, testing infrastructure, industrial commons, and capital markets for innovation. Historical backfill already archived under the narrower AI-governance-heavy mix is not rewritten by this rule; new weekly and backfill runs use the broader scoring and write-order policy.

AI economy, LLM industry deployment, compute and infrastructure spending, organizational AI adoption, labor-market effects, research culture, researcher wellbeing, research assessment, and tax or investment incentives for innovation are also treated as technology-innovation support when the source is a report, brief, substantive index chapter, or policy project. Generic detail pages without meta summaries fall back to the first substantive body text so that scoring does not miss innovation-support material hidden outside metadata. For PDF-backed industry reports, HTML pages that include related-card blocks can trigger PDF text fallback to avoid archiving navigation or recommendation text as source material.

Within the same priority bucket, the write queue and weekly brief priority section prefer candidates tagged with technology innovation, semiconductors, advanced manufacturing, digital economy, science and technology talent, defense AI, or innovation-enabling technology governance before pure governance items. When a backfill or weekly command uses `--write-limit`, at least half of the limited batch is reserved for innovation-support candidates when enough such candidates are available, so pure governance sources do not crowd out broader technology-development material. The weekly brief reserves visible P0/P1 slots for innovation-support reports and separates pure AI or technology governance items into a lower-prominence observation section.

Search profiles in `config/search_profiles.yaml` make this scope explicit. `broad_innovation_support` keeps candidates tagged as technology innovation, semiconductors, advanced manufacturing, digital economy, science and technology talent, defense AI, or innovation-enabling technology governance, and excludes candidates that only carry AI governance or technology governance tags without innovation-support signals. Its working definition also covers industrial and supply chains, clean technology, biotechnology, quantum and space technology, electric grids and energy infrastructure, AI compute and data-center foundations, innovation finance, public compute, R&D budgets, research organizations, technology policy, pro-innovation regulation, standards, metrology and quality infrastructure, testing and evaluation capacity, R&D tax incentives, intangible capital, industrial commons, and talent mobility when they support science and technology innovation. The weekly brief also caps pure governance-only items in the expanded P0/P1 section when innovation-support items are available. `ai_governance_watch` remains available for dedicated governance monitoring. The Python `run-weekly`, `run-daily`, and `backfill` commands and their PowerShell wrappers default to `broad_innovation_support`; use `--search-profile ai_governance_watch` or `-SearchProfile ai_governance_watch` only for a dedicated governance watch.

China/Shanghai relevance is treated as a context signal. It can raise priority only when paired with a substantive technology, AI, semiconductor, manufacturing, digital economy, innovation, governance, or talent signal; China-only diplomacy or event pages are capped at P2.

## Core Commands

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m unittest discover -s tests -v
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --batch 1 --limit 5 --dry-run
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --institution carnegie-tech --limit 30 --backfill --lookback-years 3 --unseen-only --search-profile broad_innovation_support
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli audit --batch 1 --limit 5
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli run-weekly --batch 1 --limit 30
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli backfill --batch 1 --limit 5 --min-priority P1 --write-limit 8 --lookback-years 3 --search-profile broad_innovation_support
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli rebuild-state --archive-root archive --state state\articles.sqlite
powershell -ExecutionPolicy Bypass -File scripts\run_weekly.ps1 -Batch 1 -Limit 30
powershell -ExecutionPolicy Bypass -File scripts\run_backfill_batch.ps1 -Batch 1 -Limit 5 -MinPriority P1 -WriteLimit 8 -LookbackYears 3
```

Candidate source URLs are restricted to the institution's own site or subdomains. Event, people, podcast, project, topic, video, webinar, broad index, award-news, and announcement-style pages are filtered out before scoring. Non-report book announcements are capped below P1 even when they mention technology competition. Backfill runs interleave feed, list/topic page, and sitemap candidates so one source type does not exhaust the per-institution limit.

Historical backfill is bounded to the last three years by default. Candidates without a verifiable publication date, candidates dated before the lookback window, and future-dated candidates are skipped during backfill runs.

Weekly incremental runs use a 14-day freshness window by default. Older unseen items should enter through explicit backfill commands, which keeps weekly briefs focused on current signals and prevents stale sitemap or aggregate-page candidates from being treated as current updates.

When a detail page exposes a source PDF and the extracted HTML body is short or does not match the article title, the crawler extracts bounded PDF text as the English source material. This prevents archive pollution from related-article blocks, navigation text, and institution landing-page recommendations.

## Summary and Weekly Brief Standard

Each archived Markdown file now treats the Chinese summary as a research card rather than a short abstract. The minimum Chinese section is structured as `核心观点`, `建议`, and `中国/上海参考`. When a source summary is not yet manually rewritten, the archive still preserves the available summary under `核心观点` and marks missing recommendation or China/Shanghai reference fields for follow-up extraction.

Weekly briefs expand more material than historical daily briefs: up to 18 P0/P1 items, longer per-item summary text, 12 visible technology-innovation support items, 18 broad innovation-support items, 12 China/Shanghai items, and 160 index lines. The weekly P0/P1 section renders the same three-part summary fields so that each priority report exposes its core argument, policy or action advice, and China/Shanghai reference value.

Weekly briefs also reserve a front `漫画导读` section. Markdown, HTML, and PDF weekly outputs now render the comic opener before the overview section. The current candidate style is the single-report evidence-chain sample under `comic/weekly-tech-watch-v7/`; it anchors one report, shows the mechanism and transmission chain, then pairs the image with a textual `读图说明` for the core argument, recommendation, and China/Shanghai reference. `comic/weekly-tech-watch-v6/`, `comic/weekly-tech-watch-v5/`, `comic/weekly-tech-watch-v4/`, `comic/weekly-tech-watch-v3/`, `comic/weekly-tech-watch-v2/`, and the older four-panel sample are retained only as comparison candidates. Automated comic generation should be wired only after the visual style is accepted and generated Chinese text is manually checked.

## Outputs

- Local workspace target: `C:\Users\WINDOWS\OneDrive\知识库\智库信息爬虫`.
- `archive/{institution}/{year}/`: one Markdown file per article/report.
- `briefs/weekly/{year}/`: weekly Markdown, HTML, and PDF briefs.
- `briefs/daily/{year}/`: historical daily Markdown, HTML, and PDF briefs retained for compatibility.
- `comic/weekly-tech-watch-v7/`: current single-report evidence-chain sample analysis, storyboard, prompts, and page for weekly comic openers.
- `comic/weekly-tech-watch-v6/`, `comic/weekly-tech-watch-v5/`, `comic/weekly-tech-watch-v4/`, `comic/weekly-tech-watch-v3/`, `comic/weekly-tech-watch-v2/`, `comic/weekly-tech-watch-sample/`: older comparison samples.
- `state/articles.sqlite`: dedupe and run state.
- `reports/{date}_source_health.csv`: read-only source health report.
- Knowledge-base index target: `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际智库抓取索引.csv`.
- Institution schema target: `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际科技智库机构口径表.csv`.

`state/articles.sqlite` is local runtime state and is not committed. If the repository is cloned on another machine or local state is lost, rebuild it from tracked Markdown archives with `rebuild-state` before running weekly or backfill jobs.

## Automation

The local Codex automation `国际科技智库每周抓取` runs every Sunday at 14:00 Beijing time. It executes tests, runs source health audit, runs `scripts\run_weekly.ps1`, checks weekly brief outputs, fills Chinese title and summary fields for new P0/P1 Markdown files when generated, then commits and pushes tracked `archive/` and `briefs/` outputs to the private GitHub repository.

## Source Status Notes

- Current local coverage and gaps are tracked in `docs/backfill_coverage_audit.md`. Use that audit before resuming historical backfill, especially for zero-coverage and low-coverage sources.
- Multi-agent backfill work should follow `docs/multi_agent_execution.md`: evaluator agents run read-only `evaluate` batches, while only the controller writes `archive/`, `state/articles.sqlite`, the knowledge-base CSV, and weekly briefs. `scripts/run_evaluate_sources.ps1` is the shared read-only evaluator wrapper.
- The default first-batch pool now includes broad innovation-support sources CSIS, Bruegel, ECIPE, ASPI, ORF America, CEPS, Atlantic Council GeoTech, Alan Turing Institute, Hoover TPA, and NBR in addition to RAND, CSET, ITIF, Stanford HAI, Carnegie, Brookings, CNAS, MERICS, OECD.AI, Belfer STPP, IDA STPI, NISTEP, and STEPI.
- CSET uses the WordPress sitemap index for broader backfill discovery across hardware and compute, supply chains, technology talent, research, innovation, biotechnology, quantum, space, and China technology analysis.
- Remaining second-batch P0/P1 sources have guarded configs for Ada Lovelace, interface, and GovAI; GovAI is capped with `run_limit` because it is a specialist governance source.
- ASPI's main site returns Cloudflare 403 to static requests; The Strategist is configured as an explicit auxiliary ASPI domain.
- Belfer uses Drupal sitemap indexes; sitemap candidates are sorted by `lastmod` before truncation so recent science, technology, cyber, innovation, and space materials are not crowded out by older sitemap pages.
- RUSI uses `https://www.rusi.org/sitemap-index.xml` for defense technology, cyber, AI, China, supply-chain, and innovation-support backfill. Media mentions, networks, event recordings, and booking-form pages are filtered before scoring.
- CEPS and NBR can use the explicit `text_proxy_fallback` route when static requests are blocked. This route is source-specific, remains subject to same-domain and publication-detail filters, and should be validated with `evaluate` before any resumed backfill write.
- Slow or high-noise sources can set `run_limit` in `config/institutions/*.yaml`; auxiliary official domains can be listed under `allowed_domains`.

## Copyright Boundary

The intended GitHub repository is private. Public reuse should only use metadata, source links, short summaries, and original analysis. Commercial or paid sources such as Gartner are tracked as metadata-only unless separately authorized.
