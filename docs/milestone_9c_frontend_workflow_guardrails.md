# Milestone 9C: Frontend Workflow Guardrails

## Purpose

Milestone 9C hardens the React interface so the product behaves more like business software and less like a fragile prototype.

The goal is to prevent confusing workflows when users click tabs before the required data exists.

## Key changes

- Adds workflow prerequisite notices
- Disables downstream workflow tabs until data/recommendations exist
- Adds AI runtime visibility in the frontend
- Fixes missing `circularActionReport` frontend state
- Clears stale AI/report outputs when recommendations are rerun
- Improves user guidance when the workflow is not ready

## Guardrail logic

Tabs that need only loaded data:

```text
Recommendations
Raw data
```

Tabs that need locked recommendations:

```text
AI Copilot
AI reasoning
Resolution plans
Material playbooks
Supplier loops
Review pack
Action plan
Evidence register
Action report
```

## Product value

This milestone reduces fragile demo behaviour and improves user trust.

A business-grade product cannot assume the user will click everything in the perfect order.
