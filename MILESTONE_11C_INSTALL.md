# Milestone 11C Install Notes

## Branch

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-11c-retrieval-insight-quality-evaluation
```

## Apply

Extract this zip into the repo root, then run:

```powershell
.\apply_milestone_11c_retrieval_insight_quality_evaluation.ps1
```

## Backend tests

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

## Frontend build

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
```

## Manual checks

Start backend, then run:

```powershell
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/evaluation/cases | ConvertTo-Json -Depth 8

$body = @{
  case_ids = @("eval_mixed_plastics_high_contamination")
} | ConvertTo-Json

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/evaluation/run -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/evaluation/summary | ConvertTo-Json -Depth 10
```

Expected signs:

```text
mixed plastics case matches plastics
battery future route is forbidden and absent
notes_dependency_not_required passes
claim_boundary_present passes
unknown generic rejects has no material match
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add backend/app/evaluation backend/app/routers/evaluation.py backend/app/main.py backend/app/schemas.py backend/tests/test_retrieval_insight_evaluation.py
git add docs/milestone_11c_retrieval_insight_quality_evaluation.md MILESTONE_11C_INSTALL.md apply_milestone_11c_retrieval_insight_quality_evaluation.ps1

git commit -m "Add retrieval and insight quality evaluation"
git push -u origin milestone-11c-retrieval-insight-quality-evaluation
```
