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

export default function ReviewPackPanel({ reviewPack }) {
  if (!reviewPack) {
    return (
      <section id="review-pack-panel" className="review-panel empty">
        <h2>Agentic review pack</h2>
        <p>Select a recommendation to inspect the evidence, risk, procurement and symbiosis review.</p>
      </section>
    );
  }

  const base = reviewPack.base_recommendation || {};
  const evidence = reviewPack.evidence_audit || {};
  const procurement = reviewPack.procurement_review || {};
  const symbiosis = reviewPack.industrial_symbiosis_review || {};
  const resource = reviewPack.resource_efficiency_review || {};
  const executive = reviewPack.executive_synthesis || {};

  return (
    <section id="review-pack-panel" className="review-panel">
      <div className="section-heading">
        <div>
          <h2>{reviewPack.stream_id}: {reviewPack.stream_name}</h2>
          <p>{reviewPack.material} · rule locked by {reviewPack.rule_applied}</p>
        </div>
        <ReviewBadge required={base.human_review_required} />
      </div>

      <div className="review-grid">
        <article>
          <h3>Locked recommendation</h3>
          <p><strong>{base.recommended_circular_action}</strong></p>
          <RiskBadge value={base.risk_level} />
          <div className="score-stack inline">
            <ScoreBadge label="Confidence" value={base.confidence_score} />
            <ScoreBadge label="Evidence" value={base.evidence_quality_score} />
          </div>
        </article>

        <article>
          <h3>Executive synthesis</h3>
          <p>{executive.decision_position}</p>
          <p>{executive.evidence_position}</p>
          <p><strong>Management action:</strong> {executive.recommended_management_action}</p>
        </article>

        <article>
          <h3>Evidence audit</h3>
          <ListBlock title="Measured data" items={evidence.measured_data} />
          <ListBlock title="Estimated data" items={evidence.estimated_data} />
          <ListBlock title="Missing data" items={evidence.missing_data} />
          <p className="boundary-note">{evidence.claim_boundary}</p>
        </article>

        <article>
          <h3>Procurement review</h3>
          <p><strong>Supplier:</strong> {procurement.supplier}</p>
          <ListBlock title="Procurement levers" items={procurement.procurement_levers} />
          <ListBlock title="Supplier questions" items={procurement.supplier_questions} />
        </article>

        <article>
          <h3>Industrial symbiosis screen</h3>
          <p><strong>Status:</strong> {symbiosis.symbiosis_screening_status}</p>
          <ListBlock title="Screening questions" items={symbiosis.screening_questions} />
          <ListBlock title="Barriers to resolve" items={symbiosis.barriers_to_resolve} />
        </article>

        <article>
          <h3>Resource efficiency</h3>
          <p><strong>Reduce-before-recycle check:</strong> {String(resource.reduce_before_recycle_check)}</p>
          <ListBlock title="Process improvement levers" items={resource.process_improvement_levers} />
        </article>
      </div>
    </section>
  );
}
