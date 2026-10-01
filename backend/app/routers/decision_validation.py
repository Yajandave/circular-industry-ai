"""Circular decision-quality validation endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app import schemas
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
