"""Milestone 11A knowledge graph relationship tests."""

from fastapi.testclient import TestClient

from app.knowledge_graph.service import build_stream_knowledge_graph
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


def test_stream_graph_maps_blank_notes_plastics_without_false_materials():
    result = build_stream_knowledge_graph(RAW_PLASTICS_STREAM)

    assert result["graph_scope"] == "stream_match"
    assert result["stream_id"] == "RAW001"
    assert result["matched_material_families"] == ["plastics"]
    assert "material_plastics_v1" in result["source_knowledge_ids"]
    assert "future_battery_recycling_v1" not in result["source_knowledge_ids"]

    node_ids = {node["node_id"] for node in result["nodes"]}
    assert "stream:RAW001" in node_ids
    assert "material:plastics" in node_ids
    assert not any(node_id == "material:batteries" for node_id in node_ids)
    assert not any(node_id == "material:cardboard_packaging" for node_id in node_ids)


def test_stream_graph_contains_route_evidence_claim_and_future_relationships():
    result = build_stream_knowledge_graph(RAW_PLASTICS_STREAM)

    relationships = {edge["relationship"] for edge in result["edges"]}
    node_types = {node["node_type"] for node in result["nodes"]}

    assert "matches_material_family" in relationships
    assert "has_candidate_route" in relationships
    assert "requires_evidence" in relationships or "requires_data" in relationships
    assert "must_not_claim" in relationships
    assert "future_horizon" in node_types
    assert "claim_boundary" in node_types
    assert result["graph_path"]


def test_knowledge_graph_catalog_endpoint_returns_catalog():
    response = client.get("/api/knowledge/graph")
    assert response.status_code == 200

    payload = response.json()
    assert payload["graph_scope"] == "knowledge_catalog"
    assert payload["nodes"]
    assert payload["edges"]
    assert payload["knowledge_validation"]["valid"] is True


def test_knowledge_graph_match_endpoint_accepts_raw_blank_notes():
    response = client.post("/api/knowledge/graph/match", json=RAW_PLASTICS_STREAM)
    assert response.status_code == 200

    payload = response.json()
    assert payload["stream_id"] == "RAW001"
    assert payload["matched_material_families"] == ["plastics"]
    assert "material_plastics_v1" in payload["source_knowledge_ids"]


def test_knowledge_graph_existing_stream_endpoint(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    client.post("/api/streams/load-sample")

    response = client.get("/api/knowledge/graph/stream/S008")
    assert response.status_code == 200

    payload = response.json()
    assert payload["stream_id"] == "S008"
    assert "plastics" in payload["matched_material_families"]
    assert payload["nodes"]
    assert payload["edges"]
