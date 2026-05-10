import { useMemo, useState } from 'react';

import { formatCurrency, formatKg, formatNumber, humanise } from '../utils/formatters.js';

function EmptyVisual({ text = 'Run recommendations to populate this visual.' }) {
  return <p className="visual-empty">{text}</p>;
}

function makeSlice({ id, title, type, ...rest }) {
  return { id, title, type, ...rest };
}

function sliceMatchesRecord(slice, record) {
  if (!slice || !record) return false;

  if (slice.type === 'matrix') {
    return record.risk_level === slice.risk && record.opportunity_bucket === slice.opportunity;
  }
  if (slice.type === 'material') {
    return record.material === slice.material;
  }
  if (slice.type === 'cost') {
    return record.stream_id === slice.stream_id;
  }
  if (slice.type === 'evidence') {
    return record.evidence_bucket === slice.bucket;
  }
  if (slice.type === 'claim') {
    return record.claim_bucket === slice.bucket;
  }
  if (slice.type === 'supplier') {
    return record.supplier_bucket === slice.bucket;
  }
  if (slice.type === 'scenario') {
    return record.stream_id === slice.stream_id;
  }

  return false;
}

function sortRecords(records, mode) {
  const sorted = [...records];
  const selectors = {
    priority: (record) => Number(record.priority_score) || 0,
    cost: (record) => Number(record.estimated_annual_disposal_cost_avoided) || 0,
    evidence_weakness: (record) => 100 - (Number(record.evidence_quality_score) || 0),
    diversion: (record) => Number(record.estimated_annual_waste_diverted_kg) || 0,
  };
  const selector = selectors[mode] || selectors.priority;
  return sorted.sort((a, b) => selector(b) - selector(a));
}

function VisualBarList({ rows = [], formatter = formatNumber, selectedSlice, onSelectSlice, getSlice }) {
  const max = Math.max(...rows.map((row) => Number(row.value) || 0), 0);
  if (!rows.length) return <EmptyVisual />;

  return (
    <div className="visual-bar-list">
      {rows.slice(0, 8).map((row) => {
        const value = Number(row.value) || 0;
        const width = max > 0 ? Math.max((value / max) * 100, 4) : 4;
        const slice = getSlice(row);
        const selected = selectedSlice?.id === slice.id;

        return (
          <button
            type="button"
            className={`visual-bar-row visual-select-row ${selected ? 'selected' : ''}`}
            key={row.bucket || row.label}
            onClick={() => onSelectSlice(slice)}
          >
            <div className="visual-bar-label">
              <span>{row.label}</span>
              <strong>{formatter(value)}</strong>
            </div>
            <div className="visual-bar-track"><span style={{ width: `${width}%` }} /></div>
          </button>
        );
      })}
    </div>
  );
}

function ParetoList({ rows = [], formatter, selectedSlice, onSelectSlice, getSlice }) {
  if (!rows.length) return <EmptyVisual />;

  return (
    <div className="pareto-list">
      {rows.slice(0, 8).map((row, index) => {
        const slice = getSlice(row);
        const selected = selectedSlice?.id === slice.id;

        return (
          <button
            type="button"
            className={`pareto-row visual-select-row ${selected ? 'selected' : ''}`}
            key={`${row.label}-${index}`}
            onClick={() => onSelectSlice(slice)}
          >
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
          </button>
        );
      })}
    </div>
  );
}

function RiskOpportunityMatrix({ matrix, selectedSlice, onSelectSlice }) {
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
            const slice = makeSlice({
              id: `matrix:${row.key}:${column.key}`,
              title: `${row.label} risk · ${column.label}`,
              type: 'matrix',
              risk: row.key,
              opportunity: column.key,
            });
            const selected = selectedSlice?.id === slice.id;

            return (
              <button
                type="button"
                className={`matrix-cell chart-select-button ${cell.count ? 'active' : ''} ${selected ? 'selected' : ''}`}
                style={{ '--cell-intensity': cell.count / max }}
                key={`${row.key}-${column.key}`}
                onClick={() => onSelectSlice(slice)}
                title="Inspect matrix cell"
              >
                <strong>{cell.count}</strong>
                <small>{formatCurrency(cell.exposure)}</small>
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function EvidenceDonut({ rows = [], total = 0, selectedSlice, onSelectSlice }) {
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
        {rows.map((row) => {
          const slice = makeSlice({
            id: `evidence:${row.bucket}`,
            title: row.label,
            type: 'evidence',
            bucket: row.bucket,
          });
          const selected = selectedSlice?.id === slice.id;

          return (
            <button
              type="button"
              className={`donut-legend-row visual-select-row ${selected ? 'selected' : ''}`}
              key={row.label}
              onClick={() => onSelectSlice(slice)}
            >
              <span style={{ background: row.tone }} />
              <div><strong>{row.label}</strong><small>{formatNumber(row.value)} records</small></div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function ScenarioPanel({ items = [], selectedSlice, onSelectSlice, onSelectReviewPack }) {
  if (!items.length) return <EmptyVisual text="No scenario candidates yet. Run recommendations first." />;

  return (
    <div className="scenario-list">
      {items.map((item) => {
        const slice = makeSlice({
          id: `scenario:${item.stream_id}`,
          title: `Scenario candidate · ${item.stream_id}`,
          type: 'scenario',
          stream_id: item.stream_id,
        });
        const selected = selectedSlice?.id === slice.id;

        return (
          <article className={`scenario-card ${selected ? 'selected' : ''}`} key={item.stream_id}>
            <div>
              <span className="record-id">{item.stream_id}</span>
              <h4>{item.stream_name}</h4>
              <p>{item.scenario}</p>
            </div>
            <div className="scenario-score">
              <strong>{item.priority_score}</strong>
              <small>screening score</small>
              <button type="button" className="link-button compact" onClick={() => onSelectSlice(slice)}>Inspect</button>
              {onSelectReviewPack && <button type="button" className="link-button compact" onClick={() => onSelectReviewPack(item.stream_id)}>Review</button>}
            </div>
          </article>
        );
      })}
    </div>
  );
}

function DrilldownListRow({ record, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`drilldown-list-row ${selected ? 'selected' : ''}`}
      onClick={() => onSelect(record.stream_id)}
    >
      <div>
        <span className="record-id">{record.stream_id}</span>
        <strong>{record.stream_name}</strong>
        <small>{record.priority_band} · {record.risk_level}</small>
      </div>
      <div className="drilldown-row-metrics">
        <strong>{record.evidence_quality_score}/100</strong>
        <small>{formatCurrency(record.estimated_annual_disposal_cost_avoided)}</small>
      </div>
    </button>
  );
}

function DrilldownInspector({ record, onSelectReviewPack }) {
  if (!record) {
    return (
      <aside className="drilldown-inspector empty">
        <h3>Select a record</h3>
        <p>Choose an item from the compact list to inspect the locked risk, evidence, supplier and action signals.</p>
      </aside>
    );
  }

  return (
    <aside className="drilldown-inspector">
      <div className="drilldown-inspector-header">
        <div>
          <span className="record-id">{record.stream_id}</span>
          <h3>{record.stream_name}</h3>
          <p>{record.material} · {record.department} · Supplier: {record.supplier}</p>
        </div>
        {onSelectReviewPack && (
          <button type="button" className="secondary-button" onClick={() => onSelectReviewPack(record.stream_id)}>
            Review pack
          </button>
        )}
      </div>

      <div className="drilldown-kpi-grid">
        <article><span>Locked risk</span><strong>{record.risk_level}</strong><small>Review: {record.human_review_required ? 'required' : 'clear'}</small></article>
        <article><span>Evidence quality</span><strong>{record.evidence_quality_score}/100</strong><small>Confidence: {record.confidence_score}/100</small></article>
        <article><span>Screened cost exposure</span><strong>{formatCurrency(record.estimated_annual_disposal_cost_avoided)}</strong><small>Not verified savings</small></article>
        <article><span>Screened diversion</span><strong>{formatKg(record.estimated_annual_waste_diverted_kg)}</strong><small>Not verified impact</small></article>
      </div>

      <div className="drilldown-detail-box">
        <span>Recommended circular action</span>
        <p>{record.recommended_circular_action}</p>
      </div>

      <div className="drilldown-detail-box">
        <span>Next action</span>
        <p>{record.next_action}</p>
      </div>

      <div className="drilldown-detail-grid">
        <div><span>Opportunity bucket</span><strong>{record.opportunity_label}</strong></div>
        <div><span>Evidence bucket</span><strong>{record.evidence_label}</strong></div>
        <div><span>Claim bucket</span><strong>{record.claim_label}</strong></div>
        <div><span>Supplier bucket</span><strong>{record.supplier_label}</strong></div>
      </div>

      <p className="governance-strip drilldown-governance">
        This drilldown is an operator triage view. It does not change the locked decision record or validate claims.
      </p>
    </aside>
  );
}

function OperatorDrilldownPanel({
  selectedSlice,
  records,
  selectedRecordId,
  onSelectRecord,
  sortMode,
  onSortModeChange,
  onSelectReviewPack,
}) {
  if (!selectedSlice) {
    return (
      <section className="operator-drilldown-panel" id="operator-drilldown-panel">
        <div className="drilldown-empty">
          <h3>Operator drilldown</h3>
          <p>Select a matrix cell, Pareto row, evidence segment, claim-readiness group, supplier-loop category or scenario candidate to inspect the underlying records.</p>
        </div>
      </section>
    );
  }

  const selectedRecord = records.find((record) => record.stream_id === selectedRecordId) || records[0] || null;

  return (
    <section className="operator-drilldown-panel" id="operator-drilldown-panel">
      <div className="drilldown-summary">
        <div>
          <span className="eyebrow">Operator drilldown</span>
          <h3>{selectedSlice.title}</h3>
          <p>This is a screening and triage view. Use it to identify the records behind the visual signal, then move into the review pack for decision detail.</p>
        </div>
        <div className="drilldown-summary-count">
          <strong>{formatNumber(records.length)}</strong>
          <span>matching records</span>
        </div>
      </div>

      <div className="drilldown-toolbar">
        <label>
          Sort records
          <select value={sortMode} onChange={(event) => onSortModeChange(event.target.value)}>
            <option value="priority">Priority score</option>
            <option value="cost">Screened cost exposure</option>
            <option value="evidence_weakness">Evidence weakness</option>
            <option value="diversion">Screened diversion</option>
          </select>
        </label>
      </div>

      {records.length ? (
        <div className="drilldown-layout">
          <div className="drilldown-list">
            {records.map((record) => (
              <DrilldownListRow
                key={record.stream_id}
                record={record}
                selected={selectedRecord?.stream_id === record.stream_id}
                onSelect={onSelectRecord}
              />
            ))}
          </div>
          <DrilldownInspector record={selectedRecord} onSelectReviewPack={onSelectReviewPack} />
        </div>
      ) : (
        <div className="drilldown-empty">
          <h3>No matching records</h3>
          <p>This visual slice has no matching records in the current screening dataset.</p>
        </div>
      )}
    </section>
  );
}

export default function VisualAnalyticsDashboard({ analytics, onSelectReviewPack }) {
  const [selectedSlice, setSelectedSlice] = useState(null);
  const [selectedRecordId, setSelectedRecordId] = useState('');
  const [sortMode, setSortMode] = useState('priority');

  const drilldownRecords = analytics?.drilldownRecords || [];

  const getRecordsForSlice = (slice) => drilldownRecords.filter((record) => sliceMatchesRecord(slice, record));

  const selectedRecords = useMemo(() => {
    if (!selectedSlice) return [];
    return sortRecords(getRecordsForSlice(selectedSlice), sortMode);
  }, [selectedSlice, drilldownRecords, sortMode]);

  function handleSelectSlice(slice) {
    const records = sortRecords(getRecordsForSlice(slice), sortMode);
    setSelectedSlice(slice);
    setSelectedRecordId(records[0]?.stream_id || '');
    window.setTimeout(() => {
      document.getElementById('operator-drilldown-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 0);
  }

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
        <article className="visual-card visual-card-wide">
          <h3>Risk vs opportunity matrix</h3>
          <p>Count and screened value exposure by locked risk level and opportunity strength.</p>
          <RiskOpportunityMatrix matrix={analytics.matrix} selectedSlice={selectedSlice} onSelectSlice={handleSelectSlice} />
        </article>

        <article className="visual-card">
          <h3>Evidence maturity</h3>
          <p>Whether records are strong enough for action planning or need evidence uplift.</p>
          <EvidenceDonut rows={analytics.evidenceMaturity} total={analytics.totalRecords} selectedSlice={selectedSlice} onSelectSlice={handleSelectSlice} />
        </article>

        <article className="visual-card">
          <h3>Claim-readiness control</h3>
          <p>Screening proxy based on evidence score, risk and human-review gate.</p>
          <VisualBarList
            rows={analytics.claimReadiness}
            selectedSlice={selectedSlice}
            onSelectSlice={handleSelectSlice}
            getSlice={(row) => makeSlice({ id: `claim:${row.bucket}`, title: row.label, type: 'claim', bucket: row.bucket })}
          />
        </article>

        <article className="visual-card visual-card-wide">
          <h3>Material quantity Pareto</h3>
          <p>Largest annual material-flow groups by screened quantity.</p>
          <ParetoList
            rows={analytics.materialPareto}
            formatter={formatKg}
            selectedSlice={selectedSlice}
            onSelectSlice={handleSelectSlice}
            getSlice={(row) => makeSlice({ id: `material:${row.material}`, title: `Material flow · ${row.material}`, type: 'material', material: row.material })}
          />
        </article>

        <article className="visual-card visual-card-wide">
          <h3>Cost exposure Pareto</h3>
          <p>Largest screened disposal-cost exposure records. Not verified savings.</p>
          <ParetoList
            rows={analytics.costPareto}
            formatter={formatCurrency}
            selectedSlice={selectedSlice}
            onSelectSlice={handleSelectSlice}
            getSlice={(row) => makeSlice({ id: `cost:${row.stream_id}`, title: `Cost exposure · ${row.label}`, type: 'cost', stream_id: row.stream_id })}
          />
        </article>

        <article className="visual-card">
          <h3>Supplier-loop opportunity profile</h3>
          <p>Supplier-facing routes split into candidate, controlled-review and supplier-data-gap groups.</p>
          <VisualBarList
            rows={analytics.supplierLoopProfile}
            selectedSlice={selectedSlice}
            onSelectSlice={handleSelectSlice}
            getSlice={(row) => makeSlice({ id: `supplier:${row.bucket}`, title: row.label, type: 'supplier', bucket: row.bucket })}
          />
        </article>

        <article className="visual-card visual-card-wide">
          <h3>Scenario screening panel</h3>
          <p>Compact triage list for the next operator action.</p>
          <ScenarioPanel
            items={analytics.scenarioItems}
            selectedSlice={selectedSlice}
            onSelectSlice={handleSelectSlice}
            onSelectReviewPack={onSelectReviewPack}
          />
        </article>

        <article className="visual-card">
          <h3>Decision controls</h3>
          <p>What these visuals are allowed to mean.</p>
          <div className="visual-control-list">
            <div><strong>{formatNumber(analytics.controlSummary.humanReview)}</strong><span>human-review records</span></div>
            <div><strong>{formatNumber(analytics.controlSummary.lowEvidence)}</strong><span>evidence uplift records</span></div>
            <div><strong>{formatNumber(analytics.controlSummary.supplierDataGaps)}</strong><span>supplier data gaps</span></div>
            <div><strong>{humanise(analytics.controlSummary.boundary)}</strong><span>decision boundary</span></div>
          </div>
        </article>
      </div>

      <OperatorDrilldownPanel
        selectedSlice={selectedSlice}
        records={selectedRecords}
        selectedRecordId={selectedRecordId}
        onSelectRecord={setSelectedRecordId}
        sortMode={sortMode}
        onSortModeChange={setSortMode}
        onSelectReviewPack={onSelectReviewPack}
      />

      <p className="governance-strip visual-governance-strip">These visuals rank screening records for operator attention. They do not override locked risk, review gate, evidence control, claim boundary, legal/compliance status or verified impact.</p>
    </section>
  );
}

