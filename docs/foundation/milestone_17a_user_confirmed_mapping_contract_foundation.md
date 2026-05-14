# Milestone 17A — User-Confirmed Mapping Contract Foundation

## Purpose
Introduce the backend contract and validation service for user-confirmed CSV mappings.

This is the first implementation step after the Data Profiler stabilisation sequence.

## Why This Matters
The Data Profiler can suggest semantic roles, but system inference must not be treated as verified input.

Before building a mapping UI or flexible import endpoint, the backend needs a deterministic contract for validating user-confirmed mappings.

## Scope
This milestone adds:
- mapping request/response schemas
- a backend mapping validation service
- focused tests for confirmed mapping behaviour

## Expected Files Changed
- `backend/app/schemas.py`
- `backend/app/mapping_validation.py`
- `backend/tests/test_mapping_validation.py`
- `docs/foundation/milestone_17a_user_confirmed_mapping_contract_foundation.md`

## Behaviour
The validation service should:
- check required roles for a target workspace
- distinguish confirmed mappings from system suggestions
- block import-readiness when required roles are unresolved
- flag duplicate target-role mappings
- warn on low-confidence user-confirmed mappings
- preserve claim/evidence governance boundaries

## Current Target
The first target workspace is `circular-core`, because Circular Core remains the main product.

The contract should also be structured so later work can extend it to other workspaces.

## Non-Goals
This milestone does not:
- add a frontend mapping screen
- add a mapping API endpoint
- persist mapping plans
- import data into Circular Core
- create audit records
- change Data Profiler output
- change recommendation logic

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

Manual review:
- mapping validation is deterministic
- required-role blocking is explicit
- user confirmation is separated from system suggestion
- no verified-impact claims are introduced
