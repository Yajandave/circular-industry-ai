# Milestone 11D: Operator UI for Agentic Intelligence

## Purpose

11D exposes the backend intelligence layers in the frontend.

The product already has:

- knowledge retrieval
- autonomous insight generation
- insight history
- knowledge graph relationships
- agentic retrieval workflow
- evaluation suite

11D adds an operator-facing UI so users can inspect those layers without using API calls manually.

## Frontend capability

The new Agentic Intelligence Operator panel allows users to:

- select a material stream
- run the deterministic agentic retrieval workflow
- run and save a generated insight
- load saved insight history
- run evaluation summary
- inspect workflow steps
- inspect quality gates
- inspect graph path and relationship counts
- inspect generated insight sections
- inspect claim boundaries and do-not-claim controls

## New frontend view

```text
Agentic intelligence
```

## API client additions

- agenticRetrievalForStream
- agenticRetrievalRunAndSaveForStream
- insightHistory
- evaluationSummary

## Governance boundary

The UI presents advisory intelligence and traceability.

It does not imply verified:

- legal compliance
- supplier acceptance
- route feasibility
- recycling
- circularity
- diversion
- carbon savings
- financial savings
- operational impact

## Product significance

11D turns hidden backend intelligence into an inspectable operator workflow.

This makes Circular Industry AI feel less like a dashboard and more like a controlled intelligence cockpit.
