# Milestone 9F Install Notes

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-9f-data-quality-validation
```

Then extract the zip into the repo root.

## Apply

```powershell
.\apply_milestone_9f_data_quality_validation.ps1
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

## Manual API check

Start backend, then:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/streams/load-sample
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/data-quality/current | ConvertTo-Json -Depth 5
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git add backend/app/data_quality.py backend/app/routers/data_quality.py backend/app/main.py backend/app/schemas.py backend/tests/test_data_quality.py
git add docs/milestone_9f_data_quality_validation.md MILESTONE_9F_INSTALL.md apply_milestone_9f_data_quality_validation.ps1
git commit -m "Add data quality validation layer"
```
