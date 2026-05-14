# Milestone 17E — Mapping Validation UX Hardening

## Purpose
Harden the user-confirmed mapping panel before flexible import work begins.

This milestone improves operator guidance and error-prevention in the Data Profiler mapping workflow. It does not implement import, saved mapping plans, persistence, or audit records.

## Why This Matters
17D introduced the first mapping confirmation panel. Before import logic depends on it, the UI should make required roles, duplicate mappings and confirmation boundaries harder to miss.

## Scope
This milestone adds:
- required-role checklist for Circular Core mapping readiness
- local duplicate confirmed-role warnings before backend validation
- local missing required-role guidance before backend validation
- “accept all high-confidence suggestions” action
- clearer governance wording that validated mapping is not verified source data
- stronger blocked/ready explanation in the validation result panel

## Expected Files Changed
- `frontend/src/components/DataProfilerPanel.jsx`
- `frontend/src/styles.css`
- `docs/foundation/milestone_17e_mapping_validation_ux_hardening.md`

## Behaviour
The panel should help the operator understand:
- which Circular Core required roles are confirmed
- which required roles are still missing
- when multiple confirmed columns target the same role
- that backend validation checks mapping readiness only
- that import remains unavailable until a later milestone

## Non-Goals
This milestone does not:
- import mapped rows
- create saved mapping plans
- persist mapping decisions
- create audit records
- add authentication
- change backend validation rules
- change Data Profiler profiling logic

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
- use “accept all high-confidence suggestions”
- check required-role checklist
- validate mapping
- confirm blocked mappings show as validation outcomes, not UI crashes
