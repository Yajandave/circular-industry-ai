"""Deterministic evaluation suite for retrieval and insight quality.

11C evaluates the complete intelligence chain:
retrieval -> graph -> autonomous insight -> agentic workflow quality gates.

The goal is not to prove real-world recycling or compliance.
The goal is to detect weak retrieval, false positives, missing claim boundaries and unsafe generated advice.
"""

from __future__ import annotations

from typing import Any

from app.agentic_retrieval.service import run_agentic_retrieval_workflow


EVALUATION_CASES: list[dict[str, Any]] = [
    {
        "case_id": "eval_mixed_plastics_high_contamination",
        "title": "Mixed plastics with high contamination",
        "description": "Blank-notes plastics case used to test plastics-only retrieval, contamination controls and unsafe-claim boundaries.",
        "stream": {
            "stream_id": "EVAL001",
            "stream_name": "Mixed polymer injection moulding rejects",
            "material": "mixed plastics",
            "source_process": "injection moulding",
            "monthly_quantity_kg": 1680,
            "current_route": "general waste",
            "disposal_cost_per_month": 720,
            "contamination_risk": "high",
            "hazardous_flag": "false",
            "department": "Production",
            "supplier": "PolyMax Resins",
            "supplier_takeback_available": "unknown",
            "recycled_content_available": "unknown",
            "notes": "",
        },
        "expectations": {
            "expected_material_families": ["plastics"],
            "forbidden_material_families": ["batteries", "cardboard_packaging"],
            "expected_knowledge_ids": ["material_plastics_v1"],
            "forbidden_knowledge_ids": ["future_battery_recycling_v1", "material_batteries_v1", "material_cardboard_packaging_v1"],
            "required_evidence_terms": ["polymer", "contamination"],
            "required_do_not_claim_terms": ["verified recycling", "closed-loop", "carbon"],
            "required_quality_gates": {
                "notes_independence": "pass",
                "claim_boundary_present": "pass",
                "graph_relationships_present": "pass",
                "human_review_control": "review",
            },
        },
    },
    {
        "case_id": "eval_aluminium_machining_offcuts",
        "title": "Aluminium machining offcuts",
        "description": "Low-contamination metal stream used to test metals retrieval, grade/segregation evidence and candidate route relationships.",
        "stream": {
            "stream_id": "EVAL002",
            "stream_name": "Aluminium machining offcuts",
            "material": "aluminium",
            "source_process": "CNC machining",
            "monthly_quantity_kg": 1850,
            "current_route": "scrap merchant",
            "disposal_cost_per_month": 420,
            "contamination_risk": "low",
            "hazardous_flag": "false",
            "department": "Machining",
            "supplier": "AluForm Metals Ltd",
            "supplier_takeback_available": "unknown",
            "recycled_content_available": "unknown",
            "notes": "",
        },
        "expectations": {
            "expected_material_families": ["metals"],
            "forbidden_material_families": ["plastics", "batteries"],
            "expected_knowledge_ids": [],
            "forbidden_knowledge_ids": ["future_battery_recycling_v1"],
            "required_evidence_terms": ["grade"],
            "required_do_not_claim_terms": ["verified"],
            "required_quality_gates": {
                "notes_independence": "pass",
                "claim_boundary_present": "pass",
                "graph_relationships_present": "pass",
            },
        },
    },
    {
        "case_id": "eval_unknown_generic_rejects",
        "title": "Unknown generic production rejects",
        "description": "Generic low-information stream used to test false-positive control when material data is weak.",
        "stream": {
            "stream_id": "EVAL003",
            "stream_name": "General production rejects",
            "material": "unknown",
            "source_process": "production",
            "monthly_quantity_kg": 100,
            "current_route": "general waste",
            "disposal_cost_per_month": 50,
            "contamination_risk": "unknown",
            "hazardous_flag": "unknown",
            "department": "Production",
            "supplier": "Unknown",
            "supplier_takeback_available": "unknown",
            "recycled_content_available": "unknown",
            "notes": "",
        },
        "expectations": {
            "expected_material_families": [],
            "forbidden_material_families": ["plastics", "metals", "batteries", "cardboard_packaging"],
            "expected_knowledge_ids": [],
            "forbidden_knowledge_ids": ["material_plastics_v1", "material_metals_v1", "future_battery_recycling_v1"],
            "required_evidence_terms": [],
            "required_do_not_claim_terms": ["verified"],
            "required_quality_gates": {
                "notes_independence": "pass",
                "claim_boundary_present": "pass",
                "human_review_control": "review",
            },
            "expect_no_material_match": True,
        },
    },
    {
        "case_id": "eval_paint_contaminated_metal_brackets",
        "title": "Paint-contaminated metal brackets",
        "description": "High-contamination metal stream used to test controlled review and claim-safety behaviour.",
        "stream": {
            "stream_id": "EVAL004",
            "stream_name": "Paint-contaminated metal brackets",
            "material": "metals",
            "source_process": "coating rework",
            "monthly_quantity_kg": 310,
            "current_route": "hazardous waste contractor",
            "disposal_cost_per_month": 310,
            "contamination_risk": "high",
            "hazardous_flag": "unknown",
            "department": "Finishing",
            "supplier": "MetalFab Components",
            "supplier_takeback_available": "unknown",
            "recycled_content_available": "unknown",
            "notes": "",
        },
        "expectations": {
            "expected_material_families": ["metals"],
            "forbidden_material_families": ["plastics", "cardboard_packaging"],
            "expected_knowledge_ids": [],
            "forbidden_knowledge_ids": ["future_battery_recycling_v1"],
            "required_evidence_terms": ["contamination"],
            "required_do_not_claim_terms": ["safe", "verified"],
            "required_quality_gates": {
                "notes_independence": "pass",
                "claim_boundary_present": "pass",
                "human_review_control": "review",
            },
        },
    },
]


def list_evaluation_cases() -> list[dict[str, Any]]:
    """Return available deterministic evaluation cases."""
    return EVALUATION_CASES


def _lower_values(values: list[Any]) -> list[str]:
    return [str(value or "").lower() for value in values]


def _contains_term(values: list[Any], term: str) -> bool:
    term_lower = term.lower()
    return any(term_lower in value for value in _lower_values(values))


def _check(check_id: str, status: str, expected: Any, actual: Any, detail: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": status,
        "expected": expected,
        "actual": actual,
        "detail": detail,
    }


def _case_status(checks: list[dict[str, Any]]) -> str:
    statuses = {check["status"] for check in checks}
    if "fail" in statuses:
        return "fail"
    if "review" in statuses:
        return "review"
    return "pass"


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    workflow = run_agentic_retrieval_workflow(case["stream"], save_insight=False)
    expectations = case.get("expectations", {})

    checks: list[dict[str, Any]] = []

    families = workflow["retrieval_summary"].get("matched_material_families", [])
    family_set = set(families)
    source_ids = set(workflow["retrieval_summary"].get("source_knowledge_ids", []))
    insight = workflow.get("insight", {})
    gates = {gate["gate"]: gate["status"] for gate in workflow.get("quality_gates", [])}

    expected_families = expectations.get("expected_material_families", [])
    for family in expected_families:
        checks.append(
            _check(
                f"expected_material_family:{family}",
                "pass" if family in family_set else "fail",
                family,
                families,
                "Expected material family should be present in retrieval output.",
            )
        )

    if expectations.get("expect_no_material_match"):
        checks.append(
            _check(
                "expect_no_material_match",
                "pass" if not families else "fail",
                [],
                families,
                "Generic unknown stream should not trigger a material-family match.",
            )
        )

    for family in expectations.get("forbidden_material_families", []):
        checks.append(
            _check(
                f"forbidden_material_family:{family}",
                "pass" if family not in family_set else "fail",
                f"not {family}",
                families,
                "Forbidden material family should not appear.",
            )
        )

    for knowledge_id in expectations.get("expected_knowledge_ids", []):
        checks.append(
            _check(
                f"expected_knowledge_id:{knowledge_id}",
                "pass" if knowledge_id in source_ids else "fail",
                knowledge_id,
                sorted(source_ids),
                "Expected knowledge ID should support the workflow.",
            )
        )

    for knowledge_id in expectations.get("forbidden_knowledge_ids", []):
        checks.append(
            _check(
                f"forbidden_knowledge_id:{knowledge_id}",
                "pass" if knowledge_id not in source_ids else "fail",
                f"not {knowledge_id}",
                sorted(source_ids),
                "Forbidden knowledge ID should not be retrieved.",
            )
        )

    evidence_needed = insight.get("evidence_needed", [])
    for term in expectations.get("required_evidence_terms", []):
        checks.append(
            _check(
                f"required_evidence_term:{term}",
                "pass" if _contains_term(evidence_needed, term) else "review",
                term,
                evidence_needed,
                "Evidence list should include this concept.",
            )
        )

    do_not_claim = insight.get("do_not_claim", [])
    for term in expectations.get("required_do_not_claim_terms", []):
        checks.append(
            _check(
                f"required_do_not_claim_term:{term}",
                "pass" if _contains_term(do_not_claim, term) else "review",
                term,
                do_not_claim,
                "Unsafe-claim boundaries should include this concept.",
            )
        )

    for gate, expected_status in expectations.get("required_quality_gates", {}).items():
        actual_status = gates.get(gate)
        checks.append(
            _check(
                f"quality_gate:{gate}",
                "pass" if actual_status == expected_status else "fail",
                expected_status,
                actual_status,
                "Workflow quality gate should match expected status.",
            )
        )

    checks.append(
        _check(
            "claim_boundary_present",
            "pass" if insight.get("claim_boundary") else "fail",
            "non-empty claim boundary",
            insight.get("claim_boundary"),
            "Every evaluated insight must include a claim boundary.",
        )
    )

    checks.append(
        _check(
            "notes_dependency_not_required",
            "pass" if insight.get("notes_dependency") == "not_required" else "fail",
            "not_required",
            insight.get("notes_dependency"),
            "Generated insight should not depend on dataset notes.",
        )
    )

    checks.append(
        _check(
            "graph_has_nodes_and_edges",
            "pass" if workflow.get("graph", {}).get("nodes") and workflow.get("graph", {}).get("edges") else "review",
            "nodes and edges present",
            {
                "node_count": len(workflow.get("graph", {}).get("nodes", [])),
                "edge_count": len(workflow.get("graph", {}).get("edges", [])),
            },
            "Knowledge graph should explain relationship path when knowledge is matched.",
        )
    )

    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "status": _case_status(checks),
        "checks": checks,
        "workflow_id": workflow["workflow_id"],
        "matched_material_families": families,
        "source_knowledge_ids": sorted(source_ids),
        "quality_gate_summary": gates,
        "governance_note": (
            "Evaluation checks retrieval and insight quality. Passing evaluation does not verify operational feasibility, "
            "supplier acceptance, legal compliance, circularity claims, carbon savings or financial savings."
        ),
    }


def run_evaluation_suite(case_ids: list[str] | None = None) -> dict[str, Any]:
    """Run selected or all evaluation cases."""
    selected_ids = set(case_ids or [])
    cases = [
        case
        for case in EVALUATION_CASES
        if not selected_ids or case["case_id"] in selected_ids
    ]

    results = [_evaluate_case(case) for case in cases]

    status_breakdown = {"pass": 0, "review": 0, "fail": 0}
    for result in results:
        status_breakdown[result["status"]] = status_breakdown.get(result["status"], 0) + 1

    failed_checks = sum(
        1
        for result in results
        for check in result["checks"]
        if check["status"] == "fail"
    )
    review_checks = sum(
        1
        for result in results
        for check in result["checks"]
        if check["status"] == "review"
    )

    overall_status = "pass"
    if failed_checks:
        overall_status = "fail"
    elif review_checks:
        overall_status = "review"

    return {
        "suite_name": "retrieval_insight_quality_evaluation_v1",
        "overall_status": overall_status,
        "total_cases": len(results),
        "status_breakdown": status_breakdown,
        "failed_checks": failed_checks,
        "review_checks": review_checks,
        "results": results,
        "governance_note": (
            "The evaluation suite checks internal retrieval, graph, workflow and insight quality. "
            "It is a product quality-control layer, not third-party verification of circular economy outcomes."
        ),
    }
