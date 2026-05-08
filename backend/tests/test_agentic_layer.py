from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _prepare_recommendations():
    load_response = client.post("/api/streams/load-sample")
    assert load_response.status_code == 200
    run_response = client.post("/api/recommendations/run")
    assert run_response.status_code == 200


def test_agentic_review_pack_keeps_rules_locked_for_s001():
    _prepare_recommendations()

    rec_response = client.get("/api/recommendations/S001")
    assert rec_response.status_code == 200
    recommendation = rec_response.json()

    pack_response = client.get("/api/agent/review-pack/S001")
    assert pack_response.status_code == 200
    pack = pack_response.json()

    assert pack["decision_locked_by_rules"] is True
    assert pack["rule_applied"] == recommendation["rule_applied"]
    assert pack["base_recommendation"]["recommended_circular_action"] == recommendation["recommended_circular_action"]
    assert pack["risk_review"]["locked_controls"]
    assert "evidence_audit" in pack
    assert "procurement_review" in pack


def test_agentic_review_pack_preserves_high_risk_human_review():
    _prepare_recommendations()

    pack_response = client.get("/api/agent/review-pack/S022")
    assert pack_response.status_code == 200
    pack = pack_response.json()

    assert pack["base_recommendation"]["human_review_required"] is True
    assert pack["risk_review"]["human_review_required"] is True
    assert "EHS or competent environmental compliance review" in pack["risk_review"]["review_gates"]
    assert any("cannot lower risk" in control for control in pack["risk_review"]["locked_controls"])


def test_agentic_management_summary_returns_portfolio_metrics():
    _prepare_recommendations()

    response = client.get("/api/agent/management-summary")
    assert response.status_code == 200
    summary = response.json()

    assert summary["total_recommendations"] == 50
    assert summary["human_review_required"] >= 1
    assert summary["decision_source"] == "rules_engine_locked_with_agentic_synthesis"
    assert len(summary["top_cost_avoidance_candidates"]) <= 5
    assert "decision-support" in summary["portfolio_note"]


def test_agentic_action_plan_groups_items_into_phases():
    _prepare_recommendations()

    response = client.get("/api/agent/action-plan?limit=10")
    assert response.status_code == 200
    plan = response.json()

    assert "ranking_method" in plan
    assert isinstance(plan["phases"], dict)
    assert plan["phases"]
    assert "claims" in plan["governance_note"]
