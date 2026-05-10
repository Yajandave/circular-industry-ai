"""Workspace and analysis-run metadata tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_workspace_context_bootstraps_default_metadata():
    response = client.get("/api/workspace/context")
    assert response.status_code == 200
    payload = response.json()
    assert payload["organisation"]["organisation_name"] == "Default Organisation"
    assert payload["site"]["site_name"] == "Default Manufacturing Site"
    assert payload["data_model_stage"] == "Alpha 9D metadata foundation"
    assert "governance_note" in payload


def test_analysis_run_snapshot_captures_current_workflow_state(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")

    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post("/api/workspace/analysis-runs/snapshot")
    assert response.status_code == 200
    snapshot = response.json()
    assert snapshot["stream_count"] >= 40
    assert snapshot["recommendation_count"] >= 40
    assert snapshot["run_status"] == "snapshot_created"
    assert snapshot["decision_source"] == "locked_rules_engine"

    list_response = client.get("/api/workspace/analysis-runs")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1
