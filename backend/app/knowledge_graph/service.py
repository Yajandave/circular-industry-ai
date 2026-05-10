"""Deterministic knowledge-graph relationship layer.

The graph layer converts retrieved knowledge into explicit relationship paths:
stream -> material family -> route options -> evidence rules -> future watch -> claim controls.
"""

from __future__ import annotations

from typing import Any

from app.knowledge_base.loader import load_collection, validate_knowledge_base
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


def _dedupe(values: list[str]) -> list[str]:
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
    return result


def _node(node_id: str, label: str, node_type: str, detail: str = "", source_knowledge_id: str | None = None) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "label": label,
        "node_type": node_type,
        "detail": detail,
        "source_knowledge_id": source_knowledge_id,
    }


def _edge(
    source: str,
    target: str,
    relationship: str,
    evidence_level: str = "knowledge_base",
    governance_note: str = "",
) -> dict[str, Any]:
    return {
        "source": source,
        "target": target,
        "relationship": relationship,
        "evidence_level": evidence_level,
        "governance_note": governance_note,
    }


def _material_graph_nodes_and_edges(stream_node_id: str, retrieval: dict[str, Any]) -> tuple[list[dict], list[dict], list[str]]:
    nodes: list[dict] = []
    edges: list[dict] = []
    graph_path: list[str] = []

    for material in retrieval["matched_materials"]:
        knowledge_id = material.get("knowledge_id", "")
        family = material.get("material_family", "unknown material")
        node_id = f"material:{family}"

        nodes.append(
            _node(
                node_id,
                family,
                "material_family",
                "Matched material-family knowledge.",
                knowledge_id,
            )
        )
        edges.append(
            _edge(
                stream_node_id,
                node_id,
                "matches_material_family",
                "retrieved_match",
                "Material relationship is based on deterministic knowledge retrieval, not notes-only interpretation.",
            )
        )
        graph_path.append(f"stream -> material family: {family}")

        for blocker in material.get("blocked_by", []):
            blocker_id = f"blocker:{family}:{_normalise(blocker).replace(' ', '_')}"
            nodes.append(_node(blocker_id, blocker, "blocker", "Condition that can block or weaken a circular route.", knowledge_id))
            edges.append(_edge(node_id, blocker_id, "blocked_by", "knowledge_base"))
            graph_path.append(f"{family} -> blocker: {blocker}")

        for trigger in material.get("human_review_triggers", []):
            trigger_id = f"review_trigger:{family}:{_normalise(trigger).replace(' ', '_')}"
            nodes.append(_node(trigger_id, trigger, "human_review_trigger", "Trigger requiring controlled human review.", knowledge_id))
            edges.append(_edge(node_id, trigger_id, "requires_review_when", "knowledge_base"))

        for unsafe in material.get("unsafe_claims", []):
            unsafe_id = f"unsafe_claim:{family}:{_normalise(unsafe).replace(' ', '_')}"
            nodes.append(_node(unsafe_id, unsafe, "unsafe_claim", "Claim that must not be made without evidence.", knowledge_id))
            edges.append(_edge(node_id, unsafe_id, "must_not_claim", "knowledge_base"))

    return nodes, edges, graph_path


def _route_graph_nodes_and_edges(retrieval: dict[str, Any]) -> tuple[list[dict], list[dict], list[str]]:
    nodes: list[dict] = []
    edges: list[dict] = []
    graph_path: list[str] = []

    material_nodes = [f"material:{m.get('material_family')}" for m in retrieval["matched_materials"]]

    for route in retrieval["matched_routes"]:
        knowledge_id = route.get("knowledge_id", "")
        route_name = route.get("route", "unknown_route")
        route_id = f"route:{route_name}"
        strength = route.get("route_strength", "candidate")

        nodes.append(
            _node(
                route_id,
                route_name.replace("_", " "),
                "circular_route",
                f"Candidate route. Strength: {strength}.",
                knowledge_id,
            )
        )

        for material_id in material_nodes:
            edges.append(
                _edge(
                    material_id,
                    route_id,
                    "has_candidate_route",
                    "retrieved_match",
                    "Route is a candidate relationship, not verified operational acceptance.",
                )
            )
            graph_path.append(f"{material_id} -> route: {route_name}")

        for evidence in route.get("required_evidence", []):
            evidence_id = f"evidence:{route_name}:{_normalise(evidence).replace(' ', '_')}"
            nodes.append(_node(evidence_id, evidence, "required_evidence", "Evidence required before route can be treated as validated.", knowledge_id))
            edges.append(_edge(route_id, evidence_id, "requires_evidence", "knowledge_base"))

        for data in route.get("required_data", []):
            data_id = f"data:{route_name}:{_normalise(data).replace(' ', '_')}"
            nodes.append(_node(data_id, data, "required_data", "Data required for controlled route assessment.", knowledge_id))
            edges.append(_edge(route_id, data_id, "requires_data", "knowledge_base"))

        claim_boundary = route.get("claim_boundary")
        if claim_boundary:
            boundary_id = f"claim_boundary:{route_name}"
            nodes.append(_node(boundary_id, "Claim boundary", "claim_boundary", claim_boundary, knowledge_id))
            edges.append(_edge(route_id, boundary_id, "has_claim_boundary", "knowledge_base"))

    return nodes, edges, graph_path


def _evidence_rule_nodes_and_edges(retrieval: dict[str, Any]) -> tuple[list[dict], list[dict], list[str]]:
    nodes: list[dict] = []
    edges: list[dict] = []
    graph_path: list[str] = []

    route_nodes = [f"route:{r.get('route')}" for r in retrieval["matched_routes"]]

    for rule in retrieval["evidence_rules"]:
        knowledge_id = rule.get("knowledge_id", "")
        rule_name = rule.get("rule_name", "evidence_rule")
        rule_id = f"evidence_rule:{rule_name}"

        nodes.append(
            _node(
                rule_id,
                rule_name.replace("_", " "),
                "evidence_rule",
                "Evidence control rule matched to this stream.",
                knowledge_id,
            )
        )

        for route_id in route_nodes:
            edges.append(_edge(route_id, rule_id, "controlled_by_evidence_rule", "knowledge_base"))
            graph_path.append(f"{route_id} -> evidence rule: {rule_name}")

        for unsafe in rule.get("unsafe_claims", []):
            unsafe_id = f"unsafe_claim:{rule_name}:{_normalise(unsafe).replace(' ', '_')}"
            nodes.append(_node(unsafe_id, unsafe, "unsafe_claim", "Evidence-rule unsafe claim boundary.", knowledge_id))
            edges.append(_edge(rule_id, unsafe_id, "must_not_claim", "knowledge_base"))

    return nodes, edges, graph_path


def _future_nodes_and_edges(retrieval: dict[str, Any]) -> tuple[list[dict], list[dict], list[str]]:
    nodes: list[dict] = []
    edges: list[dict] = []
    graph_path: list[str] = []

    material_nodes = [f"material:{m.get('material_family')}" for m in retrieval["matched_materials"]]

    for item in retrieval["future_horizon"]:
        knowledge_id = item.get("knowledge_id", "")
        topic = item.get("topic", "future horizon")
        topic_key = _normalise(topic).replace(" ", "_")
        future_id = f"future:{topic_key}"
        maturity = item.get("maturity", "emerging")
        confidence = item.get("confidence", "unknown")

        nodes.append(
            _node(
                future_id,
                topic,
                "future_horizon",
                f"Future-watch topic. Maturity: {maturity}. Confidence: {confidence}.",
                knowledge_id,
            )
        )

        related = {_normalise(value) for value in item.get("related_material_families", [])}
        linked_any_material = False
        for material in retrieval["matched_materials"]:
            family = _normalise(material.get("material_family"))
            if family in related:
                material_id = f"material:{material.get('material_family')}"
                edges.append(
                    _edge(
                        material_id,
                        future_id,
                        "has_future_watch_route",
                        "knowledge_base",
                        "Future-watch relationship is not an operational recommendation.",
                    )
                )
                linked_any_material = True
                graph_path.append(f"{material_id} -> future watch: {topic}")

        if not linked_any_material and "cross_material" in related:
            for material_id in material_nodes:
                edges.append(
                    _edge(
                        material_id,
                        future_id,
                        "has_cross_material_future_watch",
                        "knowledge_base",
                        "Cross-material future-watch item supports data-readiness planning only.",
                    )
                )

        for do_not_claim in item.get("do_not_claim", []):
            unsafe_id = f"unsafe_claim:{topic_key}:{_normalise(do_not_claim).replace(' ', '_')}"
            nodes.append(_node(unsafe_id, do_not_claim, "unsafe_claim", "Future-watch claim boundary.", knowledge_id))
            edges.append(_edge(future_id, unsafe_id, "must_not_claim", "knowledge_base"))

    return nodes, edges, graph_path


def _dedupe_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for node in nodes:
        node_id = node["node_id"]
        if node_id in seen:
            continue
        seen.add(node_id)
        output.append(node)
    return output


def _dedupe_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    output: list[dict[str, Any]] = []
    for edge in edges:
        key = (edge["source"], edge["target"], edge["relationship"])
        if key in seen:
            continue
        seen.add(key)
        output.append(edge)
    return output


def build_knowledge_graph_catalog() -> dict[str, Any]:
    """Build a lightweight catalog graph of all knowledge-base records."""
    validation = validate_knowledge_base()
    materials = load_collection("materials")
    routes = load_collection("circular_routes")
    evidence_rules = load_collection("evidence_rules")
    future_horizon = load_collection("future_horizon")

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for material in materials:
        family = material.get("material_family", "unknown")
        material_id = f"material:{family}"
        nodes.append(_node(material_id, family, "material_family", "Knowledge-base material family.", material.get("knowledge_id")))

        route_terms = " ".join(material.get("available_now_routes", []) + material.get("pilot_ready_routes", [])).lower()
        for route in routes:
            route_name = route.get("route", "")
            route_label = route_name.replace("_", " ")
            if route_name and (route_name.replace("_", " ") in route_terms or route_label in route_terms):
                route_id = f"route:{route_name}"
                nodes.append(_node(route_id, route_label, "circular_route", "Knowledge-base route.", route.get("knowledge_id")))
                edges.append(_edge(material_id, route_id, "can_link_to_route", "knowledge_base"))

    for rule in evidence_rules:
        rule_name = rule.get("rule_name", "evidence_rule")
        nodes.append(_node(f"evidence_rule:{rule_name}", rule_name.replace("_", " "), "evidence_rule", "Knowledge-base evidence rule.", rule.get("knowledge_id")))

    for future in future_horizon:
        topic = future.get("topic", "future horizon")
        future_id = f"future:{_normalise(topic).replace(' ', '_')}"
        nodes.append(_node(future_id, topic, "future_horizon", f"Maturity: {future.get('maturity')}.", future.get("knowledge_id")))
        for family in future.get("related_material_families", []):
            if _normalise(family) == "cross_material":
                continue
            edges.append(_edge(f"material:{family}", future_id, "can_link_to_future_watch", "knowledge_base"))

    return {
        "graph_scope": "knowledge_catalog",
        "stream_id": None,
        "nodes": _dedupe_nodes(nodes),
        "edges": _dedupe_edges(edges),
        "graph_path": [],
        "matched_material_families": [],
        "source_knowledge_ids": _dedupe(
            [item.get("knowledge_id", "") for item in materials + routes + evidence_rules + future_horizon]
        ),
        "retrieval_notes": [],
        "knowledge_validation": validation,
        "governance_note": (
            "Knowledge graph catalog shows relationships available in the controlled knowledge base. "
            "It does not verify site-specific route feasibility, supplier acceptance, compliance or impact."
        ),
    }


def build_stream_knowledge_graph(stream: Any) -> dict[str, Any]:
    """Build a relationship graph for one raw or existing stream."""
    retrieval = retrieve_knowledge_for_stream(stream)

    stream_id = _text(stream, "stream_id") or retrieval.get("stream_id") or "unknown"
    stream_label = _text(stream, "stream_name") or "Unknown stream"
    stream_node_id = f"stream:{stream_id}"

    nodes: list[dict[str, Any]] = [
        _node(
            stream_node_id,
            stream_label,
            "stream",
            f"Raw operational stream. Material: {_text(stream, 'material')}. Process: {_text(stream, 'source_process')}.",
            None,
        )
    ]
    edges: list[dict[str, Any]] = []
    graph_path: list[str] = [f"stream: {stream_id}"]

    for builder in [
        lambda: _material_graph_nodes_and_edges(stream_node_id, retrieval),
        lambda: _route_graph_nodes_and_edges(retrieval),
        lambda: _evidence_rule_nodes_and_edges(retrieval),
        lambda: _future_nodes_and_edges(retrieval),
    ]:
        new_nodes, new_edges, new_path = builder()
        nodes.extend(new_nodes)
        edges.extend(new_edges)
        graph_path.extend(new_path)

    source_knowledge_ids = _dedupe(
        [
            record.get("knowledge_id", "")
            for record in (
                retrieval["matched_materials"]
                + retrieval["matched_routes"]
                + retrieval["evidence_rules"]
                + retrieval["future_horizon"]
            )
        ]
    )

    return {
        "graph_scope": "stream_match",
        "stream_id": stream_id,
        "nodes": _dedupe_nodes(nodes),
        "edges": _dedupe_edges(edges),
        "graph_path": _dedupe(graph_path),
        "matched_material_families": _dedupe([item.get("material_family", "") for item in retrieval["matched_materials"]]),
        "source_knowledge_ids": source_knowledge_ids,
        "retrieval_notes": retrieval["retrieval_notes"],
        "knowledge_validation": retrieval["knowledge_validation"],
        "governance_note": (
            "Stream knowledge graph explains retrieved relationships behind advisory intelligence. "
            "It is a relationship map for screening and traceability, not proof of route feasibility, "
            "supplier acceptance, legal compliance, verified diversion, carbon saving or financial saving."
        ),
    }
