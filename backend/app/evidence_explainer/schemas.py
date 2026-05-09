"""Structured output schema for the AI evidence gap explainer."""

from __future__ import annotations

EVIDENCE_GAP_EXPLANATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "evidence_gap_summary": {"type": "string"},
        "claim_readiness_explanation": {"type": "string"},
        "evidence_to_collect": {"type": "array", "items": {"type": "string"}},
        "supplier_documents_required": {"type": "array", "items": {"type": "string"}},
        "process_checks_required": {"type": "array", "items": {"type": "string"}},
        "safe_current_statement": {"type": "string"},
        "unsafe_claims_to_avoid": {"type": "array", "items": {"type": "string"}},
        "recommended_review_gate": {"type": "string"},
    },
    "required": [
        "evidence_gap_summary",
        "claim_readiness_explanation",
        "evidence_to_collect",
        "supplier_documents_required",
        "process_checks_required",
        "safe_current_statement",
        "unsafe_claims_to_avoid",
        "recommended_review_gate",
    ],
    "additionalProperties": False,
}
