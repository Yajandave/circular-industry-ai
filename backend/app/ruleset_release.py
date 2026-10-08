"""Ruleset release identity and rule-family versions.

Version 1.0.0 freezes the current deterministic screening logic. Version labels
are assigned only to recommendation runs generated after this feature is active;
legacy rows are not retrospectively labelled. Future logic changes must bump
the affected rule-family version and the ruleset version.
"""

from __future__ import annotations

RULESET_VERSION = "circular-core-ruleset-v1.0.0"
RULESET_RELEASE_DATE = "2026-10-08"
RULESET_STATUS = "alpha_screening_not_independently_validated"

RULE_VERSIONS = {
    "R001_HAZARDOUS_OR_UNKNOWN_REVIEW": "1.0.0",
    "R002_HIGH_CONTAMINATION_REVIEW": "1.0.0",
    "R003_REDUCE_AT_SOURCE": "1.0.0",
    "R004_SUPPLIER_TAKEBACK_AVAILABLE": "1.0.0",
    "R005_METAL_CLOSED_LOOP": "1.0.0",
    "R006_PACKAGING_REUSE": "1.0.0",
    "R007_MIXED_PLASTIC_RECYCLING": "1.0.0",
    "R008_PLASTIC_CLOSED_LOOP": "1.0.0",
    "R009_SYMBIOSIS_OR_RESOURCE_RECOVERY": "1.0.0",
    "R010_SPECIALIST_RECOVERY": "1.0.0",
    "R999_DEFAULT_EVIDENCE_IMPROVEMENT": "1.0.0",
}


def rule_version(rule_id: str) -> str:
    if rule_id not in RULE_VERSIONS:
        raise ValueError(f"Unversioned rule: {rule_id}")
    return RULE_VERSIONS[rule_id]


def ruleset_metadata() -> dict:
    return {
        "ruleset_version": RULESET_VERSION,
        "release_date": RULESET_RELEASE_DATE,
        "status": RULESET_STATUS,
        "rule_versions": dict(RULE_VERSIONS),
        "provenance_note": (
            "Version identity describes which internal screening logic produced a decision. "
            "It is not a legal determination, independent assurance or accuracy certification. "
            "Pre-versioning records are not retroactively assigned a ruleset version."
        ),
    }
