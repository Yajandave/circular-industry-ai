"""SQLAlchemy models for industrial material and waste streams."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
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


# Milestone 9D: product data-model foundation

class Organisation(Base):
    """Business organisation using the Circular Industry AI workflow."""

    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organisation_name: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    sector: Mapped[str] = mapped_column(String(120), nullable=False, default="manufacturing")
    region: Mapped[str] = mapped_column(String(120), nullable=False, default="unspecified")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Site(Base):
    """Operational site where material streams are reviewed."""

    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organisation_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    site_name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    site_type: Mapped[str] = mapped_column(String(120), nullable=False, default="manufacturing")
    country: Mapped[str] = mapped_column(String(120), nullable=False, default="unspecified")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AnalysisRun(Base):
    """Metadata snapshot of one product analysis run."""

    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organisation_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    site_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    run_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    run_status: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    decision_source: Mapped[str] = mapped_column(String(120), nullable=False)
    stream_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommendation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    human_review_required_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    low_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    medium_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blocked_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_estimated_annual_waste_diverted_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total_estimated_annual_disposal_cost_avoided: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    governance_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# Milestone 9E: audit and traceability layer

class AuditEvent(Base):
    """Traceable product workflow event."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    entity_id: Mapped[str] = mapped_column(String(160), index=True, nullable=True)
    actor_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="system")
    actor_id: Mapped[str] = mapped_column(String(160), nullable=True)
    source: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    decision_source: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    claim_boundary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# Milestone 10E: generated insight history and traceability

class GeneratedInsight(Base):
    """Persisted autonomous insight record for audit and history."""

    __tablename__ = "generated_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stream_id: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    stream_name: Mapped[str] = mapped_column(String(255), nullable=False)
    material: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    source_process: Mapped[str] = mapped_column(String(160), nullable=False)
    analysis_run_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)

    input_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    matched_material_families_json: Mapped[str] = mapped_column(Text, nullable=False)
    current_action_json: Mapped[str] = mapped_column(Text, nullable=False)
    near_future_action_json: Mapped[str] = mapped_column(Text, nullable=False)
    future_watch_json: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_needed_json: Mapped[str] = mapped_column(Text, nullable=False)
    supplier_questions_json: Mapped[str] = mapped_column(Text, nullable=False)
    human_review_triggers_json: Mapped[str] = mapped_column(Text, nullable=False)
    do_not_claim_json: Mapped[str] = mapped_column(Text, nullable=False)
    source_knowledge_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_notes_json: Mapped[str] = mapped_column(Text, nullable=False)

    input_notes_present: Mapped[bool] = mapped_column(nullable=False, default=False)
    notes_dependency: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    insight_summary: Mapped[str] = mapped_column(Text, nullable=False)
    claim_boundary: Mapped[str] = mapped_column(Text, nullable=False)
    generation_mode: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="deterministic")
    governance_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )



# Milestone 20B.4: saved intervention scenario history

class SavedInterventionScenario(Base):
    """Immutable saved snapshot of one intervention screening scenario revision."""

    __tablename__ = "saved_intervention_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stream_id: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    scenario_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    lifecycle_stage: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="screening")

    stream_name: Mapped[str] = mapped_column(String(255), nullable=False)
    material: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    candidate_route: Mapped[str] = mapped_column(String(255), nullable=False)

    baseline_annual_quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_annual_disposal_cost_exposure: Mapped[float] = mapped_column(Float, nullable=False)
    addressable_fraction_pct: Mapped[float] = mapped_column(Float, nullable=False)
    technical_capture_rate_pct: Mapped[float] = mapped_column(Float, nullable=False)
    route_acceptance_rate_pct: Mapped[float] = mapped_column(Float, nullable=False)
    scenario_screened_fraction_pct: Mapped[float] = mapped_column(Float, nullable=False)
    scenario_screened_recoverable_quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)

    recommendation_confidence_score: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_quality_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    human_review_required: Mapped[bool] = mapped_column(nullable=False)
    scenario_status: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    claim_status: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    assumptions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    evidence_needed_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    formula: Mapped[str] = mapped_column(Text, nullable=False)
    governance_note: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )



# Milestone 20B.5: observed outcome evidence linked to saved scenarios

class ObservedScenarioOutcome(Base):
    """Immutable observed pilot/outcome record linked to one saved scenario revision."""

    __tablename__ = "observed_scenario_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    saved_scenario_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    stream_id: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    scenario_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    scenario_revision_number: Mapped[int] = mapped_column(Integer, nullable=False)

    observation_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    observation_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    observation_period_days: Mapped[int] = mapped_column(Integer, nullable=False)

    observed_recovered_quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    scenario_screened_quantity_for_period_kg: Mapped[float] = mapped_column(Float, nullable=False)
    variance_quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    variance_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    evidence_source_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    evidence_reference: Mapped[str] = mapped_column(Text, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    claim_status: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    governance_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
