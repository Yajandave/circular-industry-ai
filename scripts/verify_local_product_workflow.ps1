$ErrorActionPreference = "Stop"

Write-Host "Circular Industry AI - local product workflow verification"
Write-Host "Backend must already be running at http://127.0.0.1:8000"
Write-Host ""

$baseUrl = "http://127.0.0.1:8000"

function Invoke-Step {
  param(
    [string]$Label,
    [scriptblock]$Command
  )

  Write-Host "==> $Label"
  $result = & $Command
  Write-Host "OK: $Label"
  return $result
}

Invoke-Step "Health check" {
  Invoke-RestMethod -Method Get "$baseUrl/health"
}

Invoke-Step "Load sample dataset" {
  Invoke-RestMethod -Method Post "$baseUrl/api/streams/load-sample"
}

Invoke-Step "Run locked rules engine" {
  Invoke-RestMethod -Method Post "$baseUrl/api/recommendations/run"
}

Invoke-Step "Evidence summary" {
  Invoke-RestMethod -Method Get "$baseUrl/api/evidence-register/summary"
}

Invoke-Step "Supplier-loop summary" {
  Invoke-RestMethod -Method Get "$baseUrl/api/procurement/supplier-loops/summary"
}

Invoke-Step "Site-wide AI copilot or fallback summary" {
  Invoke-RestMethod -Method Get "$baseUrl/api/ai-copilot/site-summary"
}

Invoke-Step "AI evidence gap explainer or fallback" {
  Invoke-RestMethod -Method Post "$baseUrl/api/evidence-register/S001/ai-explainer"
}

Invoke-Step "Supplier email draft or fallback" {
  Invoke-RestMethod -Method Post "$baseUrl/api/procurement/supplier-loops/S001/email-draft"
}

Invoke-Step "Circular action report or fallback" {
  Invoke-RestMethod -Method Post "$baseUrl/api/reports/streams/S001/circular-action-report"
}

$readiness = Invoke-Step "Workflow readiness diagnostic" {
  Invoke-RestMethod -Method Get "$baseUrl/api/diagnostics/workflow-readiness"
}

Write-Host ""
Write-Host "Readiness result:"
$readiness | ConvertTo-Json -Depth 6

if ($readiness.ready_for_full_demo -ne $true) {
  throw "Workflow is not ready for full demo. Check blocked diagnostic steps above."
}

Write-Host ""
Write-Host "Local product workflow verification completed successfully."
