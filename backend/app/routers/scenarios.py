"""Intervention scenario screening endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.intervention_scenario import build_intervention_scenario, build_intervention_scenario_comparison

router = APIRouter(prefix="/api/scenarios", tags=["intervention scenarios"])


@router.post("/{stream_id}/screen", response_model=schemas.InterventionScenarioResult)
def screen_intervention_scenario(
    stream_id: str,
    payload: schemas.InterventionScenarioRequest,
    db: Session = Depends(get_db),
) -> schemas.InterventionScenarioResult:
    """Screen one intervention scenario using explicit operator assumptions."""

    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    recommendation = crud.get_recommendation_by_stream_id(db, stream_id=stream_id)
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No locked recommendation found for stream {stream_id}. "
                "Run POST /api/recommendations/run before screening an intervention scenario."
            ),
        )

    scenario = build_intervention_scenario(
        stream,
        recommendation,
        addressable_fraction_pct=payload.addressable_fraction_pct,
        technical_capture_rate_pct=payload.technical_capture_rate_pct,
        route_acceptance_rate_pct=payload.route_acceptance_rate_pct,
        operator_note=payload.operator_note,
    )

    crud.create_audit_event(
        db,
        event_type="intervention_scenario_screened",
        entity_type="industrial_stream",
        entity_id=stream_id,
        actor_type="operator",
        actor_id="local_user",
        source="intervention_scenario_router",
        action="screen_intervention_scenario",
        summary=(
            f"Screened intervention scenario for {stream_id} using explicit addressable, "
            "capture and route-acceptance assumptions."
        ),
        decision_source="operator_assumption_scenario",
        claim_boundary=(
            "Scenario outputs are screening estimates only. They do not verify diversion, "
            "recovery, savings or environmental impact."
        ),
        metadata={
            "candidate_route": scenario["candidate_route"],
            "addressable_fraction_pct": scenario["addressable_fraction_pct"],
            "technical_capture_rate_pct": scenario["technical_capture_rate_pct"],
            "route_acceptance_rate_pct": scenario["route_acceptance_rate_pct"],
            "baseline_annual_quantity_kg": scenario["baseline_annual_quantity_kg"],
            "baseline_annual_disposal_cost_exposure": scenario["baseline_annual_disposal_cost_exposure"],
            "scenario_screened_recoverable_quantity_kg": scenario["scenario_screened_recoverable_quantity_kg"],
            "scenario_status": scenario["scenario_status"],
            "claim_status": scenario["claim_status"],
        },
    )

    return schemas.InterventionScenarioResult(**scenario)



@router.post("/{stream_id}/compare", response_model=schemas.InterventionScenarioComparisonResult)
def compare_intervention_scenarios(
    stream_id: str,
    payload: schemas.InterventionScenarioComparisonRequest,
    db: Session = Depends(get_db),
) -> schemas.InterventionScenarioComparisonResult:
    """Compare multiple explicit screening cases for one locked recommendation."""

    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    recommendation = crud.get_recommendation_by_stream_id(db, stream_id=stream_id)
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No locked recommendation found for stream {stream_id}. "
                "Run POST /api/recommendations/run before comparing intervention scenarios."
            ),
        )

    names = [case.case_name.strip() for case in payload.cases]
    if len(set(name.lower() for name in names)) != len(names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scenario comparison case names must be unique.",
        )

    comparison = build_intervention_scenario_comparison(
        stream,
        recommendation,
        cases=[case.model_dump() for case in payload.cases],
    )

    crud.create_audit_event(
        db,
        event_type="intervention_scenarios_compared",
        entity_type="industrial_stream",
        entity_id=stream_id,
        actor_type="operator",
        actor_id="local_user",
        source="intervention_scenario_router",
        action="compare_intervention_scenarios",
        summary=(
            f"Compared {len(payload.cases)} intervention screening cases for {stream_id} "
            "using explicit operator assumptions."
        ),
        decision_source="operator_assumption_scenario_comparison",
        claim_boundary=(
            "Scenario comparison outputs are screening estimates only and do not select a preferred case, "
            "verify diversion, recovery, savings or environmental impact."
        ),
        metadata={
            "candidate_route": comparison["candidate_route"],
            "case_names": names,
            "case_count": len(payload.cases),
            "baseline_annual_quantity_kg": comparison["baseline_annual_quantity_kg"],
            "minimum_screened_recoverable_quantity_kg": comparison["minimum_screened_recoverable_quantity_kg"],
            "maximum_screened_recoverable_quantity_kg": comparison["maximum_screened_recoverable_quantity_kg"],
            "screened_quantity_range_kg": comparison["screened_quantity_range_kg"],
            "claim_status": comparison["claim_status"],
            "cases": [
                {
                    "case_name": item["case_name"],
                    "addressable_fraction_pct": item["scenario"]["addressable_fraction_pct"],
                    "technical_capture_rate_pct": item["scenario"]["technical_capture_rate_pct"],
                    "route_acceptance_rate_pct": item["scenario"]["route_acceptance_rate_pct"],
                    "scenario_screened_recoverable_quantity_kg": item["scenario"]["scenario_screened_recoverable_quantity_kg"],
                    "scenario_status": item["scenario"]["scenario_status"],
                }
                for item in comparison["cases"]
            ],
        },
    )

    return schemas.InterventionScenarioComparisonResult(**comparison)



@router.post("/{stream_id}/save", response_model=schemas.SavedInterventionScenarioRead)
def save_intervention_scenario_revision(
    stream_id: str,
    payload: schemas.SaveInterventionScenarioRequest,
    db: Session = Depends(get_db),
) -> schemas.SavedInterventionScenarioRead:
    """Recalculate and persist one immutable named scenario revision."""

    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    recommendation = crud.get_recommendation_by_stream_id(db, stream_id=stream_id)
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No locked recommendation found for stream {stream_id}. "
                "Run POST /api/recommendations/run before saving an intervention scenario."
            ),
        )

    if not payload.scenario_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scenario name must contain non-whitespace characters.",
        )

    if payload.lifecycle_stage in {"pilot_observed", "measured_unverified"} and not (
        payload.operator_note and payload.operator_note.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pilot-observed and measured-unverified revisions require an operator note describing the evidence basis.",
        )

    scenario = build_intervention_scenario(
        stream,
        recommendation,
        addressable_fraction_pct=payload.addressable_fraction_pct,
        technical_capture_rate_pct=payload.technical_capture_rate_pct,
        route_acceptance_rate_pct=payload.route_acceptance_rate_pct,
        operator_note=payload.operator_note,
    )

    saved = crud.save_intervention_scenario(
        db,
        scenario_name=payload.scenario_name,
        lifecycle_stage=payload.lifecycle_stage,
        operator_note=payload.operator_note,
        scenario=scenario,
    )

    crud.create_audit_event(
        db,
        event_type="intervention_scenario_saved",
        entity_type="saved_intervention_scenario",
        entity_id=str(saved.id),
        actor_type="operator",
        actor_id="local_user",
        source="intervention_scenario_router",
        action="save_intervention_scenario_revision",
        summary=(
            f"Saved scenario '{saved.scenario_name}' revision {saved.revision_number} "
            f"for {stream_id} at lifecycle stage {saved.lifecycle_stage}."
        ),
        decision_source="operator_saved_scenario",
        claim_boundary=(
            "Saved scenario revisions preserve screening assumptions and workflow stage only. "
            "They do not verify diversion, recovery, savings or environmental impact."
        ),
        metadata={
            "stream_id": saved.stream_id,
            "scenario_name": saved.scenario_name,
            "revision_number": saved.revision_number,
            "lifecycle_stage": saved.lifecycle_stage,
            "scenario_screened_recoverable_quantity_kg": saved.scenario_screened_recoverable_quantity_kg,
            "scenario_status": saved.scenario_status,
            "claim_status": saved.claim_status,
        },
    )

    return saved


@router.get("/{stream_id}/history", response_model=schemas.SavedInterventionScenarioHistory)
def intervention_scenario_history(
    stream_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> schemas.SavedInterventionScenarioHistory:
    """Return immutable saved scenario revisions for one stream."""

    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    return crud.get_saved_intervention_scenario_history(
        db,
        stream_id=stream_id,
        limit=max(1, min(limit, 500)),
    )



@router.post(
    "/saved/{saved_scenario_id}/outcomes",
    response_model=schemas.ObservedScenarioOutcomeRead,
)
def create_observed_outcome(
    saved_scenario_id: int,
    payload: schemas.ObservedScenarioOutcomeCreate,
    db: Session = Depends(get_db),
) -> schemas.ObservedScenarioOutcomeRead:
    """Record observed pilot/outcome evidence against one saved scenario revision."""

    saved_scenario = crud.get_saved_intervention_scenario_by_id(
        db,
        saved_scenario_id=saved_scenario_id,
    )
    if saved_scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved intervention scenario not found: {saved_scenario_id}",
        )

    if payload.observation_end_date < payload.observation_start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Observation end date must be on or after the start date.",
        )

    if not payload.evidence_reference.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evidence reference must contain non-whitespace characters.",
        )

    outcome = crud.create_observed_scenario_outcome(
        db,
        saved_scenario=saved_scenario,
        payload=payload,
    )

    crud.create_audit_event(
        db,
        event_type="observed_scenario_outcome_recorded",
        entity_type="observed_scenario_outcome",
        entity_id=str(outcome.id),
        actor_type="operator",
        actor_id="local_user",
        source="intervention_scenario_router",
        action="create_observed_outcome",
        summary=(
            f"Recorded observed outcome evidence for scenario '{outcome.scenario_name}' "
            f"revision {outcome.scenario_revision_number}."
        ),
        decision_source="operator_observed_outcome",
        claim_boundary=(
            "Observed outcome records remain non-claim-ready until a later evidence-verification process. "
            "Variance against the saved scenario is not proof of causal intervention impact."
        ),
        metadata={
            "saved_scenario_id": outcome.saved_scenario_id,
            "stream_id": outcome.stream_id,
            "scenario_name": outcome.scenario_name,
            "scenario_revision_number": outcome.scenario_revision_number,
            "observation_start_date": str(outcome.observation_start_date),
            "observation_end_date": str(outcome.observation_end_date),
            "observation_period_days": outcome.observation_period_days,
            "observed_recovered_quantity_kg": outcome.observed_recovered_quantity_kg,
            "scenario_screened_quantity_for_period_kg": outcome.scenario_screened_quantity_for_period_kg,
            "variance_quantity_kg": outcome.variance_quantity_kg,
            "variance_pct": outcome.variance_pct,
            "evidence_source_type": outcome.evidence_source_type,
            "verification_status": outcome.verification_status,
            "claim_status": outcome.claim_status,
        },
    )

    return outcome


@router.get(
    "/saved/{saved_scenario_id}/outcomes",
    response_model=schemas.ObservedScenarioOutcomeHistory,
)
def observed_outcome_history(
    saved_scenario_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> schemas.ObservedScenarioOutcomeHistory:
    """Return observed outcome evidence history for one saved scenario revision."""

    saved_scenario = crud.get_saved_intervention_scenario_by_id(
        db,
        saved_scenario_id=saved_scenario_id,
    )
    if saved_scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved intervention scenario not found: {saved_scenario_id}",
        )

    return crud.get_observed_scenario_outcome_history(
        db,
        saved_scenario=saved_scenario,
        limit=max(1, min(limit, 500)),
    )



@router.post(
    "/outcomes/{observed_outcome_id}/reviews",
    response_model=schemas.ObservedOutcomeEvidenceReviewRead,
)
def create_observed_outcome_evidence_review(
    observed_outcome_id: int,
    payload: schemas.ObservedOutcomeEvidenceReviewCreate,
    db: Session = Depends(get_db),
) -> schemas.ObservedOutcomeEvidenceReviewRead:
    """Record one immutable internal evidence review for an observed outcome."""

    outcome = crud.get_observed_scenario_outcome_by_id(
        db,
        observed_outcome_id=observed_outcome_id,
    )
    if outcome is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observed scenario outcome not found: {observed_outcome_id}",
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
    if not payload.review_note.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review note must contain non-whitespace characters.",
        )

    review = crud.create_observed_outcome_evidence_review(
        db,
        outcome=outcome,
        payload=payload,
    )

    crud.create_audit_event(
        db,
        event_type="observed_outcome_evidence_reviewed",
        entity_type="observed_outcome_evidence_review",
        entity_id=str(review.id),
        actor_type="operator",
        actor_id="local_user",
        source="intervention_scenario_router",
        action="create_observed_outcome_evidence_review",
        summary=(
            f"Recorded internal evidence review for observed outcome {observed_outcome_id}: "
            f"{review.verification_decision}."
        ),
        decision_source="deterministic_evidence_verification_gate",
        claim_boundary=(
            "Evidence-review outputs support internal factual reporting only when the gate passes. "
            "External claims remain blocked pending a separate verification process."
        ),
        metadata={
            "observed_outcome_id": review.observed_outcome_id,
            "saved_scenario_id": review.saved_scenario_id,
            "stream_id": review.stream_id,
            "reviewer_name": review.reviewer_name,
            "reviewer_role": review.reviewer_role,
            "evidence_completeness": review.evidence_completeness,
            "source_traceability_confirmed": review.source_traceability_confirmed,
            "quantity_basis_confirmed": review.quantity_basis_confirmed,
            "period_basis_confirmed": review.period_basis_confirmed,
            "route_destination_confirmed": review.route_destination_confirmed,
            "verification_decision": review.verification_decision,
            "internal_claim_readiness": review.internal_claim_readiness,
            "external_claim_readiness": review.external_claim_readiness,
            "allowed_internal_statement": review.allowed_internal_statement,
            "missing_checks": review.missing_checks,
        },
    )

    return review


@router.get(
    "/outcomes/{observed_outcome_id}/reviews",
    response_model=schemas.ObservedOutcomeEvidenceReviewHistory,
)
def observed_outcome_evidence_review_history(
    observed_outcome_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> schemas.ObservedOutcomeEvidenceReviewHistory:
    """Return immutable internal evidence reviews for one observed outcome."""

    outcome = crud.get_observed_scenario_outcome_by_id(
        db,
        observed_outcome_id=observed_outcome_id,
    )
    if outcome is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observed scenario outcome not found: {observed_outcome_id}",
        )

    return crud.get_observed_outcome_evidence_review_history(
        db,
        outcome=outcome,
        limit=max(1, min(limit, 500)),
    )
