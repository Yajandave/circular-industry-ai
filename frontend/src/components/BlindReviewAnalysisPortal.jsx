import { useEffect, useState } from 'react';
import { api } from '../api/client.js';

function pct(value) {
  return value === null || value === undefined ? '—' : `${value}%`;
}

function humanise(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function yesNo(value) {
  if (value === null || value === undefined) return '—';
  return value ? 'Yes' : 'No';
}

function matchLabel(value) {
  if (value === null || value === undefined) return 'No stable consensus';
  return value ? 'Matches consensus' : 'Differs from consensus';
}

export default function BlindReviewAnalysisPortal() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError('');
      try {
        const result = await api.blindReviewAnalysis();
        if (!cancelled) setAnalysis(result);
      } catch (err) {
        if (!cancelled) setError(err.message || 'Unable to load reviewer analysis.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <main className="review-analysis-shell">
        <section className="review-analysis-loading">
          <span className="eyebrow">Circular Industry AI</span>
          <h1>Loading multi-reviewer analysis…</h1>
        </section>
      </main>
    );
  }

  if (error || !analysis) {
    return (
      <main className="review-analysis-shell">
        <section className="review-analysis-loading">
          <span className="eyebrow">Circular Industry AI</span>
          <h1>Reviewer analysis unavailable</h1>
          <p>{error || 'No analysis response was returned.'}</p>
        </section>
      </main>
    );
  }

  const enoughForComparison = analysis.cases_with_multiple_reviewers > 0;

  return (
    <main className="review-analysis-shell">
      <section className="review-analysis-hero">
        <div>
          <span className="eyebrow">Validation analysis workspace</span>
          <h1>Multi-reviewer agreement</h1>
          <p>
            This view summarises how reviewers agree with each other and where Circular Industry AI aligns with the
            leading reviewer judgement. Reviewer consensus is not treated as ground truth.
          </p>
        </div>
        <div className="review-analysis-hero-note">
          <strong>{analysis.unique_reviewers}</strong>
          <span>self-identified reviewers</span>
          <small>{analysis.deduplicated_submission_count} latest reviewer-case judgements analysed</small>
        </div>
      </section>

      <section className="review-analysis-boundary">
        <strong>Interpretation boundary</strong>
        <p>{analysis.governance_note}</p>
      </section>

      <section className="review-analysis-summary-grid">
        <article>
          <span>Cases reviewed</span>
          <strong>{analysis.unique_cases_reviewed}</strong>
          <small>{analysis.cases_with_multiple_reviewers} have at least two reviewers</small>
        </article>
        <article>
          <span>Reviewer pair agreement · strategy</span>
          <strong>{pct(analysis.overall_pairwise_agreement.strategy_pct)}</strong>
          <small>Same strategy label on shared cases</small>
        </article>
        <article>
          <span>Reviewer pair agreement · risk</span>
          <strong>{pct(analysis.overall_pairwise_agreement.risk_pct)}</strong>
          <small>Same risk label on shared cases</small>
        </article>
        <article>
          <span>Reviewer pair agreement · human review</span>
          <strong>{pct(analysis.overall_pairwise_agreement.human_review_pct)}</strong>
          <small>Same review-gate decision on shared cases</small>
        </article>
      </section>

      {!enoughForComparison && (
        <section className="review-analysis-empty">
          <h2>More reviewers are needed for inter-reviewer agreement.</h2>
          <p>
            The system can store and compare a single reviewer with Circular Industry AI, but reviewer consensus and
            pairwise agreement only become meaningful once at least two independent reviewers assess the same case.
          </p>
        </section>
      )}

      <section className="review-system-consensus">
        <div className="section-heading compact-heading">
          <div>
            <h2>System vs reviewer consensus</h2>
            <p>Only cases with at least two reviewers and a non-tied leading label are eligible.</p>
          </div>
          <span>{analysis.cases_with_multiple_reviewers} multi-reviewer cases</span>
        </div>

        <div className="review-system-consensus-grid">
          {[
            ['Strategy', analysis.system_consensus_match.strategy],
            ['Risk', analysis.system_consensus_match.risk],
            ['Human review', analysis.system_consensus_match.human_review],
          ].map(([label, metric]) => (
            <article key={label}>
              <span>{label}</span>
              <strong>{pct(metric.match_pct)}</strong>
              <small>{metric.matched} matches from {metric.eligible} eligible cases</small>
            </article>
          ))}
        </div>
      </section>

      <section className="review-analysis-case-list">
        {analysis.cases.length === 0 ? (
          <article className="review-analysis-empty">
            <h2>No reviewer submissions yet.</h2>
            <p>Send reviewers the blind-review portal first, then return here after submissions are stored.</p>
          </article>
        ) : (
          analysis.cases.map((item) => (
            <article className="review-analysis-case" key={item.case_id}>
              <div className="review-analysis-case-header">
                <div>
                  <span className="record-id">{item.case_id}</span>
                  <h2>{item.reviewer_count} reviewer{item.reviewer_count === 1 ? '' : 's'}</h2>
                </div>
                <span className={item.system_snapshot_consistent ? 'review-snapshot stable' : 'review-snapshot changed'}>
                  {item.system_snapshot_consistent
                    ? 'System snapshot stable'
                    : `${item.system_snapshot_count} system snapshots`}
                </span>
              </div>

              <div className="review-consensus-grid">
                {[
                  ['Strategy', item.strategy_consensus, item.system_matches_strategy_consensus],
                  ['Risk', item.risk_consensus, item.system_matches_risk_consensus],
                  ['Human review', item.human_review_consensus, item.system_matches_human_review_consensus],
                ].map(([label, consensus, systemMatch]) => (
                  <div className="review-consensus-card" key={label}>
                    <span>{label}</span>
                    <strong>{consensus.leading_label === null ? 'No stable leader' : humanise(consensus.leading_label)}</strong>
                    <small>
                      {humanise(consensus.consensus_status)} · {consensus.leading_share_pct}% leading share
                    </small>
                    <small>Reviewer pair agreement: {pct(consensus.pairwise_agreement_pct)}</small>
                    <b className={
                      systemMatch === null
                        ? 'review-system-match neutral'
                        : systemMatch
                          ? 'review-system-match yes'
                          : 'review-system-match no'
                    }>
                      {matchLabel(systemMatch)}
                    </b>
                  </div>
                ))}
              </div>

              <div className="review-analysis-system-box">
                <span>Latest stored system snapshot</span>
                <div>
                  <strong>{item.latest_system_snapshot.strategy_category}</strong>
                  <strong>Risk: {humanise(item.latest_system_snapshot.risk_level)}</strong>
                  <strong>Human review: {yesNo(item.latest_system_snapshot.human_review_required)}</strong>
                </div>
                <p>{item.latest_system_snapshot.recommended_action}</p>
                <small>Rule: {item.latest_system_snapshot.rule_applied}</small>
              </div>

              <div className="review-reasoning-list">
                <h3>Reviewer reasoning</h3>
                {item.reviewer_reasoning.map((review, index) => (
                  <article key={`${item.case_id}-${review.reviewer_name}-${index}`}>
                    <div>
                      <strong>{review.reviewer_name}</strong>
                      <span>{review.reviewer_role}{review.reviewer_organisation ? ` · ${review.reviewer_organisation}` : ''}</span>
                    </div>
                    <span className="review-confidence">Confidence {review.confidence}/5</span>
                    <p>{review.reasoning}</p>
                  </article>
                ))}
              </div>
            </article>
          ))
        )}
      </section>
    </main>
  );
}
