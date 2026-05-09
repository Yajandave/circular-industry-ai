from app.llm_reasoning.fallback import fallback_reasoning
from app.llm_reasoning.reasoning_service import reasoning_status
from app.rules_engine import recommend_for_stream
from app.circular_resolution.resolution_engine import build_resolution_plan
from app.evidence_register import build_evidence_record
from app import schemas


def make_stream(**overrides):
    data = {
        "stream_id": "T001",
        "stream_name": "Aluminium machining offcuts",
        "material": "metals",
        "source_process": "CNC machining",
        "monthly_quantity_kg": 1000,
        "current_route": "mixed scrap",
        "disposal_cost_per_month": 100,
        "contamination_risk": "low",
        "hazardous_flag": "false",
        "department": "Manufacturing",
        "supplier": "AluForm Metals Ltd",
        "supplier_takeback_available": "unknown",
        "recycled_content_available": "yes",
        "notes": "alloy grade not always recorded",
    }
    data.update(overrides)
    return schemas.IndustrialStreamCreate(**data)


def test_reasoning_status_has_guardrail_summary(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    status = reasoning_status()
    assert status["mode"] == "deterministic_fallback"
    assert "Rules decide" in status["guardrail_summary"]


def test_fallback_reasoning_keeps_rules_locked():
    stream = make_stream()
    rec = recommend_for_stream(stream)
    evidence = build_evidence_record(stream, rec)
    resolution = build_resolution_plan(stream, rec)
    result = fallback_reasoning(stream, rec, evidence, resolution)
    assert result["stream_id"] == "T001"
    assert result["decision_lock_status"] == "rules_locked"
    assert result["generation_mode"] == "deterministic_fallback"
    assert "verified" in result["claim_safety_note"].lower() or "screening" in result["claim_safety_note"].lower()
    assert result["supplier_questions"]


def test_fallback_reasoning_strengthens_human_review_case():
    stream = make_stream(
        stream_id="T045",
        stream_name="Grease trap waste",
        material="organic/process residue",
        source_process="canteen wastewater",
        contamination_risk="high",
        hazardous_flag="true",
        supplier="WasteCare Services",
    )
    rec = recommend_for_stream(stream)
    evidence = build_evidence_record(stream, rec)
    resolution = build_resolution_plan(stream, rec)
    result = fallback_reasoning(stream, rec, evidence, resolution)
    assert rec.human_review_required is True
    assert "human review" in result["human_review_note"].lower()
    assert any("classification" in q.lower() for q in result["supplier_questions"])
