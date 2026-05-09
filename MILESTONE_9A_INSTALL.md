# Milestone 9A Install Notes

## Important order

Create the branch before extracting future milestone zips.

For this milestone:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-9a-product-workflow-stabilisation
```

Then extract the zip into the repo root.

## Apply

```powershell
.\apply_milestone_9a_product_workflow_stabilisation.ps1
```

The script creates backups unless you pass `-NoBackup`.

Remove backups before commit:

```powershell
Remove-Item backend\app\main.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\schemas.py.bak-* -ErrorAction SilentlyContinue
```

## Test backend

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
pytest
```

## Test frontend still builds

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
```

## Run local workflow verification

Start backend:

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd E:\Games\Cricket\circular-industry-ai
.\scripts\verify_local_product_workflow.ps1
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git add backend/app/routers/diagnostics.py backend/app/main.py backend/app/schemas.py backend/tests/test_product_workflow_smoke.py scripts/verify_local_product_workflow.ps1 docs/milestone_9a_product_workflow_stabilisation.md MILESTONE_9A_INSTALL.md apply_milestone_9a_product_workflow_stabilisation.ps1
git commit -m "Add product workflow readiness diagnostics"
```
