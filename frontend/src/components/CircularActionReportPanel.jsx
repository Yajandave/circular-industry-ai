import { formatCurrency, formatNumber } from '../utils/formatters.js';

function ReportList({ title, items = [] }) {
  const safeItems = Array.isArray(items) ? items.filter(Boolean) : [];

  return (
    <article className="action-report-list-card">
      <h4>{title}</h4>
      {safeItems.length ? (
        <ul>
          {safeItems.map((item, index) => (
            <li key={`${title}-${index}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No items returned.</p>
      )}
    </article>
  );
}

function ReportSection({ title, children }) {
  return (
    <article className="action-report-section-card">
      <h4>{title}</h4>
      <p>{children}</p>
    </article>
  );
}

export default function CircularActionReportPanel({
  streams = [],
  recommendations = [],
  report = null,
  onGenerate,
  busy = false,
}) {
  const recommendationByStream = new Map(recommendations.map((rec) => [rec.stream_id, rec]));
  const reportCandidates = streams
    .filter((stream) => recommendationByStream.has(stream.stream_id))
    .map((stream) => {
      const recommendation = recommendationByStream.get(stream.stream_id);
      return {
        ...stream,
        risk_level: recommendation?.risk_level,
        human_review_required: recommendation?.human_review_required,
        evidence_quality_score: recommendation?.evidence_quality_score,
        estimated_annual_disposal_cost_avoided: recommendation?.estimated_annual_disposal_cost_avoided,
      };
    })
    .sort((a, b) => {
      const reviewSort = Number(b.human_review_required) - Number(a.human_review_required);
      if (reviewSort !== 0) return reviewSort;
      return (b.estimated_annual_disposal_cost_avoided || 0) - (a.estimated_annual_disposal_cost_avoided || 0);
    });

  return (
    <section className="circular-action-report-page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Milestone 8F</span>
          <h2>Circular action report builder</h2>
          <p>
            Generate a consultant-style stream report from locked rules, evidence, resolution planning and supplier-loop
            data. The report is designed for review packs, portfolio screenshots and print/PDF export.
          </p>
        </div>
      </div>

      <div className="action-report-candidate-panel">
        <div>
          <h3>Select a stream</h3>
          <p>
            Choose a stream with an existing rules-engine recommendation. High-risk or low-evidence streams are useful
            examples because the report shows review gates and claim boundaries clearly.
          </p>
        </div>
        <div className="action-report-candidate-grid">
          {reportCandidates.slice(0, 12).map((stream) => (
            <button
              key={stream.stream_id}
              type="button"
              className="action-report-candidate"
              onClick={() => onGenerate(stream.stream_id)}
              disabled={busy}
            >
              <span>{stream.stream_id}</span>
              <strong>{stream.stream_name}</strong>
              <small>
                {stream.material} · {stream.risk_level} · {formatCurrency(stream.estimated_annual_disposal_cost_avoided || 0)}
              </small>
            </button>
          ))}
        </div>
      </div>

      {!report && (
        <div className="empty-state action-report-empty">
          Select a stream above to generate a circular action report. Run recommendations first if no candidates appear.
        </div>
      )}

      {report && (
        <article className="circular-action-report" id="circular-action-report">
          <div className="action-report-cover">
            <div>
              <span className="eyebrow">Circular Industry AI report</span>
              <h2>{report.report_title}</h2>
              <p>{report.executive_summary}</p>
            </div>
            <div className="action-report-cover-meta">
              <span>{report.generation_mode?.replaceAll('_', ' ')}</span>
              <strong>{report.stream_id}</strong>
              <small>{report.decision_lock_status}</small>
            </div>
          </div>

          <div className="action-report-lock-grid">
            <article>
              <span>Locked recommendation</span>
              <strong>{report.locked_recommendation}</strong>
            </article>
            <article>
              <span>Risk / review</span>
              <strong>{report.locked_risk_level} · review {String(report.locked_human_review_required)}</strong>
            </article>
            <article>
              <span>Claim readiness</span>
              <strong>{report.locked_claim_readiness}</strong>
            </article>
            <article>
              <span>Procurement route</span>
              <strong>{report.locked_procurement_route}</strong>
            </article>
          </div>

          <div className="action-report-section-grid">
            <ReportSection title="Risk and review status">{report.risk_and_review_status}</ReportSection>
            <ReportSection title="Evidence position">{report.evidence_position}</ReportSection>
            <ReportSection title="Circular resolution summary">{report.circular_resolution_summary}</ReportSection>
            <ReportSection title="Supplier-loop summary">{report.supplier_loop_summary}</ReportSection>
          </div>

          <div className="action-report-list-grid">
            <ReportList title="Implementation plan" items={report.implementation_plan} />
            <ReportList title="Evidence to collect" items={report.evidence_to_collect} />
            <ReportList title="Recommended next actions" items={report.recommended_next_actions} />
            <ReportList title="Unsafe claims to avoid" items={report.unsafe_claims_to_avoid} />
          </div>

          <div className="action-report-claim-card">
            <h4>Claim boundary</h4>
            <p>{report.claim_boundary}</p>
          </div>

          <div className="governance-strip">
            {report.governance_note}
          </div>

          {!!report.validation_warnings?.length && (
            <div className="action-report-warning">
              <h4>Validation warnings</h4>
              <ul>
                {report.validation_warnings.map((warning, index) => (
                  <li key={`report-warning-${index}`}>{warning}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="action-report-print-note">
            Use your browser print command to save this report as PDF. The layout includes print-friendly styling.
          </div>
        </article>
      )}
    </section>
  );
}
