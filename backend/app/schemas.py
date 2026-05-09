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


# Milestone 4: advanced agentic decision-support schemas

class AgenticReviewPack(BaseModel):
    stream_id: str
    stream_name: str
    material: str
    decision_locked_by_rules: bool
    rule_applied: str
    base_recommendation: dict
    executive_synthesis: dict
    evidence_audit: dict
    risk_review: dict
    procurement_review: dict
    industrial_symbiosis_review: dict
    resource_efficiency_review: dict


class AgenticManagementSummary(BaseModel):
    decision_source: str
    total_recommendations: int
    human_review_required: int
    risk_breakdown: dict
    strategy_breakdown: dict
    high_priority_count: int
    low_evidence_count: int
    estimated_annual_waste_diverted_kg: float
    estimated_annual_disposal_cost_avoided: float
    executive_summary: str
    top_cost_avoidance_candidates: list[dict]
    portfolio_note: str


class AgenticActionPlan(BaseModel):
    ranking_method: str
    phases: dict
    governance_note: str


# Milestone 7: evidence register and export schemas

class EvidenceRegisterRecord(BaseModel):
    stream_id: str
    stream_name: str
    material: str
    department: str
    supplier: str
    recommended_circular_action: str
    circular_strategy_category: str
    rule_applied: str
    risk_level: str
    human_review_required: bool
    confidence_score: int
    evidence_quality_score: int
    evidence_status: str
    review_gate: str
    claim_readiness: str
    measured_data: str
    estimated_data: str
    assumptions: str
    missing_data: str
    risk_triggers: str
    review_gates: str
    claim_boundary: str
    next_action: str
    estimated_annual_waste_diverted_kg: float
    estimated_annual_disposal_cost_avoided: float


class EvidenceRegisterSummary(BaseModel):
    total_records: int
    human_review_required: int
    low_evidence_records: int
    strong_evidence_records: int
    records_with_missing_data: int
    evidence_status_breakdown: dict
    claim_readiness_breakdown: dict
    governance_note: str
