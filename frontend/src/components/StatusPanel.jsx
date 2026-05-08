import { API_BASE_URL } from '../api/client.js';

export default function StatusPanel({ status, message, error }) {
  return (
    <section className="status-panel">
      <div>
        <span className={`status-dot ${status === 'ok' ? 'ok' : 'warn'}`} />
        <strong>Backend:</strong> {status === 'ok' ? 'connected' : 'not confirmed'}
      </div>
      <div className="muted">API: {API_BASE_URL}</div>
      {message && <div className="notice">{message}</div>}
      {error && <div className="error">{error}</div>}
    </section>
  );
}
