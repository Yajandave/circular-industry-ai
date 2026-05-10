function runtimeLabel(mode) {
  if (mode === 'ai_on') return 'Optional AI drafting active';
  if (mode === 'fallback_key_missing') return 'Optional AI drafting unavailable';
  if (mode === 'fallback_ai_disabled') return 'Optional AI drafting disabled';
  return 'System intelligence status';
}

function statusText(status) {
  if (status.runtime_mode === 'ai_on') {
    return 'AI drafting is available for explanations, supplier emails and reports. Locked rules, review gates and claim boundaries still own the decision record.';
  }

  return 'Deterministic rules, retrieval, graph, insight and evaluation workflows remain active. Optional LLM drafting is not being used.';
}

export default function AIRuntimeStatus({ status }) {
  if (!status) return null;

  const aiOn = status.runtime_mode === 'ai_on';

  return (
    <section className={`ai-runtime-status operator-runtime ${aiOn ? 'ai-on' : ''}`}>
      <div className="operator-runtime-main">
        <div>
          <span className="eyebrow">System intelligence</span>
          <h3>{runtimeLabel(status.runtime_mode)}</h3>
          <p>{statusText(status)}</p>
        </div>
        <span className={`runtime-mode-pill ${aiOn ? 'on' : 'deterministic'}`}>
          {aiOn ? 'AI drafting on' : 'Deterministic mode'}
        </span>
      </div>

      <div className="ai-runtime-note">
        <strong>Decision guardrail:</strong> {status.guardrail_summary}
      </div>

      <details className="runtime-diagnostics">
        <summary>Diagnostics</summary>
        <div className="ai-runtime-grid">
          <article><span>Provider</span><strong>{status.llm_provider}</strong></article>
          <article><span>Model</span><strong>{status.configured_model}</strong></article>
          <article><span>Timeout</span><strong>{status.timeout_seconds}s</strong></article>
          <article><span>Fallback</span><strong>{status.fallback_available ? 'Available' : 'Unavailable'}</strong></article>
        </div>
        <p className="muted-note">{status.recommended_operator_action}</p>
      </details>
    </section>
  );
}
