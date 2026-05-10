import { useMemo, useState } from 'react';

function StatusPill({ value }) {
  const safe = String(value || 'unknown').toLowerCase();
  return <span className={`agentic-pill status-${safe}`}>{value || 'unknown'}</span>;
}

function MiniMetric({ label, value, note }) {
  return (
    <article className="agentic-metric">
      <span>{label}</span>
      <strong>{value}</strong>
      {note && <small>{note}</small>}
    </article>
  );
}

function StepList({ steps = [] }) {
  return (
    <div className="agentic-step-list">
      {steps.map((step) => (
        <article key={step.step_id} className="agentic-step-card">
          <div>
            <span>{step.step_id}</span>
            <h4>{step.name}</h4>
          </div>
          <StatusPill value={step.status} />
          <p>{step.summary}</p>
          {step.outputs?.length > 0 && (
            <ul>
              {step.outputs.slice(0, 5).map((item) => <li key={`${step.step_id}-${item}`}>{item}</li>)}
            </ul>
          )}
        </article>
      ))}
    </div>
  );
}

function QualityGates({ gates = [] }) {
  return (
    <div className="agentic-gate-grid">
      {gates.map((gate) => (
        <article key={gate.gate} className="agentic-gate-card">
          <div>
            <strong>{gate.gate.replaceAll('_', ' ')}</strong>
            <StatusPill value={gate.status} />
          </div>
          <p>{gate.detail}</p>
        </article>
      ))}
    </div>
  );
}

function GraphSummary({ workflow }) {
  const graph = workflow?.graph;
  const relationshipSummary = workflow?.relationship_summary;

  if (!graph) {
    return <p className="muted">Run agentic workflow to inspect graph relationships.</p>;
  }

  return (
    <div className="agentic-graph-view">
      <div className="agentic-metric-grid compact">
        <MiniMetric label="Graph nodes" value={graph.nodes?.length || 0} note="relationship objects" />
        <MiniMetric label="Graph edges" value={graph.edges?.length || 0} note="mapped relationships" />
        <MiniMetric label="Graph path" value={graph.graph_path?.length || 0} note="explanation steps" />
        <MiniMetric label="Knowledge IDs" value={graph.source_knowledge_ids?.length || 0} note="traceable sources" />
      </div>

      <div className="agentic-split">
        <article>
          <h4>Relationship types</h4>
          {!relationshipSummary?.relationship_breakdown && <p className="muted">No relationship summary available.</p>}
          {Object.entries(relationshipSummary?.relationship_breakdown || {}).map(([key, value]) => (
            <div className="agentic-row" key={key}>
              <span>{key.replaceAll('_', ' ')}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </article>
        <article>
          <h4>Graph path</h4>
          <ol>
            {(graph.graph_path || []).slice(0, 8).map((item) => <li key={item}>{item}</li>)}
          </ol>
        </article>
      </div>
    </div>
  );
}

function InsightSummary({ workflow }) {
  const insight = workflow?.insight;

  if (!insight) {
    return <p className="muted">Run agentic workflow to generate insight output.</p>;
  }

  return (
    <div className="agentic-insight-grid">
      <article>
        <h4>Insight summary</h4>
        <p>{insight.insight_summary}</p>
        <small>{insight.governance_note}</small>
      </article>
      <article>
        <h4>Current action</h4>
        <p>{insight.current_action?.content}</p>
      </article>
      <article>
        <h4>Near-future action</h4>
        <p>{insight.near_future_action?.content}</p>
      </article>
      <article>
        <h4>Claim boundary</h4>
        <p>{insight.claim_boundary}</p>
      </article>
      <article>
        <h4>Evidence needed</h4>
        <ul>{(insight.evidence_needed || []).slice(0, 8).map((item) => <li key={item}>{item}</li>)}</ul>
      </article>
      <article>
        <h4>Do not claim</h4>
        <ul>{(insight.do_not_claim || []).slice(0, 8).map((item) => <li key={item}>{item}</li>)}</ul>
      </article>
    </div>
  );
}

function HistoryList({ history = [] }) {
  if (!history.length) {
    return <p className="muted">No saved insights loaded for this stream yet.</p>;
  }

  return (
    <div className="agentic-history-list">
      {history.slice(0, 6).map((item) => (
        <article key={item.id} className="agentic-history-card">
          <div>
            <strong>Insight #{item.id}</strong>
            <StatusPill value={item.generation_mode} />
          </div>
          <p>{item.insight_summary}</p>
          <small>{new Date(item.created_at).toLocaleString()} · {item.notes_dependency}</small>
        </article>
      ))}
    </div>
  );
}

function EvaluationSummary({ evaluation }) {
  if (!evaluation) {
    return <p className="muted">Run evaluation to inspect retrieval and insight quality.</p>;
  }

  return (
    <div className="agentic-evaluation">
      <div className="agentic-metric-grid compact">
        <MiniMetric label="Overall status" value={evaluation.overall_status} note="suite result" />
        <MiniMetric label="Cases" value={evaluation.total_cases} note="evaluation scenarios" />
        <MiniMetric label="Failed checks" value={evaluation.failed_checks} note="must fix" />
        <MiniMetric label="Review checks" value={evaluation.review_checks} note="quality review" />
      </div>

      <div className="agentic-case-list">
        {(evaluation.results || []).map((result) => (
          <article key={result.case_id} className="agentic-case-card">
            <div>
              <h4>{result.title}</h4>
              <StatusPill value={result.status} />
            </div>
            <p>{result.case_id}</p>
            <small>
              Families: {(result.matched_material_families || []).join(', ') || 'none'} · Sources: {result.source_knowledge_ids?.length || 0}
            </small>
          </article>
        ))}
      </div>
    </div>
  );
}

export default function AgenticIntelligencePanel({
  streams = [],
  workflow,
  history = [],
  evaluation,
  onRunWorkflow,
  onRunAndSaveWorkflow,
  onLoadHistory,
  onRunEvaluation,
  busy,
}) {
  const [selectedStreamId, setSelectedStreamId] = useState(streams[0]?.stream_id || '');

  const selectedStream = useMemo(
    () => streams.find((stream) => stream.stream_id === selectedStreamId),
    [streams, selectedStreamId],
  );

  const canRun = Boolean(selectedStreamId) && !busy;

  return (
    <section className="agentic-panel">
      <div className="section-heading compact-heading">
        <div>
          <h2>Agentic intelligence operator</h2>
          <p>
            Inspect the controlled workflow that links raw stream data to retrieval, graph relationships,
            autonomous insight, saved history and evaluation checks.
          </p>
        </div>
        <span>Rules locked</span>
      </div>

      <div className="agentic-toolbar">
        <label>
          Stream
          <select value={selectedStreamId} onChange={(event) => setSelectedStreamId(event.target.value)}>
            {streams.map((stream) => (
              <option key={stream.stream_id} value={stream.stream_id}>
                {stream.stream_id} · {stream.stream_name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" disabled={!canRun} onClick={() => onRunWorkflow(selectedStreamId)}>
          Run workflow
        </button>
        <button type="button" disabled={!canRun} onClick={() => onRunAndSaveWorkflow(selectedStreamId)}>
          Run + save
        </button>
        <button type="button" className="secondary" disabled={!canRun} onClick={() => onLoadHistory(selectedStreamId)}>
          Load history
        </button>
        <button type="button" className="secondary" disabled={busy} onClick={onRunEvaluation}>
          Run evaluation
        </button>
      </div>

      {selectedStream && (
        <div className="agentic-selected-stream">
          <strong>{selectedStream.stream_name}</strong>
          <span>{selectedStream.material} · {selectedStream.source_process} · {selectedStream.contamination_risk} contamination</span>
        </div>
      )}

      <div className="agentic-metric-grid">
        <MiniMetric label="Workflow mode" value={workflow?.workflow_mode || 'not run'} note="deterministic first" />
        <MiniMetric label="Saved insight" value={workflow?.saved_insight_id || 'none'} note={workflow?.save_insight ? 'persisted' : 'stateless'} />
        <MiniMetric label="Matched families" value={workflow?.retrieval_summary?.matched_material_families?.join(', ') || 'none'} note="retrieval output" />
        <MiniMetric label="Quality gates" value={workflow?.quality_gates?.length || 0} note="workflow checks" />
      </div>

      <div className="agentic-section">
        <h3>Workflow steps</h3>
        <StepList steps={workflow?.steps || []} />
      </div>

      <div className="agentic-section">
        <h3>Quality gates</h3>
        <QualityGates gates={workflow?.quality_gates || []} />
      </div>

      <div className="agentic-section">
        <h3>Knowledge graph path</h3>
        <GraphSummary workflow={workflow} />
      </div>

      <div className="agentic-section">
        <h3>Generated insight</h3>
        <InsightSummary workflow={workflow} />
      </div>

      <div className="agentic-two-column">
        <section className="agentic-section">
          <h3>Saved insight history</h3>
          <HistoryList history={history} />
        </section>
        <section className="agentic-section">
          <h3>Evaluation summary</h3>
          <EvaluationSummary evaluation={evaluation} />
        </section>
      </div>

      <p className="governance-strip">
        Agentic intelligence output is advisory. The workflow explains retrieval, graph relationships and generated
        insight, but it does not verify legal compliance, supplier acceptance, verified diversion, carbon savings,
        financial savings or completed operational impact.
      </p>
    </section>
  );
}
