from types import SimpleNamespace

from app.report_builder.service import generate_circular_action_report


def test_circular_action_report_fallback_locks_decision_fields(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")

    stream = SimpleNamespace(
        stream_id="S001",
        stream_name="Aluminium machining offcuts",
        material="metals",
        department="Machining",
        supplier="AluForm Metals Ltd",
    )
    recommendation = SimpleNamespace(
        stream_id="S001",
        recommended_circular_action="Closed-loop recycling review",
        rule_applied="R005_METAL_CLOSED_LOOP",
        risk_level="low",
        human_review_required=False,
        confidence_score=88,
        evidence_quality_score=86,
        estimated_annual_waste_diverted_kg=22200,
        estimated_annual_disposal_cost_avoided=5040,
        next_action="Confirm grade segregation and supplier route evidence.",
    )
    evidence = {
        "evidence_status": "strong evidence",
        "claim_readiness": "internal screening only: validate before claims",
        "review_gate": "rules-cleared for validation",
        "missing_data": "supplier take-back evidence",
        "claim_boundary": "screening only",
        "next_action": "Confirm supplier evidence.",
    }
    resolution = {
        "specific_resolution_idea": "Create a segregated closed-loop route for aluminium offcuts.",
        "implementation_steps": ["Segregate by grade", "Confirm supplier acceptance", "Run pilot"],
        "evidence_required": ["grade evidence", "collection records"],
        "claim_boundary": "Do not claim verified savings until measured.",
    }
    supplier_plan = {
        "procurement_route": "closed-loop material return with supplier or recycler",
        "supplier_relationship_type": "supplier/recycler closed-loop partnership",
        "negotiation_position": "Request a controlled pilot with evidence obligations.",
        "supplier_evidence_required": ["route documentation", "acceptance criteria"],
        "review_gate": "Procurement validation gate",
        "claim_boundary": "Do not make external circularity claims until evidence is validated.",
    }

    result = generate_circular_action_report(stream, recommendation, evidence, resolution, supplier_plan)

    assert result["generation_mode"] == "deterministic_fallback"
    assert result["locked_rule_applied"] == "R005_METAL_CLOSED_LOOP"
    assert result["locked_risk_level"] == "low"
    assert result["locked_human_review_required"] is False
    assert result["locked_claim_readiness"] == "internal screening only: validate before claims"
    assert result["locked_procurement_route"] == "closed-loop material return with supplier or recycler"
    assert "Circular Action Report" in result["report_title"]
    assert result["implementation_plan"]
    assert result["unsafe_claims_to_avoid"]
    assert "not verified" in result["executive_summary"].lower()
