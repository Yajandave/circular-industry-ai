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
  scenarioHistory,
  onRunScenario,
  onCompareScenarios,
  onSaveScenario,
  onLoadScenarioHistory,
  busy,
}) {
  const [selectedId, setSelectedId] = useState('');
  const [assumptions, setAssumptions] = useState(DEFAULT_ASSUMPTIONS);
  const [comparisonCases, setComparisonCases] = useState(DEFAULT_COMPARISON_CASES);
  const [scenarioName, setScenarioName] = useState('');
  const [lifecycleStage, setLifecycleStage] = useState('screening');
  const [saveError, setSaveError] = useState('');
  const [localError, setLocalError] = useState('');
  const [comparisonError, setComparisonError] = useState('');

  useEffect(() => {
    if (!selectedId && recommendations.length) {
      setSelectedId(recommendations[0].stream_id);
    }
  }, [recommendations, selectedId]);

  useEffect(() => {
    if (selectedId) {
      onLoadScenarioHistory(selectedId);
      setScenarioName('');
      setLifecycleStage('screening');
      setSaveError('');
    }
    // The App callback is intentionally omitted because it is recreated on render.
  }, [selectedId]);

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
  const historyMatchesSelection = scenarioHistory?.stream_id === selectedId;

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

  function loadSavedRevision(record) {
    setAssumptions({
      addressable_fraction_pct: String(record.addressable_fraction_pct),
      technical_capture_rate_pct: String(record.technical_capture_rate_pct),
      route_acceptance_rate_pct: String(record.route_acceptance_rate_pct),
      operator_note: record.operator_note || '',
    });
    setScenarioName(record.scenario_name);
    setLifecycleStage(record.lifecycle_stage);
    setSaveError('');
    setLocalError('');
  }

  async function saveCurrentScenario() {
    setSaveError('');

    const name = scenarioName.trim();
    if (!name) {
      setSaveError('Give the scenario a name before saving it.');
      return;
    }

    const numericFields = [
      'addressable_fraction_pct',
      'technical_capture_rate_pct',
      'route_acceptance_rate_pct',
    ];
    const payload = {
      scenario_name: name,
      lifecycle_stage: lifecycleStage,
      operator_note: assumptions.operator_note.trim() || null,
    };

    for (const field of numericFields) {
      const value = Number(assumptions[field]);
      if (!Number.isFinite(value) || value < 0 || value > 100) {
        setSaveError('Each saved scenario percentage must be a number between 0 and 100.');
        return;
      }
      payload[field] = value;
    }

    try {
      await onSaveScenario(selectedId, payload);
    } catch {
      // App-level status reporting already surfaces the API error.
    }
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
      </div>

      <section className="scenario-history-section">
        <div className="section-heading compact-heading">
          <div>
            <h3>Save and revisit scenario revisions</h3>
            <p>
              Saved revisions are immutable snapshots. Saving the same named scenario again creates a new revision
              instead of overwriting the previous one.
            </p>
          </div>
          <span>{historyMatchesSelection ? scenarioHistory.total_saved_revisions : 0} saved revisions</span>
        </div>

        <div className="scenario-save-controls">
          <label>
            <span>Scenario name</span>
            <input
              type="text"
              value={scenarioName}
              onChange={(event) => {
                setScenarioName(event.target.value);
                setSaveError('');
              }}
              placeholder="e.g. Supplier take-back pilot"
              disabled={busy}
            />
          </label>

          <label>
            <span>Lifecycle stage</span>
            <select
              value={lifecycleStage}
              onChange={(event) => {
                setLifecycleStage(event.target.value);
                setSaveError('');
              }}
              disabled={busy}
            >
              <option value="screening">Screening</option>
              <option value="pilot_planned">Pilot planned</option>
              <option value="pilot_observed">Pilot observed</option>
              <option value="measured_unverified">Measured, unverified</option>
            </select>
          </label>

          <button type="button" onClick={saveCurrentScenario} disabled={busy || !selectedId}>
            {busy ? 'Saving revision…' : 'Save current scenario'}
          </button>
        </div>

        {saveError && <p className="error">{saveError}</p>}

        <div className="scenario-history-governance">
          Lifecycle stage records workflow progress only. Even “measured, unverified” remains non-claim-ready until a later evidence-verification step.
        </div>

        {!historyMatchesSelection || !scenarioHistory?.records?.length ? (
          <div className="scenario-history-empty">
            No saved scenario revisions for this stream yet.
          </div>
        ) : (
          <div className="scenario-history-list">
            {scenarioHistory.records.map((record) => (
              <article className="scenario-history-card" key={record.id}>
                <div className="scenario-history-card-header">
                  <div>
                    <span className="record-id">{record.scenario_name}</span>
                    <strong>Revision {record.revision_number}</strong>
                    <small>{new Date(record.created_at).toLocaleString('en-GB')}</small>
                  </div>
                  <span className="scenario-history-stage">{humanise(record.lifecycle_stage)}</span>
                </div>

                <div className="scenario-history-metrics">
                  <div>
                    <span>Screened quantity</span>
                    <strong>{formatKg(record.scenario_screened_recoverable_quantity_kg)}</strong>
                  </div>
                  <div>
                    <span>Addressable / capture / acceptance</span>
                    <strong>
                      {record.addressable_fraction_pct}% / {record.technical_capture_rate_pct}% / {record.route_acceptance_rate_pct}%
                    </strong>
                  </div>
                  <div>
                    <span>Status</span>
                    <strong>{humanise(record.scenario_status)}</strong>
                  </div>
                </div>

                {record.operator_note && <p>{record.operator_note}</p>}

                <button
                  type="button"
                  className="secondary"
                  onClick={() => loadSavedRevision(record)}
                  disabled={busy}
                >
                  Load assumptions into builder
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="scenario-comparison-section">
        <div className="section-heading compact-heading">
          <div>
            <h3>Compare assumption cases</h3>
            <p>
              Compare three editable screening cases for the same stream and locked route. The starting values are illustrative only;
              replace them with evidence-backed assumptions before relying on the comparison.
            </p>
          </div>
          <span>3 explicit cases</span>
        </div>

        <div className="scenario-comparison-inputs">
          {comparisonCases.map((item, index) => (
            <article className="scenario-case-builder" key={item.case_name || index}>
              <label>
                <span>Case name</span>
                <input
                  type="text"
                  value={item.case_name}
                  onChange={(event) => updateComparisonCase(index, 'case_name', event.target.value)}
                  disabled={busy}
                />
              </label>
              <div className="scenario-case-number-grid">
                <label>
                  <span>Addressable %</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={item.addressable_fraction_pct}
                    onChange={(event) => updateComparisonCase(index, 'addressable_fraction_pct', event.target.value)}
                    disabled={busy}
                  />
                </label>
                <label>
                  <span>Capture %</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={item.technical_capture_rate_pct}
                    onChange={(event) => updateComparisonCase(index, 'technical_capture_rate_pct', event.target.value)}
                    disabled={busy}
                  />
                </label>
                <label>
                  <span>Acceptance %</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={item.route_acceptance_rate_pct}
                    onChange={(event) => updateComparisonCase(index, 'route_acceptance_rate_pct', event.target.value)}
                    disabled={busy}
                  />
                </label>
              </div>
              <label>
                <span>Case note (optional)</span>
                <textarea
                  rows="2"
                  value={item.operator_note}
                  onChange={(event) => updateComparisonCase(index, 'operator_note', event.target.value)}
                  placeholder="Evidence or rationale for this case"
                  disabled={busy}
                />
              </label>
            </article>
          ))}
        </div>

        {comparisonError && <p className="error">{comparisonError}</p>}
        <button type="button" onClick={submitComparison} disabled={busy || !selectedId}>
          {busy ? 'Comparing cases…' : 'Compare cases'}
        </button>

        {comparisonResult && !comparisonMatchesSelection && (
          <div className="scenario-stale-result-note">
            Last comparison shown is for {comparisonResult.stream_id}. Compare cases for {selectedId} to replace it.
          </div>
        )}

        {comparisonResult && (
          <div className="scenario-comparison-result">
            <div className="scenario-comparison-summary">
              <ScenarioMetric
                label="Lower screened quantity"
                value={formatKg(comparisonResult.minimum_screened_recoverable_quantity_kg)}
                helper="Lowest result in the submitted assumption set"
              />
              <ScenarioMetric
                label="Upper screened quantity"
                value={formatKg(comparisonResult.maximum_screened_recoverable_quantity_kg)}
                helper="Highest result in the submitted assumption set"
              />
              <ScenarioMetric
                label="Range"
                value={formatKg(comparisonResult.screened_quantity_range_kg)}
                helper="Sensitivity across submitted cases"
              />
            </div>

            <div className="scenario-comparison-cards">
              {comparisonResult.cases.map((item) => (
                <article className="scenario-comparison-card" key={item.case_name}>
                  <span className="record-id">{item.case_name}</span>
                  <strong>{formatKg(item.scenario.scenario_screened_recoverable_quantity_kg)}</strong>
                  <small>{item.scenario.scenario_screened_fraction_pct}% of baseline annual quantity</small>
                  <dl>
                    <div><dt>Addressable</dt><dd>{item.scenario.addressable_fraction_pct}%</dd></div>
                    <div><dt>Capture</dt><dd>{item.scenario.technical_capture_rate_pct}%</dd></div>
                    <div><dt>Acceptance</dt><dd>{item.scenario.route_acceptance_rate_pct}%</dd></div>
                    <div><dt>Status</dt><dd>{humanise(item.scenario.scenario_status)}</dd></div>
                  </dl>
                </article>
              ))}
            </div>

            <div className="governance-strip">
              <strong>{humanise(comparisonResult.claim_status)}</strong>
              <p>{comparisonResult.governance_note}</p>
            </div>
          </div>
        )}
      </section>
    </section>
  );
}
