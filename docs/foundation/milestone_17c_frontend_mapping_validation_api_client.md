# Milestone 17C — Frontend Mapping Validation API Client

## Purpose
Expose the Milestone 17B mapping validation endpoint through the frontend API client.

This is not the mapping UI yet. It is a small frontend integration foundation so the future user-confirmed mapping screen can call the backend validation contract cleanly.

## Why This Matters
The backend now supports:

```text
POST /api/data-profiler/validate-mapping
```

Before building UI, the frontend should have a clear API function for this endpoint rather than embedding fetch logic inside components.

## Scope
This milestone adds:
- `api.validateMapping(payload)` to `frontend/src/api/client.js`
- documentation for the frontend integration boundary

## Expected Files Changed
- `frontend/src/api/client.js`
- `docs/foundation/milestone_17c_frontend_mapping_validation_api_client.md`

## Behaviour
The new frontend API method should:
- accept a mapping validation payload
- POST it as JSON
- return the backend validation report
- reuse the existing shared `request(...)` helper
- avoid introducing UI behaviour prematurely

## Example Payload Shape

```json
{
  "target_workspace": "circular-core",
  "mappings": [
    {
      "source_column": "Waste Material",
      "target_role": "material",
      "mapping_state": "accepted_by_user",
      "confidence": 96,
      "user_confirmed": true
    }
  ]
}
```

## Non-Goals
This milestone does not:
- build the mapping screen
- add frontend state management
- persist mappings
- import rows
- save mapping plans
- create audit trail records
- change backend behaviour

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

Manual review:
- API client has a single `validateMapping` method
- no component-level fetch duplication is introduced
- no UI overclaiming is introduced
