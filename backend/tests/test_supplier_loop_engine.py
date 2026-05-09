from app.circular_resolution.resolution_engine import build_resolution_plans
from app.procurement.supplier_loop_engine import build_supplier_loop_plans, build_supplier_loop_summary
from app.rules_engine import recommend_for_stream
from app.schemas import IndustrialStreamCreate


def _stream(**overrides):
    data = {
        "stream_id": "T001",
        "stream_name": "LDPE shrink wrap from inbound pallets",
        "material": "plastics",
        "source_process": "goods-in packaging",
        "monthly_quantity_kg": 640,
        "current_route": "baled recycling",
        "disposal_cost_per_month": 120,
        "contamination_risk": "low",
        "hazardous_flag": "false",
        "department": "Warehouse",
        "supplier": "LogiWrap Packaging",
        "supplier_takeback_available": "yes",
        "recycled_content_available": "yes",
        "notes": "Clean recurring inbound packaging stream.",
    }
    data.update(overrides)
    return IndustrialStreamCreate(**data)


def test_supplier_loop_plan_generates_supplier_questions():
    stream = _stream()
    recommendation = recommend_for_stream(stream)
    plans = build_supplier_loop_plans([stream], [recommendation])

    assert len(plans) == 1
    plan = plans[0]
    assert plan["stream_id"] == "T001"
    assert "supplier" in plan["procurement_route"] or "packaging" in plan["procurement_route"]
    assert plan["supplier_questions"]
    assert plan["contract_levers"]
    assert plan["claim_boundary"]


def test_supplier_loop_plan_keeps_hazardous_stream_controlled():
    stream = _stream(
        stream_id="T002",
        stream_name="Contaminated solvent containers",
        material="chemicals/solvents",
        source_process="surface cleaning",
        current_route="hazardous waste contractor",
        contamination_risk="high",
        hazardous_flag="true",
        supplier="CleanChem Supplies",
        supplier_takeback_available="unknown",
        recycled_content_available="unknown",
    )
    recommendation = recommend_for_stream(stream)
    plans = build_supplier_loop_plans([stream], [recommendation])
    plan = plans[0]

    assert plan["human_review_required"] is True
    assert "controlled" in plan["procurement_priority"]
    assert "classification" in " ".join(plan["supplier_evidence_required"]).lower()
    assert "Do not proceed" in plan["review_gate"]


def test_supplier_loop_summary_counts_candidates_and_controlled_reviews():
    safe = _stream(stream_id="T001")
    controlled = _stream(
        stream_id="T002",
        stream_name="Damaged lithium battery packs",
        material="electronic components",
        source_process="returns inspection",
        contamination_risk="high",
        hazardous_flag="true",
        supplier="PowerCell Systems",
    )
    recs = [recommend_for_stream(safe), recommend_for_stream(controlled)]
    plans = build_supplier_loop_plans([safe, controlled], recs)
    summary = build_supplier_loop_summary(plans)

    assert summary["total_plans"] == 2
    assert summary["controlled_supplier_reviews"] >= 1
    assert summary["procurement_priority_breakdown"]
