"""Deterministic circular action report fallback."""

from __future__ import annotations

from typing import Any


def _items(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text or text.lower() in {"none", "none recorded", "none identified for mvp fields"}:
        return []
    return [item.strip() for item in text.split(";") if item.strip()]


def _money(value: Any) -> str:
    try:
        return f"GBP {float(value):,.0f}"
    except Exception:
        return "GBP 0"


def build_fallback_circular_action_report(
    stream: Any,
    recommendation: Any,
    evidence: dict[str, Any],
    resolution: dict[str, Any],
    supplier_plan: dict[str, Any],
) -> dict[str, Any]:
    evidence_required = _items(resolution.get("evidence_required")) + _items(supplier_plan.get("supplier_evidence_required"))
    if not evidence_required:
        evidence_required = _items(evidence.get("missing_data"))

    unsafe_claims = [
        "Do not claim verified waste diversion until actual post-implementation weights are recorded.",
        "Do not claim verified cost savings until finance records or supplier invoices confirm avoided cost.",
        "Do not claim carbon savings without a separate carbon method, boundary and evidence trail.",
        "Do not claim supplier capability, legal compliance or route acceptance from the report alone.",
    ]

    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        unsafe_claims.append(
            "Do not present this stream as implementation-ready until the controlled review gate is closed."
        )

    implementation_plan = _items(resolution.get("implementation_steps"))
    if not implementation_plan:
        implementation_plan = [
            "Confirm material composition, contamination status and source-process ownership.",
            "Check supplier or contractor acceptance criteria.",
            "Run a controlled pilot only after review gates and evidence requirements are documented.",
            "Track actual quantity, cost and route evidence before making any impact claim.",
        ]

    next_actions = [
        evidence.get("next_action") or recommendation.next_action,
        supplier_plan.get("review_gate"),
        "Update the evidence register after supplier, contractor or operational evidence is received.",
        "Keep all outputs as internal screening until validation evidence is complete.",
    ]
    next_actions = [item for item in next_actions if item]

    return {
        "generation_mode": "deterministic_fallback",
        "model_name": "none",
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "decision_lock_status": "Rules engine locked. Circular action report advisory only.",
        "report_title": f"Circular Action Report: {stream.stream_id} - {stream.stream_name}",
        "executive_summary": (
            f"{stream.stream_name} has been screened under the locked rules engine with the recommendation "
            f"'{recommendation.recommended_circular_action}'. The stream is currently risk-rated '{recommendation.risk_level}' "
            f"with human review required = {recommendation.human_review_required}. Screened annual value at stake is "
            f"{_money(recommendation.estimated_annual_disposal_cost_avoided)} and screened diversion potential is "
            f"{recommendation.estimated_annual_waste_diverted_kg:,.0f} kg, but these are not verified outcomes."
        ),
        "locked_recommendation": recommendation.recommended_circular_action,
        "risk_and_review_status": (
            f"Rule applied: {recommendation.rule_applied}. Risk level: {recommendation.risk_level}. "
            f"Review gate: {evidence.get('review_gate')}. Human review required: {recommendation.human_review_required}."
        ),
        "evidence_position": (
            f"Evidence status: {evidence.get('evidence_status')}. Claim readiness: {evidence.get('claim_readiness')}. "
            f"Missing evidence: {evidence.get('missing_data')}."
        ),
        "circular_resolution_summary": (
            resolution.get("specific_resolution_idea")
            or resolution.get("circular_problem")
            or "Circular resolution plan should be confirmed after evidence gaps are closed."
        ),
        "supplier_loop_summary": (
            f"Procurement route: {supplier_plan.get('procurement_route')}. "
            f"Supplier relationship type: {supplier_plan.get('supplier_relationship_type')}. "
            f"Negotiation position: {supplier_plan.get('negotiation_position')}."
        ),
        "implementation_plan": implementation_plan,
        "evidence_to_collect": list(dict.fromkeys(evidence_required)),
        "unsafe_claims_to_avoid": unsafe_claims,
        "recommended_next_actions": next_actions,
        "claim_boundary": (
            supplier_plan.get("claim_boundary")
            or evidence.get("claim_boundary")
            or "Do not make external circularity claims until evidence is validated."
        ),
        "governance_note": (
            "This report is an internal decision-support output. It does not verify savings, diversion, carbon impact, "
            "supplier compliance, legal waste status or completed operational impact."
        ),
        "validation_warnings": [],
        "locked_rule_applied": recommendation.rule_applied,
        "locked_risk_level": recommendation.risk_level,
        "locked_human_review_required": recommendation.human_review_required,
        "locked_claim_readiness": evidence.get("claim_readiness"),
        "locked_review_gate": evidence.get("review_gate"),
        "locked_procurement_route": supplier_plan.get("procurement_route"),
    }
