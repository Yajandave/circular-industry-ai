import { useEffect, useMemo, useState } from 'react';
import { api } from './api/client.js';
import ActionPlan from './components/ActionPlan.jsx';
import AIReasoningPanel from './components/AIReasoningPanel.jsx';
import Controls from './components/Controls.jsx';
import CircularResolutionPlans from './components/CircularResolutionPlans.jsx';
import Dashboard from './components/Dashboard.jsx';
import EvidenceRegister from './components/EvidenceRegister.jsx';
import FiltersPanel from './components/FiltersPanel.jsx';
import PortfolioSnapshot from './components/PortfolioSnapshot.jsx';
import RecommendationsTable from './components/RecommendationsTable.jsx';
import ReviewPackPanel from './components/ReviewPackPanel.jsx';
import StatusPanel from './components/StatusPanel.jsx';
import StreamsTable from './components/StreamsTable.jsx';
import SummaryCards from './components/SummaryCards.jsx';
import WorkflowNav from './components/WorkflowNav.jsx';
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
  const [resolutionPlans, setResolutionPlans] = useState([]);
  const [resolutionSummary, setResolutionSummary] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [aiReasoning, setAiReasoning] = useState(null);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [activeView, setActiveView] = useState('dashboard');

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

    const [loadedRecs, recSummary, mgmtSummary, plan, evidence, evSummary, resolutions, resSummary, aiMode] = await Promise.all([
      api.listRecommendations().catch(() => []),
      api.recommendationSummary().catch(() => null),
      api.managementSummary().catch(() => null),
      api.actionPlan(12).catch(() => null),
      api.evidenceRegister().catch(() => []),
      api.evidenceSummary().catch(() => null),
      api.resolutionPlans().catch(() => []),
      api.resolutionSummary().catch(() => null),
      api.aiReasoningStatus().catch(() => null),
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
      setResolutionPlans([]);
      setResolutionSummary(null);
      setReviewPack(null);
      setAiReasoning(null);
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
      setResolutionPlans([]);
      setResolutionSummary(null);
      setReviewPack(null);
      setAiReasoning(null);
      setFilters(DEFAULT_FILTERS);
      setActiveView('dashboard');
      await refreshData();
    });
  }

  async function runRecommendations() {
    await safeRun('Rules engine, dashboard metrics and agentic portfolio outputs refreshed.', async () => {
      await api.runRecommendations();
      await api.runResolutions().catch(() => null);
      await refreshData();
      setActiveView('dashboard');
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
          <strong>Milestone 7C</strong>
          <span>Rules-locked LLM reasoning layer and table-formatting QA</span>
        </div>
      </header>

      <StatusPanel status={backendStatus} message={message} error={error} />
      <Controls
        onLoadSample={loadSample}
        onUploadCsv={uploadCsv}
        onRunRecommendations={runRecommendations}
        onRefresh={() => safeRun('View refreshed.', refreshData)}
        busy={busy}
      />
      <SummaryCards streamSummary={streamSummary} recommendationSummary={recommendationSummary} agentSummary={agentSummary} />
      <WorkflowNav
        activeView={activeView}
        onChange={setActiveView}
        recommendationCount={recommendations.length}
        reviewPack={reviewPack}
      />

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
          <EvidenceRegister records={evidenceRecords} summary={evidenceSummary} />
        </section>
      )}

      {activeView === 'raw-data' && (
        <section className="workflow-panel raw-data-view">
          <StreamsTable streams={streams} />
        </section>
      )}
    </main>
  );
}
