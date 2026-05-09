"""Circular procurement and supplier-loop intelligence engine.

Milestone 7E converts circular resolution plans into supplier-facing actions:
contract levers, reverse-logistics checks, supplier evidence requests, acceptance
criteria and procurement pilot scopes. It never overrides the locked rules-engine
recommendation, risk level, human-review flag or claim boundary.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from app import models
from app.circular_resolution.advanced_playbooks import get_advanced_playbook
from app.circular_resolution.resolution_engine import build_resolution_plans


def _text(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, resolution: dict[str, Any]) -> str:
    return " ".join(
        str(value or "")
        for value in [
            stream.stream_id,
            stream.stream_name,
            stream.material,
            stream.source_process,
            stream.current_route,
            stream.department,
            stream.supplier,
            stream.supplier_takeback_available,
            stream.recycled_content_available,
            stream.notes,
            recommendation.circular_strategy_category,
            resolution.get("specific_resolution_idea"),
        ]
    ).lower()


def _contains(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _supplier_known(supplier: str | None) -> bool:
    if not supplier:
        return False
    return supplier.strip().lower() not in {"unknown", "various suppliers", "various", "n/a", "na"}


def _procurement_route(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, resolution: dict[str, Any]) -> str:
    text = _text(stream, recommendation, resolution)
    category = (recommendation.circular_strategy_category or "").lower()
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "controlled supplier / contractor evidence review"
    if "supplier take-back" in category or str(stream.supplier_takeback_available).lower() == "yes":
        return "supplier take-back and reverse-logistics loop"
    if _contains(text, ["pallet", "crate", "tote", "foam insert", "carton", "wrap", "packaging"]):
        return "returnable packaging or packaging-prevention loop"
    if "closed-loop" in category:
        return "closed-loop material return with supplier or recycler"
    if "reduce" in category:
        return "supplier specification and process-prevention review"
    if "industrial symbiosis" in category:
        return "external partner qualification and by-product agreement"
    if "open-loop" in category:
        return "specialist recycler qualification and acceptance review"
    return "procurement evidence-improvement review"


def _relationship_type(stream: models.IndustrialStream, route: str) -> str:
    if not _supplier_known(stream.supplier):
        return "supplier mapping required"
    if "contractor" in route or "specialist" in route:
        return "waste/recovery contractor relationship"
    if "packaging" in route or "reverse" in route or "take-back" in route:
        return "supplier loop / reverse-logistics relationship"
    if "closed-loop" in route:
        return "supplier/recycler closed-loop partnership"
    if "external partner" in route:
        return "industrial symbiosis partner relationship"
    return "commercial supplier relationship"


def _reverse_logistics_model(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> str:
    text = f"{stream.stream_name} {stream.current_route} {stream.notes}".lower()
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "No reverse-logistics movement should be designed until classification, contamination and authorised handling evidence are resolved."
    if "packaging" in route or _contains(text, ["pallet", "crate", "tote", "wrap", "insert", "carton"]):
        return "Return-to-supplier or pooled packaging loop with defined ownership, collection frequency, storage location and damage/rejection rules."
    if "closed-loop" in route or _contains(text, ["offcut", "scrap", "swarf", "trim"]):
        return "Segregated collection from source process to supplier/recycler, with grade/composition evidence and contamination acceptance limits."
    if "external partner" in route:
        return "Qualified transfer to approved partner only after composition, liability, storage and transport conditions are agreed."
    return "Supplier/contractor collection review with documented acceptance criteria and chain-of-custody evidence."


def _contract_levers(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> list[str]:
    levers = [
        "acceptance and rejection criteria for the material stream",
        "evidence requirement for route, collection, recovery or take-back outcome",
        "clear ownership and liability boundary before, during and after collection",
        "data-sharing requirement for quantities, rejected loads and route evidence",
    ]
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return [
            "competent-person review before any route change",
            "contractor authorisation and permit/registration evidence",
            "hazardous/non-hazardous classification and contamination evidence",
            "no circular claim or recovery statement until the review gate is closed",
        ]
    if "packaging" in route:
        levers += [
            "returnable packaging ownership model",
            "damage, loss and cleaning responsibility",
            "minimum return-cycle target or reusable packaging trial period",
        ]
    if "take-back" in route or "reverse" in route:
        levers += [
            "supplier take-back terms",
            "collection frequency and minimum volume threshold",
            "supplier evidence for onward reuse, recycling or closed-loop route",
        ]
    if "closed-loop" in route:
        levers += [
            "material grade/composition specification",
            "segregation requirements at source",
            "closed-loop route evidence or recycler certificate where available",
        ]
    if "specification" in route:
        levers += [
            "specification review to reduce over-ordering, over-packaging or reject generation",
            "supplier design-change request and trial acceptance criteria",
        ]
    return list(dict.fromkeys(levers))


def _supplier_questions(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> list[str]:
    supplier = stream.supplier if _supplier_known(stream.supplier) else "the responsible supplier or contractor"
    base = [
        f"Can {supplier} confirm the acceptance criteria for this stream, including contamination, segregation and minimum-volume requirements?",
        "What documentation can be provided to evidence the accepted route and final treatment or reuse/recycling outcome?",
        "What collection frequency, storage condition and packaging/container requirement would apply?",
        "What would cause a load to be rejected and who carries the cost or responsibility?",
    ]
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return [
            f"Can {supplier} provide authorised handling evidence, permit/registration details or contractor qualification for this stream?",
            "What classification, SDS, contamination analysis or consignment/transfer evidence is required before any route change?",
            "Is any recovery route available only after pre-treatment, segregation or specialist approval?",
            "What claims, if any, are supported by documented route evidence rather than marketing language?",
        ]
    if "packaging" in route:
        base += [
            "Can one-way packaging be reduced, redesigned or replaced by returnable transit packaging?",
            "Can the supplier run a limited returnable packaging pilot and report damage rate, return cycles and logistics cost?",
        ]
    if "take-back" in route or "reverse" in route:
        base += [
            "Can the supplier offer a take-back arrangement and provide evidence of what happens after collection?",
            "Can reverse logistics be combined with existing inbound deliveries to avoid a separate collection journey?",
        ]
    if "closed-loop" in route:
        base += [
            "Can the supplier or recycler accept material segregated by grade or composition for a closed-loop or equivalent route?",
            "What material specification and contamination limits must be recorded at source?",
        ]
    if "specification" in route:
        base += [
            "Can the supplier propose a lower-waste specification, packaging format or delivery method?",
            "What trial data would prove that the specification change reduces waste without increasing defects or damage?",
        ]
    return list(dict.fromkeys(base))


def _evidence_required(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, resolution: dict[str, Any], route: str) -> list[str]:
    evidence = list(resolution.get("evidence_required") or [])
    evidence += [
        "supplier or contractor acceptance criteria",
        "documented collection, transfer or take-back records",
        "quantity records for baseline and pilot period",
        "route evidence suitable for internal audit",
    ]
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        evidence += ["hazardous/non-hazardous classification", "contamination profile", "authorised contractor evidence"]
    if "packaging" in route:
        evidence += ["return-cycle records", "damage/loss records", "storage and handling feasibility"]
    if "closed-loop" in route:
        evidence += ["material grade/composition evidence", "closed-loop or equivalent route confirmation"]
    if "specification" in route:
        evidence += ["before/after defect or scrap data", "supplier design-change evidence"]
    return [item for item in dict.fromkeys(evidence) if item]


def _acceptance_criteria(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> list[str]:
    criteria = [
        "material must match supplier/contractor specification",
        "contamination must be within documented acceptance limits",
        "quantity and collection frequency must be commercially viable",
        "evidence must be sufficient for internal audit and claim-control rules",
    ]
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        criteria += ["competent review gate must be closed", "legal route and authorised handling must be confirmed"]
    if "packaging" in route:
        criteria += ["returnable assets must have ownership, cleaning, damage and loss rules"]
    if "closed-loop" in route:
        criteria += ["grade/composition segregation must be maintained from source to collection"]
    return criteria


def _commercial_checks(stream: models.IndustrialStream, recommendation: models.CircularRecommendation) -> list[str]:
    return [
        f"Compare current annual cost exposure of £{recommendation.estimated_annual_disposal_cost_avoided:,.0f} with pilot handling, storage and collection costs.",
        "Check whether any supplier rebate, credit, collection fee or minimum-volume condition changes the business case.",
        "Confirm whether the circular option creates additional labour, storage, transport or quality-control costs.",
        "Track value at stake as screening-level only until real invoice or supplier data exists.",
    ]


def _operational_checks(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> list[str]:
    checks = [
        f"Confirm where {stream.stream_name} is stored between generation and collection.",
        "Define responsible department owner and handover point to supplier/contractor.",
        "Set contamination check and rejection escalation process.",
    ]
    if "packaging" in route:
        checks += ["Check space for returnable packaging storage", "Define cleaning/inspection routine for returnable items"]
    if "closed-loop" in route:
        checks += ["Define labelled segregation containers", "Prevent mixing with lower-grade or contaminated material"]
    if recommendation.human_review_required:
        checks += ["Do not move to pilot implementation until review gates are completed"]
    return checks


def _data_requests(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> list[str]:
    requests = [
        "monthly quantity by source process",
        "current disposal/recovery invoices or service charges",
        "supplier/contractor acceptance criteria and rejection reasons",
        "collection records and route evidence",
    ]
    if "packaging" in route:
        requests += ["delivery frequency by supplier", "packaging weight per delivery", "damage rate"]
    if "closed-loop" in route:
        requests += ["grade/composition records", "recycler or supplier route documentation"]
    if recommendation.human_review_required:
        requests += ["hazard classification", "contamination analysis", "permit/authorisation evidence"]
    return list(dict.fromkeys(requests))


def _negotiation_position(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> str:
    if not _supplier_known(stream.supplier):
        return "Map supplier ownership first. For mixed or unknown suppliers, rank contributors before negotiating a circular loop."
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return f"Position the discussion with {stream.supplier} as an evidence and compliance review, not as a circular economy claim or implementation request."
    if recommendation.estimated_annual_waste_diverted_kg > 10000 or recommendation.estimated_annual_disposal_cost_avoided > 3000:
        return f"Use the volume/cost exposure to request a structured pilot from {stream.supplier}, with clear data-sharing and evidence obligations."
    return f"Use a low-risk pilot request with {stream.supplier}, focusing on feasibility evidence before commercial scale-up."


def _clause(route: str, recommendation: models.CircularRecommendation) -> str:
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "Supplier/contractor shall provide classification, authorised handling evidence, acceptance criteria and route documentation before any recovery or circular route is represented or implemented."
    if "packaging" in route:
        return "Supplier shall participate in a returnable packaging or packaging-reduction pilot, including return-cycle records, damage/loss tracking, collection responsibilities and documented fallback route."
    if "take-back" in route or "reverse" in route:
        return "Supplier shall provide take-back terms, collection conditions, acceptance/rejection criteria and evidence of onward reuse, recycling or recovery outcome for accepted material."
    if "closed-loop" in route:
        return "Supplier or recycler shall define material-grade requirements, contamination thresholds and evidence needed to support a closed-loop or equivalent recycling route."
    return "Supplier shall provide circular option evidence, route documentation and data needed to validate the proposed intervention before claims or scale-up."


def _priority(recommendation: models.CircularRecommendation, route: str) -> str:
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "controlled contract / compliance review"
    if "take-back" in route or "packaging" in route or "closed-loop" in route:
        if recommendation.evidence_quality_score >= 80 and recommendation.confidence_score >= 80:
            return "supplier-loop pilot candidate"
        return "supplier-loop evidence improvement"
    if "specification" in route:
        return "supplier specification review"
    return "procurement evidence improvement"


def _pilot_scope(stream: models.IndustrialStream, recommendation: models.CircularRecommendation, route: str) -> str:
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "Desk-based review only: supplier/contractor evidence, classification and acceptance criteria before any physical route change."
    if "packaging" in route:
        return "Run a 6-8 week pilot on one recurring supplier lane or delivery route, tracking return cycles, damage, storage, cost and avoided one-way packaging."
    if "closed-loop" in route or "take-back" in route or "reverse" in route:
        return "Run a 6-8 week controlled loop using segregated material, documented acceptance criteria and collection evidence before scaling."
    if "specification" in route:
        return "Run a before/after specification or process-prevention trial and compare quantity, quality defects, cost and rejection data."
    return "Run a limited evidence-gathering pilot with defined acceptance, cost and data requirements."


def _review_gate(recommendation: models.CircularRecommendation) -> str:
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "Do not proceed beyond evidence request until competent review confirms classification, legal route and acceptance criteria."
    if recommendation.evidence_quality_score < 70:
        return "Evidence-improvement gate: supplier evidence and baseline data required before pilot."
    return "Procurement validation gate: pilot may be scoped after supplier acceptance and evidence obligations are documented."


def _fallback(route: str, recommendation: models.CircularRecommendation) -> str:
    if recommendation.human_review_required or recommendation.risk_level in {"high", "blocked"}:
        return "Continue compliant authorised handling while evidence is unresolved."
    if "packaging" in route:
        return "Keep clean segregated recycling or current route as fallback if returnable packaging is not viable."
    if "closed-loop" in route or "take-back" in route:
        return "Use documented open-loop recycling or current compliant route if closed-loop/take-back acceptance fails."
    return "Maintain current compliant route until supplier evidence supports a change."


def _esrs_mapping(recommendation: models.CircularRecommendation) -> list[str]:
    mapping = ["ESRS E5 actions and resources", "resource outflows", "value-chain collaboration"]
    category = recommendation.circular_strategy_category.lower()
    if "supplier" in category or "procurement" in category:
        mapping.append("resource inflows and supplier circularity")
    if "packaging" in category:
        mapping.append("packaging and waste reduction")
    if recommendation.human_review_required:
        mapping.append("waste and hazardous/controlled stream governance")
    return list(dict.fromkeys(mapping))


def _cti_metrics(recommendation: models.CircularRecommendation, route: str) -> list[str]:
    metrics = ["% accepted by circular route", "screened value at stake", "evidence-readiness status"]
    if "packaging" in route or "reverse" in route or "take-back" in route:
        metrics += ["return-loop participation rate", "supplier evidence completion rate"]
    if "closed-loop" in route:
        metrics += ["% material kept in comparable loop", "% source-segregated material accepted"]
    if recommendation.human_review_required:
        metrics += ["review-gate closure status", "authorised-route evidence status"]
    return list(dict.fromkeys(metrics))


def build_supplier_loop_plan(
    stream: models.IndustrialStream,
    recommendation: models.CircularRecommendation,
    resolution: dict[str, Any],
) -> dict[str, Any]:
    playbook = get_advanced_playbook(stream.material)
    route = _procurement_route(stream, recommendation, resolution)
    return {
        "stream_id": stream.stream_id,
        "stream_name": stream.stream_name,
        "material": stream.material,
        "department": stream.department,
        "supplier": stream.supplier,
        "locked_recommendation": recommendation.recommended_circular_action,
        "risk_level": recommendation.risk_level,
        "human_review_required": recommendation.human_review_required,
        "rule_applied": recommendation.rule_applied,
        "procurement_route": route,
        "supplier_loop_opportunity": "controlled review" if recommendation.human_review_required else "screening opportunity",
        "supplier_relationship_type": _relationship_type(stream, route),
        "reverse_logistics_model": _reverse_logistics_model(stream, recommendation, route),
        "contract_levers": _contract_levers(stream, recommendation, route),
        "supplier_questions": _supplier_questions(stream, recommendation, route),
        "supplier_evidence_required": _evidence_required(stream, recommendation, resolution, route),
        "acceptance_criteria": _acceptance_criteria(stream, recommendation, route),
        "commercial_checks": _commercial_checks(stream, recommendation),
        "operational_checks": _operational_checks(stream, recommendation, route),
        "data_requests": _data_requests(stream, recommendation, route),
        "negotiation_position": _negotiation_position(stream, recommendation, route),
        "circular_procurement_clause": _clause(route, recommendation),
        "procurement_priority": _priority(recommendation, route),
        "pilot_scope": _pilot_scope(stream, recommendation, route),
        "review_gate": _review_gate(recommendation),
        "claim_boundary": resolution.get("claim_boundary") or "Do not make external circularity claims until evidence is validated.",
        "fallback_position": _fallback(route, recommendation),
        "linked_esrs_e5_area": _esrs_mapping(recommendation),
        "cti_procurement_metrics": _cti_metrics(recommendation, route),
        "material_playbook_supplier_levers": playbook.supplier_and_procurement_levers,
        "estimated_annual_value_at_stake": recommendation.estimated_annual_disposal_cost_avoided,
    }


def build_supplier_loop_plans(
    streams: list[models.IndustrialStream],
    recommendations: list[models.CircularRecommendation],
) -> list[dict[str, Any]]:
    resolution_plans = build_resolution_plans(streams, recommendations)
    stream_lookup = {stream.stream_id: stream for stream in streams}
    rec_lookup = {rec.stream_id: rec for rec in recommendations}
    plans = []
    for resolution in resolution_plans:
        stream = stream_lookup.get(resolution["stream_id"])
        recommendation = rec_lookup.get(resolution["stream_id"])
        if stream and recommendation:
            plans.append(build_supplier_loop_plan(stream, recommendation, resolution))
    return plans


def build_supplier_loop_summary(plans: list[dict[str, Any]]) -> dict[str, Any]:
    priority_counts = Counter(plan["procurement_priority"] for plan in plans)
    route_counts = Counter(plan["procurement_route"] for plan in plans)
    supplier_loop_candidates = sum(1 for plan in plans if "pilot candidate" in plan["procurement_priority"])
    reverse_candidates = sum(1 for plan in plans if "reverse" in plan["procurement_route"] or "packaging" in plan["procurement_route"] or "closed-loop" in plan["procurement_route"])
    controlled = sum(1 for plan in plans if plan["human_review_required"])
    contract_review = sum(1 for plan in plans if "evidence" in plan["procurement_priority"] or "contract" in plan["procurement_priority"] or plan["human_review_required"])
    top = sorted(
        [plan for plan in plans if not plan["human_review_required"]],
        key=lambda plan: plan["estimated_annual_value_at_stake"],
        reverse=True,
    )[:6]
    return {
        "total_plans": len(plans),
        "supplier_loop_candidates": supplier_loop_candidates,
        "reverse_logistics_candidates": reverse_candidates,
        "contract_review_required": contract_review,
        "controlled_supplier_reviews": controlled,
        "procurement_priority_breakdown": dict(priority_counts),
        "procurement_route_breakdown": dict(route_counts),
        "top_supplier_actions": [
            {
                "stream_id": plan["stream_id"],
                "stream_name": plan["stream_name"],
                "supplier": plan["supplier"],
                "procurement_route": plan["procurement_route"],
                "estimated_annual_value_at_stake": plan["estimated_annual_value_at_stake"],
                "supplier_question": plan["supplier_questions"][0] if plan["supplier_questions"] else "No supplier question generated.",
            }
            for plan in top
        ],
        "method_note": (
            "Supplier-loop plans translate circular resolution plans into procurement actions. They are not contract advice, legal advice or supplier verification. They define evidence requests, negotiation prompts and pilot controls for human procurement review."
        ),
    }
