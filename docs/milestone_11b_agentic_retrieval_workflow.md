# Milestone 11B: Agentic Retrieval Workflow

## Purpose

Milestone 11B adds a controlled multi-step retrieval workflow.

This is the move from one-pass retrieval toward rules-locked agentic intelligence.

The system now orchestrates:

```text
1. classify stream context
2. retrieve controlled knowledge
3. build graph relationships
4. generate autonomous insight
5. optionally persist and audit the insight
```

## Why this matters

10C retrieved knowledge.
10D generated insight.
10E saved insight history.
11A explained graph relationships.

11B turns those parts into a single deterministic workflow.

## New backend module

```text
backend/app/agentic_retrieval/service.py
```

## New endpoints

```text
POST /api/agentic-retrieval/run
POST /api/agentic-retrieval/run-and-save
GET  /api/agentic-retrieval/stream/{stream_id}
POST /api/agentic-retrieval/stream/{stream_id}/run-and-save
```

## Workflow output

The workflow returns:

- workflow ID
- workflow mode
- stream context
- workflow steps
- quality gates
- retrieval summary
- relationship summary
- graph
- insight
- saved insight ID if persistence was requested
- governance note

## Quality gates

The workflow checks:

- notes independence
- material match
- false-positive control for plastics
- human review control
- claim boundary presence
- graph relationship presence

## Governance boundary

11B is agentic in workflow structure, not in decision ownership.

It does not allow an LLM or workflow layer to override:

- risk level
- human-review status
- rule applied
- claim boundary
- evidence quality
- verified impact
- legal/compliance status

## Product significance

11B gives Circular Industry AI a proper operational workflow:

```text
raw stream data
→ structured context
→ retrieved knowledge
→ graph explanation
→ generated insight
→ saved traceable record
```

This is a controlled agentic system, not a free-roaming AI agent.
