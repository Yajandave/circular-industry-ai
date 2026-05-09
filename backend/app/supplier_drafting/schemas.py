"""Structured output schema for supplier evidence request drafts."""

from __future__ import annotations

SUPPLIER_EMAIL_DRAFT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "email_body": {"type": "string"},
        "evidence_request_summary": {"type": "array", "items": {"type": "string"}},
        "attachments_or_documents_to_request": {"type": "array", "items": {"type": "string"}},
        "internal_follow_up_actions": {"type": "array", "items": {"type": "string"}},
        "claim_safety_note": {"type": "string"},
    },
    "required": [
        "subject",
        "email_body",
        "evidence_request_summary",
        "attachments_or_documents_to_request",
        "internal_follow_up_actions",
        "claim_safety_note",
    ],
    "additionalProperties": False,
}
