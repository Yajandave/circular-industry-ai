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


class CircularRecommendationBase(BaseModel):
    stream_id: str = Field(..., examples=["S001"])
    recommended_circular_action: str
    circular_strategy_category: str
    reasoning: str
    risk_level: str
    confidence_score: int
    evidence_quality_score: int
    missing_data: str
    human_review_required: bool
    estimated_annual_waste_diverted_kg: float
    estimated_annual_disposal_cost_avoided: float
    supplier_procurement_action: str
    industrial_symbiosis_opportunity: str
    next_action: str
    dashboard_priority: str
    rule_applied: str


class CircularRecommendationCreate(CircularRecommendationBase):
    pass


class CircularRecommendationRead(CircularRecommendationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RunRecommendationsResponse(BaseModel):
    analysed_streams: int
    recommendations_created: int
    human_review_required: int
    high_priority_items: int
    message: str


class RecommendationSummary(BaseModel):
    total_recommendations: int
    human_review_required: int
    low_risk: int
    medium_risk: int
    high_risk: int
    blocked: int
    total_estimated_annual_waste_diverted_kg: float
    total_estimated_annual_disposal_cost_avoided: float
