import { API_BASE_URL } from '../api/client.js';
import { formatCurrency, formatNumber } from '../utils/formatters.js';

function BreakdownList({ title, data }) {
  const entries = Object.entries(data || {});
  if (!entries.length) return null;
  return (
    <div className="evidence-breakdown-card">
      <h4>{title}</h4>
      <div className="evidence-breakdown-list">
        {entries.map(([label, value]) => (
          <div key={label} className="breakdown-row">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function ExplainerList({ title, items = [] }) {
  const safeItems = Array.isArray(items) ? items.filter(Boolean) : [];
  return (
    <article className="evidence-explainer-list">
      <h4>{title}</h4>
      {safeItems.length ? (
        <ul>{safeItems.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}</ul>
      ) : (
        <p className="muted">No items returned.</p>
      )}
    </article>
  );
}

function EvidenceGapExplainer({ explanation }) {
  if (!explanation) return null;
  return (
    <section className="evidence-gap-explainer" id="evidence-gap-explainer">
      <div className="section-heading compact-heading">
        <div>
          <span className="eyebrow">Milestone 8C</span>
          <h3>AI evidence gap explainer: {explanation.stream_id}</h3>
          <p>Advisory explanation for claim readiness, missing evidence and safe next steps. Locked rules-engine fields remain unchanged.</p>
        </div>
        <span>{explanation.generation_mode?.replaceAll('_', ' ')}</span>
      </div>
      <div className="evidence-explainer-lock-grid">
        <article><span>Risk level</span><strong>{explanation.locked_risk_level}</strong></article>
        <article><span>Review gate</span><strong>{explanation.locked_review_gate}</strong></article>
        <article><span>Claim readiness</span><strong>{explanation.locked_claim_readiness}</strong></article>
      </div>
      <div className="evidence-explainer-grid">
        <article><h4>Evidence gap summary</h4><p>{explanation.evidence_gap_summary}</p></article>
        <article><h4>Claim readiness explanation</h4><p>{explanation.claim_readiness_explanation}</p></article>
        <article><h4>Safe current statement</h4><p>{explanation.safe_current_statement}</p></article>
        <article><h4>Recommended review gate</h4><p>{explanation.recommended_review_gate}</p></article>
      </div>
      <div className="evidence-explainer-grid list-grid">
        <ExplainerList title="Evidence to collect" items={explanation.evidence_to_collect} />
        <ExplainerList title="Supplier documents required" items={explanation.supplier_documents_required} />
        <ExplainerList title="Process checks required" items={explanation.process_checks_required} />
        <ExplainerList title="Unsafe claims to avoid" items={explanation.unsafe_claims_to_avoid} />
      </div>
      <div className="governance-strip">{explanation.governance_note}</div>
      {!!explanation.validation_warnings?.length && (
        <div className="evidence-explainer-warning">
          <h4>Validation warnings</h4>
          <ul>{explanation.validation_warnings.map((warning, index) => <li key={`evidence-warning-${index}`}>{warning}</li>)}</ul>
        </div>
      )}
    </section>
  );
}

function downloadCsv(path) {
  window.open(`${API_BASE_URL}${path}`, '_blank', 'noopener,noreferrer');
}

export default function EvidenceRegister({ records = [], summary = null, explanation = null, onExplain = null, busy = false }) {
  const sortedRecords = [...records].sort((a, b) => {
    const reviewSort = Number(b.human_review_required) - Number(a.human_review_required);
    if (reviewSort !== 0) return reviewSort;
    return a.evidence_quality_score - b.evidence_quality_score;
  });
  const criticalRecords = sortedRecords.filter((record) => record.human_review_required || record.evidence_quality_score < 70);

  return (
    <section className="section-card evidence-register-section">
      <div className="section-heading evidence-heading">
        <div>
          <span className="eyebrow">Milestone 8C evidence workflow</span>
          <h2>Evidence register and AI evidence gap explainer</h2>
          <p>Trace each recommendation back to measured fields, estimated calculations, assumptions, missing evidence and review gates. The explainer turns evidence gaps into audit-ready next steps without changing locked decisions.</p>
        </div>
        <div className="export-actions">
          <button type="button" className="secondary-button" onClick={() => downloadCsv('/api/export/recommendations.csv')}>Export recommendations CSV</button>
          <button type="button" onClick={() => downloadCsv('/api/export/evidence-register.csv')}>Export evidence register CSV</button>
        </div>
      </div>

      {!records.length && <div className="empty-state">Run the recommendation engine first. The evidence register is generated from locked rules-engine outputs.</div>}

      {summary && (
        <div className="evidence-summary-grid">
          <div className="metric-card"><span>Total records</span><strong>{summary.total_records}</strong><small>recommendations with evidence trail</small></div>
          <div className="metric-card"><span>Human review gates</span><strong>{summary.human_review_required}</strong><small>must be reviewed before action</small></div>
          <div className="metric-card"><span>Low-evidence records</span><strong>{summary.low_evidence_records}</strong><small>below 70/100 evidence quality</small></div>
          <div className="metric-card"><span>Strong evidence</span><strong>{summary.strong_evidence_records}</strong><small>85/100 or higher</small></div>
        </div>
      )}

      {summary && (
        <div className="evidence-breakdown-grid">
          <BreakdownList title="Evidence status" data={summary.evidence_status_breakdown} />
          <BreakdownList title="Claim readiness" data={summary.claim_readiness_breakdown} />
          <div className="evidence-governance-note"><h4>Governance note</h4><p>{summary.governance_note}</p></div>
        </div>
      )}

      <EvidenceGapExplainer explanation={explanation} />

      {!!criticalRecords.length && (
        <div className="evidence-priority-box">
          <h3>Evidence priorities</h3>
          <p>These records should be resolved first because they have human-review gates, high risk or weak evidence.</p>
          <div className="evidence-priority-grid">
            {criticalRecords.slice(0, 8).map((record) => (
              <article key={record.stream_id} className="evidence-priority-card">
                <span>{record.stream_id}</span>
                <strong>{record.stream_name}</strong>
                <small>{record.review_gate}</small>
                <p>{record.missing_data}</p>
                {onExplain && <button type="button" className="secondary-button evidence-explain-button" onClick={() => onExplain(record.stream_id)} disabled={busy}>Explain evidence gap</button>}
              </article>
            ))}
          </div>
        </div>
      )}

      {!!records.length && (
        <div className="table-wrap evidence-table-wrap">
          <table className="data-table evidence-table">
            <thead>
              <tr>
                <th>ID</th><th>Stream</th><th>Evidence status</th><th>Scores</th><th>Review gate</th><th>Missing evidence</th><th>Claim boundary</th><th>Screened exposure</th><th>AI explainer</th>
              </tr>
            </thead>
            <tbody>
              {sortedRecords.map((record) => (
                <tr key={record.stream_id}>
                  <td>{record.stream_id}</td>
                  <td><strong>{record.stream_name}</strong><small>{record.material} · {record.department}</small></td>
                  <td><span className={`evidence-status-pill ${record.evidence_status.replaceAll(' ', '-')}`}>{record.evidence_status}</span><small>{record.claim_readiness}</small></td>
                  <td><span>Evidence: {record.evidence_quality_score}/100</span><small>Confidence: {record.confidence_score}/100</small></td>
                  <td>{record.review_gate}</td>
                  <td>{record.missing_data}</td>
                  <td>{record.claim_boundary}</td>
                  <td><strong>{formatCurrency(record.estimated_annual_disposal_cost_avoided)}</strong><small>{formatNumber(record.estimated_annual_waste_diverted_kg)} kg screened diversion</small></td>
                  <td>{onExplain && <button type="button" className="link-button compact" onClick={() => onExplain(record.stream_id)} disabled={busy}>Explain</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
