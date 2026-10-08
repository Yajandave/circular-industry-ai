"""Tests for qualitative governance maturity.

These tests deliberately avoid legacy 0-100 score inputs. Maturity must be
explainable from explicit risk, human-review, rule and missing-evidence
conditions rather than from pseudo-precise numerical thresholds.
"""

from types import SimpleNamespace

from app.governance_maturity import (
    SCORE_SEMANTICS,
    decision_support_band,
    evidence_maturity,
)


def _rec(**overrides):
    base = {
        "risk_level": "low",
        "human_review_required": False,
        "missing_data": "none identified for MVP fields",
        "rule_applied": "R005_METAL_CLOSED_LOOP",
        # Deliberately present legacy fields to show they are ignored.
        "confidence_score": 5,
        "evidence_quality_score": 5,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_screening_ready_does_not_depend_on_legacy_numeric_scores():
    low_numbers = _rec(confidence_score=1, evidence_quality_score=1)
    high_numbers = _rec(confidence_score=99, evidence_quality_score=99)

    assert evidence_maturity(low_numbers) == "screening_ready"
    assert evidence_maturity(high_numbers) == "screening_ready"
    assert decision_support_band(low_numbers) == "strong_screening_basis"
    assert decision_support_band(high_numbers) == "strong_screening_basis"


def test_missing_evidence_creates_screening_ready_with_checks():
    rec = _rec(
        missing_data="supplier take-back evidence",
        confidence_score=99,
        evidence_quality_score=99,
    )

    assert evidence_maturity(rec) == "screening_ready_with_checks"
    assert decision_support_band(rec) == "screening_basis_with_checks"


def test_default_rule_is_insufficient_for_route_change():
    rec = _rec(
        rule_applied="R999_DEFAULT_EVIDENCE_IMPROVEMENT",
        confidence_score=99,
        evidence_quality_score=99,
    )

    assert evidence_maturity(rec) == "insufficient_for_route_change"
    assert decision_support_band(rec) == "limited_screening_basis"


def test_human_review_overrides_apparent_numeric_strength():
    rec = _rec(
        risk_level="high",
        human_review_required=True,
        confidence_score=100,
        evidence_quality_score=100,
    )

    assert evidence_maturity(rec) == "controlled_review_required"
    assert decision_support_band(rec) == "human_review_gate"


def test_score_semantics_reject_probability_and_assurance_interpretation():
    lower = SCORE_SEMANTICS.lower()
    assert "not probabilities" in lower
    assert "assurance" in lower
    assert "not" in lower
