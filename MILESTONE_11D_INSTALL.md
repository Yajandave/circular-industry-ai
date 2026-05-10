# Milestone 11D Install Notes

## Branch

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-11d-operator-ui-agentic-intelligence
```

## Apply

Extract this zip into the repo root, then run:

```powershell
.\apply_milestone_11d_operator_ui_agentic_intelligence.ps1
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

## Manual check

Run backend and frontend, then:

1. Load sample dataset.
2. Open the new Agentic intelligence tab.
3. Select S008 or another stream.
4. Click Run workflow.
5. Confirm workflow steps, quality gates, graph path and generated insight appear.
6. Click Run + save.
7. Click Load history.
8. Click Run evaluation.

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add frontend/src/api/client.js frontend/src/App.jsx frontend/src/components/WorkflowNav.jsx frontend/src/components/AgenticIntelligencePanel.jsx frontend/src/styles.css
git add docs/milestone_11d_operator_ui_agentic_intelligence.md MILESTONE_11D_INSTALL.md apply_milestone_11d_operator_ui_agentic_intelligence.ps1

git commit -m "Add operator UI for agentic intelligence"
git push -u origin milestone-11d-operator-ui-agentic-intelligence
```
