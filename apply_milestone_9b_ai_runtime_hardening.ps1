param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$schemasPath = Join-Path $repoRoot "backend\app\schemas.py"
$mainPath = Join-Path $repoRoot "backend\app\main.py"
$openaiClientPath = Join-Path $repoRoot "backend\app\llm_reasoning\openai_client.py"
$appPath = Join-Path $repoRoot "frontend\src\App.jsx"
$clientPath = Join-Path $repoRoot "frontend\src\api\client.js"
$stylesPath = Join-Path $repoRoot "frontend\src\styles.css"
$runtimeComponentPath = Join-Path $repoRoot "frontend\src\components\AIRuntimeStatus.jsx"

foreach ($path in @($schemasPath, $mainPath, $openaiClientPath, $appPath, $clientPath, $stylesPath, $runtimeComponentPath)) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from repo root after extracting the zip."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  foreach ($path in @($schemasPath, $mainPath, $openaiClientPath, $appPath, $clientPath, $stylesPath)) {
    Copy-Item $path "$path.bak-$stamp"
  }
}

# 1. Add configurable timeout helper to OpenAI/Gemini client.
$openai = Get-Content $openaiClientPath -Raw
if ($openai -notmatch "def llm_timeout_seconds") {
  $anchor = "def configured_base_url() -> str:"
  $helper = @'
def llm_timeout_seconds() -> int:
    """Return the configured LLM request timeout in seconds.

    Keep a bounded timeout so AI features cannot hang the product workflow.
    """
    raw_value = _env("LLM_TIMEOUT_SECONDS", "20") or "20"
    try:
        timeout = int(raw_value)
    except ValueError:
        timeout = 20
    return max(3, min(timeout, 60))


'@
  if ($openai.Contains($anchor)) {
    $openai = $openai.Replace($anchor, $helper + $anchor)
  } else {
    throw "Could not find configured_base_url anchor in openai_client.py."
  }
}

$openai = $openai.Replace("timeout=45", "timeout=llm_timeout_seconds()")
Set-Content $openaiClientPath $openai

# 2. Replace timeout=45 in other LLM clients and import helper.
$clientFiles = @(
  "backend\app\ai_copilot\llm_client.py",
  "backend\app\evidence_explainer\llm_client.py",
  "backend\app\supplier_drafting\llm_client.py",
  "backend\app\report_builder\llm_client.py"
)

foreach ($rel in $clientFiles) {
  $path = Join-Path $repoRoot $rel
  if (Test-Path $path) {
    $text = Get-Content $path -Raw
    $text = $text.Replace("timeout=45", "timeout=llm_timeout_seconds()")
    if ($text -notmatch "llm_timeout_seconds") {
      $text = $text.Replace("llm_provider,", "llm_provider,`r`n    llm_timeout_seconds,")
    }
    Set-Content $path $text
  }
}

# 3. Append backend schema.
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class AIRuntimeStatus") {
  $schemaAppend = @'

# Milestone 9B: AI runtime reliability schemas

class AIRuntimeStatus(BaseModel):
    ai_reasoning_enabled: bool
    llm_provider: str
    api_key_configured: bool
    configured_model: str
    configured_base_url: str
    timeout_seconds: int
    runtime_mode: str
    live_check_requested: bool
    live_check_status: str
    fallback_available: bool
    agentic_role: str
    guardrail_summary: str
    recommended_operator_action: str
'@
  Add-Content $schemasPath $schemaAppend
}

# 4. Mount ai_runtime router.
$lines = Get-Content $mainPath
$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )ai_runtime(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "ai_runtime"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}
$main = $patchedLines -join [Environment]::NewLine
if ($main -notmatch "app\.include_router\(ai_runtime\.router\)") {
  if ($main -match "app\.include_router\(ai_copilot\.router\)") {
    $main = $main.Replace("app.include_router(ai_copilot.router)", "app.include_router(ai_copilot.router)`r`napp.include_router(ai_runtime.router)")
  } else {
    $main += "`r`napp.include_router(ai_runtime.router)`r`n"
  }
}
Set-Content $mainPath $main

# 5. Patch frontend API client.
$client = Get-Content $clientPath -Raw
if ($client -notmatch "aiRuntimeStatus") {
  $anchor = "  aiReasoningStatus: () => request('/api/ai-reasoning/status'),"
  if ($client.Contains($anchor)) {
    $client = $client.Replace($anchor, "$anchor`r`n  aiRuntimeStatus: () => request('/api/ai-runtime/status'),")
  } else {
    throw "Could not find aiReasoningStatus API anchor."
  }
  Set-Content $clientPath $client
}

# 6. Patch frontend App import, state, refresh and display.
$app = Get-Content $appPath -Raw

if ($app -notmatch "AIRuntimeStatus") {
  $importAnchor = "import AIReasoningPanel from './components/AIReasoningPanel.jsx';"
  $app = $app.Replace($importAnchor, "$importAnchor`r`nimport AIRuntimeStatus from './components/AIRuntimeStatus.jsx';")
}

if ($app -notmatch "aiRuntimeStatus") {
  $stateAnchor = "  const [aiStatus, setAiStatus] = useState(null);"
  $app = $app.Replace($stateAnchor, "$stateAnchor`r`n  const [aiRuntimeStatus, setAiRuntimeStatus] = useState(null);")
}

if ($app -notmatch "const \[circularActionReport, setCircularActionReport\]") {
  $stateAnchor = "  const [supplierEmailDraft, setSupplierEmailDraft] = useState(null);"
  $app = $app.Replace($stateAnchor, "$stateAnchor`r`n  const [circularActionReport, setCircularActionReport] = useState(null);")
}

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

$app = $app -replace "<strong>Milestone [^<]+</strong>\s*<span>[^<]*</span>", "<strong>Milestone 9B</strong>`r`n          <span>AI runtime reliability, fallback visibility and agentic mode hardening</span>"

$displayAnchor = "      <SummaryCards streamSummary={streamSummary} recommendationSummary={recommendationSummary} agentSummary={agentSummary} />"
if ($app.Contains($displayAnchor) -and $app -notmatch "<AIRuntimeStatus status=\{aiRuntimeStatus\}") {
  $app = $app.Replace($displayAnchor, "$displayAnchor`r`n      <AIRuntimeStatus status={aiRuntimeStatus} />")
}

Set-Content $appPath $app

# 7. Append CSS.
$styles = Get-Content $stylesPath -Raw
if ($styles -notmatch "Milestone 9B: AI runtime reliability status") {
  $cssToAdd = Get-Content (Join-Path $repoRoot "MILESTONE_9B_AI_RUNTIME_STYLES.css") -Raw
  Add-Content $stylesPath "`r`n$cssToAdd"
}

Write-Host "Milestone 9B AI runtime hardening patch applied."
Write-Host "Next: remove backups, run backend pytest, frontend build, and workflow verification."
