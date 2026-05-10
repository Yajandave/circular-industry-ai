# Milestone 10C: Knowledge Retrieval Engine

## Purpose

Milestone 10C connects raw stream data to the structured knowledge base created in 10B.

This is the first operational step toward agentic circular economy intelligence:

```text
raw stream data
→ matched material knowledge
→ matched circular route knowledge
→ matched evidence rules
→ matched future-horizon knowledge
```

## New backend module

```text
backend/app/knowledge_base/retriever.py
```

## New endpoints

```text
GET  /api/knowledge/validate
POST /api/knowledge/match
GET  /api/knowledge/stream/{stream_id}
```

## What it proves

The system can retrieve relevant knowledge even when the uploaded stream has blank notes.

Example:

```text
material = mixed plastics
source_process = injection moulding
contamination_risk = high
hazardous_flag = false
notes = blank
```

The retriever can still match:

```text
material_plastics_v1
route_specialist_recovery_v1
route_process_redesign_v1
evidence_claim_readiness_v1
future_plastics_advanced_recycling_v1
```

## Product principle

The dataset supplies raw facts.

The knowledge base supplies domain understanding.

The AI layer will later use retrieved knowledge to generate insight, explanations, supplier questions and reports.

## Governance boundary

Knowledge retrieval provides advisory context. It does not verify legal compliance, supplier acceptance, circularity claims, carbon savings, financial savings or operational impact.
