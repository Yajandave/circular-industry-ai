"""Advanced but controlled agentic analysis layer.

This module intentionally keeps the rules engine as the source of truth. The
agentic layer composes specialist review perspectives around an existing rules
recommendation: evidence, risk, procurement, industrial symbiosis, resource
efficiency and executive synthesis.

The result is industrial-grade decision support without allowing an LLM or
agentic workflow to silently override risk controls.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from app import models


HIGH_VALUE_MATERIALS = {"metals", "electronic components", "glass", "rubber"}
SUPPLIER_LINKED_MATERIALS = {"cardboard/packaging", "wood/pallets", "plastics", "metals"}
SYMBIOSIS_CANDIDATES = {
    "organic/process residue",
    "process mineral residue",
    "process water",
    "energy/resource stream",
    "wood/pallets",
    "textiles",
    "rubber",
    "glass",
}


def _normalise(value: Any) -> str:
    return str(value or "").strip().lower()


def _split_missing_data(missing_data: str) -> list[str]:
    if not missing_data or missing_data.lower().strip() in {"none", "n/a"}:
        return []
    parts = [part.strip(" .") for part in missing_data.replace(";", ",").split(",")]
    return [part for part in parts if part]


def _claim_safety_controls(recommendation: models.CircularRecommendation) -> list[str]:
    controls = [
        "Do not describe estimated diversion or avoided cost as verified impact until actions are completed and evidenced.",
        "Keep the rules engine output as the locked recommendation source for auditability.",
    ]
    if recommendation.human_review_required:
        controls.append(
            "Do not progress operational action until a competent human reviewer has checked the risk and evidence gaps."
        )
    if recommendation.risk_level in {"high", "blocked"}:
        controls.append(
            "Do not make circularity, recycling, recovery or reuse claims for this stream until the high-risk status is resolved."
        )
    return controls


def evidence_audit(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Review data maturity and claim boundaries for one stream."""
    measured_data = []
    estimated_data = []
    assumptions = []
    missing = _split_missing_data(recommendation.missing_data)

    if stream.monthly_quantity_kg > 0:
        measured_data.append("monthly_quantity_kg is present in the uploaded stream dataset")
    else:
        missing.append("measured monthly quantity")

    if stream.disposal_cost_per_month > 0:
        measured_data.append("disposal_cost_per_month is present in the uploaded stream dataset")
    else:
        missing.append("current disposal cost")

    if _normalise(stream.hazardous_flag) == "unknown":
        missing.append("confirmed hazardous status")
    else:
        measured_data.append("hazardous_flag is recorded in the uploaded stream dataset")

    if _normalise(stream.contamination_risk) == "unknown":
        missing.append("confirmed contamination risk")
    else:
        measured_data.append("contamination_risk is recorded in the uploaded stream dataset")

    estimated_data.extend(
        [
            "estimated_annual_waste_diverted_kg is calculated as monthly_quantity_kg multiplied by 12",
            "estimated_annual_disposal_cost_avoided is calculated as disposal_cost_per_month multiplied by 12",
        ]
    )

    if "unknown" in _normalise(stream.supplier_takeback_available):
        assumptions.append("supplier take-back potential is unverified and must be checked with the supplier")
    if "not always recorded" in _normalise(stream.notes):
        assumptions.append("operational notes suggest incomplete source evidence")
    if recommendation.evidence_quality_score < 70:
        assumptions.append("evidence quality is below the preferred threshold for confident action")

    claim_boundary = (
        "This review supports opportunity screening only. It does not verify legal waste status, supplier compliance, "
        "environmental permits, product quality acceptance, or carbon savings."
    )

    return {
        "evidence_quality_score": recommendation.evidence_quality_score,
        "measured_data": measured_data,
        "estimated_data": estimated_data,
        "assumptions": assumptions,
        "missing_data": sorted(set(missing)),
        "claim_boundary": claim_boundary,
        "claim_safety_controls": _claim_safety_controls(recommendation),
    }


def risk_reviewer(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Explain risk locks and review conditions."""
    risk_triggers = []
    review_gates = []

    if _normalise(stream.hazardous_flag) == "true":
        risk_triggers.append("hazardous_flag is true")
        review_gates.append("EHS or competent environmental compliance review")
    elif _normalise(stream.hazardous_flag) == "unknown":
        risk_triggers.append("hazardous status is unknown")
        review_gates.append("hazard classification confirmation")

    if _normalise(stream.contamination_risk) in {"high", "unknown"}:
        risk_triggers.append(f"contamination_risk is {stream.contamination_risk}")
        review_gates.append("contamination assessment and acceptance criteria")

    if recommendation.risk_level == "blocked":
        review_gates.append("blocked recommendation review before any circular route is proposed")

    if not risk_triggers:
        risk_triggers.append("no major safety or contamination trigger identified from uploaded fields")

    return {
        "risk_level": recommendation.risk_level,
        "human_review_required": recommendation.human_review_required,
        "risk_triggers": risk_triggers,
        "review_gates": sorted(set(review_gates)),
        "locked_controls": [
            "agentic layer cannot lower risk level",
            "agentic layer cannot remove human_review_required",
            "agentic layer cannot replace the rule_applied field",
        ],
    }


def procurement_agent(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Generate supplier and procurement actions."""
    supplier = stream.supplier or "current supplier"
    material = _normalise(stream.material)
    questions = [
        f"Can {supplier} provide documented recycled-content options for this material or input category?",
        f"Can {supplier} support segregation, take-back, returnable packaging, or closed-loop routing?",
        "What evidence can be provided: specification sheet, acceptance criteria, certificate, audit record, or contract clause?",
    ]
    levers = []

    if material in SUPPLIER_LINKED_MATERIALS:
        levers.extend(["supplier take-back review", "contract clause for reverse logistics"])
    if _normalise(stream.recycled_content_available) == "yes":
        levers.append("compare virgin versus recycled-content procurement option")
    if _normalise(stream.supplier_takeback_available) == "yes":
        levers.append("test take-back route as priority action")
    elif _normalise(stream.supplier_takeback_available) == "unknown":
        levers.append("request supplier take-back evidence")

    return {
        "supplier": supplier,
        "procurement_levers": sorted(set(levers)) or ["procurement evidence request"],
        "supplier_questions": questions,
        "procurement_action": recommendation.supplier_procurement_action,
        "contract_evidence_needed": [
            "take-back terms or rejection criteria",
            "material specification and segregation requirements",
            "recycled content or secondary material evidence where claimed",
        ],
    }


def symbiosis_agent(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Assess whether industrial symbiosis is a credible screening route."""
    material = _normalise(stream.material)
    route = _normalise(recommendation.industrial_symbiosis_opportunity)
    possible = material in SYMBIOSIS_CANDIDATES or "possible" in route or "screen" in route

    screening_questions = [
        "Is the stream composition stable enough for another organisation to accept it as an input?",
        "Is the monthly volume consistent enough to justify collection, storage and transport?",
        "Are contamination controls and liability boundaries documented?",
        "Would transport and processing reduce the benefit compared with on-site reduction or supplier take-back?",
    ]

    likely_partners = []
    if material == "organic/process residue":
        likely_partners = ["anaerobic digestion operator", "animal feed or composting route subject to compliance"]
    elif material == "process water":
        likely_partners = ["on-site reuse process", "nearby industrial water user subject to treatment quality"]
    elif material == "energy/resource stream":
        likely_partners = ["nearby heat user", "internal heat recovery project"]
    elif material in {"glass", "rubber", "textiles", "wood/pallets"}:
        likely_partners = ["specialist recycler", "secondary material processor", "local industrial user"]

    return {
        "symbiosis_screening_status": "screening recommended" if possible else "not primary route",
        "likely_partner_types": likely_partners,
        "screening_questions": screening_questions,
        "barriers_to_resolve": [
            "composition and contamination evidence",
            "volume consistency",
            "transport and storage practicality",
            "legal status and acceptance criteria",
        ],
    }


def resource_efficiency_agent(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Suggest process-level opportunities before end-of-pipe routes."""
    process = stream.source_process
    material = _normalise(stream.material)
    levers = [
        f"Review why {stream.stream_name} arises from {process} before choosing an end-of-pipe route.",
        "Check whether process settings, cutting plans, batch quality, handling or storage are causing avoidable scrap.",
    ]

    if material == "metals":
        levers.append("Assess nesting/cutting optimisation and alloy segregation at source.")
    elif material == "plastics":
        levers.append("Check polymer separation, purge reduction and regrind compatibility.")
    elif material == "cardboard/packaging":
        levers.append("Review inbound packaging specifications and returnable transit packaging potential.")
    elif material == "chemicals/solvents":
        levers.append("Check solvent minimisation, substitution and specialist recovery before disposal.")

    return {
        "reduce_before_recycle_check": True,
        "process_improvement_levers": levers,
        "priority_reason": recommendation.dashboard_priority,
    }


def executive_synthesis(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
    evidence: dict[str, Any],
    risk: dict[str, Any],
) -> dict[str, Any]:
    """Create decision-ready wording for managers."""
    decision_source = "rules_engine_locked"
    if recommendation.human_review_required:
        decision_position = (
            f"{stream.stream_name} should be treated as a controlled review item before circular action. "
            f"The current rule output is {recommendation.recommended_circular_action} with {recommendation.risk_level} risk."
        )
    else:
        decision_position = (
            f"{stream.stream_name} is a candidate for {recommendation.recommended_circular_action.lower()} because the "
            f"rules engine identified a {recommendation.circular_strategy_category} opportunity with {recommendation.risk_level} risk."
        )

    evidence_position = (
        f"Evidence quality is {recommendation.evidence_quality_score}/100 and confidence is "
        f"{recommendation.confidence_score}/100. Missing evidence should be resolved before presenting this as verified impact."
    )

    return {
        "decision_source": decision_source,
        "decision_position": decision_position,
        "evidence_position": evidence_position,
        "recommended_management_action": recommendation.next_action,
        "what_not_to_claim": evidence["claim_safety_controls"],
        "human_review_position": "required" if risk["human_review_required"] else "not required by current rules",
    }


def build_stream_review_pack(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Build a multi-agent review pack for one industrial stream."""
    evidence = evidence_audit(stream, recommendation)
    risk = risk_reviewer(stream, recommendation)
    procurement = procurement_agent(stream, recommendation)
    symbiosis = symbiosis_agent(stream, recommendation)
    resource_efficiency = resource_efficiency_agent(stream, recommendation)
    synthesis = executive_synthesis(stream, recommendation, evidence, risk)

    return {
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "material": stream.material,
        "decision_locked_by_rules": True,
        "rule_applied": recommendation.rule_applied,
        "base_recommendation": {
            "recommended_circular_action": recommendation.recommended_circular_action,
            "circular_strategy_category": recommendation.circular_strategy_category,
            "risk_level": recommendation.risk_level,
            "confidence_score": recommendation.confidence_score,
            "evidence_quality_score": recommendation.evidence_quality_score,
            "human_review_required": recommendation.human_review_required,
        },
        "executive_synthesis": synthesis,
        "evidence_audit": evidence,
        "risk_review": risk,
        "procurement_review": procurement,
        "industrial_symbiosis_review": symbiosis,
        "resource_efficiency_review": resource_efficiency,
    }


def build_management_summary(
    recommendations: list[models.CircularRecommendation],
) -> dict[str, Any]:
    """Create portfolio-grade executive summary from all recommendations."""
    total = len(recommendations)
    human_review = sum(1 for rec in recommendations if rec.human_review_required)
    risk_counts = Counter(rec.risk_level for rec in recommendations)
    strategy_counts = Counter(rec.circular_strategy_category for rec in recommendations)
    high_priority = [rec for rec in recommendations if rec.dashboard_priority == "high"]
    low_evidence = [rec for rec in recommendations if rec.evidence_quality_score < 70]

    top_value = sorted(
        recommendations,
        key=lambda rec: (rec.estimated_annual_disposal_cost_avoided, rec.estimated_annual_waste_diverted_kg),
        reverse=True,
    )[:5]

    return {
        "decision_source": "rules_engine_locked_with_agentic_synthesis",
        "total_recommendations": total,
        "human_review_required": human_review,
        "risk_breakdown": dict(risk_counts),
        "strategy_breakdown": dict(strategy_counts),
        "high_priority_count": len(high_priority),
        "low_evidence_count": len(low_evidence),
        "estimated_annual_waste_diverted_kg": round(sum(rec.estimated_annual_waste_diverted_kg for rec in recommendations), 2),
        "estimated_annual_disposal_cost_avoided": round(sum(rec.estimated_annual_disposal_cost_avoided for rec in recommendations), 2),
        "executive_summary": (
            f"The current rules run generated {total} circular economy recommendations. "
            f"{human_review} streams require human review, which should be treated as a control rather than a failure. "
            f"The strongest immediate focus should be high-priority, low-risk streams with good evidence, while high-risk or low-evidence streams should move through controlled review."
        ),
        "top_cost_avoidance_candidates": [
            {
                "stream_id": rec.stream_id,
                "recommended_circular_action": rec.recommended_circular_action,
                "estimated_annual_disposal_cost_avoided": rec.estimated_annual_disposal_cost_avoided,
                "risk_level": rec.risk_level,
                "human_review_required": rec.human_review_required,
            }
            for rec in top_value
        ],
        "portfolio_note": (
            "This summary is decision-support output. It should not be presented as verified operational savings or verified environmental impact until actions are completed and evidenced."
        ),
    }


def build_action_plan(
    recommendations: list[models.CircularRecommendation],
    limit: int = 12,
) -> dict[str, Any]:
    """Rank recommendations into a practical action plan."""
    def score(rec: models.CircularRecommendation) -> float:
        review_penalty = 35 if rec.human_review_required else 0
        risk_penalty = {"low": 0, "medium": 10, "high": 35, "blocked": 60}.get(rec.risk_level, 20)
        value_score = min(rec.estimated_annual_disposal_cost_avoided / 100, 25)
        diversion_score = min(rec.estimated_annual_waste_diverted_kg / 5000, 20)
        return rec.confidence_score + value_score + diversion_score - risk_penalty - review_penalty

    ranked = sorted(recommendations, key=score, reverse=True)[:limit]
    phases: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for rec in ranked:
        if rec.human_review_required or rec.risk_level in {"high", "blocked"}:
            phase = "controlled review"
        elif rec.dashboard_priority == "high" and rec.evidence_quality_score >= 70:
            phase = "quick-win validation"
        else:
            phase = "opportunity development"

        phases[phase].append(
            {
                "stream_id": rec.stream_id,
                "recommended_circular_action": rec.recommended_circular_action,
                "risk_level": rec.risk_level,
                "confidence_score": rec.confidence_score,
                "evidence_quality_score": rec.evidence_quality_score,
                "estimated_annual_waste_diverted_kg": rec.estimated_annual_waste_diverted_kg,
                "estimated_annual_disposal_cost_avoided": rec.estimated_annual_disposal_cost_avoided,
                "next_action": rec.next_action,
            }
        )

    return {
        "ranking_method": "confidence + value/diversion potential - risk/review penalties",
        "phases": dict(phases),
        "governance_note": "High-scoring items still require evidence confirmation before claims are made.",
    }
