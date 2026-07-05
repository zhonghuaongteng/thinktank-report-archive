param(
    [int]$Batch = 1,
    [int]$Limit = 5,
    [int]$WriteLimit = 8,
    [int]$LookbackYears = 3,
    [ValidateSet("P0", "P1", "P2", "P3")]
    [string]$MinPriority = "P1",
    [string]$SearchProfile = "broad_innovation_support",
    [string]$Python = "C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$args = @(
    "-m", "thinktank_watch.cli", "backfill",
    "--batch", $Batch,
    "--limit", $Limit,
    "--min-priority", $MinPriority,
    "--write-limit", $WriteLimit,
    "--lookback-years", $LookbackYears
)
if ($SearchProfile) {
    $args += @("--search-profile", $SearchProfile)
}

& $Python @args
