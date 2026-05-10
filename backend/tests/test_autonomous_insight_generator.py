"""Autonomous insight generator tests."""

from fastapi.testclient import TestClient

from app.insight_generator.service import generate_autonomous_insight
from app.main import app

client = TestClient(app)


def _raw_plastics_stream():
    return {
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


def test_autonomous_insight_generates_from_blank_notes():
    result = generate_autonomous_insight(_raw_plastics_stream())

    assert result["input_notes_present"] is False
    assert result["notes_dependency"] == "not_required"
    assert "plastics" in result["matched_material_families"]
    assert "cardboard_packaging" not in result["matched_material_families"]
    assert "batteries" not in result["matched_material_families"]
    assert "contamination" in result["current_action"]["content"].lower()
    assert result["evidence_needed"]
    assert result["supplier_questions"]
    assert result["do_not_claim"]
    assert "future_plastics_advanced_recycling_v1" in result["source_knowledge_ids"]


def test_autonomous_insight_endpoint_accepts_raw_stream_without_notes():
    response = client.post("/api/insights/generate", json=_raw_plastics_stream())
    assert response.status_code == 200
    payload = response.json()

    assert payload["notes_dependency"] == "not_required"
    assert payload["current_action"]["title"] == "Current action"
    assert payload["near_future_action"]["title"] == "Near-future action"
    assert payload["future_watch"]["title"] == "Future watch"
    assert "verified" in " ".join(payload["do_not_claim"]).lower()


def test_existing_stream_insight_endpoint_uses_sample_data(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    client.post("/api/streams/load-sample")

    response = client.get("/api/insights/stream/S008")
    assert response.status_code == 200
    payload = response.json()

    assert payload["stream_id"] == "S008"
    assert payload["matched_material_families"]
    assert payload["claim_boundary"]
    assert payload["governance_note"]


def test_unknown_generic_stream_does_not_invent_material_specific_advice():
    stream = {
        "stream_id": "RAW004",
        "stream_name": "General production rejects",
        "material": "unknown",
        "source_process": "production",
        "monthly_quantity_kg": 100,
        "current_route": "general waste",
        "disposal_cost_per_month": 50,
        "contamination_risk": "unknown",
        "hazardous_flag": "unknown",
        "department": "Production",
        "supplier": "Unknown",
        "supplier_takeback_available": "unknown",
        "recycled_content_available": "unknown",
        "notes": "",
    }

    result = generate_autonomous_insight(stream)
    assert result["matched_material_families"] == []
    assert "No material-family knowledge matched" in result["insight_summary"]
    assert any("Hazardous status is true or unknown" in item for item in result["human_review_triggers"])
