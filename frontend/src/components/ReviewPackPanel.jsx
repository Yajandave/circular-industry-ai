import { RiskBadge, ReviewBadge, ScoreBadge } from './Badges.jsx';

function ListBlock({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="list-block">
      <h4>{title}</h4>
      <ul>
        {items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}
      </ul>
    </div>
  );
}

function ReviewSummaryCard({ title, value, detail }) {
  return (
    <article className="review-summary-card">
      <span>{title}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </article>
  );
}

export default function ReviewPackPanel({ reviewPack }) {
  if (!reviewPack) {
    return (
      <section id="review-pack-panel" className="review-panel empty focused-review-panel">
        <h2>Agentic review pack</h2>
        <p>
          Select <strong>Review</strong> from a recommendation or dashboard candidate to inspect the evidence audit, risk locks,
          procurement questions, symbiosis screen and resource-efficiency levers for that stream.
        </p>
        <p className="boundary-note">
          The review pack is a drill-down view. It does not replace the locked rules-engine recommendation or approve an operational route.
        </p>
      </section>
    );
  }

  const base = reviewPack.base_recommendation || {};
  const evidence = reviewPack.evidence_audit || {};
  const procurement = reviewPack.procurement_review || {};
  const symbiosis = reviewPack.industrial_symbiosis_review || {};
  const resource = reviewPack.resource_efficiency_review || {};
  const executive = reviewPack.executive_synthesis || {};
  const risk = reviewPack.risk_review || {};

  return (
    <section id="review-pack-panel" className="review-panel focused-review-panel">
      <div className="section-heading">
        <div>
          <h2>{reviewPack.stream_id}: {reviewPack.stream_name}</h2>
          <p>{reviewPack.material} · rule locked by {reviewPack.rule_applied}</p>
        </div>
        <ReviewBadge required={base.human_review_required} />
      </div>

      <div className="review-summary-grid">
        <ReviewSummaryCard title="Locked decision" value={base.recommended_circular_action} detail={base.circular_strategy_category} />
        <ReviewSummaryCard title="Risk level" value={base.risk_level || 'unknown'} detail={base.human_review_required ? 'Human review required' : 'Rules-cleared'} />
        <ReviewSummaryCard title="Confidence" value={`${base.confidence_score ?? 0}/100`} detail="Rules-engine confidence" />
        <ReviewSummaryCard title="Evidence" value={`${base.evidence_quality_score ?? 0}/100`} detail="Evidence maturity score" />
      </div>

      <article className="executive-review-card">
        <div>
          <h3>Executive synthesis</h3>
          <p>{executive.decision_position}</p>
          <p>{executive.evidence_position}</p>
        </div>
        <div className="management-action-box">
          <span>Recommended management action</span>
          <strong>{executive.recommended_management_action}</strong>
        </div>
      </article>

      <div className="review-grid focused-grid">
        <article>
          <h3>Risk locks and review gates</h3>
          <RiskBadge value={base.risk_level} />
          <ListBlock title="Risk triggers" items={risk.risk_triggers} />
          <ListBlock title="Review gates" items={risk.review_gates} />
          <ListBlock title="Locked controls" items={risk.locked_controls} />
        </article>

        <article>
          <h3>Evidence audit</h3>
          <ListBlock title="Measured data" items={evidence.measured_data} />
          <ListBlock title="Estimated data" items={evidence.estimated_data} />
          <ListBlock title="Missing data" items={evidence.missing_data} />
          <ListBlock title="Assumptions" items={evidence.assumptions} />
          <p className="boundary-note">{evidence.claim_boundary}</p>
        </article>

        <article>
          <h3>Procurement review</h3>
          <p><strong>Supplier or contractor:</strong> {procurement.supplier}</p>
          <ListBlock title="Procurement levers" items={procurement.procurement_levers} />
          <ListBlock title="Supplier / contractor questions" items={procurement.supplier_questions} />
          <ListBlock title="Contract evidence needed" items={procurement.contract_evidence_needed} />
        </article>

        <article>
          <h3>Industrial symbiosis screen</h3>
          <p><strong>Status:</strong> {symbiosis.symbiosis_screening_status}</p>
          <ListBlock title="Likely partner types" items={symbiosis.likely_partner_types} />
          <ListBlock title="Screening questions" items={symbiosis.screening_questions} />
          <ListBlock title="Barriers to resolve" items={symbiosis.barriers_to_resolve} />
        </article>

        <article className="wide-review-card">
          <h3>Resource efficiency review</h3>
          <p><strong>Reduce-before-recycle check:</strong> {String(resource.reduce_before_recycle_check)}</p>
          <ListBlock title="Process-specific improvement levers" items={resource.process_improvement_levers} />
        </article>
      </div>
    </section>
  );
}
