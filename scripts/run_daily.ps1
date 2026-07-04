param(
    [int]$Batch = 1,
    [int]$Limit = 20,
    [string]$Python = "C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\python.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

& $Python -m thinktank_watch.cli run-daily --batch $Batch --limit $Limit
