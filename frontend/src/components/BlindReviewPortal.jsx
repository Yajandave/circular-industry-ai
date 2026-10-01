import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client.js';

const EMPTY_REVIEWER = {
  reviewer_name: '',
  reviewer_role: '',
  reviewer_organisation: '',
  reviewer_declared_blind: false,
};

function emptyAnswer() {
  return {
    strategy_category: '',
    risk_level: '',
    human_review_required: '',
    confidence: 3,
    reasoning: '',
  };
}

function humanise(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function yesNo(value) {
  return value ? 'Yes' : 'No';
}

function riskClass(value) {
  return `blind-risk blind-risk-${value || 'unknown'}`;
}

export default function BlindReviewPortal() {
  const [pack, setPack] = useState([]);
  const [answers, setAnswers] = useState({});
  const [reviewer, setReviewer] = useState(EMPTY_REVIEWER);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [submission, setSubmission] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadPack() {
      setLoading(true);
      setError('');
      try {
        const result = await api.blindDecisionReviewPack();
        if (cancelled) return;
        setPack(result);
        setAnswers(Object.fromEntries(result.map((item) => [item.case_id, emptyAnswer()])));
      } catch (err) {
        if (!cancelled) setError(err.message || 'Unable to load the blind reviewer pack.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPack();
    return () => {
      cancelled = true;
    };
  }, []);

  const currentCase = pack[currentIndex] || null;
  const caseLookup = useMemo(
    () => Object.fromEntries(pack.map((item) => [item.case_id, item])),
    [pack],
  );

  function answerComplete(caseId) {
    const answer = answers[caseId];
    return Boolean(
      answer
      && answer.strategy_category
      && answer.risk_level
      && typeof answer.human_review_required === 'boolean'
      && answer.confidence >= 1
      && answer.confidence <= 5
      && answer.reasoning.trim(),
    );
  }

  const completedCount = pack.filter((item) => answerComplete(item.case_id)).length;
  const allCasesComplete = pack.length > 0 && completedCount === pack.length;
  const reviewerComplete = Boolean(
    reviewer.reviewer_name.trim()
    && reviewer.reviewer_role.trim()
    && reviewer.reviewer_declared_blind,
  );

  function updateReviewer(key, value) {
    setReviewer((current) => ({ ...current, [key]: value }));
    setError('');
  }

  function updateAnswer(caseId, key, value) {
    setAnswers((current) => ({
      ...current,
      [caseId]: {
        ...current[caseId],
        [key]: value,
      },
    }));
    setError('');
  }

  function moveTo(index) {
    setCurrentIndex(Math.max(0, Math.min(index, pack.length - 1)));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function submitReview(event) {
    event.preventDefault();
    setError('');

    if (!reviewer.reviewer_name.trim()) {
      setError('Enter your name before submitting the review.');
      return;
    }
    if (!reviewer.reviewer_role.trim()) {
      setError('Enter your professional role before submitting the review.');
      return;
    }
    if (!reviewer.reviewer_declared_blind) {
      setError('Confirm the blind-review declaration before submitting.');
      return;
    }
    if (!allCasesComplete) {
      const firstIncomplete = pack.findIndex((item) => !answerComplete(item.case_id));
      setError('Complete all 10 cases before submitting the blind review.');
      if (firstIncomplete >= 0) moveTo(firstIncomplete);
      return;
    }

    const payload = {
      reviewer_name: reviewer.reviewer_name.trim(),
      reviewer_role: reviewer.reviewer_role.trim(),
      reviewer_organisation: reviewer.reviewer_organisation.trim() || null,
      reviewer_declared_blind: true,
      labels: pack.map((item) => ({
        case_id: item.case_id,
        strategy_category: answers[item.case_id].strategy_category,
        risk_level: answers[item.case_id].risk_level,
        human_review_required: answers[item.case_id].human_review_required,
        confidence: Number(answers[item.case_id].confidence),
        reasoning: answers[item.case_id].reasoning.trim(),
      })),
    };

    setSubmitting(true);
    try {
      const result = await api.submitBlindDecisionReview(payload);
      setSubmission(result);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.message || 'Unable to submit the blind review.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <main className="blind-review-shell">
        <section className="blind-review-loading">
          <span className="eyebrow">Circular Industry AI</span>
          <h1>Loading blind reviewer pack…</h1>
          <p>The system comparison remains hidden until reviewer submission.</p>
        </section>
      </main>
    );
  }

  if (submission) {
    return (
      <main className="blind-review-shell">
        <section className="blind-review-hero blind-review-complete">
          <div>
            <span className="eyebrow">Blind review submitted</span>
            <h1>Comparison unlocked</h1>
            <p>
              Your judgement was stored before Circular Industry AI&apos;s outputs were revealed.
              The metrics below show agreement, not proof of accuracy or independent assurance.
            </p>
          </div>
          <div className="blind-review-hero-note">
            <strong>{submission.total_labels} cases</strong>
            <span>{submission.submission_batch_id}</span>
          </div>
        </section>

        <section className="blind-review-metrics">
          <article>
            <span>Strategy agreement</span>
            <strong>{submission.strategy_agreement_pct}%</strong>
            <small>{submission.strategy_agreement_count} of {submission.total_labels} cases</small>
          </article>
          <article>
            <span>Risk agreement</span>
            <strong>{submission.risk_agreement_pct}%</strong>
            <small>{submission.risk_agreement_count} of {submission.total_labels} cases</small>
          </article>
          <article>
            <span>Human-review agreement</span>
            <strong>{submission.human_review_agreement_pct}%</strong>
            <small>{submission.human_review_agreement_count} of {submission.total_labels} cases</small>
          </article>
          <article>
            <span>Full three-part agreement</span>
            <strong>{submission.full_agreement_pct}%</strong>
            <small>{submission.full_agreement_count} of {submission.total_labels} cases</small>
          </article>
        </section>

        <section className="blind-review-boundary">
          <strong>Interpretation boundary</strong>
          <p>{submission.governance_note}</p>
        </section>

        <section className="blind-comparison-list">
          {submission.submissions.map((record) => {
            const caseMeta = caseLookup[record.case_id];
            const fullAgreement = record.strategy_agreement
              && record.risk_agreement
              && record.human_review_agreement;

            return (
              <article className="blind-comparison-card" key={record.id}>
                <div className="blind-comparison-header">
                  <div>
                    <span className="record-id">
                      Case {caseMeta?.case_number || '—'} · {record.case_id}
                    </span>
                    <h2>{caseMeta?.stream?.stream_name || record.case_id}</h2>
                  </div>
                  <span className={fullAgreement ? 'blind-match yes' : 'blind-match no'}>
                    {fullAgreement ? 'Full agreement' : 'Difference found'}
                  </span>
                </div>

                <div className="blind-comparison-grid">
                  <div>
                    <span>Reviewer strategy</span>
                    <strong>{record.reviewer_strategy_category}</strong>
                  </div>
                  <div>
                    <span>System strategy</span>
                    <strong>{record.system_strategy_category}</strong>
                  </div>
                  <div>
                    <span>Reviewer risk</span>
                    <strong className={riskClass(record.reviewer_risk_level)}>
                      {humanise(record.reviewer_risk_level)}
                    </strong>
                  </div>
                  <div>
                    <span>System risk</span>
                    <strong className={riskClass(record.system_risk_level)}>
                      {humanise(record.system_risk_level)}
                    </strong>
                  </div>
                  <div>
                    <span>Reviewer human review?</span>
                    <strong>{yesNo(record.reviewer_human_review_required)}</strong>
                  </div>
                  <div>
                    <span>System human review?</span>
                    <strong>{yesNo(record.system_human_review_required)}</strong>
                  </div>
                </div>

                <div className="blind-review-reasoning">
                  <span>Your reasoning · confidence {record.reviewer_confidence}/5</span>
                  <p>{record.reviewer_reasoning}</p>
                </div>

                <div className="blind-system-action">
                  <span>System action revealed after submission</span>
                  <p>{record.system_recommended_action}</p>
                  <small>Rule snapshot: {record.system_rule_applied}</small>
                </div>
              </article>
            );
          })}
        </section>
      </main>
    );
  }

  const currentAnswer = currentCase ? answers[currentCase.case_id] : null;

  return (
    <main className="blind-review-shell">
      <section className="blind-review-hero">
        <div>
          <span className="eyebrow">Independent reviewer workspace</span>
          <h1>Blind circular-decision review</h1>
          <p>
            Assess each material-stream case using only the information shown here.
            Circular Industry AI&apos;s recommendations, rules and validation answers remain hidden until you submit the full review.
          </p>
        </div>
        <div className="blind-review-hero-note">
          <strong>{completedCount} / {pack.length}</strong>
          <span>cases complete</span>
          <button type="button" className="secondary" onClick={() => window.print()}>
            Print / save pack
          </button>
        </div>
      </section>

      <section className="blind-review-boundary">
        <strong>Blind-review condition</strong>
        <p>
          Do not use the main Circular Industry AI application, recommendation endpoints, rule documentation,
          20C validation answers or challenge summaries while completing this review.
        </p>
      </section>

      <section className="blind-print-pack" aria-hidden="true">
        <div className="blind-print-heading">
          <h1>Circular Industry AI · Blind reviewer pack</h1>
          <p>
            Reviewer: {reviewer.reviewer_name || '________________'} · Role: {reviewer.reviewer_role || '________________'}
          </p>
          <p>
            Complete these cases without viewing Circular Industry AI recommendations, rules, grounded constraints or expected answers.
          </p>
        </div>
        {pack.map((item) => (
          <article className="blind-print-case" key={item.case_id}>
            <h2>Case {item.case_number}: {item.stream.stream_name}</h2>
            <dl>
              <div><dt>Material</dt><dd>{item.stream.material}</dd></div>
              <div><dt>Source process</dt><dd>{item.stream.source_process}</dd></div>
              <div><dt>Monthly quantity</dt><dd>{item.stream.monthly_quantity_kg} kg</dd></div>
              <div><dt>Current route</dt><dd>{item.stream.current_route}</dd></div>
              <div><dt>Contamination risk</dt><dd>{item.stream.contamination_risk}</dd></div>
              <div><dt>Hazardous flag</dt><dd>{item.stream.hazardous_flag}</dd></div>
              <div><dt>Supplier take-back</dt><dd>{item.stream.supplier_takeback_available}</dd></div>
              <div><dt>Department</dt><dd>{item.stream.department}</dd></div>
            </dl>
            {item.stream.notes && <p><strong>Notes:</strong> {item.stream.notes}</p>}
            <div className="blind-print-response-lines">
              <p><strong>Strategy category:</strong> ______________________________________________</p>
              <p><strong>Risk level:</strong> __________________</p>
              <p><strong>Human review required?</strong> __________________</p>
              <p><strong>Confidence (1–5):</strong> __________________</p>
              <p><strong>Reasoning:</strong></p>
              <div className="blind-print-lines">________________________________________________________________________________<br />________________________________________________________________________________<br />________________________________________________________________________________</div>
            </div>
          </article>
        ))}
      </section>

      <form onSubmit={submitReview}>
        <section className="blind-reviewer-card">
          <div className="section-heading compact-heading">
            <div>
              <h2>Reviewer details</h2>
              <p>These details are stored with the immutable review record.</p>
            </div>
            <span>Required before submission</span>
          </div>

          <div className="blind-reviewer-grid">
            <label>
              <span>Name</span>
              <input
                type="text"
                value={reviewer.reviewer_name}
                onChange={(event) => updateReviewer('reviewer_name', event.target.value)}
                placeholder="Reviewer name"
                disabled={submitting}
              />
            </label>
            <label>
              <span>Professional role</span>
              <input
                type="text"
                value={reviewer.reviewer_role}
                onChange={(event) => updateReviewer('reviewer_role', event.target.value)}
                placeholder="e.g. Waste & Resource Manager"
                disabled={submitting}
              />
            </label>
            <label>
              <span>Organisation (optional)</span>
              <input
                type="text"
                value={reviewer.reviewer_organisation}
                onChange={(event) => updateReviewer('reviewer_organisation', event.target.value)}
                placeholder="Organisation"
                disabled={submitting}
              />
            </label>
          </div>

          <label className="blind-declaration">
            <input
              type="checkbox"
              checked={reviewer.reviewer_declared_blind}
              onChange={(event) => updateReviewer('reviewer_declared_blind', event.target.checked)}
              disabled={submitting}
            />
            <span>
              I confirm that I have not viewed Circular Industry AI&apos;s answer, rule, expected validation label or grounded case interpretation before making these judgements.
            </span>
          </label>
        </section>

        {currentCase && currentAnswer && (
          <section className="blind-case-card">
            <div className="blind-case-topline">
              <div>
                <span className="record-id">
                  Case {currentCase.case_number} of {pack.length}
                </span>
                <h2>{currentCase.stream.stream_name}</h2>
              </div>
              <span className={answerComplete(currentCase.case_id) ? 'blind-case-status complete' : 'blind-case-status'}>
                {answerComplete(currentCase.case_id) ? 'Complete' : 'Needs response'}
              </span>
            </div>

            <div className="blind-stream-grid">
              {[
                ['Material', currentCase.stream.material],
                ['Source process', currentCase.stream.source_process],
                ['Monthly quantity', `${currentCase.stream.monthly_quantity_kg} kg`],
                ['Current route', currentCase.stream.current_route],
                ['Contamination risk', currentCase.stream.contamination_risk],
                ['Hazardous flag', currentCase.stream.hazardous_flag],
                ['Supplier take-back', currentCase.stream.supplier_takeback_available],
                ['Department', currentCase.stream.department],
              ].map(([label, value]) => (
                <div key={label}>
                  <span>{label}</span>
                  <strong>{value || 'Not provided'}</strong>
                </div>
              ))}
            </div>

            {currentCase.stream.notes && (
              <div className="blind-case-notes">
                <span>Case notes</span>
                <p>{currentCase.stream.notes}</p>
              </div>
            )}

            <div className="blind-question-grid">
              <label>
                <span>Screening strategy category</span>
                <select
                  value={currentAnswer.strategy_category}
                  onChange={(event) => updateAnswer(currentCase.case_id, 'strategy_category', event.target.value)}
                  disabled={submitting}
                >
                  <option value="">Select a category</option>
                  {currentCase.strategy_category_options.map((option) => (
                    <option value={option} key={option}>{option}</option>
                  ))}
                </select>
              </label>

              <label>
                <span>Risk level</span>
                <select
                  value={currentAnswer.risk_level}
                  onChange={(event) => updateAnswer(currentCase.case_id, 'risk_level', event.target.value)}
                  disabled={submitting}
                >
                  <option value="">Select risk</option>
                  {currentCase.risk_level_options.map((option) => (
                    <option value={option} key={option}>{humanise(option)}</option>
                  ))}
                </select>
              </label>

              <label>
                <span>Human review required?</span>
                <select
                  value={
                    typeof currentAnswer.human_review_required === 'boolean'
                      ? String(currentAnswer.human_review_required)
                      : ''
                  }
                  onChange={(event) => updateAnswer(
                    currentCase.case_id,
                    'human_review_required',
                    event.target.value === '' ? '' : event.target.value === 'true',
                  )}
                  disabled={submitting}
                >
                  <option value="">Select</option>
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </label>

              <label>
                <span>Confidence</span>
                <select
                  value={currentAnswer.confidence}
                  onChange={(event) => updateAnswer(currentCase.case_id, 'confidence', Number(event.target.value))}
                  disabled={submitting}
                >
                  <option value={1}>1 · very uncertain</option>
                  <option value={2}>2</option>
                  <option value={3}>3 · moderate</option>
                  <option value={4}>4</option>
                  <option value={5}>5 · very confident</option>
                </select>
              </label>
            </div>

            <label className="blind-reasoning-field">
              <span>Reasoning</span>
              <textarea
                rows="5"
                value={currentAnswer.reasoning}
                onChange={(event) => updateAnswer(currentCase.case_id, 'reasoning', event.target.value)}
                placeholder="Explain the decision you would make from the case information alone, including any uncertainty or evidence you would want before implementation."
                disabled={submitting}
              />
            </label>

            <p className="blind-case-prompt">{currentCase.reviewer_prompt}</p>

            <div className="blind-case-nav">
              <button
                type="button"
                className="secondary"
                onClick={() => moveTo(currentIndex - 1)}
                disabled={currentIndex === 0 || submitting}
              >
                Previous case
              </button>

              <div className="blind-case-dots" aria-label="Review case progress">
                {pack.map((item, index) => (
                  <button
                    type="button"
                    key={item.case_id}
                    className={`blind-case-dot ${index === currentIndex ? 'active' : ''} ${answerComplete(item.case_id) ? 'complete' : ''}`}
                    onClick={() => moveTo(index)}
                    aria-label={`Open case ${index + 1}`}
                    disabled={submitting}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>

              <button
                type="button"
                onClick={() => moveTo(currentIndex + 1)}
                disabled={currentIndex === pack.length - 1 || submitting}
              >
                Next case
              </button>
            </div>
          </section>
        )}

        <section className="blind-submit-card">
          <div>
            <h2>Submit blind review</h2>
            <p>
              Submission unlocks Circular Industry AI&apos;s comparison. Your original judgements are stored unchanged.
            </p>
          </div>
          <div className="blind-submit-actions">
            <strong>{completedCount} / {pack.length} cases complete</strong>
            <button
              type="submit"
              disabled={!reviewerComplete || !allCasesComplete || submitting}
            >
              {submitting ? 'Submitting blind review…' : 'Submit and unlock comparison'}
            </button>
          </div>
        </section>

        {error && <p className="blind-review-error">{error}</p>}
      </form>
    </main>
  );
}
