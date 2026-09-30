import { useEffect, useMemo, useState } from 'react';

import { RiskBadge, ReviewBadge, ScoreBadge } from './Badges.jsx';
import { formatCurrency, formatKg, humanise } from '../utils/formatters.js';

const DEFAULT_ASSUMPTIONS = {
  addressable_fraction_pct: '80',
  technical_capture_rate_pct: '85',
  route_acceptance_rate_pct: '90',
  operator_note: '',
};

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
  onRunScenario,
  busy,
}) {
  const [selectedId, setSelectedId] = useState('');
  const [assumptions, setAssumptions] = useState(DEFAULT_ASSUMPTIONS);
  const [localError, setLocalError] = useState('');

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

  function updateAssumption(key, value) {
    setAssumptions((current) => ({ ...current, [key]: value }));
    setLocalError('');
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

    await onRunScenario(selectedId, payload);
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
    </section>
  );
}
