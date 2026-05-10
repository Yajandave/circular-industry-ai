import { formatCurrency, formatKg } from '../utils/formatters.js';

function SnapshotMetric({ label, value, note }) {
  return (
    <article className="snapshot-metric">
      <span>{label}</span>
      <strong>{value}</strong>
      {note && <small>{note}</small>}
    </article>
  );
}

function SnapshotList({ title, items, valueKey, valueFormatter }) {
  return (
    <article className="snapshot-list-card">
      <h3>{title}</h3>
      {!items.length && <p className="muted">Run recommendations to populate this list.</p>}
      <ol>
        {items.slice(0, 4).map((item) => (
          <li key={`${title}-${item.stream_id}`}>
            <div>
              <strong>{item.stream_id}</strong>
              <span>{item.stream?.stream_name || item.recommended_circular_action}</span>
            </div>
            <b>{valueFormatter(item[valueKey])}</b>
          </li>
        ))}
      </ol>
    </article>
  );
}

export default function PortfolioSnapshot({ dashboardData, agentSummary }) {
  const quickWins = dashboardData.enriched
    .filter((rec) => rec.priority_band === 'quick win')
    .slice(0, 4);

  const controlledReview = dashboardData.enriched
    .filter((rec) => rec.priority_band === 'controlled review')
    .slice(0, 4);

  return (
    <section className="portfolio-snapshot" aria-label="Operational intelligence summary snapshot">
      <div className="section-heading compact-heading">
        <div>
          <h2>Operational intelligence snapshot</h2>
          <p>A site-level summary of screened material flows, review gates, value exposure and evidence-controlled circular opportunities.</p>
        </div>
        <span>Management briefing ready</span>
      </div>

      <div className="snapshot-grid">
        <SnapshotMetric label="Streams screened" value={agentSummary?.total_recommendations || dashboardData.enriched.length} note="industrial material and waste streams" />
        <SnapshotMetric label="Review gates" value={agentSummary?.human_review_required || dashboardData.controlledReview} note="hazard, risk or weak evidence controls" />
        <SnapshotMetric label="Screened value exposure" value={formatCurrency(dashboardData.totalCostExposure)} note="not verified savings" />
        <SnapshotMetric label="Diversion potential" value={formatKg(dashboardData.totalDiversionPotential)} note="screening estimate only" />
      </div>

      <div className="snapshot-body">
        <article className="snapshot-narrative">
          <h3>Decision-support position</h3>
          <p>
            Circular Industry AI combines deterministic circular economy rules, risk scoring, evidence maturity checks, knowledge retrieval and
            controlled autonomous insight generation. The interface is designed to support operational screening, supplier engagement,
            review gates and evidence-led circular action planning while keeping the decision source auditable.
          </p>
          <p className="snapshot-warning">
            The system supports opportunity screening. It does not verify savings, environmental benefit, supplier compliance,
            legal waste status or carbon claims without completed actions and evidence.
          </p>
        </article>

        <SnapshotList title="Priority validation opportunities" items={quickWins} valueKey="estimated_annual_waste_diverted_kg" valueFormatter={formatKg} />
        <SnapshotList title="Controlled review priorities" items={controlledReview} valueKey="estimated_annual_disposal_cost_avoided" valueFormatter={formatCurrency} />
      </div>
    </section>
  );
}

