"""Autonomous insight generation and insight-history endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.insight_generator.service import generate_autonomous_insight
from app.insight_history.service import persist_autonomous_insight

router = APIRouter(prefix="/api/insights", tags=["autonomous insights"])


@router.post("/generate", response_model=schemas.AutonomousInsightResult)
def generate_insight_from_raw_stream(
    stream: schemas.KnowledgeStreamInput,
) -> schemas.AutonomousInsightResult:
    """Generate autonomous insight from stream-like raw input without saving it."""
    return generate_autonomous_insight(stream)


@router.post("/generate-and-save", response_model=schemas.GeneratedInsightRead)
def generate_and_save_insight_from_raw_stream(
    stream: schemas.KnowledgeStreamInput,
    db: Session = Depends(get_db),
) -> schemas.GeneratedInsightRead:
    """Generate autonomous insight from raw input and persist the result for audit/history."""
    insight = generate_autonomous_insight(stream)
    return persist_autonomous_insight(db, stream=stream, insight=insight)


@router.get("/history", response_model=list[schemas.GeneratedInsightRead])
def list_saved_insights(
    stream_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.GeneratedInsightRead]:
    """Return saved insight history, optionally filtered by stream_id."""
    if stream_id:
        return crud.get_generated_insights_by_stream_id(db, stream_id=stream_id, limit=limit)
    return crud.get_generated_insights(db, limit=limit)


@router.get("/history/{stream_id}", response_model=list[schemas.GeneratedInsightRead])
def get_stream_insight_history(
    stream_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.GeneratedInsightRead]:
    """Return saved insight history for one stream."""
    return crud.get_generated_insights_by_stream_id(db, stream_id=stream_id, limit=limit)


@router.get("/latest/{stream_id}", response_model=schemas.GeneratedInsightRead)
def get_latest_stream_insight(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.GeneratedInsightRead:
    """Return the latest saved insight for one stream."""
    insight = crud.get_latest_generated_insight_by_stream_id(db, stream_id=stream_id)
    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No saved autonomous insight found for stream: {stream_id}",
        )
    return insight


@router.get("/stream/{stream_id}", response_model=schemas.AutonomousInsightResult)
def generate_insight_for_existing_stream(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.AutonomousInsightResult:
    """Generate autonomous insight for an existing loaded stream without saving it."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    return generate_autonomous_insight(stream)


@router.post("/stream/{stream_id}/generate-and-save", response_model=schemas.GeneratedInsightRead)
def generate_and_save_insight_for_existing_stream(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.GeneratedInsightRead:
    """Generate and save autonomous insight for an existing loaded stream."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    insight = generate_autonomous_insight(stream)
    return persist_autonomous_insight(db, stream=stream, insight=insight)
