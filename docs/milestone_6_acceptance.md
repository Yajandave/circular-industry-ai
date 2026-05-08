# Milestone 6 Acceptance Criteria

## Milestone
Dashboard and filters layer for Circular Industry AI.

## Objective
Turn the recommendation interface into a decision dashboard that helps users prioritise industrial circular economy actions by strategy, risk, evidence quality, confidence, material type, value exposure and diversion potential.

## Added in this milestone

- Dashboard insight cards for quick wins, controlled review items, low-evidence records and screened value exposure.
- Executive portfolio summary from the controlled agentic layer.
- Visual breakdowns for recommended strategy mix, risk profile, priority bands and annual material quantity by material type.
- Top candidate lists for annual cost exposure and annual diversion potential.
- Advanced filtering by search, material, strategy, risk, review status, priority band, confidence threshold and evidence threshold.
- Sort controls for priority score, annual cost exposure, annual diversion potential, risk severity, confidence and evidence quality.
- Enriched recommendation table showing stream name, material, department, priority band and calculated priority score.
- Review-pack jump behaviour for dashboard and table candidates.
- Clear governance note explaining that dashboard values are screening outputs, not verified savings or verified environmental benefit.

## Acceptance criteria

- Frontend connects to the FastAPI backend.
- User can load sample data.
- User can run the rules engine.
- Dashboard displays portfolio insight cards and visual breakdowns.
- Filters update the recommendations table without changing the locked backend recommendation records.
- Search works across stream ID, stream name, supplier, department, recommendation and next action text.
- User can sort recommendations by priority, cost exposure, diversion potential, risk, confidence or evidence quality.
- User can open an agentic review pack from both the dashboard candidate cards and the recommendations table.
- High-risk and human-review records remain clearly labelled.
- The dashboard includes claim-boundary language to avoid presenting estimates as verified outcomes.

## Suggested test route

1. Start backend.
2. Start frontend.
3. Open `http://127.0.0.1:5173`.
4. Click `Load sample dataset`.
5. Click `Run recommendations`.
6. Confirm dashboard charts appear.
7. Search for `aluminium`.
8. Filter strategy to `supplier take-back / circular procurement`.
9. Filter review status to `human review required`.
10. Sort by `annual cost exposure`.
11. Open a review pack from a dashboard candidate.
12. Open a review pack from the recommendations table.

## Suggested commit message

```bash
git commit -m "feat: add dashboard and advanced recommendation filters"
```

## Recruiter-facing proof

This milestone shows that the project can move from raw API output to a practical decision-support interface. It demonstrates dashboard design, prioritisation logic, evidence-led filtering, risk communication and responsible AI governance for industrial circular economy screening.
