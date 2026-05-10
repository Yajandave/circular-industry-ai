import { formatCurrency, formatKg, formatNumber } from '../utils/formatters.js';

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
    <div className="resolution-list-block">
      <h4>{title}</h4>
      {safeItems.length ? (
        <ul>
          {safeItems.map((item, index) => (
            <li key={`${title}-${index}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>None recorded.</p>
      )}
    </div>
  );
}

function ResolutionPlanCard({ plan }) {
  return (
    <article className={`resolution-card ${plan.human_review_required ? 'controlled' : 'ready'}`}>
      <div className="resolution-card-header">
        <div>
          <span>{plan.stream_id}</span>
          <h3>{plan.stream_name}</h3>
          <p>{plan.material} · {plan.department}</p>
        </div>
        <div className="resolution-tags">
          <strong>{plan.circularity_route_strength}</strong>
          <small>{plan.human_review_required ? 'Controlled review' : 'Pilot candidate'}</small>
        </div>
      </div>

      {plan.core_circularity_question && (
        <div className="playbook-context-box">
          <span>{plan.material_cycle}</span>
          <strong>{plan.core_circularity_question}</strong>
        </div>
      )}

      <div className="resolution-body-grid">
        <section>
          <h4>Circular problem</h4>
          <p>{plan.circular_problem}</p>
        </section>
        <section>
          <h4>Specific resolution idea</h4>
          <p>{plan.specific_resolution_idea}</p>
        </section>
        <section>
          <h4>Why this is circular economy</h4>
          <p>{plan.why_this_is_circular_economy}</p>
        </section>
        <section>
          <h4>Value-retention logic</h4>
          <p>{plan.value_retention_logic}</p>
        </section>
      </div>

      <div className="resolution-detail-grid">
        <ListBlock title="Implementation steps" items={plan.implementation_steps} />
        <ListBlock title="KPIs" items={plan.kpis} />
        <ListBlock title="Evidence required" items={plan.evidence_required} />
        <ListBlock title="Decision gates" items={plan.decision_gates} />
      </div>

      <div className="resolution-detail-grid advanced-resolution-grid">
        <ListBlock title="Material-specific intervention patterns" items={plan.high_value_intervention_patterns} />
        <ListBlock title="Prevention and design levers" items={plan.prevention_and_design_levers} />
        <ListBlock title="Routes to avoid" items={plan.routes_to_avoid} />
        <ListBlock title="Material-specific evidence tests" items={plan.material_specific_evidence_tests} />
        <ListBlock title="Material red flags" items={plan.material_specific_red_flags} />
        <ListBlock title="Claim controls" items={plan.playbook_claim_controls} />
      </div>

      <div className="resolution-actions-grid">
        <div>
          <h4>Supplier / procurement action</h4>
          <p>{plan.supplier_or_procurement_action}</p>
        </div>
        <div>
          <h4>Process redesign action</h4>
          <p>{plan.process_redesign_action}</p>
        </div>
        <div>
          <h4>Industrial symbiosis action</h4>
          <p>{plan.industrial_symbiosis_action}</p>
        </div>
        <div>
          <h4>Pilot plan</h4>
          <p>{plan.pilot_plan}</p>
        </div>
      </div>

      <div className="claim-boundary-box">
        <h4>Claim boundary</h4>
        <p>{plan.claim_boundary}</p>
      </div>

      <div className="resolution-footer-grid">
        <div>
          <span>Fallback route</span>
          <p>{plan.fallback_route}</p>
        </div>
        <div>
          <span>Confidence notes</span>
          <p>{plan.confidence_notes}</p>
        </div>
        <div>
          <span>Screened exposure</span>
          <p>{formatCurrency(plan.estimated_annual_disposal_cost_avoided)} · {formatKg(plan.estimated_annual_waste_diverted_kg)}</p>
        </div>
      </div>
    </article>
  );
}

export default function CircularResolutionPlans({ plans = [], summary = null }) {
  const topPlans = plans.slice(0, 8);
  const controlled = plans.filter((plan) => plan.human_review_required).slice(0, 5);

  return (
    <section className="resolution-section">
      <div className="section-heading">
        <div>
          <h2>Circular resolution engine</h2>
          <p>Specific circular economy intervention plans generated from locked rules, playbooks, evidence gates and claim controls.</p>
        </div>
        <div className="export-actions">
          <ExportButton href="http://127.0.0.1:8000/api/export/resolution-plans.csv">Export CSV</ExportButton>
        </div>
      </div>

      <div className="operator-summary-grid">
        <div className="operator-summary-card">
          <span>Resolution register</span>
          <strong>{formatNumber(summary?.total_plans || plans.length)}</strong>
          <small>screened intervention records</small>
        </div>
        <div className="operator-summary-card">
          <span>Controlled reviews</span>
          <strong>{formatNumber(summary?.controlled_review_plans || 0)}</strong>
          <small>risk, hazard or evidence gates</small>
        </div>
        <div className="operator-summary-card">
          <span>Claim-control cases</span>
          <strong>{formatNumber(summary?.claim_blocked_or_not_ready || 0)}</strong>
          <small>not claim-ready until evidence improves</small>
        </div>
      </div>

      {summary?.method_note && (
        <div className="evidence-governance-note resolution-note">
          <h4>Method note</h4>
          <p>{summary.method_note}</p>
        </div>
      )}

      <div className="resolution-overview-grid">
        <div className="evidence-breakdown-card">
          <h4>Route strength breakdown</h4>
          <div className="breakdown-list">
            {Object.entries(summary?.route_strength_breakdown || {}).map(([key, value]) => (
              <div className="breakdown-row" key={key}><span>{key}</span><strong>{value}</strong></div>
            ))}
          </div>
        </div>
        <div className="evidence-breakdown-card">
          <h4>Top validation candidates</h4>
          <div className="resolution-candidate-list">
            {(summary?.top_validation_candidates || []).map((candidate) => (
              <div className="resolution-candidate" key={candidate.stream_id}>
                <strong>{candidate.stream_id} · {candidate.stream_name}</strong>
                <small>{formatKg(candidate.estimated_annual_waste_diverted_kg)} · {formatCurrency(candidate.estimated_annual_disposal_cost_avoided)}</small>
                <p>{candidate.specific_resolution_idea}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="section-heading compact-heading">
        <div>
          <h3>Priority resolution plans</h3>
          <p>Showing the first eight ranked plans. Use the CSV export for the full structured register.</p>
        </div>
      </div>
      <div className="resolution-card-stack">
        {topPlans.map((plan) => <ResolutionPlanCard key={plan.stream_id} plan={plan} />)}
      </div>

      {controlled.length > 0 && (
        <div className="controlled-resolution-box">
          <h3>Controlled review examples</h3>
          <p>These plans are intentionally blocked from implementation until evidence and compliance gates are resolved.</p>
          <div className="resolution-card-stack compact">
            {controlled.map((plan) => <ResolutionPlanCard key={`controlled-${plan.stream_id}`} plan={plan} />)}
          </div>
        </div>
      )}
    </section>
  );
}


