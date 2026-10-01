"""Deterministic evidence-verification gate for observed scenario outcomes.

Milestone 20B.6 does not perform independent assurance. It evaluates whether
an observed outcome has enough internally reviewed, traceable evidence to
support a narrow internal factual statement while keeping external claims gated.
"""

from __future__ import annotations

from typing import Protocol


class ObservedOutcomeLike(Protocol):
    observed_recovered_quantity_kg: float
    observation_start_date: object
    observation_end_date: object
    evidence_source_type: str
    evidence_reference: str
    verification_status: str


DOCUMENTARY_SOURCE_TYPES = {
    "weighbridge_ticket",
    "supplier_confirmation",
    "invoice_or_credit",
    "system_export",
    "other_documentary",
}

BLOCKED_CLAIMS = [
    "verified diversion",
    "verified recycling or recovery rate",
    "causal impact attributable to the intervention",
    "carbon or greenhouse-gas savings",
    "financial savings or avoided cost",
    "legal compliance or waste-status verification",
]


def evaluate_observed_outcome_evidence(
    outcome: ObservedOutcomeLike,
    *,
    evidence_completeness: str,
    source_traceability_confirmed: bool,
    quantity_basis_confirmed: bool,
    period_basis_confirmed: bool,
    route_destination_confirmed: bool,
) -> dict:
    """Return a deterministic internal claim-readiness decision."""

    checks = {
        "evidence_completeness_complete": evidence_completeness == "complete",
        "source_traceability_confirmed": bool(source_traceability_confirmed),
        "quantity_basis_confirmed": bool(quantity_basis_confirmed),
        "period_basis_confirmed": bool(period_basis_confirmed),
        "documentary_source_present": outcome.evidence_source_type in DOCUMENTARY_SOURCE_TYPES,
        "outcome_internally_reviewed": outcome.verification_status == "internally_reviewed",
        "route_destination_confirmed": bool(route_destination_confirmed),
    }

    core_ready = all(
        checks[key]
        for key in (
            "evidence_completeness_complete",
            "source_traceability_confirmed",
            "quantity_basis_confirmed",
            "period_basis_confirmed",
            "documentary_source_present",
            "outcome_internally_reviewed",
        )
    )

    if not core_ready:
        decision = "evidence_insufficient_for_internal_claim"
        internal_claim_readiness = "not_ready"
        allowed_statement = None
    elif route_destination_confirmed:
        decision = "internally_supported_with_route_context"
        internal_claim_readiness = "internal_factual_reporting_ready"
        allowed_statement = (
            f"Internal evidence review supports recording "
            f"{float(outcome.observed_recovered_quantity_kg):g} kg as recovered during "
            f"{outcome.observation_start_date} to {outcome.observation_end_date}, "
            "with route or destination evidence confirmed."
        )
    else:
        decision = "internally_supported_observed_quantity"
        internal_claim_readiness = "internal_factual_reporting_ready"
        allowed_statement = (
            f"Internal evidence review supports recording "
            f"{float(outcome.observed_recovered_quantity_kg):g} kg as observed recovered quantity during "
            f"{outcome.observation_start_date} to {outcome.observation_end_date}. "
            "The destination or circular route is not confirmed by this review."
        )

    missing_checks = [key for key, passed in checks.items() if not passed and key != "route_destination_confirmed"]

    return {
        "verification_decision": decision,
        "internal_claim_readiness": internal_claim_readiness,
        "external_claim_readiness": "external_verification_required",
        "allowed_internal_statement": allowed_statement,
        "blocked_claims": BLOCKED_CLAIMS,
        "checks": checks,
        "missing_checks": missing_checks,
        "governance_note": (
            "This gate supports internal factual reporting only. It does not provide independent assurance "
            "or authorise external claims. External claim use requires a separate verification process, and "
            "this review does not establish causality, carbon savings, financial savings or legal compliance."
        ),
    }
