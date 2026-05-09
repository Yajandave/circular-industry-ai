"""Tests for Milestone 7 evidence register endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _prepare_recommendations():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")


def test_evidence_register_returns_records():
    _prepare_recommendations()
    response = client.get("/api/evidence-register")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 50
    first = data[0]
    assert "evidence_status" in first
    assert "claim_readiness" in first
    assert "claim_boundary" in first


def test_evidence_summary_contains_governance_metrics():
    _prepare_recommendations()
    response = client.get("/api/evidence-register/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 50
    assert data["human_review_required"] >= 1
    assert "governance_note" in data


def test_evidence_csv_export_is_available():
    _prepare_recommendations()
    response = client.get("/api/export/evidence-register.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "stream_id" in response.text
    assert "claim_readiness" in response.text


def test_recommendations_csv_export_is_available():
    _prepare_recommendations()
    response = client.get("/api/export/recommendations.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "recommended_circular_action" in response.text
