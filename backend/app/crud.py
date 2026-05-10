"""Database read/write helpers."""

from __future__ import annotations

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
