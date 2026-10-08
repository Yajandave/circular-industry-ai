"""Evidence register generation for Circular Industry AI.

Milestone 7 turns recommendation outputs into an auditable evidence trail. The
register is derived from the locked rules-engine recommendation plus the
controlled agentic evidence audit. It does not create new decisions or override
risk controls.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from app import models
from app.agentic.orchestrator import evidence_audit, risk_reviewer
from app.governance_maturity import SCORE_SEMANTICS, decision_support_band, evidence_maturity


def _join_items(items: list[str]) -> str:
    """Return a stable semi-colon separated cell value for CSV/API display."""
    return "; ".join(item for item in items if item) if items else "none recorded"


def _evidence_status(recommendation: models.CircularRecommendation) -> str:
    """Return a readable evidence state without treating a heuristic as assurance."""
    maturity = evidence_maturity(recommendation)
    return {
        "controlled_review_required": "controlled review required",
        "insufficient_for_route_change": "insufficient for route change",
        "screening_ready_with_checks": "screening-ready with checks",
        "screening_ready": "screening-ready",
    }[maturity]


def _claim_readiness(recommendation: models.CircularRecommendation) -> str:
    """Return a conservative claim boundary from explicit governance conditions."""
    maturity = evidence_maturity(recommendation)
    if maturity == "controlled_review_required":
        return "not claim-ready: review gate unresolved"
    if maturity == "insufficient_for_route_change":
        return "not claim-ready: decision basis insufficient"
    if maturity == "screening_ready_with_checks":
        return "internal screening only: evidence checks remain"
    return "internal screening only: validate before claims"


def _review_gate(recommendation: models.CircularRecommendation) -> str:
    maturity = evidence_maturity(recommendation)
    if maturity == "controlled_review_required":
        return "human review required before circular route selection"
    if maturity == "insufficient_for_route_change":
        return "evidence improvement required before route change"
    if maturity == "screening_ready_with_checks":
        return "evidence checks recommended before implementation"
    return "rules-cleared for validation"


def build_evidence_record(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Build one evidence register record for a stream recommendation."""
    audit = evidence_audit(stream, recommendation)
    risk = risk_reviewer(stream, recommendation)

    evidence_status = _evidence_status(recommendation)

    return {
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "material": stream.material,
        "department": stream.department,
        "supplier": stream.supplier,
        "recommended_circular_action": recommendation.recommended_circular_action,
        "circular_strategy_category": recommendation.circular_strategy_category,
        "rule_applied": recommendation.rule_applied,
        "risk_level": recommendation.risk_level,
        "human_review_required": recommendation.human_review_required,
        "confidence_score": recommendation.confidence_score,
        "evidence_quality_score": recommendation.evidence_quality_score,
        "evidence_maturity": evidence_maturity(recommendation),
        "decision_support_band": decision_support_band(recommendation),
        "score_semantics": SCORE_SEMANTICS,
        "evidence_status": evidence_status,
        "review_gate": _review_gate(recommendation),
        "claim_readiness": _claim_readiness(recommendation),
        "measured_data": _join_items(audit.get("measured_data", [])),
        "estimated_data": _join_items(audit.get("estimated_data", [])),
        "assumptions": _join_items(audit.get("assumptions", [])),
        "missing_data": _join_items(audit.get("missing_data", [])),
        "risk_triggers": _join_items(risk.get("risk_triggers", [])),
        "review_gates": _join_items(risk.get("review_gates", [])),
        "claim_boundary": audit.get("claim_boundary", "screening only"),
        "next_action": recommendation.next_action,
        "estimated_annual_waste_diverted_kg": recommendation.estimated_annual_waste_diverted_kg,
        "estimated_annual_disposal_cost_avoided": recommendation.estimated_annual_disposal_cost_avoided,
    }


def build_evidence_register(
    streams: list[models.IndustrialStream],
    recommendations: list[models.CircularRecommendation],
) -> list[dict[str, Any]]:
    """Build an evidence register by joining streams to recommendations."""
    stream_lookup = {stream.stream_id: stream for stream in streams}
    records: list[dict[str, Any]] = []

    for recommendation in sorted(recommendations, key=lambda rec: rec.stream_id):
        stream = stream_lookup.get(recommendation.stream_id)
        if not stream:
            continue
        records.append(build_evidence_record(stream, recommendation))

    return records


def build_evidence_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return summary metrics for the evidence register."""
    statuses = Counter(record["evidence_status"] for record in records)
    maturity = Counter(record["evidence_maturity"] for record in records)
    support = Counter(record["decision_support_band"] for record in records)
    claim_readiness = Counter(record["claim_readiness"] for record in records)
    review_required = sum(1 for record in records if record["human_review_required"])
    low_evidence = sum(
        1
        for record in records
        if record["evidence_maturity"] in {"insufficient_for_route_change", "controlled_review_required"}
    )
    strong_evidence = sum(1 for record in records if record["evidence_maturity"] == "screening_ready")
    missing_data_records = sum(
        1
        for record in records
        if record["missing_data"] not in {"none recorded", "none identified for MVP fields"}
    )

    return {
        "total_records": len(records),
        "human_review_required": review_required,
        "low_evidence_records": low_evidence,
        "strong_evidence_records": strong_evidence,
        "records_with_missing_data": missing_data_records,
        "evidence_status_breakdown": dict(statuses),
        "evidence_maturity_breakdown": dict(maturity),
        "decision_support_breakdown": dict(support),
        "claim_readiness_breakdown": dict(claim_readiness),
        "score_semantics": SCORE_SEMANTICS,
        "governance_note": (
            "Evidence register outputs are for internal screening and audit preparation. "
            "They do not verify legal waste status, supplier compliance, carbon savings or completed operational impact."
        ),
    }
