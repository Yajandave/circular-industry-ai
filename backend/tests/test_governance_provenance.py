"""Governance and provenance regression tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agentic.orchestrator import build_action_plan
from app.database import Base, get_db
from app.main import app
from app.review_governance import build_review_governance
from app.rule_provenance import get_rule_provenance


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


def test_hazard_review_rule_exposes_external_grounding_without_claiming_assurance():
    provenance = get_rule_provenance("R001_HAZARDOUS_OR_UNKNOWN_REVIEW")

    assert provenance["provenance_status"] == "externally_grounded_safety_boundary"
    assert "waste_classification" in provenance["external_source_ids"]
    assert provenance["sources"]
    assert "legal" in provenance["claim_boundary"].lower()
    assert "independent" in provenance["claim_boundary"].lower()


def test_material_route_rule_is_labelled_as_internal_screening_judgement():
    provenance = get_rule_provenance("R005_METAL_CLOSED_LOOP")

    assert provenance["provenance_status"] == "internal_material_screening_rule"
    assert "waste_hierarchy" in provenance["external_source_ids"]
    assert "technical" in provenance["internal_interpretation"].lower()
    assert "unverified" in provenance["internal_interpretation"].lower()


def test_high_risk_battery_routes_to_competent_review_and_second_review():
    stream = SimpleNamespace(
        material="batteries",
        stream_name="Damaged swollen lithium-ion batteries",
        source_process="maintenance",
        notes="Damaged lithium battery modules",
    )
    recommendation = SimpleNamespace(
        rule_applied="R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
        risk_level="high",
        human_review_required=True,
    )

    profile = build_review_governance(stream, recommendation)

    assert profile["gate_status"] == "competent_human_review_required"
    assert profile["second_review_recommended"] is True
    assert any("waste classification" in item for item in profile["primary_reviewer_competence"])
    assert any("battery safety" in item for item in profile["supporting_reviewer_competence"])
    assert "does not silently overwrite" in profile["override_policy"].lower()


def test_action_plan_ranking_does_not_require_legacy_numeric_scores():
    records = [
        SimpleNamespace(
            stream_id="A",
            recommended_circular_action="Closed-loop review",
            risk_level="low",
            human_review_required=False,
            rule_applied="R005_METAL_CLOSED_LOOP",
            missing_data="none identified for MVP fields",
            dashboard_priority="high",
            estimated_annual_waste_diverted_kg=15000.0,
            estimated_annual_disposal_cost_avoided=7000.0,
            next_action="Validate route.",
        ),
        SimpleNamespace(
            stream_id="B",
            recommended_circular_action="Human review",
            risk_level="high",
            human_review_required=True,
            rule_applied="R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
            missing_data="confirmed hazardous status",
            dashboard_priority="high - review required",
            estimated_annual_waste_diverted_kg=1000.0,
            estimated_annual_disposal_cost_avoided=500.0,
            next_action="Resolve classification.",
        ),
    ]

    result = build_action_plan(records)

    assert "controlled review" in result["phases"]
    assert "validation priority" in result["phases"]
    assert "confidence score" in result["ranking_method"].lower()
    assert "no probability" in result["ranking_method"].lower()


def test_recorded_decision_challenge_does_not_mutate_locked_recommendation(isolated_client):
    client = isolated_client

    assert client.post("/api/streams/load-sample").status_code == 200
    assert client.post("/api/recommendations/run").status_code == 200

    before = client.get("/api/recommendations/S001").json()

    response = client.post(
        "/api/governance/decision-challenges/S001",
        json={
            "challenger_name": "External Reviewer",
            "challenger_role": "Waste and resource specialist",
            "challenger_organisation": "Independent Review",
            "challenge_type": "route",
            "proposed_change": "Consider a different route after grade evidence is confirmed.",
            "rationale": "The current stream description may not establish closed-loop acceptance.",
            "supporting_evidence_reference": "Reviewer note GOV-001",
        },
    )

    assert response.status_code == 200
    challenge = response.json()
    assert challenge["decision_effect"] == "no_automatic_override"
    assert challenge["recommendation_rule_applied"] == before["rule_applied"]

    after = client.get("/api/recommendations/S001").json()
    assert after["rule_applied"] == before["rule_applied"]
    assert after["recommended_circular_action"] == before["recommended_circular_action"]
    assert after["circular_strategy_category"] == before["circular_strategy_category"]

    history = client.get("/api/governance/decision-challenges/S001").json()
    assert history["total_challenges"] == 1
    assert history["records"][0]["status"] == "recorded_for_governance_review"

    audit_events = client.get("/api/audit/events?event_type=decision_challenge_recorded").json()
    assert len(audit_events) == 1
    assert audit_events[0]["metadata_json"]["decision_effect"] == "no_automatic_override"


def test_governance_api_exposes_rule_catalogue_and_review_profile(isolated_client):
    client = isolated_client

    rules = client.get("/api/governance/rules")
    assert rules.status_code == 200
    assert any(item["rule_id"] == "R001_HAZARDOUS_OR_UNKNOWN_REVIEW" for item in rules.json())

    client.post("/api/streams/load-sample")
    client.post("/api/recommendations/run")

    profile = client.get("/api/governance/review-profile/S001")
    assert profile.status_code == 200
    assert profile.json()["primary_reviewer_competence"]
    assert "override_policy" in profile.json()



def test_evidence_policy_separates_documentary_support_from_independent_assurance(isolated_client):
    client = isolated_client
    response = client.get("/api/governance/evidence-policy")
    assert response.status_code == 200
    policy = response.json()

    by_type = {item["source_type"]: item for item in policy["source_classes"]}
    assert by_type["operator_log"]["eligible_for_internal_claim_gate"] is False
    assert by_type["weighbridge_ticket"]["eligible_for_internal_claim_gate"] is True
    assert by_type["weighbridge_ticket"]["independent_assurance"] is False
    assert by_type["supplier_confirmation"]["independent_assurance"] is False
    assert by_type["independent_assurance"]["supported_by_current_alpha"] is False
    assert "authenticate" in policy["governance_note"].lower()
