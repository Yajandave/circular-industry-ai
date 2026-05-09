"""Post-generation guardrails for AI reasoning narratives."""

from __future__ import annotations

from typing import Any

FORBIDDEN_CONFIDENCE_CLAIMS = [
    "verified savings",
    "verified carbon",
    "carbon neutral",
    "legally compliant",
    "supplier has confirmed",
    "guaranteed",
]


def validate_and_lock_reasoning(raw: dict[str, Any], stream: Any, recommendation: Any, resolution: dict[str, Any], model_name: str) -> dict[str, Any]:
    warnings: list[str] = []
    safe = dict(raw)

    for key in [
        "executive_summary",
        "circular_economy_reasoning",
        "evidence_gap_explanation",
        "pilot_guidance",
        "claim_safety_note",
        "human_review_note",
    ]:
        if not isinstance(safe.get(key), str) or not safe.get(key, "").strip():
            safe[key] = "Not generated. Use the deterministic resolution plan and evidence register for this field."
            warnings.append(f"Missing or invalid field corrected: {key}")

    if not isinstance(safe.get("supplier_questions"), list):
        safe["supplier_questions"] = []
        warnings.append("supplier_questions was not a list and was reset.")
    if not isinstance(safe.get("implementation_risks"), list):
        safe["implementation_risks"] = []
        warnings.append("implementation_risks was not a list and was reset.")

    combined_text = " ".join(
        [str(safe.get("executive_summary", "")), str(safe.get("claim_safety_note", "")), str(safe.get("circular_economy_reasoning", ""))]
    ).lower()
    for phrase in FORBIDDEN_CONFIDENCE_CLAIMS:
        if phrase in combined_text:
            warnings.append(f"Potential unsupported claim detected: '{phrase}'. Human review required before using this wording externally.")

    if recommendation.human_review_required and "human" not in safe["human_review_note"].lower():
        safe["human_review_note"] = (
            "Human review is required by the locked rules engine before circular route selection. "
            + safe["human_review_note"]
        )
        warnings.append("Human-review warning strengthened because the rules engine requires review.")

    safe["stream_id"] = stream.stream_id
    safe["stream_name"] = stream.stream_name
    safe["generation_mode"] = "llm_structured_output"
    safe["model_name"] = model_name
    safe["decision_lock_status"] = "rules_locked"
    safe["locked_rule_applied"] = recommendation.rule_applied
    safe["locked_risk_level"] = recommendation.risk_level
    safe["locked_human_review_required"] = recommendation.human_review_required
    safe["locked_recommendation"] = recommendation.recommended_circular_action
    safe["claim_boundary"] = resolution.get("claim_boundary", recommendation.next_action)
    safe["validation_warnings"] = warnings
    return safe
