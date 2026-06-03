# Milestone 18D — Draft Import Preview Panel

## Purpose

Add a controlled frontend preview panel for Circular Core draft imports.

This milestone lets the operator build a preview report from the selected CSV and the user-confirmed mapping after backend mapping validation.

## Why This Matters

Milestone 18B exposed the backend draft-import endpoint.

Milestone 18C added the shared frontend API client for that endpoint.

Milestone 18D connects the validated mapping workflow to a visible operator review panel. It allows the user to see draft Circular Core rows, row-level warnings and blocking errors before any future import or persistence feature is added.

## Scope

This milestone adds:

- a browser-side CSV row reader for the selected file
- a draft import preview action after mapping validation
- a controlled preview panel for ready, ready-with-warnings and blocked reports
- summary cards for source rows, draft rows, row warnings and blocking errors
- a small preview table for generated draft rows
- row warning and blocking error lists
- claim-safe boundary wording

## Expected Files Changed

- `frontend/src/components/DataProfilerPanel.jsx`
- `frontend/src/styles.css`
- `docs/foundation/milestone_18d_draft_import_preview_panel.md`

## Behaviour

The frontend should:

- keep the selected CSV file available after profiling
- allow the operator to validate mappings first
- call `api.buildCircularCoreDraftImport(payload)` after validation
- build the payload using:
  - the current user-confirmed mapping
  - source rows parsed from the selected CSV
- show the returned draft-import report
- treat blocked reports as controlled validation outcomes, not frontend failures
- display row warnings and blocking errors clearly

## Important Boundary

This milestone only builds a preview.

It does not save rows to SQLite, overwrite stream records, run Circular Core recommendations, create audit records, save mapping plans or verify any environmental/commercial claims.

Draft rows are for operator review only.

## Non-Goals

This milestone does not:

- add database import behaviour
- persist draft rows
- create audit events
- run recommendation execution
- save reusable mapping plans
- create rollback controls
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
- confirm the UI shows draft rows or a controlled blocked report
- confirm no wording implies saved data or verified claims
