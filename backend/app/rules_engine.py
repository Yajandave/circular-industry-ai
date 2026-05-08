"""Deterministic circular economy recommendation engine.

Milestone 3 deliberately uses rules before AI. The objective is to create
traceable first-pass recommendations that can later be explained by an AI layer
without allowing the AI to override risk or evidence constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.scoring import score_stream


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


def _annual_diversion(stream: StreamLike, action: str, human_review_required: bool) -> float:
    if human_review_required and "human review" in action.lower():
        return 0.0
    if stream.monthly_quantity_kg <= 0:
        return 0.0
    return round(stream.monthly_quantity_kg * 12, 2)


def _annual_cost_avoided(stream: StreamLike, action: str, human_review_required: bool) -> float:
    if human_review_required and "human review" in action.lower():
        return 0.0
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
    annual_diversion = _annual_diversion(stream, action, scores.human_review_required)
    annual_cost = _annual_cost_avoided(stream, action, scores.human_review_required)
    supplier_action = _supplier_action(stream, action)
    symbiosis = _symbiosis_flag(_clean(stream.material), action, scores.risk_level)
    priority = _priority(stream, scores.risk_level, scores.confidence_score, annual_cost)

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
        estimated_annual_waste_diverted_kg=annual_diversion,
        estimated_annual_disposal_cost_avoided=annual_cost,
        supplier_procurement_action=supplier_action,
        industrial_symbiosis_opportunity=symbiosis,
        next_action=next_action,
        dashboard_priority=priority,
        rule_applied=rule_applied,
    )


def recommend_for_streams(streams: list[StreamLike]) -> list[RuleRecommendation]:
    return [recommend_for_stream(stream) for stream in streams]
