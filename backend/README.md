# Backend - Circular Industry AI

This backend is the Milestone 2 foundation for the Circular Industry AI portfolio project.

It uses:

- FastAPI for the API layer
- SQLite for local storage
- SQLAlchemy for database models
- Pydantic for request/response schemas
- Pandas for loading the synthetic industrial stream CSV

## What this milestone does

Milestone 2 turns the Milestone 1 dataset into a working backend service.

The API can:

1. create the SQLite database tables
2. load the sample industrial material/waste stream dataset
3. return all streams
4. return one stream by stream ID
5. return basic summary metrics

It does **not** yet run circular economy recommendations. That comes in Milestone 3.

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
```

## Suggested manual test order

1. Start the backend with `uvicorn app.main:app --reload`
2. Open `http://127.0.0.1:8000/docs`
3. Run `POST /api/streams/load-sample`
4. Run `GET /api/streams`
5. Run `GET /api/streams/S001`
6. Run `GET /api/streams/summary`

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
