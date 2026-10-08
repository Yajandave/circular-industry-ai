"""End-to-end regression for the external governance demo journey.

This test deliberately exercises the same sequence intended for a professional
review meeting while using an isolated in-memory database. It protects the
integration between data loading, deterministic recommendations, provenance,
human review routing, scenarios, evidence gating, disagreement governance and
blind review.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def isolated_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_external_governance_demo_journey_end_to_end(isolated_client):
    client = isolated_client

    # 1. Start from a clean, controlled sample dataset.
    load = client.post("/api/streams/load-sample")
    assert load.status_code == 200
    assert load.json()["loaded_rows"] == 50

    run = client.post("/api/recommendations/run")
    assert run.status_code == 200
    assert run.json()["recommendations_created"] == 50

    # 2. Inspect one rules-cleared material case with provenance and reviewer routing.
    rec_before = client.get("/api/recommendations/S001")
    assert rec_before.status_code == 200
    rec_before_json = rec_before.json()
    assert rec_before_json["rule_applied"] == "R005_METAL_CLOSED_LOOP"
    assert rec_before_json["risk_level"] == "low"
    assert rec_before_json["human_review_required"] is False
    assert rec_before_json["evidence_maturity"] in {
        "screening_ready",
        "screening_ready_with_checks",
    }

    pack = client.get("/api/agent/review-pack/S001")
    assert pack.status_code == 200
    pack_json = pack.json()
    assert pack_json["decision_locked_by_rules"] is True
    assert pack_json["rule_provenance"]["provenance_status"] == "internal_material_screening_rule"
    assert pack_json["rule_provenance"]["sources"]
    assert pack_json["review_governance"]["primary_reviewer_competence"]
    assert "silently overwrite" in pack_json["review_governance"]["override_policy"].lower()

    # 3. Confirm a review-gated case routes to competent review rather than routine optimisation.
    gated_pack = client.get("/api/agent/review-pack/S022")
    assert gated_pack.status_code == 200
    gated_json = gated_pack.json()
    assert gated_json["base_recommendation"]["human_review_required"] is True
    assert gated_json["review_governance"]["gate_status"] == "competent_human_review_required"
    assert gated_json["review_governance"]["second_review_recommended"] is True

    # 4. Screen and save an explicit intervention assumption case.
    scenario = client.post(
        "/api/scenarios/S001/screen",
        json={
            "addressable_fraction_pct": 80,
            "technical_capture_rate_pct": 85,
            "route_acceptance_rate_pct": 90,
            "operator_note": "Automated governance demo regression.",
        },
    )
    assert scenario.status_code == 200
    scenario_json = scenario.json()
    assert scenario_json["scenario_screened_recoverable_quantity_kg"] > 0
    assert scenario_json["claim_status"] == "screening_only_not_claim_ready"
    assert "verify" in scenario_json["governance_note"].lower() or "screen" in scenario_json["governance_note"].lower()

    saved = client.post(
        "/api/scenarios/S001/save",
        json={
            "scenario_name": "Governance demo regression",
            "lifecycle_stage": "screening",
            "addressable_fraction_pct": 80,
            "technical_capture_rate_pct": 85,
            "route_acceptance_rate_pct": 90,
            "operator_note": "Automated regression only.",
        },
    )
    assert saved.status_code == 200
    saved_json = saved.json()
    saved_id = saved_json["id"]
    assert saved_json["revision_number"] == 1
    assert saved_json["lifecycle_stage"] == "screening"

    # 5. Record observed documentary evidence and pass only the narrow internal factual gate.
    outcome = client.post(
        f"/api/scenarios/saved/{saved_id}/outcomes",
        json={
            "observation_start_date": "2026-09-01",
            "observation_end_date": "2026-09-30",
            "observed_recovered_quantity_kg": 1000,
            "evidence_source_type": "weighbridge_ticket",
            "evidence_reference": "TEST-WB-001",
            "verification_status": "internally_reviewed",
            "operator_note": "Synthetic automated regression evidence.",
        },
    )
    assert outcome.status_code == 200
    outcome_json = outcome.json()
    outcome_id = outcome_json["id"]
    assert outcome_json["claim_status"] == "observed_outcome_not_claim_ready"

    review = client.post(
        f"/api/scenarios/outcomes/{outcome_id}/reviews",
        json={
            "reviewer_name": "Automated Test Reviewer",
            "reviewer_role": "Internal evidence reviewer",
            "evidence_completeness": "complete",
            "source_traceability_confirmed": True,
            "quantity_basis_confirmed": True,
            "period_basis_confirmed": True,
            "route_destination_confirmed": True,
            "review_note": "All regression evidence checks completed.",
        },
    )
    assert review.status_code == 200
    review_json = review.json()
    assert review_json["verification_decision"] == "internally_supported_with_route_context"
    assert review_json["internal_claim_readiness"] == "internal_factual_reporting_ready"
    assert review_json["external_claim_readiness"] == "external_verification_required"
    assert review_json["allowed_internal_statement"]
    assert any("carbon" in claim.lower() for claim in review_json["blocked_claims"])
    assert any("financial" in claim.lower() for claim in review_json["blocked_claims"])
    assert any("legal" in claim.lower() for claim in review_json["blocked_claims"])

    # 6. Record professional disagreement and prove the locked recommendation is unchanged.
    challenge = client.post(
        "/api/governance/decision-challenges/S001",
        json={
            "challenger_name": "Automated External Reviewer",
            "challenger_role": "Waste and resource specialist",
            "challenger_organisation": "Regression Test",
            "challenge_type": "route",
            "proposed_change": "Require alloy-grade confirmation before treating closed-loop recycling as the preferred route.",
            "rationale": "Closed-loop acceptance depends on alloy specification and recycler acceptance evidence.",
            "supporting_evidence_reference": "TEST-GOV-001",
        },
    )
    assert challenge.status_code == 200
    challenge_json = challenge.json()
    assert challenge_json["decision_effect"] == "no_automatic_override"
    assert challenge_json["status"] == "recorded_for_governance_review"

    rec_after = client.get("/api/recommendations/S001")
    assert rec_after.status_code == 200
    rec_after_json = rec_after.json()
    assert rec_after_json["rule_applied"] == rec_before_json["rule_applied"]
    assert rec_after_json["recommended_circular_action"] == rec_before_json["recommended_circular_action"]
    assert rec_after_json["circular_strategy_category"] == rec_before_json["circular_strategy_category"]

    challenge_history = client.get("/api/governance/decision-challenges/S001")
    assert challenge_history.status_code == 200
    assert challenge_history.json()["total_challenges"] == 1

    # 7. Verify the blind pack withholds the system answer before submission.
    blind_pack = client.get("/api/decision-validation/blind-review-pack")
    assert blind_pack.status_code == 200
    blind_cases = blind_pack.json()
    assert len(blind_cases) == 10
    hidden_keys = {
        "constraints",
        "interpretation",
        "sources",
        "source_ids",
        "rule_applied",
        "recommended_circular_action",
        "circular_strategy_category",
        "risk_level",
        "human_review_required",
        "actual",
        "expected",
    }
    for case in blind_cases:
        assert set(case).isdisjoint(hidden_keys)

    # 8. Submit a declared-blind reviewer judgement and reveal comparison only afterwards.
    blind_submit = client.post(
        "/api/decision-validation/blind-review-submit",
        json={
            "reviewer_name": "Automated Blind Reviewer",
            "reviewer_role": "Waste and Resource Specialist",
            "reviewer_organisation": "Regression Test",
            "reviewer_declared_blind": True,
            "labels": [
                {
                    "case_id": "gc_damaged_lithium_battery",
                    "strategy_category": "human review required",
                    "risk_level": "high",
                    "human_review_required": True,
                    "confidence": 5,
                    "reasoning": "Damaged batteries require specialist review before route selection.",
                },
                {
                    "case_id": "gc_metal_trim_prevention",
                    "strategy_category": "reduce / process redesign",
                    "risk_level": "low",
                    "human_review_required": False,
                    "confidence": 4,
                    "reasoning": "Source reduction should be screened before relying on recycling.",
                },
            ],
        },
    )
    assert blind_submit.status_code == 200
    blind_result = blind_submit.json()
    assert blind_result["reviewer_declared_blind"] is True
    assert blind_result["total_labels"] == 2
    assert len(blind_result["submissions"]) == 2

    analysis = client.get("/api/decision-validation/blind-review-analysis")
    assert analysis.status_code == 200
    analysis_json = analysis.json()
    assert analysis_json["unique_reviewers"] == 1
    assert analysis_json["unique_cases_reviewed"] == 2
    assert analysis_json["cases_with_multiple_reviewers"] == 0
    assert "consensus is not treated as ground truth" in analysis_json["governance_note"].lower()

    # 9. The evidence policy must keep documentary support separate from assurance.
    evidence_policy = client.get("/api/governance/evidence-policy")
    assert evidence_policy.status_code == 200
    policy = evidence_policy.json()
    source_map = {item["source_type"]: item for item in policy["source_classes"]}
    assert source_map["weighbridge_ticket"]["eligible_for_internal_claim_gate"] is True
    assert source_map["weighbridge_ticket"]["independent_assurance"] is False
    assert source_map["independent_assurance"]["supported_by_current_alpha"] is False

    # 10. Audit history should contain each governed operator/reviewer transition.
    events = client.get("/api/audit/events?limit=500")
    assert events.status_code == 200
    event_types = {event["event_type"] for event in events.json()}
    assert "dataset_loaded" in event_types
    assert "rules_engine_run" in event_types
    assert "intervention_scenario_screened" in event_types
    assert "intervention_scenario_saved" in event_types
    assert "observed_scenario_outcome_recorded" in event_types
    assert "observed_outcome_evidence_reviewed" in event_types
    assert "decision_challenge_recorded" in event_types
    assert "blind_decision_review_submitted" in event_types
