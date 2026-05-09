"""Deterministic fallback for the AI evidence gap explainer."""

from __future__ import annotations

from typing import Any


def _split_items(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text or text.lower() in {"none", "none recorded", "none identified for mvp fields"}:
        return []
    return [item.strip() for item in text.split(";") if item.strip()]


def _contains(text: str, *needles: str) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def build_fallback_evidence_gap_explanation(stream: Any, recommendation: Any, evidence: dict[str, Any]) -> dict[str, Any]:
    missing_items = _split_items(evidence.get("missing_data") or recommendation.missing_data)
    risk_level = str(recommendation.risk_level or "").lower()
    claim_readiness = evidence.get("claim_readiness", "internal screening only")
    review_gate = evidence.get("review_gate", recommendation.next_action)

    evidence_to_collect: list[str] = []
    supplier_documents: list[str] = []
    process_checks: list[str] = []
    missing_text = "; ".join(missing_items).lower()

    if not missing_items:
        evidence_to_collect.append("Confirm measured operational data for quantity, current route, material quality and implementation outcome.")

    for item in missing_items:
        evidence_to_collect.append(f"Close missing evidence item: {item}.")

    if risk_level in {"high", "blocked"} or recommendation.human_review_required:
        evidence_to_collect.extend([
            "Confirm hazardous classification and applicable handling requirements with a competent person.",
            "Document the current legal disposal or recovery route before changing the circular route.",
        ])
        process_checks.append("Complete a formal human review gate before reuse, recycling, supplier return or symbiosis is implemented.")

    if _contains(missing_text, "contamination", "hazard", "composition", "polymer", "grade"):
        evidence_to_collect.append("Obtain material composition, grade, contamination profile and acceptance criteria from a qualified processor.")
        process_checks.append("Check whether segregation, storage and contamination controls are strong enough for the proposed route.")

    if _contains(missing_text, "supplier", "take-back", "takeback", "recycled", "procurement"):
        supplier_documents.extend([
            "Supplier take-back confirmation including acceptance criteria, volume limits and collection frequency.",
            "Supplier statement or certificate for recycled-content availability, where relevant.",
            "Written evidence of responsibilities, documentation requirements and rejected-material rules.",
        ])

    if not supplier_documents:
        supplier_documents.append("Supplier or contractor confirmation of route feasibility, acceptance criteria and documentation requirements.")

    if not process_checks:
        process_checks.extend([
            "Check source segregation, storage method and operational ownership before implementation.",
            "Define how actual diverted quantity and avoided disposal cost will be measured after implementation.",
        ])

    unsafe_claims = [
        "Do not claim verified waste diversion until actual post-implementation weights are recorded.",
        "Do not claim verified cost savings until disposal invoices or finance records confirm avoided cost.",
        "Do not claim carbon savings unless a separate carbon method and evidence trail have been completed.",
        "Do not claim legal compliance, hazardous status or supplier capability from the AI explanation alone.",
    ]
    if risk_level in {"high", "blocked"}:
        unsafe_claims.append("Do not present this stream as circular-route ready until the review gate and legal handling checks are complete.")

    return {
        "generation_mode": "deterministic_fallback",
        "model_name": "none",
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "decision_lock_status": "Rules engine locked. Evidence explainer advisory only.",
        "evidence_gap_summary": f"{stream.stream_id} is currently classified as '{evidence.get('evidence_status')}'. The main evidence issue is: {evidence.get('missing_data')}.",
        "claim_readiness_explanation": f"Claim readiness is '{claim_readiness}'. The screened diversion and cost values remain estimates, not verified claims, until the missing evidence and review gate are resolved.",
        "evidence_to_collect": evidence_to_collect,
        "supplier_documents_required": supplier_documents,
        "process_checks_required": process_checks,
        "safe_current_statement": f"Safe current statement: {stream.stream_name} has been screened as a potential circular economy opportunity under rule {recommendation.rule_applied}, but it is not a verified impact claim.",
        "unsafe_claims_to_avoid": unsafe_claims,
        "recommended_review_gate": review_gate,
        "governance_note": "This explainer supports evidence planning only. It does not verify legal waste status, supplier compliance, carbon savings, completed diversion or financial savings.",
        "validation_warnings": [],
        "locked_rule_applied": recommendation.rule_applied,
        "locked_risk_level": recommendation.risk_level,
        "locked_human_review_required": recommendation.human_review_required,
        "locked_claim_readiness": evidence.get("claim_readiness"),
        "locked_review_gate": evidence.get("review_gate"),
    }


