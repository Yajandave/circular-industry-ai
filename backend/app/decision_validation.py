"""Decision-quality benchmark for the deterministic circular rules engine.

Milestone 20C.1 establishes an internal benchmark framework. The expectations
below are authored reference labels for regression and structured review; they
are not external expert validation, regulatory approval or proof of real-world
operational feasibility.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from app.rules_engine import recommend_for_stream


def _stream(
    stream_id: str,
    stream_name: str,
    material: str,
    *,
    source_process: str = "production",
    monthly_quantity_kg: float = 500,
    current_route: str = "general waste",
    disposal_cost_per_month: float = 250,
    contamination_risk: str = "low",
    hazardous_flag: str = "false",
    department: str = "Operations",
    supplier: str = "Example Supplier",
    supplier_takeback_available: str = "no",
    recycled_content_available: str = "unknown",
    notes: str = "",
) -> dict[str, Any]:
    return {
        "stream_id": stream_id,
        "stream_name": stream_name,
        "material": material,
        "source_process": source_process,
        "monthly_quantity_kg": monthly_quantity_kg,
        "current_route": current_route,
        "disposal_cost_per_month": disposal_cost_per_month,
        "contamination_risk": contamination_risk,
        "hazardous_flag": hazardous_flag,
        "department": department,
        "supplier": supplier,
        "supplier_takeback_available": supplier_takeback_available,
        "recycled_content_available": recycled_content_available,
        "notes": notes,
    }


def _case(
    case_id: str,
    title: str,
    stream: dict[str, Any],
    *,
    expected_rule: str,
    expected_category: str,
    expected_risk: str,
    expected_human_review: bool,
    rationale: str,
    case_type: str = "baseline",
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "title": title,
        "case_type": case_type,
        "label_source": "internal_reference_expectation",
        "validation_status": "benchmark_draft",
        "rationale": rationale,
        "stream": stream,
        "expectations": {
            "rule_applied": expected_rule,
            "circular_strategy_category": expected_category,
            "risk_level": expected_risk,
            "human_review_required": expected_human_review,
        },
    }


DECISION_VALIDATION_CASES: list[dict[str, Any]] = [
    _case(
        "dv_hazardous_solvent",
        "Hazardous solvent stream",
        _stream(
            "DV001", "Spent cleaning solvent", "chemicals/solvents",
            hazardous_flag="true", contamination_risk="medium",
            current_route="hazardous waste contractor",
        ),
        expected_rule="R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
        expected_category="human review required",
        expected_risk="high",
        expected_human_review=True,
        rationale="Hazardous solvent evidence should block automatic circular route selection.",
    ),
    _case(
        "dv_high_contamination_metal",
        "Highly contaminated metal scrap",
        _stream(
            "DV002", "Oil-contaminated steel scrap", "metals",
            hazardous_flag="false", contamination_risk="high",
        ),
        expected_rule="R002_HIGH_CONTAMINATION_REVIEW",
        expected_category="compliant disposal / specialist recovery",
        expected_risk="high",
        expected_human_review=True,
        rationale="High contamination should force specialist recovery or disposal review.",
    ),
    _case(
        "dv_trim_loss_prevention",
        "Sheet-metal trim loss",
        _stream(
            "DV003", "Aluminium trim losses", "metals",
            source_process="sheet trimming",
        ),
        expected_rule="R003_REDUCE_AT_SOURCE",
        expected_category="reduce / process redesign",
        expected_risk="low",
        expected_human_review=False,
        rationale="Repeated trim loss should prioritise prevention before downstream recycling.",
    ),
    _case(
        "dv_packaging_takeback",
        "Packaging supplier take-back",
        _stream(
            "DV004", "Corrugated transit packaging", "cardboard/packaging",
            supplier_takeback_available="yes",
        ),
        expected_rule="R004_SUPPLIER_TAKEBACK_AVAILABLE",
        expected_category="supplier take-back / circular procurement",
        expected_risk="low",
        expected_human_review=False,
        rationale="Confirmed take-back should trigger supplier-loop review before open recycling.",
    ),
    _case(
        "dv_metal_closed_loop",
        "Segregated metal closed-loop candidate",
        _stream("DV005", "Segregated aluminium offcuts", "metals"),
        expected_rule="R005_METAL_CLOSED_LOOP",
        expected_category="closed-loop recycling",
        expected_risk="low",
        expected_human_review=False,
        rationale="Low-contamination segregated metals should enter closed-loop recycling review.",
    ),
    _case(
        "dv_pallet_reuse",
        "Reusable timber pallets",
        _stream("DV006", "Undamaged timber pallets", "wood/pallets"),
        expected_rule="R006_PACKAGING_REUSE",
        expected_category="internal reuse / returnable packaging",
        expected_risk="low",
        expected_human_review=False,
        rationale="Low-contamination pallets should be screened for reuse before recycling.",
    ),
    _case(
        "dv_mixed_plastic",
        "Mixed polymer rejects",
        _stream("DV007", "Mixed polymer rejects", "plastics"),
        expected_rule="R007_MIXED_PLASTIC_RECYCLING",
        expected_category="open-loop recycling",
        expected_risk="low",
        expected_human_review=False,
        rationale="Mixed polymers weaken closed-loop confidence and should trigger material testing.",
    ),
    _case(
        "dv_single_polymer_plastic",
        "Single-polymer plastic rejects",
        _stream("DV008", "HDPE moulding rejects", "plastics"),
        expected_rule="R008_PLASTIC_CLOSED_LOOP",
        expected_category="closed-loop recycling",
        expected_risk="low",
        expected_human_review=False,
        rationale="Known low-contamination plastics should enter controlled closed-loop review.",
    ),
    _case(
        "dv_organic_residue",
        "Organic process residue",
        _stream("DV009", "Food-process organic residue", "organic/process residue"),
        expected_rule="R009_SYMBIOSIS_OR_RESOURCE_RECOVERY",
        expected_category="industrial symbiosis / resource recovery",
        expected_risk="low",
        expected_human_review=False,
        rationale="Organic residues should be screened for recovery or symbiosis routes.",
    ),
    _case(
        "dv_process_water",
        "Process water recovery",
        _stream("DV010", "Rinse-water stream", "process water"),
        expected_rule="R009_SYMBIOSIS_OR_RESOURCE_RECOVERY",
        expected_category="industrial symbiosis / resource recovery",
        expected_risk="low",
        expected_human_review=False,
        rationale="Process water should be screened for recovery or resource-efficiency use.",
    ),
    _case(
        "dv_mineral_residue",
        "Mineral process residue",
        _stream("DV011", "Mineral fines", "process mineral residue"),
        expected_rule="R009_SYMBIOSIS_OR_RESOURCE_RECOVERY",
        expected_category="industrial symbiosis / resource recovery",
        expected_risk="low",
        expected_human_review=False,
        rationale="Mineral residues may have secondary-input or recovery potential.",
    ),
    _case(
        "dv_glass_specialist",
        "Glass specialist recovery",
        _stream("DV012", "Broken process glass", "glass"),
        expected_rule="R010_SPECIALIST_RECOVERY",
        expected_category="open-loop recycling / specialist recovery",
        expected_risk="low",
        expected_human_review=False,
        rationale="Glass should route to specialist recovery review when contamination is controlled.",
    ),
    _case(
        "dv_rubber_specialist",
        "Rubber specialist recovery",
        _stream(
            "DV013", "Rubber trimming residue", "rubber",
            contamination_risk="medium",
        ),
        expected_rule="R003_REDUCE_AT_SOURCE",
        expected_category="reduce / process redesign",
        expected_risk="medium",
        expected_human_review=False,
        rationale="A trimming-generated rubber stream should prioritise prevention even where recovery is possible.",
    ),
    _case(
        "dv_electronics_low_risk",
        "Non-hazardous electronic component rejects",
        _stream(
            "DV014", "Electronic component rejects", "electronic components",
            hazardous_flag="false", contamination_risk="low",
        ),
        expected_rule="R010_SPECIALIST_RECOVERY",
        expected_category="open-loop recycling / specialist recovery",
        expected_risk="low",
        expected_human_review=False,
        rationale="Confirmed non-hazardous electronics should enter specialist recovery review.",
    ),
    _case(
        "dv_unknown_material",
        "Unknown production reject",
        _stream(
            "DV015", "General production rejects", "unknown",
            hazardous_flag="unknown", contamination_risk="unknown",
        ),
        expected_rule="R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
        expected_category="human review required",
        expected_risk="high",
        expected_human_review=True,
        rationale="Low-information streams should fail safe into human review.",
        case_type="challenge",
    ),
    _case(
        "dv_contaminated_packaging",
        "Highly contaminated packaging",
        _stream(
            "DV016", "Contaminated cardboard packaging", "cardboard/packaging",
            contamination_risk="high",
        ),
        expected_rule="R002_HIGH_CONTAMINATION_REVIEW",
        expected_category="compliant disposal / specialist recovery",
        expected_risk="high",
        expected_human_review=True,
        rationale="High contamination must override otherwise reusable packaging logic.",
        case_type="challenge",
    ),
    _case(
        "dv_plastic_takeback_precedence",
        "Plastic supplier take-back precedence",
        _stream(
            "DV017", "Clean PP transport trays", "plastics",
            supplier_takeback_available="yes",
        ),
        expected_rule="R004_SUPPLIER_TAKEBACK_AVAILABLE",
        expected_category="supplier take-back / circular procurement",
        expected_risk="low",
        expected_human_review=False,
        rationale="Confirmed supplier take-back should take precedence over generic plastics recycling.",
    ),
    _case(
        "dv_metal_takeback_precedence",
        "Metal supplier take-back precedence",
        _stream(
            "DV018", "Steel return scrap", "metals",
            supplier_takeback_available="yes",
        ),
        expected_rule="R004_SUPPLIER_TAKEBACK_AVAILABLE",
        expected_category="supplier take-back / circular procurement",
        expected_risk="low",
        expected_human_review=False,
        rationale="Supplier return loops should take precedence over generic metal recycling.",
    ),
    _case(
        "dv_battery_blocked",
        "Hazardous battery stream",
        _stream(
            "DV019", "Damaged battery modules", "batteries",
            hazardous_flag="true", contamination_risk="high",
            current_route="specialist hazardous contractor",
        ),
        expected_rule="R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
        expected_category="human review required",
        expected_risk="blocked",
        expected_human_review=True,
        rationale="Hazardous, highly contaminated batteries must remain under controlled review.",
        case_type="challenge",
    ),
    _case(
        "dv_wee_unknown_hazard",
        "Electronics with unresolved hazardous status",
        _stream(
            "DV020", "Mixed electronic assemblies", "electronic components",
            hazardous_flag="unknown", contamination_risk="medium",
        ),
        expected_rule="R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
        expected_category="human review required",
        expected_risk="high",
        expected_human_review=True,
        rationale="Unresolved hazardous status in electronics should prevent automatic recovery selection.",
        case_type="challenge",
    ),
]


def list_decision_validation_cases() -> list[dict[str, Any]]:
    return DECISION_VALIDATION_CASES


def _check(check_id: str, expected: Any, actual: Any) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": "pass" if expected == actual else "fail",
        "expected": expected,
        "actual": actual,
    }


def evaluate_decision_case(case: dict[str, Any]) -> dict[str, Any]:
    recommendation = recommend_for_stream(SimpleNamespace(**case["stream"]))
    expected = case["expectations"]

    checks = [
        _check("rule_applied", expected["rule_applied"], recommendation.rule_applied),
        _check(
            "circular_strategy_category",
            expected["circular_strategy_category"],
            recommendation.circular_strategy_category,
        ),
        _check("risk_level", expected["risk_level"], recommendation.risk_level),
        _check(
            "human_review_required",
            expected["human_review_required"],
            recommendation.human_review_required,
        ),
    ]
    failed = [check for check in checks if check["status"] == "fail"]

    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "case_type": case["case_type"],
        "label_source": case["label_source"],
        "validation_status": case["validation_status"],
        "status": "pass" if not failed else "fail",
        "checks": checks,
        "actual": {
            "rule_applied": recommendation.rule_applied,
            "circular_strategy_category": recommendation.circular_strategy_category,
            "risk_level": recommendation.risk_level,
            "human_review_required": recommendation.human_review_required,
            "recommended_circular_action": recommendation.recommended_circular_action,
            "missing_data": recommendation.missing_data,
        },
        "rationale": case["rationale"],
    }


def run_decision_validation(case_ids: list[str] | None = None) -> dict[str, Any]:
    selected_ids = set(case_ids or [])
    cases = [
        case
        for case in DECISION_VALIDATION_CASES
        if not selected_ids or case["case_id"] in selected_ids
    ]
    results = [evaluate_decision_case(case) for case in cases]

    total = len(results)
    check_names = [
        "rule_applied",
        "circular_strategy_category",
        "risk_level",
        "human_review_required",
    ]
    agreement: dict[str, dict[str, float | int]] = {}
    for check_name in check_names:
        passed = sum(
            1
            for result in results
            for check in result["checks"]
            if check["check_id"] == check_name and check["status"] == "pass"
        )
        agreement[check_name] = {
            "passed": passed,
            "total": total,
            "agreement_pct": round((passed / total) * 100, 1) if total else 0.0,
        }

    full_agreement = sum(1 for result in results if result["status"] == "pass")
    return {
        "suite_name": "circular_decision_internal_benchmark_v1",
        "benchmark_status": "internal_reference_only",
        "total_cases": total,
        "full_agreement_cases": full_agreement,
        "full_agreement_pct": round((full_agreement / total) * 100, 1) if total else 0.0,
        "agreement": agreement,
        "results": results,
        "governance_note": (
            "This suite is an internal benchmark for regression and structured review. "
            "Its labels are not external expert validation, legal advice, regulatory approval, "
            "supplier acceptance evidence or proof of operational feasibility."
        ),
    }
