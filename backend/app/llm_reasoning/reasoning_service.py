"""Service for generating rules-locked AI reasoning narratives."""

from __future__ import annotations

from typing import Any

from app.llm_reasoning.context_builder import build_llm_context
from app.llm_reasoning.fallback import fallback_reasoning
from app.llm_reasoning.guardrails import validate_and_lock_reasoning
from app.llm_reasoning.openai_client import ai_reasoning_enabled, api_key_configured, call_structured_reasoning, configured_base_url, configured_model, llm_provider


def generate_reasoning(stream: Any, recommendation: Any, evidence: dict[str, Any], resolution: dict[str, Any]) -> dict[str, Any]:
    if not ai_reasoning_enabled() or not api_key_configured():
        return fallback_reasoning(stream, recommendation, evidence, resolution)

    context = build_llm_context(stream, recommendation, evidence, resolution)
    try:
        raw = call_structured_reasoning(context)
        return validate_and_lock_reasoning(raw, stream, recommendation, resolution, configured_model())
    except Exception as exc:  # keep the product usable if the optional LLM fails
        result = fallback_reasoning(stream, recommendation, evidence, resolution)
        result["generation_mode"] = "deterministic_fallback_after_llm_error"
        result["validation_warnings"] = [f"LLM call failed and fallback text was used: {exc}"]
        return result


def reasoning_status() -> dict[str, Any]:
    return {
        "ai_reasoning_enabled": ai_reasoning_enabled(),
        "openai_api_key_configured": api_key_configured(),
        "llm_provider": llm_provider(),
        "api_key_configured": api_key_configured(),
        "configured_model": configured_model(),
        "configured_base_url": configured_base_url(),
        "mode": f"{llm_provider()}_structured_output" if ai_reasoning_enabled() and api_key_configured() else "deterministic_fallback",
        "guardrail_summary": (
            "Rules decide. Resolution Engine designs. Optional LLM explains and customises. "
            "Risk level, human review status, rule applied and claim boundaries remain locked."
        ),
    }
