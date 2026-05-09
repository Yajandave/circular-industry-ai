from types import SimpleNamespace

from app.evidence_explainer.service import generate_evidence_gap_explanation


def test_evidence_gap_explainer_fallback_locks_decision_fields(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    stream = SimpleNamespace(stream_id="S999", stream_name="Test contaminated stream", material="plastics", department="Production", supplier="Test Supplier")
    recommendation = SimpleNamespace(
        stream_id="S999",
        recommended_circular_action="Compliant disposal or specialist recovery review",
        circular_strategy_category="compliant disposal / specialist recovery",
        rule_applied="R002_HIGH_CONTAMINATION_REVIEW",
        risk_level="high",
        human_review_required=True,
        confidence_score=52,
        evidence_quality_score=42,
        missing_data="contamination assessment; supplier acceptance criteria",
        estimated_annual_waste_diverted_kg=0,
        estimated_annual_disposal_cost_avoided=0,
        next_action="Obtain contamination data and ask a qualified contractor whether safe recovery is viable.",
    )
    evidence = {
        "evidence_status": "controlled review required",
        "review_gate": "human review required before circular route selection",
        "claim_readiness": "not claim-ready: review gate unresolved",
        "missing_data": "contamination assessment; supplier acceptance criteria",
        "claim_boundary": "screening only",
    }
    result = generate_evidence_gap_explanation(stream, recommendation, evidence)
    assert result["generation_mode"] == "deterministic_fallback"
    assert result["locked_rule_applied"] == "R002_HIGH_CONTAMINATION_REVIEW"
    assert result["locked_risk_level"] == "high"
    assert result["locked_human_review_required"] is True
    assert result["locked_claim_readiness"] == "not claim-ready: review gate unresolved"
    assert result["evidence_to_collect"]
    assert result["unsafe_claims_to_avoid"]
    assert "verified" in result["claim_readiness_explanation"].lower()
