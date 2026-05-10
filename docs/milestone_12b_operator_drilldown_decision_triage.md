# Milestone 12B: Operator Drilldown and Decision Triage Layer

## Product context

Circular Industry AI is an industry / market / professional-grade circular economy, ESG, EIA and sustainability intelligence dashboard.

It converts raw operational data into rules-locked circular recommendations, evidence controls, supplier-loop actions, risk signals, claim-readiness checks, agentic insight workflows and operator-facing analytics.

## Purpose

Milestone 12A added decision-useful visuals.

Milestone 12B makes those visuals actionable by adding an operator drilldown layer.

The workflow is:

```text
Visual signal -> click/select -> filtered record list -> selected record inspector -> review pack action
```

## Added capability

12B adds interactive drilldown for:

- risk vs opportunity matrix cells
- material quantity Pareto rows
- cost exposure Pareto rows
- evidence maturity groups
- claim-readiness groups
- supplier-loop opportunity groups
- scenario screening candidates

## Drilldown data model

The visual analytics data now includes `drilldownRecords`.

Each drilldown record includes:

- stream ID
- stream name
- material
- department
- supplier
- risk level
- priority band
- priority score
- evidence quality score
- confidence score
- human-review requirement
- screened cost exposure
- screened diversion potential
- recommended circular action
- next action
- opportunity bucket
- evidence bucket
- claim bucket
- supplier bucket

## Operator drilldown UI

The new drilldown panel includes:

- selected slice title
- matching record count
- sort selector
- compact record list
- selected record inspector
- review pack action

The inspector shows:

- locked risk level
- human-review status
- evidence quality
- confidence score
- screened cost exposure
- screened diversion
- recommended circular action
- next action
- bucket classifications
- governance note

## UX rules

12B follows the 11E and 12A interface lessons:

- no wide tables
- no whole-page horizontal scroll
- no cramped all-fields cards
- compact list plus selected detail inspector
- visual analytics first, detailed decision evidence second

## Governance boundary

The drilldown layer is operator triage only.

It does not override:

- locked risk level
- review status
- rule applied
- claim boundary
- evidence controls
- legal/compliance status
- verified impact

The rules engine remains the locked decision source.
