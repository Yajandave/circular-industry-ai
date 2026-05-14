# Milestone 17F — Mapping Panel Role Options and Copy Cleanup

## Purpose
Clean up the user-confirmed mapping panel before flexible import work begins.

This milestone fixes frontend role-option mismatch, stale copy, reset controls and repeated governance text. It does not implement import, saved mapping plans, persistence or audit records.

## Why This Matters
Manual smoke testing after 17E showed the core validation flow works, but also exposed a trust issue:

```text
STREAM ID
Target role: Unmapped / unresolved
User Confirmed
```

That happened because the backend can suggest `stream_id`, but the frontend role dropdown did not include `stream_id`.

Before import logic depends on mappings, the frontend must display the backend role contract accurately.

## Scope
This milestone adds:
- frontend role options aligned with backend Data Profiler roles
- `stream_id` and other missing backend roles in the dropdown
- per-row reset-to-suggestion control
- restore-all-suggestions control
- updated detected-column wording
- updated profiler status wording
- reduced duplicate governance copy after backend validation

## Expected Files Changed
- `frontend/src/components/DataProfilerPanel.jsx`
- `docs/foundation/milestone_17f_mapping_panel_role_options_copy_cleanup.md`

## Behaviour
The mapping panel should:
- display `Stream ID` as a selectable/visible role
- avoid showing `Unmapped / unresolved` with `User Confirmed` for backend-suggested roles
- allow the operator to undo accidental changes
- allow all suggestions to be restored
- avoid stale “next milestone” copy
- avoid repeated governance paragraphs after validation

## Non-Goals
This milestone does not:
- import mapped rows
- save mapping plans
- persist mapping decisions
- create audit records
- change backend validation rules
- change Data Profiler role scoring

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
- profile the UTF-8 Circular Core test CSV
- click Accept high-confidence suggestions
- confirm Stream ID displays as Stream ID, not Unmapped
- validate mapping
- confirm backend result is Ready
