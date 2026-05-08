# Circular Decision Logic

This document explains the Milestone 3 rules engine used by Circular Industry AI.

## Why rules before AI

The project uses deterministic rules before AI because industrial circular economy recommendations affect safety, compliance, procurement and operational decisions. AI-generated text can support explanation later, but it should not independently decide whether a stream is safe to reuse, recycle, recover or exchange.

## Decision hierarchy

The rules engine follows this practical circular hierarchy:

1. Avoid or reduce material use
2. Redesign process to reduce scrap
3. Reuse internally
4. Return to supplier or use take-back
5. Use as input for another process or industry
6. Closed-loop recycling
7. Open-loop recycling
8. Energy or value recovery
9. Compliant disposal where higher options are not currently viable
10. Human review where evidence, hazard or contamination risk blocks a confident recommendation

## Rule families

```text
R001_HAZARDOUS_OR_UNKNOWN_REVIEW
R002_HIGH_CONTAMINATION_REVIEW
R003_REDUCE_AT_SOURCE
R004_SUPPLIER_TAKEBACK_AVAILABLE
R005_METAL_CLOSED_LOOP
R006_PACKAGING_REUSE
R007_MIXED_PLASTIC_RECYCLING
R008_PLASTIC_CLOSED_LOOP
R009_SYMBIOSIS_OR_RESOURCE_RECOVERY
R010_SPECIALIST_RECOVERY
R999_DEFAULT_EVIDENCE_IMPROVEMENT
```

## Scoring

Each recommendation includes:

- risk level
- evidence quality score
- confidence score
- missing data
- human review flag

The score is not a sustainability claim. It is a decision-support indicator based on the quality and risk of the input data.

## Human review principle

The system must not automatically approve circular routes for hazardous, unknown or highly contaminated streams. These receive human review flags and zero assumed diversion until a competent review confirms a safe route.

## Limitation

Milestone 3 does not include carbon accounting, legal waste classification, supplier verification or AI-generated reasoning. Those require stronger evidence and should be handled in later milestones.
