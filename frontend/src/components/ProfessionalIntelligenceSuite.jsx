import { useMemo, useState } from 'react';

import { formatCurrency, formatKg, formatNumber, humanise } from '../utils/formatters.js';

function safeRecords(dashboardData) {
  return dashboardData?.visualAnalytics?.drilldownRecords || [];
}

function sortByPriority(records) {
  return [...records].sort((a, b) => {
    const priorityDelta = Number(b.priority_score || 0) - Number(a.priority_score || 0);
    if (priorityDelta !== 0) return priorityDelta;
    return Number(b.estimated_annual_disposal_cost_avoided || 0) - Number(a.estimated_annual_disposal_cost_avoided || 0);
  });
}

function evidenceWeakness(record) {
  return Math.max(0, 100 - Number(record.evidence_quality_score || 0));
}

function classifyIssue(record) {
  const material = String(record.material || '').toLowerCase();
  const risk = record.risk_level || 'unknown';
  const hazardousMaterial = ['chemical', 'solvent', 'battery', 'electronics', 'weee', 'oil', 'residue'].some((term) => material.includes(term));

  if (['high', 'blocked'].includes(risk) || hazardousMaterial) {
    return {
      esg_theme: 'Pollution and hazardous material control',
      eia_issue_area: 'Waste, contamination and environmental management',
      receptor_or_concern: 'Potential environmental compliance, handling, storage or disposal sensitivity.',
      review_gate: 'Controlled environmental and compliance review required before action.',
    };
  }

  if (record.supplier_bucket === 'supplier_loop_candidate' || record.supplier_bucket === 'supplier_data_gap') {
    return {
      esg_theme: 'Circular procurement and supplier evidence',
      eia_issue_area: 'Supply-chain and materials management',
      receptor_or_concern: 'Supplier dependency, reverse-logistics feasibility and third-party evidence quality.',
      review_gate: 'Supplier evidence and commercial feasibility review required.',
    };
  }

  if (record.evidence_bucket === 'evidence_uplift') {
    return {
      esg_theme: 'Evidence readiness and claim control',
      eia_issue_area: 'Assessment evidence and reporting reliability',
      receptor_or_concern: 'Weak evidence may affect prioritisation, claim safety and implementation confidence.',
      review_gate: 'Evidence uplift required before claim, reporting or implementation decision.',
    };
  }

  if (material.includes('water') || material.includes('heat') || material.includes('energy')) {
    return {
      esg_theme: 'Resource efficiency and operational resilience',
      eia_issue_area: 'Resource use and operational efficiency',
      receptor_or_concern: 'Resource consumption, recovery potential and operational performance.',
      review_gate: 'Engineering feasibility and performance baseline review required.',
    };
  }

  return {
    esg_theme: 'Circular economy and resource efficiency',
    eia_issue_area: 'Waste hierarchy and materials management',
    receptor_or_concern: 'Material flow, waste hierarchy position and opportunity for value retention.',
    review_gate: record.human_review_required ? 'Human review required before action.' : 'Internal validation before implementation.',
  };
}

function buildIssueRegister(records) {
  return sortByPriority(records).map((record, index) => {
    const issue = classifyIssue(record);
    return {
      ...record,
      issue_id: `ISS-${String(index + 1).padStart(3, '0')}`,
      ...issue,
      evidence_required:
        record.evidence_bucket === 'evidence_uplift'
          ? 'Measured quantity, material specification, supplier documentation and action evidence.'
          : 'Maintain evidence trail, decision log and implementation records before making claims.',
      suggested_action: record.next_action || 'Review locked recommendation and collect missing evidence.',
      claim_boundary: 'Screening and internal decision support only. Do not present as verified impact or external claim.',
    };
  });
}

function scenarioScore(record, scenario) {
  const evidence = Number(record.evidence_quality_score || 0);
  const confidence = Number(record.confidence_score || 0);
  const priority = Number(record.priority_score || 0);
  const riskPenalty = record.risk_level === 'blocked' ? 45 : record.risk_level === 'high' ? 30 : record.risk_level === 'medium' ? 12 : 0;
  const reviewPenalty = record.human_review_required ? 18 : 0;
  const supplierBoost = record.supplier_bucket === 'supplier_loop_candidate' ? 14 : 0;
  const evidencePenalty = record.evidence_bucket === 'evidence_uplift' ? 18 : 0;

  const scenarioBias = {
    reduce_avoid: 14,
    internal_reuse: record.opportunity_bucket === 'quick_win' ? 16 : 8,
    supplier_takeback: supplierBoost,
    closed_loop_recycling: String(record.material || '').toLowerCase().includes('metal') ? 12 : 7,
    industrial_symbiosis: record.opportunity_bucket === 'developing' ? 13 : 6,
    recovery: record.risk_level === 'low' ? 5 : 2,
    controlled_disposal_fallback: record.human_review_required || ['high', 'blocked'].includes(record.risk_level) ? 18 : -8,
  }[scenario.key] || 0;

  return Math.max(0, Math.min(100, Math.round(priority * 0.45 + evidence * 0.24 + confidence * 0.18 + scenarioBias - riskPenalty - reviewPenalty - evidencePenalty)));
}

function buildScenarios(record) {
  if (!record) return [];

  const baseScenarios = [
    {
      key: 'reduce_avoid',
      label: 'Reduce / avoid at source',
      route: 'Prevention-first review',
      dependency: 'Process owner',
      complexity: 'Medium',
      evidence: 'Baseline quantity, cause analysis and post-change measurement.',
    },
    {
      key: 'internal_reuse',
      label: 'Internal reuse',
      route: 'Internal value-retention route',
      dependency: 'Operations and storage control',
      complexity: 'Low to medium',
      evidence: 'Reuse route, quality check and receiving process record.',
    },
    {
      key: 'supplier_takeback',
      label: 'Supplier take-back',
      route: 'Circular procurement / reverse logistics',
      dependency: 'Supplier and contract terms',
      complexity: 'Medium',
      evidence: 'Supplier confirmation, take-back terms and chain-of-custody evidence.',
    },
    {
      key: 'closed_loop_recycling',
      label: 'Closed-loop recycling',
      route: 'Material recovery with quality controls',
      dependency: 'Segregation and recycler evidence',
      complexity: 'Medium',
      evidence: 'Material grade, contamination check and recycler output evidence.',
    },
    {
      key: 'industrial_symbiosis',
      label: 'Industrial symbiosis',
      route: 'External by-product valorisation route',
      dependency: 'External partner and legal status review',
      complexity: 'High',
      evidence: 'By-product specification, recipient use case and compliance review.',
    },
    {
      key: 'recovery',
      label: 'Recovery',
      route: 'Lower-value fallback before disposal',
      dependency: 'Permitted recovery route',
      complexity: 'Medium',
      evidence: 'Recovery route evidence, permitting and mass-balance records.',
    },
    {
      key: 'controlled_disposal_fallback',
      label: 'Controlled disposal fallback',
      route: 'Compliance-first fallback route',
      dependency: 'Waste contractor and compliance records',
      complexity: 'Low to medium',
      evidence: 'Waste classification, transfer notes and disposal documentation.',
    },
  ];

  return baseScenarios
    .map((scenario) => {
      const score = scenarioScore(record, scenario);
      const reviewRequired = record.human_review_required || ['high', 'blocked'].includes(record.risk_level) || record.evidence_bucket === 'evidence_uplift';
      return {
        ...scenario,
        score,
        reviewRequired,
        claimSafety: reviewRequired
          ? 'No external claim. Use as screening route until evidence and review gates are closed.'
          : 'Internal validation route only. Do not claim verified impact until implementation evidence exists.',
      };
    })
    .sort((a, b) => b.score - a.score);
}

function MetricCard({ label, value, note }) {
  return (
    <article className="professional-metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function ExecutiveReport({ records, dashboardData }) {
  const sorted = sortByPriority(records);
  const quickWins = sorted.filter((record) => record.priority_band === 'quick win').slice(0, 5);
  const controlled = sorted.filter((record) => record.human_review_required || ['high', 'blocked'].includes(record.risk_level)).slice(0, 5);
  const evidenceGaps = sorted.filter((record) => record.evidence_bucket === 'evidence_uplift').slice(0, 5);
  const supplierActions = sorted.filter((record) => record.supplier_bucket === 'supplier_loop_candidate').slice(0, 5);

  return (
    <div className="professional-suite-panel">
      <div className="professional-report-grid">
        <MetricCard label="Records screened" value={formatNumber(records.length)} note="locked recommendation records" />
        <MetricCard label="Controlled review" value={formatNumber(controlled.length)} note="risk, evidence or review-gated records" />
        <MetricCard label="Screened exposure" value={formatCurrency(dashboardData.totalCostExposure)} note="not verified savings" />
        <MetricCard label="Diversion potential" value={formatKg(dashboardData.totalDiversionPotential)} note="screening estimate only" />
      </div>

      <article className="professional-briefing-card wide">
        <h3>Executive briefing</h3>
        <p>
          Circular Industry AI has screened operational material-flow records and converted them into controlled circular economy,
          ESG, EIA-style and sustainability intelligence outputs. The briefing below identifies where operators should focus
          attention first: high-priority opportunities, controlled reviews, evidence gaps and supplier-loop actions.
        </p>
        <p className="professional-governance-note">
          This report is an operator decision-support briefing. It does not verify savings, diversion, environmental benefit,
          supplier compliance, legal status or public claims.
        </p>
      </article>

      <ReportList title="Priority circular opportunities" records={quickWins} empty="No quick-win records currently identified." />
      <ReportList title="Controlled review priorities" records={controlled} empty="No controlled-review records currently identified." />
      <ReportList title="Evidence uplift actions" records={evidenceGaps} empty="No evidence-uplift records currently identified." />
      <ReportList title="Supplier-loop actions" records={supplierActions} empty="No supplier-loop candidate records currently identified." />
    </div>
  );
}

function ReportList({ title, records, empty }) {
  return (
    <article className="professional-briefing-card">
      <h3>{title}</h3>
      {!records.length && <p className="muted">{empty}</p>}
      <div className="professional-record-stack">
        {records.map((record) => (
          <div className="professional-record-row" key={`${title}-${record.stream_id}`}>
            <div>
              <span className="record-id">{record.stream_id}</span>
              <strong>{record.stream_name}</strong>
              <small>{record.material} · {record.risk_level} risk · evidence {record.evidence_quality_score}/100</small>
            </div>
            <div className="professional-row-value">
              <strong>{formatCurrency(record.estimated_annual_disposal_cost_avoided)}</strong>
              <small>{formatKg(record.estimated_annual_waste_diverted_kg)}</small>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function IssueRegister({ records, onSelectReviewPack }) {
  const issues = useMemo(() => buildIssueRegister(records), [records]);
  const [selectedId, setSelectedId] = useState(issues[0]?.issue_id || '');
  const selected = issues.find((issue) => issue.issue_id === selectedId) || issues[0];

  return (
    <div className="professional-suite-panel">
      <div className="professional-register-layout">
        <div className="professional-register-list">
          <div className="professional-list-header">
            <strong>ESG / EIA issue register</strong>
            <small>{formatNumber(issues.length)} derived screening issues</small>
          </div>
          {issues.map((issue) => (
            <button
              type="button"
              className={`professional-list-row ${selected?.issue_id === issue.issue_id ? 'selected' : ''}`}
              key={issue.issue_id}
              onClick={() => setSelectedId(issue.issue_id)}
            >
              <span className="record-id">{issue.issue_id} · {issue.stream_id}</span>
              <strong>{issue.esg_theme}</strong>
              <small>{issue.stream_name}</small>
            </button>
          ))}
        </div>

        <IssueInspector issue={selected} onSelectReviewPack={onSelectReviewPack} />
      </div>
    </div>
  );
}

function IssueInspector({ issue, onSelectReviewPack }) {
  if (!issue) {
    return <aside className="professional-inspector empty"><h3>Select an issue</h3><p>No issue selected.</p></aside>;
  }

  return (
    <aside className="professional-inspector">
      <div className="professional-inspector-header">
        <div>
          <span className="record-id">{issue.issue_id} · {issue.stream_id}</span>
          <h3>{issue.stream_name}</h3>
          <p>{issue.material} · {issue.department} · Supplier: {issue.supplier}</p>
        </div>
        {onSelectReviewPack && (
          <button type="button" className="secondary-button" onClick={() => onSelectReviewPack(issue.stream_id)}>
            Review pack
          </button>
        )}
      </div>

      <div className="professional-kpi-grid">
        <article><span>Risk</span><strong>{issue.risk_level}</strong></article>
        <article><span>Evidence</span><strong>{issue.evidence_quality_score}/100</strong></article>
        <article><span>Review</span><strong>{issue.human_review_required ? 'Required' : 'Internal validation'}</strong></article>
        <article><span>Priority</span><strong>{issue.priority_band}</strong></article>
      </div>

      <DetailBlock label="ESG theme" value={issue.esg_theme} />
      <DetailBlock label="EIA-style issue area" value={issue.eia_issue_area} />
      <DetailBlock label="Potential receptor / concern" value={issue.receptor_or_concern} />
      <DetailBlock label="Review gate" value={issue.review_gate} />
      <DetailBlock label="Evidence required" value={issue.evidence_required} />
      <DetailBlock label="Suggested action" value={issue.suggested_action} />
      <DetailBlock label="Claim boundary" value={issue.claim_boundary} warning />
    </aside>
  );
}

function DetailBlock({ label, value, warning = false }) {
  return (
    <div className={`professional-detail-block ${warning ? 'warning' : ''}`}>
      <span>{label}</span>
      <p>{value}</p>
    </div>
  );
}

function ScenarioComparison({ records, onSelectReviewPack }) {
  const sorted = sortByPriority(records);
  const [selectedId, setSelectedId] = useState(sorted[0]?.stream_id || '');
  const selected = sorted.find((record) => record.stream_id === selectedId) || sorted[0];
  const scenarios = useMemo(() => buildScenarios(selected), [selected]);

  return (
    <div className="professional-suite-panel">
      <div className="professional-scenario-layout">
        <div className="professional-register-list compact">
          <div className="professional-list-header">
            <strong>Scenario records</strong>
            <small>Select a stream to compare routes</small>
          </div>
          {sorted.slice(0, 18).map((record) => (
            <button
              type="button"
              className={`professional-list-row ${selected?.stream_id === record.stream_id ? 'selected' : ''}`}
              key={record.stream_id}
              onClick={() => setSelectedId(record.stream_id)}
            >
              <span className="record-id">{record.stream_id}</span>
              <strong>{record.stream_name}</strong>
              <small>{record.material} · {formatCurrency(record.estimated_annual_disposal_cost_avoided)}</small>
            </button>
          ))}
        </div>

        <div className="scenario-comparison-panel">
          {selected && (
            <div className="professional-inspector-header scenario-heading">
              <div>
                <span className="record-id">{selected.stream_id}</span>
                <h3>{selected.stream_name}</h3>
                <p>{selected.material} · {selected.department} · {selected.risk_level} risk · evidence {selected.evidence_quality_score}/100</p>
              </div>
              {onSelectReviewPack && (
                <button type="button" className="secondary-button" onClick={() => onSelectReviewPack(selected.stream_id)}>
                  Review pack
                </button>
              )}
            </div>
          )}

          <div className="scenario-card-grid">
            {scenarios.map((scenario) => (
              <article className="scenario-comparison-card" key={scenario.key}>
                <div className="scenario-card-topline">
                  <div>
                    <h4>{scenario.label}</h4>
                    <span>{scenario.route}</span>
                  </div>
                  <strong>{scenario.score}</strong>
                </div>
                <div className="scenario-mini-grid">
                  <div><span>Complexity</span><strong>{scenario.complexity}</strong></div>
                  <div><span>Dependency</span><strong>{scenario.dependency}</strong></div>
                  <div><span>Review</span><strong>{scenario.reviewRequired ? 'Required' : 'Internal validation'}</strong></div>
                </div>
                <p><b>Evidence:</b> {scenario.evidence}</p>
                <p className="professional-governance-note"><b>Claim safety:</b> {scenario.claimSafety}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ProfessionalIntelligenceSuite({ dashboardData, onSelectReviewPack }) {
  const records = safeRecords(dashboardData);
  const [activeView, setActiveView] = useState('report');

  if (!records.length) return null;

  const views = [
    { key: 'report', label: 'Executive report' },
    { key: 'issues', label: 'ESG / EIA issue register' },
    { key: 'scenarios', label: 'Scenario comparison' },
  ];

  return (
    <section className="professional-suite-section">
      <div className="section-heading professional-suite-heading">
        <div>
          <h2>Professional intelligence suite</h2>
          <p>
            Executive reporting, ESG/EIA-style issue classification and scenario comparison built from locked screening records.
          </p>
        </div>
        <span>12D/E/F suite</span>
      </div>

      <div className="professional-suite-tabs" role="tablist" aria-label="Professional intelligence suite views">
        {views.map((view) => (
          <button
            type="button"
            key={view.key}
            className={`professional-suite-tab ${activeView === view.key ? 'active' : ''}`}
            onClick={() => setActiveView(view.key)}
          >
            {view.label}
          </button>
        ))}
      </div>

      {activeView === 'report' && <ExecutiveReport records={records} dashboardData={dashboardData} />}
      {activeView === 'issues' && <IssueRegister records={records} onSelectReviewPack={onSelectReviewPack} />}
      {activeView === 'scenarios' && <ScenarioComparison records={records} onSelectReviewPack={onSelectReviewPack} />}

      <p className="governance-strip professional-suite-governance">
        This suite organises locked screening outputs into operator-facing professional intelligence. It does not change the rules-engine decision record or verify claims, savings, diversion, environmental benefit, legal status or supplier compliance.
      </p>
    </section>
  );
}
