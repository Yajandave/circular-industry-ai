const TABS = [
  {
    id: 'dashboard',
    label: 'Executive dashboard',
    helper: 'Portfolio snapshot, strategy mix and opportunity profile',
  },
  {
    id: 'recommendations',
    label: 'Recommendations',
    helper: 'Filter, rank and inspect locked rules-engine outputs',
  },

  {
    id: 'ai-reasoning',
    label: 'AI reasoning',
    helper: 'Optional LLM narrative with rules locked and guardrails active',
  },
  {
    id: 'resolutions',
    label: 'Resolution plans',
    helper: 'Specific circular interventions, pilots, KPIs and claim boundaries',
  },

  {
    id: 'playbooks',
    label: 'Material playbooks',
    helper: 'Material-specific CE patterns, red flags and evidence tests',
  },
  {
    id: 'review',
    label: 'Review pack',
    helper: 'Evidence, risk, procurement and symbiosis context',
  },
  {
    id: 'action-plan',
    label: 'Action plan',
    helper: 'Prioritised validation and implementation phases',
  },
  {
    id: 'evidence',
    label: 'Evidence register',
    helper: 'Audit trail, missing data, claim boundaries and exports',
  },
  {
    id: 'raw-data',
    label: 'Raw data',
    helper: 'Underlying industrial stream dataset',
  },
];

export default function WorkflowNav({ activeView, onChange, recommendationCount, reviewPack }) {
  return (
    <section className="workflow-shell">
      <div className="section-heading compact-heading">
        <div>
          <h2>Decision workflow</h2>
          <p>Use the dashboard first, then drill into recommendations, resolution plans, AI reasoning, evidence and raw data only when needed.</p>
        </div>
        <span>{recommendationCount || 0} recommendations</span>
      </div>
      <div className="workflow-tabs" role="tablist" aria-label="Circular Industry AI workflow views">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`workflow-tab ${activeView === tab.id ? 'active' : ''}`}
            onClick={() => onChange(tab.id)}
            role="tab"
            aria-selected={activeView === tab.id}
          >
            <strong>{tab.label}</strong>
            <small>{tab.id === 'review' && reviewPack ? `Loaded: ${reviewPack.stream_id}` : tab.helper}</small>
          </button>
        ))}
      </div>
    </section>
  );
}
