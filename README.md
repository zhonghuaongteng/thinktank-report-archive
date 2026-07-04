# thinktank-report-archive

International technology think-tank monitoring workflow.

This repository tracks public research outputs from selected international think tanks and policy research organizations. It is designed for a private GitHub repository and a local research knowledge base.

## Scope

- Technology innovation
- AI governance
- Science and technology governance
- Defense AI and cyber
- Digital economy and digital trade
- Industrial policy
- Semiconductors and advanced manufacturing
- China and Shanghai relevance

China/Shanghai relevance is treated as a context signal. It can raise priority only when paired with a substantive technology, AI, semiconductor, manufacturing, digital economy, governance, or talent signal; China-only diplomacy or event pages are capped at P2.

## Core Commands

```powershell
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m unittest discover -s tests -v
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --batch 1 --limit 5 --dry-run
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli evaluate --institution carnegie-tech --limit 30 --backfill
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli audit --batch 1 --limit 5
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli run-daily --batch 1 --limit 20
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli backfill --batch 1 --limit 5 --min-priority P1 --write-limit 8
C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe -m thinktank_watch.cli rebuild-state --archive-root archive --state state\articles.sqlite
powershell -ExecutionPolicy Bypass -File scripts\run_backfill_batch.ps1 -Batch 1 -Limit 5 -MinPriority P1 -WriteLimit 8
```

Candidate source URLs are restricted to the institution's own site or subdomains. Event, people, podcast, project, topic, video, webinar, broad index, and announcement-style pages are filtered out before scoring. Backfill runs interleave feed, list/topic page, and sitemap candidates so one source type does not exhaust the per-institution limit.

## Outputs

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

- Second-batch P0/P1 sources now have guarded configs for CSIS, ASPI, Ada Lovelace, interface, Atlantic Council, Bruegel, ECIPE, and GovAI.
- ASPI's main site returns Cloudflare 403 to static requests; The Strategist is configured as an explicit auxiliary ASPI domain.
- CEPS RSS and detail pages are unstable or blocked for static requests. CEPS remains in the institution table, but this source should be treated as metadata/health-check first until a browser-backed parser is added.
- Slow or high-noise sources can set `run_limit` in `config/institutions/*.yaml`; auxiliary official domains can be listed under `allowed_domains`.

## Copyright Boundary

The intended GitHub repository is private. Public reuse should only use metadata, source links, short summaries, and original analysis. Commercial or paid sources such as Gartner are tracked as metadata-only unless separately authorized.
