"""Deterministic fallback narratives when the optional LLM is disabled/unavailable."""

from __future__ import annotations

from typing import Any


def fallback_reasoning(stream: Any, recommendation: Any, evidence: dict[str, Any], resolution: dict[str, Any]) -> dict[str, Any]:
    human_review = bool(recommendation.human_review_required)
    supplier = stream.supplier or "the responsible supplier/contractor"
    review_note = (
        "Human review is required before any circular route is selected. Treat this as a controlled review item, not an implementation candidate."
        if human_review
        else "Human review is not required by the current rules, but evidence must still be validated before implementation or claims."
    )

    supplier_questions = [
        f"Can {supplier} confirm acceptance criteria, rejection conditions and documentation for the proposed route?",
        "What contamination limits, segregation requirements and collection frequency would apply?",
        "What evidence can be provided for audit: specification, contract clause, transfer record, recovery certificate or acceptance note?",
    ]
    if human_review:
        supplier_questions.insert(0, "Can the contractor confirm legal classification, hazardous status and authorised handling requirements before any circular route is considered?")

    return {
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "generation_mode": "deterministic_fallback",
        "model_name": "none",
        "decision_lock_status": "rules_locked",
        "executive_summary": (
            f"{stream.stream_name} has a locked recommendation of '{recommendation.recommended_circular_action}'. "
            f"The current risk level is {recommendation.risk_level} with evidence quality {recommendation.evidence_quality_score}/100."
        ),
        "circular_economy_reasoning": resolution.get("why_this_is_circular_economy", "The plan follows the circular hierarchy and prioritises value retention before disposal."),
        "evidence_gap_explanation": evidence.get("missing_data", recommendation.missing_data or "No missing evidence listed by the current MVP fields."),
        "supplier_questions": supplier_questions,
        "pilot_guidance": resolution.get("pilot_plan", "Run a small controlled validation pilot before scaling."),
        "claim_safety_note": resolution.get("claim_boundary", evidence.get("claim_boundary", "Screening only. Do not claim verified impact until evidence exists.")),
        "human_review_note": review_note,
        "implementation_risks": [
            "Supplier or contractor acceptance may differ from screening assumptions.",
            "Contamination, quality or legal classification may block the preferred circular route.",
            "Screened diversion and cost figures are not verified savings until actions are completed and evidenced.",
        ],
        "validation_warnings": [],
    }
