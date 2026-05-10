"""Knowledge retrieval engine for stream-level circular economy intelligence."""

from __future__ import annotations

import re
from typing import Any

from app.knowledge_base.loader import load_collection, validate_knowledge_base


GENERIC_MATCH_TOKENS = {
    "mixed",
    "waste",
    "reject",
    "rejects",
    "material",
    "materials",
    "stream",
    "streams",
    "general",
    "production",
    "process",
    "route",
    "supplier",
    "unknown",
    "current",
}


def _get(record: Any, field: str, default: Any = "") -> Any:
    if isinstance(record, dict):
        return record.get(field, default)
    return getattr(record, field, default)


def _text(record: Any, field: str) -> str:
    value = _get(record, field, "")
    if value is None:
        return ""
    return str(value).strip()


def _normalise(value: Any) -> str:
    return str(value or "").strip().lower()


def _tokens(value: Any) -> set[str]:
    text = _normalise(value)
    return {
        token
        for token in re.split(r"[^a-z0-9]+", text)
        if len(token) >= 3 and token not in GENERIC_MATCH_TOKENS
    }


def _contains_any(search_blob: str, values: list[str]) -> bool:
    blob = _normalise(search_blob)
    return any(_normalise(value) and _normalise(value) in blob for value in values)


def _score_material(material_record: dict[str, Any], search_blob: str) -> int:
    score = 0
    family = _normalise(material_record.get("material_family"))
    aliases = [_normalise(alias) for alias in material_record.get("aliases", [])]
    common_streams = [_normalise(item) for item in material_record.get("common_streams", [])]
    typical_processes = [_normalise(item) for item in material_record.get("typical_processes", [])]

    if family and family in _normalise(search_blob):
        score += 8

    for alias in aliases:
        if alias and alias in _normalise(search_blob):
            score += 5

    for stream in common_streams:
        if stream and stream in _normalise(search_blob):
            score += 4

    for process in typical_processes:
        if process and process in _normalise(search_blob):
            score += 3

    # Token overlap helps catch partial matches such as "mixed polymer rejects".
    blob_tokens = _tokens(search_blob)
    material_tokens = set()
    for value in [family, *aliases, *common_streams, *typical_processes]:
        material_tokens.update(_tokens(value))
    score += min(5, len(blob_tokens.intersection(material_tokens)))

    return score


def _route_score(
    route_record: dict[str, Any],
    *,
    search_blob: str,
    material_records: list[dict[str, Any]],
    contamination_risk: str,
    hazardous_flag: str,
    supplier_takeback_available: str,
) -> int:
    route = _normalise(route_record.get("route"))
    score = 0
    route_tokens = _tokens(route)
    search_tokens = _tokens(search_blob)

    if route_tokens.intersection(search_tokens):
        score += 2

    material_route_text = " ".join(
        " ".join(record.get(field, []))
        for record in material_records
        for field in ["available_now_routes", "pilot_ready_routes"]
    ).lower()

    if route.replace("_", " ") in material_route_text:
        score += 5

    if "take-back" in material_route_text and route == "supplier_takeback":
        score += 5
    if "closed-loop" in material_route_text and route == "closed_loop_recycling":
        score += 5
    if "specialist" in material_route_text and route == "specialist_recovery":
        score += 4
    if "redesign" in material_route_text and route == "process_redesign":
        score += 4

    if hazardous_flag in {"true", "unknown"} and route in {"compliant_disposal", "specialist_recovery"}:
        score += 8

    if contamination_risk == "high" and route in {"specialist_recovery", "process_redesign", "compliant_disposal"}:
        score += 5

    if supplier_takeback_available in {"yes", "unknown", ""} and route == "supplier_takeback":
        score += 3

    if contamination_risk == "low" and hazardous_flag == "false" and route == "closed_loop_recycling":
        score += 4

    return score


def _select_evidence_rules(
    stream: Any,
    *,
    matched_materials: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence_rules = load_collection("evidence_rules")
    selected: list[dict[str, Any]] = []

    hazardous_flag = _normalise(_text(stream, "hazardous_flag"))
    contamination_risk = _normalise(_text(stream, "contamination_risk"))
    supplier = _normalise(_text(stream, "supplier"))
    takeback = _normalise(_text(stream, "supplier_takeback_available"))
    material_families = {_normalise(material.get("material_family")) for material in matched_materials}

    for rule in evidence_rules:
        rule_name = _normalise(rule.get("rule_name"))
        if rule_name == "claim_readiness_ladder":
            selected.append(rule)
        elif rule_name == "hazardous_unknown_review" and (
            hazardous_flag in {"true", "unknown"} or contamination_risk == "high" or "chemicals_solvents" in material_families or "batteries" in material_families
        ):
            selected.append(rule)
        elif rule_name == "supplier_evidence_requirements" and (supplier and supplier not in {"unknown", "n/a", "na"} or takeback in {"yes", "unknown"}):
            selected.append(rule)

    return selected


def _select_future_horizon(matched_materials: list[dict[str, Any]], stream: Any) -> list[dict[str, Any]]:
    future_items = load_collection("future_horizon")
    selected: list[dict[str, Any]] = []
    material_families = {_normalise(material.get("material_family")) for material in matched_materials}
    supplier = _normalise(_text(stream, "supplier"))
    recycled = _normalise(_text(stream, "recycled_content_available"))

    for item in future_items:
        related = {_normalise(value) for value in item.get("related_material_families", [])}
        if material_families.intersection(related):
            selected.append(item)
            continue

        if "cross_material" in related and (supplier or recycled in {"unknown", "no"}):
            selected.append(item)

    return selected


def _compact_record(record: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    compact = {field: record.get(field) for field in fields if field in record}
    compact["source_references"] = record.get("source_references", [])
    return compact


def retrieve_knowledge_for_stream(stream: Any, *, include_full_records: bool = False) -> dict[str, Any]:
    """Retrieve relevant material, route, evidence and future-horizon knowledge for a stream."""
    validation = validate_knowledge_base()
    materials = load_collection("materials")
    routes = load_collection("circular_routes")

    stream_id = _text(stream, "stream_id") or "unknown"
    search_blob = " ".join(
        [
            _text(stream, "stream_id"),
            _text(stream, "stream_name"),
            _text(stream, "material"),
            _text(stream, "source_process"),
            _text(stream, "current_route"),
            _text(stream, "department"),
            _text(stream, "supplier"),
            _text(stream, "notes"),
        ]
    )

    scored_materials = sorted(
        [
            (material, _score_material(material, search_blob))
            for material in materials
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    top_material_score = scored_materials[0][1] if scored_materials else 0
    material_match_min_score = max(5, top_material_score - 4)

    matched_materials = [
        material
        for material, score in scored_materials
        if score >= material_match_min_score and score > 0
    ][:3]

    contamination_risk = _normalise(_text(stream, "contamination_risk"))
    hazardous_flag = _normalise(_text(stream, "hazardous_flag"))
    supplier_takeback_available = _normalise(_text(stream, "supplier_takeback_available"))

    scored_routes = [
        (
            route,
            _route_score(
                route,
                search_blob=search_blob,
                material_records=matched_materials,
                contamination_risk=contamination_risk,
                hazardous_flag=hazardous_flag,
                supplier_takeback_available=supplier_takeback_available,
            ),
        )
        for route in routes
    ]
    matched_routes = [
        route for route, score in sorted(scored_routes, key=lambda item: item[1], reverse=True) if score > 0
    ][:5]

    evidence_rules = _select_evidence_rules(stream, matched_materials=matched_materials)
    future_horizon = _select_future_horizon(matched_materials, stream)

    retrieval_notes: list[str] = []
    if not validation["valid"]:
        retrieval_notes.append("Knowledge base validation has issues; inspect validation summary before relying on retrieval.")
    if not matched_materials:
        retrieval_notes.append("No material-family knowledge matched this stream. Add a material playbook or improve aliases.")
    if hazardous_flag in {"true", "unknown"}:
        retrieval_notes.append("Hazardous or unknown status detected. Human/EHS review must precede circular routing.")
    if contamination_risk == "high":
        retrieval_notes.append("High contamination detected. Recovery routes need contamination evidence before action.")
    if not future_horizon:
        retrieval_notes.append("No future-horizon item matched this stream.")

    if include_full_records:
        material_output = matched_materials
        route_output = matched_routes
        evidence_output = evidence_rules
        future_output = future_horizon
    else:
        material_output = [
            _compact_record(
                record,
                [
                    "knowledge_id",
                    "material_family",
                    "aliases",
                    "available_now_routes",
                    "pilot_ready_routes",
                    "future_watch_routes",
                    "evidence_required",
                    "supplier_questions",
                    "human_review_triggers",
                    "unsafe_claims",
                    "default_claim_boundary",
                ],
            )
            for record in matched_materials
        ]
        route_output = [
            _compact_record(
                record,
                [
                    "knowledge_id",
                    "route",
                    "route_strength",
                    "best_for",
                    "not_suitable_for",
                    "required_data",
                    "required_evidence",
                    "implementation_steps",
                    "claim_boundary",
                ],
            )
            for record in matched_routes
        ]
        evidence_output = [
            _compact_record(
                record,
                [
                    "knowledge_id",
                    "rule_name",
                    "evidence_ladder",
                    "required_evidence",
                    "required_action",
                    "supplier_documents",
                    "commercial_checks",
                    "unsafe_claims",
                    "default_claim_boundary",
                ],
            )
            for record in evidence_rules
        ]
        future_output = [
            _compact_record(
                record,
                [
                    "knowledge_id",
                    "topic",
                    "related_material_families",
                    "maturity",
                    "confidence",
                    "current_use",
                    "when_to_suggest",
                    "evidence_needed_to_upgrade",
                    "do_not_claim",
                    "claim_boundary",
                ],
            )
            for record in future_horizon
        ]

    return {
        "stream_id": stream_id,
        "stream_name": _text(stream, "stream_name"),
        "material": _text(stream, "material"),
        "source_process": _text(stream, "source_process"),
        "matched_materials": material_output,
        "matched_routes": route_output,
        "evidence_rules": evidence_output,
        "future_horizon": future_output,
        "retrieval_notes": retrieval_notes,
        "knowledge_validation": validation,
        "governance_note": (
            "Knowledge retrieval provides advisory context for AI reasoning. It does not verify legal compliance, "
            "supplier acceptance, circularity claims, carbon savings, financial savings or operational impact."
        ),
    }
