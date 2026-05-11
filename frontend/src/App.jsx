import { useEffect, useMemo, useState } from 'react';
import { api } from './api/client.js';
import ActionPlan from './components/ActionPlan.jsx';
import AIReasoningPanel from './components/AIReasoningPanel.jsx';
import AgenticIntelligencePanel from './components/AgenticIntelligencePanel.jsx';
import AIRuntimeStatus from './components/AIRuntimeStatus.jsx';
import Controls from './components/Controls.jsx';
import CircularResolutionPlans from './components/CircularResolutionPlans.jsx';
import CircularActionReportPanel from './components/CircularActionReportPanel.jsx';
import Dashboard from './components/Dashboard.jsx';
import DomainWorkspace from './components/DomainWorkspace.jsx';
import EvidenceRegister from './components/EvidenceRegister.jsx';
import FiltersPanel from './components/FiltersPanel.jsx';
import MaterialPlaybooks from './components/MaterialPlaybooks.jsx';
import PortfolioSnapshot from './components/PortfolioSnapshot.jsx';
import RecommendationsTable from './components/RecommendationsTable.jsx';
import ReviewPackPanel from './components/ReviewPackPanel.jsx';
import StatusPanel from './components/StatusPanel.jsx';
import SiteAICopilotPanel from './components/SiteAICopilotPanel.jsx';
import StreamsTable from './components/StreamsTable.jsx';
import SummaryCards from './components/SummaryCards.jsx';
import SupplierLoopIntelligence from './components/SupplierLoopIntelligence.jsx';
import WorkflowNav from './components/WorkflowNav.jsx';
import WorkflowPrerequisiteNotice from './components/WorkflowPrerequisiteNotice.jsx';
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


const DOMAIN_WORKSPACES = [
  {
    id: 'circular-core',
    label: 'Circular Core',
    eyebrow: 'Main system',
    helper: 'Industrial material-flow, waste/resource stream and circular procurement decision support.',
  },
  {
    id: 'esg',
    label: 'ESG',
    eyebrow: 'Supporting intelligence',
    helper: 'ESG score, evidence and sustainability performance context.',
  },
  {
    id: 'ghg-net-zero',
    label: 'GHG & Net Zero',
    eyebrow: 'Supporting intelligence',
    helper: 'Scope 1, 2 and 3 emissions, reduction opportunities and net zero readiness.',
  },
  {
    id: 'eia',
    label: 'EIA',
    eyebrow: 'Environmental Impact Assessment',
    helper: 'Environmental Impact Assessment issue, receptor, mitigation, residual-effect and evidence-gap intelligence.',
  },
  {
    id: 'greenwashing-claims',
    label: 'Greenwashing / Claims',
    eyebrow: 'Evidence control',
    helper: 'Sustainability claim screening, evidence sufficiency and safer wording routes.',
  },
  {
    id: 'supplier-procurement',
    label: 'Supplier & Procurement',
    eyebrow: 'Supporting intelligence',
    helper: 'Supplier sustainability, circular procurement and evidence-request intelligence.',
  },
  {
    id: 'data-profiler',
    label: 'Data Profiler',
    eyebrow: 'Fallback profiler',
    helper: 'Generic CSV profiling, column intelligence and recommended analysis route detection.',
  },
];

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

    const [loadedRecs, recSummary, mgmtSummary, plan, evidence, evSummary, resolutions, resSummary, aiMode, runtimeMode, playbooks, playbookSummary, supplierLoops, supplierLoopsSummary] = await Promise.all([
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
      await refreshData();
    });
  }

  async function uploadCsv(file) {
    if (!file) return;
    await safeRun(`Uploaded ${file.name}.`, async () => {
      await api.uploadCsv(file);
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
      await refreshData();
    });
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
      setTimeout(() => {
        document.getElementById('circular-action-report')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 50);
    });
  }
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
      setTimeout(() => {
        document.getElementById('ai-reasoning-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 50);
    });
  }

  async function openReviewPack(streamId) {
    await safeRun(`Review pack loaded for ${streamId}.`, async () => {
      const pack = await api.reviewPack(streamId);
      setReviewPack(pack);
      setActiveView('review');
      setTimeout(() => {
        document.getElementById('review-pack-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 50);
    });
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

  const activeDomainMeta = DOMAIN_WORKSPACES.find((domain) => domain.id === activeDomain) || DOMAIN_WORKSPACES[0];

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
              <span>{domain.eyebrow}</span>
              <strong>{domain.label}</strong>
            </button>
          ))}
        </div>
      </section>

      {activeDomain !== 'circular-core' && (
        <DomainWorkspace domain={activeDomainMeta} onBackToCore={() => setActiveDomain('circular-core')} />
      )}

      <section className={activeDomain === 'circular-core' ? 'domain-core-workflow' : 'domain-core-workflow hidden'}>
      <Controls
        onLoadSample={loadSample}
        onUploadCsv={uploadCsv}
        onRunRecommendations={runRecommendations}
        onRefresh={() => safeRun('View refreshed.', refreshData)}
        busy={busy}
      />
      <SummaryCards streamSummary={streamSummary} recommendationSummary={recommendationSummary} agentSummary={agentSummary} />
      <AIRuntimeStatus status={aiRuntimeStatus} />
      <WorkflowNav
        activeView={activeView}
        onChange={setActiveView}
        recommendationCount={recommendations.length}
        reviewPack={reviewPack}
        hasData={streams.length > 0}
      />

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
      {activeView === 'dashboard' && (
        <section className="workflow-panel dashboard-view">
          <Dashboard dashboardData={dashboardData} agentSummary={agentSummary} onSelectReviewPack={openReviewPack} />
          <PortfolioSnapshot dashboardData={dashboardData} agentSummary={agentSummary} />
        </section>
      )}

      {activeView === 'recommendations' && (
        <section className="workflow-panel recommendations-view">
          <FiltersPanel
            filters={filters}
            onChange={setFilters}
            materials={materials}
            strategies={strategies}
            priorities={priorities}
            resultCount={filteredRecommendations.length}
            totalCount={recommendations.length}
          />
          <RecommendationsTable recommendations={filteredRecommendations} onSelectReviewPack={openReviewPack} />
        </section>
      )}



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
      {activeView === 'ai-copilot' && (
        <section className="workflow-panel ai-copilot-view" id="site-ai-copilot-panel">
          <SiteAICopilotPanel
            summary={siteCopilotSummary}
            onRefresh={refreshSiteCopilot}
            busy={busy}
          />
        </section>
      )}
      {activeView === 'ai-reasoning' && (
        <section className="workflow-panel ai-reasoning-view" id="ai-reasoning-panel">
          <AIReasoningPanel
            plans={resolutionPlans}
            recommendations={recommendations}
            status={aiStatus}
            reasoning={aiReasoning}
            onGenerate={generateAiReasoning}
            busy={busy}
          />
        </section>
      )}

      {activeView === 'resolutions' && (
        <section className="workflow-panel resolution-view">
          <CircularResolutionPlans plans={resolutionPlans} summary={resolutionSummary} />
        </section>
      )}



      {activeView === 'playbooks' && (
        <section className="workflow-panel playbooks-view">
          <MaterialPlaybooks playbooks={materialPlaybooks} summary={materialPlaybookSummary} />
        </section>
      )}


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
      {activeView === 'supplier-loops' && (
        <section className="workflow-panel supplier-loops-view">
          <SupplierLoopIntelligence
            plans={supplierLoopPlans}
            summary={supplierLoopSummary}
            emailDraft={supplierEmailDraft}
            onDraftEmail={draftSupplierEmail}
            busy={busy}
          />
        </section>
      )}

      {activeView === 'review' && (
        <section className="workflow-panel review-view">
          <ReviewPackPanel reviewPack={reviewPack} />
        </section>
      )}

      {activeView === 'action-plan' && (
        <section className="workflow-panel action-view">
          <ActionPlan actionPlan={actionPlan} />
        </section>
      )}

      {activeView === 'evidence' && (
        <section className="workflow-panel evidence-view">
          <EvidenceRegister
            records={evidenceRecords}
            summary={evidenceSummary}
            explanation={evidenceGapExplanation}
            onExplain={explainEvidenceGap}
            busy={busy}
          />
        </section>
      )}

      {activeView === 'raw-data' && (
        <section className="workflow-panel raw-data-view">
          <StreamsTable streams={streams} />
        </section>
      )}
      </section>
    </main>
  );
}
