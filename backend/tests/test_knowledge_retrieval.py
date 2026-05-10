"""Knowledge retrieval engine tests."""

from fastapi.testclient import TestClient

from app.knowledge_base.retriever import retrieve_knowledge_for_stream
from app.main import app

client = TestClient(app)


def test_retriever_matches_plastics_and_future_horizon_from_raw_stream():
    stream = {
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

    result = retrieve_knowledge_for_stream(stream)
    material_families = {item["material_family"] for item in result["matched_materials"]}
    future_ids = {item["knowledge_id"] for item in result["future_horizon"]}
    evidence_ids = {item["knowledge_id"] for item in result["evidence_rules"]}

    assert "plastics" in material_families
    assert "cardboard_packaging" not in material_families
    assert "batteries" not in material_families
    assert "future_plastics_advanced_recycling_v1" in future_ids
    assert "future_battery_recycling_v1" not in future_ids
    assert "evidence_claim_readiness_v1" in evidence_ids
    assert result["governance_note"]


def test_knowledge_validate_endpoint_reports_valid_seed_base():
    response = client.get("/api/knowledge/validate")
    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["counts"]["materials"] >= 6
    assert payload["source_count"] >= 6


def test_knowledge_match_endpoint_accepts_blank_notes_raw_input():
    payload = {
        "stream_id": "RAW002",
        "stream_name": "Aluminium machining offcuts",
        "material": "aluminium",
        "source_process": "CNC machining",
        "monthly_quantity_kg": 1850,
        "current_route": "scrap merchant",
        "disposal_cost_per_month": 420,
        "contamination_risk": "low",
        "hazardous_flag": "false",
        "department": "Machining",
        "supplier": "AluForm Metals Ltd",
        "supplier_takeback_available": "unknown",
        "recycled_content_available": "unknown",
        "notes": "",
    }

    response = client.post("/api/knowledge/match", json=payload)
    assert response.status_code == 200
    result = response.json()
    families = {item["material_family"] for item in result["matched_materials"]}
    routes = {item["route"] for item in result["matched_routes"]}

    assert "metals" in families
    assert "closed_loop_recycling" in routes or "supplier_takeback" in routes


def test_knowledge_stream_endpoint_matches_existing_sample_stream(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    client.post("/api/streams/load-sample")

    response = client.get("/api/knowledge/stream/S008")
    assert response.status_code == 200
    result = response.json()
    families = {item["material_family"] for item in result["matched_materials"]}

    assert "plastics" in families
    assert result["evidence_rules"]


def test_retriever_does_not_match_generic_words_only():
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

    result = retrieve_knowledge_for_stream(stream)
    assert result["matched_materials"] == []
    assert any("No material-family knowledge matched" in note for note in result["retrieval_notes"])
