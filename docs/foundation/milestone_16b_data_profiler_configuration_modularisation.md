# Milestone 16B — Data Profiler Configuration Modularisation

## Purpose
Reduce `backend/app/data_profiler.py` responsibility by moving static profiler configuration into a dedicated module.

This is a stabilisation/refactor milestone. It should not change Data Profiler behaviour.

## Why This Matters
After 16A, the Data Profiler has stronger edge-case coverage. The next safe step is to reduce file complexity before adding mapping/import runtime features.

The current profiler file contains:
- static governance wording
- role aliases
- role labels
- value hints
- workspace routing rules
- parsing/type inference helpers
- role scoring logic
- workspace scoring logic
- CSV profiling orchestration

That is too much responsibility for one file if the product is moving toward reliable import, mapping confirmation, saved mapping plans, and auditability.

## Scope
This milestone extracts static configuration into:

```text
backend/app/data_profiler_config.py
```

The main profiler keeps the profiling logic and public function:

```text
profile_csv_bytes(...)
```

## Expected Files Changed
- `backend/app/data_profiler.py`
- `backend/app/data_profiler_config.py`
- `docs/foundation/milestone_16b_data_profiler_configuration_modularisation.md`

## Behaviour Boundary
This milestone should not change:
- API responses
- role names
- role labels
- workspace IDs
- workspace scoring behaviour
- governance wording
- test expectations
- frontend behaviour

## Non-Goals
This milestone does not:
- split every helper function
- redesign confidence scoring
- implement mapping UI
- implement flexible import
- add saved mapping plans
- change API contracts

## Acceptance Criteria
Run from `backend`:

```powershell
python -m pytest
```

Expected:
- all backend tests pass

Run from `frontend`:

```powershell
npm run build
```

Expected:
- frontend build passes

Manual review:
- `data_profiler.py` is smaller
- static config is isolated
- public profiler behaviour remains unchanged
