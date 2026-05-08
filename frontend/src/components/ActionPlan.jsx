import { RiskBadge } from './Badges.jsx';
import { formatCurrency, formatKg } from '../utils/formatters.js';

export default function ActionPlan({ actionPlan }) {
  if (!actionPlan?.phases) return null;
  return (
    <section className="action-plan">
      <div className="section-heading">
        <div>
          <h2>Ranked action plan</h2>
          <p>{actionPlan.ranking_method}</p>
        </div>
      </div>
      <div className="phase-grid">
        {Object.entries(actionPlan.phases).map(([phaseName, items]) => (
          <article className="phase-card" key={phaseName}>
            <h3>{phaseName}</h3>
            {items.map((item) => (
              <div className="action-item" key={item.stream_id}>
                <div className="action-topline">
                  <strong>{item.stream_id}</strong>
                  <RiskBadge value={item.risk_level} />
                </div>
                <p>{item.recommended_circular_action}</p>
                <small>{formatKg(item.estimated_annual_waste_diverted_kg)} · {formatCurrency(item.estimated_annual_disposal_cost_avoided)}</small>
              </div>
            ))}
          </article>
        ))}
      </div>
      <p className="boundary-note">{actionPlan.governance_note}</p>
    </section>
  );
}
