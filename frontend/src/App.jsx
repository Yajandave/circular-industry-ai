import { useEffect, useMemo, useState } from 'react';
import { api } from './api/client.js';
import CircularCoreWorkspace from './components/CircularCoreWorkspace.jsx';
import DomainWorkspace from './components/DomainWorkspace.jsx';
import StatusPanel from './components/StatusPanel.jsx';
import { DOMAIN_WORKSPACES, getDomainWorkspaceMeta } from './config/domainWorkspaces.js';
import { applyRecommendationFilters, buildDashboardData, sortRecommendations } from './utils/analytics.js';

const DEFAULT_FILTERS = {
  search: '',
  material: 'all',
  risk: 'all',
  strategy: 'all',
  review: 'all',
  priority: 'all',
  minConfidence: 0,
  minEvidence: 0,
  sortBy: 'priority',
};

export default function App() {
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [streams, setStreams] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [streamSummary, setStreamSummary] = useState(null);
  const [recommendationSummary, setRecommendationSummary] = useState(null);
  const [agentSummary, setAgentSummary] = useState(null);
  const [actionPlan, setActionPlan] = useState(null);
  const [reviewPack, setReviewPack] = useState(null);
  const [evidenceRecords, setEvidenceRecords] = useState([]);
  const [evidenceSummary, setEvidenceSummary] = useState(null);
  const [evidenceGapExplanation, setEvidenceGapExplanation] = useState(null);
  const [resolutionPlans, setResolutionPlans] = useState([]);
  const [resolutionSummary, setResolutionSummary] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [aiRuntimeStatus, setAiRuntimeStatus] = useState(null);
  const [aiReasoning, setAiReasoning] = useState(null);
  const [siteCopilotSummary, setSiteCopilotSummary] = useState(null);
  const [agenticWorkflow, setAgenticWorkflow] = useState(null);
  const [agenticInsightHistory, setAgenticInsightHistory] = useState([]);
  const [evaluationSummary, setEvaluationSummary] = useState(null);
  const [materialPlaybooks, setMaterialPlaybooks] = useState([]);
  const [materialPlaybookSummary, setMaterialPlaybookSummary] = useState(null);
  const [supplierLoopPlans, setSupplierLoopPlans] = useState([]);
  const [supplierLoopSummary, setSupplierLoopSummary] = useState(null);
  const [supplierEmailDraft, setSupplierEmailDraft] = useState(null);
  const [circularActionReport, setCircularActionReport] = useState(null);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [activeView, setActiveView] = useState('dashboard');
  const [activeDomain, setActiveDomain] = useState('circular-core');

  async function safeRun(label, task) {
    setBusy(true);
    setError('');
    setMessage('');
    try {
      const result = await task();
      setMessage(label);
      return result;
    } catch (err) {
      setError(err.message || 'Something went wrong.');
      throw err;
    } finally {
      setBusy(false);
    }
  }

  async function refreshData() {
    const [loadedStreams, loadedStreamSummary] = await Promise.all([
      api.listStreams().catch(() => []),
      api.streamSummary().catch(() => null),
    ]);
    setStreams(loadedStreams);
    setStreamSummary(loadedStreamSummary);

    const [
      loadedRecs,
      recSummary,
      mgmtSummary,
      plan,
      evidence,
      evSummary,
      resolutions,
      resSummary,
      aiMode,
      runtimeMode,
      playbooks,
      playbookSummary,
      supplierLoops,
      supplierLoopsSummary,
    ] = await Promise.all([
      api.listRecommendations().catch(() => []),
      api.recommendationSummary().catch(() => null),
      api.managementSummary().catch(() => null),
      api.actionPlan(12).catch(() => null),
      api.evidenceRegister().catch(() => []),
      api.evidenceSummary().catch(() => null),
      api.resolutionPlans().catch(() => []),
      api.resolutionSummary().catch(() => null),
      api.aiReasoningStatus().catch(() => null),
      api.aiRuntimeStatus().catch(() => null),
      api.materialPlaybooks().catch(() => []),
      api.materialPlaybookSummary().catch(() => null),
      api.supplierLoopPlans().catch(() => []),
      api.supplierLoopSummary().catch(() => null),
    ]);
    setRecommendations(loadedRecs);
    setRecommendationSummary(recSummary);
    setAgentSummary(mgmtSummary);
    setActionPlan(plan);
    setEvidenceRecords(evidence);
    setEvidenceSummary(evSummary);
    setResolutionPlans(resolutions);
    setResolutionSummary(resSummary);
    setAiStatus(aiMode);
    setAiRuntimeStatus(runtimeMode);
    setMaterialPlaybooks(playbooks);
    setMaterialPlaybookSummary(playbookSummary);
    setSupplierLoopPlans(supplierLoops);
    setSupplierLoopSummary(supplierLoopsSummary);
  }

  async function loadSample() {
    await safeRun('Sample industrial stream dataset loaded.', async () => {
      await api.loadSample();
      resetGeneratedOutputs();
      await refreshData();
    });
  }

  async function uploadCsv(file) {
    if (!file) return;
    await safeRun(`Uploaded ${file.name}.`, async () => {
      await api.uploadCsv(file);
      resetGeneratedOutputs();
      await refreshData();
    });
  }

  function resetGeneratedOutputs() {
    setRecommendations([]);
    setRecommendationSummary(null);
    setAgentSummary(null);
    setActionPlan(null);
    setEvidenceRecords([]);
    setEvidenceSummary(null);
    setEvidenceGapExplanation(null);
    setResolutionPlans([]);
    setResolutionSummary(null);
    setSupplierLoopPlans([]);
    setSupplierLoopSummary(null);
    setSupplierEmailDraft(null);
    setCircularActionReport(null);
    setReviewPack(null);
    setAiReasoning(null);
    setSiteCopilotSummary(null);
    setAgenticWorkflow(null);
    setAgenticInsightHistory([]);
    setEvaluationSummary(null);
    setFilters(DEFAULT_FILTERS);
    setActiveView('dashboard');
  }

  async function runRecommendations() {
    await safeRun('Rules engine, dashboard metrics and operational intelligence outputs refreshed.', async () => {
      setEvidenceGapExplanation(null);
      setSupplierEmailDraft(null);
      setCircularActionReport(null);
      setAiReasoning(null);
      setSiteCopilotSummary(null);
      setAgenticWorkflow(null);
      setAgenticInsightHistory([]);
      setEvaluationSummary(null);
      setReviewPack(null);
      await api.runRecommendations();
      await api.runResolutions().catch(() => null);
      await api.runSupplierLoops().catch(() => null);
      await refreshData();
      setActiveView('dashboard');
    });
  }

  async function generateCircularActionReport(streamId) {
    await safeRun(`Circular action report generated for ${streamId}.`, async () => {
      const result = await api.generateCircularActionReport(streamId);
      setCircularActionReport(result);
      setActiveView('action-report');
      scrollToPanel('circular-action-report');
    });
  }

  async function draftSupplierEmail(streamId) {
    await safeRun(`Supplier evidence request draft generated for ${streamId}.`, async () => {
      const result = await api.generateSupplierEmailDraft(streamId);
      setSupplierEmailDraft(result);
      setActiveView('supplier-loops');
      scrollToPanel('supplier-email-draft-panel');
    });
  }

  async function explainEvidenceGap(streamId) {
    await safeRun(`AI evidence gap explanation generated for ${streamId}.`, async () => {
      const result = await api.generateEvidenceGapExplanation(streamId);
      setEvidenceGapExplanation(result);
      setActiveView('evidence');
      scrollToPanel('evidence-gap-explainer');
    });
  }

  async function refreshSiteCopilot() {
    await safeRun('Site-wide AI copilot summary refreshed.', async () => {
      const result = await api.siteAICopilotSummary();
      setSiteCopilotSummary(result);
      setActiveView('ai-copilot');
    });
  }

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

  async function generateAiReasoning(streamId) {
    await safeRun(`AI reasoning generated for ${streamId}.`, async () => {
      const result = await api.generateAiReasoning(streamId);
      setAiReasoning(result);
      setActiveView('ai-reasoning');
      scrollToPanel('ai-reasoning-panel');
    });
  }

  async function openReviewPack(streamId) {
    await safeRun(`Review pack loaded for ${streamId}.`, async () => {
      const pack = await api.reviewPack(streamId);
      setReviewPack(pack);
      setActiveView('review');
      scrollToPanel('review-pack-panel');
    });
  }

  function scrollToPanel(elementId) {
    setTimeout(() => {
      document.getElementById(elementId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }

  useEffect(() => {
    async function initialise() {
      try {
        await api.health();
        setBackendStatus('ok');
        await refreshData();
      } catch {
        setBackendStatus('warn');
      }
    }
    initialise();
  }, []);

  const dashboardData = useMemo(() => buildDashboardData(recommendations, streams), [recommendations, streams]);

  const materials = useMemo(() => {
    const unique = new Set(streams.map((stream) => stream.material).filter(Boolean));
    return ['all', ...Array.from(unique).sort()];
  }, [streams]);

  const strategies = useMemo(() => {
    const unique = new Set(recommendations.map((rec) => rec.circular_strategy_category).filter(Boolean));
    return ['all', ...Array.from(unique).sort()];
  }, [recommendations]);

  const priorities = useMemo(() => {
    const unique = new Set(dashboardData.enriched.map((rec) => rec.priority_band).filter(Boolean));
    return ['all', ...Array.from(unique).sort()];
  }, [dashboardData.enriched]);

  const filteredRecommendations = useMemo(() => {
    const filtered = applyRecommendationFilters(dashboardData.enriched, filters);
    return sortRecommendations(filtered, filters.sortBy);
  }, [dashboardData.enriched, filters]);

  const activeDomainMeta = useMemo(() => getDomainWorkspaceMeta(activeDomain), [activeDomain]);

  const coreWorkspaceProps = {
    busy,
    streams,
    recommendations,
    streamSummary,
    recommendationSummary,
    agentSummary,
    actionPlan,
    reviewPack,
    evidenceRecords,
    evidenceSummary,
    evidenceGapExplanation,
    resolutionPlans,
    resolutionSummary,
    aiStatus,
    aiRuntimeStatus,
    aiReasoning,
    siteCopilotSummary,
    agenticWorkflow,
    agenticInsightHistory,
    evaluationSummary,
    materialPlaybooks,
    materialPlaybookSummary,
    supplierLoopPlans,
    supplierLoopSummary,
    supplierEmailDraft,
    circularActionReport,
    filters,
    activeView,
    dashboardData,
    materials,
    strategies,
    priorities,
    filteredRecommendations,
    onLoadSample: loadSample,
    onUploadCsv: uploadCsv,
    onRunRecommendations: runRecommendations,
    onRefresh: () => safeRun('View refreshed.', refreshData),
    onViewChange: setActiveView,
    onFiltersChange: setFilters,
    onSelectReviewPack: openReviewPack,
    onGenerateCircularActionReport: generateCircularActionReport,
    onDraftSupplierEmail: draftSupplierEmail,
    onExplainEvidenceGap: explainEvidenceGap,
    onRefreshSiteCopilot: refreshSiteCopilot,
    onRunAgenticWorkflow: runAgenticWorkflow,
    onRunAndSaveAgenticWorkflow: runAndSaveAgenticWorkflow,
    onLoadAgenticInsightHistory: loadAgenticInsightHistory,
    onRunEvaluationSummary: runEvaluationSummary,
    onGenerateAiReasoning: generateAiReasoning,
  };

  return (
    <main>
      <header className="hero">
        <div>
          <span className="eyebrow">Industrial circular economy decision support</span>
          <h1>Circular Industry AI</h1>
          <p>
            A controlled agentic system for material-flow screening, by-product valorisation, circular procurement and
            evidence-led action planning. The rules engine remains the locked decision source.
          </p>
        </div>
        <div className="hero-note">
          <strong>Operational intelligence layer</strong>
          <span>Rules-locked screening, knowledge retrieval, autonomous insights and evidence-controlled action planning</span>
        </div>
      </header>

      <StatusPanel status={backendStatus} message={message} error={error} />

      <section className="domain-workspace-shell" aria-label="Circular Industry AI domain workspaces">
        <div className="section-heading compact-heading">
          <div>
            <h2>Domain workspaces</h2>
            <p>
              Circular Core remains the main industrial circular economy workflow. ESG, GHG, EIA, claims,
              supplier and data-profiler workspaces support adjacent professional intelligence without replacing the core system.
            </p>
          </div>
          <span>{activeDomainMeta.eyebrow}</span>
        </div>
        <div className="domain-workspace-bar" role="tablist" aria-label="Professional sustainability domains">
          {DOMAIN_WORKSPACES.map((domain) => (
            <button
              key={domain.id}
              type="button"
              className={`domain-workspace-tab ${activeDomain === domain.id ? 'active' : ''}`}
              onClick={() => setActiveDomain(domain.id)}
              role="tab"
              aria-selected={activeDomain === domain.id}
              title={domain.helper}
            >
              <strong>{domain.label}</strong>
            </button>
          ))}
        </div>
      </section>

      {activeDomain === 'circular-core' ? (
        <CircularCoreWorkspace {...coreWorkspaceProps} />
      ) : (
        <DomainWorkspace domain={activeDomainMeta} onBackToCore={() => setActiveDomain('circular-core')} />
      )}
    </main>
  );
}
