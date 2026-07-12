param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [int]$LookbackDays = 7,
    [string]$Python = "C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$args = @(
    "-m", "thinktank_watch.cli", "prepare-weekly-comics",
    "--date", $Date,
    "--lookback-days", $LookbackDays
)

& $Python @args
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
