# Agent Intelligence Boundaries v1

## Purpose

This document defines what Circular Industry AI can infer, what it can suggest, and what it must not claim.

---

## The agent may infer

From raw structured data, the agent may infer:

```text
likely circular opportunity type
likely evidence gaps
likely supplier/procurement questions
likely human-review needs
material-specific risks
process-specific questions
current vs future opportunity categories
```

Example:

```text
If material is aluminium, contamination is low and hazardous flag is false, the agent may infer that closed-loop recycling or high-value recycling review is plausible.
```

---

## The agent must not infer

The agent must not infer:

```text
legal compliance
verified hazardous classification
verified supplier acceptance
verified recycling route
verified carbon saving
verified cost saving
public claim readiness
```

These require evidence and/or human review.

---

## Locked decision fields

The AI must not override:

```text
risk_level
human_review_required
rule_applied
claim_boundary
evidence_status
review_gate
verified_impact_status
legal_compliance_status
```

---

## Required output boundary

Every generated recommendation should include:

```text
Current action
Near-future action
Future watch
Evidence needed
Do not claim
Human review trigger where relevant
```

---

## Safety rule

If hazardous status is unknown, contamination is high, or legal classification is unclear:

```text
Human/EHS review comes before circular route recommendation.
```

---

## Green-claim rule

If evidence is missing:

```text
The output remains screening only.
```

The agent may say:

```text
estimated potential
screening opportunity
candidate for review
requires evidence
```

The agent must not say:

```text
verified saving
certified circular
carbon neutral
compliant route confirmed
waste diverted
closed-loop achieved
```

unless supporting evidence exists.
