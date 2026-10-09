import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client.js';

import { RiskBadge, ReviewBadge } from './Badges.jsx';
import { formatCurrency, formatKg, humanise } from '../utils/formatters.js';

function PriorityCell({ band }) {
  const safeBand = String(band || 'unclassified');
  return (
    <div className="priority-cell">
      <span className={`priority-pill priority-${safeBand.replaceAll(' ', '-')}`}>{safeBand}</span>
      <small className="table-subtext">Governance-led triage band</small>
    </div>
  );
}

function RecommendationListItem({ rec, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`operator-list-row ${selected ? 'selected' : ''}`}
      onClick={() => onSelect(rec.stream_id)}
      title={`Open ${rec.stream_id}`}
    >
      <div className="operator-row-main">
        <span className="record-id">{rec.stream_id}</span>
        <strong>{rec.stream?.stream_name || 'Stream unavailable'}</strong>
        <small>{rec.stream?.material || 'unknown'} · {rec.stream?.department || 'unknown department'}</small>
      </div>
      <div className="operator-row-meta">
        <RiskBadge value={rec.risk_level} />
        <span>{formatCurrency(rec.estimated_annual_disposal_cost_avoided)}</span>
      </div>
    </button>
  );
}

function RecommendationInspector({ rec, onSelectReviewPack }) {
  const [feasibility, setFeasibility] = useState(null);
  const [feasibilityError, setFeasibilityError] = useState(false);
  useEffect(() => {
    let active = true;
    setFeasibility(null);
    setFeasibilityError(false);
    if (rec?.stream_id) api.recommendationFeasibility(rec.stream_id)
      .then((result) => { if (active) setFeasibility(result); })
      .catch(() => { if (active) setFeasibilityError(true); });
    return () => { active = false; };
  }, [rec?.stream_id]);
  if (!rec) {
    return (
      <aside className="operator-inspector empty">
        <h3>Select a recommendation</h3>
        <p>Choose a record to inspect decision logic, review status, evidence maturity and next action.</p>
      </aside>
    );
  }

  return (
    <aside className="operator-inspector">
      <div className="operator-inspector-header">
        <div>
          <span className="record-id">{rec.stream_id}</span>
          <h3>{rec.stream?.stream_name || 'Stream unavailable'}</h3>
          <p>{rec.stream?.material || 'unknown'} · {rec.stream?.department || 'unknown department'}</p>
        </div>
        <button className="link-button compact table-action-button" onClick={() => onSelectReviewPack(rec.stream_id)}>
          Open review pack
        </button>
      </div>

      <div className="inspector-decision-box">
        <span>Locked recommendation</span>
        <strong>{rec.recommended_circular_action}</strong>
        <p>{rec.circular_strategy_category}</p>
      </div>

      <div className="inspector-kpi-grid">
        <article>
          <span>Risk</span>
          <RiskBadge value={rec.risk_level} />
        </article>
        <article>
          <span>Review</span>
          <ReviewBadge required={rec.human_review_required} />
        </article>
        <article>
          <span>Priority</span>
          <PriorityCell band={rec.priority_band} />
        </article>
        <article>
          <span>Decision basis</span>
          <strong>{humanise(rec.decision_support_band)}</strong>
          <small>{humanise(rec.evidence_maturity)}</small>
        </article>
      </div>

      <div className="operator-detail-section">
        <span>Screened cost exposure</span>
        <strong>{formatCurrency(rec.estimated_annual_disposal_cost_avoided)}</strong>
        <p>{formatKg(rec.estimated_annual_waste_diverted_kg)} screened annual quantity opportunity. Potential only; not verified diversion or savings.</p>
      </div>

      <div className="operator-detail-section">
        <span>Next action</span>
        <p>{rec.next_action}</p>
      </div>

      <div className="operator-detail-section" aria-label="Operational feasibility">
        <span>Operational feasibility</span>
        {feasibilityError ? <p>Feasibility check unavailable. Route remains unverified and unauthorised.</p>
          : !feasibility ? <p>Loading read-only feasibility checks…</p>
          : <>
              <strong>{humanise(feasibility.state)}</strong>
              <ul>
                {Object.entries(feasibility.checks || {}).map(([name, state]) => (
                  <li key={name}>{humanise(name)}: {humanise(state)}</li>
                ))}
              </ul>
              <p>These checks do not independently verify supplier acceptance, legal compliance or commercial feasibility. This application does not authorise a route.</p>
            </>}
      </div>

      <div className="governance-strip compact">
        Rules-engine recommendation. Evidence maturity and decision-basis labels are qualitative governance states, not probability or assurance scores.
      </div>
    </aside>
  );
}

export default function RecommendationsTable({ recommendations, onSelectReviewPack }) {
  const [selectedId, setSelectedId] = useState(recommendations[0]?.stream_id || '');

  const selected = useMemo(
    () => recommendations.find((rec) => rec.stream_id === selectedId) || recommendations[0],
    [recommendations, selectedId],
  );

  return (
    <section className="table-card featured-table screen-table-section recommendation-section operator-master-detail-section">
      <div className="section-heading">
        <div>
          <h2>Circular recommendations</h2>
          <p>Use the list to triage streams, then inspect the selected recommendation in the detail panel.</p>
        </div>
        <span>{recommendations.length} shown</span>
      </div>

      <div className="operator-master-detail">
        <div className="operator-list-panel">
          <div className="operator-list-header">
            <strong>Recommendation list</strong>
            <small>ID, stream, risk and screened cost exposure</small>
          </div>
          <div className="operator-list-scroll">
            {recommendations.map((rec) => (
              <RecommendationListItem
                key={rec.stream_id}
                rec={rec}
                selected={selected?.stream_id === rec.stream_id}
                onSelect={setSelectedId}
              />
            ))}
          </div>
        </div>

        <RecommendationInspector rec={selected} onSelectReviewPack={onSelectReviewPack} />
      </div>
    </section>
  );
}
