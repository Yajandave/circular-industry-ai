"""Pydantic schemas used by the API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IndustrialStreamBase(BaseModel):
    stream_id: str = Field(..., examples=["S001"])
    stream_name: str
    material: str
    source_process: str
    monthly_quantity_kg: float
    current_route: str
    disposal_cost_per_month: float
    contamination_risk: str
    hazardous_flag: str
    department: str
    supplier: str
    supplier_takeback_available: str
    recycled_content_available: str
    notes: Optional[str] = None


class IndustrialStreamCreate(IndustrialStreamBase):
    pass


class IndustrialStreamRead(IndustrialStreamBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoadSampleResponse(BaseModel):
    loaded_rows: int
    replaced_existing_rows: bool
    message: str


class StreamSummary(BaseModel):
    total_streams: int
    total_monthly_quantity_kg: float
    total_annual_quantity_kg: float
    total_monthly_disposal_cost: float
    total_annual_disposal_cost: float
    hazardous_streams: int
    unknown_hazard_status_streams: int
