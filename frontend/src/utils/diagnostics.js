// Privacy-first, session-only diagnostics. No request bodies, URLs, headers or business data.
const events = [];
const MAX_EVENTS = 200;
function add(event) {
  events.push({ time: new Date().toISOString(), ...event });
  if (events.length > MAX_EVENTS) events.shift();
}
function category(path) {
  const segments = String(path).split('?')[0].split('/').filter(Boolean);
  return '/' + segments.slice(0, 2).join('/');
}
export function recordApiResult(path, method, status, durationMs, failed = false) {
  add({
    type: 'api_request',
    endpoint_group: category(path),
    method: String(method || 'GET').toUpperCase(),
    status: Number.isInteger(status) ? status : null,
    duration_ms: Math.round(durationMs),
    outcome: failed ? 'failed' : 'ok',
  });
}
export function startDiagnostics() {
  if (typeof window === 'undefined' || window.__circularDiagnosticsStarted) return;
  window.__circularDiagnosticsStarted = true;
  window.addEventListener('error', (event) => {
    add({ type: 'browser_error', error_kind: event.error?.name || 'Error' });
  });
  window.addEventListener('unhandledrejection', (event) => {
    add({ type: 'unhandled_rejection', error_kind: event.reason?.name || 'PromiseRejection' });
  });
}
export async function downloadDiagnostics() {
  let readiness = { status: 'unavailable' };
  try {
    // Same-origin Vite proxy in Codespaces; never include URL/query headers in export.
    const response = await fetch('/api/diagnostics/workflow-readiness');
    if (response.ok) {
      const result = await response.json();
      readiness = {
        status: 'available',
        product_stage: result.product_stage,
        backend_status: result.backend_status,
        alpha_exit_status: result.alpha_exit_status,
        total_streams: result.total_streams,
        total_recommendations: result.total_recommendations,
        steps: (result.steps || []).map(({ name, status }) => ({ name, status })),
      };
    } else readiness = { status: 'http_error', http_status: response.status };
  } catch {
    readiness = { status: 'connection_failed' };
  }
  const report = {
    schema_version: 1,
    exported_at: new Date().toISOString(),
    application: 'Circular Industry AI',
    environment: { user_agent: navigator.userAgent, frontend_origin: location.origin },
    privacy: 'Includes only endpoint groups, response codes, timings, error types and summary counts. Does not include request bodies, tokens, raw datasets or backend terminal logs. Review before sharing.',
    readiness,
    events: [...events],
  };
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'circular-industry-ai-diagnostics.json';
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
