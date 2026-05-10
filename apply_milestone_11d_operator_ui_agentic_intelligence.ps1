$ErrorActionPreference = "Stop"

Write-Host "Applying Milestone 11D: Operator UI for Agentic Intelligence" -ForegroundColor Cyan

function Backup-File($Path) {
    if (Test-Path $Path) {
        $backup = "$Path.bak-11d-$(Get-Date -Format yyyyMMddHHmmss)"
        Copy-Item $Path $backup
        Write-Host "Backup created: $backup" -ForegroundColor DarkGray
    }
}

New-Item -ItemType Directory -Force -Path frontend\src\components | Out-Null
Copy-Item _milestone_11d_files\frontend\src\components\AgenticIntelligencePanel.jsx frontend\src\components\AgenticIntelligencePanel.jsx -Force
Copy-Item _milestone_11d_files\docs\milestone_11d_operator_ui_agentic_intelligence.md docs\milestone_11d_operator_ui_agentic_intelligence.md -Force

# Patch API client
Backup-File "frontend\src\api\client.js"
$client = Get-Content frontend\src\api\client.js -Raw
if ($client -notmatch "agenticRetrievalForStream") {
    $client = $client.Replace(
"  generateSupplierEmailDraft: (streamId) => request(`/api/procurement/supplier-loops/${encodeURIComponent(streamId)}/email-draft`, { method: 'POST' }),
};",
"  generateSupplierEmailDraft: (streamId) => request(`/api/procurement/supplier-loops/${encodeURIComponent(streamId)}/email-draft`, { method: 'POST' }),
  agenticRetrievalForStream: (streamId) => request(`/api/agentic-retrieval/stream/${encodeURIComponent(streamId)}`),
  agenticRetrievalRunAndSaveForStream: (streamId) => request(`/api/agentic-retrieval/stream/${encodeURIComponent(streamId)}/run-and-save`, { method: 'POST' }),
  insightHistory: (streamId) => request(`/api/insights/history/${encodeURIComponent(streamId)}`),
  evaluationSummary: () => request('/api/evaluation/summary'),
};"
    )
    Set-Content frontend\src\api\client.js $client
    Write-Host "Patched: frontend/src/api/client.js" -ForegroundColor Green
} else {
    Write-Host "Already patched: frontend/src/api/client.js" -ForegroundColor Yellow
}

# Patch WorkflowNav
Backup-File "frontend\src\components\WorkflowNav.jsx"
$nav = Get-Content frontend\src\components\WorkflowNav.jsx -Raw
if ($nav -notmatch "agentic-intelligence") {
    $anchor = @"
  {
    id: 'ai-copilot',
    label: 'AI Copilot',
    helper: 'Site-wide briefing for risk, evidence gaps, supplier actions and next steps',
    requiresData: true,
    requiresRecommendations: true,
  },
"@
    $insert = @"
  {
    id: 'agentic-intelligence',
    label: 'Agentic intelligence',
    helper: 'Workflow steps, graph path, saved insights and evaluation checks',
    requiresData: true,
    requiresRecommendations: false,
  },
  {
    id: 'ai-copilot',
    label: 'AI Copilot',
    helper: 'Site-wide briefing for risk, evidence gaps, supplier actions and next steps',
    requiresData: true,
    requiresRecommendations: true,
  },
"@
    $nav = $nav.Replace($anchor, $insert)
    Set-Content frontend\src\components\WorkflowNav.jsx $nav
    Write-Host "Patched: frontend/src/components/WorkflowNav.jsx" -ForegroundColor Green
} else {
    Write-Host "Already patched: frontend/src/components/WorkflowNav.jsx" -ForegroundColor Yellow
}

# Patch App.jsx
Backup-File "frontend\src\App.jsx"
$app = Get-Content frontend\src\App.jsx -Raw

if ($app -notmatch "AgenticIntelligencePanel") {
    $app = $app.Replace(
"import AIReasoningPanel from './components/AIReasoningPanel.jsx';",
"import AIReasoningPanel from './components/AIReasoningPanel.jsx';
import AgenticIntelligencePanel from './components/AgenticIntelligencePanel.jsx';"
    )

    $app = $app.Replace(
"  const [siteCopilotSummary, setSiteCopilotSummary] = useState(null);",
"  const [siteCopilotSummary, setSiteCopilotSummary] = useState(null);
  const [agenticWorkflow, setAgenticWorkflow] = useState(null);
  const [agenticInsightHistory, setAgenticInsightHistory] = useState([]);
  const [evaluationSummary, setEvaluationSummary] = useState(null);"
    )

    $app = $app.Replace(
"      setSiteCopilotSummary(null);
      setFilters(DEFAULT_FILTERS);",
"      setSiteCopilotSummary(null);
      setAgenticWorkflow(null);
      setAgenticInsightHistory([]);
      setEvaluationSummary(null);
      setFilters(DEFAULT_FILTERS);"
    )

    $app = $app.Replace(
"      setSiteCopilotSummary(null);
      setFilters(DEFAULT_FILTERS);",
"      setSiteCopilotSummary(null);
      setAgenticWorkflow(null);
      setAgenticInsightHistory([]);
      setEvaluationSummary(null);
      setFilters(DEFAULT_FILTERS);"
    )

    $app = $app.Replace(
"      setSiteCopilotSummary(null);
      setReviewPack(null);      await api.runRecommendations();",
"      setSiteCopilotSummary(null);
      setAgenticWorkflow(null);
      setAgenticInsightHistory([]);
      setEvaluationSummary(null);
      setReviewPack(null);
      await api.runRecommendations();"
    )

    $functions = @"

  async function runAgenticWorkflow(streamId) {
    await safeRun(`Agentic retrieval workflow generated for ${streamId}.`, async () => {
      const result = await api.agenticRetrievalForStream(streamId);
      setAgenticWorkflow(result);
      setActiveView('agentic-intelligence');
    });
  }

  async function runAndSaveAgenticWorkflow(streamId) {
    await safeRun(`Agentic workflow generated and saved for ${streamId}.`, async () => {
      const result = await api.agenticRetrievalRunAndSaveForStream(streamId);
      setAgenticWorkflow(result);
      const history = await api.insightHistory(streamId).catch(() => []);
      setAgenticInsightHistory(history);
      setActiveView('agentic-intelligence');
    });
  }

  async function loadAgenticInsightHistory(streamId) {
    await safeRun(`Insight history loaded for ${streamId}.`, async () => {
      const result = await api.insightHistory(streamId);
      setAgenticInsightHistory(result);
      setActiveView('agentic-intelligence');
    });
  }

  async function runEvaluationSummary() {
    await safeRun('Retrieval and insight evaluation summary refreshed.', async () => {
      const result = await api.evaluationSummary();
      setEvaluationSummary(result);
      setActiveView('agentic-intelligence');
    });
  }
"@

    $app = $app.Replace(
"  async function generateAiReasoning(streamId) {",
"$functions
  async function generateAiReasoning(streamId) {"
    )

    $renderBlock = @"

      {activeView === 'agentic-intelligence' && (
        <section className="workflow-panel agentic-intelligence-view">
          <AgenticIntelligencePanel
            streams={streams}
            workflow={agenticWorkflow}
            history={agenticInsightHistory}
            evaluation={evaluationSummary}
            onRunWorkflow={runAgenticWorkflow}
            onRunAndSaveWorkflow={runAndSaveAgenticWorkflow}
            onLoadHistory={loadAgenticInsightHistory}
            onRunEvaluation={runEvaluationSummary}
            busy={busy}
          />
        </section>
      )}
"@

    $app = $app.Replace(
"      {activeView === 'ai-copilot' && (",
"$renderBlock
      {activeView === 'ai-copilot' && ("
    )

    Set-Content frontend\src\App.jsx $app
    Write-Host "Patched: frontend/src/App.jsx" -ForegroundColor Green
} else {
    Write-Host "Already patched: frontend/src/App.jsx" -ForegroundColor Yellow
}

# Append styles
Backup-File "frontend\src\styles.css"
$styles = Get-Content frontend\src\styles.css -Raw
if ($styles -notmatch "agentic-panel") {
    Add-Content frontend\src\styles.css @'

/* Milestone 11D: operator UI for agentic intelligence */
.agentic-panel {
  margin-top: 22px;
  padding: 24px;
  border-radius: 24px;
  background: #ffffff;
  border: 1px solid #dfe7e2;
  box-shadow: 0 10px 30px rgba(36, 51, 44, 0.08);
}
.agentic-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: end;
  margin: 16px 0;
}
.agentic-toolbar label {
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: min(420px, 100%);
  color: #56675f;
  font-size: 0.9rem;
  font-weight: 800;
}
.agentic-selected-stream {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-radius: 18px;
  padding: 14px 16px;
  background: #f4f7f5;
  border: 1px solid #dfe7e2;
  margin-bottom: 16px;
}
.agentic-selected-stream span { color: #60716a; }
.agentic-metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin: 16px 0;
}
.agentic-metric-grid.compact { margin: 0 0 14px; }
.agentic-metric {
  border-radius: 18px;
  padding: 16px;
  background: #f5f8f6;
  border: 1px solid #dfe7e2;
}
.agentic-metric span {
  display: block;
  color: #60716a;
  font-weight: 800;
  font-size: 0.82rem;
}
.agentic-metric strong {
  display: block;
  margin: 7px 0 4px;
  font-size: 1.35rem;
  letter-spacing: -0.03em;
}
.agentic-metric small { color: #66766e; line-height: 1.35; }
.agentic-section {
  margin-top: 16px;
  border-radius: 22px;
  padding: 18px;
  background: #fbfdfb;
  border: 1px solid #dfe7e2;
}
.agentic-section h3 { margin: 0 0 12px; }
.agentic-step-list,
.agentic-gate-grid,
.agentic-insight-grid,
.agentic-case-list,
.agentic-history-list {
  display: grid;
  gap: 12px;
}
.agentic-step-list { grid-template-columns: repeat(5, minmax(0, 1fr)); }
.agentic-gate-grid,
.agentic-insight-grid,
.agentic-case-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.agentic-step-card,
.agentic-gate-card,
.agentic-insight-grid article,
.agentic-case-card,
.agentic-history-card,
.agentic-split article {
  border-radius: 18px;
  padding: 15px;
  background: #ffffff;
  border: 1px solid #dfe7e2;
}
.agentic-step-card h4,
.agentic-case-card h4,
.agentic-split h4,
.agentic-insight-grid h4 { margin: 0 0 8px; }
.agentic-step-card span {
  display: block;
  color: #60716a;
  font-weight: 800;
  font-size: 0.76rem;
  margin-bottom: 6px;
}
.agentic-step-card p,
.agentic-gate-card p,
.agentic-insight-grid p,
.agentic-case-card p,
.agentic-history-card p { color: #33443d; line-height: 1.5; }
.agentic-pill {
  display: inline-flex;
  width: fit-content;
  border-radius: 999px;
  padding: 5px 9px;
  font-size: 0.76rem;
  font-weight: 900;
  text-transform: capitalize;
  background: #eef3ef;
  color: #25513f;
}
.status-pass,
.status-completed,
.status-deterministic { background: #e4f4eb; color: #15613d; }
.status-review,
.status-skipped { background: #fff4dc; color: #7b4c00; }
.status-fail { background: #fbe5e2; color: #8f251d; }
.agentic-gate-card > div,
.agentic-case-card > div,
.agentic-history-card > div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: start;
}
.agentic-split,
.agentic-two-column {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.agentic-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid #e5ece8;
  padding: 8px 0;
}
.agentic-row span { color: #53645d; text-transform: capitalize; }
.agentic-row strong { color: #1f5b43; }
.agentic-graph-view ol { margin: 0; padding-left: 20px; line-height: 1.55; }

@media (max-width: 1180px) {
  .agentic-metric-grid,
  .agentic-step-list,
  .agentic-gate-grid,
  .agentic-insight-grid,
  .agentic-case-list,
  .agentic-split,
  .agentic-two-column {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 680px) {
  .agentic-metric-grid,
  .agentic-step-list,
  .agentic-gate-grid,
  .agentic-insight-grid,
  .agentic-case-list,
  .agentic-split,
  .agentic-two-column {
    grid-template-columns: 1fr;
  }
  .agentic-toolbar { align-items: stretch; flex-direction: column; }
}
'@
    Write-Host "Patched: frontend/src/styles.css" -ForegroundColor Green
} else {
    Write-Host "Already patched: frontend/src/styles.css" -ForegroundColor Yellow
}

Write-Host "Milestone 11D applied." -ForegroundColor Green
Write-Host "Run backend pytest and frontend npm build before commit." -ForegroundColor Cyan
