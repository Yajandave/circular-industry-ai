# Milestone 10D: Autonomous Insight Generator

## Purpose

Milestone 10D turns knowledge retrieval into generated advisory output.

This milestone proves the product can create useful circular economy statements from:

```text
raw stream data
+ retrieved material knowledge
+ retrieved circular route knowledge
+ retrieved evidence rules
+ retrieved future-horizon knowledge
```

It does not require pre-written dataset notes.

## New backend module

```text
backend/app/insight_generator/service.py
```

## New endpoints

```text
POST /api/insights/generate
GET  /api/insights/stream/{stream_id}
```

## Generated output

The generator produces:

```text
insight summary
current action
near-future action
future watch
evidence needed
supplier questions
human review triggers
do not claim boundaries
claim boundary
source knowledge IDs
```

## Product principle

```text
The dataset supplies raw facts.
The knowledge base supplies domain understanding.
The generator creates advisory interpretation.
```

## Why deterministic first?

This milestone is deterministic by design.

That proves the product can generate useful advice without depending on Gemini/OpenAI and without relying on narrative notes in the uploaded dataset.

The LLM layer can later improve language, but the core intelligence structure is now visible and testable.

## Governance boundary

Autonomous insights are advisory. They do not verify legal compliance, supplier acceptance, circularity claims, carbon savings, financial savings or operational impact.
