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

export default function RecommendationsTable({ recommendations, onSelectReviewPack }) {
  return (
    <section className="table-card featured-table screen-table-section">
      <div className="section-heading">
        <div>
          <h2>Circular recommendations</h2>
          <p>Rules engine output remains the locked decision source. Agentic review adds context only.</p>
        </div>
        <span>{recommendations.length} shown</span>
      </div>
      <div className="table-wrap recommendations-table-wrap">
        <table className="recommendations-table">
          <thead>
            <tr>
              <th className="col-id">ID</th>
              <th>Stream and owner</th>
              <th>Decision</th>
              <th>Priority</th>
              <th>Risk and review</th>
              <th>Evidence</th>
              <th>Screened exposure</th>
              <th>Next action</th>
              <th>Pack</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec) => (
              <tr key={rec.stream_id}>
                <td className="col-id strong-id">{rec.stream_id}</td>
                <td>
                  <strong>{rec.stream?.stream_name || 'Stream unavailable'}</strong>
                  <small className="table-subtext">{rec.stream?.material || 'unknown'} · {rec.stream?.department || 'unknown department'}</small>
                </td>
                <td>
                  <strong>{rec.recommended_circular_action}</strong>
                  <small className="table-subtext strategy-text">{rec.circular_strategy_category}</small>
                </td>
                <td><PriorityCell band={rec.priority_band} score={rec.priority_score} /></td>
                <td>
                  <div className="score-stack">
                    <RiskBadge value={rec.risk_level} />
                    <ReviewBadge required={rec.human_review_required} />
                  </div>
                </td>
                <td className="score-stack">
                  <ScoreBadge label="Conf" value={rec.confidence_score} />
                  <ScoreBadge label="Evidence" value={rec.evidence_quality_score} />
                </td>
                <td>
                  <strong>{formatCurrency(rec.estimated_annual_disposal_cost_avoided)}</strong>
                  <small className="table-subtext">{formatKg(rec.estimated_annual_waste_diverted_kg)} annual diversion</small>
                </td>
                <td className="next-action-cell">{rec.next_action}</td>
                <td>
                  <button className="link-button compact" onClick={() => onSelectReviewPack(rec.stream_id)}>
                    Review
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
