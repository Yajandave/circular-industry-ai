"""LLM client for structured supplier evidence request email drafts."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.llm_reasoning.openai_client import (
    OPENAI_RESPONSES_URL,
    _api_key,
    _extract_gemini_text,
    _extract_openai_output_text,
    _parse_json_output,
    _to_gemini_schema,
    configured_base_url,
    configured_model,
    llm_provider,
)
from app.supplier_drafting.schemas import SUPPLIER_EMAIL_DRAFT_JSON_SCHEMA


def _system_message() -> str:
    return (
        "You are a supplier evidence request drafting assistant inside Circular Industry AI. "
        "You draft cautious, professional supplier emails from locked circular procurement, recommendation and evidence data. "
        "Do not make decisions. Do not verify claims. Do not invent supplier capability, legal compliance, take-back availability, "
        "route acceptance, verified waste diversion, verified cost savings or carbon savings. "
        "Use the supplied locked fields only. If risk is high, blocked or human review is required, frame the email as an evidence/compliance request only, not an implementation request. "
        "Return only valid JSON matching the schema."
    )


def _call_openai_supplier_email(context: dict[str, Any]) -> dict[str, Any]:
    api_key = _api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    request_body = {
        "model": configured_model(),
        "input": [
            {"role": "system", "content": _system_message()},
            {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "circular_ai_supplier_email_draft",
                "schema": SUPPLIER_EMAIL_DRAFT_JSON_SCHEMA,
                "strict": True,
            }
        },
    }

    data = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=llm_timeout_seconds()) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API request failed: {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI API request failed: {exc.reason}") from exc

    output_text = _extract_openai_output_text(response_payload)
    if not output_text:
        raise RuntimeError("OpenAI response did not include structured output text.")
    return _parse_json_output(output_text)


def _call_gemini_supplier_email(context: dict[str, Any]) -> dict[str, Any]:
    api_key = _api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    base_url = configured_base_url().rstrip("/")
    model = configured_model()
    encoded_model = urllib.parse.quote(model, safe="")
    url = f"{base_url}/models/{encoded_model}:generateContent"

    request_body = {
        "systemInstruction": {"parts": [{"text": _system_message()}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Use the supplied locked Circular Industry AI supplier-loop context to draft the JSON email object.\n"
                            "Context JSON:\n"
                            f"{json.dumps(context, ensure_ascii=False)}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": _to_gemini_schema(SUPPLIER_EMAIL_DRAFT_JSON_SCHEMA),
        },
    }

    data = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=llm_timeout_seconds()) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API request failed: {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Gemini API request failed: {exc.reason}") from exc

    output_text = _extract_gemini_text(response_payload)
    if not output_text:
        raise RuntimeError("Gemini response did not include structured output text.")
    return _parse_json_output(output_text)


def call_structured_supplier_email(context: dict[str, Any]) -> dict[str, Any]:
    provider = llm_provider()
    if provider == "gemini":
        return _call_gemini_supplier_email(context)
    if provider != "openai":
        raise RuntimeError(f"Unsupported LLM_PROVIDER '{provider}'. Use 'openai' or 'gemini'.")
    return _call_openai_supplier_email(context)

