"""Milestone 10E insight history and traceability tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


RAW_PLASTICS_STREAM = {
    "stream_id": "RAW001",
    "stream_name": "Mixed polymer injection moulding rejects",
    "material": "mixed plastics",
    "source_process": "injection moulding",
    "monthly_quantity_kg": 1680,
    "current_route": "general waste",
    "disposal_cost_per_month": 720,
    "contamination_risk": "high",
    "hazardous_flag": "false",
    "department": "Production",
    "supplier": "PolyMax Resins",
    "supplier_takeback_available": "unknown",
    "recycled_content_available": "unknown",
    "notes": "",
}


def test_generate_and_save_persists_blank_notes_insight():
    response = client.post("/api/insights/generate-and-save", json=RAW_PLASTICS_STREAM)
    assert response.status_code == 200

    payload = response.json()
    assert payload["id"] > 0
    assert payload["stream_id"] == "RAW001"
    assert payload["input_notes_present"] is False
    assert payload["notes_dependency"] == "not_required"
    assert payload["generation_mode"] == "deterministic"
    assert payload["matched_material_families"] == ["plastics"]
    assert "material_plastics_v1" in payload["source_knowledge_ids"]
    assert payload["current_action"]["content"]
    assert payload["near_future_action"]["content"]
    assert payload["future_watch"]["content"]
    assert payload["claim_boundary"]
    assert payload["input_snapshot"]["notes"] == ""


def test_insight_history_and_latest_endpoints_return_saved_insight():
    saved = client.post("/api/insights/generate-and-save", json=RAW_PLASTICS_STREAM).json()

    history_response = client.get("/api/insights/history/RAW001")
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) >= 1
    assert history[0]["stream_id"] == "RAW001"
    assert history[0]["notes_dependency"] == "not_required"

    latest_response = client.get("/api/insights/latest/RAW001")
    assert latest_response.status_code == 200
    latest = latest_response.json()
    assert latest["stream_id"] == "RAW001"
    assert latest["id"] >= saved["id"]
    assert latest["source_knowledge_ids"]


def test_insight_history_list_can_filter_by_stream_id():
    client.post("/api/insights/generate-and-save", json=RAW_PLASTICS_STREAM)

    response = client.get("/api/insights/history", params={"stream_id": "RAW001", "limit": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(item["stream_id"] == "RAW001" for item in payload)


def test_generate_and_save_existing_loaded_stream_creates_audit_event(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    client.post("/api/streams/load-sample")

    response = client.post("/api/insights/stream/S008/generate-and-save")
    assert response.status_code == 200
    saved = response.json()
    assert saved["stream_id"] == "S008"
    assert saved["notes_dependency"] == "not_required"
    assert saved["source_knowledge_ids"]

    audit_response = client.get(
        "/api/audit/events",
        params={"event_type": "insight_generated", "entity_type": "stream", "limit": 20},
    )
    assert audit_response.status_code == 200
    events = audit_response.json()
    assert any(event["entity_id"] == "S008" for event in events)
