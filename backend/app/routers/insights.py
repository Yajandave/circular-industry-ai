"""Autonomous insight generation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.insight_generator.service import generate_autonomous_insight

router = APIRouter(prefix="/api/insights", tags=["autonomous insights"])


@router.post("/generate", response_model=schemas.AutonomousInsightResult)
def generate_insight_from_raw_stream(
    stream: schemas.KnowledgeStreamInput,
) -> schemas.AutonomousInsightResult:
    """Generate autonomous insight from stream-like raw input."""
    return generate_autonomous_insight(stream)


@router.get("/stream/{stream_id}", response_model=schemas.AutonomousInsightResult)
def generate_insight_for_existing_stream(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.AutonomousInsightResult:
    """Generate autonomous insight for an existing loaded stream."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    return generate_autonomous_insight(stream)
