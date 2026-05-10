const TABS = [
  { id: 'dashboard', label: 'Dashboard', helper: 'Site-level screening and opportunity profile', requiresData: false, requiresRecommendations: false },
  { id: 'recommendations', label: 'Recommendations', helper: 'Locked rules-engine outputs', requiresData: true, requiresRecommendations: false },
  { id: 'agentic-intelligence', label: 'Agentic intelligence', helper: 'Workflow, graph, history and evaluation', requiresData: true, requiresRecommendations: false },
  { id: 'ai-copilot', label: 'AI Copilot', helper: 'Site briefing and next actions', requiresData: true, requiresRecommendations: true },
  { id: 'ai-reasoning', label: 'AI reasoning', helper: 'Optional AI explanation', requiresData: true, requiresRecommendations: true },
  { id: 'resolutions', label: 'Resolution plans', helper: 'Pilots, KPIs and claim boundaries', requiresData: true, requiresRecommendations: true },
  { id: 'playbooks', label: 'Playbooks', helper: 'Material patterns and evidence tests', requiresData: true, requiresRecommendations: true },
  { id: 'supplier-loops', label: 'Supplier loops', helper: 'Procurement and take-back actions', requiresData: true, requiresRecommendations: true },
  { id: 'review', label: 'Review pack', helper: 'Evidence, risk and procurement context', requiresData: true, requiresRecommendations: true },
  { id: 'action-plan', label: 'Action plan', helper: 'Validation and implementation phases', requiresData: true, requiresRecommendations: true },
  { id: 'evidence', label: 'Evidence register', helper: 'Missing data and claim controls', requiresData: true, requiresRecommendations: true },
  { id: 'action-report', label: 'Action report', helper: 'Consultant-style report', requiresData: true, requiresRecommendations: true },
  { id: 'raw-data', label: 'Raw data', helper: 'Underlying stream dataset', requiresData: true, requiresRecommendations: false },
];

function disabledReason(tab, hasData, hasRecommendations) {
  if (tab.requiresData && !hasData) return 'Load data first';
  if (tab.requiresRecommendations && !hasRecommendations) return 'Run recommendations first';
  return null;
}

export default function WorkflowNav({
  activeView,
  onChange,
  recommendationCount,
  reviewPack,
  hasData = false,
}) {
  const hasRecommendations = (recommendationCount || 0) > 0;
  const activeTab = TABS.find((tab) => tab.id === activeView) || TABS[0];

  return (
    <section className="workflow-shell operator-workflow-shell">
      <div className="section-heading compact-heading">
        <div>
          <h2>Decision workflow</h2>
          <p>{activeTab.helper}</p>
        </div>
        <span>{recommendationCount || 0} recommendations</span>
      </div>

      <div className="workflow-tabs compact-workflow-tabs" role="tablist" aria-label="Circular Industry AI workflow views">
        {TABS.map((tab) => {
          const reason = disabledReason(tab, hasData, hasRecommendations);
          const disabled = Boolean(reason);
          const helper = tab.id === 'review' && reviewPack ? `Loaded: ${reviewPack.stream_id}` : tab.helper;

          return (
            <button
              key={tab.id}
              type="button"
              className={`workflow-tab compact-workflow-tab ${activeView === tab.id ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
              onClick={() => {
                if (!disabled) onChange(tab.id);
              }}
              disabled={disabled}
              role="tab"
              aria-selected={activeView === tab.id}
              aria-disabled={disabled}
              title={reason || helper}
            >
              <strong>{tab.label}</strong>
            </button>
          );
        })}
      </div>
    </section>
  );
}
