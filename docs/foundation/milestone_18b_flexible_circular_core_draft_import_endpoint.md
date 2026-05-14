# Milestone 18B — Flexible Circular Core Draft Import API Endpoint

## Purpose
Expose the Milestone 18A flexible Circular Core import contract through a backend API endpoint.

This endpoint builds draft Circular Core rows from user-confirmed mappings and source rows. It does not persist data, run recommendations, create audit records or verify claims.

## Why This Matters
18A added the pure transformation service. 18B makes that service reachable by the frontend or future workflow layers without yet allowing database import.

## Scope
This milestone adds:
- `POST /api/data-profiler/build-circular-core-draft-import`
- endpoint tests for ready and blocked draft import reports
- documentation for the endpoint boundary

## Expected Files Changed
- `backend/app/routers/data_profiler.py`
- `backend/tests/test_flexible_circular_import_endpoint.py`
- `docs/foundation/milestone_18b_flexible_circular_core_draft_import_endpoint.md`

## Behaviour
The endpoint should:
- accept a flexible Circular Core import request
- call the 18A transformation service
- return draft rows and row warnings
- return blocked reports as valid 200 responses when mapping validation blocks draft import
- return 400 only for malformed/unexpected processing errors

## Important Boundary
A blocked draft import is not an API failure.

It is a controlled validation outcome that tells the operator the mapping or source rows are not ready for draft transformation.

## Non-Goals
This milestone does not:
- save rows to SQLite
- overwrite existing stream records
- run Circular Core recommendations
- create audit events
- save mapping plans
- add frontend import UI
- verify savings, diversion, supplier compliance or environmental benefit

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
