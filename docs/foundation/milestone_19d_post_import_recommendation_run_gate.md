# Milestone 19D — Post-import Recommendation Run Gate

## Purpose

Add a separate frontend gate for running the rules engine after a controlled draft import has been saved.

This keeps import and recommendation execution as two explicit operator actions.

## Why This Matters

Milestone 19C allowed the operator to save approved draft rows to SQLite from the frontend.

Milestone 19D adds the next controlled step:

```text
import approved rows → then manually run recommendations
```

This prevents recommendations from being generated automatically at the moment of import.

## Scope

This milestone adds:

- a post-import recommendation gate inside the data profiler workflow
- an explicit operator confirmation checkbox before running the rules engine
- a controlled button that calls the existing `api.runRecommendations()`
- a follow-up call to `api.recommendationSummary()`
- a result panel showing analysed streams, recommendations created, human review count and high-priority count
- claim-safe wording that recommendation outputs are screening outputs only

## Expected Files Changed

- `frontend/src/components/DataProfilerPanel.jsx`
- `frontend/src/styles.css`
- `docs/foundation/milestone_19d_post_import_recommendation_run_gate.md`

## Behaviour

The frontend should:

- show the recommendation gate only after rows are successfully imported
- require operator confirmation before enabling the recommendation run
- call the existing recommendation run endpoint
- show the run result returned by the backend
- show summary metrics after the run
- clearly state that outputs are not verified claims

## Important Boundary

This milestone does not:

- automatically run recommendations after import
- verify cost savings
- verify waste diversion
- verify supplier compliance
- verify carbon reduction
- verify environmental benefit
- create evidence documents
- approve recommendations for action
- replace human review

The rules engine output is decision support only.

## Existing Backend Used

The backend already exposes:

```text
POST /api/recommendations/run
GET /api/recommendations/summary
```

The frontend already has API client functions for these endpoints:

```text
api.runRecommendations()
api.recommendationSummary()
```

19D uses those existing functions rather than adding backend logic.

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

Manual check:

- profile a CSV
- validate mappings
- build draft preview
- approve and save draft rows
- confirm the post-import recommendation gate appears
- tick the recommendation confirmation checkbox
- run recommendations
- confirm run result and summary appear
- confirm no wording implies verified savings, diversion, supplier compliance or environmental benefit
