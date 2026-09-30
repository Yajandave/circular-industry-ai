from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.intervention_scenario import build_intervention_scenario, build_intervention_scenario_comparison
from app.main import app

client = TestClient(app)


def _stream(**overrides):
    base = dict(
        stream_id="SCN-001",
        stream_name="Scenario test stream",
        material="metals",
        monthly_quantity_kg=20000 / 12,
        disposal_cost_per_month=500,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _recommendation(**overrides):
    base = dict(
        recommended_circular_action="Closed-loop recycling review",
        risk_level="low",
        confidence_score=82,
        evidence_quality_score=78,
        missing_data="alloy grade; recycler acceptance evidence",
        human_review_required=False,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_intervention_scenario_calculates_screened_recoverable_quantity():
    result = build_intervention_scenario(
        _stream(),
        _recommendation(),
        addressable_fraction_pct=80,
        technical_capture_rate_pct=85,
        route_acceptance_rate_pct=90,
    )

    assert result["baseline_annual_quantity_kg"] == 20000.0
    assert result["baseline_annual_disposal_cost_exposure"] == 6000.0
    assert result["scenario_screened_fraction_pct"] == 61.2
    assert result["scenario_screened_recoverable_quantity_kg"] == 12240.0
    assert result["scenario_status"] == "screening_ready"
    assert result["claim_status"] == "screening_only_not_claim_ready"
    assert "measured diversion" in result["governance_note"].lower()


def test_intervention_scenario_keeps_controlled_review_gate():
    result = build_intervention_scenario(
        _stream(),
        _recommendation(
            risk_level="blocked",
            human_review_required=True,
            evidence_quality_score=45,
        ),
        addressable_fraction_pct=100,
        technical_capture_rate_pct=100,
        route_acceptance_rate_pct=100,
    )

    assert result["scenario_screened_recoverable_quantity_kg"] == 20000.0
    assert result["scenario_status"] == "controlled_review_required"
    assert result["human_review_required"] is True
    assert result["claim_status"] == "screening_only_not_claim_ready"


def test_scenario_endpoint_requires_locked_recommendation_then_records_scenario():
    load_response = client.post("/api/streams/load-sample")
    assert load_response.status_code == 200

    before_run = client.post(
        "/api/scenarios/S001/screen",
        json={
            "addressable_fraction_pct": 80,
            "technical_capture_rate_pct": 85,
            "route_acceptance_rate_pct": 90,
        },
    )
    assert before_run.status_code == 409
    assert "Run POST /api/recommendations/run" in before_run.json()["detail"]

    run_response = client.post("/api/recommendations/run")
    assert run_response.status_code == 200

    stream_response = client.get("/api/streams/S001")
    assert stream_response.status_code == 200
    stream = stream_response.json()

    response = client.post(
        "/api/scenarios/S001/screen",
        json={
            "addressable_fraction_pct": 80,
            "technical_capture_rate_pct": 85,
            "route_acceptance_rate_pct": 90,
            "operator_note": "Initial screening assumption set.",
        },
    )
    assert response.status_code == 200
    scenario = response.json()

    expected_annual_quantity = round(stream["monthly_quantity_kg"] * 12, 2)
    expected_recoverable = round(expected_annual_quantity * 0.80 * 0.85 * 0.90, 2)

    assert scenario["stream_id"] == "S001"
    assert scenario["baseline_annual_quantity_kg"] == expected_annual_quantity
    assert scenario["scenario_screened_fraction_pct"] == 61.2
    assert scenario["scenario_screened_recoverable_quantity_kg"] == expected_recoverable
    assert scenario["candidate_route"]
    assert scenario["formula"].startswith("annual_stream_quantity_kg")
    assert any("Operator note" in item for item in scenario["assumptions"])

    audit_response = client.get(
        "/api/audit/events?event_type=intervention_scenario_screened&limit=20"
    )
    assert audit_response.status_code == 200
    event = next(
        item for item in audit_response.json()
        if item["entity_id"] == "S001"
    )
    assert event["metadata_json"]["scenario_screened_recoverable_quantity_kg"] == expected_recoverable
    assert event["metadata_json"]["claim_status"] == "screening_only_not_claim_ready"


def test_scenario_endpoint_rejects_percentage_above_100():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post(
        "/api/scenarios/S001/screen",
        json={
            "addressable_fraction_pct": 101,
            "technical_capture_rate_pct": 85,
            "route_acceptance_rate_pct": 90,
        },
    )

    assert response.status_code == 422



def test_intervention_scenario_comparison_reports_range_without_selecting_case():
    comparison = build_intervention_scenario_comparison(
        _stream(),
        _recommendation(),
        cases=[
            {
                "case_name": "Conservative",
                "addressable_fraction_pct": 50,
                "technical_capture_rate_pct": 60,
                "route_acceptance_rate_pct": 70,
                "operator_note": None,
            },
            {
                "case_name": "Working",
                "addressable_fraction_pct": 80,
                "technical_capture_rate_pct": 85,
                "route_acceptance_rate_pct": 90,
                "operator_note": None,
            },
            {
                "case_name": "Upper-screen",
                "addressable_fraction_pct": 95,
                "technical_capture_rate_pct": 95,
                "route_acceptance_rate_pct": 95,
                "operator_note": None,
            },
        ],
    )

    quantities = {
        item["case_name"]: item["scenario"]["scenario_screened_recoverable_quantity_kg"]
        for item in comparison["cases"]
    }
    assert quantities["Conservative"] == 4200.0
    assert quantities["Working"] == 12240.0
    assert quantities["Upper-screen"] == 17147.5
    assert comparison["minimum_screened_recoverable_quantity_kg"] == 4200.0
    assert comparison["maximum_screened_recoverable_quantity_kg"] == 17147.5
    assert comparison["screened_quantity_range_kg"] == 12947.5
    assert comparison["claim_status"] == "screening_comparison_only_not_claim_ready"
    assert "No case is selected or endorsed" in comparison["governance_note"]


def test_scenario_comparison_endpoint_records_one_audited_comparison():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post(
        "/api/scenarios/S001/compare",
        json={
            "cases": [
                {
                    "case_name": "Conservative",
                    "addressable_fraction_pct": 50,
                    "technical_capture_rate_pct": 60,
                    "route_acceptance_rate_pct": 70,
                },
                {
                    "case_name": "Working",
                    "addressable_fraction_pct": 80,
                    "technical_capture_rate_pct": 85,
                    "route_acceptance_rate_pct": 90,
                },
                {
                    "case_name": "Upper-screen",
                    "addressable_fraction_pct": 95,
                    "technical_capture_rate_pct": 95,
                    "route_acceptance_rate_pct": 95,
                },
            ]
        },
    )

    assert response.status_code == 200
    comparison = response.json()
    assert comparison["stream_id"] == "S001"
    assert len(comparison["cases"]) == 3
    assert comparison["minimum_screened_recoverable_quantity_kg"] <= comparison["maximum_screened_recoverable_quantity_kg"]

    audit_response = client.get(
        "/api/audit/events?event_type=intervention_scenarios_compared&limit=20"
    )
    assert audit_response.status_code == 200
    event = next(item for item in audit_response.json() if item["entity_id"] == "S001")
    assert event["metadata_json"]["case_count"] == 3
    assert event["metadata_json"]["case_names"] == ["Conservative", "Working", "Upper-screen"]
    assert event["metadata_json"]["claim_status"] == "screening_comparison_only_not_claim_ready"


def test_scenario_comparison_endpoint_rejects_duplicate_case_names():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post(
        "/api/scenarios/S001/compare",
        json={
            "cases": [
                {
                    "case_name": "Working",
                    "addressable_fraction_pct": 70,
                    "technical_capture_rate_pct": 80,
                    "route_acceptance_rate_pct": 90,
                },
                {
                    "case_name": "working",
                    "addressable_fraction_pct": 80,
                    "technical_capture_rate_pct": 85,
                    "route_acceptance_rate_pct": 90,
                },
            ]
        },
    )

    assert response.status_code == 400
    assert "case names must be unique" in response.json()["detail"].lower()



def test_saved_scenario_history_creates_immutable_revisions():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    first = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": "Supplier take-back pilot",
            "lifecycle_stage": "screening",
            "addressable_fraction_pct": 70,
            "technical_capture_rate_pct": 75,
            "route_acceptance_rate_pct": 80,
            "operator_note": "Initial screening assumptions.",
        },
    )
    assert first.status_code == 200
    first_saved = first.json()
    assert first_saved["revision_number"] == 1
    assert first_saved["lifecycle_stage"] == "screening"
    assert first_saved["claim_status"] == "screening_only_not_claim_ready"

    second = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": "Supplier take-back pilot",
            "lifecycle_stage": "pilot_planned",
            "addressable_fraction_pct": 75,
            "technical_capture_rate_pct": 80,
            "route_acceptance_rate_pct": 85,
            "operator_note": "Revised after supplier discussion.",
        },
    )
    assert second.status_code == 200
    second_saved = second.json()
    assert second_saved["revision_number"] == 2
    assert second_saved["lifecycle_stage"] == "pilot_planned"
    assert second_saved["id"] != first_saved["id"]
    assert second_saved["scenario_screened_recoverable_quantity_kg"] != first_saved["scenario_screened_recoverable_quantity_kg"]
    assert second_saved["claim_status"] == "screening_only_not_claim_ready"

    history_response = client.get("/api/scenarios/S001/history")
    assert history_response.status_code == 200
    history = history_response.json()

    matching = [
        record
        for record in history["records"]
        if record["scenario_name"] == "Supplier take-back pilot"
    ]
    assert len(matching) >= 2
    assert matching[0]["revision_number"] == 2
    assert matching[1]["revision_number"] == 1
    assert history["latest_revision"]["id"] == matching[0]["id"]
    assert "does not verify" in history["governance_note"].lower()


def test_saved_scenario_measured_unverified_stage_remains_not_claim_ready():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post(
        "/api/scenarios/S002/save",
        json={
            "scenario_name": "Observed pilot case",
            "lifecycle_stage": "measured_unverified",
            "addressable_fraction_pct": 60,
            "technical_capture_rate_pct": 70,
            "route_acceptance_rate_pct": 80,
            "operator_note": "Operational observation entered; evidence not independently verified.",
        },
    )

    assert response.status_code == 200
    saved = response.json()
    assert saved["lifecycle_stage"] == "measured_unverified"
    assert saved["claim_status"] == "screening_only_not_claim_ready"
    assert "not measured diversion" in saved["governance_note"].lower()


def test_saved_scenario_rejects_unsupported_lifecycle_stage():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": "Invalid verified case",
            "lifecycle_stage": "verified",
            "addressable_fraction_pct": 70,
            "technical_capture_rate_pct": 80,
            "route_acceptance_rate_pct": 90,
        },
    )

    assert response.status_code == 422
