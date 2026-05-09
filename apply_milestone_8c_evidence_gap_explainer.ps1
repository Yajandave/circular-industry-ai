param([switch]$NoBackup)
$ErrorActionPreference = "Stop"
$repoRoot = Get-Location
$schemasPath = Join-Path $repoRoot "backend\app\schemas.py"
$evidenceRouterPath = Join-Path $repoRoot "backend\app\routers\evidence.py"
$clientPath = Join-Path $repoRoot "frontend\src\api\client.js"
$appPath = Join-Path $repoRoot "frontend\src\App.jsx"
$stylesPath = Join-Path $repoRoot "frontend\src\styles.css"
$evidenceComponentPath = Join-Path $repoRoot "frontend\src\components\EvidenceRegister.jsx"
$required = @($schemasPath, $evidenceRouterPath, $clientPath, $appPath, $stylesPath, $evidenceComponentPath)
foreach ($path in $required) { if (!(Test-Path $path)) { throw "Missing expected file: $path. Run this script from the repo root." } }
if (!$NoBackup) { $stamp = Get-Date -Format "yyyyMMdd-HHmmss"; foreach ($path in $required) { Copy-Item $path "$path.bak-$stamp" } }

$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class AIEvidenceGapExplanation") {
  Add-Content $schemasPath @'

# Milestone 8C: AI evidence gap explainer schemas

class AIEvidenceGapExplanation(BaseModel):
    generation_mode: str
    model_name: str
    stream_id: str
    stream_name: str
    decision_lock_status: str
    evidence_gap_summary: str
    claim_readiness_explanation: str
    evidence_to_collect: list[str]
    supplier_documents_required: list[str]
    process_checks_required: list[str]
    safe_current_statement: str
    unsafe_claims_to_avoid: list[str]
    recommended_review_gate: str
    governance_note: str
    validation_warnings: list[str]
    locked_rule_applied: str | None = None
    locked_risk_level: str | None = None
    locked_human_review_required: bool | None = None
    locked_claim_readiness: str | None = None
    locked_review_gate: str | None = None
'@
}

$router = Get-Content $evidenceRouterPath -Raw
if ($router -notmatch "generate_evidence_gap_explanation") {
  $router = $router.Replace("from app.evidence_register import build_evidence_register, build_evidence_summary", "from app.evidence_explainer.service import generate_evidence_gap_explanation`r`nfrom app.evidence_register import build_evidence_record, build_evidence_register, build_evidence_summary")
}
if ($router -notmatch "/evidence-register/\{stream_id\}/ai-explainer") {
  $endpoint = @'

@router.post("/evidence-register/{stream_id}/ai-explainer", response_model=schemas.AIEvidenceGapExplanation)
def explain_evidence_gap(stream_id: str, db: Session = Depends(get_db)):
    """Generate an advisory evidence-gap explanation for one locked recommendation."""
    stream = crud.get_stream_by_stream_id(db, stream_id)
    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail=f"No stream found for stream ID {stream_id}.")
    if not recommendation:
        raise HTTPException(status_code=404, detail="No recommendation found. Run POST /api/recommendations/run first.")
    evidence = build_evidence_record(stream, recommendation)
    return generate_evidence_gap_explanation(stream, recommendation, evidence)

'@
  $anchor = '@router.get("/export/evidence-register.csv")'
  if ($router.Contains($anchor)) { $router = $router.Replace($anchor, $endpoint + $anchor) } else { $router += $endpoint }
}
Set-Content $evidenceRouterPath $router

$client = Get-Content $clientPath -Raw
if ($client -notmatch "generateEvidenceGapExplanation") {
  $anchor = "  evidenceSummary: () => request('/api/evidence-register/summary'),"
  $replacement = "$anchor`r`n  generateEvidenceGapExplanation: (streamId) => request(`/api/evidence-register/${encodeURIComponent(streamId)}/ai-explainer`, { method: 'POST' }),"
  if ($client.Contains($anchor)) { $client = $client.Replace($anchor, $replacement) } else { throw "Could not find evidenceSummary anchor in frontend API client." }
  Set-Content $clientPath $client
}

$app = Get-Content $appPath -Raw
if ($app -notmatch "evidenceGapExplanation") {
  $stateAnchor = "  const [evidenceSummary, setEvidenceSummary] = useState(null);"
  $app = $app.Replace($stateAnchor, "$stateAnchor`r`n  const [evidenceGapExplanation, setEvidenceGapExplanation] = useState(null);")
}
$app = $app.Replace("      setEvidenceSummary(null);`r`n      setResolutionPlans([]);", "      setEvidenceSummary(null);`r`n      setEvidenceGapExplanation(null);`r`n      setResolutionPlans([]);")
$app = $app.Replace("      setEvidenceSummary(null);`n      setResolutionPlans([]);", "      setEvidenceSummary(null);`n      setEvidenceGapExplanation(null);`n      setResolutionPlans([]);")
if ($app -notmatch "explainEvidenceGap") {
  $functionAnchor = "  async function refreshSiteCopilot() {"
  $newFunction = @'
  async function explainEvidenceGap(streamId) {
    await safeRun(`AI evidence gap explanation generated for ${streamId}.`, async () => {
      const result = await api.generateEvidenceGapExplanation(streamId);
      setEvidenceGapExplanation(result);
      setActiveView('evidence');
      setTimeout(() => {
        document.getElementById('evidence-gap-explainer')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 50);
    });
  }

'@
  if ($app.Contains($functionAnchor)) { $app = $app.Replace($functionAnchor, $newFunction + $functionAnchor) } else { throw "Could not find refreshSiteCopilot anchor in App.jsx." }
}
$app = $app -replace "<strong>Milestone [^<]+</strong>\s*<span>[^<]*</span>", "<strong>Milestone 8C</strong>`r`n          <span>AI evidence gap explainer for claim-readiness and audit-focused evidence planning</span>"
$oldEvidenceCall = "<EvidenceRegister records={evidenceRecords} summary={evidenceSummary} />"
$newEvidenceCall = @'
<EvidenceRegister
            records={evidenceRecords}
            summary={evidenceSummary}
            explanation={evidenceGapExplanation}
            onExplain={explainEvidenceGap}
            busy={busy}
          />
'@
if ($app.Contains($oldEvidenceCall)) { $app = $app.Replace($oldEvidenceCall, $newEvidenceCall) } elseif ($app -notmatch "onExplain=\{explainEvidenceGap\}") { throw "Could not patch EvidenceRegister props in App.jsx." }
Set-Content $appPath $app

$styles = Get-Content $stylesPath -Raw
if ($styles -notmatch "Milestone 8C: AI evidence gap explainer") {
  $cssToAdd = Get-Content (Join-Path $repoRoot "MILESTONE_8C_EVIDENCE_EXPLAINER_STYLES.css") -Raw
  Add-Content $stylesPath "`r`n$cssToAdd"
}
Write-Host "Milestone 8C AI evidence gap explainer patch applied."
Write-Host "Next: run pytest from backend and npm run build from frontend."
