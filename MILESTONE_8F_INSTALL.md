# Milestone 8F Install Notes

## Apply

After syncing `main`, extract this zip into:

```text
E:\Games\Cricket\circular-industry-ai
```

Then run from the repo root:

```powershell
.\apply_milestone_8f_frontend_action_report_panel.ps1
```

The script creates backups unless you pass `-NoBackup`.

## Test frontend

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
npm run dev
```

## Manual UI check

1. Start backend
2. Start frontend
3. Load sample dataset
4. Run recommendations
5. Open `Action report`
6. Select a stream
7. Confirm the report appears with locked fields and claim boundary

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout -b milestone-8f-frontend-action-report-panel
git add frontend/src/App.jsx frontend/src/api/client.js frontend/src/components/WorkflowNav.jsx frontend/src/components/CircularActionReportPanel.jsx frontend/src/styles.css docs/milestone_8f_frontend_action_report_panel.md MILESTONE_8F_INSTALL.md MILESTONE_8F_ACTION_REPORT_STYLES.css apply_milestone_8f_frontend_action_report_panel.ps1
git commit -m "Add frontend circular action report panel"
```
