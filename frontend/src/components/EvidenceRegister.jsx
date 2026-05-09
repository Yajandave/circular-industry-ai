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

function downloadCsv(path) {
  window.open(`${API_BASE_URL}${path}`, '_blank', 'noopener,noreferrer');
}

export default function EvidenceRegister({ records = [], summary = null }) {
  const sortedRecords = [...records].sort((a, b) => {
    const reviewSort = Number(b.human_review_required) - Number(a.human_review_required);
    if (reviewSort !== 0) return reviewSort;
    return a.evidence_quality_score - b.evidence_quality_score;
  });

  const criticalRecords = sortedRecords.filter(
    (record) => record.human_review_required || record.evidence_quality_score < 70,
  );

  return (
    <section className="section-card evidence-register-section">
      <div className="section-heading evidence-heading">
        <div>
          <span className="eyebrow">Milestone 7 evidence workflow</span>
          <h2>Evidence register and export controls</h2>
          <p>
            Trace each recommendation back to measured fields, estimated calculations, assumptions, missing evidence and
            review gates. This is the anti-greenwashing layer of the project.
          </p>
        </div>
        <div className="export-actions">
          <button type="button" className="secondary-button" onClick={() => downloadCsv('/api/export/recommendations.csv')}>
            Export recommendations CSV
          </button>
          <button type="button" onClick={() => downloadCsv('/api/export/evidence-register.csv')}>
            Export evidence register CSV
          </button>
        </div>
      </div>

      {!records.length && (
        <div className="empty-state">
          Run the recommendation engine first. The evidence register is generated from locked rules-engine outputs.
        </div>
      )}

      {summary && (
        <div className="evidence-summary-grid">
          <div className="metric-card">
            <span>Total records</span>
            <strong>{summary.total_records}</strong>
            <small>recommendations with evidence trail</small>
          </div>
          <div className="metric-card">
            <span>Human review gates</span>
            <strong>{summary.human_review_required}</strong>
            <small>must be reviewed before action</small>
          </div>
          <div className="metric-card">
            <span>Low-evidence records</span>
            <strong>{summary.low_evidence_records}</strong>
            <small>below 70/100 evidence quality</small>
          </div>
          <div className="metric-card">
            <span>Strong evidence</span>
            <strong>{summary.strong_evidence_records}</strong>
            <small>85/100 or higher</small>
          </div>
        </div>
      )}

      {summary && (
        <div className="evidence-breakdown-grid">
          <BreakdownList title="Evidence status" data={summary.evidence_status_breakdown} />
          <BreakdownList title="Claim readiness" data={summary.claim_readiness_breakdown} />
          <div className="evidence-governance-note">
            <h4>Governance note</h4>
            <p>{summary.governance_note}</p>
          </div>
        </div>
      )}

      {!!criticalRecords.length && (
        <div className="evidence-priority-box">
          <h3>Evidence priorities</h3>
          <p>
            These records should be resolved first because they have human-review gates, high risk or weak evidence.
          </p>
          <div className="evidence-priority-grid">
            {criticalRecords.slice(0, 8).map((record) => (
              <article key={record.stream_id} className="evidence-priority-card">
                <span>{record.stream_id}</span>
                <strong>{record.stream_name}</strong>
                <small>{record.review_gate}</small>
                <p>{record.missing_data}</p>
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
                <th>ID</th>
                <th>Stream</th>
                <th>Evidence status</th>
                <th>Scores</th>
                <th>Review gate</th>
                <th>Missing evidence</th>
                <th>Claim boundary</th>
                <th>Screened exposure</th>
              </tr>
            </thead>
            <tbody>
              {sortedRecords.map((record) => (
                <tr key={record.stream_id}>
                  <td>{record.stream_id}</td>
                  <td>
                    <strong>{record.stream_name}</strong>
                    <small>{record.material} · {record.department}</small>
                  </td>
                  <td>
                    <span className={`evidence-status-pill ${record.evidence_status.replaceAll(' ', '-')}`}>
                      {record.evidence_status}
                    </span>
                    <small>{record.claim_readiness}</small>
                  </td>
                  <td>
                    <span>Evidence: {record.evidence_quality_score}/100</span>
                    <small>Confidence: {record.confidence_score}/100</small>
                  </td>
                  <td>{record.review_gate}</td>
                  <td>{record.missing_data}</td>
                  <td>{record.claim_boundary}</td>
                  <td>
                    <strong>{formatCurrency(record.estimated_annual_disposal_cost_avoided)}</strong>
                    <small>{formatNumber(record.estimated_annual_waste_diverted_kg)} kg screened diversion</small>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
