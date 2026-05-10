"""API routes for rules-based circular economy recommendations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.rules_engine import recommend_for_streams

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.post("/run", response_model=schemas.RunRecommendationsResponse)
def run_recommendations(db: Session = Depends(get_db)) -> schemas.RunRecommendationsResponse:
    """Run the deterministic circular recommendation engine for all loaded streams."""
    streams = crud.get_streams(db, limit=500)
    if not streams:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No industrial streams found. Run POST /api/streams/load-sample first.",
        )

    recommendations = [
        schemas.CircularRecommendationCreate(**rec.__dict__)
        for rec in recommend_for_streams(streams)
    ]
    created_count = crud.bulk_replace_recommendations(db, recommendations)
    crud.create_audit_event(
        db,
        event_type="rules_engine_run",
        entity_type="recommendation_run",
        entity_id="latest",
        actor_type="system",
        actor_id="rules_engine",
        source="recommendations_router",
        action="run_locked_rules_engine",
        summary=f"Generated {created_count} locked circular economy recommendations.",
        decision_source="locked_rules_engine",
        claim_boundary="Rules-engine outputs are screening recommendations, not verified circularity, cost or environmental impact claims.",
        metadata={
            "analysed_streams": len(streams),
            "recommendations_created": created_count,
        },
    )
    human_review_count = sum(1 for rec in recommendations if rec.human_review_required)
    high_priority_count = sum(
        1 for rec in recommendations if rec.dashboard_priority.lower().startswith("high")
    )

    return schemas.RunRecommendationsResponse(
        analysed_streams=len(streams),
        recommendations_created=created_count,
        human_review_required=human_review_count,
        high_priority_items=high_priority_count,
        message="Rules-based circular economy recommendations generated.",
    )


@router.get("", response_model=list[schemas.CircularRecommendationRead])
def list_recommendations(
    risk_level: str | None = Query(default=None),
    circular_strategy_category: str | None = Query(default=None),
    human_review_required: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.CircularRecommendationRead]:
    """Return generated circular economy recommendations with basic filters."""
    return crud.get_recommendations(
        db,
        risk_level=risk_level,
        circular_strategy_category=circular_strategy_category,
        human_review_required=human_review_required,
        skip=skip,
        limit=limit,
    )


@router.get("/summary", response_model=schemas.RecommendationSummary)
def recommendation_summary(db: Session = Depends(get_db)) -> schemas.RecommendationSummary:
    """Return summary metrics for the latest rules-based recommendation run."""
    return crud.get_recommendation_summary(db)


@router.get("/{stream_id}", response_model=schemas.CircularRecommendationRead)
def get_recommendation(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.CircularRecommendationRead:
    """Return one generated recommendation by stream ID, such as S001."""
    recommendation = crud.get_recommendation_by_stream_id(db, stream_id=stream_id)
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation not found for stream: {stream_id}. Run POST /api/recommendations/run first.",
        )
    return recommendation

