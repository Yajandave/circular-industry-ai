# Milestone 16D — Data Profiler Role-Scoring Modularisation

## Purpose
Reduce `backend/app/data_profiler.py` responsibility by moving role-scoring and semantic candidate logic into a dedicated module.

This is a behaviour-preserving stabilisation/refactor milestone.

## Why This Matters
After:
- 16A added profiler edge-case tests
- 16B extracted static profiler configuration
- 16C extracted type inference

the remaining profiler file still contains semantic role-scoring logic. That logic is important enough to isolate before building confirmed mapping and flexible import runtime features.

## Scope
This milestone adds:

```text
backend/app/data_profiler_role_scoring.py
```

The new module owns:
- header normalisation
- token generation
- value-hint scoring
- type-based scoring
- semantic role candidate generation

`data_profiler.py` continues to own:
- column profile assembly
- best-role mapping extraction
- workspace compatibility
- summary generation
- CSV profiling orchestration

## Expected Files Changed
- `backend/app/data_profiler.py`
- `backend/app/data_profiler_role_scoring.py`
- `backend/tests/test_data_profiler_role_scoring.py`
- `docs/foundation/milestone_16d_data_profiler_role_scoring_modularisation.md`

## Behaviour Boundary
This milestone should not change:
- profiler API response shape
- role confidence thresholds
- workspace routing
- governance wording
- frontend behaviour
- existing test expectations

## Non-Goals
This milestone does not:
- change scoring rules
- change thresholds
- add mapping UI
- implement flexible import
- implement saved mapping plans
- redesign workspace routing
- change output wording

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
- semantic role scoring is isolated
- profiler behaviour remains unchanged
