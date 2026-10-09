"""Read-only feasibility screening; never authorises a route or invents partners.

A proposed circular route is an opportunity, NOT proven operational feasibility.
"""
from app.governance_maturity import has_material_evidence_gap

REQUIRED_CHECKS = (
    "material_specification_confirmed",
    "contamination_and_hazard_classification_confirmed",
    "receiving_facility_or_supplier_acceptance_confirmed",
    "logistics_and_storage_feasible",
    "cost_and_contract_terms_checked",
    "applicable_permissions_and_duty_of_care_checked",
)

def assess_feasibility(recommendation, evidence=None):
    evidence = evidence or {}
    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be a dictionary of explicit confirmations.")
    checks = {}
    for key in REQUIRED_CHECKS:
        value = evidence.get(key)
        # Only explicit Boolean True counts: strings like "yes" are not verification.
        checks[key] = "confirmed_by_operator" if value is True else "unconfirmed"
    controlled = (bool(recommendation.human_review_required)
                  or str(recommendation.risk_level).lower() in {"blocked", "high"}
                  or str(recommendation.rule_applied).upper() == "R999_DEFAULT_EVIDENCE_IMPROVEMENT")
    if controlled:
        state = "human_review_required"
    elif has_material_evidence_gap(recommendation):
        state = "needs_more_information"
    elif not all(value == "confirmed_by_operator" for value in checks.values()):
        state = "potential_opportunity"
    else:
        state = "feasibility_evidence_recorded_not_authorised"
    return {
        "state": state,
        "checks": checks,
        "required_checks": list(REQUIRED_CHECKS),
        "human_review_required": controlled,
        "route_authorised": False,
        "verified_operational_feasibility": False,
        "governance_note": "A user-supplied confirmation is not independent verification. This screening never grants legal approval, route authorisation, supplier acceptance or verified savings.",
    }
