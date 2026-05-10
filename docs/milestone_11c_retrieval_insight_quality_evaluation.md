# Milestone 11C: Retrieval and Insight Quality Evaluation Suite

## Purpose

11C adds deterministic quality evaluation for the intelligence chain.

It evaluates:

```text
retrieval
→ knowledge graph
→ autonomous insight
→ agentic retrieval workflow
```

The aim is to catch:

- false-positive material matches
- wrong future-watch routes
- missing claim boundaries
- missing unsafe-claim controls
- weak evidence lists
- missing graph relationships
- notes dependency regression
- workflow gate failures

## Why this matters

The system is now powerful enough to generate and persist advisory intelligence.

That makes quality control more important.

11C makes the system harder to fool.

## New backend module

```text
backend/app/evaluation/service.py
```

## New endpoints

```text
GET  /api/evaluation/cases
POST /api/evaluation/run
GET  /api/evaluation/summary
```

## Evaluation cases

Initial cases include:

- mixed plastics with high contamination
- aluminium machining offcuts
- unknown generic production rejects
- paint-contaminated metal brackets

## What each case checks

Each case can check:

- expected material families
- forbidden material families
- expected knowledge IDs
- forbidden knowledge IDs
- required evidence terms
- required do-not-claim terms
- expected quality gate statuses
- claim boundary presence
- notes dependency
- graph node/edge presence

## Governance boundary

Passing an evaluation case does not verify real-world circular economy outcomes.

Evaluation only checks internal system quality.

It does not verify:

- supplier acceptance
- legal compliance
- route feasibility
- verified recycling
- verified diversion
- carbon savings
- financial savings
- operational impact

## Product significance

11C turns the product from a feature-building system into a quality-controlled intelligence system.

This should be run after major retrieval, knowledge, graph or insight-generation changes.
