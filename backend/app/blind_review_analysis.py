"""Transparent multi-reviewer agreement analysis for blind decision reviews.

The analysis avoids treating any reviewer as ground truth. It summarises
reviewer distributions, leading consensus, unanimity and pairwise agreement,
then compares the stored system snapshot with the reviewer consensus where a
leading label exists.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Any


def _reviewer_key(record: Any) -> tuple[str, str, str]:
    return (
        str(record.reviewer_name).strip().lower(),
        str(record.reviewer_role).strip().lower(),
        str(record.reviewer_organisation or "").strip().lower(),
    )


def latest_review_per_reviewer_case(records: list[Any]) -> list[Any]:
    """Use the latest stored record for each self-identified reviewer/case pair."""
    latest: dict[tuple[tuple[str, str, str], str], Any] = {}
    ordered = sorted(
        records,
        key=lambda item: (item.created_at, item.id),
        reverse=True,
    )
    for record in ordered:
        key = (_reviewer_key(record), record.case_id)
        if key not in latest:
            latest[key] = record
    return list(latest.values())


def _dimension_consensus(values: list[Any]) -> dict[str, Any]:
    total = len(values)
    if not total:
        return {
            "reviewer_count": 0,
            "distribution": {},
            "leading_label": None,
            "leading_count": 0,
            "leading_share_pct": 0.0,
            "unanimous": False,
            "pairwise_agreement_pct": None,
            "consensus_status": "no_reviews",
        }

    normalised = [str(value).lower() if isinstance(value, bool) else str(value) for value in values]
    counts = Counter(normalised)
    ranked = counts.most_common()
    leading_label, leading_count = ranked[0]
    tied_for_lead = len(ranked) > 1 and ranked[1][1] == leading_count
    leading_share = round((leading_count / total) * 100, 1)

    pairs = list(combinations(normalised, 2))
    if pairs:
        matching_pairs = sum(1 for left, right in pairs if left == right)
        pairwise_pct = round((matching_pairs / len(pairs)) * 100, 1)
    else:
        pairwise_pct = None

    if total == 1:
        status = "single_reviewer_only"
    elif tied_for_lead:
        status = "split"
    elif leading_count == total:
        status = "unanimous"
    elif leading_share >= 66.7:
        status = "strong_majority"
    elif leading_share > 50:
        status = "simple_majority"
    else:
        status = "mixed"

    return {
        "reviewer_count": total,
        "distribution": dict(sorted(counts.items())),
        "leading_label": None if tied_for_lead else leading_label,
        "leading_count": leading_count,
        "leading_share_pct": leading_share,
        "unanimous": leading_count == total and total > 1,
        "pairwise_agreement_pct": pairwise_pct,
        "consensus_status": status,
    }


def _system_matches(consensus: dict[str, Any], system_value: Any) -> bool | None:
    leading = consensus["leading_label"]
    if leading is None:
        return None
    normalised_system = str(system_value).lower() if isinstance(system_value, bool) else str(system_value)
    return normalised_system == leading


def build_multi_reviewer_analysis(records: list[Any]) -> dict[str, Any]:
    deduplicated = latest_review_per_reviewer_case(records)
    by_case: dict[str, list[Any]] = defaultdict(list)
    for record in deduplicated:
        by_case[record.case_id].append(record)

    case_results: list[dict[str, Any]] = []
    all_strategy_pairs: list[bool] = []
    all_risk_pairs: list[bool] = []
    all_review_pairs: list[bool] = []

    for case_id in sorted(by_case):
        case_records = sorted(by_case[case_id], key=lambda item: (item.created_at, item.id))
        strategy = _dimension_consensus([item.reviewer_strategy_category for item in case_records])
        risk = _dimension_consensus([item.reviewer_risk_level for item in case_records])
        human_review = _dimension_consensus([item.reviewer_human_review_required for item in case_records])

        for left, right in combinations(case_records, 2):
            all_strategy_pairs.append(
                left.reviewer_strategy_category.strip().lower()
                == right.reviewer_strategy_category.strip().lower()
            )
            all_risk_pairs.append(left.reviewer_risk_level == right.reviewer_risk_level)
            all_review_pairs.append(
                left.reviewer_human_review_required == right.reviewer_human_review_required
            )

        system = case_records[-1]
        snapshot_counts = Counter(
            (
                item.system_rule_applied,
                item.system_strategy_category,
                item.system_risk_level,
                item.system_human_review_required,
                item.system_recommended_action,
            )
            for item in case_records
        )
        system_snapshots = [
            {
                "rule_applied": snapshot[0],
                "strategy_category": snapshot[1],
                "risk_level": snapshot[2],
                "human_review_required": snapshot[3],
                "recommended_action": snapshot[4],
                "submission_count": count,
            }
            for snapshot, count in snapshot_counts.items()
        ]

        case_results.append(
            {
                "case_id": case_id,
                "reviewer_count": len(case_records),
                "strategy_consensus": strategy,
                "risk_consensus": risk,
                "human_review_consensus": human_review,
                "system_snapshot_consistent": len(system_snapshots) == 1,
                "system_snapshot_count": len(system_snapshots),
                "system_snapshots": system_snapshots,
                "latest_system_snapshot": {
                    "rule_applied": system.system_rule_applied,
                    "strategy_category": system.system_strategy_category,
                    "risk_level": system.system_risk_level,
                    "human_review_required": system.system_human_review_required,
                    "recommended_action": system.system_recommended_action,
                },
                "system_matches_strategy_consensus": _system_matches(
                    strategy, system.system_strategy_category
                ),
                "system_matches_risk_consensus": _system_matches(
                    risk, system.system_risk_level
                ),
                "system_matches_human_review_consensus": _system_matches(
                    human_review, system.system_human_review_required
                ),
                "reviewer_reasoning": [
                    {
                        "reviewer_name": item.reviewer_name,
                        "reviewer_role": item.reviewer_role,
                        "reviewer_organisation": item.reviewer_organisation,
                        "confidence": item.reviewer_confidence,
                        "reasoning": item.reviewer_reasoning,
                    }
                    for item in case_records
                ],
            }
        )

    def aggregate_pairwise(values: list[bool]) -> float | None:
        if not values:
            return None
        return round((sum(1 for value in values if value) / len(values)) * 100, 1)

    reviewer_keys = {_reviewer_key(record) for record in deduplicated}
    cases_with_multiple = sum(1 for item in case_results if item["reviewer_count"] >= 2)

    system_consensus_eligible = [
        item
        for item in case_results
        if item["reviewer_count"] >= 2
    ]

    def consensus_match_summary(field: str) -> dict[str, Any]:
        eligible = [item[field] for item in system_consensus_eligible if item[field] is not None]
        matched = sum(1 for value in eligible if value)
        return {
            "matched": matched,
            "eligible": len(eligible),
            "match_pct": round((matched / len(eligible)) * 100, 1) if eligible else None,
        }

    return {
        "unique_reviewers": len(reviewer_keys),
        "unique_cases_reviewed": len(case_results),
        "cases_with_multiple_reviewers": cases_with_multiple,
        "deduplicated_submission_count": len(deduplicated),
        "overall_pairwise_agreement": {
            "strategy_pct": aggregate_pairwise(all_strategy_pairs),
            "risk_pct": aggregate_pairwise(all_risk_pairs),
            "human_review_pct": aggregate_pairwise(all_review_pairs),
        },
        "system_consensus_match": {
            "strategy": consensus_match_summary("system_matches_strategy_consensus"),
            "risk": consensus_match_summary("system_matches_risk_consensus"),
            "human_review": consensus_match_summary("system_matches_human_review_consensus"),
        },
        "cases": case_results,
        "governance_note": (
            "Reviewer consensus is not treated as ground truth. Pairwise agreement measures how often reviewer "
            "pairs chose the same label on the same case. System-versus-consensus comparisons use the latest stored "
            "system snapshot and are reported only where a non-tied leading reviewer label exists. Cases also disclose "
            "whether system snapshots changed across reviewer submissions. Interpretation should retain disagreements, "
            "reviewer reasoning, model-version effects and sample-size limitations."
        ),
    }
