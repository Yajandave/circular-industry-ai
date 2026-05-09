param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$schemasPath = Join-Path $repoRoot "backend\app\schemas.py"
$procurementRouterPath = Join-Path $repoRoot "backend\app\routers\procurement.py"
$clientPath = Join-Path $repoRoot "frontend\src\api\client.js"
$appPath = Join-Path $repoRoot "frontend\src\App.jsx"
$stylesPath = Join-Path $repoRoot "frontend\src\styles.css"
$supplierComponentPath = Join-Path $repoRoot "frontend\src\components\SupplierLoopIntelligence.jsx"

$required = @($schemasPath, $procurementRouterPath, $clientPath, $appPath, $stylesPath, $supplierComponentPath)
foreach ($path in $required) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from the circular-industry-ai repo root."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  foreach ($path in $required) {
    Copy-Item $path "$path.bak-$stamp"
  }
}

# 1. Append backend schema
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class SupplierEvidenceEmailDraft") {
  $schemaAppend = @'

# Milestone 8D: supplier evidence request drafting schemas

class SupplierEvidenceEmailDraft(BaseModel):
    generation_mode: str
    model_name: str
    stream_id: str
    stream_name: str
    supplier: str
    decision_lock_status: str
    draft_type: str
    subject: str
    email_body: str
    evidence_request_summary: list[str]
    attachments_or_documents_to_request: list[str]
    internal_follow_up_actions: list[str]
    claim_safety_note: str
    governance_note: str
    validation_warnings: list[str]
    locked_rule_applied: str | None = None
    locked_risk_level: str | None = None
    locked_human_review_required: bool | None = None
    locked_claim_readiness: str | None = None
    locked_procurement_route: str | None = None
    locked_review_gate: str | None = None
'@
  Add-Content $schemasPath $schemaAppend
}

# 2. Patch procurement router
$router = Get-Content $procurementRouterPath -Raw
if ($router -notmatch "generate_supplier_email_draft") {
  $router = $router.Replace(
    "from app.procurement.supplier_loop_engine import build_supplier_loop_plans, build_supplier_loop_summary",
    "from app.evidence_register import build_evidence_record`r`nfrom app.procurement.supplier_loop_engine import build_supplier_loop_plans, build_supplier_loop_summary`r`nfrom app.supplier_drafting.service import generate_supplier_email_draft"
  )
}

if ($router -notmatch "/procurement/supplier-loops/\{stream_id\}/email-draft") {
  $endpoint = @'

@router.post("/procurement/supplier-loops/{stream_id}/email-draft", response_model=schemas.SupplierEvidenceEmailDraft)
def draft_supplier_evidence_email(stream_id: str, db: Session = Depends(get_db)):
    """Draft a supplier evidence request email from locked supplier-loop and evidence data."""
    stream = crud.get_stream_by_stream_id(db, stream_id)
    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail=f"No stream found for stream ID {stream_id}.")
    if not recommendation:
        raise HTTPException(status_code=404, detail="No recommendation found. Run POST /api/recommendations/run first.")

    supplier_plan = None
    for plan in _require_supplier_loop_plans(db):
        if plan["stream_id"] == stream_id:
            supplier_plan = plan
            break

    if supplier_plan is None:
        raise HTTPException(status_code=404, detail=f"No supplier-loop plan found for stream ID {stream_id}.")

    evidence = build_evidence_record(stream, recommendation)
    return generate_supplier_email_draft(stream, recommendation, supplier_plan, evidence)

'@
  $anchor = '@router.get("/export/supplier-loop-plans.csv")'
  if ($router.Contains($anchor)) {
    $router = $router.Replace($anchor, $endpoint + $anchor)
  } else {
    Add-Content $procurementRouterPath $endpoint
  }
}
Set-Content $procurementRouterPath $router

# 3. Patch frontend API client
$client = Get-Content $clientPath -Raw
if ($client -notmatch "generateSupplierEmailDraft") {
  $anchor = "  supplierLoopSummary: () => request('/api/procurement/supplier-loops/summary'),"
  $replacement = "$anchor`r`n  generateSupplierEmailDraft: (streamId) => request(`/api/procurement/supplier-loops/${encodeURIComponent(streamId)}/email-draft`, { method: 'POST' }),"
  if ($client.Contains($anchor)) {
    $client = $client.Replace($anchor, $replacement)
  } else {
    throw "Could not find supplierLoopSummary anchor in frontend API client."
  }
  Set-Content $clientPath $client
}

# 4. Patch App state/function/props/hero
$app = Get-Content $appPath -Raw

if ($app -notmatch "supplierEmailDraft") {
  $stateAnchor = "  const [supplierLoopSummary, setSupplierLoopSummary] = useState(null);"
  $app = $app.Replace($stateAnchor, "$stateAnchor`r`n  const [supplierEmailDraft, setSupplierEmailDraft] = useState(null);")
}

$app = $app.Replace("      setSupplierLoopSummary(null);`r`n      setReviewPack(null);", "      setSupplierLoopSummary(null);`r`n      setSupplierEmailDraft(null);`r`n      setReviewPack(null);")
$app = $app.Replace("      setSupplierLoopSummary(null);`n      setReviewPack(null);", "      setSupplierLoopSummary(null);`n      setSupplierEmailDraft(null);`n      setReviewPack(null);")

if ($app -notmatch "draftSupplierEmail") {
  $functionAnchor = "  async function explainEvidenceGap(streamId) {"
  $newFunction = @'
  async function draftSupplierEmail(streamId) {
    await safeRun(`Supplier evidence request draft generated for ${streamId}.`, async () => {
      const result = await api.generateSupplierEmailDraft(streamId);
      setSupplierEmailDraft(result);
      setActiveView('supplier-loops');
      setTimeout(() => {
        document.getElementById('supplier-email-draft-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 50);
    });
  }

'@
  if ($app.Contains($functionAnchor)) {
    $app = $app.Replace($functionAnchor, $newFunction + $functionAnchor)
  } else {
    throw "Could not find explainEvidenceGap anchor in App.jsx."
  }
}

$app = $app -replace "<strong>Milestone [^<]+</strong>\s*<span>[^<]*</span>", "<strong>Milestone 8D</strong>`r`n          <span>AI supplier evidence request drafting from locked supplier-loop and evidence data</span>"

$oldSupplierCall = "<SupplierLoopIntelligence plans={supplierLoopPlans} summary={supplierLoopSummary} />"
$newSupplierCall = @'
<SupplierLoopIntelligence
            plans={supplierLoopPlans}
            summary={supplierLoopSummary}
            emailDraft={supplierEmailDraft}
            onDraftEmail={draftSupplierEmail}
            busy={busy}
          />
'@
if ($app.Contains($oldSupplierCall)) {
  $app = $app.Replace($oldSupplierCall, $newSupplierCall)
} elseif ($app -notmatch "onDraftEmail=\{draftSupplierEmail\}") {
  throw "Could not patch SupplierLoopIntelligence props in App.jsx."
}

Set-Content $appPath $app

# 5. Append CSS once
$styles = Get-Content $stylesPath -Raw
if ($styles -notmatch "Milestone 8D: supplier evidence request drafting") {
  $cssToAdd = Get-Content (Join-Path $repoRoot "MILESTONE_8D_SUPPLIER_DRAFTING_STYLES.css") -Raw
  Add-Content $stylesPath "`r`n$cssToAdd"
}

Write-Host "Milestone 8D supplier evidence request drafting patch applied."
Write-Host "Next: run pytest from backend and npm run build from frontend."
