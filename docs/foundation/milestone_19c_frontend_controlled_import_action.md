# Milestone 19C — Frontend Controlled Import Action

## Purpose

Add the frontend action that lets an operator explicitly approve and save reviewed Circular Core draft rows to SQLite.

This connects the 18D/18E draft import preview panel to the 19A/19B backend persistence and audit endpoint.

## Why This Matters

Milestone 19A added a controlled backend import endpoint.

Milestone 19B added claim-safe audit traceability.

Milestone 19C adds the operator-facing frontend action while keeping the same controls:

- preview first
- review warnings and blocking errors
- explicit operator approval
- save rows only
- create audit traceability
- do not run recommendations
- do not verify claims

## Scope

This milestone adds:

- `api.importCircularCoreDraft(payload)` in the frontend API client
- a controlled import approval gate in the draft import preview panel
- an optional approval note field
- a "Save approved draft rows" action
- success response display showing rows imported and audit event ID
- claim-safe messaging that recommendations were not run
- frontend styles for the controlled import panel

## Expected Files Changed

- `frontend/src/api/client.js`
- `frontend/src/components/DataProfilerPanel.jsx`
- `frontend/src/styles.css`
- `docs/foundation/milestone_19c_frontend_controlled_import_action.md`

## Behaviour

The frontend should:

- call `POST /api/data-profiler/import-circular-core-draft`
- require the operator approval checkbox before enabling the save action
- pass the current draft import report to the backend
- pass `operator_approval: true`
- pass optional approval note text
- display rows imported
- display audit event ID when returned
- state that recommendations were cleared but not run
- keep blocked reports locked

## Important Boundary

This milestone allows frontend-controlled persistence only.

It does not:

- run recommendations
- create recommendation records
- verify cost savings
- verify waste diversion
- verify supplier compliance
- verify carbon reduction
- verify environmental benefit
- add rollback controls
- save reusable mapping plans

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
- accept required Circular Core mappings
- validate mapping
- build draft preview
- review row warnings
- tick the approval checkbox
- save approved draft rows
- confirm the response shows rows imported and audit event ID
- confirm no wording implies recommendations were run or claims were verified
