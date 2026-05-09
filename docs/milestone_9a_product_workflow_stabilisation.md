# Milestone 9A: Product-Grade Workflow Stabilisation

## Purpose

Milestone 9A starts the Alpha hardening phase.

The goal is not to add another shiny feature. The goal is to prove the existing product workflow works reliably from data load to final report.

## New backend endpoint

```text
GET /api/diagnostics/workflow-readiness
```

This endpoint reports whether the current local workflow has the required data and locked outputs for a full product demo/use cycle.

It checks:

- backend health
- dataset loaded
- locked rules-engine recommendations generated
- evidence register available
- supplier-loop intelligence available
- AI-assisted outputs can operate from locked outputs
- fallback mode remains available

## New smoke test

```text
backend/tests/test_product_workflow_smoke.py
```

This test runs the core local product workflow with AI disabled:

```text
load sample data
run recommendations
evidence summary
supplier-loop summary
site-wide copilot fallback
evidence gap explainer fallback
supplier email draft fallback
circular action report fallback
workflow readiness diagnostic
```

## New verification script

```text
scripts/verify_local_product_workflow.ps1
```

Run this while the backend is already running to smoke-test the API as a local product workflow.

## Alpha exit logic

Circular Industry AI should not leave Alpha until:

- backend tests pass
- frontend build passes
- workflow readiness is true
- full local verification script passes
- no hidden dependency on live LLM keys exists
- fallback mode works
- outputs preserve claim-safety boundaries

## Governance boundary

The readiness check is deterministic. It does not verify legal compliance, supplier capability, carbon savings, financial savings or completed operational impact.
