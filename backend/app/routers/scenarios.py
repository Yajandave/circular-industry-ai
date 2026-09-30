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
