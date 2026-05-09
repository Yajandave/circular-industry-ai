param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$schemasPath = Join-Path $repoRoot "backend\app\schemas.py"
$mainPath = Join-Path $repoRoot "backend\app\main.py"

foreach ($path in @($schemasPath, $mainPath)) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from the circular-industry-ai repo root."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  Copy-Item $schemasPath "$schemasPath.bak-$stamp"
  Copy-Item $mainPath "$mainPath.bak-$stamp"
}

# 1. Append schema
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class CircularActionReport") {
  $schemaAppend = @'

# Milestone 8E: circular action report builder schemas

class CircularActionReport(BaseModel):
    generation_mode: str
    model_name: str
    stream_id: str
    stream_name: str
    decision_lock_status: str
    report_title: str
    executive_summary: str
    locked_recommendation: str
    risk_and_review_status: str
    evidence_position: str
    circular_resolution_summary: str
    supplier_loop_summary: str
    implementation_plan: list[str]
    evidence_to_collect: list[str]
    unsafe_claims_to_avoid: list[str]
    recommended_next_actions: list[str]
    claim_boundary: str
    governance_note: str
    validation_warnings: list[str]
    locked_rule_applied: str | None = None
    locked_risk_level: str | None = None
    locked_human_review_required: bool | None = None
    locked_claim_readiness: str | None = None
    locked_review_gate: str | None = None
    locked_procurement_route: str | None = None
'@
  Add-Content $schemasPath $schemaAppend
}

# 2. Patch main.py router imports and includes
$lines = Get-Content $mainPath

$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )reports(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "reports"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}

$main = $patchedLines -join [Environment]::NewLine

if ($main -notmatch "app\.include_router\(reports\.router\)") {
  if ($main -match "app\.include_router\(procurement\.router\)") {
    $main = $main.Replace("app.include_router(procurement.router)", "app.include_router(procurement.router)`r`napp.include_router(reports.router)")
  } elseif ($main -match "app\.include_router\(playbooks\.router\)") {
    $main = $main.Replace("app.include_router(playbooks.router)", "app.include_router(reports.router)`r`napp.include_router(playbooks.router)")
  } else {
    $main += "`r`napp.include_router(reports.router)`r`n"
  }
}

Set-Content $mainPath $main

Write-Host "Milestone 8E circular action report backend patch applied."
Write-Host "Next: run pytest from backend."
