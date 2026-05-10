import { API_BASE_URL } from '../api/client.js';
import { formatCurrency, formatNumber } from '../utils/formatters.js';

function ExportButton({ href, children }) {
  return (
    <a className="secondary-button" href={href} target="_blank" rel="noreferrer">
      {children}
    </a>
  );
}

function ListBlock({ title, items }) {
  const safeItems = Array.isArray(items) ? items : [];
  return (
    <div className="supplier-list-block">
      <h4>{title}</h4>
      {safeItems.length ? (
        <ul>
          {safeItems.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}
        </ul>
      ) : (
        <p>None recorded.</p>
      )}
    </div>
  );
}

function BreakdownCard({ title, data }) {
  const entries = Object.entries(data || {});
  return (
    <div className="evidence-breakdown-card">
      <h4>{title}</h4>
      <div className="breakdown-list">
        {entries.length ? entries.map(([key, value]) => (
          <div className="breakdown-row" key={key}>
            <span>{key}</span>
            <strong>{value}</strong>
          </div>
        )) : <p>No records yet.</p>}
      </div>
    </div>
  );
}

function SupplierEmailDraftPanel({ draft }) {
  if (!draft) return null;

  return (
    <section className="supplier-email-draft-panel" id="supplier-email-draft-panel">
      <div className="section-heading compact-heading">
        <div>
          
          <h3>Supplier evidence request draft: {draft.stream_id}</h3>
          <p>
            AI-assisted supplier communication generated from locked procurement, recommendation and evidence-register data.
          </p>
        </div>
        <span>{draft.generation_mode?.replaceAll('_', ' ')}</span>
      </div>

      <div className="supplier-email-lock-grid">
        <article>
          <span>Supplier</span>
          <strong>{draft.supplier}</strong>
        </article>
        <article>
          <span>Risk / review</span>
          <strong>{draft.locked_risk_level} · review {String(draft.locked_human_review_required)}</strong>
        </article>
        <article>
          <span>Procurement route</span>
          <strong>{draft.locked_procurement_route}</strong>
        </article>
      </div>

      <article className="supplier-email-body-card">
        <h4>Subject</h4>
        <p className="supplier-email-subject">{draft.subject}</p>
        <h4>Email body</h4>
        <pre>{draft.email_body}</pre>
      </article>

      <div className="supplier-email-grid">
        <ListBlock title="Evidence request summary" items={draft.evidence_request_summary} />
        <ListBlock title="Documents to request" items={draft.attachments_or_documents_to_request} />
        <ListBlock title="Internal follow-up actions" items={draft.internal_follow_up_actions} />
      </div>

      <div className="supplier-email-claim-card">
        <h4>Claim safety note</h4>
        <p>{draft.claim_safety_note}</p>
      </div>

      <div className="governance-strip">
        {draft.governance_note}
      </div>

      {!!draft.validation_warnings?.length && (
        <div className="supplier-email-warning">
          <h4>Validation warnings</h4>
          <ul>
            {draft.validation_warnings.map((warning, index) => (
              <li key={`supplier-email-warning-${index}`}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function SupplierPlanCard({ plan, onDraftEmail, busy }) {
  return (
    <article className={`supplier-loop-card ${plan.human_review_required ? 'controlled' : 'candidate'}`}>
      <div className="supplier-loop-header">
        <div>
          <span>{plan.stream_id} · {plan.material}</span>
          <h3>{plan.stream_name}</h3>
          <p>{plan.department} · Supplier: {plan.supplier || 'not recorded'}</p>
        </div>
        <div className="supplier-loop-priority">
          <strong>{plan.procurement_priority}</strong>
          <small>{plan.human_review_required ? 'Controlled review' : 'Supplier action candidate'}</small>
          {onDraftEmail && (
            <button
              type="button"
              className="secondary-button supplier-email-button"
              onClick={() => onDraftEmail(plan.stream_id)}
              disabled={busy}
            >
              Draft supplier email
            </button>
          )}
        </div>
      </div>

      <div className="supplier-loop-summary-grid">
        <div>
          <span>Procurement route</span>
          <p>{plan.procurement_route}</p>
        </div>
        <div>
          <span>Relationship type</span>
          <p>{plan.supplier_relationship_type}</p>
        </div>
        <div>
          <span>Value at stake</span>
          <p>{formatCurrency(plan.estimated_annual_value_at_stake)}</p>
        </div>
      </div>

      <div className="supplier-loop-section">
        <h4>Reverse logistics model</h4>
        <p>{plan.reverse_logistics_model}</p>
      </div>

      <div className="supplier-loop-section">
        <h4>Negotiation position</h4>
        <p>{plan.negotiation_position}</p>
      </div>

      <div className="supplier-loop-grid">
        <ListBlock title="Supplier questions" items={plan.supplier_questions} />
        <ListBlock title="Contract levers" items={plan.contract_levers} />
        <ListBlock title="Evidence required" items={plan.supplier_evidence_required} />
        <ListBlock title="Acceptance criteria" items={plan.acceptance_criteria} />
        <ListBlock title="Commercial checks" items={plan.commercial_checks} />
        <ListBlock title="Operational checks" items={plan.operational_checks} />
      </div>

      <div className="supplier-loop-clause">
        <h4>Circular procurement clause starter</h4>
        <p>{plan.circular_procurement_clause}</p>
      </div>

      <div className="supplier-loop-footer-grid">
        <div>
          <span>Pilot scope</span>
          <p>{plan.pilot_scope}</p>
        </div>
        <div>
          <span>Review gate</span>
          <p>{plan.review_gate}</p>
        </div>
        <div>
          <span>Fallback position</span>
          <p>{plan.fallback_position}</p>
        </div>
      </div>
    </article>
  );
}

export default function SupplierLoopIntelligence({
  plans = [],
  summary = null,
  emailDraft = null,
  onDraftEmail = null,
  busy = false,
}) {
  const supplierCandidates = plans
    .filter((plan) => !plan.human_review_required)
    .slice(0, 8);
  const controlled = plans
    .filter((plan) => plan.human_review_required)
    .slice(0, 4);

  return (
    <section className="supplier-loop-section-page">
      <div className="section-heading">
        <div>
          <h2>Circular procurement and supplier-loop intelligence</h2>
          <p>
            Supplier-facing actions that translate circular resolution plans into take-back terms, reverse logistics,
            contract evidence, supplier questions, acceptance criteria and procurement pilot controls.
          </p>
        </div>
        <div className="export-actions">
          <ExportButton href={`${API_BASE_URL}/api/export/supplier-loop-plans.csv`}>Export CSV</ExportButton>
        </div>
      </div>

      <div className="operator-summary-grid">
        <div className="operator-summary-card">
          <span>Supplier action register</span>
          <strong>{formatNumber(summary?.total_plans || plans.length)}</strong>
          <small>evidence-controlled procurement records</small>
        </div>
        <div className="operator-summary-card">
          <span>Supplier-loop candidates</span>
          <strong>{formatNumber(summary?.supplier_loop_candidates || 0)}</strong>
          <small>good candidates for supplier pilot scoping</small>
        </div>
        <div className="operator-summary-card">
          <span>Reverse logistics candidates</span>
          <strong>{formatNumber(summary?.reverse_logistics_candidates || 0)}</strong>
          <small>return, take-back or packaging-loop opportunities</small>
        </div>
        <div className="operator-summary-card">
          <span>Controlled supplier reviews</span>
          <strong>{formatNumber(summary?.controlled_supplier_reviews || 0)}</strong>
          <small>contractor/compliance evidence gates</small>
        </div>
      </div>

      {summary?.method_note && (
        <div className="evidence-governance-note resolution-note">
          <h4>Method note</h4>
          <p>{summary.method_note}</p>
        </div>
      )}

      <SupplierEmailDraftPanel draft={emailDraft} />

      <div className="resolution-overview-grid">
        <BreakdownCard title="Procurement priority breakdown" data={summary?.procurement_priority_breakdown} />
        <BreakdownCard title="Procurement route breakdown" data={summary?.procurement_route_breakdown} />
      </div>

      <div className="section-heading compact-heading">
        <div>
          <h3>Top supplier actions</h3>
          <p>Supplier-facing opportunities ranked by screened value exposure. These are evidence requests, not final contract instructions.</p>
        </div>
      </div>
      <div className="supplier-action-list">
        {(summary?.top_supplier_actions || []).map((action) => (
          <div className="supplier-action-card" key={action.stream_id}>
            <strong>{action.stream_id} · {action.stream_name}</strong>
            <span>{action.supplier} · {action.procurement_route}</span>
            <p>{action.supplier_question}</p>
            <small>{formatCurrency(action.estimated_annual_value_at_stake)} screened value at stake</small>
            {onDraftEmail && (
              <button
                type="button"
                className="link-button compact"
                onClick={() => onDraftEmail(action.stream_id)}
                disabled={busy}
              >
                Draft supplier email
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="section-heading compact-heading">
        <div>
          <h3>Supplier-loop candidates</h3>
          <p>Showing the first eight non-controlled supplier-loop plans. Use export for the full register.</p>
        </div>
      </div>
      <div className="supplier-loop-card-stack">
        {supplierCandidates.map((plan) => (
          <SupplierPlanCard
            key={plan.stream_id}
            plan={plan}
            onDraftEmail={onDraftEmail}
            busy={busy}
          />
        ))}
      </div>

      {controlled.length > 0 && (
        <div className="controlled-resolution-box">
          <h3>Controlled supplier / contractor reviews</h3>
          <p>These records must stay in evidence and compliance review before any supplier-loop or recovery claim is made.</p>
          <div className="supplier-loop-card-stack compact">
            {controlled.map((plan) => (
              <SupplierPlanCard
                key={`controlled-${plan.stream_id}`}
                plan={plan}
                onDraftEmail={onDraftEmail}
                busy={busy}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}


