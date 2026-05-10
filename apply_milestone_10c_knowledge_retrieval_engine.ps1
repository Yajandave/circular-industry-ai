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

# 1. Append knowledge retrieval schemas.
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class KnowledgeStreamInput") {
  $schemaAppend = @'


# Milestone 10C: knowledge retrieval engine schemas

class KnowledgeValidationSummary(BaseModel):
    valid: bool
    counts: dict
    source_count: int
    issues: list[str]
    governance_note: str


class KnowledgeStreamInput(BaseModel):
    stream_id: str | None = None
    stream_name: str
    material: str
    source_process: str
    monthly_quantity_kg: float | None = None
    current_route: str | None = None
    disposal_cost_per_month: float | None = None
    contamination_risk: str | None = None
    hazardous_flag: str | None = None
    department: str | None = None
    supplier: str | None = None
    supplier_takeback_available: str | None = None
    recycled_content_available: str | None = None
    notes: str | None = None


class KnowledgeRetrievalResult(BaseModel):
    stream_id: str
    stream_name: str
    material: str
    source_process: str
    matched_materials: list[dict]
    matched_routes: list[dict]
    evidence_rules: list[dict]
    future_horizon: list[dict]
    retrieval_notes: list[str]
    knowledge_validation: dict
    governance_note: str
'@
  Add-Content $schemasPath $schemaAppend
}

# 2. Mount knowledge router.
$lines = Get-Content $mainPath
$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )knowledge(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "knowledge"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}

$main = $patchedLines -join [Environment]::NewLine

if ($main -notmatch "app\.include_router\(knowledge\.router\)") {
  if ($main -match "app\.include_router\(data_quality\.router\)") {
    $main = $main.Replace("app.include_router(data_quality.router)", "app.include_router(data_quality.router)`r`napp.include_router(knowledge.router)")
  } elseif ($main -match "app\.include_router\(audit\.router\)") {
    $main = $main.Replace("app.include_router(audit.router)", "app.include_router(audit.router)`r`napp.include_router(knowledge.router)")
  } else {
    $main += "`r`napp.include_router(knowledge.router)`r`n"
  }
}

Set-Content $mainPath $main

Write-Host "Milestone 10C knowledge retrieval engine patch applied."
Write-Host "Next: remove backups, run backend tests, frontend build, and manual API checks."
