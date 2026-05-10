"""Controlled agentic retrieval workflow.

This module orchestrates a deterministic multi-step workflow:
raw stream data -> knowledge retrieval -> relationship graph -> insight generation -> optional persistence.

It is "agentic" because it runs a staged reasoning workflow.
It is not autonomous decision-making: the rules engine and governance boundaries remain locked.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.insight_generator.service import generate_autonomous_insight
from app.insight_history.service import persist_autonomous_insight
from app.knowledge_base.retriever import retrieve_knowledge_for_stream
from app.knowledge_graph.service import build_stream_knowledge_graph


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
    output: list[str] = []
    for value in values:
        cleaned = str(value or "").strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(cleaned)
    return output


def _step(
    *,
    step_id: str,
    name: str,
    status: str,
    summary: str,
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
    governance_note: str = "",
) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "name": name,
        "status": status,
        "summary": summary,
        "inputs": inputs or [],
        "outputs": outputs or [],
        "governance_note": governance_note,
    }


def _classify_stream_context(stream: Any) -> dict[str, Any]:
    material = _normalise(_text(stream, "material"))
    contamination = _normalise(_text(stream, "contamination_risk"))
    hazardous = _normalise(_text(stream, "hazardous_flag"))
    supplier_takeback = _normalise(_text(stream, "supplier_takeback_available"))
    recycled_content = _normalise(_text(stream, "recycled_content_available"))
    notes_present = bool(_text(stream, "notes"))

    risk_flags: list[str] = []
    if hazardous in {"true", "unknown"}:
        risk_flags.append("hazardous status true or unknown")
    if contamination == "high":
        risk_flags.append("high contamination")
    if supplier_takeback in {"unknown", ""}:
        risk_flags.append("supplier take-back availability unknown")
    if recycled_content in {"unknown", ""}:
        risk_flags.append("recycled-content availability unknown")

    return {
        "stream_id": _text(stream, "stream_id") or "unknown",
        "material": material,
        "source_process": _text(stream, "source_process"),
        "contamination_risk": contamination or "unknown",
        "hazardous_flag": hazardous or "unknown",
        "supplier_takeback_available": supplier_takeback or "unknown",
        "recycled_content_available": recycled_content or "unknown",
        "input_notes_present": notes_present,
        "notes_dependency": "not_required",
        "risk_flags": risk_flags,
        "classification_summary": (
            "Stream context classified from structured fields. Notes are recorded as present/absent "
            "but are not required for workflow execution."
        ),
    }


def _relationship_summary(graph: dict[str, Any]) -> dict[str, Any]:
    node_types: dict[str, int] = {}
    edge_types: dict[str, int] = {}

    for node in graph.get("nodes", []):
        node_type = node.get("node_type", "unknown")
        node_types[node_type] = node_types.get(node_type, 0) + 1

    for edge in graph.get("edges", []):
        relationship = edge.get("relationship", "unknown")
        edge_types[relationship] = edge_types.get(relationship, 0) + 1

    return {
        "node_type_breakdown": node_types,
        "relationship_breakdown": edge_types,
        "graph_path_count": len(graph.get("graph_path", [])),
    }


def _workflow_quality_gates(context: dict[str, Any], retrieval: dict[str, Any], graph: dict[str, Any], insight: dict[str, Any]) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []

    matched_materials = retrieval.get("matched_materials", [])
    source_ids = set(insight.get("source_knowledge_ids", []))
    families = set(insight.get("matched_material_families", []))

    gates.append(
        {
            "gate": "notes_independence",
            "status": "pass" if insight.get("notes_dependency") == "not_required" else "review",
            "detail": "Insight generation does not require pre-written dataset notes.",
        }
    )

    gates.append(
        {
            "gate": "material_match",
            "status": "pass" if matched_materials else "review",
            "detail": f"Matched material families: {', '.join(sorted(families)) if families else 'none'}",
        }
    )

    if "plastics" in families:
        false_positive = any(item in source_ids for item in {"future_battery_recycling_v1", "material_batteries_v1", "material_cardboard_packaging_v1"})
        gates.append(
            {
                "gate": "false_positive_control",
                "status": "pass" if not false_positive else "fail",
                "detail": "Plastics stream should not pull battery/cardboard future routes.",
            }
        )

    review_needed = bool(context.get("risk_flags")) or bool(insight.get("human_review_triggers"))
    gates.append(
        {
            "gate": "human_review_control",
            "status": "review" if review_needed else "pass",
            "detail": "Review required when risk flags or human-review triggers are present.",
        }
    )

    gates.append(
        {
            "gate": "claim_boundary_present",
            "status": "pass" if insight.get("claim_boundary") else "fail",
            "detail": "Insight must include a claim boundary.",
        }
    )

    gates.append(
        {
            "gate": "graph_relationships_present",
            "status": "pass" if graph.get("nodes") and graph.get("edges") else "review",
            "detail": "Workflow should produce graph nodes and edges for traceability.",
        }
    )

    return gates


def run_agentic_retrieval_workflow(
    stream: Any,
    *,
    db: Session | None = None,
    save_insight: bool = False,
) -> dict[str, Any]:
    """Run the deterministic agentic retrieval workflow for raw or existing stream input."""
    workflow_id = f"workflow_{uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()

    context = _classify_stream_context(stream)
    retrieval = retrieve_knowledge_for_stream(stream)
    graph = build_stream_knowledge_graph(stream)
    insight = generate_autonomous_insight(stream)

    saved_insight = None
    if save_insight:
        if db is None:
            raise ValueError("db session is required when save_insight=True")
        saved_insight = persist_autonomous_insight(db, stream=stream, insight=insight)

    steps = [
        _step(
            step_id="01_classify_stream_context",
            name="Classify stream context",
            status="completed",
            summary=context["classification_summary"],
            inputs=["stream_id", "material", "source_process", "contamination_risk", "hazardous_flag", "supplier fields", "notes presence"],
            outputs=["risk_flags", "notes_dependency", "structured stream context"],
        ),
        _step(
            step_id="02_retrieve_knowledge",
            name="Retrieve controlled knowledge",
            status="completed" if retrieval.get("matched_materials") else "review",
            summary="Retrieved material, route, evidence-rule and future-horizon knowledge for the stream.",
            inputs=["structured stream fields"],
            outputs=[
                f"{len(retrieval.get('matched_materials', []))} material matches",
                f"{len(retrieval.get('matched_routes', []))} route matches",
                f"{len(retrieval.get('evidence_rules', []))} evidence rules",
                f"{len(retrieval.get('future_horizon', []))} future-watch items",
            ],
            governance_note="Retrieval supports advisory intelligence. It does not verify operational feasibility.",
        ),
        _step(
            step_id="03_build_relationship_graph",
            name="Build knowledge relationship graph",
            status="completed" if graph.get("nodes") and graph.get("edges") else "review",
            summary="Mapped stream, material, route, evidence, unsafe-claim and future-watch relationships.",
            inputs=["retrieved knowledge"],
            outputs=[f"{len(graph.get('nodes', []))} nodes", f"{len(graph.get('edges', []))} edges"],
            governance_note="Graph relationships explain context; they are not proof of compliance or impact.",
        ),
        _step(
            step_id="04_generate_autonomous_insight",
            name="Generate autonomous insight",
            status="completed",
            summary="Generated current action, near-future action, future watch, evidence needs, supplier questions and claim controls.",
            inputs=["structured stream fields", "retrieved knowledge", "graph context"],
            outputs=["current_action", "near_future_action", "future_watch", "evidence_needed", "supplier_questions", "do_not_claim"],
            governance_note="Generated insight is advisory and deterministic.",
        ),
        _step(
            step_id="05_persist_and_audit",
            name="Persist and audit insight",
            status="completed" if saved_insight else "skipped",
            summary="Saved generated insight and created audit event." if saved_insight else "Persistence skipped for stateless workflow run.",
            inputs=["generated insight"],
            outputs=[f"generated_insight_id={saved_insight.id}"] if saved_insight else [],
            governance_note="Saved records remain advisory unless validated by evidence and human review.",
        ),
    ]

    quality_gates = _workflow_quality_gates(context, retrieval, graph, insight)

    source_knowledge_ids = _dedupe(
        retrieval_ids := [
            record.get("knowledge_id", "")
            for record in (
                retrieval.get("matched_materials", [])
                + retrieval.get("matched_routes", [])
                + retrieval.get("evidence_rules", [])
                + retrieval.get("future_horizon", [])
            )
        ]
    )

    return {
        "workflow_id": workflow_id,
        "workflow_name": "rules_locked_agentic_retrieval_workflow",
        "workflow_mode": "deterministic",
        "stream_id": context["stream_id"],
        "created_at": created_at,
        "save_insight": save_insight,
        "saved_insight_id": saved_insight.id if saved_insight else None,
        "stream_context": context,
        "steps": steps,
        "quality_gates": quality_gates,
        "retrieval_summary": {
            "matched_material_families": insight.get("matched_material_families", []),
            "matched_route_count": len(retrieval.get("matched_routes", [])),
            "evidence_rule_count": len(retrieval.get("evidence_rules", [])),
            "future_horizon_count": len(retrieval.get("future_horizon", [])),
            "source_knowledge_ids": source_knowledge_ids,
            "retrieval_notes": retrieval.get("retrieval_notes", []),
        },
        "relationship_summary": _relationship_summary(graph),
        "graph": graph,
        "insight": insight,
        "governance_note": (
            "Agentic retrieval workflow is deterministic and rules-locked. It orchestrates classification, retrieval, "
            "relationship mapping, insight generation and optional persistence. It does not verify legal compliance, "
            "supplier acceptance, circularity claims, carbon savings, financial savings or operational impact."
        ),
    }
