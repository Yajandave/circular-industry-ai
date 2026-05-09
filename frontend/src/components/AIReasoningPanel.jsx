import { useMemo, useState } from 'react';

function ListSection({ title, items }) {
  const safeItems = Array.isArray(items) ? items : [];
  return (
    <section className="ai-list-card">
      <h4>{title}</h4>
      {safeItems.length ? (
        <ul>
          {safeItems.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}
        </ul>
      ) : (
        <p>None generated.</p>
      )}
    </section>
  );
}

function NarrativeBlock({ title, children, emphasis = false }) {
  return (
    <section className={`ai-narrative-block ${emphasis ? 'emphasis' : ''}`}>
      <h4>{title}</h4>
      <p>{children || 'Not generated yet.'}</p>
    </section>
  );
}

export default function AIReasoningPanel({
  plans = [],
  recommendations = [],
  status = null,
  reasoning = null,
  onGenerate,
  busy = false,
}) {
  const defaultStreamId = plans[0]?.stream_id || recommendations[0]?.stream_id || '';
  const [selectedStreamId, setSelectedStreamId] = useState(defaultStreamId);

  const options = useMemo(() => {
    const planOptions = plans.map((plan) => ({
      stream_id: plan.stream_id,
      label: `${plan.stream_id} · ${plan.stream_name}`,
    }));
    if (planOptions.length) return planOptions;
    return recommendations.map((rec) => ({
      stream_id: rec.stream_id,
      label: `${rec.stream_id} · ${rec.recommended_circular_action}`,
    }));
  }, [plans, recommendations]);

  const selected = selectedStreamId || options[0]?.stream_id || '';

  return (
    <section className="ai-reasoning-section">
      <div className="section-heading ai-heading">
        <div>
          <span className="eyebrow">Milestone 7C reasoning layer</span>
          <h2>Rules-locked AI reasoning</h2>
          <p>
            Generate a consultant-style reasoning narrative from the locked rules recommendation, evidence register and
            circular resolution plan. The AI can explain and draft, but it cannot override the rule, risk level or review gate.
          </p>
        </div>
        <div className="ai-status-card">
          <span>Current mode</span>
          <strong>{status?.mode || 'checking'}</strong>
          <small>{status?.llm_provider ? `Provider: ${status.llm_provider}` : 'Provider unavailable'}</small>
          <small>{status?.configured_model ? `Model: ${status.configured_model}` : 'Model setting unavailable'}</small>
        </div>
      </div>

      <div className="ai-control-card">
        <label>
          Select stream for AI reasoning
          <select value={selected} onChange={(event) => setSelectedStreamId(event.target.value)}>
            {options.map((option) => (
              <option key={option.stream_id} value={option.stream_id}>{option.label}</option>
            ))}
          </select>
        </label>
        <button type="button" onClick={() => selected && onGenerate(selected)} disabled={!selected || busy}>
          Generate reasoning
        </button>
        <p>{status?.guardrail_summary}</p>
      </div>

      {!reasoning && (
        <div className="empty-state">
          Select a stream and generate reasoning. If no API key is configured, the app will show deterministic fallback reasoning.
        </div>
      )}

      {reasoning && (
        <article className="ai-output-card">
          <div className="ai-output-header">
            <div>
              <span>{reasoning.stream_id}</span>
              <h3>{reasoning.stream_name}</h3>
              <p>{reasoning.decision_lock_status} · {reasoning.generation_mode}</p>
            </div>
            <div className="ai-lock-box">
              <span>Locked controls</span>
              <strong>{reasoning.locked_risk_level || 'risk unchanged'}</strong>
              <small>{reasoning.locked_human_review_required ? 'Human review required' : 'Rules-cleared for validation'}</small>
            </div>
          </div>

          <div className="ai-narrative-grid">
            <NarrativeBlock title="Executive summary" emphasis>{reasoning.executive_summary}</NarrativeBlock>
            <NarrativeBlock title="Circular economy reasoning">{reasoning.circular_economy_reasoning}</NarrativeBlock>
            <NarrativeBlock title="Evidence-gap explanation">{reasoning.evidence_gap_explanation}</NarrativeBlock>
            <NarrativeBlock title="Pilot guidance">{reasoning.pilot_guidance}</NarrativeBlock>
            <NarrativeBlock title="Claim safety note" emphasis>{reasoning.claim_safety_note}</NarrativeBlock>
            <NarrativeBlock title="Human review note">{reasoning.human_review_note}</NarrativeBlock>
          </div>

          <div className="ai-list-grid">
            <ListSection title="Supplier / contractor questions" items={reasoning.supplier_questions} />
            <ListSection title="Implementation risks" items={reasoning.implementation_risks} />
            <ListSection title="Validation warnings" items={reasoning.validation_warnings} />
          </div>
        </article>
      )}
    </section>
  );
}
