# Milestone 18C — Frontend API Client for Circular Core Draft Import

## Purpose

Add a frontend API client function for the Milestone 18B Circular Core draft import endpoint.

This milestone connects the frontend API layer to the backend draft-import endpoint without adding a user-facing import interface.

## Why This Matters

Milestone 18B exposed the backend endpoint:

```text
POST /api/data-profiler/build-circular-core-draft-import
```

That endpoint builds draft Circular Core rows from user-confirmed mappings and source rows.

Milestone 18C makes the endpoint available through the shared frontend API client so future UI layers can call it without duplicating fetch logic inside components.

## Scope

This milestone adds:

- `api.buildCircularCoreDraftImport(payload)`
- JSON request handling consistent with `api.validateMapping(payload)`
- documentation for the frontend API-client boundary

## Expected Files Changed

- `frontend/src/api/client.js`
- `docs/foundation/milestone_18c_frontend_api_client_for_circular_core_draft_import.md`

## Behaviour

The frontend API client should:

- send a JSON `POST` request to `/api/data-profiler/build-circular-core-draft-import`
- accept a prepared draft-import payload
- return the backend draft-import report
- reuse the existing shared request helper
- avoid component-level fetch duplication

## Important Boundary

This milestone only adds the API client function.

It does not add a user-facing draft import UI.

The backend endpoint remains draft-only. It does not persist rows, run recommendations, create audit records or verify claims.

## Non-Goals

This milestone does not:

- create a frontend import review panel
- save rows to SQLite
- overwrite existing stream records
- run Circular Core recommendations
- create audit events
- save mapping plans
- add database import behaviour
- verify savings, diversion, supplier compliance or environmental benefit

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
