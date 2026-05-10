"""AI runtime reliability and agentic mode diagnostics."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app import schemas
from app.llm_reasoning.openai_client import (
    ai_reasoning_enabled,
    api_key_configured,
    configured_base_url,
    configured_model,
    llm_provider,
    llm_timeout_seconds,
)

router = APIRouter(prefix="/api/ai-runtime", tags=["AI runtime reliability"])


@router.get("/status", response_model=schemas.AIRuntimeStatus)
def ai_runtime_status(live_check: bool = Query(default=False)) -> schemas.AIRuntimeStatus:
    """Return deterministic AI runtime configuration and operating mode."""
    enabled = ai_reasoning_enabled()
    key_configured = api_key_configured()
    provider = llm_provider()
    timeout = llm_timeout_seconds()

    if enabled and key_configured:
        runtime_mode = "ai_on"
        live_status = "not_checked" if not live_check else "configured_not_pinged"
        operator_action = (
            "AI requests may use the configured provider. If responses are slow, reduce "
            "LLM_TIMEOUT_SECONDS or switch AI_REASONING_ENABLED=false for fallback mode."
        )
    elif enabled and not key_configured:
        runtime_mode = "fallback_key_missing"
        live_status = "not_available"
        operator_action = (
            "Add a valid provider API key or set AI_REASONING_ENABLED=false to run deterministic "
            "fallback mode intentionally."
        )
    else:
        runtime_mode = "fallback_ai_disabled"
        live_status = "not_applicable"
        operator_action = (
            "Fallback mode is active. Enable AI_REASONING_ENABLED=true and configure a provider key "
            "for live AI drafting/reasoning."
        )

    return schemas.AIRuntimeStatus(
        ai_reasoning_enabled=enabled,
        llm_provider=provider,
        api_key_configured=key_configured,
        configured_model=configured_model(),
        configured_base_url=configured_base_url(),
        timeout_seconds=timeout,
        runtime_mode=runtime_mode,
        live_check_requested=live_check,
        live_check_status=live_status,
        fallback_available=True,
        agentic_role=(
            "AI explains, summarises, drafts evidence requests and produces reports from locked outputs. "
            "It does not own the decision record."
        ),
        guardrail_summary=(
            "Rules engine, evidence register, review gates, risk level, claim readiness and claim boundaries "
            "remain locked. AI output is advisory and fallback-safe."
        ),
        recommended_operator_action=operator_action,
    )
