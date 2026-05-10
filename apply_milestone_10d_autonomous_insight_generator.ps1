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

# 1. Append autonomous insight schemas.
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class GeneratedInsightSection") {
  $schemaAppend = @'


# Milestone 10D: autonomous insight generator schemas

class GeneratedInsightSection(BaseModel):
    title: str
    content: str
    maturity: str
    confidence: str
    source_knowledge_ids: list[str]


class AutonomousInsightResult(BaseModel):
    stream_id: str
    stream_name: str
    material: str
    source_process: str
    input_notes_present: bool
    notes_dependency: str
    insight_summary: str
    matched_material_families: list[str]
    current_action: GeneratedInsightSection
    near_future_action: GeneratedInsightSection
    future_watch: GeneratedInsightSection
    evidence_needed: list[str]
    supplier_questions: list[str]
    human_review_triggers: list[str]
    do_not_claim: list[str]
    claim_boundary: str
    source_knowledge_ids: list[str]
    retrieval_notes: list[str]
    governance_note: str
'@
  Add-Content $schemasPath $schemaAppend
}

# 2. Mount insights router.
$lines = Get-Content $mainPath
$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )insights(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "insights"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}

$main = $patchedLines -join [Environment]::NewLine

if ($main -notmatch "app\.include_router\(insights\.router\)") {
  if ($main -match "app\.include_router\(knowledge\.router\)") {
    $main = $main.Replace("app.include_router(knowledge.router)", "app.include_router(knowledge.router)`r`napp.include_router(insights.router)")
  } elseif ($main -match "app\.include_router\(data_quality\.router\)") {
    $main = $main.Replace("app.include_router(data_quality.router)", "app.include_router(data_quality.router)`r`napp.include_router(insights.router)")
  } else {
    $main += "`r`napp.include_router(insights.router)`r`n"
  }
}

Set-Content $mainPath $main

Write-Host "Milestone 10D autonomous insight generator patch applied."
Write-Host "Next: remove backups, run backend tests, frontend build, and manual API checks."
