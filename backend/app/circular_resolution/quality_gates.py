"""Quality gates for circular resolution plans."""

from __future__ import annotations

from app import models


def claim_boundary_for(recommendation: models.CircularRecommendation) -> str:
    """Return a consistent anti-greenwashing boundary for a resolution plan."""
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return (
            "Not claim-ready. This stream is a controlled review item. Do not claim circular impact, diversion, "
            "cost saving, recovery, compliance or carbon benefit until classification, contamination, authorised route "
            "and evidence gates are resolved."
        )
    if recommendation.evidence_quality_score < 70:
        return (
            "Not claim-ready. The recommendation may support internal screening, but evidence gaps remain. Do not use "
            "external circularity, diversion, cost-saving or carbon claims until missing evidence is closed."
        )
    return (
        "Internal screening only. The plan can be used to design a pilot or supplier discussion, but verified circular "
        "impact should only be claimed after implementation records, supplier/contractor evidence and measurement data exist."
    )


def decision_gates_for(stream: models.IndustrialStream, recommendation: models.CircularRecommendation) -> list[str]:
    """Build decision gates that must be cleared before implementation/claims."""
    gates: list[str] = []
    hazard = (stream.hazardous_flag or "").lower()
    contamination = (stream.contamination_risk or "").lower()

    if hazard == "true":
        gates.append("EHS or competent environmental compliance review before any circular route is proposed")
    if hazard == "unknown":
        gates.append("confirm hazardous/non-hazardous classification before route selection")
    if contamination == "high":
        gates.append("obtain contamination assessment and route-specific acceptance criteria")
    if recommendation.risk_level == "blocked":
        gates.append("blocked-risk gate: do not proceed beyond screening until classification and authorised handling are confirmed")
    if recommendation.evidence_quality_score < 70:
        gates.append("evidence maturity gate: close material, route or supplier evidence gaps before implementation")
    if recommendation.estimated_annual_waste_diverted_kg == 0 and "energy" not in (stream.material or "").lower():
        gates.append("measurement gate: confirm baseline quantity before diversion or value-retention claims")
    if not gates:
        gates.append("pilot validation gate: confirm route acceptance, records and measurement before claims")
    return gates


def route_strength(recommendation: models.CircularRecommendation) -> str:
    """Classify the strength of the proposed circular route."""
    category = (recommendation.circular_strategy_category or "").lower()
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "controlled review only"
    if "reduce" in category:
        return "high: prevention or reduction route"
    if "internal reuse" in category or "supplier take-back" in category:
        return "high: reuse or reverse-logistics loop"
    if "industrial symbiosis" in category:
        return "medium-high: by-product valorisation screening"
    if "closed-loop" in category:
        return "medium-high: material quality retention route"
    if "open-loop" in category:
        return "medium: lower-value recycling or specialist recovery"
    return "low-medium: evidence improvement or compliant fallback route"


def confidence_notes(stream: models.IndustrialStream, recommendation: models.CircularRecommendation) -> str:
    """Explain why a resolution plan is strong or weak."""
    if recommendation.human_review_required:
        return (
            f"Confidence is constrained because the stream is {recommendation.risk_level} risk and requires human review. "
            "The plan should be treated as a controlled evidence-gathering workflow, not an implementation recommendation."
        )
    if recommendation.evidence_quality_score >= 85 and recommendation.confidence_score >= 85:
        return (
            "The screening signal is strong because the rules engine found a low-risk route with strong evidence maturity. "
            "The next step is validation through pilot records and supplier/contractor confirmation."
        )
    if recommendation.evidence_quality_score < 70:
        return (
            "The route is only a weak screening candidate because evidence quality is below the preferred threshold. "
            "Improve material, route and supplier evidence before implementation."
        )
    return (
        "The route is a moderate screening candidate. It needs targeted evidence checks before implementation or any external claim."
    )
