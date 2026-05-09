from app.circular_resolution.resolution_engine import build_resolution_plan, build_resolution_plans, build_resolution_summary
from app.rules_engine import analyse_stream
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


def test_resolution_plan_is_specific_for_clean_metal():
    stream = make_stream()
    rec = analyse_stream(stream)
    plan = build_resolution_plan(stream, rec)
    assert plan["stream_id"] == "T001"
    assert "alloy" in " ".join(plan["evidence_required"]).lower()
    assert "closed-loop" in plan["specific_resolution_idea"].lower() or "quality-retention" in plan["specific_resolution_idea"].lower()
    assert plan["human_review_required"] is False
    assert "Internal screening" in plan["claim_boundary"]


def test_resolution_plan_blocks_hazardous_grease_trap_stream():
    stream = make_stream(
        stream_id="T045",
        stream_name="Grease trap waste",
        material="organic/process residue",
        source_process="canteen wastewater",
        contamination_risk="high",
        hazardous_flag="true",
        supplier="WasteCare Services",
        notes="FOG stream requiring contractor classification",
    )
    rec = analyse_stream(stream)
    plan = build_resolution_plan(stream, rec)
    assert plan["human_review_required"] is True
    assert "FOG" in plan["specific_resolution_idea"] or "grease" in plan["specific_resolution_idea"].lower()
    assert "Not claim-ready" in plan["claim_boundary"]
    assert any("classification" in gate.lower() for gate in plan["decision_gates"])


def test_resolution_summary_counts_controlled_plans():
    streams = [
        make_stream(stream_id="T001"),
        make_stream(
            stream_id="T002",
            stream_name="Damaged lithium battery packs",
            material="electronic components",
            source_process="returns inspection",
            contamination_risk="high",
            hazardous_flag="true",
            supplier="PowerCell Systems",
        ),
    ]
    recs = [analyse_stream(stream) for stream in streams]
    plans = build_resolution_plans(streams, recs)
    summary = build_resolution_summary(plans)
    assert summary["total_plans"] == 2
    assert summary["controlled_review_plans"] == 1
    assert summary["claim_blocked_or_not_ready"] >= 1
