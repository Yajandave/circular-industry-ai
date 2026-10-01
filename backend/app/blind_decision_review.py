"""Blind reviewer pack and reviewer-vs-system comparison helpers.

The blind pack deliberately excludes Circular Industry AI outputs, grounded
constraints, interpretations, source catalogue and expected answers.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from app.grounded_decision_validation import GROUNDED_CHALLENGE_CASES
from app.rules_engine import recommend_for_stream


CASE_MAP = {case["case_id"]: case for case in GROUNDED_CHALLENGE_CASES}

STRATEGY_CATEGORY_OPTIONS = [
    "human review required",
    "compliant disposal / specialist recovery",
    "reduce / process redesign",
    "supplier take-back / circular procurement",
    "closed-loop recycling",
    "internal reuse / returnable packaging",
    "open-loop recycling",
    "industrial symbiosis / resource recovery",
    "open-loop recycling / specialist recovery",
    "compliant disposal",
    "other / insufficient information",
]

RISK_LEVEL_OPTIONS = ["low", "medium", "high", "blocked"]


def build_blind_review_pack() -> list[dict[str, Any]]:
    pack: list[dict[str, Any]] = []
    for index, case in enumerate(GROUNDED_CHALLENGE_CASES, start=1):
        pack.append(
            {
                "case_id": case["case_id"],
                "case_number": index,
                "jurisdiction": case["jurisdiction"],
                "stream": case["stream"],
                "strategy_category_options": STRATEGY_CATEGORY_OPTIONS,
                "risk_level_options": RISK_LEVEL_OPTIONS,
                "reviewer_prompt": (
                    "Using only the case information shown, record the most appropriate screening-level "
                    "strategy category, risk level, whether human review is required, and your reasoning."
                ),
                "blind_pack_note": (
                    "This pack intentionally omits Circular Industry AI's recommendation, rule, validation "
                    "constraints, grounded interpretation and source catalogue until after reviewer submission."
                ),
            }
        )
    return pack


def system_snapshot_for_case(case_id: str) -> dict[str, Any]:
    case = CASE_MAP.get(case_id)
    if case is None:
        raise KeyError(case_id)

    recommendation = recommend_for_stream(SimpleNamespace(**case["stream"]))
    return {
        "case_id": case_id,
        "system_rule_applied": recommendation.rule_applied,
        "system_strategy_category": recommendation.circular_strategy_category,
        "system_risk_level": recommendation.risk_level,
        "system_human_review_required": recommendation.human_review_required,
        "system_recommended_action": recommendation.recommended_circular_action,
    }


def compare_blind_label(label: dict[str, Any]) -> dict[str, Any]:
    snapshot = system_snapshot_for_case(label["case_id"])
    return {
        **snapshot,
        "strategy_agreement": label["strategy_category"].strip().lower()
        == snapshot["system_strategy_category"].strip().lower(),
        "risk_agreement": label["risk_level"] == snapshot["system_risk_level"],
        "human_review_agreement": label["human_review_required"]
        == snapshot["system_human_review_required"],
    }


def summarise_blind_review_submissions(submissions: list[Any]) -> dict[str, Any]:
    total = len(submissions)

    def count(field: str) -> int:
        return sum(1 for submission in submissions if bool(getattr(submission, field)))

    strategy = count("strategy_agreement")
    risk = count("risk_agreement")
    review = count("human_review_agreement")
    full = sum(
        1
        for submission in submissions
        if submission.strategy_agreement
        and submission.risk_agreement
        and submission.human_review_agreement
    )

    pct = lambda value: round((value / total) * 100, 1) if total else 0.0

    return {
        "total_labels": total,
        "strategy_agreement_count": strategy,
        "strategy_agreement_pct": pct(strategy),
        "risk_agreement_count": risk,
        "risk_agreement_pct": pct(risk),
        "human_review_agreement_count": review,
        "human_review_agreement_pct": pct(review),
        "full_agreement_count": full,
        "full_agreement_pct": pct(full),
    }
