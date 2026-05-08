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
