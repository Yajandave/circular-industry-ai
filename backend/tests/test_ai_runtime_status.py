"""AI runtime reliability endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ai_runtime_status_reports_fallback_when_disabled(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    response = client.get("/api/ai-runtime/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_mode"] == "fallback_ai_disabled"
    assert payload["fallback_available"] is True
    assert payload["timeout_seconds"] >= 1
    assert "Rules engine" in payload["guardrail_summary"]


def test_ai_runtime_status_reports_missing_key_when_enabled_without_key(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.get("/api/ai-runtime/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_mode"] in {"fallback_key_missing", "ai_on"}
    assert payload["fallback_available"] is True
