# Milestone 16C — Data Profiler Type-Inference Modularisation

## Purpose
Reduce `backend/app/data_profiler.py` responsibility further by moving sample extraction and type-inference helpers into a dedicated module.

This is a behaviour-preserving stabilisation/refactor milestone.

## Why This Matters
After 16A added edge-case coverage and 16B extracted static configuration, the next safe refactor is to isolate parsing/type inference.

The Data Profiler is becoming an ingestion foundation. Type inference is important enough to be isolated because future work will need to handle:
- numeric parsing
- date-like fields
- unit hints
- empty columns
- text/categorical distinction
- warning-safe parsing behaviour

Keeping this logic separate makes later edge-case hardening safer.

## Scope
This milestone adds:

```text
backend/app/data_profiler_type_inference.py
```

The new module owns:
- sample value extraction
- deterministic date-like parsing checks
- column type inference

`data_profiler.py` continues to own:
- role scoring
- column profiling
- workspace routing
- CSV profiling orchestration

## Expected Files Changed
- `backend/app/data_profiler.py`
- `backend/app/data_profiler_type_inference.py`
- `backend/tests/test_data_profiler_type_inference.py`
- `docs/foundation/milestone_16c_data_profiler_type_inference_modularisation.md`

## Behaviour Boundary
This milestone should not change:
- profiler API response shape
- workspace routing
- confidence scoring
- governance wording
- frontend behaviour
- existing test expectations

## Non-Goals
This milestone does not:
- change scoring thresholds
- implement mapping UI
- implement flexible import
- implement saved mapping plans
- redesign parsing rules
- add new frontend behaviour

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
- type inference logic is isolated
- profiler behaviour remains unchanged
