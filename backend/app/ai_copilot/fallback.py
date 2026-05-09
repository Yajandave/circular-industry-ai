"""Deterministic fallback summaries for the site-wide AI copilot."""

from __future__ import annotations

from typing import Any


def build_fallback_site_summary(context: dict[str, Any]) -> dict[str, Any]:
    scope = context["portfolio_scope"]
    risk = context["risk_breakdown"]
    top_opportunities = context["top_opportunities"]
    highest_risk = context["highest_risk_items"]
    evidence_gaps = context["evidence_gap_items"]
    supplier_items = context["supplier_procurement_items"]

    opportunity_lines = [
        f"{item['stream_id']} ({item['material']}): {item['recommended_circular_action']}"
        for item in top_opportunities[:5]
    ]

    risk_lines = [
        f"{item['stream_id']} ({item['material']}): {item['risk_level']} risk, rule {item['rule_applied']}"
        for item in highest_risk[:5]
    ]

    evidence_lines = [
        f"{item['stream_id']} needs stronger evidence: {item['missing_data']}"
        for item in evidence_gaps[:5]
    ]

    supplier_lines = [
        f"{item['stream_id']} supplier action: {item['supplier_procurement_action']}"
        for item in supplier_items[:5]
    ]

    next_actions = [
        "Review blocked and high-risk streams before any implementation claim is made.",
        "Close missing-data fields for low-evidence streams before using results externally.",
        "Prioritise supplier take-back and recycled-content questions for procurement-linked streams.",
        "Use estimated savings only as screening values until verified with measured site data.",
        "Prepare a human review pack for streams with hazardous, unknown or contamination-related triggers.",
    ]

    return {
        "generation_mode": "deterministic_fallback",
        "model_name": "none",
        "decision_lock_status": "Rules engine locked. AI copilot advisory only.",
        "executive_summary": (
            f"The system contains {scope['total_streams']} industrial streams and "
            f"{scope['total_recommendations']} generated recommendations. "
            f"{scope['human_review_required']} streams require human review. "
            f"Estimated annual diversion is {scope['total_estimated_annual_waste_diverted_kg']} kg and "
            f"estimated annual disposal cost avoided is {scope['total_estimated_annual_disposal_cost_avoided']}."
        ),
        "risk_summary": (
            f"Risk breakdown: {risk}. Blocked and high-risk streams should be treated as controlled-review items."
        ),
        "opportunity_summary": (
            "Top opportunity areas include: " + "; ".join(opportunity_lines)
            if opportunity_lines
            else "No circular opportunity summary is available until recommendations are generated."
        ),
        "evidence_gap_summary": (
            "Evidence gaps found: " + "; ".join(evidence_lines)
            if evidence_lines
            else "No major evidence gaps were detected from the current rules output."
        ),
        "supplier_procurement_summary": (
            "Supplier/procurement actions include: " + "; ".join(supplier_lines)
            if supplier_lines
            else "No supplier/procurement actions were identified from the current rules output."
        ),
        "human_review_priorities": risk_lines or ["No blocked or high-risk review priorities were found."],
        "recommended_next_actions": next_actions,
        "claim_safety_note": (
            "All diversion, cost and circularity values remain estimated screening outputs unless separately verified. "
            "The AI copilot must not convert estimates into validated environmental or financial claims."
        ),
        "governance_note": (
            "Rules decide. The AI copilot explains, summarises and drafts only. Risk level, review status, "
            "rule applied, recommendation route and claim boundaries remain locked."
        ),
        "validation_warnings": [],
    }
