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


# Milestone 7B: circular resolution engine schemas

class CircularResolutionPlan(BaseModel):
    stream_id: str
    stream_name: str
    material: str
    department: str
    supplier: str
    locked_recommendation: str
    circular_strategy_category: str
    risk_level: str
    human_review_required: bool
    rule_applied: str
    material_playbook_focus: str
    material_cycle: str | None = None
    core_circularity_question: str | None = None
    high_value_intervention_patterns: list[str] = []
    prevention_and_design_levers: list[str] = []
    routes_to_avoid: list[str] = []
    material_specific_evidence_tests: list[str] = []
    material_specific_red_flags: list[str] = []
    playbook_supplier_questions: list[str] = []
    playbook_process_questions: list[str] = []
    playbook_claim_controls: list[str] = []
    esrs_e5_mapping: list[str] = []
    cti_style_metrics: list[str] = []
    circular_problem: str
    specific_resolution_idea: str
    why_this_is_circular_economy: str
    value_retention_logic: str
    implementation_steps: list[str]
    supplier_or_procurement_action: str
    process_redesign_action: str
    industrial_symbiosis_action: str
    pilot_plan: str
    kpis: list[str]
    evidence_required: list[str]
    decision_gates: list[str]
    claim_boundary: str
    fallback_route: str
    confidence_notes: str
    circularity_route_strength: str
    estimated_annual_waste_diverted_kg: float
    estimated_annual_disposal_cost_avoided: float


class CircularResolutionSummary(BaseModel):
    total_plans: int
    controlled_review_plans: int
    claim_blocked_or_not_ready: int
    route_strength_breakdown: dict
    playbook_focus_breakdown: dict
    top_validation_candidates: list[dict]
    method_note: str


class RunCircularResolutionsResponse(BaseModel):
    generated_plans: int
    controlled_review_plans: int
    claim_blocked_or_not_ready: int
    message: str


# Milestone 7D: advanced material-specific circular playbooks

class AdvancedMaterialPlaybook(BaseModel):
    material_family: str
    material_cycle: str
    core_circularity_question: str
    best_fit_streams: list[str]
    high_value_intervention_patterns: list[str]
    prevention_and_design_levers: list[str]
    value_retention_levers: list[str]
    supplier_and_procurement_levers: list[str]
    industrial_symbiosis_partner_types: list[str]
    evidence_tests: list[str]
    red_flags: list[str]
    routes_to_avoid: list[str]
    pilot_patterns: list[str]
    kpis: list[str]
    claim_controls: list[str]
    esrs_e5_mapping: list[str]
    cti_style_metrics: list[str]
    circular_design_questions: list[str]
    fallback_controls: list[str]
    example_resolution_prompt: str


class MaterialPlaybookSummary(BaseModel):
    total_playbooks: int
    material_families: list[str]
    technical_cycle_count: int
    biological_or_water_energy_count: int
    coverage_note: str


# Milestone 7C: optional rules-locked LLM reasoning schemas

class AIReasoningStatus(BaseModel):
    ai_reasoning_enabled: bool
    openai_api_key_configured: bool
    llm_provider: str | None = None
    api_key_configured: bool | None = None
    configured_model: str
    configured_base_url: str | None = None
    mode: str
    guardrail_summary: str


class AIReasoningNarrative(BaseModel):
    stream_id: str
    stream_name: str
    generation_mode: str
    model_name: str
    decision_lock_status: str
    executive_summary: str
    circular_economy_reasoning: str
    evidence_gap_explanation: str
    supplier_questions: list[str]
    pilot_guidance: str
    claim_safety_note: str
    human_review_note: str
    implementation_risks: list[str]
    validation_warnings: list[str]
    locked_rule_applied: str | None = None
    locked_risk_level: str | None = None
    locked_human_review_required: bool | None = None
    locked_recommendation: str | None = None
    claim_boundary: str | None = None


# Milestone 8A: site-wide AI copilot schemas

class SiteAICopilotSummary(BaseModel):
    generation_mode: str
    model_name: str
    decision_lock_status: str
    executive_summary: str
    risk_summary: str
    opportunity_summary: str
    evidence_gap_summary: str
    supplier_procurement_summary: str
    human_review_priorities: list[str]
    recommended_next_actions: list[str]
    claim_safety_note: str
    governance_note: str
    validation_warnings: list[str]

# Milestone 8C: AI evidence gap explainer schemas

class AIEvidenceGapExplanation(BaseModel):
    generation_mode: str
    model_name: str
    stream_id: str
    stream_name: str
    decision_lock_status: str
    evidence_gap_summary: str
    claim_readiness_explanation: str
    evidence_to_collect: list[str]
    supplier_documents_required: list[str]
    process_checks_required: list[str]
    safe_current_statement: str
    unsafe_claims_to_avoid: list[str]
    recommended_review_gate: str
    governance_note: str
    validation_warnings: list[str]
    locked_rule_applied: str | None = None
    locked_risk_level: str | None = None
    locked_human_review_required: bool | None = None
    locked_claim_readiness: str | None = None
    locked_review_gate: str | None = None

# Milestone 8D: supplier evidence request drafting schemas

class SupplierEvidenceEmailDraft(BaseModel):
    generation_mode: str
    model_name: str
    stream_id: str
    stream_name: str
    supplier: str
    decision_lock_status: str
    draft_type: str
    subject: str
    email_body: str
    evidence_request_summary: list[str]
    attachments_or_documents_to_request: list[str]
    internal_follow_up_actions: list[str]
    claim_safety_note: str
    governance_note: str
    validation_warnings: list[str]
    locked_rule_applied: str | None = None
    locked_risk_level: str | None = None
    locked_human_review_required: bool | None = None
    locked_claim_readiness: str | None = None
    locked_procurement_route: str | None = None
    locked_review_gate: str | None = None
