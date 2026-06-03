# Milestone 18E — Draft Import UX Hardening and Review Controls

## Purpose

Harden the Milestone 18D draft import preview workflow before any future database import feature is added.

This milestone improves operator clarity around ready, warning and blocked draft-import states.

## Why This Matters

Milestone 18D introduced the draft import preview panel. It allowed the operator to build draft Circular Core rows from the selected CSV and user-confirmed mapping.

Milestone 18E makes that preview safer and more decision-useful by adding stronger review-state guidance, issue grouping, selected-row inspection and explicitly disabled future-import controls.

## Scope

This milestone adds:

- operator guidance for `ready`, `ready_with_warnings` and `blocked` preview states
- grouped row warning and blocking-error summaries
- selected draft-row inspection
- row-specific warning display
- disabled future-import controls to show what remains intentionally locked
- clearer boundary wording before persistence is designed

## Expected Files Changed

- `frontend/src/components/DataProfilerPanel.jsx`
- `frontend/src/styles.css`
- `docs/foundation/milestone_18e_draft_import_ux_hardening_and_review_controls.md`

## Behaviour

The frontend should:

- keep draft import preview as review-only
- display a clear operator review state after preview generation
- separate warnings from blocking errors
- group issues by issue code
- allow an operator to inspect individual preview rows
- show row-specific warnings for the selected draft row
- show future import actions as disabled placeholders only

## Important Boundary

This milestone does not import anything.

It does not save rows to SQLite, overwrite stream records, run Circular Core recommendations, create audit events, save mapping plans or verify claims.

The disabled future-import controls are intentionally non-functional and exist only to communicate the next controlled workflow boundary.

## Non-Goals

This milestone does not:

- add a real import button
- persist draft rows
- create audit records
- save reusable mapping plans
- run the rules engine on preview rows
- add rollback controls
- verify savings, diversion, supplier compliance, carbon reduction or environmental benefit

## Acceptance Criteria

Run from `frontend`:

```powershell
npm.cmd run build
```

Expected:

- frontend build passes

Run from `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected:

- backend tests pass

Manual check:

- profile a CSV
- accept the required Circular Core mappings
- validate mapping
- build draft preview
- confirm ready, warning or blocked guidance appears
- confirm issue groups are shown
- confirm a draft row can be inspected
- confirm future import controls are disabled
