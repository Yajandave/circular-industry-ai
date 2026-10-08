"""Evidence-source governance policy for observed outcome review.

The policy describes evidential role, not truth. A document type can be suitable
for internal factual reporting without being independently assured, current,
authentic or sufficient for a public environmental claim.
"""

from __future__ import annotations


EVIDENCE_SOURCE_POLICY = [
    {
        "source_type": "operator_log",
        "evidence_class": "operator_assertion",
        "supported_by_current_alpha": True,
        "eligible_for_internal_claim_gate": False,
        "independent_assurance": False,
        "typical_use": "Operational context, incident note or preliminary observation.",
        "limitations": (
            "Self-reported operational evidence. It cannot by itself pass the current internal factual claim gate."
        ),
    },
    {
        "source_type": "weighbridge_ticket",
        "evidence_class": "traceable_documentary_record",
        "supported_by_current_alpha": True,
        "eligible_for_internal_claim_gate": True,
        "independent_assurance": False,
        "typical_use": "Quantity evidence for a defined movement or period.",
        "limitations": (
            "Supports quantity traceability only when date, stream, unit and destination linkage are checked. "
            "It does not prove circularity, causality or environmental benefit."
        ),
    },
    {
        "source_type": "invoice_or_credit",
        "evidence_class": "traceable_commercial_record",
        "supported_by_current_alpha": True,
        "eligible_for_internal_claim_gate": True,
        "independent_assurance": False,
        "typical_use": "Commercial evidence linked to a route, quantity or service.",
        "limitations": (
            "Commercial documentation is not independent assurance of treatment outcome, compliance or environmental impact."
        ),
    },
    {
        "source_type": "system_export",
        "evidence_class": "traceable_internal_system_record",
        "supported_by_current_alpha": True,
        "eligible_for_internal_claim_gate": True,
        "independent_assurance": False,
        "typical_use": "ERP, waste-management or operational system record.",
        "limitations": (
            "System provenance, access controls, extraction scope and source-data quality still require review."
        ),
    },
    {
        "source_type": "supplier_confirmation",
        "evidence_class": "counterparty_documentary_record",
        "supported_by_current_alpha": True,
        "eligible_for_internal_claim_gate": True,
        "independent_assurance": False,
        "typical_use": "Supplier or contractor confirmation of collection, acceptance or route.",
        "limitations": (
            "A counterparty statement is useful evidence but is not independent assurance and may require corroboration."
        ),
    },
    {
        "source_type": "other_documentary",
        "evidence_class": "documentary_record_requires_classification",
        "supported_by_current_alpha": True,
        "eligible_for_internal_claim_gate": True,
        "independent_assurance": False,
        "typical_use": "Other traceable record reviewed by an operator.",
        "limitations": (
            "The reviewer must document what the evidence is, who issued it and why it supports the factual statement."
        ),
    },
    {
        "source_type": "independent_assurance",
        "evidence_class": "independent_external_assurance",
        "supported_by_current_alpha": False,
        "eligible_for_internal_claim_gate": False,
        "independent_assurance": True,
        "typical_use": "Future external verification or assurance process outside the current alpha.",
        "limitations": (
            "The current alpha does not ingest or certify independent assurance. Scope, standard, assurer competence "
            "and assurance conclusion would need separate governance."
        ),
    },
]


def evidence_source_policy() -> dict:
    return {
        "policy_version": "evidence-governance-2026-10-08",
        "source_classes": EVIDENCE_SOURCE_POLICY,
        "cross_cutting_checks": [
            "authenticity / source identity",
            "date and reporting-period relevance",
            "quantity and unit basis",
            "stream and site linkage",
            "route / destination linkage where relevant",
            "scope limitations and contradictory evidence",
            "reviewer competence and independence where required",
        ],
        "governance_note": (
            "Evidence class describes the role a source may play. The software does not authenticate documents, "
            "prove that a record is current or complete, resolve contradictory evidence automatically, or provide "
            "independent assurance."
        ),
    }
