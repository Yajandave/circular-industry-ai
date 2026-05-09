"""Service layer for circular action reports."""

from __future__ import annotations

from typing import Any

from app.llm_reasoning.openai_client import ai_reasoning_enabled, api_key_configured, configured_model
from app.report_builder.fallback import build_fallback_circular_action_report
from app.report_builder.llm_client import call_structured_circular_action_report


_REQUIRED_FIELDS = [
    "report_title",
    "executive_summary",
    "risk_and_review_status",
    "evidence_position",
    "circular_resolution_summary",
    "supplier_loop_summary",
    "implementation_plan",
    "evidence_to_collect",
    "unsafe_claims_to_avoid",
    "recommended_next_actions",
    "claim_boundary",
]


def _clean_text(value: Any) -> Any:
    if isinstance(value, str):
        return (
            value.replace("Â£", "GBP ")
            .replace("â€™", "'")
            .replace("â€œ", '"')
            .replace("â€\x9d", '"')
            .replace("â€“", "-")
            .replace("â€”", "-")
            .replace("Â", "")
        )
    if isinstance(value, list):
        return [_clean_text(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_text(item) for key, item in value.items()}
    return value


def _build_context(stream: Any, recommendation: Any, evidence: dict[str, Any], resolution: dict[str, Any], supplier_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "system_name": "Circular Industry AI",
        "decision_source": "Locked rules engine, evidence register, resolution plan and supplier-loop plan",
        "ai_role": "Write a controlled circular action report only. Do not verify or change facts.",
        "locked_fields": {
            "stream_id": stream.stream_id,
            "stream_name": stream.stream_name,
            "material": stream.material,
            "department": stream.department,
            "supplier": stream.supplier,
            "recommended_circular_action": recommendation.recommended_circular_action,
            "rule_applied": recommendation.rule_applied,
            "risk_level": recommendation.risk_level,
            "human_review_required": recommendation.human_review_required,
            "confidence_score": recommendation.confidence_score,
            "evidence_quality_score": recommendation.evidence_quality_score,
            "claim_readiness": evidence.get("claim_readiness"),
            "evidence_status": evidence.get("evidence_status"),
            "review_gate": evidence.get("review_gate"),
            "procurement_route": supplier_plan.get("procurement_route"),
            "claim_boundary": supplier_plan.get("claim_boundary") or evidence.get("claim_boundary"),
            "estimated_annual_waste_diverted_kg": recommendation.estimated_annual_waste_diverted_kg,
            "estimated_annual_disposal_cost_avoided": recommendation.estimated_annual_disposal_cost_avoided,
        },
        "evidence_record": evidence,
        "resolution_plan": resolution,
        "supplier_plan": supplier_plan,
        "non_override_rules": [
            "Do not change risk level.",
            "Do not change human review status.",
            "Do not change rule applied.",
            "Do not change claim readiness.",
            "Do not change review gate.",
            "Do not change procurement route.",
            "Do not invent verified savings, diversion, carbon impact, compliance or supplier capability.",
        ],
        "required_tone": "Consultant-style, practical, concise, audit-aware and suitable for a sustainability/procurement review pack.",
    }


def _lock_response(raw: dict[str, Any], fallback: dict[str, Any], recommendation: Any, evidence: dict[str, Any], supplier_plan: dict[str, Any]) -> dict[str, Any]:
    locked = {
        "generation_mode": "llm_structured_output",
        "model_name": configured_model(),
        "stream_id": fallback["stream_id"],
        "stream_name": fallback["stream_name"],
        "decision_lock_status": fallback["decision_lock_status"],
        "locked_recommendation": recommendation.recommended_circular_action,
        "governance_note": fallback["governance_note"],
        "validation_warnings": [],
        "locked_rule_applied": recommendation.rule_applied,
        "locked_risk_level": recommendation.risk_level,
        "locked_human_review_required": recommendation.human_review_required,
        "locked_claim_readiness": evidence.get("claim_readiness"),
        "locked_review_gate": evidence.get("review_gate"),
        "locked_procurement_route": supplier_plan.get("procurement_route"),
    }

    for field in _REQUIRED_FIELDS:
        value = raw.get(field)
        if value in {None, ""}:
            value = fallback[field]
        if field in {"implementation_plan", "evidence_to_collect", "unsafe_claims_to_avoid", "recommended_next_actions"} and not isinstance(value, list):
            value = fallback[field]
        locked[field] = value

    return _clean_text(locked)


def generate_circular_action_report(
    stream: Any,
    recommendation: Any,
    evidence: dict[str, Any],
    resolution: dict[str, Any],
    supplier_plan: dict[str, Any],
) -> dict[str, Any]:
    fallback = build_fallback_circular_action_report(stream, recommendation, evidence, resolution, supplier_plan)

    if not ai_reasoning_enabled() or not api_key_configured():
        return _clean_text(fallback)

    try:
        raw = call_structured_circular_action_report(_build_context(stream, recommendation, evidence, resolution, supplier_plan))
        return _lock_response(raw, fallback, recommendation, evidence, supplier_plan)
    except Exception as exc:
        result = fallback
        result["generation_mode"] = "deterministic_fallback_after_llm_error"
        result["validation_warnings"] = [f"LLM call failed and fallback text was used: {exc}"]
        return _clean_text(result)
