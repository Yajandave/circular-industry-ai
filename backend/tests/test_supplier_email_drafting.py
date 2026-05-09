from types import SimpleNamespace

from app.supplier_drafting.service import generate_supplier_email_draft


def test_supplier_email_draft_fallback_locks_decision_fields(monkeypatch):
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
    )
    supplier_plan = {
        "procurement_route": "closed-loop material return with supplier or recycler",
        "supplier_relationship_type": "supplier/recycler closed-loop partnership",
        "supplier_questions": ["Can the supplier confirm grade acceptance criteria?"],
        "supplier_evidence_required": ["material grade/composition evidence", "route documentation"],
        "acceptance_criteria": ["material must match supplier specification"],
        "data_requests": ["monthly quantity by source process"],
        "contract_levers": ["acceptance and rejection criteria"],
        "claim_boundary": "Do not make external circularity claims until evidence is validated.",
        "review_gate": "Procurement validation gate",
        "estimated_annual_value_at_stake": 5040,
    }
    evidence = {
        "claim_readiness": "internal screening only: validate before claims",
        "evidence_status": "strong evidence",
        "review_gate": "rules-cleared for validation",
    }

    result = generate_supplier_email_draft(stream, recommendation, supplier_plan, evidence)

    assert result["generation_mode"] == "deterministic_fallback"
    assert result["locked_rule_applied"] == "R005_METAL_CLOSED_LOOP"
    assert result["locked_risk_level"] == "low"
    assert result["locked_human_review_required"] is False
    assert result["locked_procurement_route"] == "closed-loop material return with supplier or recycler"
    assert "Aluminium machining offcuts" in result["email_body"]
    assert "verified" in result["claim_safety_note"].lower()
    assert result["attachments_or_documents_to_request"]
