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
        <small>Review detected roles below, then confirm mappings in the checkpoint panel before future import.</small>
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
  { role: 'stream_id', label: 'Stream ID' },
  { role: 'stream_name', label: 'Stream name' },
  { role: 'material', label: 'Material' },
  { role: 'waste_stream_type', label: 'Waste / stream type' },
  { role: 'source_process', label: 'Source process' },
  { role: 'quantity', label: 'Quantity' },
  { role: 'quantity_unit', label: 'Quantity unit' },
  { role: 'current_route', label: 'Current route' },
  { role: 'disposal_cost_per_month', label: 'Disposal cost per month' },
  { role: 'contamination_risk', label: 'Contamination risk' },
  { role: 'hazardous_flag', label: 'Hazardous status' },
  { role: 'department', label: 'Department' },
  { role: 'supplier', label: 'Supplier' },
  { role: 'supplier_takeback_available', label: 'Supplier takeback available' },
  { role: 'recycled_content_available', label: 'Recycled content available' },
  { role: 'notes', label: 'Notes' },
  { role: 'reporting_year', label: 'Reporting year' },
  { role: 'esg_score', label: 'ESG score' },
  { role: 'esg_rating', label: 'ESG rating' },
  { role: 'esg_theme', label: 'ESG theme' },
  { role: 'evidence', label: 'Evidence' },
  { role: 'emission_scope', label: 'GHG scope' },
  { role: 'emissions_quantity', label: 'Emissions quantity' },
  { role: 'emission_source', label: 'Emission source' },
  { role: 'emission_factor', label: 'Emission factor' },
  { role: 'baseline_year', label: 'Baseline year' },
  { role: 'target_year', label: 'Target year' },
  { role: 'eia_topic', label: 'EIA topic' },
  { role: 'receptor', label: 'Receptor' },
  { role: 'impact', label: 'Impact' },
  { role: 'magnitude', label: 'Magnitude' },
  { role: 'sensitivity', label: 'Sensitivity' },
  { role: 'significance', label: 'Significance' },
  { role: 'mitigation', label: 'Mitigation' },
  { role: 'residual_effect', label: 'Residual effect' },
  { role: 'monitoring', label: 'Monitoring' },
  { role: 'stakeholder', label: 'Stakeholder' },
  { role: 'claim_text', label: 'Claim text' },
  { role: 'claim_type', label: 'Claim type' },
  { role: 'product', label: 'Product' },
  { role: 'certificate', label: 'Certificate' },
  { role: 'standard', label: 'Standard' },
  { role: 'verification_status', label: 'Verification status' },
  { role: 'geography', label: 'Geography' },
  { role: 'spend', label: 'Spend' },
  { role: 'procurement_category', label: 'Procurement category' },
  { role: 'supplier_country', label: 'Supplier country' },
  { role: 'contract_status', label: 'Contract status' },
];

const CIRCULAR_CORE_REQUIRED_ROLES = [
  { role: 'material', label: 'Material' },
  { role: 'quantity', label: 'Quantity' },
  { role: 'current_route', label: 'Current route' },
];

function getConfirmedRoles(mappingDraft) {
  return new Set(
    mappingDraft
      .filter((item) => item.user_confirmed && item.target_role)
      .map((item) => item.target_role),
  );
}

function getDuplicateConfirmedRoles(mappingDraft) {
  const counts = mappingDraft.reduce((accumulator, item) => {
    if (!item.user_confirmed || !item.target_role) return accumulator;
    accumulator[item.target_role] = (accumulator[item.target_role] || 0) + 1;
    return accumulator;
  }, {});

  return Object.entries(counts)
    .filter(([, count]) => count > 1)
    .map(([role]) => role);
}

function buildMappingValidationPayload(report, mappingDraft) {
  return {
    target_workspace: report.detected_workspace === 'circular-core' ? 'circular-core' : report.detected_workspace,
    mappings: mappingDraft.map((item) => ({
      source_column: item.source_column,
      target_role: item.target_role || null,
      mapping_state: item.mapping_state,
      confidence: item.confidence,
      user_confirmed: item.user_confirmed,
    })),
  };
}

function parseCsvRecords(text) {
  const records = [];
  let row = [];
  let cell = '';
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        cell += '"';
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === ',' && !inQuotes) {
      row.push(cell);
      cell = '';
      continue;
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') index += 1;
      row.push(cell);
      if (row.some((value) => String(value).trim() !== '')) {
        records.push(row);
      }
      row = [];
      cell = '';
      continue;
    }

    cell += char;
  }

  row.push(cell);
  if (row.some((value) => String(value).trim() !== '')) {
    records.push(row);
  }

  return records;
}

function parseCsvTextToRows(text) {
  const records = parseCsvRecords(text);
  if (records.length < 2) return [];

  const headers = records[0].map((header) => String(header || '').trim());

  return records.slice(1)
    .filter((record) => record.some((value) => String(value).trim() !== ''))
    .map((record) => headers.reduce((row, header, index) => {
      if (header) row[header] = record[index] ?? '';
      return row;
    }, {}));
}

function RequiredRoleChecklist({ mappingDraft }) {
  const confirmedRoles = getConfirmedRoles(mappingDraft);

  return (
    <div className="mapping-readiness-checklist">
      <div>
        <strong>Circular Core required roles</strong>
        <small>These must be explicitly accepted before a mapped import can be considered later.</small>
      </div>
      <div className="mapping-required-role-grid">
        {CIRCULAR_CORE_REQUIRED_ROLES.map((role) => {
          const confirmed = confirmedRoles.has(role.role);
          return (
            <span className={`mapping-required-role ${confirmed ? 'ready' : 'missing'}`} key={role.role}>
              {confirmed ? 'Confirmed' : 'Missing'}: {role.label}
            </span>
          );
        })}
      </div>
    </div>
  );
}

function LocalMappingWarnings({ mappingDraft }) {
  const confirmedRoles = getConfirmedRoles(mappingDraft);
  const missingRequiredRoles = CIRCULAR_CORE_REQUIRED_ROLES.filter((role) => !confirmedRoles.has(role.role));
  const duplicateRoles = getDuplicateConfirmedRoles(mappingDraft);
  const hasWarnings = missingRequiredRoles.length > 0 || duplicateRoles.length > 0;

  if (!hasWarnings) {
    return (
      <div className="mapping-local-warning success">
        <strong>Local readiness check</strong>
        <span>Required Circular Core roles are confirmed and no duplicate confirmed target roles are visible locally.</span>
      </div>
    );
  }

  return (
    <div className="mapping-local-warning">
      <strong>Review before validation</strong>
      {!!missingRequiredRoles.length && (
        <span>Missing required roles: {missingRequiredRoles.map((role) => role.label).join(', ')}.</span>
      )}
      {!!duplicateRoles.length && (
        <span>Duplicate confirmed target roles: {duplicateRoles.join(', ')}. Backend validation will block duplicates.</span>
      )}
    </div>
  );
}

function MappingBoundaryNotice() {
  return (
    <div className="mapping-boundary-notice">
      <strong>Boundary:</strong>
      <span>
        Validating a mapping only confirms that selected source columns can be used for a future controlled import. It does
        not verify the uploaded data, supplier compliance, diversion, savings, carbon reduction or environmental benefit.
      </span>
    </div>
  );
}

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

function DraftImportStatusPill({ status }) {
  const tone = status === 'ready' ? 'strong' : status === 'ready_with_warnings' ? 'medium' : 'weak';
  return <span className={`draft-import-status-pill ${tone}`}>{status?.replaceAll('_', ' ') || 'not built'}</span>;
}

function getDraftImportStage(report) {
  if (!report) {
    return {
      tone: 'weak',
      title: 'No draft preview built yet',
      detail: 'Validate the mapping, then build a draft preview to review generated rows and warnings.',
      action: 'No data has been saved or analysed.',
    };
  }

  if (report.import_status === 'ready') {
    return {
      tone: 'strong',
      title: 'Preview ready for operator review',
      detail: 'Draft rows were generated without blocking errors. Review the row details before designing any future import step.',
      action: 'Next safe action: review rows, then continue to a controlled import-design milestone.',
    };
  }

  if (report.import_status === 'ready_with_warnings') {
    return {
      tone: 'medium',
      title: 'Preview generated with warnings',
      detail: 'Draft rows were generated, but one or more rows need operator attention before any future import.',
      action: 'Next safe action: inspect warnings and correct source data or mappings where needed.',
    };
  }

  return {
    tone: 'weak',
    title: 'Draft import blocked by validation controls',
    detail: 'The backend returned a controlled blocked report. This is not a frontend failure.',
    action: 'Next safe action: resolve blocking errors, then rebuild the draft preview.',
  };
}

function groupImportIssues(issues = []) {
  const groups = issues.reduce((accumulator, issue) => {
    const code = issue.code || 'uncategorised_issue';

    if (!accumulator[code]) {
      accumulator[code] = {
        code,
        count: 0,
        items: [],
      };
    }

    accumulator[code].count += 1;
    accumulator[code].items.push(issue);
    return accumulator;
  }, {});

  return Object.values(groups).sort((left, right) => right.count - left.count);
}

function DraftImportStageGuidance({ report }) {
  const stage = getDraftImportStage(report);

  return (
    <section className={`draft-import-guidance-card ${stage.tone}`}>
      <div>
        <span className="eyebrow">Operator review state</span>
        <h4>{stage.title}</h4>
        <p>{stage.detail}</p>
      </div>
      <strong>{stage.action}</strong>
    </section>
  );
}

function ControlledDraftImportAction({
  report,
  operatorApproval,
  setOperatorApproval,
  approvalNote,
  setApprovalNote,
  importBusy,
  importError,
  importResult,
  onImportDraft,
}) {
  if (!report) return null;

  const blockingErrors = report.blocking_errors || [];
  const readyForImport = (
    ['ready', 'ready_with_warnings'].includes(report.import_status)
    && !!report.draft_rows?.length
    && blockingErrors.length === 0
  );

  return (
    <section className={`controlled-import-action ${readyForImport ? 'ready' : 'locked'}`}>
      <div className="controlled-import-heading">
        <div>
          <span className="eyebrow">Controlled import action</span>
          <h4>{readyForImport ? 'Save approved draft rows to SQLite' : 'Import action locked'}</h4>
          <p>
            This action saves the reviewed draft rows as Circular Core stream records and creates an audit event. It does
            not run recommendations or verify any savings, diversion, supplier compliance or environmental benefit.
          </p>
        </div>
        <DraftImportStatusPill status={report.import_status} />
      </div>

      {!readyForImport && (
        <div className="controlled-import-lock">
          <strong>Import unavailable</strong>
          <span>
            Resolve blocking errors or rebuild a ready draft preview before saving rows. Blocked previews are controlled
            validation outcomes, not frontend failures.
          </span>
        </div>
      )}

      {readyForImport && (
        <>
          <label className="controlled-import-approval">
            <input
              type="checkbox"
              checked={operatorApproval}
              onChange={(event) => setOperatorApproval(event.target.checked)}
            />
            <span>
              I have reviewed the draft rows, warnings and claim boundary. I understand this saves rows to SQLite only
              and does not run recommendations or verify impact claims.
            </span>
          </label>

          <label className="controlled-import-note">
            Approval note
            <textarea
              value={approvalNote}
              onChange={(event) => setApprovalNote(event.target.value)}
              placeholder="Optional: record what was reviewed before import."
              rows={3}
            />
          </label>

          <div className="controlled-import-actions">
            <button
              type="button"
              className="primary-button"
              onClick={onImportDraft}
              disabled={!operatorApproval || importBusy}
            >
              {importBusy ? 'Saving approved draft rows...' : 'Save approved draft rows'}
            </button>
            <small>
              Existing stream rows will be replaced and stale recommendations cleared. New recommendations will not be
              created in this step.
            </small>
          </div>
        </>
      )}

      {importError && <p className="status-error">{importError}</p>}

      {importResult && (
        <div className="controlled-import-result">
          <div>
            <span>Rows imported</span>
            <strong>{importResult.rows_imported}</strong>
          </div>
          <div>
            <span>Audit event</span>
            <strong>{importResult.audit_event_created ? `#${importResult.audit_event_id}` : 'Not recorded'}</strong>
          </div>
          <div>
            <span>Recommendations</span>
            <strong>{importResult.recommendations_cleared ? 'Cleared, not run' : 'Not run'}</strong>
          </div>
          <p>{importResult.message}</p>
          {importResult.traceability_note && <small>{importResult.traceability_note}</small>}
          {!!importResult.imported_stream_ids?.length && (
            <p className="controlled-import-streams">
              Imported stream IDs: {importResult.imported_stream_ids.slice(0, 10).join(', ')}
            </p>
          )}
        </div>
      )}
    </section>
  );
}

function ImportIssueGroupList({ title, issues, emptyText }) {
  const groupedIssues = groupImportIssues(issues);

  return (
    <article>
      <h4>{title}</h4>
      {!groupedIssues.length && <small>{emptyText}</small>}
      {groupedIssues.map((group) => {
        const affectedRows = [...new Set(group.items.map((issue) => issue.source_row_number).filter(Boolean))];

        return (
          <div className="draft-import-issue-group" key={group.code}>
            <strong>{group.code.replaceAll('_', ' ')}</strong>
            <span>
              {group.count} issue{group.count === 1 ? '' : 's'}
              {!!affectedRows.length && ` across row${affectedRows.length === 1 ? '' : 's'} ${affectedRows.slice(0, 6).join(', ')}`}
            </span>
            {group.items.slice(0, 3).map((issue, index) => (
              <small key={`${group.code}-${issue.source_row_number || 'mapping'}-${issue.source_column || issue.target_role || index}`}>
                {issue.source_row_number ? `Row ${issue.source_row_number}: ` : ''}
                {issue.message}
              </small>
            ))}
          </div>
        );
      })}
    </article>
  );
}

function DraftRowInspector({ row, rowWarnings }) {
  if (!row) {
    return (
      <section className="draft-row-inspector empty">
        <h4>No draft row selected</h4>
        <p>Build a ready or warning preview to inspect individual draft rows.</p>
      </section>
    );
  }

  return (
    <section className="draft-row-inspector">
      <div className="draft-row-inspector-heading">
        <div>
          <span className="eyebrow">Selected draft row</span>
          <h4>{row.stream_name}</h4>
          <p>Source row {row.source_row_number} Â· {row.stream_id}</p>
        </div>
        <strong>{row.draft_status?.replaceAll('_', ' ')}</strong>
      </div>

      <div className="draft-row-detail-grid">
        <article>
          <span>Material</span>
          <strong>{row.material}</strong>
        </article>
        <article>
          <span>Current route</span>
          <strong>{row.current_route}</strong>
        </article>
        <article>
          <span>Quantity</span>
          <strong>{row.monthly_quantity_kg} kg/month</strong>
        </article>
        <article>
          <span>Cost exposure</span>
          <strong>{row.disposal_cost_per_month}</strong>
        </article>
        <article>
          <span>Department</span>
          <strong>{row.department}</strong>
        </article>
        <article>
          <span>Supplier</span>
          <strong>{row.supplier}</strong>
        </article>
      </div>

      <div className="draft-row-review-box">
        <strong>Claim boundary</strong>
        <p>{row.claim_boundary}</p>
      </div>

      <div className="draft-row-review-box">
        <strong>Row warnings</strong>
        {!rowWarnings.length && <p>No row-specific warnings for this selected draft row.</p>}
        {rowWarnings.map((warning) => (
          <p key={`${warning.code}-${warning.source_column || warning.target_role || warning.message}`}>
            {warning.message}
          </p>
        ))}
      </div>
    </section>
  );
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
    </article>
  );
}

function DraftImportPreviewReport({
  report,
  operatorApproval,
  setOperatorApproval,
  approvalNote,
  setApprovalNote,
  importBusy,
  importError,
  importResult,
  onImportDraft,
}) {
  const [selectedSourceRowNumber, setSelectedSourceRowNumber] = useState(null);

  if (!report) return null;

  const previewRows = report.draft_rows?.slice(0, 8) || [];
  const rowWarnings = report.row_warnings || [];
  const blockingErrors = report.blocking_errors || [];
  const selectedRow = previewRows.find((row) => row.source_row_number === selectedSourceRowNumber) || previewRows[0];
  const selectedRowWarnings = rowWarnings.filter((warning) => warning.source_row_number === selectedRow?.source_row_number);

  return (
    <article className="draft-import-preview-result">
      <div className="draft-import-result-heading">
        <div>
          <span className="eyebrow">Draft import preview</span>
          <h3>Circular Core draft rows</h3>
          <p>
            These rows are preview-only until the operator explicitly approves the controlled import action.
            Importing saves rows to SQLite but does not run recommendations or verify claims.
          </p>
        </div>
        <DraftImportStatusPill status={report.import_status} />
      </div>

      <DraftImportStageGuidance report={report} />

      <div className="draft-import-summary-grid">
        <article>
          <span>Source rows</span>
          <strong>{report.source_row_count}</strong>
          <small>read from selected CSV in browser</small>
        </article>
        <article>
          <span>Draft rows</span>
          <strong>{report.draft_row_count}</strong>
          <small>ready for controlled approval only</small>
        </article>
        <article>
          <span>Row warnings</span>
          <strong>{rowWarnings.length}</strong>
          <small>grouped for operator review</small>
        </article>
        <article>
          <span>Blocking errors</span>
          <strong>{blockingErrors.length}</strong>
          <small>controlled validation outcome</small>
        </article>
      </div>

      {!!previewRows.length && (
        <div className="draft-import-detail-layout">
          <div className="draft-import-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Review</th>
                  <th>Row</th>
                  <th>Stream</th>
                  <th>Material</th>
                  <th>Quantity kg/month</th>
                  <th>Current route</th>
                  <th>Cost/month</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row) => (
                  <tr
                    className={selectedRow?.source_row_number === row.source_row_number ? 'selected-draft-row' : ''}
                    key={`${row.source_row_number}-${row.stream_id}`}
                  >
                    <td>
                      <button
                        type="button"
                        className="link-button compact draft-row-select-button"
                        onClick={() => setSelectedSourceRowNumber(row.source_row_number)}
                      >
                        Inspect
                      </button>
                    </td>
                    <td>{row.source_row_number}</td>
                    <td>
                      <strong>{row.stream_name}</strong>
                      <small>{row.stream_id}</small>
                    </td>
                    <td>{row.material}</td>
                    <td>{row.monthly_quantity_kg}</td>
                    <td>{row.current_route}</td>
                    <td>{row.disposal_cost_per_month}</td>
                    <td>{row.draft_status?.replaceAll('_', ' ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <DraftRowInspector row={selectedRow} rowWarnings={selectedRowWarnings} />
        </div>
      )}

      {!previewRows.length && (
        <p className="draft-import-empty">
          No draft rows returned. If the report is blocked, review the blocking errors before attempting a future import.
        </p>
      )}

      <div className="draft-import-warning-grid">
        <ImportIssueGroupList
          title="Grouped row warnings"
          issues={rowWarnings}
          emptyText="No row warnings returned."
        />
        <ImportIssueGroupList
          title="Grouped blocking errors"
          issues={blockingErrors}
          emptyText="No blocking errors returned."
        />
      </div>

      <ControlledDraftImportAction
        report={report}
        operatorApproval={operatorApproval}
        setOperatorApproval={setOperatorApproval}
        approvalNote={approvalNote}
        setApprovalNote={setApprovalNote}
        importBusy={importBusy}
        importError={importError}
        importResult={importResult}
        onImportDraft={onImportDraft}
      />

      <p className="draft-import-governance">{report.governance_note}</p>
    </article>
  );
}

function UserConfirmedMappingPanel({ report, mappingDraft, setMappingDraft, sourceFile }) {
  const [validationReport, setValidationReport] = useState(null);
  const [mappingError, setMappingError] = useState('');
  const [mappingBusy, setMappingBusy] = useState(false);
  const [draftImportReport, setDraftImportReport] = useState(null);
  const [draftImportError, setDraftImportError] = useState('');
  const [draftImportBusy, setDraftImportBusy] = useState(false);
  const [commitImportResult, setCommitImportResult] = useState(null);
  const [commitImportError, setCommitImportError] = useState('');
  const [commitImportBusy, setCommitImportBusy] = useState(false);
  const [operatorApproval, setOperatorApproval] = useState(false);
  const [approvalNote, setApprovalNote] = useState('');

  if (!report) return null;

  const highConfidenceSuggestions = mappingDraft.filter(
    (item) => item.target_role && item.mapping_state === 'suggested_by_system' && item.confidence >= 85,
  );
  const duplicateConfirmedRoles = getDuplicateConfirmedRoles(mappingDraft);

  function clearValidationState() {
    setValidationReport(null);
    setMappingError('');
    setDraftImportReport(null);
    setCommitImportResult(null);
    setCommitImportError('');
    setCommitImportBusy(false);
    setOperatorApproval(false);
    setApprovalNote('');
    setDraftImportError('');
    setCommitImportResult(null);
    setCommitImportError('');
    setOperatorApproval(false);
    setApprovalNote('');
  }

  function updateMapping(index, updates) {
    setMappingDraft((current) => current.map((item, itemIndex) => (itemIndex === index ? { ...item, ...updates } : item)));
    clearValidationState();
  }

  function acceptMapping(index) {
    const item = mappingDraft[index];
    if (!item?.target_role) {
      updateMapping(index, { mapping_state: 'unresolved', user_confirmed: false });
      return;
    }
    updateMapping(index, { mapping_state: 'accepted_by_user', user_confirmed: true });
  }

  function resetMappingToSuggestion(index) {
    const item = mappingDraft[index];
    updateMapping(index, {
      target_role: item.suggested_role || '',
      mapping_state: item.suggested_role ? 'suggested_by_system' : 'unresolved',
      user_confirmed: false,
    });
  }

  function restoreAllSuggestions() {
    setMappingDraft(buildInitialMappingDraft(report));
    clearValidationState();
  }

  function acceptHighConfidenceSuggestions() {
    setMappingDraft((current) => current.map((item) => {
      if (item.target_role && item.mapping_state === 'suggested_by_system' && item.confidence >= 85) {
        return { ...item, mapping_state: 'accepted_by_user', user_confirmed: true };
      }
      return item;
    }));
    clearValidationState();
  }

  function ignoreMapping(index) {
    updateMapping(index, { target_role: '', mapping_state: 'ignored_by_user', user_confirmed: false });
  }

  async function validateMapping() {
    setMappingBusy(true);
    setMappingError('');
    setValidationReport(null);
    setDraftImportReport(null);
    setCommitImportResult(null);
    setCommitImportError('');
    setCommitImportBusy(false);
    setOperatorApproval(false);
    setApprovalNote('');
    setDraftImportError('');
    setCommitImportResult(null);
    setCommitImportError('');
    setOperatorApproval(false);
    setApprovalNote('');

    try {
      setValidationReport(await api.validateMapping(buildMappingValidationPayload(report, mappingDraft)));
    } catch (err) {
      setMappingError(err.message || 'Could not validate mapping.');
    } finally {
      setMappingBusy(false);
    }
  }

  async function buildDraftImportPreview() {
    setDraftImportBusy(true);
    setDraftImportError('');
    setCommitImportResult(null);
    setCommitImportError('');
    setOperatorApproval(false);
    setApprovalNote('');
    setDraftImportReport(null);
    setCommitImportResult(null);
    setCommitImportError('');
    setCommitImportBusy(false);
    setOperatorApproval(false);
    setApprovalNote('');

    try {
      if (!sourceFile) {
        throw new Error('Select and profile a CSV before building a draft import preview.');
      }

      const sourceRows = parseCsvTextToRows(await sourceFile.text());

      if (!sourceRows.length) {
        throw new Error('The selected CSV did not contain any source rows to preview.');
      }

      const payload = {
        mapping_validation: buildMappingValidationPayload(report, mappingDraft),
        source_rows: sourceRows,
      };

      setDraftImportReport(await api.buildCircularCoreDraftImport(payload));
    } catch (err) {
      setDraftImportError(err.message || 'Could not build Circular Core draft import preview.');
    } finally {
      setDraftImportBusy(false);
    }
  }

  async function commitDraftImport() {
    setCommitImportBusy(true);
    setCommitImportError('');
    setCommitImportResult(null);

    try {
      if (!draftImportReport) {
        throw new Error('Build a draft import preview before saving approved rows.');
      }

      const payload = {
        draft_import_report: draftImportReport,
        operator_approval: operatorApproval,
        approval_note: approvalNote || null,
        replace_existing_streams: true,
      };

      setCommitImportResult(await api.importCircularCoreDraft(payload));
    } catch (err) {
      setCommitImportError(err.message || 'Could not save approved draft rows.');
    } finally {
      setCommitImportBusy(false);
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
        <div className="mapping-heading-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={acceptHighConfidenceSuggestions}
            disabled={!highConfidenceSuggestions.length}
          >
            Accept high-confidence suggestions
          </button>
          <button type="button" className="secondary-button" onClick={restoreAllSuggestions}>
            Restore suggestions
          </button>
          <button type="button" className="primary-button" onClick={validateMapping} disabled={mappingBusy || !mappingDraft.length}>
            {mappingBusy ? 'Validatingâ€¦' : 'Validate mapping'}
          </button>
        </div>
      </div>

      <MappingBoundaryNotice />
      <RequiredRoleChecklist mappingDraft={mappingDraft} />
      <LocalMappingWarnings mappingDraft={mappingDraft} />

      {!!duplicateConfirmedRoles.length && (
        <p className="mapping-inline-warning">
          Duplicate confirmed roles are visible locally. Resolve them before relying on the validation result.
        </p>
      )}

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
                <button type="button" className="link-button" onClick={() => resetMappingToSuggestion(index)}>
                  Reset to suggestion
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

      {validationReport && (
        <section className="draft-import-preview-panel">
          <div className="draft-import-preview-heading">
            <div>
              <span className="eyebrow">Circular Core draft import</span>
              <h3>Build preview from confirmed mapping</h3>
              <p>
                This uses the selected CSV and the current confirmed mapping to build draft rows only. It does not save,
                overwrite, analyse or verify anything.
              </p>
            </div>
            <button type="button" className="primary-button" onClick={buildDraftImportPreview} disabled={draftImportBusy || !sourceFile}>
              {draftImportBusy ? 'Building previewâ€¦' : 'Build draft preview'}
            </button>
          </div>

          <div className="draft-import-boundary">
            <strong>Preview boundary:</strong>
            <span>
              Draft rows are generated for operator review only. They are not imported into SQLite and do not create Circular
              Core recommendations, verified savings, verified diversion or supplier-compliance claims.
            </span>
          </div>

          {draftImportError && <p className="status-error">{draftImportError}</p>}
          <DraftImportPreviewReport
            report={draftImportReport}
            operatorApproval={operatorApproval}
            setOperatorApproval={setOperatorApproval}
            approvalNote={approvalNote}
            setApprovalNote={setApprovalNote}
            importBusy={commitImportBusy}
            importError={commitImportError}
            importResult={commitImportResult}
            onImportDraft={commitDraftImport}
          />
        </section>
      )}
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
            The profiler routes data and the checkpoint validates mappings only. It does not yet import rows into Circular Core.
          </p>
        </div>
        <div className="profiler-upload-actions">
          <label className="file-button domain-file-button">
            Select CSV
            <input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          </label>
          <button type="button" className="primary-button" onClick={profileFile} disabled={!file || busy}>
            {busy ? 'Profilingâ€¦' : 'Profile CSV'}
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
          <UserConfirmedMappingPanel
            report={report}
            mappingDraft={mappingDraft}
            setMappingDraft={setMappingDraft}
            sourceFile={file}
          />

          <p className="governance-strip">{report.governance_note}</p>
        </div>
      )}
    </section>
  );
}


