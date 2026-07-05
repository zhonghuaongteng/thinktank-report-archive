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

The July 2026 scope update widens future retrieval further toward technology-innovation support systems. Science and technology indicators, public R&D budgets, strategic public investment, research organizations, innovation platforms, metascience, research productivity, technology transfer offices, university spinouts, international research collaboration, industrial value chains, production capacity, supply-chain resilience, public compute, data sharing, skills development, human capital, high-skilled mobility, defense AI, and defense innovation are all treated as substantive innovation-support signals. Additional signals include innovation policy instruments, pre-commercial procurement, regulatory sandboxes, technology accelerators, research and technology organizations, clean industry, industrial modernization, data interoperability, enterprise digitalization, workforce development, and capital markets for innovation. Historical backfill already archived under the narrower AI-governance-heavy mix is not rewritten by this rule; new daily and backfill runs use the broader scoring and write-order policy.

Within the same priority bucket, the write queue and daily brief priority section prefer candidates tagged with technology innovation, semiconductors, advanced manufacturing, digital economy, science and technology talent, or defense AI before pure governance items. When a backfill or daily command uses `--write-limit`, at least half of the limited batch is reserved for innovation-support candidates when enough such candidates are available, so pure governance sources do not crowd out broader technology-development material. The daily brief reserves visible P0/P1 slots for innovation-support reports and separates pure AI or technology governance items into a lower-prominence observation section.

Search profiles in `config/search_profiles.yaml` make this scope explicit. `broad_innovation_support` keeps candidates tagged as technology innovation, semiconductors, advanced manufacturing, digital economy, science and technology talent, or defense AI, and excludes candidates that only carry AI governance or technology governance tags. Its working definition also covers industrial and supply chains, clean technology, biotechnology, quantum and space technology, innovation finance, public compute, R&D budgets, research organizations, standards and quality infrastructure, and talent mobility when they support science and technology innovation. `ai_governance_watch` remains available for dedicated governance monitoring. The Python `run-daily` and `backfill` commands and their PowerShell wrappers default to `broad_innovation_support`; use `--search-profile ai_governance_watch` or `-SearchProfile ai_governance_watch` only for a dedicated governance watch.

China/Shanghai relevance is treated as a context signal. It can raise priority only when paired with a substantive technology, AI, semiconductor, manufacturing, digital economy, innovation, governance, or talent signal; China-only diplomacy or event pages are capped at P2.

## Core Commands

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m unittest discover -s tests -v
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --batch 1 --limit 5 --dry-run
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --institution carnegie-tech --limit 30 --backfill --lookback-years 3 --unseen-only --search-profile broad_innovation_support
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli audit --batch 1 --limit 5
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli run-daily --batch 1 --limit 20
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli backfill --batch 1 --limit 5 --min-priority P1 --write-limit 8 --lookback-years 3 --search-profile broad_innovation_support
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli rebuild-state --archive-root archive --state state\articles.sqlite
powershell -ExecutionPolicy Bypass -File scripts\run_backfill_batch.ps1 -Batch 1 -Limit 5 -MinPriority P1 -WriteLimit 8 -LookbackYears 3
```

Candidate source URLs are restricted to the institution's own site or subdomains. Event, people, podcast, project, topic, video, webinar, broad index, award-news, and announcement-style pages are filtered out before scoring. Non-report book announcements are capped below P1 even when they mention technology competition. Backfill runs interleave feed, list/topic page, and sitemap candidates so one source type does not exhaust the per-institution limit.

Historical backfill is bounded to the last three years by default. Candidates without a verifiable publication date, candidates dated before the lookback window, and future-dated candidates are skipped during backfill runs.

Daily incremental runs use a 30-day freshness window by default. Older unseen items should enter through explicit backfill commands, which keeps daily briefs focused on current signals and prevents stale sitemap or aggregate-page candidates from being treated as same-day updates.

When a detail page exposes a source PDF and the extracted HTML body is short or does not match the article title, the crawler extracts bounded PDF text as the English source material. This prevents archive pollution from related-article blocks, navigation text, and institution landing-page recommendations.

## Outputs

- Local workspace target: `C:\Users\WINDOWS\OneDrive\知识库\智库信息爬虫`.
- `archive/{institution}/{year}/`: one Markdown file per article/report.
- `briefs/daily/{year}/`: daily Markdown, HTML, and PDF briefs.
- `state/articles.sqlite`: dedupe and run state.
- `reports/{date}_source_health.csv`: read-only source health report.
- Knowledge-base index target: `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际智库抓取索引.csv`.
- Institution schema target: `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际科技智库机构口径表.csv`.

`state/articles.sqlite` is local runtime state and is not committed. If the repository is cloned on another machine or local state is lost, rebuild it from tracked Markdown archives with `rebuild-state` before running daily or backfill jobs.

## Automation

The local Codex automation `国际科技智库每日抓取` runs at 10:00 Beijing time. It executes tests, runs source health audit, runs `scripts\run_daily.ps1`, checks brief outputs, fills Chinese title and summary fields for new P0/P1 Markdown files when generated, then commits and pushes tracked `archive/` and `briefs/` outputs to the private GitHub repository.

## Source Status Notes

- The default first-batch pool now includes broad innovation-support sources CSIS, Bruegel, ECIPE, ASPI, ORF America, CEPS, Atlantic Council GeoTech, Alan Turing Institute, Hoover TPA, and NBR in addition to RAND, CSET, ITIF, Stanford HAI, Carnegie, Brookings, CNAS, MERICS, OECD.AI, Belfer STPP, IDA STPI, NISTEP, and STEPI.
- CSET uses the WordPress sitemap index for broader backfill discovery across hardware and compute, supply chains, technology talent, research, innovation, biotechnology, quantum, space, and China technology analysis.
- Remaining second-batch P0/P1 sources have guarded configs for Ada Lovelace, interface, and GovAI; GovAI is capped with `run_limit` because it is a specialist governance source.
- ASPI's main site returns Cloudflare 403 to static requests; The Strategist is configured as an explicit auxiliary ASPI domain.
- Belfer uses Drupal sitemap indexes; sitemap candidates are sorted by `lastmod` before truncation so recent science, technology, cyber, innovation, and space materials are not crowded out by older sitemap pages.
- RUSI uses `https://www.rusi.org/sitemap-index.xml` for defense technology, cyber, AI, China, supply-chain, and innovation-support backfill. Media mentions, networks, event recordings, and booking-form pages are filtered before scoring.
- CEPS RSS and detail pages are unstable or blocked for static requests. CEPS remains in the institution table, but this source should be treated as metadata/health-check first until a browser-backed parser is added.
- Slow or high-noise sources can set `run_limit` in `config/institutions/*.yaml`; auxiliary official domains can be listed under `allowed_domains`.

## Copyright Boundary

The intended GitHub repository is private. Public reuse should only use metadata, source links, short summaries, and original analysis. Commercial or paid sources such as Gartner are tracked as metadata-only unless separately authorized.
