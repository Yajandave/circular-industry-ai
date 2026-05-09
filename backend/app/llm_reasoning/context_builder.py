"""Build the controlled context package sent to the LLM.

The LLM never receives an open instruction such as "decide what to do". It gets
locked rules-engine, evidence-register and circular-resolution context, then is
asked only to write a structured reasoning narrative.
"""

from __future__ import annotations

from typing import Any


def compact_stream(stream: Any) -> dict[str, Any]:
    return {
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "material": stream.material,
        "source_process": stream.source_process,
        "monthly_quantity_kg": stream.monthly_quantity_kg,
        "current_route": stream.current_route,
        "disposal_cost_per_month": stream.disposal_cost_per_month,
        "contamination_risk": stream.contamination_risk,
        "hazardous_flag": stream.hazardous_flag,
        "department": stream.department,
        "supplier": stream.supplier,
        "supplier_takeback_available": stream.supplier_takeback_available,
        "recycled_content_available": stream.recycled_content_available,
        "notes": stream.notes,
    }


def compact_recommendation(recommendation: Any) -> dict[str, Any]:
    return {
        "recommended_circular_action": recommendation.recommended_circular_action,
        "circular_strategy_category": recommendation.circular_strategy_category,
        "reasoning": recommendation.reasoning,
        "risk_level": recommendation.risk_level,
        "confidence_score": recommendation.confidence_score,
        "evidence_quality_score": recommendation.evidence_quality_score,
        "missing_data": recommendation.missing_data,
        "human_review_required": recommendation.human_review_required,
        "estimated_annual_waste_diverted_kg": recommendation.estimated_annual_waste_diverted_kg,
        "estimated_annual_disposal_cost_avoided": recommendation.estimated_annual_disposal_cost_avoided,
        "supplier_procurement_action": recommendation.supplier_procurement_action,
        "industrial_symbiosis_opportunity": recommendation.industrial_symbiosis_opportunity,
        "next_action": recommendation.next_action,
        "dashboard_priority": recommendation.dashboard_priority,
        "rule_applied": recommendation.rule_applied,
    }


def build_llm_context(stream: Any, recommendation: Any, evidence: dict[str, Any], resolution: dict[str, Any]) -> dict[str, Any]:
    return {
        "stream": compact_stream(stream),
        "locked_recommendation": compact_recommendation(recommendation),
        "evidence_register_record": evidence,
        "circular_resolution_plan": resolution,
        "non_negotiable_controls": {
            "rules_decide": True,
            "llm_may_not_change_rule_applied": recommendation.rule_applied,
            "llm_may_not_change_risk_level": recommendation.risk_level,
            "llm_may_not_change_human_review_required": recommendation.human_review_required,
            "llm_may_not_make_verified_savings_claims": True,
            "llm_may_not_make_carbon_claims": True,
            "llm_may_not_confirm_supplier_compliance_or_legal_status": True,
        },
        "required_output_purpose": (
            "Write a stream-specific circular economy reasoning narrative for human review. "
            "Explain the locked recommendation, evidence gaps, supplier questions, pilot guidance and claim controls."
        ),
    }
