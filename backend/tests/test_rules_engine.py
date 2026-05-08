"""Rules engine checks for Milestone 3."""

from fastapi.testclient import TestClient

from app.main import app
from app.rules_engine import recommend_for_stream
from app.schemas import IndustrialStreamCreate

client = TestClient(app)


def _make_stream(**overrides):
    base = dict(
        stream_id="T001",
        stream_name="Clean aluminium offcuts",
        material="metals",
        source_process="CNC machining",
        monthly_quantity_kg=1000.0,
        current_route="sold as mixed scrap",
        disposal_cost_per_month=200.0,
        contamination_risk="low",
        hazardous_flag="false",
        department="Manufacturing",
        supplier="Test Supplier Ltd",
        supplier_takeback_available="unknown",
        recycled_content_available="yes",
        notes="Clean segregated metal stream.",
    )
    base.update(overrides)
    return IndustrialStreamCreate(**base)


def test_clean_metal_stream_gets_closed_loop_review():
    recommendation = recommend_for_stream(_make_stream())
    assert recommendation.circular_strategy_category == "closed-loop recycling"
    assert recommendation.risk_level == "low"
    assert recommendation.human_review_required is False
    assert recommendation.estimated_annual_waste_diverted_kg == 12000.0


def test_hazardous_high_contamination_stream_requires_human_review():
    recommendation = recommend_for_stream(
        _make_stream(
            material="chemicals/solvents",
            stream_name="Spent solvent",
            contamination_risk="high",
            hazardous_flag="true",
            current_route="hazardous waste contractor",
        )
    )
    assert recommendation.human_review_required is True
    assert recommendation.risk_level == "blocked"
    assert recommendation.circular_strategy_category == "human review required"
    assert recommendation.estimated_annual_waste_diverted_kg == 0.0


def test_supplier_takeback_rule_is_prioritised_for_packaging():
    recommendation = recommend_for_stream(
        _make_stream(
            stream_name="Returnable plastic crates",
            material="cardboard/packaging",
            current_route="single use recycling",
            supplier_takeback_available="yes",
            notes="Supplier take-back available for repeated packaging stream.",
        )
    )
    assert recommendation.circular_strategy_category == "supplier take-back / circular procurement"
    assert "supplier" in recommendation.supplier_procurement_action.lower()


def test_run_recommendations_endpoint_creates_outputs():
    load_response = client.post("/api/streams/load-sample")
    assert load_response.status_code == 200

    run_response = client.post("/api/recommendations/run")
    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["analysed_streams"] >= 40
    assert payload["recommendations_created"] == payload["analysed_streams"]
    assert payload["human_review_required"] > 0

    list_response = client.get("/api/recommendations")
    assert list_response.status_code == 200
    recs = list_response.json()
    assert len(recs) >= 40
    assert "recommended_circular_action" in recs[0]


def test_s001_recommendation_is_available_after_rules_run():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.get("/api/recommendations/S001")
    assert response.status_code == 200
    recommendation = response.json()
    assert recommendation["stream_id"] == "S001"
    assert recommendation["circular_strategy_category"] == "closed-loop recycling"
    assert recommendation["risk_level"] == "low"
    assert "alloy" in recommendation["missing_data"].lower()


def test_recommendation_summary_endpoint():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.get("/api/recommendations/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_recommendations"] >= 40
    assert summary["human_review_required"] > 0
    assert summary["total_estimated_annual_disposal_cost_avoided"] >= 0
