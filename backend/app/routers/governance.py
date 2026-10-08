"""Governance, provenance and human-challenge endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.evidence_governance import evidence_source_policy
from app.review_governance import build_review_governance
from app.rule_provenance import get_rule_provenance, list_rule_provenance


router = APIRouter(prefix="/api/governance", tags=["governance and provenance"])


@router.get("/evidence-policy", response_model=schemas.EvidenceGovernancePolicy)
def evidence_policy() -> dict:
    """Return the current evidence-source hierarchy and its limitations."""
    return evidence_source_policy()


@router.get("/rules", response_model=list[schemas.RuleProvenanceRecord])
def rule_provenance_catalogue() -> list[dict]:
    """Return provenance for every deterministic rule family."""
    return list_rule_provenance()


@router.get("/rules/{rule_id}", response_model=schemas.RuleProvenanceRecord)
def rule_provenance(rule_id: str) -> dict:
    """Return the public/internal basis of one deterministic rule."""
    result = get_rule_provenance(rule_id)
    if result["provenance_status"] == "provenance_not_registered":
        raise HTTPException(status_code=404, detail=f"No provenance registered for rule {rule_id}.")
    return result


@router.get("/review-profile/{stream_id}", response_model=schemas.ReviewGovernanceRecord)
def review_profile(stream_id: str, db: Session = Depends(get_db)) -> dict:
    """Return competence-routing guidance for one current recommendation."""
    stream = crud.get_stream_by_stream_id(db, stream_id)
    if stream is None:
        raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found.")

    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)
    if recommendation is None:
        raise HTTPException(
            status_code=404,
            detail="No recommendation found. Run POST /api/recommendations/run first.",
        )

    return build_review_governance(stream, recommendation)


@router.post(
    "/decision-challenges/{stream_id}",
    response_model=schemas.DecisionChallengeRead,
)
def record_decision_challenge(
    stream_id: str,
    payload: schemas.DecisionChallengeCreate,
    db: Session = Depends(get_db),
) -> schemas.DecisionChallengeRead:
    """Record human disagreement without overriding the locked decision."""
    stream = crud.get_stream_by_stream_id(db, stream_id)
    if stream is None:
        raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found.")

    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)
    if recommendation is None:
        raise HTTPException(
            status_code=404,
            detail="No recommendation found. Run POST /api/recommendations/run first.",
        )

    return crud.create_decision_challenge(
        db,
        stream=stream,
        recommendation=recommendation,
        payload=payload,
    )


@router.get(
    "/decision-challenges/{stream_id}",
    response_model=schemas.DecisionChallengeHistory,
)
def decision_challenge_history(
    stream_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> schemas.DecisionChallengeHistory:
    """Return immutable human disagreement records for one stream."""
    stream = crud.get_stream_by_stream_id(db, stream_id)
    if stream is None:
        raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found.")
    return crud.get_decision_challenges(db, stream_id=stream_id, limit=limit)
