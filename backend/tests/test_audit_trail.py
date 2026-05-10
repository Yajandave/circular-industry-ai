"""Audit trail and traceability tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_manual_audit_event_can_be_created_and_listed():
    payload = {
        "event_type": "manual_review_note",
        "entity_type": "workflow",
        "entity_id": "manual-test",
        "actor_type": "operator",
        "actor_id": "local-user",
        "source": "test",
        "action": "created manual audit note",
        "summary": "Manual audit event test.",
        "decision_source": "human_note",
        "claim_boundary": "This note does not verify operational impact.",
        "metadata_json": {"test": True},
    }

    response = client.post("/api/audit/events", json=payload)
    assert response.status_code == 200
    created = response.json()
    assert created["event_type"] == "manual_review_note"
    assert created["metadata_json"]["test"] is True

    list_response = client.get("/api/audit/events?event_type=manual_review_note")
    assert list_response.status_code == 200
    events = list_response.json()
    assert any(event["entity_id"] == "manual-test" for event in events)


def test_core_workflow_writes_audit_events(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")

    load_response = client.post("/api/streams/load-sample")
    assert load_response.status_code == 200

    run_response = client.post("/api/recommendations/run")
    assert run_response.status_code == 200

    snapshot_response = client.post("/api/workspace/analysis-runs/snapshot")
    assert snapshot_response.status_code == 200

    summary_response = client.get("/api/audit/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_events"] >= 3
    assert summary["event_type_breakdown"].get("dataset_loaded", 0) >= 1
    assert summary["event_type_breakdown"].get("rules_engine_run", 0) >= 1
    assert summary["event_type_breakdown"].get("analysis_run_snapshot", 0) >= 1
