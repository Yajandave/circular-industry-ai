import { useState } from 'react';

import { api } from '../api/client.js';

function ConfidencePill({ value }) {
  const numeric = Number(value) || 0;
  const tone = numeric >= 80 ? 'strong' : numeric >= 55 ? 'medium' : 'weak';
  return <span className={`profiler-confidence ${tone}`}>{numeric}%</span>;
}

function ListBlock({ title, items }) {
  return (
    <article className="profiler-list-card">
      <h3>{title}</h3>
      {!items?.length && <p className="muted">None identified.</p>}
      {!!items?.length && <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>}
    </article>
  );
}

function OverviewCard({ label, value, note }) {
  return (
    <article className="profiler-overview-card">
      <span>{label}</span>
      <strong>{value}</strong>
      {note && <small>{note}</small>}
    </article>
  );
}

function WorkspaceRoutes({ routes }) {
  return (
    <div className="profiler-routes-grid">
      {routes.map((route) => (
        <article className="profiler-route-card" key={route.workspace_id}>
          <div className="profiler-route-topline">
            <div>
              <h3>{route.label}</h3>
              <span>{route.status}</span>
            </div>
            <ConfidencePill value={route.score} />
          </div>
          <div className="profiler-mini-columns">
            <div>
              <strong>Matched</strong>
              {!route.matched_roles.length && <small>None yet</small>}
              {route.matched_roles.slice(0, 6).map((role) => <small key={role.role}>{role.label}</small>)}
            </div>
            <div>
              <strong>Missing</strong>
              {!route.missing_roles.length && <small>No major gaps</small>}
              {route.missing_roles.slice(0, 6).map((role) => <small key={role.role}>{role.label}</small>)}
            </div>
          </div>
          <p>{route.governance_boundary}</p>
        </article>
      ))}
    </div>
  );
}

function ColumnMappingTable({ columns }) {
  return (
    <div className="profiler-column-panel">
      <div className="profiler-column-header">
        <strong>Detected column roles</strong>
        <small>Uncertain mappings can be confirmed in the next milestone.</small>
      </div>
      <div className="profiler-column-list">
        {columns.map((column) => (
          <article className="profiler-column-row" key={column.original_name}>
            <div>
              <span className="record-id">{column.original_name}</span>
              <strong>{column.mapped_role_label || 'Unmapped'}</strong>
              <small>{column.role_reason}</small>
              {!!column.sample_values?.length && <p>Samples: {column.sample_values.join(', ')}</p>}
            </div>
            <div className="profiler-column-meta">
              <ConfidencePill value={column.role_confidence} />
              <small>{column.inferred_data_type}</small>
              {column.confirmation_required && <em>Confirm later</em>}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

export default function DataProfilerPanel() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function profileFile() {
    if (!file) return;
    setBusy(true);
    setError('');
    setReport(null);
    try {
      setReport(await api.profileCsv(file));
    } catch (err) {
      setError(err.message || 'Could not profile CSV.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="data-profiler-panel">
      <div className="domain-upload-zone profiler-upload-zone">
        <div>
          <h3>Profile a CSV before choosing an analysis route</h3>
          <p>
            Upload a clean CSV even if its column names do not match the Circular Core template. The backend maps likely
            column roles, shows missing fields and recommends a valid workspace route without inventing data.
          </p>
          <p className="domain-parser-status">
            14A profiles and routes data. It does not yet transform the CSV into a confirmed Circular Core import.
          </p>
        </div>
        <div className="profiler-upload-actions">
          <label className="file-button domain-file-button">
            Select CSV
            <input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          </label>
          <button type="button" className="primary-button" onClick={profileFile} disabled={!file || busy}>
            {busy ? 'Profiling…' : 'Profile CSV'}
          </button>
        </div>
      </div>

      {file && (
        <div className="domain-selected-file">
          <strong>Selected file:</strong> {file.name}
          <span>Profiling checks column aliases, missing fields and workspace compatibility only.</span>
        </div>
      )}

      {error && <p className="status-error">{error}</p>}

      {report && (
        <div className="profiler-report">
          <div className="section-heading compact-heading">
            <div>
              <span className="eyebrow">Data profiler result</span>
              <h2>{report.detected_workspace_label}</h2>
              <p>{report.recommended_next_action}</p>
            </div>
            <ConfidencePill value={report.workspace_confidence} />
          </div>

          <div className="profiler-overview-grid">
            <OverviewCard label="Rows" value={report.total_rows} note="not loaded into core" />
            <OverviewCard label="Columns" value={report.total_columns} note="profiled from upload" />
            <OverviewCard label="Duplicate rows" value={report.duplicate_rows} note="exact duplicate check" />
            <OverviewCard label="Route status" value={report.workspace_status} note="workspace compatibility" />
          </div>

          <div className="profiler-analysis-grid">
            <ListBlock title="Available analysis routes" items={report.available_analysis_routes} />
            <ListBlock title="Unavailable or limited routes" items={report.unavailable_analysis_routes} />
          </div>

          <WorkspaceRoutes routes={report.workspace_compatibility} />
          <ColumnMappingTable columns={report.columns} />

          <p className="governance-strip">{report.governance_note}</p>
        </div>
      )}
    </section>
  );
}
