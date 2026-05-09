"""Product-grade workflow smoke tests for Alpha hardening."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_product_workflow_readiness_blocks_before_data(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")

    # The endpoint should always respond, even before a usable workflow exists.
    response = client.get("/api/diagnostics/workflow-readiness")
    assert response.status_code == 200
    payload = response.json()
    assert payload["backend_status"] == "ready"
    assert "steps" in payload


def test_full_local_product_workflow_with_ai_fallback(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")

    load_response = client.post("/api/streams/load-sample")
    assert load_response.status_code == 200

    run_response = client.post("/api/recommendations/run")
    assert run_response.status_code == 200
    assert run_response.json()["recommendations_created"] >= 40

    evidence_response = client.get("/api/evidence-register/summary")
    assert evidence_response.status_code == 200
    assert evidence_response.json()["total_records"] >= 40

    supplier_response = client.get("/api/procurement/supplier-loops/summary")
    assert supplier_response.status_code == 200
    assert supplier_response.json()["total_plans"] >= 40

    copilot_response = client.get("/api/ai-copilot/site-summary")
    assert copilot_response.status_code == 200
    assert copilot_response.json()["decision_lock_status"].startswith("Rules engine locked")

    evidence_explainer_response = client.post("/api/evidence-register/S001/ai-explainer")
    assert evidence_explainer_response.status_code == 200
    assert evidence_explainer_response.json()["stream_id"] == "S001"
    assert evidence_explainer_response.json()["locked_rule_applied"]

    supplier_email_response = client.post("/api/procurement/supplier-loops/S001/email-draft")
    assert supplier_email_response.status_code == 200
    assert supplier_email_response.json()["stream_id"] == "S001"
    assert "verified" in supplier_email_response.json()["claim_safety_note"].lower()

    report_response = client.post("/api/reports/streams/S001/circular-action-report")
    assert report_response.status_code == 200
    assert report_response.json()["stream_id"] == "S001"
    assert report_response.json()["locked_recommendation"]

    readiness_response = client.get("/api/diagnostics/workflow-readiness")
    assert readiness_response.status_code == 200
    readiness = readiness_response.json()
    assert readiness["ready_for_full_demo"] is True
    assert readiness["total_streams"] >= 40
    assert readiness["total_recommendations"] >= 40
