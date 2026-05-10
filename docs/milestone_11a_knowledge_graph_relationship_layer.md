# Milestone 11A: Knowledge Graph Relationship Layer

## Purpose

Milestone 11A adds an explicit relationship layer on top of the knowledge base and retriever.

The system already does:

```text
10B: structured knowledge base
10C: retrieval engine
10D: autonomous insight generator
10E: saved insight history
```

11A adds:

```text
stream
→ material family
→ route options
→ evidence requirements
→ blockers
→ human review triggers
→ unsafe claims
→ claim boundaries
→ future-watch routes
```

## Why this matters

Basic retrieval can say which records matched.

The graph layer explains how those records relate.

This helps the product move toward Graph-RAG-style intelligence while keeping the rules engine locked.

## New backend module

```text
backend/app/knowledge_graph/service.py
```

## New endpoints

```text
GET  /api/knowledge/graph
POST /api/knowledge/graph/match
GET  /api/knowledge/graph/stream/{stream_id}
```

## What the stream graph returns

- graph scope
- stream ID
- nodes
- edges
- graph path
- matched material families
- source knowledge IDs
- retrieval notes
- knowledge validation
- governance note

## Example relationship path

For blank-notes mixed plastics input:

```text
stream: RAW001
→ material family: plastics
→ blocker: mixed polymer types
→ blocker: high contamination
→ route: process redesign
→ route: specialist recovery
→ evidence: polymer type
→ evidence: contamination assessment
→ unsafe claim: verified recycling without recycler acceptance
→ future watch: advanced recycling for difficult plastic streams
```

## Governance boundary

The graph explains relationships behind advisory intelligence.

It does not verify:

- route feasibility
- supplier acceptance
- legal compliance
- circularity claims
- verified diversion
- carbon savings
- financial savings
- operational impact

## Product significance

11A makes the system more explainable.

Instead of only returning recommendations or insights, Circular Industry AI can now show the relationship logic behind advisory outputs.
