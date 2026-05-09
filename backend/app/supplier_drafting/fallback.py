"""Deterministic supplier evidence request email drafts."""

from __future__ import annotations

from typing import Any


def _list(value: Any) -> list[str]:
    return [str(item).strip() for item in value or [] if str(item).strip()]


def _supplier_name(stream: Any) -> str:
    supplier = str(getattr(stream, "supplier", "") or "").strip()
    if supplier.lower() in {"", "unknown", "various", "various suppliers", "n/a", "na"}:
        return "your team"
    return supplier


def _greeting(stream: Any) -> str:
    supplier = _supplier_name(stream)
    if supplier == "your team":
        return "Hello,"
    return f"Hello {supplier} team,"


def build_fallback_supplier_email_draft(
    stream: Any,
    recommendation: Any,
    supplier_plan: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    supplier = _supplier_name(stream)
    subject = f"Evidence request for circular procurement review: {stream.stream_id} {stream.stream_name}"

    supplier_questions = _list(supplier_plan.get("supplier_questions"))[:5]
    evidence_required = _list(supplier_plan.get("supplier_evidence_required"))[:6]
    acceptance_criteria = _list(supplier_plan.get("acceptance_criteria"))[:5]
    data_requests = _list(supplier_plan.get("data_requests"))[:5]
    contract_levers = _list(supplier_plan.get("contract_levers"))[:4]

    review_warning = ""
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        review_warning = (
            "\n\nPlease note that this is an evidence request only. We are not asking for a route change or "
            "making a circularity claim at this stage because the stream is subject to a controlled review gate."
        )

    question_block = "\n".join(f"- {question}" for question in supplier_questions) or "- Please confirm route feasibility, acceptance criteria and evidence requirements."
    evidence_block = "\n".join(f"- {item}" for item in evidence_required) or "- Route feasibility evidence and acceptance criteria."
    criteria_block = "\n".join(f"- {item}" for item in acceptance_criteria) or "- Confirm material acceptance conditions and rejection rules."

    email_body = (
        f"{_greeting(stream)}\n\n"
        "I am reviewing a material stream as part of an internal circular procurement and evidence-gathering exercise. "
        "The purpose is to understand whether a safe and evidence-supported supplier loop, take-back route, recycled-content option, "
        "specialist recovery route or process-improvement opportunity may be feasible.\n\n"
        f"Stream under review: {stream.stream_id} - {stream.stream_name}\n"
        f"Material: {stream.material}\n"
        f"Current screened procurement route: {supplier_plan.get('procurement_route')}\n"
        f"Locked rules-engine recommendation: {recommendation.recommended_circular_action}\n"
        f"Risk / review status: {recommendation.risk_level}; human review required = {recommendation.human_review_required}\n\n"
        "Could you please help confirm the following?\n"
        f"{question_block}\n\n"
        "Evidence or documentation requested:\n"
        f"{evidence_block}\n\n"
        "Acceptance / rejection criteria to clarify:\n"
        f"{criteria_block}\n"
        f"{review_warning}\n\n"
        "At this stage, all quantities, avoided costs and circularity benefits are being treated as screening estimates only. "
        "We will not present them as verified savings, verified diversion, carbon savings or supplier compliance claims unless "
        "the relevant evidence and internal review gates are completed.\n\n"
        "Kind regards,"
    )

    return {
        "generation_mode": "deterministic_fallback",
        "model_name": "none",
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "supplier": supplier,
        "decision_lock_status": "Rules engine locked. Supplier email draft advisory only.",
        "draft_type": "supplier evidence request",
        "subject": subject,
        "email_body": email_body,
        "evidence_request_summary": supplier_questions or evidence_required,
        "attachments_or_documents_to_request": evidence_required + data_requests,
        "internal_follow_up_actions": [
            f"Log supplier response against evidence register item: {evidence.get('review_gate')}.",
            "Do not update claim readiness until supplier evidence has been reviewed internally.",
            "Compare supplier acceptance criteria against contamination, segregation and storage controls.",
            "Escalate to EHS/compliance before any route change for high, blocked, hazardous or unknown streams.",
        ],
        "claim_safety_note": (
            "This draft must not state that diversion, cost savings, carbon savings, supplier compliance or circularity impact "
            "are verified. It is an evidence request only."
        ),
        "governance_note": (
            "AI drafts communication only. It does not verify supplier capability, legal compliance, route suitability, "
            "cost savings, diversion, carbon savings or claim readiness."
        ),
        "validation_warnings": [],
        "locked_rule_applied": recommendation.rule_applied,
        "locked_risk_level": recommendation.risk_level,
        "locked_human_review_required": recommendation.human_review_required,
        "locked_claim_readiness": evidence.get("claim_readiness"),
        "locked_procurement_route": supplier_plan.get("procurement_route"),
        "locked_review_gate": supplier_plan.get("review_gate"),
    }
