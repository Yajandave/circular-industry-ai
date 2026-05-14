import { useEffect, useState } from 'react';

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

const ROLE_OPTIONS = [
  { role: '', label: 'Unmapped / unresolved' },
  { role: 'material', label: 'Material' },
  { role: 'quantity', label: 'Quantity' },
  { role: 'current_route', label: 'Current route' },
  { role: 'stream_name', label: 'Stream name' },
  { role: 'source_process', label: 'Source process' },
  { role: 'disposal_cost_per_month', label: 'Disposal cost per month' },
  { role: 'contamination_risk', label: 'Contamination risk' },
  { role: 'hazardous_flag', label: 'Hazardous status' },
  { role: 'supplier', label: 'Supplier' },
  { role: 'department', label: 'Department' },
  { role: 'quantity_unit', label: 'Quantity unit' },
  { role: 'waste_stream_type', label: 'Waste / stream type' },
  { role: 'supplier_takeback_available', label: 'Supplier takeback available' },
  { role: 'recycled_content_available', label: 'Recycled content available' },
  { role: 'notes', label: 'Notes' },
];

function buildInitialMappingDraft(report) {
  return (report?.columns || []).map((column) => ({
    source_column: column.original_name,
    target_role: column.mapped_role || '',
    suggested_role: column.mapped_role || '',
    suggested_label: column.mapped_role_label || 'Unmapped',
    mapping_state: column.mapped_role ? 'suggested_by_system' : 'unresolved',
    confidence: Number(column.role_confidence) || 0,
    user_confirmed: false,
    sample_values: column.sample_values || [],
    inferred_data_type: column.inferred_data_type,
    role_reason: column.role_reason,
  }));
}

function ValidationStatusPill({ status }) {
  const tone = status === 'ready' ? 'strong' : status === 'ready_with_warnings' ? 'medium' : 'weak';
  return <span className={`mapping-status-pill ${tone}`}>{status?.replaceAll('_', ' ') || 'not validated'}</span>;
}

function MappingValidationSummary({ report }) {
  if (!report) return null;

  return (
    <article className="mapping-validation-result">
      <div className="mapping-validation-topline">
        <div>
          <span className="eyebrow">Backend validation result</span>
          <h3>{report.target_workspace_label}</h3>
        </div>
        <ValidationStatusPill status={report.import_status} />
      </div>

      <div className="mapping-validation-grid">
        <div>
          <strong>Resolved required roles</strong>
          {!report.resolved_required_roles?.length && <small>None confirmed yet.</small>}
          {report.resolved_required_roles?.map((role) => <small key={role.role}>{role.label}</small>)}
        </div>
        <div>
          <strong>Missing required roles</strong>
          {!report.missing_required_roles?.length && <small>No required-role gaps.</small>}
          {report.missing_required_roles?.map((role) => <small key={role.role}>{role.label}</small>)}
        </div>
        <div>
          <strong>Warnings</strong>
          {!report.warnings?.length && <small>No warnings returned.</small>}
          {report.warnings?.slice(0, 4).map((warning) => (
            <small key={`${warning.code}-${warning.source_column || warning.target_role}`}>{warning.message}</small>
          ))}
        </div>
        <div>
          <strong>Blocking errors</strong>
          {!report.blocking_errors?.length && <small>No blocking errors.</small>}
          {report.blocking_errors?.slice(0, 4).map((error) => (
            <small key={`${error.code}-${error.source_column || error.target_role}`}>{error.message}</small>
          ))}
        </div>
      </div>

      <p className="mapping-governance-note">{report.governance_note}</p>
    </article>
  );
}

function UserConfirmedMappingPanel({ report, mappingDraft, setMappingDraft }) {
  const [validationReport, setValidationReport] = useState(null);
  const [mappingError, setMappingError] = useState('');
  const [mappingBusy, setMappingBusy] = useState(false);

  if (!report) return null;

  function updateMapping(index, updates) {
    setMappingDraft((current) => current.map((item, itemIndex) => (itemIndex === index ? { ...item, ...updates } : item)));
    setValidationReport(null);
    setMappingError('');
  }

  function acceptMapping(index) {
    const item = mappingDraft[index];
    if (!item?.target_role) {
      updateMapping(index, { mapping_state: 'unresolved', user_confirmed: false });
      return;
    }
    updateMapping(index, { mapping_state: 'accepted_by_user', user_confirmed: true });
  }

  function ignoreMapping(index) {
    updateMapping(index, { target_role: '', mapping_state: 'ignored_by_user', user_confirmed: false });
  }

  async function validateMapping() {
    setMappingBusy(true);
    setMappingError('');
    setValidationReport(null);

    const payload = {
      target_workspace: report.detected_workspace === 'circular-core' ? 'circular-core' : report.detected_workspace,
      mappings: mappingDraft.map((item) => ({
        source_column: item.source_column,
        target_role: item.target_role || null,
        mapping_state: item.mapping_state,
        confidence: item.confidence,
        user_confirmed: item.user_confirmed,
      })),
    };

    try {
      setValidationReport(await api.validateMapping(payload));
    } catch (err) {
      setMappingError(err.message || 'Could not validate mapping.');
    } finally {
      setMappingBusy(false);
    }
  }

  return (
    <section className="mapping-confirmation-panel">
      <div className="mapping-confirmation-heading">
        <div>
          <span className="eyebrow">User-confirmed mapping checkpoint</span>
          <h3>Review and validate mapped columns</h3>
          <p>
            System suggestions are not import-ready until accepted by the operator. This validation checks mapping
            readiness only; it does not verify source data, savings, diversion, carbon reduction or supplier compliance.
          </p>
        </div>
        <button type="button" className="primary-button" onClick={validateMapping} disabled={mappingBusy || !mappingDraft.length}>
          {mappingBusy ? 'Validating…' : 'Validate mapping'}
        </button>
      </div>

      <div className="mapping-draft-list">
        {mappingDraft.map((item, index) => (
          <article className="mapping-draft-row" key={item.source_column}>
            <div className="mapping-source-detail">
              <span className="record-id">{item.source_column}</span>
              <strong>Suggested: {item.suggested_label}</strong>
              <small>{item.role_reason}</small>
              {!!item.sample_values?.length && <p>Samples: {item.sample_values.slice(0, 4).join(', ')}</p>}
            </div>
            <div className="mapping-controls">
              <label>
                Target role
                <select
                  value={item.target_role}
                  onChange={(event) => updateMapping(index, {
                    target_role: event.target.value,
                    mapping_state: event.target.value ? 'changed_by_user' : 'unresolved',
                    user_confirmed: false,
                  })}
                >
                  {ROLE_OPTIONS.map((option) => <option key={option.role || 'unmapped'} value={option.role}>{option.label}</option>)}
                </select>
              </label>
              <div className="mapping-row-actions">
                <ConfidencePill value={item.confidence} />
                <button type="button" className="secondary-button" onClick={() => acceptMapping(index)} disabled={!item.target_role}>
                  Accept
                </button>
                <button type="button" className="link-button" onClick={() => ignoreMapping(index)}>
                  Ignore
                </button>
              </div>
              <small className={`mapping-state ${item.user_confirmed ? 'confirmed' : ''}`}>
                {item.user_confirmed ? 'User confirmed' : item.mapping_state.replaceAll('_', ' ')}
              </small>
            </div>
          </article>
        ))}
      </div>

      {mappingError && <p className="status-error">{mappingError}</p>}
      <MappingValidationSummary report={validationReport} />
    </section>
  );
}


export default function DataProfilerPanel() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [mappingDraft, setMappingDraft] = useState([]);

  useEffect(() => {
    setMappingDraft(buildInitialMappingDraft(report));
  }, [report]);

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
          <UserConfirmedMappingPanel report={report} mappingDraft={mappingDraft} setMappingDraft={setMappingDraft} />

          <p className="governance-strip">{report.governance_note}</p>
        </div>
      )}
    </section>
  );
}
