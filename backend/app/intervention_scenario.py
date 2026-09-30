"""Deterministic intervention scenario screening.

Milestone 20B separates baseline stream exposure from a user-supplied intervention
scenario. The calculations are deliberately simple and transparent. They do not
represent measured diversion, verified recovery, financial savings or completed
environmental impact.
"""

from __future__ import annotations

from typing import Protocol


class ScenarioStreamLike(Protocol):
    stream_id: str
    stream_name: str
    material: str
    monthly_quantity_kg: float
    disposal_cost_per_month: float


class ScenarioRecommendationLike(Protocol):
    recommended_circular_action: str
    risk_level: str
    confidence_score: int
    evidence_quality_score: int
    missing_data: str
    human_review_required: bool


def _fraction(percent: float) -> float:
    return max(0.0, min(float(percent), 100.0)) / 100.0


def _evidence_needed(recommendation: ScenarioRecommendationLike) -> list[str]:
    items: list[str] = []
    raw_missing = str(recommendation.missing_data or "").strip()

    if raw_missing and raw_missing.lower() not in {
        "none",
        "none recorded",
        "none identified for mvp fields",
    }:
        items.extend(
            item.strip()
            for item in raw_missing.split(";")
            if item.strip()
        )

    items.extend(
        [
            "site evidence supporting the addressable fraction",
            "pilot or technical evidence supporting the capture rate",
            "route or supplier acceptance evidence supporting the acceptance rate",
        ]
    )

    # Stable de-duplication keeps API output predictable.
    return list(dict.fromkeys(items))


def build_intervention_scenario(
    stream: ScenarioStreamLike,
    recommendation: ScenarioRecommendationLike,
    *,
    addressable_fraction_pct: float,
    technical_capture_rate_pct: float,
    route_acceptance_rate_pct: float,
    operator_note: str | None = None,
) -> dict:
    """Build one transparent screening scenario from a loaded stream.

    Formula:
        annual stream quantity
        × addressable fraction
        × technical capture rate
        × route acceptance rate

    The result is scenario-screened recoverable quantity, not achieved diversion.
    """

    annual_quantity = round(max(float(stream.monthly_quantity_kg or 0), 0.0) * 12, 2)
    annual_cost_exposure = round(max(float(stream.disposal_cost_per_month or 0), 0.0) * 12, 2)

    addressable = _fraction(addressable_fraction_pct)
    capture = _fraction(technical_capture_rate_pct)
    acceptance = _fraction(route_acceptance_rate_pct)
    screened_fraction = addressable * capture * acceptance
    recoverable_quantity = round(annual_quantity * screened_fraction, 2)

    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        scenario_status = "controlled_review_required"
    elif recommendation.evidence_quality_score < 70:
        scenario_status = "evidence_improvement_required"
    else:
        scenario_status = "screening_ready"

    assumptions = [
        f"{float(addressable_fraction_pct):g}% of the annual stream is assumed addressable by the candidate intervention.",
        f"{float(technical_capture_rate_pct):g}% of addressable material is assumed technically capturable.",
        f"{float(route_acceptance_rate_pct):g}% of captured material is assumed accepted by the candidate route.",
    ]
    if operator_note and operator_note.strip():
        assumptions.append(f"Operator note: {operator_note.strip()}")

    return {
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "material": stream.material,
        "candidate_route": recommendation.recommended_circular_action,
        "baseline_annual_quantity_kg": annual_quantity,
        "baseline_annual_disposal_cost_exposure": annual_cost_exposure,
        "addressable_fraction_pct": round(float(addressable_fraction_pct), 2),
        "technical_capture_rate_pct": round(float(technical_capture_rate_pct), 2),
        "route_acceptance_rate_pct": round(float(route_acceptance_rate_pct), 2),
        "scenario_screened_fraction_pct": round(screened_fraction * 100, 2),
        "scenario_screened_recoverable_quantity_kg": recoverable_quantity,
        "recommendation_confidence_score": int(recommendation.confidence_score),
        "evidence_quality_score": int(recommendation.evidence_quality_score),
        "risk_level": recommendation.risk_level,
        "human_review_required": bool(recommendation.human_review_required),
        "scenario_status": scenario_status,
        "claim_status": "screening_only_not_claim_ready",
        "assumptions": assumptions,
        "evidence_needed": _evidence_needed(recommendation),
        "formula": (
            "annual_stream_quantity_kg × addressable_fraction × "
            "technical_capture_rate × route_acceptance_rate"
        ),
        "governance_note": (
            "This is a screening scenario based on operator-supplied assumptions. "
            "The recoverable quantity is not measured diversion, verified recovery, "
            "financial savings or completed environmental impact. Baseline disposal cost "
            "is shown only as current exposure and is not converted into scenario savings."
        ),
    }



def build_intervention_scenario_comparison(
    stream: ScenarioStreamLike,
    recommendation: ScenarioRecommendationLike,
    *,
    cases: list[dict],
) -> dict:
    """Build a bounded comparison of explicit operator scenario cases."""

    case_results: list[dict] = []
    for case in cases:
        scenario = build_intervention_scenario(
            stream,
            recommendation,
            addressable_fraction_pct=case["addressable_fraction_pct"],
            technical_capture_rate_pct=case["technical_capture_rate_pct"],
            route_acceptance_rate_pct=case["route_acceptance_rate_pct"],
            operator_note=case.get("operator_note"),
        )
        case_results.append(
            {
                "case_name": str(case["case_name"]).strip(),
                "scenario": scenario,
            }
        )

    quantities = [
        item["scenario"]["scenario_screened_recoverable_quantity_kg"]
        for item in case_results
    ]
    minimum_quantity = round(min(quantities), 2)
    maximum_quantity = round(max(quantities), 2)

    first = case_results[0]["scenario"]
    return {
        "stream_id": first["stream_id"],
        "stream_name": first["stream_name"],
        "material": first["material"],
        "candidate_route": first["candidate_route"],
        "baseline_annual_quantity_kg": first["baseline_annual_quantity_kg"],
        "baseline_annual_disposal_cost_exposure": first["baseline_annual_disposal_cost_exposure"],
        "minimum_screened_recoverable_quantity_kg": minimum_quantity,
        "maximum_screened_recoverable_quantity_kg": maximum_quantity,
        "screened_quantity_range_kg": round(maximum_quantity - minimum_quantity, 2),
        "cases": case_results,
        "claim_status": "screening_comparison_only_not_claim_ready",
        "governance_note": (
            "This comparison shows the sensitivity of screened recoverable quantity to explicit "
            "operator assumptions. It is not a probability forecast, achieved diversion, verified "
            "recovery, financial savings or completed environmental impact. No case is selected "
            "or endorsed by the system."
        ),
    }
