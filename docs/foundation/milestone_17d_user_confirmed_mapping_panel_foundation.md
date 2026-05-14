# Milestone 17D — User-Confirmed Mapping Panel Foundation

## Purpose
Add the first frontend user-confirmed mapping panel inside the Data Profiler workflow.

This milestone uses the 17B backend validation endpoint through the 17C frontend API client, but it does not import data, persist mapping plans, or create audit records.

## Why This Matters
The Data Profiler can suggest mappings, but suggested mappings are not verified or import-ready by default.

This milestone introduces the operator checkpoint:
- review system suggestions
- accept or adjust target roles
- mark columns as ignored
- validate required role coverage
- show blocked, ready, or ready-with-warnings status

## Scope
This milestone adds:
- frontend mapping draft state
- mapping rows based on profiler columns
- accept/ignore controls
- role selection for target roles
- call to `api.validateMapping(payload)`
- validation result display
- claim-safe governance wording

## Expected Files Changed
- `frontend/src/components/DataProfilerPanel.jsx`
- `frontend/src/styles.css`
- `docs/foundation/milestone_17d_user_confirmed_mapping_panel_foundation.md`

## Behaviour
The panel should:
- appear after a CSV has been profiled
- start with system suggestions as unconfirmed
- require explicit user acceptance before validation considers a role confirmed
- show backend validation result
- treat blocked mappings as valid validation outcomes, not UI errors
- avoid implying source-data verification

## Non-Goals
This milestone does not:
- import mapped rows
- save mapping plans
- create audit records
- persist mapping decisions
- implement flexible Circular Core import
- create multi-user approval workflows

## Acceptance Criteria
Run from `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected:
- backend tests pass

Run from `frontend`:

```powershell
npm.cmd run build
```

Expected:
- frontend build passes

Manual smoke test:
- profile a CSV
- accept suggested mappings for Material, Quantity and Current Route
- validate mapping
- see ready / blocked / ready-with-warnings response
