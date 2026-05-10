# Milestone 9C Install Notes

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-9c-frontend-workflow-guardrails
```

Then extract the zip into the repo root.

## Apply

```powershell
.\apply_milestone_9c_frontend_workflow_guardrails.ps1
```

Remove backups before commit:

```powershell
Remove-Item frontend\src\App.jsx.bak-* -ErrorAction SilentlyContinue
Remove-Item frontend\src\api\client.js.bak-* -ErrorAction SilentlyContinue
Remove-Item frontend\src\components\WorkflowNav.jsx.bak-* -ErrorAction SilentlyContinue
Remove-Item frontend\src\styles.css.bak-* -ErrorAction SilentlyContinue
```

## Test frontend

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
```

## Test backend still passes

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

## Verify local workflow

```powershell
cd E:\Games\Cricket\circular-industry-ai
.\scripts\verify_local_product_workflow.ps1
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git add frontend/src/App.jsx frontend/src/api/client.js frontend/src/components/WorkflowNav.jsx frontend/src/components/WorkflowPrerequisiteNotice.jsx frontend/src/components/AIRuntimeStatus.jsx frontend/src/styles.css
git add docs/milestone_9c_frontend_workflow_guardrails.md MILESTONE_9C_INSTALL.md MILESTONE_9C_FRONTEND_GUARDRAILS_STYLES.css apply_milestone_9c_frontend_workflow_guardrails.ps1
git commit -m "Add frontend workflow guardrails"
```
