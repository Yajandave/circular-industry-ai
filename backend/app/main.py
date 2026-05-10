"""FastAPI entry point for Circular Industry AI."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import agent, ai_copilot, ai_reasoning, diagnostics, evidence, playbooks, procurement, recommendations, reports, resolutions, streams, ai_runtime, workspace, audit, data_quality, knowledge, insights


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise local database tables when the API starts."""
    init_db()
    yield


app = FastAPI(
    title="Circular Industry AI API",
    description="Backend API for industrial circular economy material stream analysis.",
    version="0.8.0",
    lifespan=lifespan,
)

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
app.include_router(knowledge.router)
app.include_router(insights.router)
app.include_router(playbooks.router)

