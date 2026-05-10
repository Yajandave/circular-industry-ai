# Milestone 9B Install Notes

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-9b-ai-runtime-hardening
```

Then extract the zip into the repo root.

## Apply

```powershell
.\apply_milestone_9b_ai_runtime_hardening.ps1
```

Remove backups before commit:

```powershell
Remove-Item backend\app\main.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\schemas.py.bak-* -ErrorAction SilentlyContinue
Remove-Item backend\app\llm_reasoning\openai_client.py.bak-* -ErrorAction SilentlyContinue
Remove-Item frontend\src\App.jsx.bak-* -ErrorAction SilentlyContinue
Remove-Item frontend\src\api\client.js.bak-* -ErrorAction SilentlyContinue
Remove-Item frontend\src\styles.css.bak-* -ErrorAction SilentlyContinue
```

## Test backend

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
pytest
```

## Test frontend

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
```

## Verify local workflow

Start backend with fallback mode:

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
$env:AI_REASONING_ENABLED="false"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd E:\Games\Cricket\circular-industry-ai
.\scripts\verify_local_product_workflow.ps1
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git add backend/app/routers/ai_runtime.py backend/app/main.py backend/app/schemas.py backend/app/llm_reasoning/openai_client.py backend/app/ai_copilot/llm_client.py backend/app/evidence_explainer/llm_client.py backend/app/supplier_drafting/llm_client.py backend/app/report_builder/llm_client.py backend/tests/test_ai_runtime_status.py
git add frontend/src/App.jsx frontend/src/api/client.js frontend/src/components/AIRuntimeStatus.jsx frontend/src/styles.css
git add docs/milestone_9b_ai_runtime_hardening.md MILESTONE_9B_INSTALL.md MILESTONE_9B_AI_RUNTIME_STYLES.css apply_milestone_9b_ai_runtime_hardening.ps1
git commit -m "Add AI runtime reliability diagnostics"
```
