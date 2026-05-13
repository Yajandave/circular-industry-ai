# Milestone 16A — Data Profiler Edge-Case Test Expansion

## Purpose
Strengthen the Data Profiler baseline before building mapping/import runtime features.

This milestone moves from foundation planning into stabilisation implementation.

## Why This Matters
The backend baseline passed, but pytest surfaced repeated warnings from `data_profiler.py` date detection:

```text
Could not infer format, so each element will be parsed individually, falling back to dateutil.
```

For a serious industrial circular economy decision-support product, ingestion warnings should not be ignored. Date-like fields can be ambiguous, especially where UK and US formats may be confused.

## Scope
This milestone adds:
- deterministic date-type detection helper
- edge-case tests for CSV profiler behaviour
- regression coverage for warning-free date detection
- clearer protection around empty/header-only/duplicate-row cases

## Files Changed
Expected runtime/test files:
- `backend/app/data_profiler.py`
- `backend/tests/test_data_profiler.py`

Expected documentation file:
- `docs/foundation/milestone_16a_data_profiler_edge_case_test_expansion.md`

## Intended Behaviour
The profiler should:
- avoid unformatted `pd.to_datetime(...)` inference warnings
- identify clearly date-like columns using deterministic parsing checks
- avoid classifying mixed operational text as dates
- reject empty uploads clearly
- handle header-only CSVs without crashing
- report duplicate rows consistently

## Non-Goals
This milestone does not implement:
- mapping UI
- flexible import endpoint
- saved mapping plans
- profiler modularisation
- production auth
- full CSV parser redesign

## Acceptance Criteria
Run from `backend`:

```powershell
python -m pytest
```

Expected:
- all backend tests pass
- previous profiler date parsing warnings should be removed or materially reduced

Then run from `frontend`:

```powershell
npm run build
```

Expected:
- frontend build passes
