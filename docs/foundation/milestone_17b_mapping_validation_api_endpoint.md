# Milestone 17B — Mapping Validation API Endpoint

## Purpose
Expose the Milestone 17A user-confirmed mapping validator through a backend API endpoint.

This is still backend-first. It does not implement the frontend mapping screen, flexible import, persistence, or saved mapping plans.

## Why This Matters
The product now has deterministic backend logic for checking whether a user-confirmed mapping set is structurally ready. The next step is to make that validation reachable through the API so future UI and import workflows can use it.

## Scope
This milestone adds:
- `POST /api/data-profiler/validate-mapping`
- endpoint tests for ready, blocked and unknown-workspace cases
- documentation for the backend contract

## Expected Files Changed
- `backend/app/routers/data_profiler.py`
- `backend/tests/test_mapping_validation_endpoint.py`
- `docs/foundation/milestone_17b_mapping_validation_api_endpoint.md`

## Behaviour
The endpoint should:
- accept a confirmed mapping validation payload
- call the 17A validator
- return a structured validation report
- return blocked status as a normal 200 response when mappings are invalid for import-readiness
- return 400 for invalid target workspace or malformed validation logic errors

## Important Boundary
A blocked mapping is not an API error.

A blocked mapping is a valid validation result telling the operator that the data is not ready for import.

## Non-Goals
This milestone does not:
- create a frontend screen
- import mapped rows
- save mapping plans
- create audit records
- add authentication
- persist validation results
- change Data Profiler profiling output

## Acceptance Criteria
Run from `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected:
- all backend tests pass

Run from `frontend`:

```powershell
npm.cmd run build
```

Expected:
- frontend build passes
