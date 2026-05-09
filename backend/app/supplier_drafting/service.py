"""Service layer for supplier evidence request email drafting."""

from __future__ import annotations

from typing import Any

from app.llm_reasoning.openai_client import ai_reasoning_enabled, api_key_configured, configured_model
from app.supplier_drafting.fallback import build_fallback_supplier_email_draft
from app.supplier_drafting.llm_client import call_structured_supplier_email


_REQUIRED_FIELDS = [
    "subject",
    "email_body",
    "evidence_request_summary",
    "attachments_or_documents_to_request",
    "internal_follow_up_actions",
    "claim_safety_note",
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


def _build_context(stream: Any, recommendation: Any, supplier_plan: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "system_name": "Circular Industry AI",
        "decision_source": "Locked rules engine, evidence register and supplier-loop plan",
        "ai_role": "Draft supplier evidence request communication only. Do not verify or change facts.",
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
            "claim_readiness": evidence.get("claim_readiness"),
            "evidence_status": evidence.get("evidence_status"),
            "review_gate": evidence.get("review_gate"),
            "procurement_route": supplier_plan.get("procurement_route"),
            "supplier_relationship_type": supplier_plan.get("supplier_relationship_type"),
            "claim_boundary": supplier_plan.get("claim_boundary") or evidence.get("claim_boundary"),
            "estimated_annual_value_at_stake": supplier_plan.get("estimated_annual_value_at_stake"),
        },
        "supplier_plan": supplier_plan,
        "evidence_record": evidence,
        "non_override_rules": [
            "Do not claim supplier take-back exists unless locked data says it exists.",
            "Do not claim verified savings, diversion, carbon saving or compliance.",
            "Do not change risk level, human review status, rule applied, claim readiness, review gate or procurement route.",
            "For high, blocked or human-review streams, write as evidence/compliance request only.",
        ],
        "required_tone": "Professional, practical, concise and suitable for procurement/supplier communication.",
    }


def _lock_response(raw: dict[str, Any], fallback: dict[str, Any], stream: Any, recommendation: Any, supplier_plan: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    locked = {
        "generation_mode": "llm_structured_output",
        "model_name": configured_model(),
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "supplier": fallback["supplier"],
        "decision_lock_status": "Rules engine locked. Supplier email draft advisory only.",
        "draft_type": "supplier evidence request",
        "governance_note": fallback["governance_note"],
        "validation_warnings": [],
        "locked_rule_applied": recommendation.rule_applied,
        "locked_risk_level": recommendation.risk_level,
        "locked_human_review_required": recommendation.human_review_required,
        "locked_claim_readiness": evidence.get("claim_readiness"),
        "locked_procurement_route": supplier_plan.get("procurement_route"),
        "locked_review_gate": supplier_plan.get("review_gate"),
    }

    for field in _REQUIRED_FIELDS:
        value = raw.get(field)
        if value in {None, ""}:
            value = fallback[field]
        if field in {"evidence_request_summary", "attachments_or_documents_to_request", "internal_follow_up_actions"} and not isinstance(value, list):
            value = fallback[field]
        locked[field] = value

    return _clean_text(locked)


def generate_supplier_email_draft(stream: Any, recommendation: Any, supplier_plan: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    fallback = build_fallback_supplier_email_draft(stream, recommendation, supplier_plan, evidence)

    if not ai_reasoning_enabled() or not api_key_configured():
        return _clean_text(fallback)

    try:
        raw = call_structured_supplier_email(_build_context(stream, recommendation, supplier_plan, evidence))
        return _lock_response(raw, fallback, stream, recommendation, supplier_plan, evidence)
    except Exception as exc:
        result = fallback
        result["generation_mode"] = "deterministic_fallback_after_llm_error"
        result["validation_warnings"] = [f"LLM call failed and fallback text was used: {exc}"]
        return _clean_text(result)
