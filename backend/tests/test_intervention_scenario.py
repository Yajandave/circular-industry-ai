from types import SimpleNamespace
from uuid import uuid4

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
    scenario_name = f"Supplier take-back pilot {uuid4().hex[:10]}"

    first = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": scenario_name,
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
            "scenario_name": scenario_name,
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
        if record["scenario_name"] == scenario_name
    ]
    assert len(matching) >= 2
    assert matching[0]["revision_number"] == 2
    assert matching[1]["revision_number"] == 1
    assert history["latest_revision"]["id"] == matching[0]["id"]
    assert "does not verify" in history["governance_note"].lower()

    audit_response = client.get(
        "/api/audit/events?event_type=intervention_scenario_saved&limit=50"
    )
    assert audit_response.status_code == 200
    saved_event = next(
        event
        for event in audit_response.json()
        if event["entity_id"] == str(second_saved["id"])
    )
    assert saved_event["metadata_json"]["scenario_name"] == scenario_name
    assert saved_event["metadata_json"]["revision_number"] == 2
    assert saved_event["metadata_json"]["lifecycle_stage"] == "pilot_planned"


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



def test_saved_scenario_rejects_blank_name():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": "   ",
            "lifecycle_stage": "screening",
            "addressable_fraction_pct": 70,
            "technical_capture_rate_pct": 80,
            "route_acceptance_rate_pct": 90,
        },
    )

    assert response.status_code == 400
    assert "non-whitespace" in response.json()["detail"]



def test_observed_saved_scenario_requires_operator_note():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    response = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": "Observed without evidence note",
            "lifecycle_stage": "pilot_observed",
            "addressable_fraction_pct": 70,
            "technical_capture_rate_pct": 80,
            "route_acceptance_rate_pct": 90,
        },
    )

    assert response.status_code == 400
    assert "operator note" in response.json()["detail"].lower()



def test_observed_outcome_scales_saved_scenario_to_observation_period_and_persists_evidence():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")
    scenario_name = f"Observed outcome case {uuid4().hex[:10]}"

    saved_response = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": scenario_name,
            "lifecycle_stage": "pilot_planned",
            "addressable_fraction_pct": 80,
            "technical_capture_rate_pct": 85,
            "route_acceptance_rate_pct": 90,
            "operator_note": "Pilot assumptions approved for observation.",
        },
    )
    assert saved_response.status_code == 200
    saved = saved_response.json()

    outcome_response = client.post(
        f"/api/scenarios/saved/{saved['id']}/outcomes",
        json={
            "observation_start_date": "2026-01-01",
            "observation_end_date": "2026-01-31",
            "observed_recovered_quantity_kg": 500,
            "evidence_source_type": "weighbridge_ticket",
            "evidence_reference": "WB-2026-001 to WB-2026-014",
            "verification_status": "documentary_evidence_unverified",
            "operator_note": "January pilot weighbridge records entered for review.",
        },
    )
    assert outcome_response.status_code == 200
    outcome = outcome_response.json()

    expected_period_quantity = round(
        saved["scenario_screened_recoverable_quantity_kg"] * (31 / 365.0),
        2,
    )
    expected_variance = round(500 - expected_period_quantity, 2)
    expected_variance_pct = round((expected_variance / expected_period_quantity) * 100, 2)

    assert outcome["saved_scenario_id"] == saved["id"]
    assert outcome["scenario_revision_number"] == saved["revision_number"]
    assert outcome["observation_period_days"] == 31
    assert outcome["scenario_screened_quantity_for_period_kg"] == expected_period_quantity
    assert outcome["observed_recovered_quantity_kg"] == 500.0
    assert outcome["variance_quantity_kg"] == expected_variance
    assert outcome["variance_pct"] == expected_variance_pct
    assert outcome["claim_status"] == "observed_outcome_not_claim_ready"
    assert "not seasonality-adjusted" in outcome["governance_note"]

    history_response = client.get(
        f"/api/scenarios/saved/{saved['id']}/outcomes"
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["saved_scenario_id"] == saved["id"]
    assert history["total_records"] >= 1
    assert history["records"][0]["id"] == outcome["id"]
    assert "do not by themselves make the scenario verified" in history["governance_note"]

    audit_response = client.get(
        "/api/audit/events?event_type=observed_scenario_outcome_recorded&limit=50"
    )
    assert audit_response.status_code == 200
    event = next(
        item
        for item in audit_response.json()
        if item["entity_id"] == str(outcome["id"])
    )
    assert event["metadata_json"]["saved_scenario_id"] == saved["id"]
    assert event["metadata_json"]["observed_recovered_quantity_kg"] == 500.0
    assert event["metadata_json"]["claim_status"] == "observed_outcome_not_claim_ready"


def test_observed_outcome_rejects_end_date_before_start_date():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    saved = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": f"Invalid dates {uuid4().hex[:10]}",
            "lifecycle_stage": "pilot_planned",
            "addressable_fraction_pct": 70,
            "technical_capture_rate_pct": 80,
            "route_acceptance_rate_pct": 90,
        },
    ).json()

    response = client.post(
        f"/api/scenarios/saved/{saved['id']}/outcomes",
        json={
            "observation_start_date": "2026-02-10",
            "observation_end_date": "2026-02-01",
            "observed_recovered_quantity_kg": 100,
            "evidence_source_type": "operator_log",
            "evidence_reference": "Pilot log 01",
            "verification_status": "operator_reported",
        },
    )

    assert response.status_code == 400
    assert "end date" in response.json()["detail"].lower()


def test_observed_outcome_rejects_blank_evidence_reference():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    saved = client.post(
        "/api/scenarios/S002/save",
        json={
            "scenario_name": f"Blank evidence {uuid4().hex[:10]}",
            "lifecycle_stage": "pilot_planned",
            "addressable_fraction_pct": 60,
            "technical_capture_rate_pct": 70,
            "route_acceptance_rate_pct": 80,
        },
    ).json()

    response = client.post(
        f"/api/scenarios/saved/{saved['id']}/outcomes",
        json={
            "observation_start_date": "2026-03-01",
            "observation_end_date": "2026-03-07",
            "observed_recovered_quantity_kg": 50,
            "evidence_source_type": "operator_log",
            "evidence_reference": "   ",
            "verification_status": "operator_reported",
        },
    )

    assert response.status_code == 400
    assert "evidence reference" in response.json()["detail"].lower()


def test_observed_outcome_rejects_unsupported_verification_status():
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    saved = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": f"Unsupported verification {uuid4().hex[:10]}",
            "lifecycle_stage": "pilot_planned",
            "addressable_fraction_pct": 70,
            "technical_capture_rate_pct": 80,
            "route_acceptance_rate_pct": 90,
        },
    ).json()

    response = client.post(
        f"/api/scenarios/saved/{saved['id']}/outcomes",
        json={
            "observation_start_date": "2026-04-01",
            "observation_end_date": "2026-04-30",
            "observed_recovered_quantity_kg": 100,
            "evidence_source_type": "system_export",
            "evidence_reference": "ERP-APR-2026",
            "verification_status": "independently_verified",
        },
    )

    assert response.status_code == 422



def _create_reviewable_observed_outcome(*, verification_status="internally_reviewed", source_type="weighbridge_ticket"):
    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    saved = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": f"Verification gate {uuid4().hex[:10]}",
            "lifecycle_stage": "pilot_planned",
            "addressable_fraction_pct": 80,
            "technical_capture_rate_pct": 85,
            "route_acceptance_rate_pct": 90,
            "operator_note": "Scenario saved for evidence-gate testing.",
        },
    ).json()

    response = client.post(
        f"/api/scenarios/saved/{saved['id']}/outcomes",
        json={
            "observation_start_date": "2026-05-01",
            "observation_end_date": "2026-05-31",
            "observed_recovered_quantity_kg": 640,
            "evidence_source_type": source_type,
            "evidence_reference": f"EVID-{uuid4().hex[:8]}",
            "verification_status": verification_status,
            "operator_note": "Observed record prepared for internal evidence review.",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_complete_internally_reviewed_documentary_evidence_supports_narrow_internal_statement():
    outcome = _create_reviewable_observed_outcome()

    response = client.post(
        f"/api/scenarios/outcomes/{outcome['id']}/reviews",
        json={
            "reviewer_name": "Internal Reviewer",
            "reviewer_role": "Sustainability Assurance",
            "evidence_completeness": "complete",
            "source_traceability_confirmed": True,
            "quantity_basis_confirmed": True,
            "period_basis_confirmed": True,
            "route_destination_confirmed": True,
            "review_note": "Weighbridge references and period totals reconciled to the internal record.",
        },
    )

    assert response.status_code == 200
    review = response.json()
    assert review["verification_decision"] == "internally_supported_with_route_context"
    assert review["internal_claim_readiness"] == "internal_factual_reporting_ready"
    assert review["external_claim_readiness"] == "external_verification_required"
    assert "640 kg" in review["allowed_internal_statement"]
    assert "recorded recovered quantity" in review["allowed_internal_statement"]
    assert "route or destination evidence confirmed" in review["allowed_internal_statement"]
    assert "carbon or greenhouse-gas savings" in review["blocked_claims"]
    assert review["missing_checks"] == []

    history_response = client.get(
        f"/api/scenarios/outcomes/{outcome['id']}/reviews"
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["total_reviews"] >= 1
    assert history["latest_review"]["id"] == review["id"]
    assert "external claims remain gated" in history["governance_note"].lower()

    audit_response = client.get(
        "/api/audit/events?event_type=observed_outcome_evidence_reviewed&limit=50"
    )
    assert audit_response.status_code == 200
    event = next(
        item
        for item in audit_response.json()
        if item["entity_id"] == str(review["id"])
    )
    assert event["metadata_json"]["verification_decision"] == "internally_supported_with_route_context"
    assert event["metadata_json"]["external_claim_readiness"] == "external_verification_required"


def test_internal_gate_can_support_observed_quantity_without_confirming_destination():
    outcome = _create_reviewable_observed_outcome()

    response = client.post(
        f"/api/scenarios/outcomes/{outcome['id']}/reviews",
        json={
            "reviewer_name": "Internal Reviewer",
            "reviewer_role": "Operations Review",
            "evidence_completeness": "complete",
            "source_traceability_confirmed": True,
            "quantity_basis_confirmed": True,
            "period_basis_confirmed": True,
            "route_destination_confirmed": False,
            "review_note": "Quantity and dates reconciled; destination evidence remains outstanding.",
        },
    )

    assert response.status_code == 200
    review = response.json()
    assert review["verification_decision"] == "internally_supported_observed_quantity"
    assert review["internal_claim_readiness"] == "internal_factual_reporting_ready"
    assert "destination or circular route is not confirmed" in review["allowed_internal_statement"]
    assert review["external_claim_readiness"] == "external_verification_required"


def test_operator_reported_outcome_cannot_pass_internal_claim_gate():
    outcome = _create_reviewable_observed_outcome(
        verification_status="operator_reported",
        source_type="weighbridge_ticket",
    )

    response = client.post(
        f"/api/scenarios/outcomes/{outcome['id']}/reviews",
        json={
            "reviewer_name": "Internal Reviewer",
            "reviewer_role": "Sustainability Assurance",
            "evidence_completeness": "complete",
            "source_traceability_confirmed": True,
            "quantity_basis_confirmed": True,
            "period_basis_confirmed": True,
            "route_destination_confirmed": True,
            "review_note": "Review inputs entered, but source record was never internally reviewed.",
        },
    )

    assert response.status_code == 200
    review = response.json()
    assert review["verification_decision"] == "evidence_insufficient_for_internal_claim"
    assert review["internal_claim_readiness"] == "not_ready"
    assert review["allowed_internal_statement"] is None
    assert "outcome_internally_reviewed" in review["missing_checks"]


def test_operator_log_alone_cannot_pass_documentary_evidence_gate():
    outcome = _create_reviewable_observed_outcome(
        verification_status="internally_reviewed",
        source_type="operator_log",
    )

    response = client.post(
        f"/api/scenarios/outcomes/{outcome['id']}/reviews",
        json={
            "reviewer_name": "Internal Reviewer",
            "reviewer_role": "Operations Review",
            "evidence_completeness": "complete",
            "source_traceability_confirmed": True,
            "quantity_basis_confirmed": True,
            "period_basis_confirmed": True,
            "route_destination_confirmed": False,
            "review_note": "Only an operator log is available; documentary evidence is still required.",
        },
    )

    assert response.status_code == 200
    review = response.json()
    assert review["internal_claim_readiness"] == "not_ready"
    assert "documentary_source_present" in review["missing_checks"]


def test_evidence_review_rejects_blank_reviewer_identity():
    outcome = _create_reviewable_observed_outcome()

    response = client.post(
        f"/api/scenarios/outcomes/{outcome['id']}/reviews",
        json={
            "reviewer_name": "   ",
            "reviewer_role": "Reviewer",
            "evidence_completeness": "complete",
            "source_traceability_confirmed": True,
            "quantity_basis_confirmed": True,
            "period_basis_confirmed": True,
            "route_destination_confirmed": False,
            "review_note": "Evidence was reviewed.",
        },
    )

    assert response.status_code == 400
    assert "reviewer name" in response.json()["detail"].lower()
