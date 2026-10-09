from app.reference_decision_eligibility import evaluate_reference_decision_eligibility


def test_waste_reference_alone_never_authorises_rules():
    result = evaluate_reference_decision_eligibility({"status": "found"})
    assert result["eligible_for_legacy_rule_screening"] is False
    assert "verified_hazardous_status" in result["missing_evidence"]


def test_missing_reference_blocks_even_with_other_evidence():
    result = evaluate_reference_decision_eligibility({"status": "not_found"}, verified_monthly_stream=True,
       verified_material_family="metals", hazardous_status_verified=True, contamination_verified=True)
    assert result["eligible_for_legacy_rule_screening"] is False


def test_all_explicit_evidence_passes_reference_eligibility_only():
    result = evaluate_reference_decision_eligibility({"status": "found"}, verified_monthly_stream=True,
       verified_material_family="metals", hazardous_status_verified=True, contamination_verified=True)
    assert result["eligible_for_legacy_rule_screening"] is True
    assert result["reference_only"] is True
