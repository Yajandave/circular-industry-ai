# Milestone 8E Install Notes

## Apply

After syncing `main`, extract this zip into:

```text
E:\Games\Cricket\circular-industry-ai
```

Then run from the repo root:

```powershell
.\apply_milestone_8e_circular_action_report_builder.ps1
```

The script creates backups unless you pass `-NoBackup`.

## Test backend

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
pytest
```

## Manual API test

Start backend:

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
uvicorn app.main:app --reload
```

In another terminal:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/streams/load-sample
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/recommendations/run
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/reports/streams/S001/circular-action-report | ConvertTo-Json -Depth 5
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout -b milestone-8e-circular-action-report-builder
git add backend/app/report_builder backend/app/routers/reports.py backend/app/main.py backend/app/schemas.py backend/tests/test_report_builder.py docs/milestone_8e_circular_action_report_builder.md MILESTONE_8E_INSTALL.md apply_milestone_8e_circular_action_report_builder.ps1
git commit -m "Add circular action report builder"
```
