# Milestone 8C Install Notes

## Apply

After syncing `main`, extract this zip into:

```text
E:\Games\Cricket\circular-industry-ai
```

Then run from the repo root:

```powershell
.\apply_milestone_8c_evidence_gap_explainer.ps1
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
npm run dev
```

## Manual UI check

1. Load sample dataset
2. Run recommendations
3. Open Evidence register
4. Click `Explain evidence gap`
5. Confirm the panel appears with locked risk level, locked review gate, locked claim readiness, evidence to collect and unsafe claims to avoid.
