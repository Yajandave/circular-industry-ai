"""Optional rules-locked LLM client with OpenAI and Gemini support.

This project keeps the LLM layer optional. If AI_REASONING_ENABLED is false,
no API key is configured, or the request fails, the app falls back to a fully
deterministic rules-locked narrative.

Supported providers:
- openai: OpenAI Responses API
- gemini: Gemini Developer API with structured JSON output
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.llm_reasoning.schemas import AI_REASONING_JSON_SCHEMA

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

_ENV_LOADED = False


def _load_local_env_once() -> None:
    """Load backend/.env or project .env using only the standard library.

    This avoids adding python-dotenv as a required dependency and keeps API keys
    out of the frontend. Existing environment variables win over .env values.
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True

    candidates = [
        Path.cwd() / ".env",
        Path.cwd() / "backend" / ".env",
        Path(__file__).resolve().parents[2] / ".env",  # backend/app -> backend
        Path(__file__).resolve().parents[3] / ".env",  # repo root
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def _env(name: str, default: str | None = None) -> str | None:
    _load_local_env_once()
    return os.getenv(name, default)


def llm_provider() -> str:
    provider = (_env("LLM_PROVIDER", "openai") or "openai").strip().lower()
    if provider in {"google", "google_gemini"}:
        return "gemini"
    return provider


def ai_reasoning_enabled() -> bool:
    return (_env("AI_REASONING_ENABLED", "false") or "false").strip().lower() in {"1", "true", "yes", "on"}


def configured_model() -> str:
    explicit = _env("OPENAI_MODEL")
    if explicit:
        return explicit
    if llm_provider() == "gemini":
        return "gemini-2.5-flash"
    return "gpt-5-mini"


def llm_timeout_seconds() -> int:
    """Return the configured LLM request timeout in seconds.

    Keep a bounded timeout so AI features cannot hang the product workflow.
    """
    raw_value = _env("LLM_TIMEOUT_SECONDS", "20") or "20"
    try:
        timeout = int(raw_value)
    except ValueError:
        timeout = 20
    return max(3, min(timeout, 60))

def configured_base_url() -> str:
    if llm_provider() == "gemini":
        return _env("GEMINI_API_BASE_URL", GEMINI_API_BASE_URL) or GEMINI_API_BASE_URL
    return _env("OPENAI_BASE_URL", OPENAI_RESPONSES_URL) or OPENAI_RESPONSES_URL


def _api_key() -> str | None:
    if llm_provider() == "gemini":
        return _env("GEMINI_API_KEY") or _env("OPENAI_API_KEY")
    return _env("OPENAI_API_KEY")


def api_key_configured() -> bool:
    return bool(_api_key())


def _system_message() -> str:
    return (
        "You are a circular economy reasoning assistant inside Circular Industry AI. "
        "You must not make decisions. The rules engine is the locked source of truth. "
        "Do not change risk level, human review status, rule applied, claim boundaries, or recommended route. "
        "Do not invent supplier capability, legal compliance, verified savings, verified diversion, or carbon savings. "
        "Write specific, practical, evidence-controlled reasoning for a human reviewer. "
        "Return only valid JSON matching the requested schema."
    )


def _extract_openai_output_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    texts: list[str] = []
    for item in payload.get("output", []) or []:
        for content in item.get("content", []) or []:
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str):
                    texts.append(text)
    return "\n".join(texts)


def _extract_gemini_text(payload: dict[str, Any]) -> str:
    texts: list[str] = []
    for candidate in payload.get("candidates", []) or []:
        content = candidate.get("content") or {}
        for part in content.get("parts", []) or []:
            text = part.get("text")
            if isinstance(text, str):
                texts.append(text)
    return "\n".join(texts)


def _to_gemini_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert the project JSON schema into Gemini's structured-output schema subset."""
    type_map = {
        "object": "OBJECT",
        "array": "ARRAY",
        "string": "STRING",
        "integer": "INTEGER",
        "number": "NUMBER",
        "boolean": "BOOLEAN",
    }
    converted: dict[str, Any] = {}
    schema_type = schema.get("type")
    if isinstance(schema_type, str):
        converted["type"] = type_map.get(schema_type.lower(), schema_type.upper())

    if "properties" in schema and isinstance(schema["properties"], dict):
        converted["properties"] = {
            key: _to_gemini_schema(value)
            for key, value in schema["properties"].items()
            if isinstance(value, dict)
        }
        converted["propertyOrdering"] = list(schema["properties"].keys())

    if "items" in schema and isinstance(schema["items"], dict):
        converted["items"] = _to_gemini_schema(schema["items"])

    if "required" in schema and isinstance(schema["required"], list):
        converted["required"] = schema["required"]

    if "enum" in schema and isinstance(schema["enum"], list):
        converted["enum"] = schema["enum"]

    if "description" in schema and isinstance(schema["description"], str):
        converted["description"] = schema["description"]

    return converted


def _parse_json_output(output_text: str) -> dict[str, Any]:
    text = output_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def _call_openai_structured_reasoning(context: dict[str, Any]) -> dict[str, Any]:
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
                "name": "circular_ai_reasoning",
                "schema": AI_REASONING_JSON_SCHEMA,
                "strict": True,
            }
        },
    }

    effort = _env("OPENAI_REASONING_EFFORT")
    if effort:
        request_body["reasoning"] = {"effort": effort}

    data = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
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


def _call_gemini_structured_reasoning(context: dict[str, Any]) -> dict[str, Any]:
    api_key = _api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    base_url = configured_base_url().rstrip("/")
    model = configured_model()
    encoded_model = urllib.parse.quote(model, safe="")
    url = f"{base_url}/models/{encoded_model}:generateContent"

    request_body = {
        "systemInstruction": {
            "parts": [{"text": _system_message()}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Use the supplied Circular Industry AI context to produce the JSON reasoning object.\n"
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
            "responseSchema": _to_gemini_schema(AI_REASONING_JSON_SCHEMA),
        },
    }

    data = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
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


def call_structured_reasoning(context: dict[str, Any]) -> dict[str, Any]:
    provider = llm_provider()
    if provider == "gemini":
        return _call_gemini_structured_reasoning(context)
    if provider != "openai":
        raise RuntimeError(f"Unsupported LLM_PROVIDER '{provider}'. Use 'openai' or 'gemini'.")
    return _call_openai_structured_reasoning(context)

