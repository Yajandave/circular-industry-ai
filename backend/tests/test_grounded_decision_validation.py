from fastapi.testclient import TestClient

from app.grounded_decision_validation import (
    GROUNDING_SOURCES,
    GROUNDED_CHALLENGE_CASES,
    evaluate_grounded_challenge_case,
    run_grounded_challenge_validation,
)
from app.main import app

client = TestClient(app)


def test_grounded_challenge_suite_uses_10_guidance_based_cases_without_rule_id_labels():
    assert len(GROUNDED_CHALLENGE_CASES) == 10
    assert len(GROUNDING_SOURCES) >= 6

    assert all(
        case["label_source"] == "authoritative_guidance_interpretation"
        for case in GROUNDED_CHALLENGE_CASES
    )
    assert all(
        case["validation_status"] == "grounded_challenge_v1"
        for case in GROUNDED_CHALLENGE_CASES
    )
    assert all(
        "rule_applied" not in case["constraints"]
        for case in GROUNDED_CHALLENGE_CASES
    )
    assert all(case["sources"] for case in GROUNDED_CHALLENGE_CASES)


def test_grounded_challenge_suite_exposes_current_engine_gaps():
    result = run_grounded_challenge_validation()

    assert result["suite_name"] == "circular_decision_grounded_challenge_v1"
    assert result["total_cases"] == 10
    assert result["validation_status"] == "authoritative_guidance_interpretation_not_independent_assurance"

    expected_gap_ids = {
        "gc_damaged_lithium_battery",
        "gc_unclassified_weee",
        "gc_hazardous_residue_packaging",
        "gc_edible_food_surplus",
    }
    assert expected_gap_ids.issubset(set(result["gap_case_ids"]))
    assert result["gap_cases"] >= len(expected_gap_ids)
    assert result["passing_cases"] + result["gap_cases"] == 10
    assert "not legal advice" in result["governance_note"].lower()


def test_grounded_challenge_known_safe_boundaries_still_pass():
    case_map = {case["case_id"]: case for case in GROUNDED_CHALLENGE_CASES}

    passing_ids = {
        "gc_metal_trim_prevention",
        "gc_clean_packaging_takeback",
        "gc_hazardous_solvent",
        "gc_unknown_waste_classification",
        "gc_classified_nonhaz_weee",
        "gc_high_contamination_metal",
    }

    for case_id in passing_ids:
        result = evaluate_grounded_challenge_case(case_map[case_id])
        assert result["status"] == "pass", result


def test_damaged_lithium_battery_challenge_flags_review_and_risk_gap():
    case = next(
        item
        for item in GROUNDED_CHALLENGE_CASES
        if item["case_id"] == "gc_damaged_lithium_battery"
    )
    result = evaluate_grounded_challenge_case(case)

    assert result["status"] == "gap"
    failed_checks = {
        check["check_id"]
        for check in result["checks"]
        if check["status"] == "fail"
    }
    assert "human_review_gate" in failed_checks
    assert "risk_level" in failed_checks


def test_edible_food_surplus_challenge_flags_hierarchy_gap():
    case = next(
        item
        for item in GROUNDED_CHALLENGE_CASES
        if item["case_id"] == "gc_edible_food_surplus"
    )
    result = evaluate_grounded_challenge_case(case)

    assert result["status"] == "gap"
    assert result["actual"]["circular_strategy_category"] == "industrial symbiosis / resource recovery"

    failed_checks = {
        check["check_id"]
        for check in result["checks"]
        if check["status"] == "fail"
    }
    assert "allowed_strategy_category" in failed_checks
    assert "forbidden_strategy_category" in failed_checks


def test_grounded_challenge_api_returns_cases_and_gap_summary():
    cases_response = client.get("/api/decision-validation/challenge-cases")
    assert cases_response.status_code == 200
    cases = cases_response.json()
    assert len(cases) == 10
    assert all(case["jurisdiction"] == "England" for case in cases)

    summary_response = client.get("/api/decision-validation/challenge-summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_cases"] == 10
    assert summary["gap_cases"] >= 4
    assert "gc_damaged_lithium_battery" in summary["gap_case_ids"]
    assert summary["source_catalogue"]["waste_classification"]["publisher"]


def test_grounded_challenge_api_can_run_selected_cases():
    response = client.post(
        "/api/decision-validation/challenge-run",
        json={
            "case_ids": [
                "gc_damaged_lithium_battery",
                "gc_metal_trim_prevention",
            ]
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["total_cases"] == 2
    assert {item["case_id"] for item in result["results"]} == {
        "gc_damaged_lithium_battery",
        "gc_metal_trim_prevention",
    }
