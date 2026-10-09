from types import SimpleNamespace
from app.feasibility_screen import assess_feasibility, REQUIRED_CHECKS

def rec(**overrides):
    data = dict(human_review_required=False, risk_level="low", rule_applied="R005_METAL_CLOSED_LOOP", missing_data="none identified for MVP fields")
    data.update(overrides)
    return SimpleNamespace(**data)

def test_unconfirmed_opportunity_is_not_authorised():
    result = assess_feasibility(rec())
    assert result["state"] == "potential_opportunity"
    assert result["route_authorised"] is False
    assert result["verified_operational_feasibility"] is False

def test_user_confirmations_are_not_independent_assurance():
    result = assess_feasibility(rec(), {key: True for key in REQUIRED_CHECKS})
    assert result["state"] == "feasibility_evidence_recorded_not_authorised"
    assert result["route_authorised"] is False
    assert result["verified_operational_feasibility"] is False

def test_unknown_hazard_blocks_even_when_every_check_is_ticked():
    result = assess_feasibility(rec(risk_level="high", human_review_required=True), {key: True for key in REQUIRED_CHECKS})
    assert result["state"] == "human_review_required"
    assert result["route_authorised"] is False

def test_missing_evidence_cannot_be_overridden_by_checkboxes():
    result = assess_feasibility(rec(missing_data="confirmed hazardous status"), {key: True for key in REQUIRED_CHECKS})
    assert result["state"] == "needs_more_information"

def test_string_yes_does_not_count_as_confirmation():
    result = assess_feasibility(rec(), {key: "yes" for key in REQUIRED_CHECKS})
    assert result["state"] == "potential_opportunity"
