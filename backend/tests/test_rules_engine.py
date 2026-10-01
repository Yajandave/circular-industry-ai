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


def test_hazardous_high_contamination_stream_requires_human_review_and_retains_exposure():
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
    # Annual quantity/cost remain available for screening even when route
    # selection is blocked. They are not achieved diversion or avoided cost.
    assert recommendation.estimated_annual_waste_diverted_kg == 12000.0
    assert recommendation.estimated_annual_disposal_cost_avoided == 2400.0


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



def test_damaged_battery_context_forces_high_risk_human_review_even_if_structured_flags_are_low():
    recommendation = recommend_for_stream(
        _make_stream(
            stream_name="Damaged swollen lithium-ion battery modules",
            material="batteries",
            contamination_risk="low",
            hazardous_flag="false",
            current_route="mixed recycling",
            notes="Several modules are damaged and swollen.",
        )
    )

    assert recommendation.rule_applied == "R001_HAZARDOUS_OR_UNKNOWN_REVIEW"
    assert recommendation.circular_strategy_category == "human review required"
    assert recommendation.risk_level == "high"
    assert recommendation.human_review_required is True
    assert "battery" in recommendation.recommended_circular_action.lower()
    assert "battery condition" in recommendation.missing_data.lower()


def test_unresolved_weee_classification_forces_review_before_recovery():
    recommendation = recommend_for_stream(
        _make_stream(
            stream_name="Mixed display and circuit-board assemblies",
            material="electronic components",
            contamination_risk="low",
            hazardous_flag="false",
            current_route="general recycling",
            notes="Hazardous substances and POPs classification has not been completed.",
        )
    )

    assert recommendation.rule_applied == "R001_HAZARDOUS_OR_UNKNOWN_REVIEW"
    assert recommendation.risk_level == "high"
    assert recommendation.human_review_required is True
    assert "classification" in recommendation.recommended_circular_action.lower()
    assert "weee" in recommendation.missing_data.lower()


def test_hazardous_residue_packaging_blocks_routine_reuse():
    recommendation = recommend_for_stream(
        _make_stream(
            stream_name="Solvent-contaminated return packaging",
            material="cardboard/packaging",
            contamination_risk="low",
            hazardous_flag="false",
            current_route="packaging reuse",
            notes="Packaging contains residues from a hazardous solvent product.",
        )
    )

    assert recommendation.rule_applied == "R001_HAZARDOUS_OR_UNKNOWN_REVIEW"
    assert recommendation.circular_strategy_category == "human review required"
    assert recommendation.risk_level == "high"
    assert recommendation.human_review_required is True
    assert "internal reuse" not in recommendation.recommended_circular_action.lower()
    assert "packaging classification" in recommendation.missing_data.lower()


def test_edible_food_surplus_prioritises_prevention_and_redistribution_before_recovery():
    recommendation = recommend_for_stream(
        _make_stream(
            stream_name="Unopened bakery surplus still fit for consumption",
            material="organic/process residue",
            source_process="finished goods overproduction",
            contamination_risk="low",
            hazardous_flag="false",
            current_route="anaerobic digestion",
            notes="Product remains within use-by date and fit for human consumption.",
        )
    )

    assert recommendation.rule_applied == "R003_REDUCE_AT_SOURCE"
    assert recommendation.circular_strategy_category == "reduce / process redesign"
    assert recommendation.risk_level == "low"
    assert recommendation.human_review_required is False
    assert "redistribut" in recommendation.recommended_circular_action.lower()
    assert "recovery" in recommendation.reasoning.lower()



def test_completed_nonhazardous_weee_classification_does_not_trigger_contextual_review():
    recommendation = recommend_for_stream(
        _make_stream(
            stream_name="Classified non-hazardous electronic component rejects",
            material="electronic components",
            contamination_risk="low",
            hazardous_flag="false",
            current_route="specialist recovery",
            notes="Classification completed; no hazardous properties identified.",
        )
    )

    assert recommendation.rule_applied == "R010_SPECIALIST_RECOVERY"
    assert recommendation.circular_strategy_category == "open-loop recycling / specialist recovery"
    assert recommendation.risk_level == "low"
    assert recommendation.human_review_required is False
