const events = [];
const MAX = 250;
const append = (event) => {
  events.push({ time: new Date().toISOString(), ...event });
  if (events.length > MAX) events.shift();
};
export function startFrontendDiagnostics() {
  if (window.__circularFullDiagnosticsStarted) return;
  window.__circularFullDiagnosticsStarted = true;
  window.addEventListener('error', (event) => append({ type: 'browser_error', error_type: event.error?.name || 'Error' }));
  window.addEventListener('unhandledrejection', (event) => append({ type: 'promise_rejection', error_type: event.reason?.name || 'Rejection' }));
}
export function recordFrontendRequest(path, method, status, milliseconds, errorType = null) {
  const group = '/' + String(path).split('?')[0].split('/').filter(Boolean).slice(0, 2).join('/');
  append({ type: 'api_request', endpoint_group: group, method, status, duration_ms: Math.round(milliseconds), error_type: errorType });
}
async function probe(path, name) {
  const started = performance.now();
  try {
    const response = await fetch(path, { method: 'GET', cache: 'no-store' });
    return { name, status: response.ok ? 'PASS' : 'FAIL', http_status: response.status, duration_ms: Math.round(performance.now() - started) };
  } catch (error) {
    return { name, status: 'FAIL', error_type: error?.name || 'NetworkError' };
  }
}
export async function downloadFullDiagnostics() {
  const checks = await Promise.all([probe('/health', 'frontend_to_backend_proxy'), probe('/api/diagnostics/system-report', 'backend_diagnostics_endpoint')]);
  let backend = { status: 'unavailable' };
  try {
    const response = await fetch('/api/diagnostics/system-report', { cache: 'no-store' });
    if (response.ok) backend = await response.json();
    else backend = { status: 'http_error', status_code: response.status };
  } catch (error) { backend = { status: 'failed', error_type: error?.name || 'NetworkError' }; }
  const report = {
    schema_version: 1, exported_at: new Date().toISOString(),
    application: 'Circular Industry AI',
    environment: { frontend_origin: location.origin, user_agent: navigator.userAgent },
    frontend: { checks, events: [...events] },
    backend,
    limitations: ['Does not include source code, terminal output or full stack traces.', 'Functional correctness and classification accuracy require separate fixture-based tests.', 'Does not perform database mutations or automatically run the rules engine.'],
    privacy: 'Endpoint groups, response timings and error type names only. Review before sharing.',
  };
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'circular-industry-fullstack-diagnostics.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
