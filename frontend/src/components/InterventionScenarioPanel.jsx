import { useEffect, useMemo, useState } from 'react';

import { RiskBadge, ReviewBadge, ScoreBadge } from './Badges.jsx';
import { formatCurrency, formatKg, humanise } from '../utils/formatters.js';

const DEFAULT_ASSUMPTIONS = {
  addressable_fraction_pct: '80',
  technical_capture_rate_pct: '85',
  route_acceptance_rate_pct: '90',
  operator_note: '',
};

const DEFAULT_COMPARISON_CASES = [
  {
    case_name: 'Conservative',
    addressable_fraction_pct: '50',
    technical_capture_rate_pct: '60',
    route_acceptance_rate_pct: '70',
    operator_note: '',
  },
  {
    case_name: 'Working',
    addressable_fraction_pct: '80',
    technical_capture_rate_pct: '85',
    route_acceptance_rate_pct: '90',
    operator_note: '',
  },
  {
    case_name: 'Upper-screen',
    addressable_fraction_pct: '95',
    technical_capture_rate_pct: '95',
    route_acceptance_rate_pct: '95',
    operator_note: '',
  },
];

function ScenarioMetric({ label, value, helper }) {
  return (
    <article className="scenario-metric">
      <span>{label}</span>
      <strong>{value}</strong>
      {helper ? <small>{helper}</small> : null}
    </article>
  );
}

function AssumptionInput({ label, helper, value, onChange, disabled }) {
  return (
    <label className="scenario-input">
      <span>{label}</span>
      <input
        type="number"
        min="0"
        max="100"
        step="1"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        inputMode="decimal"
      />
      <small>{helper}</small>
    </label>
  );
}

export default function InterventionScenarioPanel({
  streams,
  recommendations,
  scenarioResult,
  comparisonResult,
  onRunScenario,
  onCompareScenarios,
  busy,
}) {
  const [selectedId, setSelectedId] = useState('');
  const [assumptions, setAssumptions] = useState(DEFAULT_ASSUMPTIONS);
  const [comparisonCases, setComparisonCases] = useState(DEFAULT_COMPARISON_CASES);
  const [localError, setLocalError] = useState('');
  const [comparisonError, setComparisonError] = useState('');

  useEffect(() => {
    if (!selectedId && recommendations.length) {
      setSelectedId(recommendations[0].stream_id);
    }
  }, [recommendations, selectedId]);

  const streamLookup = useMemo(
    () => Object.fromEntries(streams.map((stream) => [stream.stream_id, stream])),
    [streams],
  );

  const selectedRecommendation = useMemo(
    () => recommendations.find((rec) => rec.stream_id === selectedId) || null,
    [recommendations, selectedId],
  );

  const selectedStream = selectedRecommendation ? streamLookup[selectedRecommendation.stream_id] : null;
  const resultMatchesSelection = scenarioResult?.stream_id === selectedId;
  const comparisonMatchesSelection = comparisonResult?.stream_id === selectedId;

  function updateAssumption(key, value) {
    setAssumptions((current) => ({ ...current, [key]: value }));
    setLocalError('');
  }

  function updateComparisonCase(index, key, value) {
    setComparisonCases((current) => current.map((item, itemIndex) => (
      itemIndex === index ? { ...item, [key]: value } : item
    )));
    setComparisonError('');
  }

  async function submitComparison() {
    setComparisonError('');

    if (!selectedId) {
      setComparisonError('Select a stream before comparing scenario cases.');
      return;
    }

    const names = comparisonCases.map((item) => item.case_name.trim());
    if (names.some((name) => !name)) {
      setComparisonError('Each comparison case needs a name.');
      return;
    }
    if (new Set(names.map((name) => name.toLowerCase())).size !== names.length) {
      setComparisonError('Comparison case names must be unique.');
      return;
    }

    const numericFields = [
      'addressable_fraction_pct',
      'technical_capture_rate_pct',
      'route_acceptance_rate_pct',
    ];

    const cases = [];
    for (const item of comparisonCases) {
      const prepared = {
        case_name: item.case_name.trim(),
        operator_note: item.operator_note.trim() || null,
      };
      for (const field of numericFields) {
        const value = Number(item[field]);
        if (!Number.isFinite(value) || value < 0 || value > 100) {
          setComparisonError('Every comparison percentage must be a number between 0 and 100.');
          return;
        }
        prepared[field] = value;
      }
      cases.push(prepared);
    }

    try {
      await onCompareScenarios(selectedId, { cases });
    } catch {
      // App-level status reporting already surfaces the API error.
    }
  }

  async function submitScenario(event) {
    event.preventDefault();
    setLocalError('');

    const numericFields = [
      'addressable_fraction_pct',
      'technical_capture_rate_pct',
      'route_acceptance_rate_pct',
    ];

    const payload = { operator_note: assumptions.operator_note.trim() || null };

    for (const field of numericFields) {
      const value = Number(assumptions[field]);
      if (!Number.isFinite(value) || value < 0 || value > 100) {
        setLocalError('Each scenario percentage must be a number between 0 and 100.');
        return;
      }
      payload[field] = value;
    }

    if (!selectedId) {
      setLocalError('Select a stream before running the scenario.');
      return;
    }

    try {
      await onRunScenario(selectedId, payload);
    } catch {
      // App-level status reporting already surfaces the API error.
    }
  }

  return (
    <section className="scenario-panel">
      <div className="section-heading">
        <div>
          <h2>Intervention scenario screening</h2>
          <p>
            Test a candidate circular route using explicit operator assumptions. The output is screening potential,
            not measured diversion or verified savings.
          </p>
        </div>
        <span>Milestone 20B</span>
      </div>

      <div className="scenario-layout">
        <form className="scenario-builder" onSubmit={submitScenario}>
          <div className="scenario-builder-heading">
            <div>
              <span className="eyebrow dark-eyebrow">Scenario inputs</span>
              <h3>Build a screening case</h3>
            </div>
            <small>Assumptions are editable and only applied when you click Run scenario.</small>
          </div>

          <label className="scenario-select">
            <span>Stream and locked recommendation</span>
            <select
              value={selectedId}
              onChange={(event) => {
                setSelectedId(event.target.value);
                setLocalError('');
              }}
              disabled={busy}
            >
              {recommendations.map((rec) => {
                const stream = streamLookup[rec.stream_id];
                return (
                  <option key={rec.stream_id} value={rec.stream_id}>
                    {rec.stream_id} · {stream?.stream_name || rec.recommended_circular_action}
                  </option>
                );
              })}
            </select>
          </label>

          {selectedRecommendation && (
            <div className="scenario-locked-route">
              <span>Locked candidate route</span>
              <strong>{selectedRecommendation.recommended_circular_action}</strong>
              <p>{selectedRecommendation.circular_strategy_category}</p>
              <div className="scenario-route-badges">
                <RiskBadge value={selectedRecommendation.risk_level} />
                <ReviewBadge required={selectedRecommendation.human_review_required} />
              </div>
            </div>
          )}

          <div className="scenario-input-grid">
            <AssumptionInput
              label="Addressable fraction (%)"
              helper="Share of the annual stream that the intervention could realistically address."
              value={assumptions.addressable_fraction_pct}
              onChange={(value) => updateAssumption('addressable_fraction_pct', value)}
              disabled={busy}
            />
            <AssumptionInput
              label="Technical capture rate (%)"
              helper="Share of addressable material assumed technically capturable."
              value={assumptions.technical_capture_rate_pct}
              onChange={(value) => updateAssumption('technical_capture_rate_pct', value)}
              disabled={busy}
            />
            <AssumptionInput
              label="Route acceptance rate (%)"
              helper="Share of captured material assumed accepted by the route or supplier."
              value={assumptions.route_acceptance_rate_pct}
              onChange={(value) => updateAssumption('route_acceptance_rate_pct', value)}
              disabled={busy}
            />
          </div>

          <label className="scenario-note">
            <span>Operator note (optional)</span>
            <textarea
              value={assumptions.operator_note}
              onChange={(event) => updateAssumption('operator_note', event.target.value)}
              placeholder="Why are these assumptions reasonable for this screening case?"
              rows="3"
              disabled={busy}
            />
          </label>

          {selectedStream && (
            <div className="scenario-baseline-preview">
              <div>
                <span>Baseline annual quantity</span>
                <strong>{formatKg(Number(selectedStream.monthly_quantity_kg || 0) * 12)}</strong>
              </div>
              <div>
                <span>Annual disposal-cost exposure</span>
                <strong>{formatCurrency(Number(selectedStream.disposal_cost_per_month || 0) * 12)}</strong>
              </div>
            </div>
          )}

          {localError && <p className="error">{localError}</p>}

          <button type="submit" disabled={busy || !selectedId}>
            {busy ? 'Running scenario…' : 'Run scenario'}
          </button>
        </form>

        <aside className="scenario-result">
          {scenarioResult && !resultMatchesSelection && (
            <div className="scenario-stale-result-note">
              Last result shown is for {scenarioResult.stream_id}. Run the scenario for {selectedId} to replace it.
            </div>
          )}
          {!scenarioResult ? (
            <div className="scenario-empty">
              <span className="eyebrow dark-eyebrow">No scenario run yet</span>
              <h3>Screen intervention potential</h3>
              <p>
                Select a stream, review the locked route, enter assumptions and run the scenario. Results will remain
                bounded by the recommendation's risk and human-review controls.
              </p>
            </div>
          ) : (
            <>
              <div className="scenario-result-header">
                <div>
                  <span className="record-id">{scenarioResult.stream_id}</span>
                  <h3>{scenarioResult.stream_name}</h3>
                  <p>{scenarioResult.material}</p>
                </div>
                <div className="scenario-route-badges">
                  <RiskBadge value={scenarioResult.risk_level} />
                  <ReviewBadge required={scenarioResult.human_review_required} />
                </div>
              </div>

              <div className="scenario-primary-result">
                <span>Scenario-screened recoverable quantity</span>
                <strong>{formatKg(scenarioResult.scenario_screened_recoverable_quantity_kg)}</strong>
                <small>{scenarioResult.scenario_screened_fraction_pct}% of baseline annual quantity under this assumption set</small>
              </div>

              <div className="scenario-metric-grid">
                <ScenarioMetric
                  label="Baseline quantity"
                  value={formatKg(scenarioResult.baseline_annual_quantity_kg)}
                  helper="Annual stream quantity at stake"
                />
                <ScenarioMetric
                  label="Cost exposure"
                  value={formatCurrency(scenarioResult.baseline_annual_disposal_cost_exposure)}
                  helper="Current exposure, not scenario savings"
                />
                <ScenarioMetric
                  label="Confidence"
                  value={`${scenarioResult.recommendation_confidence_score}/100`}
                  helper="Locked recommendation confidence"
                />
                <ScenarioMetric
                  label="Evidence"
                  value={`${scenarioResult.evidence_quality_score}/100`}
                  helper="Evidence quality score"
                />
              </div>

              <div className="scenario-decision-box">
                <span>Scenario status</span>
                <strong>{humanise(scenarioResult.scenario_status)}</strong>
                <p>{scenarioResult.candidate_route}</p>
              </div>

              <div className="scenario-score-row">
                <ScoreBadge label="Confidence" value={scenarioResult.recommendation_confidence_score} />
                <ScoreBadge label="Evidence" value={scenarioResult.evidence_quality_score} />
              </div>

              <div className="scenario-detail-block">
                <h4>Assumptions used</h4>
                <ul>
                  {scenarioResult.assumptions.map((item, index) => (
                    <li key={`scenario-assumption-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="scenario-detail-block">
                <h4>Evidence needed</h4>
                <ul>
                  {scenarioResult.evidence_needed.map((item, index) => (
                    <li key={`scenario-evidence-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="scenario-formula">
                <span>Formula</span>
                <code>{scenarioResult.formula}</code>
              </div>

              <div className="governance-strip">
                <strong>{humanise(scenarioResult.claim_status)}</strong>
                <p>{scenarioResult.governance_note}</p>
              </div>
            </>
          )}
        </aside>
      </div>\n\n      <section className="scenario-comparison-section">\n        <div className="section-heading compact-heading">\n          <div>\n            <h3>Compare assumption cases</h3>\n            <p>\n              Compare three editable screening cases for the same stream and locked route. The starting values are illustrative only;\n              replace them with evidence-backed assumptions before relying on the comparison.\n            </p>\n          </div>\n          <span>3 explicit cases</span>\n        </div>\n\n        <div className="scenario-comparison-inputs">\n          {comparisonCases.map((item, index) => (\n            <article className="scenario-case-builder" key={index}>\n              <label>\n                <span>Case name</span>\n                <input\n                  type="text"\n                  value={item.case_name}\n                  onChange={(event) => updateComparisonCase(index, 'case_name', event.target.value)}\n                  disabled={busy}\n                />\n              </label>\n              <div className="scenario-case-number-grid">\n                <label>\n                  <span>Addressable %</span>\n                  <input\n                    type="number"\n                    min="0"\n                    max="100"\n                    value={item.addressable_fraction_pct}\n                    onChange={(event) => updateComparisonCase(index, 'addressable_fraction_pct', event.target.value)}\n                    disabled={busy}\n                  />\n                </label>\n                <label>\n                  <span>Capture %</span>\n                  <input\n                    type="number"\n                    min="0"\n                    max="100"\n                    value={item.technical_capture_rate_pct}\n                    onChange={(event) => updateComparisonCase(index, 'technical_capture_rate_pct', event.target.value)}\n                    disabled={busy}\n                  />\n                </label>\n                <label>\n                  <span>Acceptance %</span>\n                  <input\n                    type="number"\n                    min="0"\n                    max="100"\n                    value={item.route_acceptance_rate_pct}\n                    onChange={(event) => updateComparisonCase(index, 'route_acceptance_rate_pct', event.target.value)}\n                    disabled={busy}\n                  />\n                </label>\n              </div>\n              <label>\n                <span>Case note (optional)</span>\n                <textarea\n                  rows="2"\n                  value={item.operator_note}\n                  onChange={(event) => updateComparisonCase(index, 'operator_note', event.target.value)}\n                  placeholder="Evidence or rationale for this case"\n                  disabled={busy}\n                />\n              </label>\n            </article>\n          ))}\n        </div>\n\n        {comparisonError && <p className="error">{comparisonError}</p>}\n        <button type="button" onClick={submitComparison} disabled={busy || !selectedId}>\n          {busy ? 'Comparing cases…' : 'Compare cases'}\n        </button>\n\n        {comparisonResult && !comparisonMatchesSelection && (\n          <div className="scenario-stale-result-note">\n            Last comparison shown is for {comparisonResult.stream_id}. Compare cases for {selectedId} to replace it.\n          </div>\n        )}\n\n        {comparisonResult && (\n          <div className="scenario-comparison-result">\n            <div className="scenario-comparison-summary">\n              <ScenarioMetric\n                label="Lower screened quantity"\n                value={formatKg(comparisonResult.minimum_screened_recoverable_quantity_kg)}\n                helper="Lowest result in the submitted assumption set"\n              />\n              <ScenarioMetric\n                label="Upper screened quantity"\n                value={formatKg(comparisonResult.maximum_screened_recoverable_quantity_kg)}\n                helper="Highest result in the submitted assumption set"\n              />\n              <ScenarioMetric\n                label="Range"\n                value={formatKg(comparisonResult.screened_quantity_range_kg)}\n                helper="Sensitivity across submitted cases"\n              />\n            </div>\n\n            <div className="scenario-comparison-cards">\n              {comparisonResult.cases.map((item) => (\n                <article className="scenario-comparison-card" key={item.case_name}>\n                  <span className="record-id">{item.case_name}</span>\n                  <strong>{formatKg(item.scenario.scenario_screened_recoverable_quantity_kg)}</strong>\n                  <small>{item.scenario.scenario_screened_fraction_pct}% of baseline annual quantity</small>\n                  <dl>\n                    <div><dt>Addressable</dt><dd>{item.scenario.addressable_fraction_pct}%</dd></div>\n                    <div><dt>Capture</dt><dd>{item.scenario.technical_capture_rate_pct}%</dd></div>\n                    <div><dt>Acceptance</dt><dd>{item.scenario.route_acceptance_rate_pct}%</dd></div>\n                    <div><dt>Status</dt><dd>{humanise(item.scenario.scenario_status)}</dd></div>\n                  </dl>\n                </article>\n              ))}\n            </div>\n\n            <div className="governance-strip">\n              <strong>{humanise(comparisonResult.claim_status)}</strong>\n              <p>{comparisonResult.governance_note}</p>\n            </div>\n          </div>\n        )}\n      </section>\n    </section>\n  );\n}\n