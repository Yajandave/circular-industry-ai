# Milestone 10C Install Notes

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-10c-knowledge-retrieval-engine
```

Then extract the zip into the repo root.

## Apply

```powershell
.\apply_milestone_10c_knowledge_retrieval_engine.ps1
```

Remove backups before commit:

```powershell
Remove-Item backend\app\schemas.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\main.py.bak-* -ErrorAction SilentlyContinue
```

## Test backend

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

## Test frontend still builds

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
```

## Manual API checks

Start backend, then:

```powershell
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/knowledge/validate | ConvertTo-Json -Depth 5

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

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/knowledge/match -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 8
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add backend/app/knowledge_base/retriever.py backend/app/routers/knowledge.py backend/app/main.py backend/app/schemas.py backend/tests/test_knowledge_retrieval.py
git add docs/milestone_10c_knowledge_retrieval_engine.md MILESTONE_10C_INSTALL.md apply_milestone_10c_knowledge_retrieval_engine.ps1

git commit -m "Add knowledge retrieval engine"
git push -u origin milestone-10c-knowledge-retrieval-engine
```
