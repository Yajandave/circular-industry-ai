"""SQLAlchemy models for industrial material and waste streams."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class IndustrialStream(Base):
    """Industrial material, waste or by-product stream uploaded for analysis."""

    __tablename__ = "industrial_streams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stream_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    stream_name: Mapped[str] = mapped_column(String(255), nullable=False)
    material: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    source_process: Mapped[str] = mapped_column(String(160), nullable=False)
    monthly_quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    current_route: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    disposal_cost_per_month: Mapped[float] = mapped_column(Float, nullable=False)
    contamination_risk: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    hazardous_flag: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    supplier: Mapped[str] = mapped_column(String(160), nullable=False)
    supplier_takeback_available: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    recycled_content_available: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CircularRecommendation(Base):
    """Rules-based circular economy recommendation for one industrial stream."""

    __tablename__ = "circular_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stream_id: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    recommended_circular_action: Mapped[str] = mapped_column(String(255), nullable=False)
    circular_strategy_category: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_quality_score: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_data: Mapped[str] = mapped_column(Text, nullable=False)
    human_review_required: Mapped[bool] = mapped_column(nullable=False)
    estimated_annual_waste_diverted_kg: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_annual_disposal_cost_avoided: Mapped[float] = mapped_column(Float, nullable=False)
    supplier_procurement_action: Mapped[str] = mapped_column(Text, nullable=False)
    industrial_symbiosis_opportunity: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    next_action: Mapped[str] = mapped_column(Text, nullable=False)
    dashboard_priority: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    rule_applied: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
