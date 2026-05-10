# Milestone 9D: Data Model Foundation

## Purpose

Milestone 9D starts moving Circular Industry AI from a single local dataset prototype toward a product-grade business data model.

It does **not** rewrite the current stream/recommendation workflow. Instead, it adds a safe metadata layer around the current workflow.

## New metadata objects

```text
Organisation
Site
AnalysisRun
```

These form the future product structure:

```text
Organisation
  -> Site
    -> AnalysisRun
      -> Material streams
      -> Recommendations
      -> Evidence records
      -> Supplier actions
      -> Reports
```

## New endpoints

```text
GET /api/workspace/context
POST /api/workspace/analysis-runs/snapshot
GET /api/workspace/analysis-runs
```

## Why this is safe

The existing Alpha workflow remains intact:

```text
industrial_streams
circular_recommendations
```

The new metadata layer does not yet force stream IDs or recommendation IDs to become project/site scoped. That deeper migration should happen later after the product workflow is stable.

## Product value

This milestone creates the foundation for:

- organisations
- sites
- analysis runs
- saved review cycles
- future audit trails
- future multi-site workflows
- future user/role permissions

## Governance boundary

Analysis-run metadata is a snapshot of current workflow outputs. It does not verify legal compliance, supplier capability, carbon savings, financial savings or completed operational impact.
