param(
    [Parameter(Mandatory = $true)]
    [string[]]$Institutions,
    [int]$Limit = 10,
    [int]$LookbackYears = 3,
    [string]$SearchProfile = "broad_innovation_support",
    [switch]$UnseenOnly,
    [switch]$UnarchivedOnly,
    [switch]$NoDetails,
    [string]$Python = "C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

foreach ($institution in $Institutions) {
    Write-Host "=== evaluate: $institution ==="
    $args = @(
        "-m", "thinktank_watch.cli", "evaluate",
        "--institution", $institution,
        "--backfill",
        "--lookback-years", $LookbackYears,
        "--limit", $Limit,
        "--search-profile", $SearchProfile
    )
    if ($UnseenOnly) {
        $args += "--unseen-only"
    }
    if ($UnarchivedOnly) {
        $args += "--unarchived-only"
    }
    if ($NoDetails) {
        $args += "--no-details"
    }

    & $Python @args
}
