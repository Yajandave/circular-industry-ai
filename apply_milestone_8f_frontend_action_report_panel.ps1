param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$clientPath = Join-Path $repoRoot "frontend\src\api\client.js"
$appPath = Join-Path $repoRoot "frontend\src\App.jsx"
$navPath = Join-Path $repoRoot "frontend\src\components\WorkflowNav.jsx"
$stylesPath = Join-Path $repoRoot "frontend\src\styles.css"
$componentPath = Join-Path $repoRoot "frontend\src\components\CircularActionReportPanel.jsx"

foreach ($path in @($clientPath, $appPath, $navPath, $stylesPath, $componentPath)) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from the circular-industry-ai repo root after extracting the zip."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  foreach ($path in @($clientPath, $appPath, $navPath, $stylesPath)) {
    Copy-Item $path "$path.bak-$stamp"
  }
}

# 1. Patch API client
$client = Get-Content $clientPath -Raw
if ($client -notmatch "generateCircularActionReport") {
  $anchor = "  generateSupplierEmailDraft: (streamId) => request(`/api/procurement/supplier-loops/${encodeURIComponent(streamId)}/email-draft`, { method: 'POST' }),"
  $newLine = '  generateCircularActionReport: (streamId) => request(`/api/reports/streams/${encodeURIComponent(streamId)}/circular-action-report`, { method: ''POST'' }),'
  if ($client.Contains($anchor)) {
    $client = $client.Replace($anchor, "$anchor`r`n$newLine")
  } else {
    $fallbackAnchor = "  siteAICopilotSummary: () => request('/api/ai-copilot/site-summary'),"
    if ($client.Contains($fallbackAnchor)) {
      $client = $client.Replace($fallbackAnchor, "$fallbackAnchor`r`n$newLine")
    } else {
      throw "Could not find a safe API client anchor."
    }
  }
  Set-Content $clientPath $client
}

# 2. Patch WorkflowNav tab
$nav = Get-Content $navPath -Raw
if ($nav -notmatch "id: 'action-report'") {
  $tab = @'
  {
    id: 'action-report',
    label: 'Action report',
    helper: 'Consultant-style circular action report for one selected stream',
  },
'@
  $anchor = "  {`r`n    id: 'raw-data',"
  if (!$nav.Contains($anchor)) {
    $anchor = "  {`n    id: 'raw-data',"
  }
  if ($nav.Contains($anchor)) {
    $nav = $nav.Replace($anchor, "$tab`r`n$anchor")
  } else {
    $nav = $nav.Replace("];", "$tab`r`n];")
  }
  Set-Content $navPath $nav
}

# 3. Patch App imports/state/function/view
$app = Get-Content $appPath -Raw

if ($app -notmatch "CircularActionReportPanel") {
  $importAnchor = "import CircularResolutionPlans from './components/CircularResolutionPlans.jsx';"
  $app = $app.Replace($importAnchor, "$importAnchor`r`nimport CircularActionReportPanel from './components/CircularActionReportPanel.jsx';")
}

if ($app -notmatch "circularActionReport") {
  $stateAnchor = "  const [supplierEmailDraft, setSupplierEmailDraft] = useState(null);"
  if ($app.Contains($stateAnchor)) {
    $app = $app.Replace($stateAnchor, "$stateAnchor`r`n  const [circularActionReport, setCircularActionReport] = useState(null);")
  } else {
    $fallbackStateAnchor = "  const [siteCopilotSummary, setSiteCopilotSummary] = useState(null);"
    $app = $app.Replace($fallbackStateAnchor, "$fallbackStateAnchor`r`n  const [circularActionReport, setCircularActionReport] = useState(null);")
  }
}

$app = $app.Replace("      setSupplierEmailDraft(null);`r`n      setReviewPack(null);", "      setSupplierEmailDraft(null);`r`n      setCircularActionReport(null);`r`n      setReviewPack(null);")
$app = $app.Replace("      setSupplierEmailDraft(null);`n      setReviewPack(null);", "      setSupplierEmailDraft(null);`n      setCircularActionReport(null);`n      setReviewPack(null);")

if ($app -notmatch "generateCircularActionReport") {
  $functionAnchor = "  async function draftSupplierEmail(streamId) {"
  $newFunction = @'
  async function generateCircularActionReport(streamId) {
    await safeRun(`Circular action report generated for ${streamId}.`, async () => {
      const result = await api.generateCircularActionReport(streamId);
      setCircularActionReport(result);
      setActiveView('action-report');
      setTimeout(() => {
        document.getElementById('circular-action-report')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 50);
    });
  }

'@
  if ($app.Contains($functionAnchor)) {
    $app = $app.Replace($functionAnchor, $newFunction + $functionAnchor)
  } else {
    $fallbackFunctionAnchor = "  async function refreshSiteCopilot() {"
    if ($app.Contains($fallbackFunctionAnchor)) {
      $app = $app.Replace($fallbackFunctionAnchor, $newFunction + $fallbackFunctionAnchor)
    } else {
      throw "Could not find a safe function anchor in App.jsx."
    }
  }
}

$app = $app -replace "<strong>Milestone [^<]+</strong>\s*<span>[^<]*</span>", "<strong>Milestone 8F</strong>`r`n          <span>Frontend circular action report panel with print-ready consultant-style output</span>"

if ($app -notmatch "activeView === 'action-report'") {
  $viewAnchor = "      {activeView === 'supplier-loops' && ("
  $newView = @'
      {activeView === 'action-report' && (
        <section className="workflow-panel action-report-view">
          <CircularActionReportPanel
            streams={streams}
            recommendations={recommendations}
            report={circularActionReport}
            onGenerate={generateCircularActionReport}
            busy={busy}
          />
        </section>
      )}

'@
  if ($app.Contains($viewAnchor)) {
    $app = $app.Replace($viewAnchor, $newView + $viewAnchor)
  } else {
    $fallbackViewAnchor = "      {activeView === 'evidence' && ("
    if ($app.Contains($fallbackViewAnchor)) {
      $app = $app.Replace($fallbackViewAnchor, $newView + $fallbackViewAnchor)
    } else {
      throw "Could not find a safe view anchor in App.jsx."
    }
  }
}

Set-Content $appPath $app

# 4. Append CSS once
$styles = Get-Content $stylesPath -Raw
if ($styles -notmatch "Milestone 8F: frontend circular action report panel") {
  $cssToAdd = Get-Content (Join-Path $repoRoot "MILESTONE_8F_ACTION_REPORT_STYLES.css") -Raw
  Add-Content $stylesPath "`r`n$cssToAdd"
}

Write-Host "Milestone 8F frontend circular action report panel patch applied."
Write-Host "Next: run npm run build from frontend."
