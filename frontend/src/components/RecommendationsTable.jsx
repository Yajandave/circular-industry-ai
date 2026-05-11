import { useMemo, useState } from 'react';

import { RiskBadge, ReviewBadge, ScoreBadge } from './Badges.jsx';
import { formatCurrency, formatKg } from '../utils/formatters.js';

function PriorityCell({ band, score }) {
  const safeBand = String(band || 'unscored');
  return (
    <div className="priority-cell">
      <span className={`priority-pill priority-${safeBand.replaceAll(' ', '-')}`}>{safeBand}</span>
      <small className="table-subtext">Priority {score ?? 0}/100</small>
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
          <PriorityCell band={rec.priority_band} score={rec.priority_score} />
        </article>
        <article>
          <span>Scores</span>
          <div className="score-stack">
            <ScoreBadge label="Conf" value={rec.confidence_score} />
            <ScoreBadge label="Evidence" value={rec.evidence_quality_score} />
          </div>
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

      <div className="governance-strip compact">
        Rules-engine recommendation. Use the review pack before making operational, supplier, cost-saving, diversion or claim decisions.
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
