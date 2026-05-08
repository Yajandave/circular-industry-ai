import { formatCurrency, formatKg } from '../utils/formatters.js';

function BarList({ rows, labelKey, valueKey, formatter = (value) => value, emptyText = 'No data yet.' }) {
  const max = Math.max(...rows.map((row) => Number(row[valueKey]) || 0), 0);
  if (!rows.length) return <p className="muted">{emptyText}</p>;

  return (
    <div className="bar-list">
      {rows.map((row) => {
        const value = Number(row[valueKey]) || 0;
        const width = max > 0 ? Math.max((value / max) * 100, 4) : 4;
        return (
          <div className="bar-row" key={row[labelKey]}>
            <div className="bar-label"><span>{row[labelKey]}</span><strong>{formatter(value)}</strong></div>
            <div className="bar-track"><span style={{ width: `${width}%` }} /></div>
          </div>
        );
      })}
    </div>
  );
}

function CandidateList({ title, items, valueFormatter, valueKey, onSelectReviewPack }) {
  return (
    <article className="candidate-card">
      <h3>{title}</h3>
      {!items.length && <p className="muted">Run recommendations to populate this list.</p>}
      {items.map((item) => (
        <div className="candidate-row" key={`${title}-${item.stream_id}`}>
          <div>
            <strong>{item.stream_id}</strong>
            <p>{item.recommended_circular_action}</p>
            <small>{item.stream?.stream_name || 'Stream detail unavailable'} · {item.risk_level}</small>
          </div>
          <div className="candidate-value">
            <strong>{valueFormatter(item[valueKey])}</strong>
            <button className="link-button compact" onClick={() => onSelectReviewPack(item.stream_id)}>Review</button>
          </div>
        </div>
      ))}
    </article>
  );
}

export default function Dashboard({ dashboardData, agentSummary, onSelectReviewPack }) {
  const {
    riskBreakdown,
    strategyBreakdown,
    priorityBreakdown,
    materialQuantity,
    topCostCandidates,
    topDiversionCandidates,
    evidenceGaps,
    reviewRequired,
    quickWins,
    controlledReview,
    totalCostExposure,
    totalDiversionPotential,
  } = dashboardData;

  return (
    <section className="dashboard-shell">
      <div className="section-heading">
        <div>
          <h2>Decision dashboard</h2>
          <p>Portfolio view for circular opportunity screening, evidence maturity, controlled review and implementation prioritisation.</p>
        </div>
        <span>Milestone 6 dashboard</span>
      </div>

      <div className="insight-grid">
        <article className="insight-card positive">
          <span>Quick-win candidates</span>
          <strong>{quickWins}</strong>
          <small>Low-risk, high-scoring items suitable for validation before implementation.</small>
        </article>
        <article className="insight-card warning">
          <span>Controlled review items</span>
          <strong>{controlledReview}</strong>
          <small>Hazard, risk or evidence-sensitive streams that need formal review gates.</small>
        </article>
        <article className="insight-card">
          <span>Low-evidence records</span>
          <strong>{evidenceGaps}</strong>
          <small>Items below 70/100 evidence quality. These are data-improvement priorities.</small>
        </article>
        <article className="insight-card dark">
          <span>Screened value exposure</span>
          <strong>{formatCurrency(totalCostExposure)}</strong>
          <small>Annual disposal cost exposure from recommendations. Not verified savings.</small>
        </article>
      </div>

      {agentSummary?.executive_summary && (
        <article className="executive-card">
          <h3>Executive portfolio summary</h3>
          <p>{agentSummary.executive_summary}</p>
          <small>{agentSummary.portfolio_note}</small>
        </article>
      )}

      <div className="dashboard-grid">
        <article className="chart-card wide">
          <h3>Recommended strategy mix</h3>
          <BarList rows={strategyBreakdown} labelKey="strategy" valueKey="count" formatter={(value) => `${value} streams`} />
        </article>
        <article className="chart-card">
          <h3>Risk profile</h3>
          <BarList rows={riskBreakdown} labelKey="risk" valueKey="count" formatter={(value) => `${value}`} />
        </article>
        <article className="chart-card">
          <h3>Priority bands</h3>
          <BarList rows={priorityBreakdown} labelKey="priority" valueKey="count" formatter={(value) => `${value}`} />
        </article>
        <article className="chart-card wide">
          <h3>Annual material quantity by material type</h3>
          <BarList rows={materialQuantity} labelKey="material" valueKey="annualKg" formatter={formatKg} />
        </article>
      </div>

      <div className="candidate-grid">
        <CandidateList
          title="Top cost-exposure candidates"
          items={topCostCandidates}
          valueFormatter={formatCurrency}
          valueKey="estimated_annual_disposal_cost_avoided"
          onSelectReviewPack={onSelectReviewPack}
        />
        <CandidateList
          title="Top diversion-potential candidates"
          items={topDiversionCandidates}
          valueFormatter={formatKg}
          valueKey="estimated_annual_waste_diverted_kg"
          onSelectReviewPack={onSelectReviewPack}
        />
      </div>

      <p className="governance-strip">
        Dashboard values are screening outputs. They support prioritisation but should not be presented as verified savings, verified diversion or verified environmental benefit until actions are completed and evidenced. Total screened diversion currently shown: {formatKg(totalDiversionPotential)}.
      </p>
    </section>
  );
}
