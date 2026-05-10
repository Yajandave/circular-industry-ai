param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$appPath = Join-Path $repoRoot "frontend\src\App.jsx"
$clientPath = Join-Path $repoRoot "frontend\src\api\client.js"
$navPath = Join-Path $repoRoot "frontend\src\components\WorkflowNav.jsx"
$stylesPath = Join-Path $repoRoot "frontend\src\styles.css"
$noticePath = Join-Path $repoRoot "frontend\src\components\WorkflowPrerequisiteNotice.jsx"
$runtimePath = Join-Path $repoRoot "frontend\src\components\AIRuntimeStatus.jsx"

foreach ($path in @($appPath, $clientPath, $navPath, $stylesPath, $noticePath, $runtimePath)) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from repo root after extracting the zip."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  foreach ($path in @($appPath, $clientPath, $navPath, $stylesPath)) {
    Copy-Item $path "$path.bak-$stamp"
  }
}

# 1. Patch API client for AI runtime status if not already present.
$client = Get-Content $clientPath -Raw
if ($client -notmatch "aiRuntimeStatus") {
  $anchor = "  aiReasoningStatus: () => request('/api/ai-reasoning/status'),"
  if ($client.Contains($anchor)) {
    $client = $client.Replace($anchor, "$anchor`r`n  aiRuntimeStatus: () => request('/api/ai-runtime/status'),")
  } else {
    throw "Could not find aiReasoningStatus anchor in client.js."
  }
  Set-Content $clientPath $client
}

# 2. Patch App imports.
$app = Get-Content $appPath -Raw

if ($app -notmatch "AIRuntimeStatus") {
  $anchor = "import AIReasoningPanel from './components/AIReasoningPanel.jsx';"
  $app = $app.Replace($anchor, "$anchor`r`nimport AIRuntimeStatus from './components/AIRuntimeStatus.jsx';")
}

if ($app -notmatch "WorkflowPrerequisiteNotice") {
  $anchor = "import WorkflowNav from './components/WorkflowNav.jsx';"
  $app = $app.Replace($anchor, "$anchor`r`nimport WorkflowPrerequisiteNotice from './components/WorkflowPrerequisiteNotice.jsx';")
}

# 3. Add missing runtime/report state.
if ($app -notmatch "const \[aiRuntimeStatus, setAiRuntimeStatus\]") {
  $anchor = "  const [aiStatus, setAiStatus] = useState(null);"
  $app = $app.Replace($anchor, "$anchor`r`n  const [aiRuntimeStatus, setAiRuntimeStatus] = useState(null);")
}

if ($app -notmatch "const \[circularActionReport, setCircularActionReport\]") {
  $anchor = "  const [supplierEmailDraft, setSupplierEmailDraft] = useState(null);"
  $app = $app.Replace($anchor, "$anchor`r`n  const [circularActionReport, setCircularActionReport] = useState(null);")
}

# 4. Fetch AI runtime status during refresh.
if ($app -notmatch "api\.aiRuntimeStatus") {
  $app = $app.Replace(
    "      api.aiReasoningStatus().catch(() => null),",
    "      api.aiReasoningStatus().catch(() => null),`r`n      api.aiRuntimeStatus().catch(() => null),"
  )
  $app = $app.Replace(
    "aiMode, playbooks, playbookSummary",
    "aiMode, runtimeMode, playbooks, playbookSummary"
  )
  $app = $app.Replace(
    "    setAiStatus(aiMode);",
    "    setAiStatus(aiMode);`r`n    setAiRuntimeStatus(runtimeMode);"
  )
}

# 5. Clear stale outputs on recommendation rerun.
$runAnchor = "      await api.runRecommendations();"
$staleReset = @'
      setEvidenceGapExplanation(null);
      setSupplierEmailDraft(null);
      setCircularActionReport(null);
      setAiReasoning(null);
      setSiteCopilotSummary(null);
      setReviewPack(null);
'@
if ($app.Contains($runAnchor) -and $app -notmatch "setCircularActionReport\(null\);\s*setAiReasoning\(null\);\s*setSiteCopilotSummary\(null\);") {
  $app = $app.Replace($runAnchor, $staleReset + $runAnchor)
}

# 6. Update milestone label.
$app = $app -replace "<strong>Milestone [^<]+</strong>\s*<span>[^<]*</span>", "<strong>Milestone 9C</strong>`r`n          <span>Frontend workflow guardrails, stale-output control and AI runtime visibility</span>"

# 7. Show AI runtime status after summary cards.
$summaryAnchor = "      <SummaryCards streamSummary={streamSummary} recommendationSummary={recommendationSummary} agentSummary={agentSummary} />"
if ($app.Contains($summaryAnchor) -and $app -notmatch "<AIRuntimeStatus status=\{aiRuntimeStatus\}") {
  $app = $app.Replace($summaryAnchor, "$summaryAnchor`r`n      <AIRuntimeStatus status={aiRuntimeStatus} />")
}

# 8. Pass hasData to WorkflowNav.
$app = $app.Replace(
  "        reviewPack={reviewPack}`r`n      />",
  "        reviewPack={reviewPack}`r`n        hasData={streams.length > 0}`r`n      />"
)
$app = $app.Replace(
  "        reviewPack={reviewPack}`n      />",
  "        reviewPack={reviewPack}`n        hasData={streams.length > 0}`n      />"
)

# 9. Add basic guarded empty notice before active views when no downstream recommendations exist.
$guardBlock = @'
      {streams.length > 0 && recommendations.length === 0 && activeView !== 'dashboard' && activeView !== 'raw-data' && activeView !== 'recommendations' && (
        <WorkflowPrerequisiteNotice
          title="Run the locked rules engine first"
          message="This workflow depends on generated recommendations. Load data, run recommendations, then reopen this workflow."
          actions={[
            'Use Load sample dataset or upload a valid CSV.',
            'Click Run recommendations to generate locked decision records.',
            'Then open evidence, supplier loops, AI reasoning or reports.',
          ]}
        />
      )}

'@
$dashboardAnchor = "      {activeView === 'dashboard' && ("
if ($app.Contains($dashboardAnchor) -and $app -notmatch "Run the locked rules engine first") {
  $app = $app.Replace($dashboardAnchor, $guardBlock + $dashboardAnchor)
}

Set-Content $appPath $app

# 10. Append CSS.
$styles = Get-Content $stylesPath -Raw
if ($styles -notmatch "Milestone 9C: frontend workflow guardrails") {
  $cssToAdd = Get-Content (Join-Path $repoRoot "MILESTONE_9C_FRONTEND_GUARDRAILS_STYLES.css") -Raw
  Add-Content $stylesPath "`r`n$cssToAdd"
}

Write-Host "Milestone 9C frontend workflow guardrails patch applied."
Write-Host "Next: remove backups, run npm build, backend tests, and workflow verification."
