"""Build site-wide AI copilot context from locked Circular Industry AI outputs."""

from __future__ import annotations

from collections import Counter
from typing import Any


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def build_site_copilot_context(streams: list[Any], recommendations: list[Any]) -> dict[str, Any]:
    """Create a compact, rules-locked context for site-wide AI summarisation.

    This context is advisory input for the LLM. The LLM must not change risk,
    review status, rule applied, claim boundary or recommendation outputs.
    """
    stream_by_id = {stream.stream_id: stream for stream in streams}
    recs = list(recommendations)

    risk_breakdown = Counter(_safe_text(rec.risk_level).lower() for rec in recs)
    strategy_breakdown = Counter(_safe_text(rec.circular_strategy_category) for rec in recs)
    material_breakdown = Counter(_safe_text(stream.material) for stream in streams)
    department_breakdown = Counter(_safe_text(stream.department) for stream in streams)

    human_review_items = [
        {
            "stream_id": rec.stream_id,
            "stream_name": getattr(stream_by_id.get(rec.stream_id), "stream_name", ""),
            "material": getattr(stream_by_id.get(rec.stream_id), "material", ""),
            "risk_level": rec.risk_level,
            "rule_applied": rec.rule_applied,
            "missing_data": rec.missing_data,
            "next_action": rec.next_action,
        }
        for rec in recs
        if rec.human_review_required
    ]

    highest_risk_items = sorted(
        [
            {
                "stream_id": rec.stream_id,
                "stream_name": getattr(stream_by_id.get(rec.stream_id), "stream_name", ""),
                "material": getattr(stream_by_id.get(rec.stream_id), "material", ""),
                "department": getattr(stream_by_id.get(rec.stream_id), "department", ""),
                "risk_level": rec.risk_level,
                "human_review_required": rec.human_review_required,
                "rule_applied": rec.rule_applied,
                "recommended_circular_action": rec.recommended_circular_action,
                "missing_data": rec.missing_data,
                "next_action": rec.next_action,
            }
            for rec in recs
            if _safe_text(rec.risk_level).lower() in {"high", "blocked"}
        ],
        key=lambda item: (item["risk_level"] != "blocked", item["stream_id"]),
    )[:10]

    top_opportunities = sorted(
        [
            {
                "stream_id": rec.stream_id,
                "stream_name": getattr(stream_by_id.get(rec.stream_id), "stream_name", ""),
                "material": getattr(stream_by_id.get(rec.stream_id), "material", ""),
                "strategy": rec.circular_strategy_category,
                "recommended_circular_action": rec.recommended_circular_action,
                "estimated_annual_waste_diverted_kg": rec.estimated_annual_waste_diverted_kg,
                "estimated_annual_disposal_cost_avoided": rec.estimated_annual_disposal_cost_avoided,
                "confidence_score": rec.confidence_score,
                "evidence_quality_score": rec.evidence_quality_score,
            }
            for rec in recs
        ],
        key=lambda item: (
            item["estimated_annual_disposal_cost_avoided"],
            item["estimated_annual_waste_diverted_kg"],
        ),
        reverse=True,
    )[:10]

    evidence_gap_items = [
        {
            "stream_id": rec.stream_id,
            "stream_name": getattr(stream_by_id.get(rec.stream_id), "stream_name", ""),
            "material": getattr(stream_by_id.get(rec.stream_id), "material", ""),
            "evidence_quality_score": rec.evidence_quality_score,
            "missing_data": rec.missing_data,
            "claim_boundary": "No verified impact claim should be made until evidence gaps are closed.",
        }
        for rec in recs
        if rec.evidence_quality_score < 70
        or _safe_text(rec.missing_data).lower() not in {"", "none", "n/a"}
    ][:15]

    supplier_items = [
        {
            "stream_id": rec.stream_id,
            "stream_name": getattr(stream_by_id.get(rec.stream_id), "stream_name", ""),
            "supplier": getattr(stream_by_id.get(rec.stream_id), "supplier", ""),
            "supplier_takeback_available": getattr(stream_by_id.get(rec.stream_id), "supplier_takeback_available", ""),
            "recycled_content_available": getattr(stream_by_id.get(rec.stream_id), "recycled_content_available", ""),
            "supplier_procurement_action": rec.supplier_procurement_action,
        }
        for rec in recs
        if _safe_text(rec.supplier_procurement_action)
    ][:15]

    return {
        "system_name": "Circular Industry AI",
        "decision_source": "Locked deterministic rules engine",
        "ai_role": "Advisory copilot for explanation, summarisation, evidence review and drafting only",
        "non_override_rules": [
            "Do not change risk level.",
            "Do not change human review status.",
            "Do not change rule applied.",
            "Do not change recommended circular action.",
            "Do not invent verified diversion, cost saving, carbon saving, legal compliance or supplier capability.",
            "Do not present estimated impacts as verified claims.",
        ],
        "portfolio_scope": {
            "total_streams": len(streams),
            "total_recommendations": len(recs),
            "total_estimated_annual_waste_diverted_kg": round(
                sum(rec.estimated_annual_waste_diverted_kg for rec in recs), 2
            ),
            "total_estimated_annual_disposal_cost_avoided": round(
                sum(rec.estimated_annual_disposal_cost_avoided for rec in recs), 2
            ),
            "human_review_required": sum(1 for rec in recs if rec.human_review_required),
        },
        "risk_breakdown": dict(risk_breakdown),
        "strategy_breakdown": dict(strategy_breakdown),
        "material_breakdown": dict(material_breakdown),
        "department_breakdown": dict(department_breakdown),
        "highest_risk_items": highest_risk_items,
        "top_opportunities": top_opportunities,
        "evidence_gap_items": evidence_gap_items,
        "supplier_procurement_items": supplier_items,
        "human_review_items": human_review_items[:15],
        "required_output_style": (
            "Write as a practical site-wide dashboard briefing for a sustainability, "
            "ESG, procurement or circular economy analyst. Be specific, cautious and action-focused."
        ),
    }
