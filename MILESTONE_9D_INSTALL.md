# Milestone 9D Install Notes

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-9d-data-model-foundation
```

Then extract the zip into the repo root.

## Apply

```powershell
.\apply_milestone_9d_data_model_foundation.ps1
```

Remove backups before commit:

```powershell
Remove-Item backend\app\models.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\schemas.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\crud.py.bak-* -ErrorAction SilentlyContinue
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

## Manual API check

Start backend, then:

```powershell
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/workspace/context | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/workspace/analysis-runs/snapshot | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/workspace/analysis-runs | ConvertTo-Json -Depth 5
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git add backend/app/models.py backend/app/schemas.py backend/app/crud.py backend/app/main.py backend/app/routers/workspace.py backend/tests/test_workspace_metadata.py
git add docs/milestone_9d_data_model_foundation.md MILESTONE_9D_INSTALL.md apply_milestone_9d_data_model_foundation.ps1
git commit -m "Add workspace and analysis run metadata foundation"
```
