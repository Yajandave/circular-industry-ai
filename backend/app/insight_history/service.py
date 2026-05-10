"""Persistence service for generated autonomous insights."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app import crud, schemas


STREAM_SNAPSHOT_FIELDS = [
    "stream_id",
    "stream_name",
    "material",
    "source_process",
    "monthly_quantity_kg",
    "current_route",
    "disposal_cost_per_month",
    "contamination_risk",
    "hazardous_flag",
    "department",
    "supplier",
    "supplier_takeback_available",
    "recycled_content_available",
    "notes",
]


def _get(record: Any, field: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(field, default)
    return getattr(record, field, default)


def build_input_snapshot(stream: Any) -> dict[str, Any]:
    """Build an auditable snapshot of the stream input used for insight generation."""
    return {field: _get(stream, field) for field in STREAM_SNAPSHOT_FIELDS}


def persist_autonomous_insight(
    db: Session,
    *,
    stream: Any,
    insight: dict[str, Any],
    generation_mode: str = "deterministic",
) -> schemas.GeneratedInsightRead:
    """Store a generated insight and create an audit event."""

    organisation, site = crud.ensure_default_workspace(db)
    latest_run = crud.get_latest_analysis_run(db, site_id=site.id)

    stored = crud.create_generated_insight(
        db,
        insight=insight,
        input_snapshot=build_input_snapshot(stream),
        analysis_run_id=latest_run.id if latest_run else None,
        generation_mode=generation_mode,
    )

    crud.create_audit_event(
        db,
        event_type="insight_generated",
        entity_type="stream",
        entity_id=stored.stream_id,
        actor_type="system",
        source="autonomous_insight_generator",
        action="generate_and_save_insight",
        summary=(
            f"Generated and saved deterministic autonomous insight for {stored.stream_id}. "
            f"Notes dependency: {stored.notes_dependency}."
        ),
        decision_source="deterministic_knowledge_retrieval",
        claim_boundary=stored.claim_boundary,
        metadata={
            "generated_insight_id": stored.id,
            "analysis_run_id": stored.analysis_run_id,
            "source_knowledge_ids": stored.source_knowledge_ids,
            "input_notes_present": stored.input_notes_present,
            "notes_dependency": stored.notes_dependency,
            "generation_mode": stored.generation_mode,
        },
    )

    return stored
