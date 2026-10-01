"""Externally grounded circular-decision challenge validation.

Milestone 20C.2 uses authoritative UK guidance to define broad safety,
classification and waste-hierarchy constraints. The constraints are intentionally
not expressed as exact Circular Industry AI rule IDs, so the suite can expose
where the current implementation is too narrow or overconfident.

The interpretation of public guidance into benchmark constraints is still an
internal product judgement. This is stronger than self-referential regression
testing, but it is not independent professional assurance or regulatory advice.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from app.rules_engine import recommend_for_stream


GROUNDING_SOURCES: dict[str, dict[str, str]] = {
    "waste_hierarchy": {
        "title": "Guidance on applying the waste hierarchy",
        "publisher": "Department for Environment, Food & Rural Affairs",
        "url": "https://www.gov.uk/government/publications/guidance-on-applying-the-waste-hierarchy",
    },
    "hazardous_producers": {
        "title": "Hazardous waste: Producers and holders",
        "publisher": "GOV.UK",
        "url": "https://www.gov.uk/dispose-hazardous-waste/producers-and-holders",
    },
    "waste_classification": {
        "title": "Classify different types of waste: your legal responsibilities",
        "publisher": "Environment Agency and Department for Environment, Food & Rural Affairs",
        "url": "https://www.gov.uk/guidance/classify-different-types-of-waste-your-legal-responsibilities",
    },
    "packaging_classification": {
        "title": "Packaging waste and recyclables: how to classify",
        "publisher": "Environment Agency and Department for Environment, Food & Rural Affairs",
        "url": "https://www.gov.uk/guidance/packaging-waste-and-recyclables-how-to-classify",
    },
    "weee_classification": {
        "title": "Waste electrical and electronic equipment (WEEE): how to classify",
        "publisher": "Environment Agency and Department for Environment, Food & Rural Affairs",
        "url": "https://www.gov.uk/guidance/waste-electrical-and-electronic-equipment-weee-how-to-classify",
    },
    "food_hierarchy": {
        "title": "Food and drink waste hierarchy: deal with surplus and waste",
        "publisher": "Department for Environment, Food & Rural Affairs",
        "url": "https://www.gov.uk/government/publications/food-and-drink-waste-hierarchy-deal-with-surplus-and-waste/food-and-drink-waste-hierarchy-deal-with-surplus-and-waste",
    },
    "battery_fire_risk": {
        "title": "Fire at waste transfer facility - Southwark",
        "publisher": "London Fire Brigade",
        "url": "https://www.london-fire.gov.uk/incidents/2026/july/fire-at-waste-transfer-facility-southwark/",
    },
    "battery_measures": {
        "title": "Waste batteries: appropriate measures for permitted facilities - general management",
        "publisher": "Environment Agency",
        "url": "https://www.gov.uk/guidance/waste-batteries-appropriate-measures-for-permitted-facilities/2-general-management-appropriate-measures",
    },
}


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


def _challenge(
    case_id: str,
    title: str,
    stream: dict[str, Any],
    *,
    source_ids: list[str],
    interpretation: str,
    constraints: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "title": title,
        "case_type": "externally_grounded_challenge",
        "jurisdiction": "England",
        "label_source": "authoritative_guidance_interpretation",
        "validation_status": "grounded_challenge_v1",
        "interpretation": interpretation,
        "source_ids": source_ids,
        "sources": [GROUNDING_SOURCES[source_id] for source_id in source_ids],
        "stream": stream,
        "constraints": constraints,
    }


GROUNDED_CHALLENGE_CASES: list[dict[str, Any]] = [
    _challenge(
        "gc_damaged_lithium_battery",
        "Damaged lithium-ion battery modules",
        _stream(
            "GC001",
            "Damaged swollen lithium-ion battery modules",
            "batteries",
            current_route="mixed recycling",
            hazardous_flag="false",
            contamination_risk="low",
            notes="Several modules are damaged and swollen.",
        ),
        source_ids=["hazardous_producers", "battery_fire_risk", "battery_measures"],
        interpretation=(
            "Damaged lithium-ion batteries present a fire and handling risk and should not receive a low-risk "
            "generic disposal/recycling recommendation without specialist review."
        ),
        constraints={
            "required_human_review": True,
            "allowed_risk_levels": ["high", "blocked"],
            "required_output_terms_any": ["review", "specialist", "battery"],
        },
    ),
    _challenge(
        "gc_unclassified_weee",
        "WEEE with unresolved hazardous/POPs classification",
        _stream(
            "GC002",
            "Mixed display and circuit-board assemblies - classification pending",
            "electronic components",
            current_route="general recycling",
            hazardous_flag="false",
            contamination_risk="low",
            notes="Hazardous substances and POPs classification has not been completed.",
        ),
        source_ids=["weee_classification", "waste_classification"],
        interpretation=(
            "WEEE must be classified before collection, disposal or recovery so applicable hazardous/POPs "
            "controls are known. A classification-pending record should not be treated as a low-risk settled route."
        ),
        constraints={
            "required_human_review": True,
            "allowed_risk_levels": ["medium", "high", "blocked"],
            "required_output_terms_any": ["classif", "hazard", "review"],
        },
    ),
    _challenge(
        "gc_hazardous_residue_packaging",
        "Packaging contaminated with hazardous solvent residue",
        _stream(
            "GC003",
            "Solvent-contaminated return packaging",
            "cardboard/packaging",
            current_route="packaging reuse",
            hazardous_flag="false",
            contamination_risk="low",
            notes="Packaging contains residues from a hazardous solvent product.",
        ),
        source_ids=["packaging_classification", "hazardous_producers"],
        interpretation=(
            "Packaging contaminated with residues of hazardous substances is classified as hazardous in the "
            "Environment Agency guidance and should not be recommended for routine reuse without classification review."
        ),
        constraints={
            "required_human_review": True,
            "allowed_risk_levels": ["high", "blocked"],
            "forbidden_strategy_categories": ["internal reuse / returnable packaging"],
            "forbidden_output_terms_any": ["internal reuse"],
        },
    ),
    _challenge(
        "gc_edible_food_surplus",
        "Unopened edible food surplus",
        _stream(
            "GC004",
            "Unopened bakery surplus still fit for consumption",
            "organic/process residue",
            source_process="finished goods overproduction",
            current_route="anaerobic digestion",
            hazardous_flag="false",
            contamination_risk="low",
            notes="Product remains within use-by date and fit for human consumption.",
        ),
        source_ids=["food_hierarchy", "waste_hierarchy"],
        interpretation=(
            "For edible surplus, prevention and redistribution sit above recycling/recovery in the food hierarchy. "
            "A resource-recovery route should not be the first screening recommendation when edible redistribution remains possible."
        ),
        constraints={
            "required_human_review": False,
            "allowed_risk_levels": ["low", "medium"],
            "allowed_strategy_categories": ["reduce / process redesign"],
            "required_output_terms_any": ["prevent", "redistribut", "surplus"],
            "forbidden_strategy_categories": ["industrial symbiosis / resource recovery"],
        },
    ),
    _challenge(
        "gc_metal_trim_prevention",
        "Clean sheet-metal trimming loss",
        _stream(
            "GC005",
            "Clean aluminium edge trim",
            "metals",
            source_process="sheet trimming",
            current_route="scrap recycling",
        ),
        source_ids=["waste_hierarchy"],
        interpretation=(
            "Prevention sits above recycling in the waste hierarchy, so a recurring process trim loss should be "
            "screened for source reduction before relying on recycling."
        ),
        constraints={
            "required_human_review": False,
            "allowed_risk_levels": ["low", "medium"],
            "allowed_strategy_categories": ["reduce / process redesign"],
            "required_output_terms_any": ["reduce", "prevent", "process"],
        },
    ),
    _challenge(
        "gc_clean_packaging_takeback",
        "Clean packaging with confirmed supplier return",
        _stream(
            "GC006",
            "Clean reusable transit packaging",
            "cardboard/packaging",
            current_route="recycling",
            supplier_takeback_available="yes",
        ),
        source_ids=["waste_hierarchy"],
        interpretation=(
            "Preparing for reuse/reuse-oriented loops sit above recycling, so a confirmed return loop is a reasonable "
            "screening priority for clean packaging."
        ),
        constraints={
            "required_human_review": False,
            "allowed_risk_levels": ["low", "medium"],
            "allowed_strategy_categories": [
                "supplier take-back / circular procurement",
                "internal reuse / returnable packaging",
            ],
            "required_output_terms_any": ["take-back", "return", "reuse"],
        },
    ),
    _challenge(
        "gc_hazardous_solvent",
        "Confirmed hazardous solvent waste",
        _stream(
            "GC007",
            "Spent solvent from cleaning",
            "chemicals/solvents",
            current_route="hazardous waste contractor",
            hazardous_flag="true",
            contamination_risk="medium",
        ),
        source_ids=["hazardous_producers", "waste_classification"],
        interpretation=(
            "Confirmed hazardous waste requires classification, safe separation/storage and authorised handling, "
            "so automatic low-risk reuse or recycling selection is inappropriate."
        ),
        constraints={
            "required_human_review": True,
            "allowed_risk_levels": ["high", "blocked"],
            "required_output_terms_any": ["review", "hazard", "compliance"],
        },
    ),
    _challenge(
        "gc_unknown_waste_classification",
        "Unknown waste composition and hazardous status",
        _stream(
            "GC008",
            "Unknown production residue",
            "unknown",
            current_route="general waste",
            hazardous_flag="unknown",
            contamination_risk="unknown",
        ),
        source_ids=["waste_classification", "hazardous_producers"],
        interpretation=(
            "A business must classify waste before it is collected, disposed of or recovered. Unknown hazardous "
            "status should therefore fail safe into review rather than a confident circular route."
        ),
        constraints={
            "required_human_review": True,
            "allowed_risk_levels": ["high", "blocked"],
            "required_output_terms_any": ["confirm", "review", "hazard"],
        },
    ),
    _challenge(
        "gc_classified_nonhaz_weee",
        "Classified non-hazardous electronic components",
        _stream(
            "GC009",
            "Classified non-hazardous electronic component rejects",
            "electronic components",
            current_route="specialist recovery",
            hazardous_flag="false",
            contamination_risk="low",
            notes="Classification completed; no hazardous properties identified.",
        ),
        source_ids=["weee_classification"],
        interpretation=(
            "Once WEEE classification is completed and the stream is confirmed non-hazardous, specialist recovery "
            "screening is reasonable provided no stronger reuse route is established."
        ),
        constraints={
            "required_human_review": False,
            "allowed_risk_levels": ["low", "medium"],
            "allowed_strategy_categories": ["open-loop recycling / specialist recovery"],
            "required_output_terms_any": ["specialist", "recovery", "recycler"],
        },
    ),
    _challenge(
        "gc_high_contamination_metal",
        "High-contamination metal requiring specialist review",
        _stream(
            "GC010",
            "Paint and oil contaminated steel components",
            "metals",
            current_route="general scrap",
            hazardous_flag="false",
            contamination_risk="high",
        ),
        source_ids=["waste_classification", "waste_hierarchy"],
        interpretation=(
            "High contamination makes a direct reuse/recycling recommendation unsafe without better classification "
            "and route evidence; specialist review is a reasonable screening boundary."
        ),
        constraints={
            "required_human_review": True,
            "allowed_risk_levels": ["high", "blocked"],
            "allowed_strategy_categories": [
                "compliant disposal / specialist recovery",
                "human review required",
            ],
            "required_output_terms_any": ["specialist", "review", "contamination"],
        },
    ),
]


def list_grounded_challenge_cases() -> list[dict[str, Any]]:
    return GROUNDED_CHALLENGE_CASES


def _output_text(recommendation: Any) -> str:
    return " ".join(
        [
            recommendation.recommended_circular_action,
            recommendation.circular_strategy_category,
            recommendation.reasoning,
            recommendation.next_action,
            recommendation.missing_data,
        ]
    ).lower()


def _check(check_id: str, passed: bool, expected: Any, actual: Any, detail: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "expected": expected,
        "actual": actual,
        "detail": detail,
    }


def evaluate_grounded_challenge_case(case: dict[str, Any]) -> dict[str, Any]:
    recommendation = recommend_for_stream(SimpleNamespace(**case["stream"]))
    constraints = case["constraints"]
    text = _output_text(recommendation)
    checks: list[dict[str, Any]] = []

    if "required_human_review" in constraints:
        expected = constraints["required_human_review"]
        checks.append(
            _check(
                "human_review_gate",
                recommendation.human_review_required == expected,
                expected,
                recommendation.human_review_required,
                "Human-review requirement should match the grounded safety/classification constraint.",
            )
        )

    allowed_risks = constraints.get("allowed_risk_levels", [])
    if allowed_risks:
        checks.append(
            _check(
                "risk_level",
                recommendation.risk_level in allowed_risks,
                allowed_risks,
                recommendation.risk_level,
                "Risk level should remain within the grounded acceptable range.",
            )
        )

    allowed_categories = constraints.get("allowed_strategy_categories", [])
    if allowed_categories:
        checks.append(
            _check(
                "allowed_strategy_category",
                recommendation.circular_strategy_category in allowed_categories,
                allowed_categories,
                recommendation.circular_strategy_category,
                "Strategy category should fall within the independently defined acceptable set.",
            )
        )

    forbidden_categories = constraints.get("forbidden_strategy_categories", [])
    if forbidden_categories:
        checks.append(
            _check(
                "forbidden_strategy_category",
                recommendation.circular_strategy_category not in forbidden_categories,
                [f"not {value}" for value in forbidden_categories],
                recommendation.circular_strategy_category,
                "Strategy category must avoid externally grounded unsafe/inappropriate routes.",
            )
        )

    required_terms = constraints.get("required_output_terms_any", [])
    if required_terms:
        present = [term for term in required_terms if term.lower() in text]
        checks.append(
            _check(
                "required_output_concept",
                bool(present),
                required_terms,
                present,
                "At least one grounded concept should be visible in action, reasoning, next action or missing-data output.",
            )
        )

    forbidden_terms = constraints.get("forbidden_output_terms_any", [])
    if forbidden_terms:
        present = [term for term in forbidden_terms if term.lower() in text]
        checks.append(
            _check(
                "forbidden_output_concept",
                not present,
                [f"not {term}" for term in forbidden_terms],
                present,
                "Grounded unsafe/inappropriate concepts should not appear in the decision output.",
            )
        )

    failed = [check for check in checks if check["status"] == "fail"]

    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "case_type": case["case_type"],
        "jurisdiction": case["jurisdiction"],
        "label_source": case["label_source"],
        "validation_status": case["validation_status"],
        "status": "pass" if not failed else "gap",
        "failed_check_count": len(failed),
        "checks": checks,
        "actual": {
            "rule_applied": recommendation.rule_applied,
            "recommended_circular_action": recommendation.recommended_circular_action,
            "circular_strategy_category": recommendation.circular_strategy_category,
            "risk_level": recommendation.risk_level,
            "human_review_required": recommendation.human_review_required,
            "missing_data": recommendation.missing_data,
        },
        "interpretation": case["interpretation"],
        "source_ids": case["source_ids"],
        "sources": case["sources"],
    }


def run_grounded_challenge_validation(case_ids: list[str] | None = None) -> dict[str, Any]:
    selected_ids = set(case_ids or [])
    cases = [
        case
        for case in GROUNDED_CHALLENGE_CASES
        if not selected_ids or case["case_id"] in selected_ids
    ]
    results = [evaluate_grounded_challenge_case(case) for case in cases]

    total = len(results)
    passed = sum(1 for result in results if result["status"] == "pass")
    gaps = total - passed
    failed_checks = sum(result["failed_check_count"] for result in results)

    check_breakdown: dict[str, dict[str, int | float]] = {}
    for result in results:
        for check in result["checks"]:
            bucket = check_breakdown.setdefault(
                check["check_id"],
                {"passed": 0, "failed": 0, "total": 0, "pass_pct": 0.0},
            )
            bucket["total"] += 1
            if check["status"] == "pass":
                bucket["passed"] += 1
            else:
                bucket["failed"] += 1

    for bucket in check_breakdown.values():
        bucket["pass_pct"] = round((bucket["passed"] / bucket["total"]) * 100, 1) if bucket["total"] else 0.0

    return {
        "suite_name": "circular_decision_grounded_challenge_v1",
        "validation_status": "authoritative_guidance_interpretation_not_independent_assurance",
        "jurisdiction": "England",
        "total_cases": total,
        "passing_cases": passed,
        "gap_cases": gaps,
        "pass_pct": round((passed / total) * 100, 1) if total else 0.0,
        "failed_checks": failed_checks,
        "check_breakdown": check_breakdown,
        "gap_case_ids": [result["case_id"] for result in results if result["status"] == "gap"],
        "source_catalogue": GROUNDING_SOURCES,
        "results": results,
        "governance_note": (
            "This challenge suite is grounded in authoritative public guidance but the translation of guidance into "
            "software constraints remains an internal product interpretation. Results identify product gaps for review; "
            "they are not legal advice, regulatory approval, professional assurance or independent expert validation."
        ),
    }
