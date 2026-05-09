param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"

$repoRoot = Get-Location
$appPath = Join-Path $repoRoot "frontend\src\App.jsx"
$clientPath = Join-Path $repoRoot "frontend\src\api\client.js"
$navPath = Join-Path $repoRoot "frontend\src\components\WorkflowNav.jsx"
$stylesPath = Join-Path $repoRoot "frontend\src\styles.css"
$componentSource = Join-Path $repoRoot "frontend\src\components\SiteAICopilotPanel.jsx"

if (!(Test-Path $appPath) -or !(Test-Path $clientPath) -or !(Test-Path $navPath) -or !(Test-Path $stylesPath) -or !(Test-Path $componentSource)) {
  throw "Run this script from the circular-industry-ai repo root after extracting the zip."
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  Copy-Item $appPath "$appPath.bak-$stamp"
  Copy-Item $clientPath "$clientPath.bak-$stamp"
  Copy-Item $navPath "$navPath.bak-$stamp"
  Copy-Item $stylesPath "$stylesPath.bak-$stamp"
}

function Replace-First {
  param(
    [string]$Text,
    [string]$Old,
    [string]$New
  )
  $index = $Text.IndexOf($Old)
  if ($index -lt 0) {
    return $Text
  }
  return $Text.Substring(0, $index) + $New + $Text.Substring($index + $Old.Length)
}

# 1. Add API method safely.
$client = Get-Content $clientPath -Raw
if ($client -notmatch "siteAICopilotSummary") {
  $anchor = "  materialPlaybookSummary: () => request('/api/playbooks/summary'),"
  $replacement = "$anchor`r`n  siteAICopilotSummary: () => request('/api/ai-copilot/site-summary'),"
  if ($client.Contains($anchor)) {
    $client = $client.Replace($anchor, $replacement)
  } else {
    $client = $client -replace "};\s*\r?\n\r?\nexport \{ API_BASE_URL \};", "  siteAICopilotSummary: () => request('/api/ai-copilot/site-summary'),`r`n};`r`n`r`nexport { API_BASE_URL };"
  }
  Set-Content $clientPath $client
}

# 2. Add workflow tab safely.
$nav = Get-Content $navPath -Raw
if ($nav -notmatch "id: 'ai-copilot'") {
  $anchor = "  {`r`n    id: 'ai-reasoning',"
  if (!$nav.Contains($anchor)) {
    $anchor = "  {`n    id: 'ai-reasoning',"
  }
  $tab = "  {`r`n    id: 'ai-copilot',`r`n    label: 'AI Copilot',`r`n    helper: 'Site-wide briefing for risk, evidence gaps, supplier actions and next steps',`r`n  },`r`n"
  if ($nav.Contains($anchor)) {
    $nav = Replace-First $nav $anchor ($tab + $anchor)
  } else {
    $nav = $nav -replace "\];", "$tab];"
  }
  Set-Content $navPath $nav
}

# 3. Patch App.jsx imports, state, refresh, view and milestone label.
$app = Get-Content $appPath -Raw

if ($app -notmatch "SiteAICopilotPanel") {
  $importAnchor = "import StatusPanel from './components/StatusPanel.jsx';"
  $app = $app.Replace($importAnchor, "$importAnchor`r`nimport SiteAICopilotPanel from './components/SiteAICopilotPanel.jsx';")
}

if ($app -notmatch "siteCopilotSummary") {
  $stateAnchor = "  const [aiReasoning, setAiReasoning] = useState(null);"
  $app = $app.Replace($stateAnchor, "$stateAnchor`r`n  const [siteCopilotSummary, setSiteCopilotSummary] = useState(null);")
}

if ($app -notmatch "refreshSiteCopilot") {
  $functionAnchor = "  async function generateAiReasoning(streamId) {"
  $newFunction = @"
  async function refreshSiteCopilot() {
    await safeRun('Site-wide AI copilot summary refreshed.', async () => {
      const result = await api.siteAICopilotSummary();
      setSiteCopilotSummary(result);
      setActiveView('ai-copilot');
    });
  }

"@
  $app = $app.Replace($functionAnchor, $newFunction + $functionAnchor)
}

if ($app -notmatch "api.siteAICopilotSummary") {
  Write-Host "Warning: refreshSiteCopilot function could not be added cleanly."
}

# Reset copilot summary when loading new data.
$app = $app.Replace("      setAiReasoning(null);`r`n      setFilters(DEFAULT_FILTERS);", "      setAiReasoning(null);`r`n      setSiteCopilotSummary(null);`r`n      setFilters(DEFAULT_FILTERS);")
$app = $app.Replace("      setAiReasoning(null);`n      setFilters(DEFAULT_FILTERS);", "      setAiReasoning(null);`n      setSiteCopilotSummary(null);`n      setFilters(DEFAULT_FILTERS);")

# Update hero note without relying on exact previous milestone text.
$app = $app -replace "<strong>Milestone [^<]+</strong>\s*<span>[^<]*</span>", "<strong>Milestone 8B</strong>`r`n          <span>Site-wide AI copilot panel connected to the locked backend summary endpoint</span>"

# Add AI copilot view before AI reasoning view.
if ($app -notmatch "activeView === 'ai-copilot'") {
  $viewAnchor = "      {activeView === 'ai-reasoning' && ("
  $newView = @"
      {activeView === 'ai-copilot' && (
        <section className="workflow-panel ai-copilot-view" id="site-ai-copilot-panel">
          <SiteAICopilotPanel
            summary={siteCopilotSummary}
            onRefresh={refreshSiteCopilot}
            busy={busy}
          />
        </section>
      )}

"@
  if ($app.Contains($viewAnchor)) {
    $app = $app.Replace($viewAnchor, $newView + $viewAnchor)
  } else {
    throw "Could not find AI reasoning view anchor in App.jsx."
  }
}

Set-Content $appPath $app

# 4. Append CSS once.
$styles = Get-Content $stylesPath -Raw
if ($styles -notmatch "Milestone 8B: Site-wide AI Copilot panel") {
  $cssToAdd = Get-Content (Join-Path $repoRoot "MILESTONE_8B_COPILOT_STYLES.css") -Raw
  Add-Content $stylesPath "`r`n$cssToAdd"
}

Write-Host "Milestone 8B frontend AI copilot panel patch applied."
Write-Host "Next: npm run build from frontend, then start the app and open the AI Copilot tab."
