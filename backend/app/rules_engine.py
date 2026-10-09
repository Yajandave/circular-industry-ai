"""Deterministic circular economy recommendation engine.

Milestone 3 deliberately uses rules before AI. The objective is to create
traceable first-pass recommendations that can later be explained by an AI layer
without allowing the AI to override risk or evidence constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.scoring import infer_contextual_safety_flags, score_stream


class StreamLike(Protocol):
    stream_id: str
    stream_name: str
    material: str
    source_process: str
    monthly_quantity_kg: float
    current_route: str
    disposal_cost_per_month: float
    contamination_risk: str
    hazardous_flag: str
    department: str
    supplier: str
    supplier_takeback_available: str
    recycled_content_available: str
    notes: str | None


@dataclass(frozen=True)
class RuleRecommendation:
    stream_id: str
    recommended_circular_action: str
    circular_strategy_category: str
    reasoning: str
    risk_level: str
    confidence_score: int
    evidence_quality_score: int
    missing_data: str
    human_review_required: bool
    estimated_annual_waste_diverted_kg: float
    estimated_annual_disposal_cost_avoided: float
    supplier_procurement_action: str
    industrial_symbiosis_opportunity: str
    next_action: str
    dashboard_priority: str
    rule_applied: str


def _clean(value: object) -> str:
    return str(value or "").strip().lower()


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _annual_material_quantity(stream: StreamLike) -> float:
    """Annualise the recorded stream quantity for screening.

    This is exposure/opportunity sizing only. It does not represent achieved
    diversion and remains available even when the circular route is blocked
    pending human review.
    """
    if stream.monthly_quantity_kg <= 0:
        return 0.0
    return round(stream.monthly_quantity_kg * 12, 2)


def _annual_disposal_cost_exposure(stream: StreamLike) -> float:
    """Annualise the recorded disposal cost for screening.

    This is the current cost exposure associated with the stream, not an
    estimate of savings or avoided cost.
    """
    if stream.disposal_cost_per_month <= 0:
        return 0.0
    return round(stream.disposal_cost_per_month * 12, 2)


def _priority(stream: StreamLike, risk_level: str, confidence_score: int, annual_cost: float) -> str:
    if risk_level in {"blocked", "high"}:
        return "high - review required"
    if annual_cost >= 5000 or stream.monthly_quantity_kg >= 1000:
        return "high"
    if confidence_score < 45:
        return "low - evidence weak"
    if annual_cost >= 1000 or stream.monthly_quantity_kg >= 250:
        return "medium"
    return "low"


def _supplier_action(stream: StreamLike, action: str) -> str:
    supplier = stream.supplier or "supplier"
    supplier_takeback = _clean(stream.supplier_takeback_available)
    recycled_content = _clean(stream.recycled_content_available)
    material = _clean(stream.material)

    if supplier_takeback == "yes":
        return f"Ask {supplier} to confirm take-back volumes, acceptance criteria and documentation."
    if "supplier" in action.lower() or material in {"cardboard/packaging", "wood/pallets", "metals", "plastics"}:
        return f"Request circular options from {supplier}, including take-back, recycled content and segregation requirements."
    if recycled_content == "yes":
        return f"Check whether {supplier} can provide recycled-content evidence or closed-loop material documentation."
    return "No immediate supplier action; confirm material data and current route first."


def _symbiosis_flag(material: str, action: str, risk_level: str) -> str:
    if risk_level in {"blocked", "high"}:
        return "no - risk review first"
    if "industrial symbiosis" in action.lower():
        return "yes"
    if material in {"organic/process residue", "process mineral residue", "process water", "energy/resource stream", "wood/pallets", "rubber", "glass"}:
        return "possible"
    return "not primary route"


def _base_decision(stream: StreamLike) -> tuple[str, str, str, str, str, int]:
    """Return action, category, reasoning, next_action, rule_id, rule_strength."""
    material = _clean(stream.material)
    name = _clean(stream.stream_name)
    source = _clean(stream.source_process)
    route = _clean(stream.current_route)
    contamination = _clean(stream.contamination_risk)
    hazardous = _clean(stream.hazardous_flag)
    takeback = _clean(stream.supplier_takeback_available)
    notes = _clean(stream.notes)
    text = " ".join([material, name, source, route, notes])
    contextual_flags = set(infer_contextual_safety_flags(stream))

    if "damaged_battery_condition" in contextual_flags:
        return (
            "Human review required for damaged battery handling and specialist route selection",
            "human review required",
            "The stream description indicates damaged battery condition. Damaged batteries can require specialist handling and should not receive a routine recycling or disposal recommendation from screening data alone.",
            "Confirm battery chemistry and condition, isolate the stream from routine mixed recycling, and obtain specialist handling, storage and authorised recovery guidance.",
            "R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
            20,
        )

    if "unresolved_weee_classification" in contextual_flags:
        return (
            "Human review required until WEEE classification is completed",
            "human review required",
            "The stream indicates unresolved WEEE hazardous-substance or POPs classification. A recovery route should not be treated as settled until the applicable classification and handling requirements are confirmed.",
            "Complete WEEE classification, confirm hazardous-substance and POPs status, then review authorised recovery options.",
            "R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
            20,
        )

    if "hazardous_residue_packaging" in contextual_flags:
        return (
            "Human review required for hazardous-residue packaging classification",
            "human review required",
            "The packaging description indicates contamination with hazardous residues. Routine reuse should not be recommended until the packaging classification, residue risk and authorised handling route are confirmed.",
            "Confirm the hazardous residue, classify the packaging stream, and obtain competent handling or recovery guidance before reuse or recycling.",
            "R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
            20,
        )

    if material in {"", "unknown", "unidentified", "unidentified composite", "not identified", "n/a", "unspecified"}:
        return (
            "Needs more information: material identification required",
            "human review required",
            "Material identity is not established. No circular recovery or disposal route can be confirmed from the supplied data.",
            "Identify composition and relevant classification, then obtain competent review before selecting or changing a route.",
            "R999_DEFAULT_EVIDENCE_IMPROVEMENT",
            8,
        )

    if hazardous not in {"true", "false"}:
        return (
            "Needs human review: hazardous status not confirmed",
            "human review required",
            "Hazardous status is missing or unresolved. A circular route cannot be supported before competent classification.",
            "Confirm hazardous classification and handling requirements before considering a recovery or reuse route.",
            "R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
            20,
        )

    if contamination not in {"low", "medium", "high"}:
        return (
            "Needs more information: contamination assessment required",
            "human review required",
            "Contamination is missing or unrecognised. Suitability for reuse, recycling or recovery cannot yet be established.",
            "Obtain contamination analysis and competent review before selecting or changing the treatment route.",
            "R002_HIGH_CONTAMINATION_REVIEW",
            16,
        )

    if hazardous == "true" or (hazardous == "unknown" and contamination in {"medium", "high", "unknown"}):
        return (
            "Human review required before circular route selection",
            "human review required",
            "Hazardous status, contamination or both create a compliance and safety constraint. The system should not recommend reuse, symbiosis or recycling until a competent person reviews the stream.",
            "Confirm hazardous classification, contamination profile, current legal route and authorised handling options.",
            "R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
            20,
        )

    if contamination == "high":
        return (
            "Compliant disposal or specialist recovery review",
            "compliant disposal / specialist recovery",
            "High contamination limits circular options. A specialist route may still recover value, but the current evidence is not strong enough for a direct circular recommendation.",
            "Obtain contamination data and ask a qualified waste or recovery contractor whether safe recovery is viable.",
            "R002_HIGH_CONTAMINATION_REVIEW",
            16,
        )

    edible_surplus = (
        material == "organic/process residue"
        and any(
            term in text
            for term in [
                "fit for human consumption",
                "still fit for consumption",
                "edible",
                "within use-by",
                "within use by",
            ]
        )
        and any(
            term in text
            for term in [
                "surplus",
                "overproduction",
                "over-production",
                "finished goods",
            ]
        )
    )
    if edible_surplus:
        return (
            "Prevent edible surplus or assess redistribution for human consumption before recovery",
            "reduce / process redesign",
            "The stream appears to be edible surplus rather than unavoidable food waste. Prevention and redistribution should be screened before anaerobic digestion, composting or other recovery routes.",
            "Confirm food-safety and date-status evidence, quantify the avoidable surplus, and assess redistribution or donation routes before sending material to recovery.",
            "R003_REDUCE_AT_SOURCE",
            18,
        )

    if _contains_any(text, ["excess", "over-order", "setup", "trim", "scrap reduction", "loss rate", "purge"]):
        return (
            "Reduce material use or redesign process to prevent scrap",
            "reduce / process redesign",
            "The stream appears linked to production setup, over-ordering, trimming or repeated process loss. Prevention should be tested before downstream recycling because it sits higher in the circular hierarchy.",
            "Review production settings, purchasing quantities, specification tolerances or setup losses before selecting a waste route.",
            "R003_REDUCE_AT_SOURCE",
            18,
        )

    if takeback == "yes" and material in {"cardboard/packaging", "wood/pallets", "metals", "plastics", "chemicals/solvents"}:
        return (
            "Supplier take-back or return loop review",
            "supplier take-back / circular procurement",
            "The stream is linked to a supplier and take-back is available. A supplier return loop may retain more value than open recycling or disposal.",
            "Confirm take-back terms, contamination limits, collection frequency and documentation with the supplier.",
            "R004_SUPPLIER_TAKEBACK_AVAILABLE",
            22,
        )

    if material == "metals" and contamination in {"low", "medium"}:
        return (
            "Closed-loop recycling review",
            "closed-loop recycling",
            "The metal stream has recoverable material value. If grades can be segregated and documented, closed-loop recycling is likely stronger than generic mixed scrap sale.",
            "Confirm grade segregation, contamination controls and whether the supplier or recycler can provide a closed-loop route.",
            "R005_METAL_CLOSED_LOOP",
            21,
        )

    if material in {"cardboard/packaging", "wood/pallets"} and contamination == "low":
        return (
            "Internal reuse or returnable packaging review",
            "internal reuse / returnable packaging",
            "Low-contamination packaging or pallet streams are often suitable for reuse, returnable logistics or supplier packaging redesign before recycling.",
            "Check internal reuse demand, damage rate, storage constraints and supplier returnable packaging options.",
            "R006_PACKAGING_REUSE",
            19,
        )

    if material == "plastics" and contamination in {"low", "medium"}:
        if "mixed" in text:
            return (
                "Open-loop recycling or material testing review",
                "open-loop recycling",
                "The plastic stream may be recyclable, but mixed polymer evidence weakens the case for closed-loop use. Material testing should come before claims about circularity.",
                "Confirm polymer type, contamination and whether the recycler can accept segregated or mixed plastic streams.",
                "R007_MIXED_PLASTIC_RECYCLING",
                16,
            )
        return (
            "Closed-loop or secondary material recycling review",
            "closed-loop recycling",
            "The plastic stream may support regrind, supplier return or controlled recycling if polymer type and contamination are confirmed.",
            "Confirm polymer grade, regrind limits, quality requirements and supplier/recycler acceptance criteria.",
            "R008_PLASTIC_CLOSED_LOOP",
            18,
        )

    if material in {"organic/process residue", "process mineral residue", "process water", "energy/resource stream"}:
        return (
            "Industrial symbiosis or resource recovery assessment",
            "industrial symbiosis / resource recovery",
            "The stream may have value as an input for another process, recovery route or resource efficiency project, but technical data is needed before action.",
            "Gather composition, quality, volume consistency and nearby user/recovery route requirements.",
            "R009_SYMBIOSIS_OR_RESOURCE_RECOVERY",
            15,
        )

    if material in {"glass", "rubber", "textiles", "electronic components"} and contamination in {"low", "medium"}:
        return (
            "Open-loop recycling or specialist recovery review",
            "open-loop recycling / specialist recovery",
            "The stream may need a specialist recovery route rather than generic disposal. Evidence should confirm quality, contamination and market acceptance.",
            "Identify specialist recyclers or recovery partners and confirm material acceptance criteria.",
            "R010_SPECIALIST_RECOVERY",
            14,
        )

    return (
        "Compliant disposal route with evidence improvement",
        "compliant disposal",
        "The available data does not yet support a higher-value circular action. The stream should remain on a compliant route while evidence is improved.",
        "Improve material composition, quantity, contamination and route evidence before changing the current route.",
        "R999_DEFAULT_EVIDENCE_IMPROVEMENT",
        8,
    )


def recommend_for_stream(stream: StreamLike) -> RuleRecommendation:
    action, category, reasoning, next_action, rule_applied, rule_strength = _base_decision(stream)
    scores = score_stream(stream, rule_strength=rule_strength)
    annual_material_quantity = _annual_material_quantity(stream)
    annual_cost_exposure = _annual_disposal_cost_exposure(stream)
    supplier_action = _supplier_action(stream, action)
    symbiosis = _symbiosis_flag(_clean(stream.material), action, scores.risk_level)
    priority = _priority(stream, scores.risk_level, scores.confidence_score, annual_cost_exposure)

    return RuleRecommendation(
        stream_id=stream.stream_id,
        recommended_circular_action=action,
        circular_strategy_category=category,
        reasoning=reasoning,
        risk_level=scores.risk_level,
        confidence_score=scores.confidence_score,
        evidence_quality_score=scores.evidence_quality_score,
        missing_data="; ".join(scores.missing_data) if scores.missing_data else "none identified for MVP fields",
        human_review_required=scores.human_review_required,
        # Legacy API/database field names are retained during Milestone 20A for
        # backwards compatibility. The values now represent annual screened
        # quantity and current annual disposal-cost exposure, not achieved
        # diversion or verified savings.
        estimated_annual_waste_diverted_kg=annual_material_quantity,
        estimated_annual_disposal_cost_avoided=annual_cost_exposure,
        supplier_procurement_action=supplier_action,
        industrial_symbiosis_opportunity=symbiosis,
        next_action=next_action,
        dashboard_priority=priority,
        rule_applied=rule_applied,
    )


def recommend_for_streams(streams: list[StreamLike]) -> list[RuleRecommendation]:
    return [recommend_for_stream(stream) for stream in streams]
