"""Milestone 11B deterministic agentic retrieval workflow tests."""

from fastapi.testclient import TestClient

from app.agentic_retrieval.service import run_agentic_retrieval_workflow
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


def test_agentic_retrieval_workflow_runs_deterministically_without_notes():
    result = run_agentic_retrieval_workflow(RAW_PLASTICS_STREAM)

    assert result["workflow_mode"] == "deterministic"
    assert result["stream_id"] == "RAW001"
    assert result["stream_context"]["input_notes_present"] is False
    assert result["stream_context"]["notes_dependency"] == "not_required"
    assert result["save_insight"] is False
    assert result["saved_insight_id"] is None
    assert len(result["steps"]) == 5
    assert result["retrieval_summary"]["matched_material_families"] == ["plastics"]
    assert "material_plastics_v1" in result["retrieval_summary"]["source_knowledge_ids"]
    assert "future_battery_recycling_v1" not in result["retrieval_summary"]["source_knowledge_ids"]
    assert result["graph"]["nodes"]
    assert result["graph"]["edges"]
    assert result["insight"]["current_action"]["content"]


def test_agentic_retrieval_quality_gates_include_notes_and_claim_boundary():
    result = run_agentic_retrieval_workflow(RAW_PLASTICS_STREAM)
    gates = {gate["gate"]: gate for gate in result["quality_gates"]}

    assert gates["notes_independence"]["status"] == "pass"
    assert gates["material_match"]["status"] == "pass"
    assert gates["claim_boundary_present"]["status"] == "pass"
    assert gates["graph_relationships_present"]["status"] == "pass"
    assert gates["human_review_control"]["status"] == "review"


def test_agentic_retrieval_run_endpoint_accepts_raw_input():
    response = client.post("/api/agentic-retrieval/run", json=RAW_PLASTICS_STREAM)
    assert response.status_code == 200

    payload = response.json()
    assert payload["workflow_mode"] == "deterministic"
    assert payload["stream_id"] == "RAW001"
    assert payload["save_insight"] is False
    assert payload["insight"]["notes_dependency"] == "not_required"
    assert payload["retrieval_summary"]["matched_material_families"] == ["plastics"]


def test_agentic_retrieval_run_and_save_persists_insight():
    response = client.post("/api/agentic-retrieval/run-and-save", json=RAW_PLASTICS_STREAM)
    assert response.status_code == 200

    payload = response.json()
    assert payload["save_insight"] is True
    assert payload["saved_insight_id"] is not None
    assert payload["insight"]["notes_dependency"] == "not_required"

    latest = client.get("/api/insights/latest/RAW001")
    assert latest.status_code == 200
    latest_payload = latest.json()
    assert latest_payload["id"] == payload["saved_insight_id"]
    assert latest_payload["source_knowledge_ids"]


def test_agentic_retrieval_existing_stream_endpoint(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    client.post("/api/streams/load-sample")

    response = client.get("/api/agentic-retrieval/stream/S008")
    assert response.status_code == 200

    payload = response.json()
    assert payload["stream_id"] == "S008"
    assert "plastics" in payload["retrieval_summary"]["matched_material_families"]
    assert payload["graph"]["nodes"]
    assert payload["steps"][0]["step_id"] == "01_classify_stream_context"
