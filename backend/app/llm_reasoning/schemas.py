"""Internal JSON schema used for optional LLM structured outputs."""

from __future__ import annotations

AI_REASONING_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "string"},
        "circular_economy_reasoning": {"type": "string"},
        "evidence_gap_explanation": {"type": "string"},
        "supplier_questions": {"type": "array", "items": {"type": "string"}},
        "pilot_guidance": {"type": "string"},
        "claim_safety_note": {"type": "string"},
        "human_review_note": {"type": "string"},
        "implementation_risks": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "executive_summary",
        "circular_economy_reasoning",
        "evidence_gap_explanation",
        "supplier_questions",
        "pilot_guidance",
        "claim_safety_note",
        "human_review_note",
        "implementation_risks",
    ],
    "additionalProperties": False,
}
