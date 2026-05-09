function ListBlock({ title, items = [] }) {
  const safeItems = Array.isArray(items) ? items.filter(Boolean) : [];

  return (
    <article className="copilot-list-block">
      <h3>{title}</h3>
      {safeItems.length > 0 ? (
        <ul>
          {safeItems.map((item, index) => (
            <li key={`${title}-${index}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No items returned for this section.</p>
      )}
    </article>
  );
}

export default function SiteAICopilotPanel({ summary, onRefresh, busy }) {
  if (!summary) {
    return (
      <section className="ai-copilot-panel empty">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Milestone 8B</span>
            <h2>Site-wide AI Copilot</h2>
            <p>
              Generate a dashboard-level briefing from locked recommendations, risk controls, evidence gaps and
              supplier-loop intelligence.
            </p>
          </div>
          <button type="button" onClick={onRefresh} disabled={busy}>
            Generate copilot summary
          </button>
        </div>
        <div className="governance-strip">
          The AI copilot is advisory only. The rules engine remains the locked decision source.
        </div>
      </section>
    );
  }

  const modeLabel =
    summary.generation_mode === 'llm_structured_output'
      ? `${summary.model_name} live summary`
      : summary.generation_mode?.replaceAll('_', ' ') || 'copilot summary';

  return (
    <section className="ai-copilot-panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Milestone 8B</span>
          <h2>Site-wide AI Copilot</h2>
          <p>
            A controlled briefing layer for portfolio-level risk, circular opportunity, evidence gaps, supplier actions
            and next steps.
          </p>
        </div>
        <button type="button" onClick={onRefresh} disabled={busy}>
          Refresh copilot summary
        </button>
      </div>

      <div className="copilot-status-grid">
        <article>
          <span>Generation mode</span>
          <strong>{modeLabel}</strong>
        </article>
        <article>
          <span>Decision lock</span>
          <strong>{summary.decision_lock_status}</strong>
        </article>
        <article>
          <span>Claim control</span>
          <strong>Estimated outputs only</strong>
        </article>
      </div>

      <article className="copilot-executive-card">
        <h3>Executive briefing</h3>
        <p>{summary.executive_summary}</p>
      </article>

      <div className="copilot-grid">
        <article>
          <h3>Risk position</h3>
          <p>{summary.risk_summary}</p>
        </article>
        <article>
          <h3>Circular opportunity</h3>
          <p>{summary.opportunity_summary}</p>
        </article>
        <article>
          <h3>Evidence gaps</h3>
          <p>{summary.evidence_gap_summary}</p>
        </article>
        <article>
          <h3>Supplier and procurement actions</h3>
          <p>{summary.supplier_procurement_summary}</p>
        </article>
      </div>

      <div className="copilot-grid lower">
        <ListBlock title="Human review priorities" items={summary.human_review_priorities} />
        <ListBlock title="Recommended next actions" items={summary.recommended_next_actions} />
      </div>

      <article className="copilot-claim-card">
        <h3>Claim safety note</h3>
        <p>{summary.claim_safety_note}</p>
      </article>

      <div className="governance-strip">
        {summary.governance_note}
      </div>

      {summary.validation_warnings?.length > 0 && (
        <article className="copilot-warning-card">
          <h3>Validation warnings</h3>
          <ul>
            {summary.validation_warnings.map((warning, index) => (
              <li key={`warning-${index}`}>{warning}</li>
            ))}
          </ul>
        </article>
      )}
    </section>
  );
}
