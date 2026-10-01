from fastapi.testclient import TestClient

from app.decision_validation import (
    DECISION_VALIDATION_CASES,
    evaluate_decision_case,
    run_decision_validation,
)
from app.main import app

client = TestClient(app)


def test_internal_decision_benchmark_contains_20_cases_and_full_ruleset():
    assert len(DECISION_VALIDATION_CASES) == 20

    expected_rules = {
        "R001_HAZARDOUS_OR_UNKNOWN_REVIEW",
        "R002_HIGH_CONTAMINATION_REVIEW",
        "R003_REDUCE_AT_SOURCE",
        "R004_SUPPLIER_TAKEBACK_AVAILABLE",
        "R005_METAL_CLOSED_LOOP",
        "R006_PACKAGING_REUSE",
        "R007_MIXED_PLASTIC_RECYCLING",
        "R008_PLASTIC_CLOSED_LOOP",
        "R009_SYMBIOSIS_OR_RESOURCE_RECOVERY",
        "R010_SPECIALIST_RECOVERY",
        "R999_DEFAULT_EVIDENCE_IMPROVEMENT",
    }

    actual_rules = {
        case["expectations"]["rule_applied"]
        for case in DECISION_VALIDATION_CASES
    }
    assert expected_rules.issubset(actual_rules)

    assert all(
        case["label_source"] == "internal_reference_expectation"
        for case in DECISION_VALIDATION_CASES
    )
    assert all(
        case["validation_status"] == "benchmark_draft"
        for case in DECISION_VALIDATION_CASES
    )


def test_each_internal_benchmark_case_agrees_with_current_deterministic_engine():
    results = [evaluate_decision_case(case) for case in DECISION_VALIDATION_CASES]

    failed = [result for result in results if result["status"] != "pass"]
    assert failed == []


def test_full_decision_validation_summary_reports_100_percent_internal_agreement():
    result = run_decision_validation()

    assert result["suite_name"] == "circular_decision_internal_benchmark_v1"
    assert result["benchmark_status"] == "internal_reference_only"
    assert result["total_cases"] == 20
    assert result["full_agreement_cases"] == 20
    assert result["full_agreement_pct"] == 100.0

    for metric in result["agreement"].values():
        assert metric["passed"] == 20
        assert metric["total"] == 20
        assert metric["agreement_pct"] == 100.0

    assert "not external expert validation" in result["governance_note"].lower()


def test_decision_validation_can_run_selected_case_only():
    result = run_decision_validation(case_ids=["dv_unknown_material"])

    assert result["total_cases"] == 1
    assert result["full_agreement_cases"] == 1
    assert result["results"][0]["case_id"] == "dv_unknown_material"
    assert result["results"][0]["actual"]["human_review_required"] is True


def test_decision_validation_api_returns_cases_and_summary():
    cases_response = client.get("/api/decision-validation/cases")
    assert cases_response.status_code == 200
    cases = cases_response.json()
    assert len(cases) == 20
    assert cases[0]["label_source"] == "internal_reference_expectation"

    summary_response = client.get("/api/decision-validation/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_cases"] == 20
    assert summary["full_agreement_pct"] == 100.0
    assert summary["benchmark_status"] == "internal_reference_only"


def test_decision_validation_api_selected_run():
    response = client.post(
        "/api/decision-validation/run",
        json={"case_ids": ["dv_metal_closed_loop", "dv_battery_blocked"]},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["total_cases"] == 2
    assert {item["case_id"] for item in result["results"]} == {
        "dv_metal_closed_loop",
        "dv_battery_blocked",
    }
