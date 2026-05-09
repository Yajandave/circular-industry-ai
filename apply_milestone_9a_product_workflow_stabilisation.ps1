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

# 1. Append workflow readiness schemas
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class ProductWorkflowStep") {
  $schemaAppend = @'

# Milestone 9A: product workflow readiness schemas

class ProductWorkflowStep(BaseModel):
    name: str
    status: str
    detail: str
    required_next_action: str


class ProductWorkflowReadiness(BaseModel):
    product_stage: str
    backend_status: str
    alpha_exit_status: str
    total_streams: int
    total_recommendations: int
    ready_for_full_demo: bool
    evidence_summary: dict | None = None
    supplier_loop_summary: dict | None = None
    steps: list[ProductWorkflowStep]
    governance_note: str
'@
  Add-Content $schemasPath $schemaAppend
}

# 2. Mount diagnostics router
$lines = Get-Content $mainPath

$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )diagnostics(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "diagnostics"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}

$main = $patchedLines -join [Environment]::NewLine

if ($main -notmatch "app\.include_router\(diagnostics\.router\)") {
  if ($main -match "app\.include_router\(reports\.router\)") {
    $main = $main.Replace("app.include_router(reports.router)", "app.include_router(reports.router)`r`napp.include_router(diagnostics.router)")
  } else {
    $main += "`r`napp.include_router(diagnostics.router)`r`n"
  }
}

Set-Content $mainPath $main

Write-Host "Milestone 9A product workflow stabilisation patch applied."
Write-Host "Next: run pytest from backend and npm run build from frontend."
