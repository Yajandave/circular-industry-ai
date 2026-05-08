# Circular Industry AI Frontend

React + Vite interface for the Industrial Circular Economy AI Agent portfolio project.

## Current milestone

Milestone 6: dashboard and advanced recommendation filters.

## What the frontend does

- Connects to the FastAPI backend.
- Loads the synthetic manufacturing material-flow dataset.
- Uploads a custom CSV following the data dictionary.
- Runs the locked rules-based recommendation engine.
- Shows dashboard cards for material quantity, human review, value exposure and recommendation portfolio status.
- Displays visual breakdowns for strategy mix, risk profile, priority bands and annual material quantity by material type.
- Provides advanced filters for search, material, strategy, risk, review status, priority band, confidence and evidence score.
- Sorts recommendations by priority, annual cost exposure, diversion potential, risk, confidence or evidence maturity.
- Opens controlled agentic review packs for evidence, risk, procurement, industrial symbiosis and resource-efficiency context.
- Shows a ranked action plan while keeping the rules engine as the locked decision source.

## Run locally

```bash
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The backend should be running at:

```text
http://127.0.0.1:8000
```

If your local npm install tries to use a private or unavailable registry, run:

```bash
npm config set registry https://registry.npmjs.org/
```

Then delete `node_modules` and `package-lock.json`, reinstall, and run the frontend again.

## Governance note

Dashboard figures are screening outputs. They should not be presented as verified savings, verified diversion or verified environmental benefit until actions are completed and evidenced.
