import { useMemo, useState } from 'react';

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
          
          <h3>Evidence gap explainer: {explanation.stream_id}</h3>
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
    </section>
  );
}

function downloadCsv(path) {
  window.open(`${API_BASE_URL}${path}`, '_blank', 'noopener,noreferrer');
}

function EvidenceListItem({ record, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`operator-list-row ${selected ? 'selected' : ''}`}
      onClick={() => onSelect(record.stream_id)}
      title={`Inspect ${record.stream_id}`}
    >
      <div className="operator-row-main">
        <span className="record-id">{record.stream_id}</span>
        <strong>{record.stream_name}</strong>
        <small>{record.material} · {record.department}</small>
      </div>
      <div className="operator-row-meta">
        <span>{record.evidence_quality_score}/100</span>
        <small>{record.human_review_required ? 'Review' : 'Clear'}</small>
      </div>
    </button>
  );
}

function EvidenceInspector({ record, onExplain, busy }) {
  if (!record) {
    return (
      <aside className="operator-inspector empty">
        <h3>Select an evidence record</h3>
        <p>Choose a stream to inspect evidence maturity, missing evidence, review gate and claim boundary.</p>
      </aside>
    );
  }

  return (
    <aside className="operator-inspector">
      <div className="operator-inspector-header">
        <div>
          <span className="record-id">{record.stream_id}</span>
          <h3>{record.stream_name}</h3>
          <p>{record.material} · {record.department}</p>
        </div>
        {onExplain && (
          <button
            type="button"
            className="secondary-button evidence-explain-button table-action-button"
            onClick={() => onExplain(record.stream_id)}
            disabled={busy}
          >
            Explain evidence gap
          </button>
        )}
      </div>

      <div className="inspector-kpi-grid">
        <article>
          <span>Evidence status</span>
          <strong>{record.evidence_status}</strong>
          <small>{record.claim_readiness}</small>
        </article>
        <article>
          <span>Evidence score</span>
          <strong>{record.evidence_quality_score}/100</strong>
          <small>Confidence: {record.confidence_score}/100</small>
        </article>
        <article>
          <span>Screened exposure</span>
          <strong>{formatCurrency(record.estimated_annual_disposal_cost_avoided)}</strong>
          <small>{formatNumber(record.estimated_annual_waste_diverted_kg)} kg screened diversion</small>
        </article>
      </div>

      <div className="operator-detail-section">
        <span>Review gate</span>
        <p>{record.review_gate}</p>
      </div>

      <div className="operator-detail-section">
        <span>Missing evidence</span>
        <p>{record.missing_data}</p>
      </div>

      <div className="operator-detail-section warning-detail">
        <span>Claim boundary</span>
        <p>{record.claim_boundary}</p>
      </div>
    </aside>
  );
}

export default function EvidenceRegister({ records = [], summary = null, explanation = null, onExplain = null, busy = false }) {
  const sortedRecords = useMemo(() => [...records].sort((a, b) => {
    const reviewSort = Number(b.human_review_required) - Number(a.human_review_required);
    if (reviewSort !== 0) return reviewSort;
    return a.evidence_quality_score - b.evidence_quality_score;
  }), [records]);

  const [selectedId, setSelectedId] = useState(sortedRecords[0]?.stream_id || '');
  const selected = sortedRecords.find((record) => record.stream_id === selectedId) || sortedRecords[0];

  return (
    <section className="section-card evidence-register-section operator-master-detail-section">
      <div className="section-heading evidence-heading">
        <div>
          
          <h2>Evidence register</h2>
          <p>Inspect evidence maturity through a readable list and detail panel. Use export for the full structured register.</p>
        </div>
        <div className="export-actions">
          <button type="button" className="secondary-button" onClick={() => downloadCsv('/api/export/recommendations.csv')}>Export recommendations</button>
          <button type="button" onClick={() => downloadCsv('/api/export/evidence-register.csv')}>Export evidence register</button>
        </div>
      </div>

      {!records.length && <div className="empty-state">Run the recommendation engine first. The evidence register is generated from locked rules-engine outputs.</div>}

      {summary && (
        <div className="operator-summary-grid">
          <div className="operator-summary-card"><span>Total records</span><strong>{summary.total_records}</strong><small>recommendations with evidence trail</small></div>
          <div className="operator-summary-card"><span>Human review gates</span><strong>{summary.human_review_required}</strong><small>must be reviewed before action</small></div>
          <div className="operator-summary-card"><span>Low-evidence records</span><strong>{summary.low_evidence_records}</strong><small>below 70/100 evidence quality</small></div>
          <div className="operator-summary-card"><span>Strong evidence</span><strong>{summary.strong_evidence_records}</strong><small>85/100 or higher</small></div>
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

      {!!records.length && (
        <div className="operator-master-detail">
          <div className="operator-list-panel">
            <div className="operator-list-header">
              <strong>Evidence records</strong>
              <small>Sorted by review gate and evidence weakness</small>
            </div>
            <div className="operator-list-scroll">
              {sortedRecords.map((record) => (
                <EvidenceListItem
                  key={record.stream_id}
                  record={record}
                  selected={selected?.stream_id === record.stream_id}
                  onSelect={setSelectedId}
                />
              ))}
            </div>
          </div>

          <EvidenceInspector record={selected} onExplain={onExplain} busy={busy} />
        </div>
      )}
    </section>
  );
}


