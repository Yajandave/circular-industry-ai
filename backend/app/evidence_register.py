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


def _join_items(items: list[str]) -> str:
    """Return a stable semi-colon separated cell value for CSV/API display."""
    return "; ".join(item for item in items if item) if items else "none recorded"


def _evidence_status(score: int, human_review_required: bool, risk_level: str) -> str:
    """Classify evidence maturity in a recruiter-readable way."""
    if human_review_required or risk_level in {"high", "blocked"}:
        return "controlled review required"
    if score >= 85:
        return "strong evidence"
    if score >= 70:
        return "usable evidence with checks"
    return "evidence improvement required"


def _claim_readiness(score: int, human_review_required: bool, risk_level: str) -> str:
    """Decide whether a recommendation can support external claims."""
    if human_review_required or risk_level in {"high", "blocked"}:
        return "not claim-ready: review gate unresolved"
    if score < 70:
        return "not claim-ready: evidence gaps remain"
    return "internal screening only: validate before claims"


def _review_gate(recommendation: models.CircularRecommendation) -> str:
    if recommendation.human_review_required:
        return "human review required before circular route selection"
    if recommendation.risk_level == "medium":
        return "evidence check recommended before implementation"
    if recommendation.evidence_quality_score < 70:
        return "data improvement recommended before implementation"
    return "rules-cleared for validation"


def build_evidence_record(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
) -> dict[str, Any]:
    """Build one evidence register record for a stream recommendation."""
    audit = evidence_audit(stream, recommendation)
    risk = risk_reviewer(stream, recommendation)

    evidence_status = _evidence_status(
        recommendation.evidence_quality_score,
        recommendation.human_review_required,
        recommendation.risk_level,
    )

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
        "evidence_status": evidence_status,
        "review_gate": _review_gate(recommendation),
        "claim_readiness": _claim_readiness(
            recommendation.evidence_quality_score,
            recommendation.human_review_required,
            recommendation.risk_level,
        ),
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
    claim_readiness = Counter(record["claim_readiness"] for record in records)
    review_required = sum(1 for record in records if record["human_review_required"])
    low_evidence = sum(1 for record in records if record["evidence_quality_score"] < 70)
    strong_evidence = sum(1 for record in records if record["evidence_quality_score"] >= 85)
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
        "claim_readiness_breakdown": dict(claim_readiness),
        "governance_note": (
            "Evidence register outputs are for internal screening and audit preparation. "
            "They do not verify legal waste status, supplier compliance, carbon savings or completed operational impact."
        ),
    }
