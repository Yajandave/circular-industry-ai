# Milestone 14C — Data Profiler Reliability and Edge-Case Hardening Plan

## Purpose
Strengthen the Data Profiler ingestion foundation before advanced feature expansion.

## Core Risks
- Silent semantic misclassification
- Weak alias detection
- Brittle CSV assumptions
- Inconsistent null handling
- Numeric parsing edge cases
- Encoding and delimiter variability
- False confidence in inferred mappings

## Stabilisation Priorities
1. Edge-case profiling tests
2. Confidence scoring refinement
3. Explicit unknown-state handling
4. Import traceability
5. Schema validation hardening
6. Safer workspace recommendation logic
7. User-confirmed mapping workflow preparation

## Recommended Technical Areas
- Column alias registry decomposition
- Profiler logic modularisation
- Structured validation layers
- Import telemetry
- Deterministic inference testing
- Regression fixtures
- Confidence downgrade rules

## Non-Goals
- Full ESG engine
- Full GHG engine
- Autonomous orchestration
- Production deployment
- Multi-tenant architecture

## Outcome
This milestone defines the reliability hardening direction required before the profiler becomes a serious operational ingestion layer.
