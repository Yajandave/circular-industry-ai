param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$schemasPath = Join-Path $repoRoot "backend\app\schemas.py"
$mainPath = Join-Path $repoRoot "backend\app\main.py"

foreach ($path in @($schemasPath, $mainPath)) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from repo root after extracting the zip."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  foreach ($path in @($schemasPath, $mainPath)) {
    Copy-Item $path "$path.bak-$stamp"
  }
}

# 1. Append data quality schemas.
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class DataQualityIssue") {
  $schemaAppend = @'


# Milestone 9F: data quality and import validation schemas

class DataQualityIssue(BaseModel):
    issue_type: str
    severity: str
    field: str
    stream_id: str | None = None
    message: str
    recommended_action: str


class DataQualityReport(BaseModel):
    dataset_label: str
    total_records: int
    readiness_status: str
    readiness_score: int
    critical_issue_count: int
    warning_issue_count: int
    info_issue_count: int
    duplicate_stream_ids: list[str]
    material_breakdown: dict
    department_breakdown: dict
    high_risk_data_flags: dict
    top_quantity_streams: list[dict]
    top_cost_streams: list[dict]
    issues: list[DataQualityIssue]
    governance_note: str
'@
  Add-Content $schemasPath $schemaAppend
}

# 2. Mount data_quality router.
$lines = Get-Content $mainPath
$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )data_quality(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "data_quality"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}

$main = $patchedLines -join [Environment]::NewLine

if ($main -notmatch "app\.include_router\(data_quality\.router\)") {
  if ($main -match "app\.include_router\(audit\.router\)") {
    $main = $main.Replace("app.include_router(audit.router)", "app.include_router(audit.router)`r`napp.include_router(data_quality.router)")
  } elseif ($main -match "app\.include_router\(diagnostics\.router\)") {
    $main = $main.Replace("app.include_router(diagnostics.router)", "app.include_router(diagnostics.router)`r`napp.include_router(data_quality.router)")
  } else {
    $main += "`r`napp.include_router(data_quality.router)`r`n"
  }
}

Set-Content $mainPath $main

Write-Host "Milestone 9F data quality validation patch applied."
Write-Host "Next: remove backups, run backend tests, frontend build, and workflow verification."
