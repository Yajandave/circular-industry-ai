# Milestone 7 Acceptance: Evidence Register and Export Workflow

## Objective

Add an auditable evidence register and export workflow so Circular Industry AI can demonstrate evidence-led circular economy decision support rather than unsupported recommendations.

## Completed scope

- Added derived evidence register generation from locked rules-engine recommendations and stream records.
- Added evidence maturity classification for every recommendation.
- Added claim-readiness boundaries to prevent unsupported circular economy, savings or environmental claims.
- Added API endpoints for evidence register, evidence summary and CSV exports.
- Added a frontend Evidence Register workflow tab.
- Added export buttons for recommendations and evidence register CSV files.
- Added evidence-priority cards for records requiring human review or data improvement.

## New API endpoints

```text
GET /api/evidence-register
GET /api/evidence-register/summary
GET /api/export/evidence-register.csv
GET /api/export/recommendations.csv
```

## Evidence fields now tracked

- stream ID and stream name
- material, department and supplier
- locked recommendation and circular strategy
- rule applied
- risk level and human-review flag
- confidence score
- evidence quality score
- evidence status
- review gate
- claim-readiness status
- measured data
- estimated data
- assumptions
- missing data
- risk triggers
- review gates
- claim boundary
- next action
- screened annual diversion and cost exposure

## Acceptance criteria

- User can load the sample dataset and run recommendations.
- Evidence Register tab appears in the workflow navigation.
- Evidence register displays 50 records after recommendations are generated.
- Evidence summary shows human-review gates, low-evidence records, strong-evidence records and claim-readiness breakdown.
- CSV export links download recommendation and evidence-register files.
- The evidence register does not create new decisions or override risk status.
- Claim boundaries clearly state that outputs are internal screening, not verified savings or environmental impact.

## Suggested commit message

```text
feat: add evidence register and export workflow
```
