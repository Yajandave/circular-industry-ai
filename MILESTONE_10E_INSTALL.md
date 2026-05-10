# Milestone 10E Install Notes

## Branch

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-10e-insight-history-traceability
```

## Apply

Extract this zip into the repo root, then run:

```powershell
.\apply_milestone_10e_insight_history_traceability.ps1
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

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/insights/generate-and-save -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 8

Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/insights/history/RAW001 | ConvertTo-Json -Depth 8

Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/insights/latest/RAW001 | ConvertTo-Json -Depth 8
```

Expected signs:

```text
input_notes_present: false
notes_dependency: not_required
generation_mode: deterministic
matched_material_families includes plastics only
source_knowledge_ids populated
input_snapshot present
history endpoint returns saved records
latest endpoint returns latest saved record
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add backend/app/insight_history backend/app/routers/insights.py backend/app/models.py backend/app/crud.py backend/app/schemas.py backend/tests/test_insight_history_traceability.py
git add docs/milestone_10e_insight_history_traceability.md MILESTONE_10E_INSTALL.md apply_milestone_10e_insight_history_traceability.ps1

git commit -m "Add insight history and traceability"
git push -u origin milestone-10e-insight-history-traceability
```
