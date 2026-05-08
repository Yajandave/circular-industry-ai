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
