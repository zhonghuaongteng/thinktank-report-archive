param(
    [string]$Python = "C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe",
    [switch]$FullTests
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$forbiddenChanges = git status --porcelain -- archive briefs state
if ($forbiddenChanges) {
    Write-Error "Strategy-only mode forbids archive, brief, or state changes:`n$forbiddenChanges"
}

git diff --check -- . ':!briefs/**/*.pdf' ':!briefs/daily/**/*.pdf' ':!briefs/weekly/**/*.pdf'
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

if ($FullTests) {
    & $Python -m unittest discover -s tests -v
} else {
    & $Python -m unittest tests.test_repository_policy -v
}
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

@'
import csv
import sqlite3
from pathlib import Path

archive_count = sum(1 for _ in Path("archive").rglob("*.md"))
conn = sqlite3.connect("state/articles.sqlite")
state_total = conn.execute("select count(*) from articles").fetchone()[0]
state_archived = conn.execute("select count(*) from articles where coalesce(archive_path,'')<>''").fetchone()[0]
conn.close()

kb_path = (
    Path.home()
    / "OneDrive"
    / "\u77e5\u8bc6\u5e93"
    / "\u7cfb\u7edf"
    / "\u7814\u7a76\u77e5\u8bc6\u5e93"
    / "06_\u6570\u636e\u8d44\u4ea7"
    / "\u7814\u62a5_\u56fd\u9645\u667a\u5e93\u6293\u53d6\u7d22\u5f15.csv"
)
with kb_path.open("r", encoding="utf-8-sig", newline="") as handle:
    kb_rows = sum(1 for _ in csv.DictReader(handle))

print(f"archive_count={archive_count}")
print(f"state_total={state_total}")
print(f"state_archived={state_archived}")
print(f"kb_rows={kb_rows}")
'@ | & $Python -
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
