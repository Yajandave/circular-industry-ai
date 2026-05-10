"""Evaluation endpoints for retrieval and insight quality."""

from __future__ import annotations

from fastapi import APIRouter

from app import schemas
from app.evaluation.service import list_evaluation_cases, run_evaluation_suite

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/cases", response_model=list[schemas.EvaluationCaseDefinition])
def get_evaluation_cases() -> list[schemas.EvaluationCaseDefinition]:
    """Return deterministic evaluation case definitions."""
    return list_evaluation_cases()


@router.post("/run", response_model=schemas.EvaluationRunResult)
def run_evaluation(request: schemas.EvaluationRunRequest) -> schemas.EvaluationRunResult:
    """Run selected or all evaluation cases."""
    return run_evaluation_suite(case_ids=request.case_ids)


@router.get("/summary", response_model=schemas.EvaluationRunResult)
def evaluation_summary() -> schemas.EvaluationRunResult:
    """Run all evaluation cases and return the quality summary."""
    return run_evaluation_suite()
