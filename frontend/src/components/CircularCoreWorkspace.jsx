import ActionPlan from './ActionPlan.jsx';
import AIReasoningPanel from './AIReasoningPanel.jsx';
import AgenticIntelligencePanel from './AgenticIntelligencePanel.jsx';
import AIRuntimeStatus from './AIRuntimeStatus.jsx';
import CircularActionReportPanel from './CircularActionReportPanel.jsx';
import CircularResolutionPlans from './CircularResolutionPlans.jsx';
import Controls from './Controls.jsx';
import Dashboard from './Dashboard.jsx';
import EvidenceRegister from './EvidenceRegister.jsx';
import FiltersPanel from './FiltersPanel.jsx';
import MaterialPlaybooks from './MaterialPlaybooks.jsx';
import PortfolioSnapshot from './PortfolioSnapshot.jsx';
import RecommendationsTable from './RecommendationsTable.jsx';
import ReviewPackPanel from './ReviewPackPanel.jsx';
import SiteAICopilotPanel from './SiteAICopilotPanel.jsx';
import StreamsTable from './StreamsTable.jsx';
import SummaryCards from './SummaryCards.jsx';
import SupplierLoopIntelligence from './SupplierLoopIntelligence.jsx';
import WorkflowNav from './WorkflowNav.jsx';
import WorkflowPrerequisiteNotice from './WorkflowPrerequisiteNotice.jsx';

const PREREQUISITE_FREE_VIEWS = ['dashboard', 'raw-data', 'recommendations'];

export default function CircularCoreWorkspace({
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
  onLoadSample,
  onUploadCsv,
  onRunRecommendations,
  onRefresh,
  onViewChange,
  onFiltersChange,
  onSelectReviewPack,
  onGenerateCircularActionReport,
  onDraftSupplierEmail,
  onExplainEvidenceGap,
  onRefreshSiteCopilot,
  onRunAgenticWorkflow,
  onRunAndSaveAgenticWorkflow,
  onLoadAgenticInsightHistory,
  onRunEvaluationSummary,
  onGenerateAiReasoning,
}) {
  const needsRecommendationNotice = (
    streams.length > 0 &&
    recommendations.length === 0 &&
    !PREREQUISITE_FREE_VIEWS.includes(activeView)
  );

  return (
    <section className="domain-core-workflow">
      <Controls
        onLoadSample={onLoadSample}
        onUploadCsv={onUploadCsv}
        onRunRecommendations={onRunRecommendations}
        onRefresh={onRefresh}
        busy={busy}
      />
      <SummaryCards streamSummary={streamSummary} recommendationSummary={recommendationSummary} agentSummary={agentSummary} />
      <AIRuntimeStatus status={aiRuntimeStatus} />
      <WorkflowNav
        activeView={activeView}
        onChange={onViewChange}
        recommendationCount={recommendations.length}
        reviewPack={reviewPack}
        hasData={streams.length > 0}
      />

      {needsRecommendationNotice && (
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
          <Dashboard dashboardData={dashboardData} agentSummary={agentSummary} onSelectReviewPack={onSelectReviewPack} />
          <PortfolioSnapshot dashboardData={dashboardData} agentSummary={agentSummary} />
        </section>
      )}

      {activeView === 'recommendations' && (
        <section className="workflow-panel recommendations-view">
          <FiltersPanel
            filters={filters}
            onChange={onFiltersChange}
            materials={materials}
            strategies={strategies}
            priorities={priorities}
            resultCount={filteredRecommendations.length}
            totalCount={recommendations.length}
          />
          <RecommendationsTable recommendations={filteredRecommendations} onSelectReviewPack={onSelectReviewPack} />
        </section>
      )}

      {activeView === 'agentic-intelligence' && (
        <section className="workflow-panel agentic-intelligence-view">
          <AgenticIntelligencePanel
            streams={streams}
            workflow={agenticWorkflow}
            history={agenticInsightHistory}
            evaluation={evaluationSummary}
            onRunWorkflow={onRunAgenticWorkflow}
            onRunAndSaveWorkflow={onRunAndSaveAgenticWorkflow}
            onLoadHistory={onLoadAgenticInsightHistory}
            onRunEvaluation={onRunEvaluationSummary}
            busy={busy}
          />
        </section>
      )}

      {activeView === 'ai-copilot' && (
        <section className="workflow-panel ai-copilot-view" id="site-ai-copilot-panel">
          <SiteAICopilotPanel
            summary={siteCopilotSummary}
            onRefresh={onRefreshSiteCopilot}
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
            onGenerate={onGenerateAiReasoning}
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
            onGenerate={onGenerateCircularActionReport}
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
            onDraftEmail={onDraftSupplierEmail}
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
            onExplain={onExplainEvidenceGap}
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
  );
}
