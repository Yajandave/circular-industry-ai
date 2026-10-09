"""FastAPI entry point for Circular Industry AI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from time import perf_counter
from fastapi import Request
from fastapi.responses import JSONResponse
from app.diagnostic_events import record

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import agent, ai_copilot, ai_reasoning, diagnostics, evidence, playbooks, procurement, recommendations, reports, resolutions, streams, ai_runtime, workspace, audit, data_quality, data_profiler, knowledge, knowledge_graph, agentic_retrieval, evaluation, insights, scenarios, decision_validation, governance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise local database tables when the API starts."""
    init_db()
    yield


app = FastAPI(
    title="Circular Industry AI API",
    description="Backend API for industrial circular economy material stream analysis.",
    version="0.19.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def diagnostic_request_metrics(request: Request, call_next):
    start = perf_counter()
    try:
        response = await call_next(request)
        record(request.url.path, request.method, response.status_code, round((perf_counter() - start) * 1000))
        return response
    except Exception as exc:
        record(request.url.path, request.method, 500, round((perf_counter() - start) * 1000), type(exc).__name__)
        # No exception content or input data is returned to the browser.
        return JSONResponse({"detail": "Internal server error; consult local backend logs."}, status_code=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "Circular Industry AI API"}


app.include_router(streams.router)
app.include_router(recommendations.router)
app.include_router(agent.router)
app.include_router(evidence.router)
app.include_router(resolutions.router)
app.include_router(ai_reasoning.router)
app.include_router(ai_copilot.router)
app.include_router(ai_runtime.router)
app.include_router(reports.router)
app.include_router(procurement.router)
app.include_router(diagnostics.router)
app.include_router(workspace.router)
app.include_router(audit.router)
app.include_router(data_quality.router)
app.include_router(data_profiler.router)
app.include_router(knowledge.router)
app.include_router(knowledge_graph.router)
app.include_router(agentic_retrieval.router)
app.include_router(evaluation.router)
app.include_router(insights.router)
app.include_router(playbooks.router)
app.include_router(scenarios.router)
app.include_router(decision_validation.router)
app.include_router(governance.router)




