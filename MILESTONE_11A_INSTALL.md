# Milestone 11A Install Notes

## Branch

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-11a-knowledge-graph-relationship-layer
```

## Apply

Extract this zip into the repo root, then run:

```powershell
.\apply_milestone_11a_knowledge_graph_relationship_layer.ps1
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
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/knowledge/graph | ConvertTo-Json -Depth 8

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

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/knowledge/graph/match -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 8
```

Expected signs:

```text
graph_scope = stream_match
matched_material_families = plastics only
nodes include stream:RAW001
nodes include material:plastics
edges include matches_material_family
edges include has_candidate_route
edges include requires_evidence or requires_data
source_knowledge_ids do not include future_battery_recycling_v1
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add backend/app/knowledge_graph backend/app/routers/knowledge_graph.py backend/app/main.py backend/app/schemas.py backend/tests/test_knowledge_graph_relationships.py
git add docs/milestone_11a_knowledge_graph_relationship_layer.md MILESTONE_11A_INSTALL.md apply_milestone_11a_knowledge_graph_relationship_layer.ps1

git commit -m "Add knowledge graph relationship layer"
git push -u origin milestone-11a-knowledge-graph-relationship-layer
```
