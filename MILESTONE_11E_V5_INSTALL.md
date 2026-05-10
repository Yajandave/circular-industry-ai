# Milestone 11E v5 Install Notes

Apply this after 11E v4.

## Apply

Extract this zip into the repo root, then run:

```powershell
cd E:\Games\Cricket\circular-industry-ai
.\apply_milestone_11e_v5_operator_cleanup.ps1
```

## Test

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
```

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

## Manual check

Confirm:

- no visible Milestone 8B
- no visible Milestone 7C
- no visible Milestone 8F
- no visible Evidence workflow label above Evidence Register
- summary counts are separated into cards
- text is readable and not glued together

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add frontend/src/components/SiteAICopilotPanel.jsx frontend/src/components/AIReasoningPanel.jsx frontend/src/components/CircularActionReportPanel.jsx frontend/src/components/CircularResolutionPlans.jsx frontend/src/components/SupplierLoopIntelligence.jsx frontend/src/components/MaterialPlaybooks.jsx frontend/src/components/EvidenceRegister.jsx frontend/src/styles.css
git add docs/milestone_11e_operator_usability_cleanup.md MILESTONE_11E_V5_INSTALL.md apply_milestone_11e_v5_operator_cleanup.ps1

git commit -m "Clean operator UI wording and summary cards"
git push -u origin milestone-11e-operator-usability-ui-refinement
```
