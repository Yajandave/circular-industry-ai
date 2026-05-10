# Milestone 11E v4 Install Notes

## Branch

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-11e-operator-usability-ui-refinement
```

## Apply

Extract this zip into the repo root, then run:

```powershell
.\apply_milestone_11e_operator_usability_ui_refinement.ps1
```

## Test

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
```

## Manual check

- no whole-page horizontal scrollbar
- workflow nav does not overflow
- recommendations use compact list + detail inspector
- evidence uses compact list + detail inspector
- buttons stay horizontal
- text stays inside boxes
- AI runtime is simplified

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add frontend/src/components/AIRuntimeStatus.jsx frontend/src/components/WorkflowNav.jsx frontend/src/components/RecommendationsTable.jsx frontend/src/components/EvidenceRegister.jsx frontend/src/styles.css
git add docs/milestone_11e_operator_usability_ui_refinement.md MILESTONE_11E_INSTALL.md apply_milestone_11e_operator_usability_ui_refinement.ps1

git commit -m "Add operator master-detail UI layout"
git push -u origin milestone-11e-operator-usability-ui-refinement
```
