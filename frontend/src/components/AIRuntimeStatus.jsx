function runtimeLabel(mode) {
  if (mode === 'ai_on') return 'AI-on mode';
  if (mode === 'fallback_key_missing') return 'Fallback: key missing';
  if (mode === 'fallback_ai_disabled') return 'Fallback: AI disabled';
  return mode || 'Unknown AI mode';
}

export default function AIRuntimeStatus({ status }) {
  if (!status) return null;

  const isAiOn = status.runtime_mode === 'ai_on';
  const isWarning = status.runtime_mode === 'fallback_key_missing';

  return (
    <section className={`ai-runtime-status ${isAiOn ? 'ai-on' : ''} ${isWarning ? 'warning' : ''}`}>
      <div>
        <span className="eyebrow">AI runtime</span>
        <h3>{runtimeLabel(status.runtime_mode)}</h3>
        <p>{status.agentic_role}</p>
      </div>
      <div className="ai-runtime-grid">
        <article>
          <span>Provider</span>
          <strong>{status.llm_provider}</strong>
        </article>
        <article>
          <span>Model</span>
          <strong>{status.configured_model}</strong>
        </article>
        <article>
          <span>Timeout</span>
          <strong>{status.timeout_seconds}s</strong>
        </article>
        <article>
          <span>Fallback</span>
          <strong>{status.fallback_available ? 'Available' : 'Unavailable'}</strong>
        </article>
      </div>
      <div className="ai-runtime-note">
        <strong>Guardrail:</strong> {status.guardrail_summary}
      </div>
      <div className="ai-runtime-note muted-note">
        {status.recommended_operator_action}
      </div>
    </section>
  );
}
