# Milestone 13A: Domain Workspace Architecture

## Purpose

This milestone establishes a cleaner professional product architecture for Circular Industry AI.

Circular Industry AI keeps its main identity as:

**Industrial Circular Economy Decision Support**

The system now has top-level domain workspaces so ESG, GHG, EIA, claims, supplier and generic CSV workflows do not get forced into the industrial material-stream upload path.

## Why this matters

A single universal upload point creates confusion because ESG score files, EIA issue registers and GHG emissions files do not contain the fields needed for circular material-flow rules.

The new approach is:

```text
Circular Core = main industrial circular economy workflow
Other domains = supporting professional intelligence workspaces
```

## Workspaces introduced

- Circular Core
- ESG
- GHG & Net Zero
- EIA / Environmental Impact Assessment
- Greenwashing / Claims
- Supplier & Procurement
- Data Profiler

## Governance boundary

This is a frontend architecture milestone.

It does not change:

- backend rules engine
- database models
- API contracts
- LLM authority
- risk level logic
- review status logic
- evidence controls
- claim boundaries
- verified impact handling

## Product boundary

The domain workspaces support industrial circular economy decision-making. They do not replace the Circular Core.

Full rules-locked circular recommendations remain available only for compatible industrial material-flow, waste/resource stream and circular procurement datasets.

## Next milestones

- 13B ESG and GHG domain parsers
- 13C EIA domain intelligence
- 13D Greenwashing and claims evidence checker
- 13E Supplier and procurement workspace intelligence
- 13F Universal data profiler fallback
