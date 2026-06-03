# Milestone 19A — Controlled SQLite Draft Import Endpoint

## Purpose

Add a backend-only endpoint that saves operator-approved Circular Core draft rows into SQLite.

This is the first controlled persistence milestone after the flexible draft import preview workflow.

## Why This Matters

Milestones 18A–18E created a safe path from flexible CSV profiling to draft row review:

- 18A created the flexible Circular Core import contract
- 18B exposed the backend draft import endpoint
- 18C added the frontend API client
- 18D added the draft preview panel
- 18E hardened the preview review controls

Milestone 19A adds the first persistence step, but only after explicit operator approval.

## Endpoint

```text
POST /api/data-profiler/import-circular-core-draft
```

## Scope

This milestone adds:

- backend request/response schemas for controlled draft persistence
- backend persistence service for approved draft rows
- endpoint wiring in the data profiler router
- tests for successful import and blocked import safeguards
- documentation for the persistence boundary

## Behaviour

The endpoint should:

- require explicit `operator_approval`
- reject blocked draft import reports
- reject reports with blocking errors
- reject empty draft reports
- reject duplicate `stream_id` values
- persist approved draft rows as `IndustrialStream` records
- replace existing stream rows using the existing controlled replacement pattern
- clear old recommendations to avoid stale recommendations linked to replaced streams
- return imported stream IDs and governance wording

## Important Boundary

This milestone saves approved draft rows to SQLite only.

It does not:

- run Circular Core recommendations
- create new recommendations
- create audit events
- add a frontend import button
- save reusable mapping plans
- add rollback controls
- verify savings, diversion, supplier compliance, carbon reduction or environmental benefit

## Why recommendations are cleared

Existing recommendations may refer to stream rows that are replaced during import. 19A clears previous recommendations as a data-integrity safeguard but does not run the recommendation engine.

A later milestone should add the controlled action for running recommendations against newly imported rows.

## Expected Files Changed

- `backend/app/schemas.py`
- `backend/app/routers/data_profiler.py`
- `backend/app/draft_import_persistence.py`
- `backend/tests/test_draft_import_persistence_endpoint.py`
- `docs/foundation/milestone_19a_controlled_sqlite_draft_import_endpoint.md`

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

- frontend build still passes

Manual API check:

- build a draft import preview
- send the preview report with `operator_approval: true`
- confirm rows appear in `/api/streams`
- confirm no recommendations are run
- confirm blocked reports are rejected
