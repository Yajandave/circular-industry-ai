"""Service layer for the site-wide AI copilot."""

from __future__ import annotations

from typing import Any

from app.ai_copilot.context_builder import build_site_copilot_context
from app.ai_copilot.fallback import build_fallback_site_summary
from app.llm_reasoning.openai_client import (
    ai_reasoning_enabled,
    api_key_configured,
    call_structured_reasoning,
    configured_model,
)


def _clean_text(value: Any) -> Any:
    """Clean common encoding artefacts from optional LLM text output."""
    if isinstance(value, str):
        return (
            value.replace("Â£", "GBP ")
            .replace("â€™", "'")
            .replace("â€œ", '"')
            .replace("â€", '"')
            .replace("â€“", "-")
            .replace("â€”", "-")
            .replace("Â", "")
        )
    if isinstance(value, list):
        return [_clean_text(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_text(item) for key, item in value.items()}
    return value


def _map_llm_reasoning_to_site_summary(raw: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Map the existing structured reasoning response into a site-wide copilot response.

    The existing LLM client already supports OpenAI/Gemini and JSON output. For this
    milestone, we reuse that safe structured-output path instead of creating another
    provider client.
    """
    fallback = build_fallback_site_summary(context)

    supplier_questions = raw.get("supplier_questions") or []
    implementation_risks = raw.get("implementation_risks") or []

    summary = {
        "generation_mode": "llm_structured_output",
        "model_name": configured_model(),
        "decision_lock_status": "Rules engine locked. AI copilot advisory only.",
        "executive_summary": raw.get("executive_summary") or fallback["executive_summary"],
        "risk_summary": (
            "Site risk is based only on the locked rules-engine breakdown: "
            f"{context['risk_breakdown']}. "
            + (raw.get("human_review_note") or "")
        ).strip(),
        "opportunity_summary": raw.get("circular_economy_reasoning") or fallback["opportunity_summary"],
        "evidence_gap_summary": raw.get("evidence_gap_explanation") or fallback["evidence_gap_summary"],
        "supplier_procurement_summary": (
            "Supplier/procurement questions to investigate: " + "; ".join(supplier_questions)
            if supplier_questions
            else fallback["supplier_procurement_summary"]
        ),
        "human_review_priorities": implementation_risks or fallback["human_review_priorities"],
        "recommended_next_actions": [
            raw.get("pilot_guidance") or "Create a controlled pilot plan for the highest-value low-risk opportunities.",
            "Close evidence gaps before making external circularity, diversion, cost or compliance claims.",
            "Escalate blocked, hazardous, unknown or contamination-sensitive streams to human review.",
            "Use supplier questions to verify take-back, recycled-content and reuse-route feasibility.",
            "Keep the rules-engine output as the decision record and use the copilot text only as briefing support.",
        ],
        "claim_safety_note": raw.get("claim_safety_note") or fallback["claim_safety_note"],
        "governance_note": fallback["governance_note"],
        "validation_warnings": [],
    }
    return _clean_text(summary)


def generate_site_copilot_summary(streams: list[Any], recommendations: list[Any]) -> dict[str, Any]:
    context = build_site_copilot_context(streams, recommendations)

    if not ai_reasoning_enabled() or not api_key_configured():
        return _clean_text(build_fallback_site_summary(context))

    try:
        raw = call_structured_reasoning(context)
        return _map_llm_reasoning_to_site_summary(raw, context)
    except Exception as exc:
        result = build_fallback_site_summary(context)
        result["generation_mode"] = "deterministic_fallback_after_llm_error"
        result["validation_warnings"] = [f"LLM call failed and fallback text was used: {exc}"]
        return _clean_text(result)
