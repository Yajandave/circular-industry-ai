"""Human-review competence routing for screening recommendations.

The alpha has no authenticated role/approval system. This module therefore
states what competence should review a case and keeps human disagreement
separate from automatic mutation of the locked recommendation.
"""

from __future__ import annotations


def _clean(value: object) -> str:
    return str(value or "").strip().lower()


def build_review_governance(stream, recommendation) -> dict:
    material = _clean(stream.material)
    text = " ".join([
        _clean(stream.stream_name),
        material,
        _clean(stream.source_process),
        _clean(stream.notes),
    ])
    rule = recommendation.rule_applied
    risk = _clean(recommendation.risk_level)

    primary = ["circular economy / resource-efficiency practitioner"]
    supporting: list[str] = []
    rationale: list[str] = []

    if rule == "R001_HAZARDOUS_OR_UNKNOWN_REVIEW" or risk in {"high", "blocked"}:
        primary = ["competent waste classification / environmental compliance reviewer"]
        rationale.append("Safety, hazardous status or classification uncertainty is controlling the decision.")
        if "battery" in text or "lithium" in text:
            supporting.append("battery safety / site EHS competence")
        if material == "electronic components" or "weee" in text or "electronic" in text:
            supporting.append("WEEE classification competence")
        if "packaging" in text and any(term in text for term in ["solvent", "chemical", "hazardous", "residue"]):
            supporting.append("hazardous packaging / waste classification competence")
    elif rule == "R002_HIGH_CONTAMINATION_REVIEW":
        primary = ["waste classification / specialist recovery reviewer"]
        rationale.append("High contamination needs classification and route-acceptance evidence.")
    elif rule == "R004_SUPPLIER_TAKEBACK_AVAILABLE":
        primary = ["sustainable procurement / supplier-management reviewer"]
        supporting.append("site operations / logistics reviewer")
        rationale.append("The route depends on supplier capability, contract terms and reverse-logistics feasibility.")
    elif rule == "R003_REDUCE_AT_SOURCE":
        primary = ["process owner / resource-efficiency reviewer"]
        if "food" in text or "edible" in text or material == "organic/process residue":
            supporting.append("food safety / surplus-management competence where edible material is involved")
        rationale.append("Prevention depends on process cause, operating constraints and post-change measurement.")
    elif rule in {"R005_METAL_CLOSED_LOOP", "R007_MIXED_PLASTIC_RECYCLING", "R008_PLASTIC_CLOSED_LOOP", "R010_SPECIALIST_RECOVERY"}:
        primary = ["materials / waste-resource specialist"]
        supporting.append("recycler or route-acceptance evidence owner")
        rationale.append("Material specification, contamination and receiving-route evidence determine feasibility.")
    elif rule == "R009_SYMBIOSIS_OR_RESOURCE_RECOVERY":
        primary = ["resource-efficiency / industrial-symbiosis reviewer"]
        supporting.append("environmental compliance reviewer where by-product or waste status is material")
        rationale.append("Recipient use, quality consistency and legal status can change the viability of the opportunity.")
    elif rule == "R999_DEFAULT_EVIDENCE_IMPROVEMENT":
        primary = ["site data owner / sustainability reviewer"]
        rationale.append("The current record is too weak to support a higher-value route.")

    if recommendation.human_review_required or risk in {"high", "blocked"}:
        gate_status = "competent_human_review_required"
        second_review = True
        minimum_expectation = (
            "A competent reviewer must resolve the controlling risk/classification issue and document the evidence checked "
            "before a route change is treated as approved."
        )
    elif risk == "medium":
        gate_status = "evidence_review_recommended"
        second_review = False
        minimum_expectation = (
            "An appropriate operational or domain reviewer should confirm the evidence and feasibility assumptions before implementation."
        )
    else:
        gate_status = "rules_cleared_for_validation"
        second_review = False
        minimum_expectation = (
            "The rule is cleared for validation planning only. Operational feasibility and claim evidence still need confirmation."
        )

    return {
        "gate_status": gate_status,
        "primary_reviewer_competence": primary,
        "supporting_reviewer_competence": supporting,
        "second_review_recommended": second_review,
        "minimum_review_expectation": minimum_expectation,
        "rationale": rationale,
        "override_policy": (
            "Human disagreement may be recorded as a decision challenge. The alpha does not silently overwrite or mutate "
            "the locked rules-engine recommendation; any future override authority requires authenticated roles and approval controls."
        ),
        "governance_note": (
            "Reviewer competence labels are routing guidance for the alpha, not certification of any individual reviewer."
        ),
    }
