# Milestone 7E Acceptance Criteria

## Objective
Add a circular procurement and supplier-loop intelligence layer that converts circular resolution plans into supplier-facing actions, contract evidence requests, reverse-logistics checks and procurement pilot controls.

## Acceptance criteria
- New API endpoints are available under `/api/procurement`.
- The system can generate supplier-loop plans for all locked recommendations.
- Supplier-loop plans keep risk level, human-review status, rule applied and claim boundaries locked.
- High-risk or hazardous streams remain in controlled supplier/contractor evidence review.
- Low-risk circular opportunities receive supplier questions, contract levers, evidence requirements, reverse-logistics model and pilot scope.
- A frontend workflow tab called `Supplier loops` displays summary metrics, top supplier actions and plan cards.
- CSV export is available at `/api/export/supplier-loop-plans.csv`.
- No API keys or environment secrets are committed.

## Suggested checks
1. `POST /api/streams/load-sample`
2. `POST /api/recommendations/run`
3. `POST /api/resolutions/run`
4. `POST /api/procurement/run`
5. `GET /api/procurement/supplier-loops/summary`
6. `GET /api/procurement/supplier-loops/S001`
7. `GET /api/procurement/supplier-loops/S045`
8. `GET /api/export/supplier-loop-plans.csv`

## Suggested commit message
`feat: add circular procurement and supplier-loop intelligence`
