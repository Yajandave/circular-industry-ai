"""Structured output schema for circular action reports."""

from __future__ import annotations

CIRCULAR_ACTION_REPORT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "report_title": {"type": "string"},
        "executive_summary": {"type": "string"},
        "risk_and_review_status": {"type": "string"},
        "evidence_position": {"type": "string"},
        "circular_resolution_summary": {"type": "string"},
        "supplier_loop_summary": {"type": "string"},
        "implementation_plan": {"type": "array", "items": {"type": "string"}},
        "evidence_to_collect": {"type": "array", "items": {"type": "string"}},
        "unsafe_claims_to_avoid": {"type": "array", "items": {"type": "string"}},
        "recommended_next_actions": {"type": "array", "items": {"type": "string"}},
        "claim_boundary": {"type": "string"},
    },
    "required": [
        "report_title",
        "executive_summary",
        "risk_and_review_status",
        "evidence_position",
        "circular_resolution_summary",
        "supplier_loop_summary",
        "implementation_plan",
        "evidence_to_collect",
        "unsafe_claims_to_avoid",
        "recommended_next_actions",
        "claim_boundary",
    ],
    "additionalProperties": False,
}
