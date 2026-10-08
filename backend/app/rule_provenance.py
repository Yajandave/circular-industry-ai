"""Rule provenance catalogue for the deterministic circular-economy engine.

This catalogue distinguishes authoritative public guidance used to inform
safety/hierarchy boundaries from internal product judgement used to translate
those boundaries into screening rules. A source-linked rule is not legal advice,
regulatory approval or proof that the recommended route is feasible.
"""

from __future__ import annotations

from app.grounded_decision_validation import GROUNDING_SOURCES


GOVERNANCE_VERSION = "ruleset-governance-2026-10-08"
LAST_REVIEWED_DATE = "2026-10-08"


_RULES: dict[str, dict] = {
    "R001_HAZARDOUS_OR_UNKNOWN_REVIEW": {
        "rule_family": "safety and classification gate",
        "provenance_status": "externally_grounded_safety_boundary",
        "external_source_ids": [
            "hazardous_producers",
            "waste_classification",
            "weee_classification",
            "packaging_classification",
            "battery_measures",
        ],
        "internal_interpretation": (
            "Where hazardous status, classification or contextual safety concerns remain unresolved, "
            "the product fails safe into competent human review instead of selecting a routine circular route."
        ),
    },
    "R002_HIGH_CONTAMINATION_REVIEW": {
        "rule_family": "contamination gate",
        "provenance_status": "externally_informed_screening_boundary",
        "external_source_ids": ["waste_classification", "waste_hierarchy"],
        "internal_interpretation": (
            "High contamination is treated as a route-selection constraint until classification, composition "
            "and specialist acceptance evidence are available."
        ),
    },
    "R003_REDUCE_AT_SOURCE": {
        "rule_family": "prevention hierarchy",
        "provenance_status": "externally_grounded_hierarchy_rule",
        "external_source_ids": ["waste_hierarchy", "food_hierarchy"],
        "internal_interpretation": (
            "The screening engine prioritises prevention and, for edible surplus, redistribution before "
            "lower-value recycling or recovery routes."
        ),
    },
    "R004_SUPPLIER_TAKEBACK_AVAILABLE": {
        "rule_family": "supplier return loop",
        "provenance_status": "internal_operational_rule_with_hierarchy_basis",
        "external_source_ids": ["waste_hierarchy"],
        "internal_interpretation": (
            "Confirmed supplier take-back is screened as a value-retention opportunity. Supplier capability, "
            "contract terms, acceptance criteria and legal status still require evidence."
        ),
    },
    "R005_METAL_CLOSED_LOOP": {
        "rule_family": "metal circular route",
        "provenance_status": "internal_material_screening_rule",
        "external_source_ids": ["waste_hierarchy"],
        "internal_interpretation": (
            "Segregated low/medium-contamination metal is screened for closed-loop recycling where grade and "
            "route evidence can be established. Technical and market feasibility remain unverified."
        ),
    },
    "R006_PACKAGING_REUSE": {
        "rule_family": "packaging reuse",
        "provenance_status": "internal_material_screening_rule",
        "external_source_ids": ["waste_hierarchy"],
        "internal_interpretation": (
            "Low-contamination packaging is screened for reuse, returnable logistics or supplier redesign before recycling."
        ),
    },
    "R007_MIXED_PLASTIC_RECYCLING": {
        "rule_family": "mixed plastic route",
        "provenance_status": "internal_material_screening_rule",
        "external_source_ids": ["waste_hierarchy"],
        "internal_interpretation": (
            "Mixed plastics are directed to material testing and open-loop screening because polymer uncertainty "
            "weakens any closed-loop claim."
        ),
    },
    "R008_PLASTIC_CLOSED_LOOP": {
        "rule_family": "plastic circular route",
        "provenance_status": "internal_material_screening_rule",
        "external_source_ids": ["waste_hierarchy"],
        "internal_interpretation": (
            "Known lower-contamination plastics are screened for controlled recycling or secondary-material routes "
            "subject to grade, quality and acceptance evidence."
        ),
    },
    "R009_SYMBIOSIS_OR_RESOURCE_RECOVERY": {
        "rule_family": "resource recovery opportunity",
        "provenance_status": "internal_opportunity_screening_rule",
        "external_source_ids": ["waste_hierarchy"],
        "internal_interpretation": (
            "Process residues, water and resource streams are flagged for symbiosis/resource-recovery investigation. "
            "The rule does not establish by-product status, recipient suitability or legal route."
        ),
    },
    "R010_SPECIALIST_RECOVERY": {
        "rule_family": "specialist recovery",
        "provenance_status": "internal_specialist_route_screening_rule",
        "external_source_ids": ["waste_hierarchy", "weee_classification"],
        "internal_interpretation": (
            "Selected material families are screened for specialist recovery where risk is not already gated. "
            "WEEE-specific guidance is relevant only where the stream is electrical/electronic."
        ),
    },
    "R999_DEFAULT_EVIDENCE_IMPROVEMENT": {
        "rule_family": "fail-safe default",
        "provenance_status": "internal_governance_fallback",
        "external_source_ids": [],
        "internal_interpretation": (
            "Where the available information does not support a higher-value route, the system keeps the current "
            "compliant-route assumption and requests better evidence rather than inventing a circular recommendation."
        ),
    },
}


def _source_record(source_id: str) -> dict:
    source = GROUNDING_SOURCES[source_id]
    return {
        "source_id": source_id,
        **source,
        "source_role": "authoritative public guidance informing a screening boundary",
    }


def get_rule_provenance(rule_id: str) -> dict:
    """Return transparent provenance for one rule ID."""
    record = _RULES.get(rule_id)
    if record is None:
        return {
            "rule_id": rule_id,
            "rule_family": "unregistered",
            "provenance_status": "provenance_not_registered",
            "external_source_ids": [],
            "sources": [],
            "internal_interpretation": "No provenance entry is registered for this rule.",
            "governance_version": GOVERNANCE_VERSION,
            "last_reviewed_date": LAST_REVIEWED_DATE,
            "claim_boundary": (
                "Unregistered provenance must be resolved before this rule is relied on beyond internal testing."
            ),
        }

    source_ids = record["external_source_ids"]
    return {
        "rule_id": rule_id,
        **record,
        "sources": [_source_record(source_id) for source_id in source_ids],
        "governance_version": GOVERNANCE_VERSION,
        "last_reviewed_date": LAST_REVIEWED_DATE,
        "claim_boundary": (
            "Source linkage documents the basis of the screening rule. It does not make the software a legal "
            "classification tool, regulator-approved system or independent professional assurance."
        ),
    }


def list_rule_provenance() -> list[dict]:
    return [get_rule_provenance(rule_id) for rule_id in _RULES]
