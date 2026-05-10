"""Database read/write helpers."""

from __future__ import annotations

import json

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app import models, schemas


def create_stream(db: Session, stream: schemas.IndustrialStreamCreate) -> models.IndustrialStream:
    db_stream = models.IndustrialStream(**stream.model_dump())
    db.add(db_stream)
    db.commit()
    db.refresh(db_stream)
    return db_stream


def bulk_replace_streams(db: Session, streams: list[schemas.IndustrialStreamCreate]) -> int:
    db.execute(delete(models.CircularRecommendation))
    db.execute(delete(models.IndustrialStream))
    db.add_all([models.IndustrialStream(**stream.model_dump()) for stream in streams])
    db.commit()
    return len(streams)


def get_streams(
    db: Session,
    *,
    material: str | None = None,
    department: str | None = None,
    hazardous_flag: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[models.IndustrialStream]:
    query = select(models.IndustrialStream).order_by(models.IndustrialStream.stream_id)

    if material:
        query = query.where(func.lower(models.IndustrialStream.material) == material.lower())
    if department:
        query = query.where(func.lower(models.IndustrialStream.department) == department.lower())
    if hazardous_flag:
        query = query.where(func.lower(models.IndustrialStream.hazardous_flag) == hazardous_flag.lower())

    query = query.offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_stream_by_stream_id(db: Session, stream_id: str) -> models.IndustrialStream | None:
    query = select(models.IndustrialStream).where(models.IndustrialStream.stream_id == stream_id)
    return db.scalars(query).first()


def get_stream_summary(db: Session) -> schemas.StreamSummary:
    streams = list(db.scalars(select(models.IndustrialStream)).all())
    total_monthly_quantity = sum(stream.monthly_quantity_kg for stream in streams)
    total_monthly_cost = sum(stream.disposal_cost_per_month for stream in streams)
    hazardous_count = sum(1 for stream in streams if str(stream.hazardous_flag).lower() == "true")
    unknown_hazard_count = sum(1 for stream in streams if str(stream.hazardous_flag).lower() == "unknown")

    return schemas.StreamSummary(
        total_streams=len(streams),
        total_monthly_quantity_kg=round(total_monthly_quantity, 2),
        total_annual_quantity_kg=round(total_monthly_quantity * 12, 2),
        total_monthly_disposal_cost=round(total_monthly_cost, 2),
        total_annual_disposal_cost=round(total_monthly_cost * 12, 2),
        hazardous_streams=hazardous_count,
        unknown_hazard_status_streams=unknown_hazard_count,
    )


def bulk_replace_recommendations(
    db: Session,
    recommendations: list[schemas.CircularRecommendationCreate],
) -> int:
    """Replace all circular recommendations with a newly generated rules run."""
    db.execute(delete(models.CircularRecommendation))
    db.add_all([models.CircularRecommendation(**rec.model_dump()) for rec in recommendations])
    db.commit()
    return len(recommendations)


def get_recommendations(
    db: Session,
    *,
    risk_level: str | None = None,
    circular_strategy_category: str | None = None,
    human_review_required: bool | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[models.CircularRecommendation]:
    query = select(models.CircularRecommendation).order_by(models.CircularRecommendation.stream_id)

    if risk_level:
        query = query.where(func.lower(models.CircularRecommendation.risk_level) == risk_level.lower())
    if circular_strategy_category:
        query = query.where(
            func.lower(models.CircularRecommendation.circular_strategy_category)
            == circular_strategy_category.lower()
        )
    if human_review_required is not None:
        query = query.where(models.CircularRecommendation.human_review_required == human_review_required)

    query = query.offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_recommendation_by_stream_id(
    db: Session,
    stream_id: str,
) -> models.CircularRecommendation | None:
    query = select(models.CircularRecommendation).where(
        models.CircularRecommendation.stream_id == stream_id
    )
    return db.scalars(query).first()


def get_recommendation_summary(db: Session) -> schemas.RecommendationSummary:
    recs = list(db.scalars(select(models.CircularRecommendation)).all())
    return schemas.RecommendationSummary(
        total_recommendations=len(recs),
        human_review_required=sum(1 for rec in recs if rec.human_review_required),
        low_risk=sum(1 for rec in recs if rec.risk_level == "low"),
        medium_risk=sum(1 for rec in recs if rec.risk_level == "medium"),
        high_risk=sum(1 for rec in recs if rec.risk_level == "high"),
        blocked=sum(1 for rec in recs if rec.risk_level == "blocked"),
        total_estimated_annual_waste_diverted_kg=round(
            sum(rec.estimated_annual_waste_diverted_kg for rec in recs), 2
        ),
        total_estimated_annual_disposal_cost_avoided=round(
            sum(rec.estimated_annual_disposal_cost_avoided for rec in recs), 2
        ),
    )


# Milestone 9D: product data-model foundation CRUD helpers

def ensure_default_workspace(db: Session) -> tuple[models.Organisation, models.Site]:
    """Ensure a default organisation and site exist for the current Alpha workflow."""
    organisation = db.scalars(
        select(models.Organisation).where(models.Organisation.organisation_name == "Default Organisation")
    ).first()

    if organisation is None:
        organisation = models.Organisation(
            organisation_name="Default Organisation",
            sector="manufacturing",
            region="unspecified",
        )
        db.add(organisation)
        db.commit()
        db.refresh(organisation)

    site = db.scalars(
        select(models.Site).where(
            models.Site.organisation_id == organisation.id,
            models.Site.site_name == "Default Manufacturing Site",
        )
    ).first()

    if site is None:
        site = models.Site(
            organisation_id=organisation.id,
            site_name="Default Manufacturing Site",
            site_type="manufacturing",
            country="unspecified",
        )
        db.add(site)
        db.commit()
        db.refresh(site)

    return organisation, site


def create_analysis_run_snapshot(
    db: Session,
    *,
    organisation_id: int,
    site_id: int,
) -> models.AnalysisRun:
    """Create a metadata snapshot of the current loaded streams and recommendations."""
    stream_summary = get_stream_summary(db)
    recommendation_summary = get_recommendation_summary(db)

    existing_count = db.scalar(
        select(func.count(models.AnalysisRun.id)).where(models.AnalysisRun.site_id == site_id)
    ) or 0

    snapshot = models.AnalysisRun(
        organisation_id=organisation_id,
        site_id=site_id,
        run_name=f"Analysis snapshot {existing_count + 1}",
        run_status="snapshot_created",
        decision_source="locked_rules_engine",
        stream_count=stream_summary.total_streams,
        recommendation_count=recommendation_summary.total_recommendations,
        human_review_required_count=recommendation_summary.human_review_required,
        low_risk_count=recommendation_summary.low_risk,
        medium_risk_count=recommendation_summary.medium_risk,
        high_risk_count=recommendation_summary.high_risk,
        blocked_count=recommendation_summary.blocked,
        total_estimated_annual_waste_diverted_kg=recommendation_summary.total_estimated_annual_waste_diverted_kg,
        total_estimated_annual_disposal_cost_avoided=recommendation_summary.total_estimated_annual_disposal_cost_avoided,
        governance_note=(
            "Analysis-run metadata is a snapshot of current Alpha workflow outputs. It does not verify "
            "legal compliance, supplier capability, carbon savings, financial savings or operational impact."
        ),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_latest_analysis_run(db: Session, *, site_id: int) -> models.AnalysisRun | None:
    query = (
        select(models.AnalysisRun)
        .where(models.AnalysisRun.site_id == site_id)
        .order_by(models.AnalysisRun.created_at.desc(), models.AnalysisRun.id.desc())
        .limit(1)
    )
    return db.scalars(query).first()


def get_analysis_runs(db: Session, *, site_id: int, limit: int = 50) -> list[models.AnalysisRun]:
    query = (
        select(models.AnalysisRun)
        .where(models.AnalysisRun.site_id == site_id)
        .order_by(models.AnalysisRun.created_at.desc(), models.AnalysisRun.id.desc())
        .limit(limit)
    )
    return list(db.scalars(query).all())


# Milestone 9E: audit and traceability CRUD helpers

def _audit_read(event: models.AuditEvent) -> schemas.AuditEventRead:
    """Convert an AuditEvent ORM row into a schema with parsed metadata."""
    try:
        metadata = json.loads(event.metadata_json or "{}")
    except json.JSONDecodeError:
        metadata = {"raw_metadata_json": event.metadata_json}

    return schemas.AuditEventRead(
        id=event.id,
        event_type=event.event_type,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        actor_type=event.actor_type,
        actor_id=event.actor_id,
        source=event.source,
        action=event.action,
        summary=event.summary,
        decision_source=event.decision_source,
        claim_boundary=event.claim_boundary,
        metadata_json=metadata,
        created_at=event.created_at,
    )


def create_audit_event(
    db: Session,
    *,
    event_type: str,
    entity_type: str,
    entity_id: str | None,
    actor_type: str = "system",
    actor_id: str | None = None,
    source: str,
    action: str,
    summary: str,
    decision_source: str,
    claim_boundary: str,
    metadata: dict | None = None,
) -> schemas.AuditEventRead:
    """Create and return a traceable audit event."""
    event = models.AuditEvent(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_type=actor_type,
        actor_id=actor_id,
        source=source,
        action=action,
        summary=summary,
        decision_source=decision_source,
        claim_boundary=claim_boundary,
        metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return _audit_read(event)


def get_audit_events(
    db: Session,
    *,
    event_type: str | None = None,
    entity_type: str | None = None,
    limit: int = 100,
) -> list[schemas.AuditEventRead]:
    query = select(models.AuditEvent).order_by(models.AuditEvent.created_at.desc(), models.AuditEvent.id.desc())

    if event_type:
        query = query.where(func.lower(models.AuditEvent.event_type) == event_type.lower())
    if entity_type:
        query = query.where(func.lower(models.AuditEvent.entity_type) == entity_type.lower())

    query = query.limit(limit)
    return [_audit_read(event) for event in db.scalars(query).all()]


def get_audit_summary(db: Session) -> schemas.AuditSummary:
    events = list(
        db.scalars(
            select(models.AuditEvent)
            .order_by(models.AuditEvent.created_at.desc(), models.AuditEvent.id.desc())
            .limit(500)
        ).all()
    )

    def breakdown(attribute: str) -> dict:
        result: dict[str, int] = {}
        for event in events:
            value = getattr(event, attribute) or "unknown"
            result[value] = result.get(value, 0) + 1
        return result

    return schemas.AuditSummary(
        total_events=len(events),
        event_type_breakdown=breakdown("event_type"),
        entity_type_breakdown=breakdown("entity_type"),
        decision_source_breakdown=breakdown("decision_source"),
        latest_events=[_audit_read(event) for event in events[:10]],
        governance_note=(
            "Audit events record workflow traceability. They do not independently verify legal compliance, "
            "supplier capability, carbon savings, financial savings or completed operational impact."
        ),
    )


# Milestone 10E: generated insight history CRUD helpers

def _json_dump(value) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False)


def _json_load(value: str, fallback):
    try:
        return json.loads(value or "")
    except (json.JSONDecodeError, TypeError):
        return fallback


def _generated_insight_read(row: models.GeneratedInsight) -> schemas.GeneratedInsightRead:
    return schemas.GeneratedInsightRead(
        id=row.id,
        stream_id=row.stream_id,
        stream_name=row.stream_name,
        material=row.material,
        source_process=row.source_process,
        analysis_run_id=row.analysis_run_id,
        input_snapshot=_json_load(row.input_snapshot_json, {}),
        input_notes_present=row.input_notes_present,
        notes_dependency=row.notes_dependency,
        insight_summary=row.insight_summary,
        matched_material_families=_json_load(row.matched_material_families_json, []),
        current_action=_json_load(row.current_action_json, {}),
        near_future_action=_json_load(row.near_future_action_json, {}),
        future_watch=_json_load(row.future_watch_json, {}),
        evidence_needed=_json_load(row.evidence_needed_json, []),
        supplier_questions=_json_load(row.supplier_questions_json, []),
        human_review_triggers=_json_load(row.human_review_triggers_json, []),
        do_not_claim=_json_load(row.do_not_claim_json, []),
        claim_boundary=row.claim_boundary,
        source_knowledge_ids=_json_load(row.source_knowledge_ids_json, []),
        retrieval_notes=_json_load(row.retrieval_notes_json, []),
        generation_mode=row.generation_mode,
        governance_note=row.governance_note,
        created_at=row.created_at,
    )


def create_generated_insight(
    db: Session,
    *,
    insight: dict,
    input_snapshot: dict,
    analysis_run_id: int | None = None,
    generation_mode: str = "deterministic",
) -> schemas.GeneratedInsightRead:
    """Persist one generated autonomous insight."""

    row = models.GeneratedInsight(
        stream_id=insight.get("stream_id") or "unknown",
        stream_name=insight.get("stream_name") or "",
        material=insight.get("material") or "",
        source_process=insight.get("source_process") or "",
        analysis_run_id=analysis_run_id,
        input_snapshot_json=_json_dump(input_snapshot),
        matched_material_families_json=_json_dump(insight.get("matched_material_families", [])),
        current_action_json=_json_dump(insight.get("current_action", {})),
        near_future_action_json=_json_dump(insight.get("near_future_action", {})),
        future_watch_json=_json_dump(insight.get("future_watch", {})),
        evidence_needed_json=_json_dump(insight.get("evidence_needed", [])),
        supplier_questions_json=_json_dump(insight.get("supplier_questions", [])),
        human_review_triggers_json=_json_dump(insight.get("human_review_triggers", [])),
        do_not_claim_json=_json_dump(insight.get("do_not_claim", [])),
        source_knowledge_ids_json=_json_dump(insight.get("source_knowledge_ids", [])),
        retrieval_notes_json=_json_dump(insight.get("retrieval_notes", [])),
        input_notes_present=bool(insight.get("input_notes_present", False)),
        notes_dependency=insight.get("notes_dependency", "unknown"),
        insight_summary=insight.get("insight_summary", ""),
        claim_boundary=insight.get("claim_boundary", ""),
        generation_mode=generation_mode,
        governance_note=insight.get("governance_note", ""),
    )

    db.add(row)
    db.commit()
    db.refresh(row)
    return _generated_insight_read(row)


def get_generated_insights(
    db: Session,
    *,
    limit: int = 100,
) -> list[schemas.GeneratedInsightRead]:
    query = (
        select(models.GeneratedInsight)
        .order_by(models.GeneratedInsight.created_at.desc(), models.GeneratedInsight.id.desc())
        .limit(limit)
    )
    return [_generated_insight_read(row) for row in db.scalars(query).all()]


def get_generated_insights_by_stream_id(
    db: Session,
    *,
    stream_id: str,
    limit: int = 50,
) -> list[schemas.GeneratedInsightRead]:
    query = (
        select(models.GeneratedInsight)
        .where(models.GeneratedInsight.stream_id == stream_id)
        .order_by(models.GeneratedInsight.created_at.desc(), models.GeneratedInsight.id.desc())
        .limit(limit)
    )
    return [_generated_insight_read(row) for row in db.scalars(query).all()]


def get_latest_generated_insight_by_stream_id(
    db: Session,
    *,
    stream_id: str,
) -> schemas.GeneratedInsightRead | None:
    query = (
        select(models.GeneratedInsight)
        .where(models.GeneratedInsight.stream_id == stream_id)
        .order_by(models.GeneratedInsight.created_at.desc(), models.GeneratedInsight.id.desc())
        .limit(1)
    )
    row = db.scalars(query).first()
    return _generated_insight_read(row) if row else None
