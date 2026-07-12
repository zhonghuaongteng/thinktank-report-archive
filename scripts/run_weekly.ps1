param(
    [int]$Batch = 1,
    [int]$Limit = 30,
    [int]$LookbackDays = 7,
    [string]$SearchProfile = "broad_innovation_support",
    [string]$Python = "C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$args = @(
    "-m", "thinktank_watch.cli", "run-weekly",
    "--batch", $Batch,
    "--limit", $Limit,
    "--lookback-days", $LookbackDays,
    "--brief-cadence", "weekly"
)
if ($SearchProfile) {
    $args += @("--search-profile", $SearchProfile)
}

& $Python @args
