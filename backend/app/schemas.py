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

# Milestone 8E: circular action report builder schemas

class CircularActionReport(BaseModel):
    generation_mode: str
    model_name: str
    stream_id: str
    stream_name: str
    decision_lock_status: str
    report_title: str
    executive_summary: str
    locked_recommendation: str
    risk_and_review_status: str
    evidence_position: str
    circular_resolution_summary: str
    supplier_loop_summary: str
    implementation_plan: list[str]
    evidence_to_collect: list[str]
    unsafe_claims_to_avoid: list[str]
    recommended_next_actions: list[str]
    claim_boundary: str
    governance_note: str
    validation_warnings: list[str]
    locked_rule_applied: str | None = None
    locked_risk_level: str | None = None
    locked_human_review_required: bool | None = None
    locked_claim_readiness: str | None = None
    locked_review_gate: str | None = None
    locked_procurement_route: str | None = None

# Milestone 9A: product workflow readiness schemas

class ProductWorkflowStep(BaseModel):
    name: str
    status: str
    detail: str
    required_next_action: str


class ProductWorkflowReadiness(BaseModel):
    product_stage: str
    backend_status: str
    alpha_exit_status: str
    total_streams: int
    total_recommendations: int
    ready_for_full_demo: bool
    evidence_summary: dict | None = None
    supplier_loop_summary: dict | None = None
    steps: list[ProductWorkflowStep]
    governance_note: str

# Milestone 7E / 9A: supplier-loop response schemas

class SupplierLoopPlan(BaseModel):
    stream_id: str
    stream_name: str
    material: str
    department: str
    supplier: str
    locked_recommendation: str
    risk_level: str
    human_review_required: bool
    rule_applied: str
    procurement_route: str
    supplier_loop_opportunity: str
    supplier_relationship_type: str
    reverse_logistics_model: str
    contract_levers: list[str]
    supplier_questions: list[str]
    supplier_evidence_required: list[str]
    acceptance_criteria: list[str]
    commercial_checks: list[str]
    operational_checks: list[str]
    data_requests: list[str]
    negotiation_position: str
    circular_procurement_clause: str
    procurement_priority: str
    pilot_scope: str
    review_gate: str
    claim_boundary: str
    fallback_position: str
    linked_esrs_e5_area: list[str]
    cti_procurement_metrics: list[str]
    material_playbook_supplier_levers: list[str]
    estimated_annual_value_at_stake: float


class SupplierLoopSummary(BaseModel):
    total_plans: int
    supplier_loop_candidates: int
    reverse_logistics_candidates: int
    contract_review_required: int
    controlled_supplier_reviews: int
    procurement_priority_breakdown: dict
    procurement_route_breakdown: dict
    top_supplier_actions: list[dict]
    method_note: str


class RunSupplierLoopsResponse(BaseModel):
    generated_plans: int
    supplier_loop_candidates: int
    controlled_supplier_reviews: int
    message: str

# Milestone 9B: AI runtime reliability schemas

class AIRuntimeStatus(BaseModel):
    ai_reasoning_enabled: bool
    llm_provider: str
    api_key_configured: bool
    configured_model: str
    configured_base_url: str
    timeout_seconds: int
    runtime_mode: str
    live_check_requested: bool
    live_check_status: str
    fallback_available: bool
    agentic_role: str
    guardrail_summary: str
    recommended_operator_action: str


# Milestone 9D: product data-model foundation schemas

class OrganisationRead(BaseModel):
    id: int
    organisation_name: str
    sector: str
    region: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SiteRead(BaseModel):
    id: int
    organisation_id: int
    site_name: str
    site_type: str
    country: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisRunRead(BaseModel):
    id: int
    organisation_id: int
    site_id: int
    run_name: str
    run_status: str
    decision_source: str
    stream_count: int
    recommendation_count: int
    human_review_required_count: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    blocked_count: int
    total_estimated_annual_waste_diverted_kg: float
    total_estimated_annual_disposal_cost_avoided: float
    governance_note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceContext(BaseModel):
    organisation: OrganisationRead
    site: SiteRead
    latest_analysis_run: AnalysisRunRead | None = None
    stream_summary: StreamSummary
    recommendation_summary: RecommendationSummary
    data_model_stage: str
    governance_note: str


# Milestone 9E: audit and traceability schemas

class AuditEventCreate(BaseModel):
    event_type: str
    entity_type: str
    entity_id: str | None = None
    actor_type: str = "system"
    actor_id: str | None = None
    source: str
    action: str
    summary: str
    decision_source: str
    claim_boundary: str
    metadata_json: dict = {}


class AuditEventRead(BaseModel):
    id: int
    event_type: str
    entity_type: str
    entity_id: str | None = None
    actor_type: str
    actor_id: str | None = None
    source: str
    action: str
    summary: str
    decision_source: str
    claim_boundary: str
    metadata_json: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditSummary(BaseModel):
    total_events: int
    event_type_breakdown: dict
    entity_type_breakdown: dict
    decision_source_breakdown: dict
    latest_events: list[AuditEventRead]
    governance_note: str


# Milestone 9F: data quality and import validation schemas

class DataQualityIssue(BaseModel):
    issue_type: str
    severity: str
    field: str
    stream_id: str | None = None
    message: str
    recommended_action: str


class DataQualityReport(BaseModel):
    dataset_label: str
    total_records: int
    readiness_status: str
    readiness_score: int
    critical_issue_count: int
    warning_issue_count: int
    info_issue_count: int
    duplicate_stream_ids: list[str]
    material_breakdown: dict
    department_breakdown: dict
    high_risk_data_flags: dict
    top_quantity_streams: list[dict]
    top_cost_streams: list[dict]
    issues: list[DataQualityIssue]
    governance_note: str


# Milestone 10C: knowledge retrieval engine schemas

class KnowledgeValidationSummary(BaseModel):
    valid: bool
    counts: dict
    source_count: int
    issues: list[str]
    governance_note: str


class KnowledgeStreamInput(BaseModel):
    stream_id: str | None = None
    stream_name: str
    material: str
    source_process: str
    monthly_quantity_kg: float | None = None
    current_route: str | None = None
    disposal_cost_per_month: float | None = None
    contamination_risk: str | None = None
    hazardous_flag: str | None = None
    department: str | None = None
    supplier: str | None = None
    supplier_takeback_available: str | None = None
    recycled_content_available: str | None = None
    notes: str | None = None


class KnowledgeRetrievalResult(BaseModel):
    stream_id: str
    stream_name: str
    material: str
    source_process: str
    matched_materials: list[dict]
    matched_routes: list[dict]
    evidence_rules: list[dict]
    future_horizon: list[dict]
    retrieval_notes: list[str]
    knowledge_validation: dict
    governance_note: str
