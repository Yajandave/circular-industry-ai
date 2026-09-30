"""Intervention scenario screening endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.intervention_scenario import build_intervention_scenario

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
