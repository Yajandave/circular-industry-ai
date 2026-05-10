# Milestone 11B Install Notes

## Branch

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-11b-agentic-retrieval-workflow
```

## Apply

Extract this zip into the repo root, then run:

```powershell
.\apply_milestone_11b_agentic_retrieval_workflow.ps1
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

Start the backend, then run:

```powershell
$body = @{
  stream_id = "RAW001"
  stream_name = "Mixed polymer injection moulding rejects"
  material = "mixed plastics"
  source_process = "injection moulding"
  monthly_quantity_kg = 1680
  current_route = "general waste"
  disposal_cost_per_month = 720
  contamination_risk = "high"
  hazardous_flag = "false"
  department = "Production"
  supplier = "PolyMax Resins"
  supplier_takeback_available = "unknown"
  recycled_content_available = "unknown"
  notes = ""
} | ConvertTo-Json

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/agentic-retrieval/run -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/agentic-retrieval/run-and-save -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 10
```

Expected signs:

```text
workflow_mode = deterministic
notes_dependency = not_required
steps include classify, retrieve, graph, insight, persist
quality_gates include notes_independence and claim_boundary_present
matched_material_families = plastics only
source_knowledge_ids exclude future_battery_recycling_v1
run-and-save returns saved_insight_id
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add backend/app/agentic_retrieval backend/app/routers/agentic_retrieval.py backend/app/main.py backend/app/schemas.py backend/tests/test_agentic_retrieval_workflow.py
git add docs/milestone_11b_agentic_retrieval_workflow.md MILESTONE_11B_INSTALL.md apply_milestone_11b_agentic_retrieval_workflow.ps1

git commit -m "Add agentic retrieval workflow"
git push -u origin milestone-11b-agentic-retrieval-workflow
```
