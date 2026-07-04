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
powershell -ExecutionPolicy Bypass -File scripts\run_backfill_batch.ps1 -Batch 1 -Limit 5 -MinPriority P1 -WriteLimit 8
```

Candidate source URLs are restricted to the institution's own site or subdomains. Event, people, podcast, video, webinar, and announcement-style pages are filtered out before scoring.

## Outputs

- `archive/{institution}/{year}/`: one Markdown file per article/report.
- `briefs/daily/{year}/`: daily Markdown, HTML, and PDF briefs.
- `state/articles.sqlite`: dedupe and run state.
- `reports/{date}_source_health.csv`: read-only source health report.
- Knowledge-base index target: `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际智库抓取索引.csv`.
- Institution schema target: `C:\Users\WINDOWS\OneDrive\知识库\系统\研究知识库\06_数据资产\研报_国际科技智库机构口径表.csv`.

## Automation

The local Codex automation `国际科技智库每日抓取` runs at 10:00 Beijing time. It executes tests, runs source health audit, runs `scripts\run_daily.ps1`, checks brief outputs, fills Chinese title and summary fields for new P0/P1 Markdown files when generated, then commits and pushes tracked `archive/` and `briefs/` outputs to the private GitHub repository.

## Copyright Boundary

The intended GitHub repository is private. Public reuse should only use metadata, source links, short summaries, and original analysis. Commercial or paid sources such as Gartner are tracked as metadata-only unless separately authorized.
