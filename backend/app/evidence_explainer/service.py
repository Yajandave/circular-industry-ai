"""Service layer for AI evidence gap explanations."""

from __future__ import annotations

from typing import Any

from app.evidence_explainer.fallback import build_fallback_evidence_gap_explanation
from app.evidence_explainer.llm_client import call_structured_evidence_gap
from app.llm_reasoning.openai_client import ai_reasoning_enabled, api_key_configured, configured_model

_REQUIRED_FIELDS = [
    "evidence_gap_summary",
    "claim_readiness_explanation",
    "evidence_to_collect",
    "supplier_documents_required",
    "process_checks_required",
    "safe_current_statement",
    "unsafe_claims_to_avoid",
    "recommended_review_gate",
]


def _clean_text(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("Â£", "GBP ").replace("Â", "")
    if isinstance(value, list):
        return [_clean_text(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_text(item) for key, item in value.items()}
    return value


def _build_context(stream: Any, recommendation: Any, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "system_name": "Circular Industry AI",
        "decision_source": "Locked deterministic rules engine and evidence register",
        "ai_role": "Explain evidence gaps and claim safety only. Do not make or change decisions.",
        "locked_fields": {
            "stream_id": stream.stream_id,
            "stream_name": stream.stream_name,
            "material": stream.material,
            "department": stream.department,
            "supplier": stream.supplier,
            "recommended_circular_action": recommendation.recommended_circular_action,
            "circular_strategy_category": recommendation.circular_strategy_category,
            "rule_applied": recommendation.rule_applied,
            "risk_level": recommendation.risk_level,
            "human_review_required": recommendation.human_review_required,
            "confidence_score": recommendation.confidence_score,
            "evidence_quality_score": recommendation.evidence_quality_score,
            "evidence_status": evidence.get("evidence_status"),
            "review_gate": evidence.get("review_gate"),
            "claim_readiness": evidence.get("claim_readiness"),
            "claim_boundary": evidence.get("claim_boundary"),
            "estimated_annual_waste_diverted_kg": recommendation.estimated_annual_waste_diverted_kg,
            "estimated_annual_disposal_cost_avoided": recommendation.estimated_annual_disposal_cost_avoided,
        },
        "evidence_record": evidence,
        "non_override_rules": [
            "Do not change risk level.",
            "Do not change human review status.",
            "Do not change rule applied.",
            "Do not change claim readiness.",
            "Do not change review gate.",
            "Do not invent verified savings, diversion, carbon impact, compliance or supplier capability.",
        ],
        "required_output_style": "Write for a junior ESG, circular economy, procurement or environmental analyst. Be practical, evidence-specific, cautious and audit-ready.",
    }


def _lock_response(raw: dict[str, Any], fallback: dict[str, Any], stream: Any, recommendation: Any, evidence: dict[str, Any]) -> dict[str, Any]:
    locked = {
        "generation_mode": "llm_structured_output",
        "model_name": configured_model(),
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "decision_lock_status": "Rules engine locked. Evidence explainer advisory only.",
        "governance_note": fallback["governance_note"],
        "validation_warnings": [],
        "locked_rule_applied": recommendation.rule_applied,
        "locked_risk_level": recommendation.risk_level,
        "locked_human_review_required": recommendation.human_review_required,
        "locked_claim_readiness": evidence.get("claim_readiness"),
        "locked_review_gate": evidence.get("review_gate"),
    }
    for field in _REQUIRED_FIELDS:
        value = raw.get(field)
        if value in {None, ""}:
            value = fallback[field]
        if field.endswith("_required") or field in {"evidence_to_collect", "unsafe_claims_to_avoid"}:
            if not isinstance(value, list):
                value = fallback[field]
        locked[field] = value
    return _clean_text(locked)


def generate_evidence_gap_explanation(stream: Any, recommendation: Any, evidence: dict[str, Any]) -> dict[str, Any]:
    fallback = build_fallback_evidence_gap_explanation(stream, recommendation, evidence)
    if not ai_reasoning_enabled() or not api_key_configured():
        return _clean_text(fallback)
    try:
        raw = call_structured_evidence_gap(_build_context(stream, recommendation, evidence))
        return _lock_response(raw, fallback, stream, recommendation, evidence)
    except Exception as exc:
        result = fallback
        result["generation_mode"] = "deterministic_fallback_after_llm_error"
        result["validation_warnings"] = [f"LLM call failed and fallback text was used: {exc}"]
        return _clean_text(result)
