"""Agentic analysis endpoints for advanced decision support."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.agentic.orchestrator import (
    build_action_plan,
    build_management_summary,
    build_stream_review_pack,
)
from app.database import get_db

router = APIRouter(prefix="/api/agent", tags=["agentic decision support"])


@router.get("/review-pack/{stream_id}", response_model=schemas.AgenticReviewPack)
def get_agentic_review_pack(stream_id: str, db: Session = Depends(get_db)):
    """Return a multi-agent review pack for one stream.

    The base recommendation is locked from the rules engine. The agentic layer
    adds evidence, risk, procurement, symbiosis and management-review context.
    """
    stream = crud.get_stream_by_stream_id(db, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found")

    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="No recommendation found. Run POST /api/recommendations/run first.",
        )

    return build_stream_review_pack(stream, recommendation)


@router.get("/management-summary", response_model=schemas.AgenticManagementSummary)
def get_agentic_management_summary(db: Session = Depends(get_db)):
    """Return an executive-style summary of the recommendation portfolio."""
    recommendations = crud.get_recommendations(db, limit=500)
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Run POST /api/recommendations/run first.",
        )
    return build_management_summary(recommendations)


@router.get("/action-plan", response_model=schemas.AgenticActionPlan)
def get_agentic_action_plan(
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Return a ranked action plan grouped into review and implementation phases."""
    recommendations = crud.get_recommendations(db, limit=500)
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Run POST /api/recommendations/run first.",
        )
    return build_action_plan(recommendations, limit=limit)
