# Milestone 11E v4: Professional Operator Master-Detail Layout

## Purpose

This replaces the failed table/card experiments with a professional operator layout.

## Design

The UI now follows a layered dashboard pattern:

1. Overview summaries
2. Compact triage list
3. Selected-record detail inspector
4. Export for full structured registers

## Changes

### Workflow navigation

The workflow navigation is compact and does not show long helper text inside every tab.

### Recommendations

The wide table is replaced by:

- compact recommendation list
- selected recommendation inspector
- review pack action in the inspector

### Evidence register

The wide table/card grid is replaced by:

- compact evidence list
- selected evidence inspector
- explain evidence gap action in the inspector

### AI runtime

Runtime status is operator-facing. Provider/model/timeout details are inside diagnostics.

## Governance boundary

No backend logic changes. No rules-engine changes. No evidence scoring changes.
