import { formatCurrency, formatKg, formatNumber, humanise } from '../utils/formatters.js';

function EmptyVisual({ text = 'Run recommendations to populate this visual.' }) {
  return <p className="visual-empty">{text}</p>;
}

function VisualBarList({ rows = [], formatter = formatNumber }) {
  const max = Math.max(...rows.map((row) => Number(row.value) || 0), 0);
  if (!rows.length) return <EmptyVisual />;

  return (
    <div className="visual-bar-list">
      {rows.slice(0, 8).map((row) => {
        const value = Number(row.value) || 0;
        const width = max > 0 ? Math.max((value / max) * 100, 4) : 4;
        return (
          <div className="visual-bar-row" key={row.label}>
            <div className="visual-bar-label">
              <span>{row.label}</span>
              <strong>{formatter(value)}</strong>
            </div>
            <div className="visual-bar-track"><span style={{ width: `${width}%` }} /></div>
          </div>
        );
      })}
    </div>
  );
}

function ParetoList({ rows = [], formatter }) {
  if (!rows.length) return <EmptyVisual />;

  return (
    <div className="pareto-list">
      {rows.slice(0, 8).map((row, index) => (
        <div className="pareto-row" key={`${row.label}-${index}`}>
          <div className="pareto-rank">{index + 1}</div>
          <div className="pareto-main">
            <div className="visual-bar-label">
              <span>{row.label}</span>
              <strong>{formatter(row.value)}</strong>
            </div>
            <div className="visual-bar-track"><span style={{ width: `${Math.max(row.share || 0, 4)}%` }} /></div>
          </div>
          <div className="pareto-share">
            <strong>{Math.round(row.cumulativeShare || 0)}%</strong>
            <small>cum.</small>
          </div>
        </div>
      ))}
    </div>
  );
}

function RiskOpportunityMatrix({ matrix }) {
  const rows = matrix?.rows || [];
  const columns = matrix?.columns || [];
  const cells = matrix?.cells || [];
  const max = Math.max(...cells.map((cell) => cell.count), 1);

  if (!rows.length || !columns.length) return <EmptyVisual />;

  return (
    <div className="risk-matrix" style={{ gridTemplateColumns: `124px repeat(${columns.length}, minmax(0, 1fr))` }}>
      <div className="matrix-corner">Risk</div>
      {columns.map((column) => <div className="matrix-heading" key={column.key}>{column.label}</div>)}
      {rows.map((row) => (
        <div className="matrix-row-fragment" key={row.key}>
          <div className="matrix-risk-label">{row.label}</div>
          {columns.map((column) => {
            const cell = cells.find((item) => item.risk === row.key && item.opportunity === column.key) || { count: 0, exposure: 0 };
            return (
              <div className={`matrix-cell ${cell.count ? 'active' : ''}`} style={{ '--cell-intensity': cell.count / max }} key={`${row.key}-${column.key}`}>
                <strong>{cell.count}</strong>
                <small>{formatCurrency(cell.exposure)}</small>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function EvidenceDonut({ rows = [], total = 0 }) {
  if (!rows.length || !total) return <EmptyVisual />;

  let running = 0;
  const segments = rows.map((row) => {
    const start = running;
    const size = ((Number(row.value) || 0) / total) * 100;
    running += size;
    return `${row.tone} ${start}% ${running}%`;
  });

  return (
    <div className="donut-layout">
      <div className="donut-chart" style={{ background: `conic-gradient(${segments.join(', ')})` }}>
        <div><strong>{formatNumber(total)}</strong><span>records</span></div>
      </div>
      <div className="donut-legend">
        {rows.map((row) => (
          <div className="donut-legend-row" key={row.label}>
            <span style={{ background: row.tone }} />
            <div><strong>{row.label}</strong><small>{formatNumber(row.value)} records</small></div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScenarioPanel({ items = [], onSelectReviewPack }) {
  if (!items.length) return <EmptyVisual text="No scenario candidates yet. Run recommendations first." />;

  return (
    <div className="scenario-list">
      {items.map((item) => (
        <article className="scenario-card" key={item.stream_id}>
          <div>
            <span className="record-id">{item.stream_id}</span>
            <h4>{item.stream_name}</h4>
            <p>{item.scenario}</p>
          </div>
          <div className="scenario-score">
            <strong>{item.priority_score}</strong>
            <small>screening score</small>
            {onSelectReviewPack && <button type="button" className="link-button compact" onClick={() => onSelectReviewPack(item.stream_id)}>Review</button>}
          </div>
        </article>
      ))}
    </div>
  );
}

export default function VisualAnalyticsDashboard({ analytics, onSelectReviewPack }) {
  if (!analytics) return null;

  return (
    <section className="visual-analytics-section">
      <div className="section-heading visual-heading">
        <div>
          <h2>Visual analytics dashboard</h2>
          <p>Decision-useful visuals for material flow, screened exposure, evidence maturity, claim control, supplier-loop opportunity and prioritisation.</p>
        </div>
        <span>Analytics layer</span>
      </div>

      <div className="visual-analytics-grid">
        <article className="visual-card visual-card-wide"><h3>Risk vs opportunity matrix</h3><p>Count and screened value exposure by locked risk level and opportunity strength.</p><RiskOpportunityMatrix matrix={analytics.matrix} /></article>
        <article className="visual-card"><h3>Evidence maturity</h3><p>Whether records are strong enough for action planning or need evidence uplift.</p><EvidenceDonut rows={analytics.evidenceMaturity} total={analytics.totalRecords} /></article>
        <article className="visual-card"><h3>Claim-readiness control</h3><p>Screening proxy based on evidence score, risk and human-review gate.</p><VisualBarList rows={analytics.claimReadiness} /></article>
        <article className="visual-card visual-card-wide"><h3>Material quantity Pareto</h3><p>Largest annual material-flow groups by screened quantity.</p><ParetoList rows={analytics.materialPareto} formatter={formatKg} /></article>
        <article className="visual-card visual-card-wide"><h3>Cost exposure Pareto</h3><p>Largest screened disposal-cost exposure records. Not verified savings.</p><ParetoList rows={analytics.costPareto} formatter={formatCurrency} /></article>
        <article className="visual-card"><h3>Supplier-loop opportunity profile</h3><p>Supplier-facing routes split into candidate, controlled-review and supplier-data-gap groups.</p><VisualBarList rows={analytics.supplierLoopProfile} /></article>
        <article className="visual-card visual-card-wide"><h3>Scenario screening panel</h3><p>Compact triage list for the next operator action.</p><ScenarioPanel items={analytics.scenarioItems} onSelectReviewPack={onSelectReviewPack} /></article>
        <article className="visual-card"><h3>Decision controls</h3><p>What these visuals are allowed to mean.</p><div className="visual-control-list"><div><strong>{formatNumber(analytics.controlSummary.humanReview)}</strong><span>human-review records</span></div><div><strong>{formatNumber(analytics.controlSummary.lowEvidence)}</strong><span>evidence uplift records</span></div><div><strong>{formatNumber(analytics.controlSummary.supplierDataGaps)}</strong><span>supplier data gaps</span></div><div><strong>{humanise(analytics.controlSummary.boundary)}</strong><span>decision boundary</span></div></div></article>
      </div>

      <p className="governance-strip visual-governance-strip">These visuals rank screening records for operator attention. They do not override locked risk, review gate, evidence control, claim boundary, legal/compliance status or verified impact.</p>
    </section>
  );
}
