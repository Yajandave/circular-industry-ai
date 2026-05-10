"""Autonomous insight generation from raw stream data and retrieved knowledge."""

from __future__ import annotations

from typing import Any

from app.knowledge_base.retriever import retrieve_knowledge_for_stream


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


def _dedupe(values: list[str], *, limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = str(value or "").strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
        if limit is not None and len(result) >= limit:
            break
    return result


def _knowledge_ids(records: list[dict[str, Any]]) -> list[str]:
    return _dedupe([record.get("knowledge_id", "") for record in records])


def _first(records: list[dict[str, Any]]) -> dict[str, Any]:
    return records[0] if records else {}


def _route_names(records: list[dict[str, Any]]) -> set[str]:
    return {_normalise(record.get("route")) for record in records}


def _material_families(records: list[dict[str, Any]]) -> list[str]:
    return _dedupe([record.get("material_family", "") for record in records])


def _build_current_action(stream: Any, retrieval: dict[str, Any]) -> dict[str, Any]:
    material = _text(stream, "material") or "this material stream"
    process = _text(stream, "source_process") or "the source process"
    contamination = _normalise(_text(stream, "contamination_risk"))
    hazardous = _normalise(_text(stream, "hazardous_flag"))
    matched_material = _first(retrieval["matched_materials"])
    routes = _route_names(retrieval["matched_routes"])
    families = set(_material_families(retrieval["matched_materials"]))

    if hazardous in {"true", "unknown"} or families.intersection({"chemicals_solvents", "batteries"}):
        content = (
            f"Treat {material} from {process} as a controlled review stream before selecting a circular route. "
            "Confirm hazardous status, handling requirements and authorised recovery/disposal options with a competent EHS or waste specialist."
        )
        maturity = "available_now"
        confidence = "high"
    elif contamination == "high":
        content = (
            f"Do not treat {material} from {process} as a direct recycling candidate yet. "
            "First identify the contamination source, confirm material composition and test whether segregation or process changes can make recovery viable."
        )
        maturity = "available_now"
        confidence = "high"
    elif "closed_loop_recycling" in routes:
        content = (
            f"Review {material} for closed-loop or high-value recovery because the stream appears suitable for material-retention screening. "
            "Confirm grade/composition, segregation quality and recycler or supplier acceptance criteria before action."
        )
        maturity = "available_now"
        confidence = "medium_high"
    elif "supplier_takeback" in routes:
        content = (
            f"Open a supplier take-back review for {material}. Confirm whether the supplier can accept the stream, what limits apply and what documentation is required."
        )
        maturity = "available_now"
        confidence = "medium"
    else:
        content = (
            f"Use the matched knowledge base to run a controlled circular opportunity review for {material}. "
            "Start with data quality, evidence gaps and current-route confirmation before making claims."
        )
        maturity = "available_now"
        confidence = "medium"

    return {
        "title": "Current action",
        "content": content,
        "maturity": maturity,
        "confidence": confidence,
        "source_knowledge_ids": _knowledge_ids(retrieval["matched_materials"] + retrieval["matched_routes"][:2]),
    }


def _build_near_future_action(stream: Any, retrieval: dict[str, Any]) -> dict[str, Any]:
    material = _text(stream, "material") or "this stream"
    matched_material = _first(retrieval["matched_materials"])
    pilot_routes = matched_material.get("pilot_ready_routes", []) if matched_material else []
    route_names = _route_names(retrieval["matched_routes"])

    if pilot_routes:
        content = (
            f"Prepare a controlled pilot for {material}: {pilot_routes[0]}. "
            "Define baseline quantity, contamination controls, supplier/recycler acceptance criteria, collection method and success metrics before implementation."
        )
    elif "process_redesign" in route_names:
        content = (
            f"Prepare a process-improvement review for {material}. Identify the operational cause of the stream, set a baseline and test whether scrap can be prevented before downstream recovery is considered."
        )
    else:
        content = (
            f"Prepare a small validation cycle for {material}. Confirm the route, evidence requirements, responsible owner, data capture method and review gate before scaling."
        )

    return {
        "title": "Near-future action",
        "content": content,
        "maturity": "pilot_ready",
        "confidence": "medium",
        "source_knowledge_ids": _knowledge_ids(retrieval["matched_materials"] + retrieval["matched_routes"]),
    }


def _build_future_watch(retrieval: dict[str, Any]) -> dict[str, Any]:
    future_items = retrieval["future_horizon"]
    if not future_items:
        return {
            "title": "Future watch",
            "content": "No specific future-horizon knowledge matched this stream yet. Add more material or sector knowledge before making future opportunity suggestions.",
            "maturity": "not_recommended",
            "confidence": "low",
            "source_knowledge_ids": [],
        }

    fragments: list[str] = []
    maturities: list[str] = []
    confidences: list[str] = []
    for item in future_items[:2]:
        topic = item.get("topic", "future circular opportunity")
        maturity = item.get("maturity", "emerging")
        boundary = item.get("claim_boundary", "Treat as future watch only until evidenced.")
        fragments.append(f"Monitor {topic} as a {maturity.replace('_', '-')} option. {boundary}")
        maturities.append(maturity)
        confidences.append(item.get("confidence", "medium"))

    return {
        "title": "Future watch",
        "content": " ".join(fragments),
        "maturity": maturities[0] if maturities else "emerging",
        "confidence": confidences[0] if confidences else "medium",
        "source_knowledge_ids": _knowledge_ids(future_items),
    }


def _collect_evidence_needed(retrieval: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for material in retrieval["matched_materials"]:
        values.extend(material.get("evidence_required", []))
    for route in retrieval["matched_routes"]:
        values.extend(route.get("required_evidence", []))
        values.extend(route.get("required_data", []))
    for rule in retrieval["evidence_rules"]:
        values.extend(rule.get("required_evidence", []))
        values.extend(rule.get("supplier_documents", []))
        values.extend(rule.get("commercial_checks", []))
    return _dedupe(values, limit=18)


def _collect_supplier_questions(retrieval: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for material in retrieval["matched_materials"]:
        values.extend(material.get("supplier_questions", []))
    if retrieval["matched_routes"]:
        for route in retrieval["matched_routes"]:
            route_name = route.get("route", "").replace("_", " ")
            if route_name:
                values.append(f"Can the supplier or contractor confirm whether {route_name} is feasible for this stream?")
            for requirement in route.get("required_evidence", [])[:3]:
                values.append(f"Can the supplier/contractor provide evidence for: {requirement}?")
    return _dedupe(values, limit=12)


def _collect_human_review_triggers(stream: Any, retrieval: dict[str, Any]) -> list[str]:
    values: list[str] = []
    contamination = _normalise(_text(stream, "contamination_risk"))
    hazardous = _normalise(_text(stream, "hazardous_flag"))

    if hazardous in {"true", "unknown"}:
        values.append("Hazardous status is true or unknown.")
    if contamination == "high":
        values.append("High contamination risk is recorded.")

    for material in retrieval["matched_materials"]:
        values.extend(material.get("human_review_triggers", []))
    for note in retrieval.get("retrieval_notes", []):
        if "review" in note.lower() or "contamination" in note.lower():
            values.append(note)

    return _dedupe(values, limit=10)


def _collect_do_not_claim(retrieval: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for material in retrieval["matched_materials"]:
        values.extend(material.get("unsafe_claims", []))
    for rule in retrieval["evidence_rules"]:
        values.extend(rule.get("unsafe_claims", []))
    for future in retrieval["future_horizon"]:
        values.extend(future.get("do_not_claim", []))
    values.extend(
        [
            "verified diversion without measured movement records",
            "verified cost saving without finance/invoice evidence",
            "carbon saving without accepted calculation method and boundary",
        ]
    )
    return _dedupe(values, limit=16)


def _claim_boundary(retrieval: dict[str, Any]) -> str:
    material = _first(retrieval["matched_materials"])
    if material.get("default_claim_boundary"):
        return material["default_claim_boundary"]

    route = _first(retrieval["matched_routes"])
    if route.get("claim_boundary"):
        return route["claim_boundary"]

    return "Screening only until evidence confirms route feasibility, operational outcome and claim boundary."


def generate_autonomous_insight(stream: Any) -> dict[str, Any]:
    """Generate deterministic advisory insight from raw stream data and retrieved knowledge."""
    retrieval = retrieve_knowledge_for_stream(stream)
    notes = _text(stream, "notes")
    matched_materials = retrieval["matched_materials"]
    matched_routes = retrieval["matched_routes"]
    evidence_rules = retrieval["evidence_rules"]
    future_horizon = retrieval["future_horizon"]

    current_action = _build_current_action(stream, retrieval)
    near_future_action = _build_near_future_action(stream, retrieval)
    future_watch = _build_future_watch(retrieval)

    source_knowledge_ids = _knowledge_ids(matched_materials + matched_routes + evidence_rules + future_horizon)

    if matched_materials:
        summary = (
            f"The stream matches {', '.join(_material_families(matched_materials))} knowledge. "
            "The generated advice is based on structured stream fields and retrieved knowledge, not on pre-written notes."
        )
    else:
        summary = (
            "No material-family knowledge matched this stream. The system can still identify governance boundaries, "
            "but material-specific autonomous advice should be limited until a relevant playbook is added."
        )

    return {
        "stream_id": _text(stream, "stream_id") or "unknown",
        "stream_name": _text(stream, "stream_name"),
        "material": _text(stream, "material"),
        "source_process": _text(stream, "source_process"),
        "input_notes_present": bool(notes),
        "notes_dependency": "not_required",
        "insight_summary": summary,
        "matched_material_families": _material_families(matched_materials),
        "current_action": current_action,
        "near_future_action": near_future_action,
        "future_watch": future_watch,
        "evidence_needed": _collect_evidence_needed(retrieval),
        "supplier_questions": _collect_supplier_questions(retrieval),
        "human_review_triggers": _collect_human_review_triggers(stream, retrieval),
        "do_not_claim": _collect_do_not_claim(retrieval),
        "claim_boundary": _claim_boundary(retrieval),
        "source_knowledge_ids": source_knowledge_ids,
        "retrieval_notes": retrieval["retrieval_notes"],
        "governance_note": (
            "Autonomous insights are generated from structured stream data plus retrieved knowledge. "
            "They are advisory and do not verify legal compliance, supplier acceptance, circularity claims, "
            "carbon savings, financial savings or operational impact."
        ),
    }
