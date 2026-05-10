# Milestone 10E: Insight History, Persistence and Traceability

## Purpose

Milestone 10D proved that Circular Industry AI can generate deterministic advisory intelligence from raw stream data and retrieved knowledge.

Milestone 10E turns those generated insights into auditable product records.

The product movement is:

```text
generate insight on request
→ save insight record
→ retrieve history
→ retrieve latest insight
→ audit what was generated and why
```

## Why this matters

A business-grade circular economy intelligence system cannot rely on temporary generated output.

Users need to know:

- when an insight was generated
- what stream input it used
- which material families matched
- which knowledge IDs supported the advice
- what evidence was missing
- what supplier questions were generated
- what claim boundary applied
- whether notes were present
- whether notes were required
- whether the insight was deterministic or LLM-based

## New persistence layer

A new `generated_insights` table stores the generated advisory output.

Stored records include:

- stream identity
- input snapshot
- matched material families
- current action
- near-future action
- future watch
- evidence needed
- supplier questions
- human review triggers
- do-not-claim boundaries
- claim boundary
- source knowledge IDs
- retrieval notes
- notes dependency
- generation mode
- governance note
- created timestamp

## New endpoints

```text
POST /api/insights/generate-and-save
POST /api/insights/stream/{stream_id}/generate-and-save
GET  /api/insights/history
GET  /api/insights/history/{stream_id}
GET  /api/insights/latest/{stream_id}
```

The existing stateless endpoints remain:

```text
POST /api/insights/generate
GET  /api/insights/stream/{stream_id}
```

## Audit behaviour

Each saved insight creates an audit event:

```text
event_type: insight_generated
entity_type: stream
source: autonomous_insight_generator
decision_source: deterministic_knowledge_retrieval
```

The audit metadata includes:

- generated insight ID
- analysis run ID if available
- source knowledge IDs
- notes dependency
- input notes presence
- generation mode

## Governance boundary

Saved insights are advisory records.

They do not verify:

- legal compliance
- supplier acceptance
- circularity claims
- carbon savings
- financial savings
- completed diversion
- operational impact

## Product significance

10E makes the system stronger because insight generation becomes traceable, repeatable and auditable.

This prepares the product for later:

- insight comparison
- stale insight detection
- stream-change detection
- approval workflows
- Graph-RAG relationships
- controlled agentic workflows
