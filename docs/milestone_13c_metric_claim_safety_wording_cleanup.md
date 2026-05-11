# Milestone 13C: Metric and Claim-Safety Wording Cleanup

## Objective

Milestone 13C tightens metric and claim-safety wording across the Circular Industry AI frontend.

The milestone reduces verified-sounding language around cost, diversion and impact outputs while preserving the existing backend fields, API contracts and locked rules engine.

## Why it matters professionally

Circular Industry AI produces screening outputs from operational material-flow data. These outputs are useful for prioritisation and review, but they are not verified savings, verified diversion, verified cost reduction or verified environmental benefit.

13C keeps the product language aligned with that evidence boundary.

## What changed

- Reworded selected dashboard, snapshot, recommendation and professional-suite labels.
- Used safer language such as screened cost exposure, screened quantity opportunity and potential only.
- Strengthened notes around unverified savings, diversion and impact.
- Added lightweight frontend aliases in analytics for safer future UI naming while preserving backend response fields.

## What does not change

This milestone does not change:

- backend rules engine
- database models
- API contracts
- scoring logic
- recommendation logic
- LLM authority
- verified impact handling
- legal/compliance boundaries

## Governance boundary

The rules engine remains the locked decision source.

Dashboard values are screening outputs. They support prioritisation and operator attention only. They must not be presented as verified savings, verified diversion, verified cost reduction, verified environmental benefit or external sustainability claims.

## Testing steps

```powershell
git diff --check
cd frontend
npm run build
cd ..
git status --short
git diff --stat
```

## Commit message

```text
Tighten metric and claim-safety wording
```

## PR title

```text
Milestone 13C: Tighten metric and claim-safety wording
```

## Pre-merge file check

Expected files:

```text
frontend/src/components/SummaryCards.jsx
frontend/src/components/Dashboard.jsx
frontend/src/components/VisualAnalyticsDashboard.jsx
frontend/src/components/ProfessionalIntelligenceSuite.jsx
frontend/src/components/PortfolioSnapshot.jsx
frontend/src/components/RecommendationsTable.jsx
frontend/src/utils/analytics.js
docs/milestone_13c_metric_claim_safety_wording_cleanup.md
```

Do not commit installer files, zip files, frontend/dist, node_modules, .env, .venv or database files.
