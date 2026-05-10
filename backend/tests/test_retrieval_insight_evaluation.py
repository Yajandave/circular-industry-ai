"""Milestone 11C retrieval and insight quality evaluation tests."""

from fastapi.testclient import TestClient

from app.evaluation.service import list_evaluation_cases, run_evaluation_suite
from app.main import app

client = TestClient(app)


def test_evaluation_cases_are_available():
    cases = list_evaluation_cases()
    case_ids = {case["case_id"] for case in cases}

    assert "eval_mixed_plastics_high_contamination" in case_ids
    assert "eval_unknown_generic_rejects" in case_ids
    assert len(cases) >= 4


def test_plastics_evaluation_case_passes_core_false_positive_checks():
    result = run_evaluation_suite(case_ids=["eval_mixed_plastics_high_contamination"])

    assert result["total_cases"] == 1
    case_result = result["results"][0]
    assert case_result["case_id"] == "eval_mixed_plastics_high_contamination"
    assert "plastics" in case_result["matched_material_families"]
    assert "future_battery_recycling_v1" not in case_result["source_knowledge_ids"]

    checks = {check["check_id"]: check for check in case_result["checks"]}
    assert checks["expected_material_family:plastics"]["status"] == "pass"
    assert checks["forbidden_material_family:batteries"]["status"] == "pass"
    assert checks["forbidden_knowledge_id:future_battery_recycling_v1"]["status"] == "pass"
    assert checks["quality_gate:notes_independence"]["status"] == "pass"
    assert checks["quality_gate:claim_boundary_present"]["status"] == "pass"
    assert checks["claim_boundary_present"]["status"] == "pass"
    assert checks["notes_dependency_not_required"]["status"] == "pass"


def test_unknown_generic_case_does_not_force_material_match():
    result = run_evaluation_suite(case_ids=["eval_unknown_generic_rejects"])

    case_result = result["results"][0]
    checks = {check["check_id"]: check for check in case_result["checks"]}

    assert case_result["matched_material_families"] == []
    assert checks["expect_no_material_match"]["status"] == "pass"
    assert checks["forbidden_material_family:plastics"]["status"] == "pass"
    assert checks["notes_dependency_not_required"]["status"] == "pass"


def test_evaluation_cases_endpoint():
    response = client.get("/api/evaluation/cases")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) >= 4
    assert payload[0]["case_id"]


def test_evaluation_run_endpoint_selected_case():
    response = client.post(
        "/api/evaluation/run",
        json={"case_ids": ["eval_mixed_plastics_high_contamination"]},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["suite_name"] == "retrieval_insight_quality_evaluation_v1"
    assert payload["total_cases"] == 1
    assert payload["results"][0]["case_id"] == "eval_mixed_plastics_high_contamination"


def test_evaluation_summary_endpoint_runs_suite():
    response = client.get("/api/evaluation/summary")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total_cases"] >= 4
    assert "status_breakdown" in payload
    assert "governance_note" in payload
