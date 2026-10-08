"""Qualitative governance states for circular-economy decision support.

The project retains legacy numeric evidence/confidence fields for backwards
compatibility and regression analysis. These functions deliberately do not use
those numbers. Operator-facing maturity should be based on explicit conditions:
risk, human-review gates, missing evidence and the rule family applied.
"""

from __future__ import annotations

from typing import Protocol


SCORE_SEMANTICS = (
    "Legacy 0-100 evidence and confidence scores are internal heuristic signals "
    "retained for backwards compatibility and regression analysis. They are not "
    "probabilities, assurance ratings, independently calibrated measures or proof "
    "of decision accuracy."
)


class RecommendationLike(Protocol):
    risk_level: str
    human_review_required: bool
    missing_data: str
    rule_applied: str


def _clean(value: object) -> str:
    return str(value or "").strip().lower()


def has_material_evidence_gap(recommendation: RecommendationLike) -> bool:
    """Return True when the stored missing-data field contains a real gap."""
    value = _clean(recommendation.missing_data)
    return value not in {
        "",
        "none",
        "none recorded",
        "none identified",
        "none identified for mvp fields",
    }


def evidence_maturity(recommendation: RecommendationLike) -> str:
    """Return an operator-facing qualitative evidence state."""
    risk = _clean(recommendation.risk_level)
    rule = _clean(recommendation.rule_applied)

    if recommendation.human_review_required or risk in {"high", "blocked"}:
        return "controlled_review_required"
    if rule == "r999_default_evidence_improvement":
        return "insufficient_for_route_change"
    if risk == "medium" or has_material_evidence_gap(recommendation):
        return "screening_ready_with_checks"
    return "screening_ready"


def decision_support_band(recommendation: RecommendationLike) -> str:
    """Describe strength of the screening basis without implying probability."""
    risk = _clean(recommendation.risk_level)
    rule = _clean(recommendation.rule_applied)

    if recommendation.human_review_required or risk in {"high", "blocked"}:
        return "human_review_gate"
    if rule == "r999_default_evidence_improvement":
        return "limited_screening_basis"
    if risk == "medium" or has_material_evidence_gap(recommendation):
        return "screening_basis_with_checks"
    return "strong_screening_basis"


def maturity_label(value: str) -> str:
    return {
        "controlled_review_required": "Controlled review required",
        "insufficient_for_route_change": "Insufficient for route change",
        "screening_ready_with_checks": "Screening-ready with checks",
        "screening_ready": "Screening-ready",
    }.get(value, value.replace("_", " ").strip().title())


def decision_support_label(value: str) -> str:
    return {
        "human_review_gate": "Human review gate",
        "limited_screening_basis": "Limited screening basis",
        "screening_basis_with_checks": "Screening basis with checks",
        "strong_screening_basis": "Strong screening basis",
    }.get(value, value.replace("_", " ").strip().title())
