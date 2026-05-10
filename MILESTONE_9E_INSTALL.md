# Milestone 9E Install Notes

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-9e-audit-traceability-layer
```

Then extract the zip into the repo root.

## Apply

```powershell
.\apply_milestone_9e_audit_traceability_layer.ps1
```

Remove backups before commit:

```powershell
Remove-Item backend\app\models.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\schemas.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\crud.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\main.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\routers\streams.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\routers\recommendations.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\routers\workspace.py.bak-* -ErrorAction SilentlyContinue
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

## Manual API check

Start backend, then:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/streams/load-sample
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/recommendations/run
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/workspace/analysis-runs/snapshot
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/audit/summary | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/audit/events | ConvertTo-Json -Depth 5
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git add backend/app/models.py backend/app/schemas.py backend/app/crud.py backend/app/main.py
git add backend/app/routers/audit.py backend/app/routers/streams.py backend/app/routers/recommendations.py backend/app/routers/workspace.py
git add backend/tests/test_audit_trail.py docs/milestone_9e_audit_traceability_layer.md MILESTONE_9E_INSTALL.md apply_milestone_9e_audit_traceability_layer.ps1
git commit -m "Add audit and traceability layer"
```
