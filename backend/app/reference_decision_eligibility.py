"""Explicit eligibility assessment before using a reference classification with legacy rules.

Lookup output is reference evidence, not permission to invoke a route rule.
Existing legacy workflows remain unchanged.
"""
from __future__ import annotations

def evaluate_reference_decision_eligibility(reference: dict, *, verified_monthly_stream: bool = False,
                                            verified_material_family: str | None = None,
                                            hazardous_status_verified: bool = False,
                                            contamination_verified: bool = False) -> dict:
    missing = []
    if reference.get("status") != "found":
        missing.append("recognised_reference_code")
    if not verified_monthly_stream:
        missing.append("verified_monthly_factory_stream_quantity")
    if not verified_material_family:
        missing.append("operator_verified_material_family")
    if not hazardous_status_verified:
        missing.append("verified_hazardous_status")
    if not contamination_verified:
        missing.append("verified_contamination_assessment")
    return {
        "eligible_for_legacy_rule_screening": not missing,
        "missing_evidence": missing,
        "proposed_material_family": verified_material_family if not missing else None,
        "reference_only": True,
        "reason": "A reported waste code alone never authorises a technical route recommendation.",
    }
