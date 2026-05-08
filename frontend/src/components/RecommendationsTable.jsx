import { RiskBadge, ReviewBadge, ScoreBadge } from './Badges.jsx';
import { formatCurrency, formatKg } from '../utils/formatters.js';

export default function RecommendationsTable({ recommendations, onSelectReviewPack }) {
  return (
    <section className="table-card featured-table">
      <div className="section-heading">
        <div>
          <h2>Circular recommendations</h2>
          <p>Rules engine output remains the locked decision source. Agentic review adds context only.</p>
        </div>
        <span>{recommendations.length} shown</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Stream</th>
              <th>Recommended action</th>
              <th>Strategy</th>
              <th>Priority</th>
              <th>Risk</th>
              <th>Scores</th>
              <th>Annual diversion</th>
              <th>Cost exposure</th>
              <th>Review</th>
              <th>Next action</th>
              <th>Agentic pack</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec) => (
              <tr key={rec.stream_id}>
                <td>{rec.stream_id}</td>
                <td>
                  <strong>{rec.stream?.stream_name || 'Stream unavailable'}</strong>
                  <small className="table-subtext">{rec.stream?.material || 'unknown'} · {rec.stream?.department || 'unknown department'}</small>
                </td>
                <td>{rec.recommended_circular_action}</td>
                <td>{rec.circular_strategy_category}</td>
                <td>
                  <span className={`priority-pill priority-${String(rec.priority_band).replaceAll(' ', '-')}`}>{rec.priority_band}</span>
                  <small className="table-subtext">Score {rec.priority_score}/100</small>
                </td>
                <td><RiskBadge value={rec.risk_level} /></td>
                <td className="score-stack">
                  <ScoreBadge label="Conf" value={rec.confidence_score} />
                  <ScoreBadge label="Evidence" value={rec.evidence_quality_score} />
                </td>
                <td>{formatKg(rec.estimated_annual_waste_diverted_kg)}</td>
                <td>{formatCurrency(rec.estimated_annual_disposal_cost_avoided)}</td>
                <td><ReviewBadge required={rec.human_review_required} /></td>
                <td>{rec.next_action}</td>
                <td>
                  <button className="link-button" onClick={() => onSelectReviewPack(rec.stream_id)}>
                    Open review
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
