"""Optional rules-locked LLM reasoning endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.circular_resolution.resolution_engine import build_resolution_plan
from app.database import get_db
from app.evidence_register import build_evidence_record
from app.llm_reasoning.reasoning_service import generate_reasoning, reasoning_status

router = APIRouter(prefix="/api", tags=["rules-locked AI reasoning"])


@router.get("/ai-reasoning/status", response_model=schemas.AIReasoningStatus)
def get_ai_reasoning_status():
    """Return whether optional LLM reasoning is configured or using fallback mode."""
    return reasoning_status()


@router.post("/ai-reasoning/{stream_id}", response_model=schemas.AIReasoningNarrative)
def generate_ai_reasoning(stream_id: str, db: Session = Depends(get_db)):
    """Generate a stream-specific reasoning narrative from locked recommendation context.

    The LLM, when enabled, cannot override the rules engine. If the API key is not
    configured, the endpoint returns deterministic fallback reasoning.
    """
    stream = crud.get_stream_by_stream_id(db, stream_id)
    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail=f"No stream found for stream ID {stream_id}.")
    if not recommendation:
        raise HTTPException(status_code=404, detail="Run POST /api/recommendations/run before generating AI reasoning.")
    evidence = build_evidence_record(stream, recommendation)
    resolution = build_resolution_plan(stream, recommendation)
    return generate_reasoning(stream, recommendation, evidence, resolution)
