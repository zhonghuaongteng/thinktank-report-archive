param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d{4}-\d{2}-\d{2}$')]
    [string]$Date,
    [int]$Batch = 1,
    [int]$Limit = 30,
    [ValidateRange(1, 366)]
    [int]$LookbackDays = 7,
    [string]$SearchProfile = "broad_innovation_support",
    [Parameter(Mandatory = $true)]
    [string]$Python
)

$ErrorActionPreference = "Stop"
[void][datetime]::ParseExact($Date, "yyyy-MM-dd", [Globalization.CultureInfo]::InvariantCulture)
if (-not [IO.Path]::IsPathRooted($Python) -or -not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python must be the verified absolute interpreter path."
}
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$args = @(
    "-m", "thinktank_watch.cli", "run-weekly",
    "--date", $Date,
    "--batch", $Batch,
    "--limit", $Limit,
    "--lookback-days", $LookbackDays,
    "--brief-cadence", "weekly"
)
if ($SearchProfile) {
    $args += @("--search-profile", $SearchProfile)
}

& $Python @args
if ($LASTEXITCODE -ne 0) {
    throw "Weekly collection failed (exit code $LASTEXITCODE)."
}
