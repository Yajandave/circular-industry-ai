# Milestone 8B: Frontend AI Copilot Panel

## What this adds

This adds a new frontend tab:

```text
AI Copilot
```

It calls the backend endpoint created in Milestone 8A:

```text
GET /api/ai-copilot/site-summary
```

The panel shows:

- executive briefing
- risk position
- circular opportunity summary
- evidence gap summary
- supplier/procurement actions
- human review priorities
- recommended next actions
- claim safety note
- governance note

## Why this zip uses a patch script

Your local frontend is already ahead of the GitHub `main` snapshot because it includes the Supplier Loops / Milestone 7E work. A full file overwrite could accidentally remove that.

This zip therefore adds the new component and uses a patch script to update your existing local files.

## How to apply

Extract this zip into the repo root:

```text
E:\Games\Cricket\circular-industry-ai
```

Then run from the repo root:

```powershell
.\apply_milestone_8b_frontend_copilot.ps1
```

The script creates backups of these files before editing:

```text
frontend/src/App.jsx
frontend/src/api/client.js
frontend/src/components/WorkflowNav.jsx
frontend/src/styles.css
```

## Test

Backend terminal:

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
uvicorn app.main:app --reload
```

Frontend terminal:

```powershell
cd E:\Games\Cricket\circular-industry-ai\frontend
npm run build
npm run dev
```

Open the app, click:

```text
AI Copilot
```

Then click:

```text
Generate copilot summary
```

## Commit

```powershell
git status
git add frontend/src/App.jsx frontend/src/api/client.js frontend/src/components/WorkflowNav.jsx frontend/src/components/SiteAICopilotPanel.jsx frontend/src/styles.css MILESTONE_8B_FRONTEND_AI_COPILOT.md MILESTONE_8B_COPILOT_STYLES.css apply_milestone_8b_frontend_copilot.ps1
git commit -m "Add frontend site-wide AI copilot panel"
```
