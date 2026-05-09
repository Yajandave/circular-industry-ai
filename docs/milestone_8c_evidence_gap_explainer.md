# Milestone 8C: AI Evidence Gap Explainer

## Purpose

Milestone 8C adds a stream-level AI evidence gap explainer to the Evidence Register.

The feature explains:

- why a stream is not claim-ready
- what evidence is missing
- what supplier documents are needed
- what process checks should be completed
- what can be safely said now
- what claims must not be made yet

## Governance boundary

The explainer is advisory only. It cannot override risk level, human review status, rule applied, recommendation route, evidence status, claim readiness, review gate, claim boundary or verified impact.

## Backend endpoint

```text
POST /api/evidence-register/{stream_id}/ai-explainer
```

## Frontend location

The feature is added inside the Evidence Register.

## Why this matters

This milestone shows the difference between a screening estimate and a verified claim. That distinction is essential for audit-readiness and anti-greenwashing controls.
