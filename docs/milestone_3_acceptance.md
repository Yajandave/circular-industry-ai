# Milestone 3 Acceptance Criteria

## Milestone title
Rules-based circular recommendation engine

## Objective
Add a deterministic circular economy rules engine that converts loaded industrial material/waste streams into structured recommendations for human review.

This milestone deliberately keeps AI out of the decision-making step. The system now uses traceable rules, risk scoring and evidence scoring before any future AI explanation layer is added.

## Added functionality

- Rules engine for first-pass circular economy recommendations
- Risk scoring for low, medium, high and blocked cases
- Evidence quality scoring from available dataset fields
- Confidence scoring based on evidence, risk and rule strength
- Human review flags for hazardous, unknown or high-contamination streams
- Annual diversion and disposal-cost-avoidance estimates
- Supplier/procurement action suggestions
- Industrial symbiosis opportunity flags
- Recommendation summary endpoint
- API tests for rules, endpoints and S001 example

## New backend files

```text
backend/app/rules_engine.py
backend/app/scoring.py
backend/app/routers/recommendations.py
backend/tests/test_rules_engine.py
```

## Updated backend files

```text
backend/app/main.py
backend/app/models.py
backend/app/schemas.py
backend/app/crud.py
backend/README.md
```

## New API endpoints

```text
POST /api/recommendations/run
GET  /api/recommendations
GET  /api/recommendations/summary
GET  /api/recommendations/{stream_id}
```

## Manual test order

1. Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

2. Open:

```text
http://127.0.0.1:8000/docs
```

3. Run:

```text
POST /api/streams/load-sample
POST /api/recommendations/run
GET  /api/recommendations
GET  /api/recommendations/S001
GET  /api/recommendations/summary
```

## Expected S001 output pattern

S001, Aluminium machining offcuts, should be classified as:

```text
Recommended action: Closed-loop recycling review
Circular strategy category: closed-loop recycling
Risk level: low
Human review required: false
Evidence gap: material grade or alloy segregation evidence
```

## Automated test result

```text
10 passed
```

## Acceptance checklist

- [x] Recommendations are generated for all loaded streams
- [x] Hazardous or uncertain streams trigger human review
- [x] Clean metal streams can receive closed-loop recycling recommendations
- [x] Supplier take-back opportunities are detected
- [x] Evidence quality score is generated
- [x] Risk level is generated
- [x] Confidence score is generated
- [x] Missing data is identified
- [x] Annual waste diversion estimate is calculated where appropriate
- [x] Annual disposal cost avoidance estimate is calculated where appropriate
- [x] API endpoints return recommendation outputs
- [x] Tests pass

## Suggested GitHub commit message

```text
feat: add rules-based circular recommendation engine
```

## What this proves to recruiters

This milestone shows that the project is not a generic AI demo. It demonstrates structured sustainability decision logic, industrial circular economy judgement, evidence scoring, risk screening and backend implementation ability.
