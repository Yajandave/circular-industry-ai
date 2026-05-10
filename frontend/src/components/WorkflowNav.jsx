const TABS = [
  {
    id: 'dashboard',
    label: 'Executive dashboard',
    helper: 'Portfolio snapshot, strategy mix and opportunity profile',
    requiresData: false,
    requiresRecommendations: false,
  },
  {
    id: 'recommendations',
    label: 'Recommendations',
    helper: 'Filter, rank and inspect locked rules-engine outputs',
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
  {
    id: 'ai-reasoning',
    label: 'AI reasoning',
    helper: 'Optional LLM narrative with rules locked and guardrails active',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'resolutions',
    label: 'Resolution plans',
    helper: 'Specific circular interventions, pilots, KPIs and claim boundaries',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'playbooks',
    label: 'Material playbooks',
    helper: 'Material-specific CE patterns, red flags and evidence tests',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'supplier-loops',
    label: 'Supplier loops',
    helper: 'Circular procurement, take-back, reverse logistics and contract evidence',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'review',
    label: 'Review pack',
    helper: 'Evidence, risk, procurement and symbiosis context',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'action-plan',
    label: 'Action plan',
    helper: 'Prioritised validation and implementation phases',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'evidence',
    label: 'Evidence register',
    helper: 'Audit trail, missing data, claim boundaries and exports',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'action-report',
    label: 'Action report',
    helper: 'Consultant-style circular action report for one selected stream',
    requiresData: true,
    requiresRecommendations: true,
  },
  {
    id: 'raw-data',
    label: 'Raw data',
    helper: 'Underlying industrial stream dataset',
    requiresData: true,
    requiresRecommendations: false,
  },
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

  return (
    <section className="workflow-shell">
      <div className="section-heading compact-heading">
        <div>
          <h2>Decision workflow</h2>
          <p>
            Load data, run the locked rules engine, then open evidence, supplier-loop, AI and report workflows.
            Guardrails prevent downstream workflows from opening before their required data exists.
          </p>
        </div>
        <span>{recommendationCount || 0} recommendations</span>
      </div>
      <div className="workflow-tabs" role="tablist" aria-label="Circular Industry AI workflow views">
        {TABS.map((tab) => {
          const reason = disabledReason(tab, hasData, hasRecommendations);
          const disabled = Boolean(reason);
          return (
            <button
              key={tab.id}
              type="button"
              className={`workflow-tab ${activeView === tab.id ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
              onClick={() => {
                if (!disabled) onChange(tab.id);
              }}
              disabled={disabled}
              role="tab"
              aria-selected={activeView === tab.id}
              aria-disabled={disabled}
              title={reason || tab.helper}
            >
              <strong>{tab.label}</strong>
              <small>{reason || (tab.id === 'review' && reviewPack ? `Loaded: ${reviewPack.stream_id}` : tab.helper)}</small>
            </button>
          );
        })}
      </div>
    </section>
  );
}
