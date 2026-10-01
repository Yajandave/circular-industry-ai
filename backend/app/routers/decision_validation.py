"""Circular decision-quality validation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.blind_decision_review import CASE_MAP, build_blind_review_pack
from app.decision_validation import list_decision_validation_cases, run_decision_validation
from app.grounded_decision_validation import list_grounded_challenge_cases, run_grounded_challenge_validation

router = APIRouter(prefix="/api/decision-validation", tags=["decision validation"])


@router.get("/cases", response_model=list[schemas.DecisionValidationCaseDefinition])
def get_decision_validation_cases() -> list[schemas.DecisionValidationCaseDefinition]:
    """Return internal benchmark case definitions."""
    return list_decision_validation_cases()


@router.post("/run", response_model=schemas.DecisionValidationRunResult)
def run_decision_validation_suite(
    request: schemas.DecisionValidationRunRequest,
) -> schemas.DecisionValidationRunResult:
    """Run selected or all internal circular-decision benchmark cases."""
    return run_decision_validation(case_ids=request.case_ids)


@router.get("/summary", response_model=schemas.DecisionValidationRunResult)
def decision_validation_summary() -> schemas.DecisionValidationRunResult:
    """Run the full internal decision benchmark."""
    return run_decision_validation()



@router.get(
    "/challenge-cases",
    response_model=list[schemas.GroundedChallengeCaseDefinition],
)
def get_grounded_challenge_cases() -> list[schemas.GroundedChallengeCaseDefinition]:
    """Return externally grounded challenge case definitions."""
    return list_grounded_challenge_cases()


@router.post(
    "/challenge-run",
    response_model=schemas.GroundedChallengeRunResult,
)
def run_grounded_challenge_suite(
    request: schemas.GroundedChallengeRunRequest,
) -> schemas.GroundedChallengeRunResult:
    """Run selected or all externally grounded circular-decision challenges."""
    return run_grounded_challenge_validation(case_ids=request.case_ids)


@router.get(
    "/challenge-summary",
    response_model=schemas.GroundedChallengeRunResult,
)
def grounded_challenge_summary() -> schemas.GroundedChallengeRunResult:
    """Run the full externally grounded challenge suite."""
    return run_grounded_challenge_validation()



@router.get(
    "/blind-review-pack",
    response_model=list[schemas.BlindDecisionReviewCase],
)
def get_blind_review_pack() -> list[schemas.BlindDecisionReviewCase]:
    """Return reviewer-facing case data with system answers and labels withheld."""
    return build_blind_review_pack()


@router.post(
    "/blind-review-submit",
    response_model=schemas.BlindDecisionReviewBatchResult,
)
def submit_blind_decision_review(
    payload: schemas.BlindDecisionReviewBatchCreate,
    db: Session = Depends(get_db),
) -> schemas.BlindDecisionReviewBatchResult:
    """Persist a blind reviewer batch and compare against contemporaneous system outputs."""

    if not payload.reviewer_declared_blind:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blind-review submission requires the reviewer to declare that Circular Industry AI outputs were not viewed before judgement.",
        )
    if not payload.reviewer_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewer name must contain non-whitespace characters.",
        )
    if not payload.reviewer_role.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewer role must contain non-whitespace characters.",
        )

    case_ids = [label.case_id for label in payload.labels]
    if len(set(case_ids)) != len(case_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A blind-review batch may contain only one label per case.",
        )

    unknown_case_ids = sorted(case_id for case_id in case_ids if case_id not in CASE_MAP)
    if unknown_case_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown blind-review case IDs: {', '.join(unknown_case_ids)}",
        )

    if any(not label.reasoning.strip() for label in payload.labels):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Each reviewer label requires non-whitespace reasoning.",
        )
    if any(not label.strategy_category.strip() for label in payload.labels):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Each reviewer label requires a non-whitespace strategy category.",
        )

    result = crud.create_blind_decision_review_batch(db, payload=payload)

    crud.create_audit_event(
        db,
        event_type="blind_decision_review_submitted",
        entity_type="blind_decision_review_batch",
        entity_id=result.submission_batch_id,
        actor_type="external_reviewer",
        actor_id=result.reviewer_name,
        source="decision_validation_router",
        action="submit_blind_decision_review",
        summary=(
            f"Stored {result.total_labels} blind reviewer labels from {result.reviewer_name} "
            f"with {result.full_agreement_count} full decision matches."
        ),
        decision_source="blind_external_review",
        claim_boundary=(
            "This records reviewer-versus-system agreement. It does not establish independent expert validation "
            "unless reviewer independence, competence and blind conditions are separately documented."
        ),
        metadata={
            "reviewer_name": result.reviewer_name,
            "reviewer_role": result.reviewer_role,
            "reviewer_organisation": result.reviewer_organisation,
            "reviewer_declared_blind": result.reviewer_declared_blind,
            "total_labels": result.total_labels,
            "strategy_agreement_pct": result.strategy_agreement_pct,
            "risk_agreement_pct": result.risk_agreement_pct,
            "human_review_agreement_pct": result.human_review_agreement_pct,
            "full_agreement_pct": result.full_agreement_pct,
            "case_ids": case_ids,
        },
    )

    return result


@router.get(
    "/blind-review-history",
    response_model=schemas.BlindDecisionReviewHistory,
)
def blind_decision_review_history(
    limit: int = 500,
    db: Session = Depends(get_db),
) -> schemas.BlindDecisionReviewHistory:
    """Return immutable stored blind-review comparisons."""
    return crud.get_blind_decision_review_history(
        db,
        limit=max(1, min(limit, 2000)),
    )
