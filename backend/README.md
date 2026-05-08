# Backend - Circular Industry AI

This backend now includes the Milestone 3 rules-based recommendation engine. It began as the Milestone 2 foundation for the Circular Industry AI portfolio project.

It uses:

- FastAPI for the API layer
- SQLite for local storage
- SQLAlchemy for database models
- Pydantic for request/response schemas
- Pandas for loading the synthetic industrial stream CSV

## What this backend does

Milestone 2 turned the Milestone 1 dataset into a working backend service. Milestone 3 adds deterministic circular economy recommendations, risk scoring, evidence scoring and human review flags.

The API can:

1. create the SQLite database tables
2. load the sample industrial material/waste stream dataset
3. return all streams
4. return one stream by stream ID
5. return basic stream summary metrics
6. run rules-based circular economy recommendations
7. return recommendation outputs and summary metrics
8. flag hazardous or weak-evidence streams for human review

## Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API

From the `backend` folder:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Main endpoints

```text
GET  /health
POST /api/streams/load-sample
GET  /api/streams
GET  /api/streams/summary
GET  /api/streams/{stream_id}
POST /api/recommendations/run
GET  /api/recommendations
GET  /api/recommendations/summary
GET  /api/recommendations/{stream_id}
```

## Suggested manual test order

1. Start the backend with `uvicorn app.main:app --reload`
2. Open `http://127.0.0.1:8000/docs`
3. Run `POST /api/streams/load-sample`
4. Run `GET /api/streams`
5. Run `GET /api/streams/S001`
6. Run `GET /api/streams/summary`
7. Run `POST /api/recommendations/run`
8. Run `GET /api/recommendations/S001`
9. Run `GET /api/recommendations/summary`

## Run tests

From the `backend` folder:

```bash
pytest
```

## Milestone 2 acceptance criteria

- FastAPI app starts successfully
- SQLite database is created locally
- sample CSV loads into the database
- `/health` returns a healthy response
- `/api/streams` returns stream records
- `/api/streams/{stream_id}` returns one stream
- `/api/streams/summary` returns basic totals

## Suggested commit message

```text
feat: add FastAPI backend and industrial stream database
```


## Milestone 3 acceptance criteria

- Rules engine generates recommendations for loaded streams
- Hazardous, unknown or high-contamination streams are flagged for human review
- S001 is classified as a closed-loop recycling review case
- Recommendation outputs include risk level, confidence score and evidence quality score
- Recommendation outputs include missing data, next action and supplier/procurement action
- Recommendation summary endpoint returns high-level metrics
- Tests pass

## Suggested Milestone 3 commit message

```text
feat: add rules-based circular recommendation engine
```


## Milestone 4: controlled agentic decision support

The API now includes an advanced agentic review layer that enriches rules-based recommendations without replacing them.

New endpoints:

```text
GET /api/agent/review-pack/{stream_id}
GET /api/agent/management-summary
GET /api/agent/action-plan
```

The agentic layer includes specialist reviewers for evidence, risk, procurement, industrial symbiosis, resource efficiency and executive synthesis. The rules engine remains the source of truth. The agentic layer cannot lower risk, remove human-review flags or override the rule applied.

## Milestone 5 additions

Milestone 5 adds a frontend-facing CSV upload route:

```text
POST /api/streams/upload-csv
```

This endpoint accepts a custom CSV file matching `data/data_dictionary.md`, validates required columns, normalises hazard status, replaces existing stream rows, and returns the number of rows loaded.

The frontend uses this route for user-uploaded industrial stream datasets while retaining the sample loader for demonstrations.
