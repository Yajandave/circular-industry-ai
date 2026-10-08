import { useState } from 'react';

import { api } from '../api/client.js';
import { RiskBadge, ReviewBadge } from './Badges.jsx';
import { humanise } from '../utils/formatters.js';

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

function reviewMaturity(base) {
  if (base.evidence_maturity) return base.evidence_maturity;
  if (base.human_review_required || ['high', 'blocked'].includes(base.risk_level)) return 'controlled_review_required';
  if (String(base.rule_applied || '').toLowerCase() === 'r999_default_evidence_improvement') return 'insufficient_for_route_change';
  const missing = String(base.missing_data || '').trim().toLowerCase();
  if (base.risk_level === 'medium' || !['', 'none', 'none recorded', 'none identified', 'none identified for mvp fields'].includes(missing)) {
    return 'screening_ready_with_checks';
  }
  return 'screening_ready';
}

function reviewDecisionBasis(base) {
  if (base.decision_support_band) return base.decision_support_band;
  return {
    controlled_review_required: 'human_review_gate',
    insufficient_for_route_change: 'limited_screening_basis',
    screening_ready_with_checks: 'screening_basis_with_checks',
    screening_ready: 'strong_screening_basis',
  }[reviewMaturity(base)] || 'limited_screening_basis';
}


const EMPTY_CHALLENGE = {
  challenger_name: '',
  challenger_role: '',
  challenger_organisation: '',
  challenge_type: 'route',
  proposed_change: '',
  rationale: '',
  supporting_evidence_reference: '',
};


export default function ReviewPackPanel({ reviewPack }) {
  const [challengeForm, setChallengeForm] = useState(EMPTY_CHALLENGE);
  const [challengeResult, setChallengeResult] = useState(null);
  const [challengeError, setChallengeError] = useState('');
  const [challengeBusy, setChallengeBusy] = useState(false);

  function updateChallenge(key, value) {
    setChallengeForm((current) => ({ ...current, [key]: value }));
    setChallengeError('');
  }

  async function submitChallenge(event) {
    event.preventDefault();
    if (!reviewPack?.stream_id) return;

    setChallengeBusy(true);
    setChallengeError('');
    setChallengeResult(null);
    try {
      const payload = {
        ...challengeForm,
        challenger_organisation: challengeForm.challenger_organisation || null,
        supporting_evidence_reference: challengeForm.supporting_evidence_reference || null,
      };
      const result = await api.recordDecisionChallenge(reviewPack.stream_id, payload);
      setChallengeResult(result);
      setChallengeForm(EMPTY_CHALLENGE);
    } catch (error) {
      setChallengeError(error.message || 'Could not record the decision challenge.');
    } finally {
      setChallengeBusy(false);
    }
  }

  if (!reviewPack) {
    return (
      <section id="review-pack-panel" className="review-panel empty focused-review-panel">
        <h2>Controlled review pack</h2>
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
  const provenance = reviewPack.rule_provenance || {};
  const reviewGovernance = reviewPack.review_governance || {};

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
        <ReviewSummaryCard title="Decision basis" value={humanise(reviewDecisionBasis(base))} detail="Qualitative screening basis, not probability" />
        <ReviewSummaryCard title="Evidence maturity" value={humanise(reviewMaturity(base))} detail="Governance state from explicit risk and evidence conditions" />
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

      <div className="review-grid focused-grid governance-review-grid">
        <article>
          <h3>Rule provenance</h3>
          <p><strong>{provenance.rule_family || reviewPack.rule_applied}</strong></p>
          <p>{humanise(provenance.provenance_status)}</p>
          <p>{provenance.internal_interpretation}</p>
          {!!provenance.sources?.length && (
            <div className="list-block">
              <h4>Public guidance informing this boundary</h4>
              <ul>
                {provenance.sources.map((source) => (
                  <li key={source.source_id}>
                    <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
                    {' '}· {source.publisher}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <small>Governance version: {provenance.governance_version} · reviewed {provenance.last_reviewed_date}</small>
          <p className="boundary-note">{provenance.claim_boundary}</p>
        </article>

        <article>
          <h3>Human review governance</h3>
          <p><strong>{humanise(reviewGovernance.gate_status)}</strong></p>
          <ListBlock title="Primary reviewer competence" items={reviewGovernance.primary_reviewer_competence} />
          <ListBlock title="Supporting competence" items={reviewGovernance.supporting_reviewer_competence} />
          <p><strong>Second review recommended:</strong> {reviewGovernance.second_review_recommended ? 'Yes' : 'No'}</p>
          <p>{reviewGovernance.minimum_review_expectation}</p>
          <ListBlock title="Why this reviewer profile" items={reviewGovernance.rationale} />
          <p className="boundary-note">{reviewGovernance.override_policy}</p>
          <small>{reviewGovernance.governance_note}</small>
        </article>
      </div>

      <details className="section-card governance-challenge-panel">
        <summary><strong>Record professional disagreement</strong></summary>
        <p>
          Use this only when a reviewer disagrees with the locked screening decision, risk, evidence position or claim boundary.
          Recording a challenge does not change the recommendation.
        </p>
        <form className="scenario-verification-form" onSubmit={submitChallenge}>
          <div className="scenario-verification-grid">
            <label>
              <span>Reviewer name</span>
              <input
                value={challengeForm.challenger_name}
                onChange={(event) => updateChallenge('challenger_name', event.target.value)}
                required
                disabled={challengeBusy}
              />
            </label>
            <label>
              <span>Reviewer role</span>
              <input
                value={challengeForm.challenger_role}
                onChange={(event) => updateChallenge('challenger_role', event.target.value)}
                required
                disabled={challengeBusy}
              />
            </label>
            <label>
              <span>Organisation (optional)</span>
              <input
                value={challengeForm.challenger_organisation}
                onChange={(event) => updateChallenge('challenger_organisation', event.target.value)}
                disabled={challengeBusy}
              />
            </label>
            <label>
              <span>Challenge type</span>
              <select
                value={challengeForm.challenge_type}
                onChange={(event) => updateChallenge('challenge_type', event.target.value)}
                disabled={challengeBusy}
              >
                <option value="route">Route / strategy</option>
                <option value="risk">Risk level</option>
                <option value="review_gate">Review gate</option>
                <option value="evidence">Evidence position</option>
                <option value="claim_boundary">Claim boundary</option>
                <option value="other">Other</option>
              </select>
            </label>
          </div>
          <label className="scenario-verification-note">
            <span>Proposed change</span>
            <textarea
              rows="2"
              value={challengeForm.proposed_change}
              onChange={(event) => updateChallenge('proposed_change', event.target.value)}
              required
              disabled={challengeBusy}
            />
          </label>
          <label className="scenario-verification-note">
            <span>Reasoning</span>
            <textarea
              rows="3"
              value={challengeForm.rationale}
              onChange={(event) => updateChallenge('rationale', event.target.value)}
              required
              disabled={challengeBusy}
            />
          </label>
          <label className="scenario-verification-note">
            <span>Supporting evidence reference (optional)</span>
            <input
              value={challengeForm.supporting_evidence_reference}
              onChange={(event) => updateChallenge('supporting_evidence_reference', event.target.value)}
              disabled={challengeBusy}
            />
          </label>
          {challengeError && <p className="error">{challengeError}</p>}
          <button type="submit" disabled={challengeBusy}>
            {challengeBusy ? 'Recording challenge…' : 'Record challenge without overriding decision'}
          </button>
        </form>
        {challengeResult && (
          <div className="governance-strip">
            <strong>{humanise(challengeResult.status)}</strong>
            <p>{challengeResult.governance_note}</p>
            <small>Decision effect: {humanise(challengeResult.decision_effect)}</small>
          </div>
        )}
      </details>

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
