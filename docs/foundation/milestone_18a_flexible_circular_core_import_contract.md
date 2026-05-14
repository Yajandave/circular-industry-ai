# Milestone 18A — Flexible Circular Core Import Contract

## Purpose
Add a backend-first contract for transforming user-confirmed mapped CSV rows into Circular Core-compatible draft rows.

This milestone does not save rows to the database, does not run recommendations, does not create audit records, and does not claim verified savings/diversion.

## Why This Matters
The Data Profiler can now:
- detect column roles
- route a file to Circular Core
- let an operator confirm mappings
- validate that Material, Quantity and Current Route are confirmed

The next safe step is to define what happens after a mapping is ready: source rows can be transformed into draft Circular Core rows for review.

## Scope
This milestone adds:
- flexible import request/response schemas
- a pure backend transformation service
- tests for ready, blocked, generated IDs, unit conversion and row warnings

## Expected Files Changed
- `backend/app/schemas.py`
- `backend/app/flexible_circular_import.py`
- `backend/tests/test_flexible_circular_import.py`
- `docs/foundation/milestone_18a_flexible_circular_core_import_contract.md`

## Behaviour
The service should:
- validate mappings using the existing 17A validation service
- block transformation if required roles are unresolved
- transform only confirmed source columns
- generate draft stream IDs when none are mapped
- convert common quantity units into kilograms where possible
- add row-level warnings for missing/invalid optional values
- mark outputs as draft rows only

## Governance Boundary
Draft rows are not verified operational data.

This milestone must not claim:
- verified savings
- verified diversion
- verified carbon reduction
- supplier compliance
- legal compliance
- externally validated sustainability claims

## Non-Goals
This milestone does not:
- add an API endpoint
- import into the SQLite stream table
- overwrite existing streams
- trigger Circular Core recommendations
- save mapping plans
- create audit events
- add frontend import buttons

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
