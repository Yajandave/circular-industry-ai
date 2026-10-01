from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.blind_review_analysis import build_multi_reviewer_analysis
from app.main import app

client = TestClient(app)


BASE_TIME = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


def _record(
    record_id,
    reviewer,
    case_id,
    *,
    strategy,
    risk,
    human_review,
    confidence=4,
    reasoning="Reviewer reasoning.",
    offset_minutes=0,
    system_strategy=None,
    system_risk=None,
    system_human_review=None,
    system_rule="R_TEST",
    system_action="System action.",
):
    return SimpleNamespace(
        id=record_id,
        reviewer_name=reviewer,
        reviewer_role="Waste Specialist",
        reviewer_organisation="Independent Practice",
        case_id=case_id,
        reviewer_strategy_category=strategy,
        reviewer_risk_level=risk,
        reviewer_human_review_required=human_review,
        reviewer_confidence=confidence,
        reviewer_reasoning=reasoning,
        system_rule_applied=system_rule,
        system_strategy_category=system_strategy or strategy,
        system_risk_level=system_risk or risk,
        system_human_review_required=(
            human_review if system_human_review is None else system_human_review
        ),
        system_recommended_action=system_action,
        created_at=BASE_TIME + timedelta(minutes=offset_minutes),
    )


def test_multi_reviewer_analysis_reports_majority_and_pairwise_agreement():
    records = [
        _record(1, "Reviewer A", "case-1", strategy="closed-loop recycling", risk="low", human_review=False),
        _record(2, "Reviewer B", "case-1", strategy="closed-loop recycling", risk="low", human_review=False, offset_minutes=1),
        _record(3, "Reviewer C", "case-1", strategy="open-loop recycling", risk="medium", human_review=True, offset_minutes=2,
                system_strategy="closed-loop recycling", system_risk="low", system_human_review=False),
    ]

    result = build_multi_reviewer_analysis(records)
    case = result["cases"][0]

    assert result["unique_reviewers"] == 3
    assert result["cases_with_multiple_reviewers"] == 1
    assert case["strategy_consensus"]["leading_label"] == "closed-loop recycling"
    assert case["strategy_consensus"]["leading_count"] == 2
    assert case["strategy_consensus"]["leading_share_pct"] == 66.7
    assert case["strategy_consensus"]["consensus_status"] == "strong_majority"
    assert case["strategy_consensus"]["pairwise_agreement_pct"] == 33.3

    assert case["risk_consensus"]["leading_label"] == "low"
    assert case["human_review_consensus"]["leading_label"] == "false"
    assert case["system_matches_strategy_consensus"] is True
    assert case["system_matches_risk_consensus"] is True
    assert case["system_matches_human_review_consensus"] is True


def test_two_reviewer_split_has_no_leading_consensus_label():
    records = [
        _record(1, "Reviewer A", "case-1", strategy="closed-loop recycling", risk="low", human_review=False),
        _record(2, "Reviewer B", "case-1", strategy="open-loop recycling", risk="medium", human_review=True, offset_minutes=1),
    ]

    result = build_multi_reviewer_analysis(records)
    case = result["cases"][0]

    assert case["strategy_consensus"]["consensus_status"] == "split"
    assert case["strategy_consensus"]["leading_label"] is None
    assert case["risk_consensus"]["leading_label"] is None
    assert case["human_review_consensus"]["leading_label"] is None
    assert case["system_matches_strategy_consensus"] is None
    assert case["system_matches_risk_consensus"] is None
    assert case["system_matches_human_review_consensus"] is None


def test_single_reviewer_case_is_not_presented_as_consensus():
    records = [
        _record(1, "Reviewer A", "case-1", strategy="closed-loop recycling", risk="low", human_review=False),
    ]

    result = build_multi_reviewer_analysis(records)
    case = result["cases"][0]

    assert result["unique_reviewers"] == 1
    assert result["cases_with_multiple_reviewers"] == 0
    assert case["strategy_consensus"]["consensus_status"] == "single_reviewer_only"
    assert case["strategy_consensus"]["pairwise_agreement_pct"] is None
    assert result["overall_pairwise_agreement"]["strategy_pct"] is None


def test_latest_repeat_submission_per_reviewer_case_is_used_once():
    records = [
        _record(1, "Reviewer A", "case-1", strategy="open-loop recycling", risk="medium", human_review=True),
        _record(2, "Reviewer A", "case-1", strategy="closed-loop recycling", risk="low", human_review=False, offset_minutes=5),
        _record(3, "Reviewer B", "case-1", strategy="closed-loop recycling", risk="low", human_review=False, offset_minutes=2),
    ]

    result = build_multi_reviewer_analysis(records)
    case = result["cases"][0]

    assert result["deduplicated_submission_count"] == 2
    assert result["unique_reviewers"] == 2
    assert case["reviewer_count"] == 2
    assert case["strategy_consensus"]["distribution"] == {"closed-loop recycling": 2}
    assert case["strategy_consensus"]["consensus_status"] == "unanimous"


def test_analysis_discloses_system_snapshot_changes_across_reviews():
    records = [
        _record(
            1,
            "Reviewer A",
            "case-1",
            strategy="closed-loop recycling",
            risk="low",
            human_review=False,
            system_strategy="open-loop recycling",
            system_risk="medium",
            system_human_review=True,
            system_rule="R_OLD",
            system_action="Old action.",
        ),
        _record(
            2,
            "Reviewer B",
            "case-1",
            strategy="closed-loop recycling",
            risk="low",
            human_review=False,
            offset_minutes=10,
            system_strategy="closed-loop recycling",
            system_risk="low",
            system_human_review=False,
            system_rule="R_NEW",
            system_action="New action.",
        ),
    ]

    result = build_multi_reviewer_analysis(records)
    case = result["cases"][0]

    assert case["system_snapshot_consistent"] is False
    assert case["system_snapshot_count"] == 2
    assert len(case["system_snapshots"]) == 2
    assert case["latest_system_snapshot"]["rule_applied"] == "R_NEW"
    assert case["system_matches_strategy_consensus"] is True
    assert "model-version effects" in result["governance_note"]


def test_blind_review_analysis_endpoint_returns_transparent_metrics():
    response = client.get("/api/decision-validation/blind-review-analysis")

    assert response.status_code == 200
    result = response.json()
    assert "unique_reviewers" in result
    assert "overall_pairwise_agreement" in result
    assert "system_consensus_match" in result
    assert "cases" in result
    assert "consensus is not treated as ground truth" in result["governance_note"].lower()
