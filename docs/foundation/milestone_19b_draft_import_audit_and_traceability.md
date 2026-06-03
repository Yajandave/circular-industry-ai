# Milestone 19B — Draft Import Audit and Traceability

## Purpose

Add traceability to the controlled SQLite draft import endpoint.

Milestone 19A saved operator-approved draft rows into SQLite. Milestone 19B records a claim-safe audit event when that controlled import action happens.

## Why This Matters

Once draft rows can be persisted, the workflow needs an evidence trail showing:

- who/what triggered the import
- how many rows were imported
- which stream IDs were imported
- whether warnings were present
- whether blocking errors were absent
- whether recommendations were cleared
- whether recommendations were run

This keeps the product aligned with auditability and claim-safe sustainability reporting.

## Scope

This milestone adds:

- audit event creation after successful controlled draft import
- audit metadata for rows imported, source rows, warning counts and imported stream IDs
- response fields confirming that an audit event was created
- tests for audit event creation and audit summary visibility
- documentation for the traceability boundary

## Expected Files Changed

- `backend/app/schemas.py`
- `backend/app/draft_import_persistence.py`
- `backend/tests/test_draft_import_audit_traceability.py`
- `docs/foundation/milestone_19b_draft_import_audit_and_traceability.md`

## Behaviour

After a successful `POST /api/data-profiler/import-circular-core-draft`, the backend should create an audit event with:

- `event_type`: `draft_import_committed`
- `entity_type`: `circular_core_import`
- `action`: `commit_approved_draft_rows`
- `decision_source`: `operator_approved_draft_import`
- claim-safe boundary wording
- metadata including:
  - rows imported
  - source row count
  - draft row count
  - import status
  - row warning count
  - blocking error count
  - warning code breakdown
  - imported stream IDs
  - recommendations cleared
  - recommendations run = false

## Important Boundary

The audit event records the controlled workflow action only.

It does not verify:

- legal compliance
- supplier capability
- cost savings
- carbon reduction
- waste diversion
- circular economy impact
- environmental benefit

## Non-Goals

This milestone does not:

- add a frontend import button
- add rollback controls
- run recommendations
- create recommendation records
- save reusable mapping plans
- verify claims
- create evidence documents

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

- import an approved draft report
- call `/api/audit/events?event_type=draft_import_committed`
- confirm the audit event records imported row count and stream IDs
- confirm the audit boundary does not imply verified savings, diversion or environmental benefit
