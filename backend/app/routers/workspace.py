"""Workspace, site and analysis-run metadata endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/workspace", tags=["workspace metadata"])


@router.get("/context", response_model=schemas.WorkspaceContext)
def get_workspace_context(db: Session = Depends(get_db)) -> schemas.WorkspaceContext:
    """Return the current default workspace/site and latest analysis-run snapshot.

    This is a product data-model foundation. It does not yet replace the existing
    single-dataset stream/recommendation workflow, but it gives the product a
    business-grade container around the current analysis state.
    """
    organisation, site = crud.ensure_default_workspace(db)
    latest_run = crud.get_latest_analysis_run(db, site_id=site.id)
    stream_summary = crud.get_stream_summary(db)
    recommendation_summary = crud.get_recommendation_summary(db)

    return schemas.WorkspaceContext(
        organisation=organisation,
        site=site,
        latest_analysis_run=latest_run,
        stream_summary=stream_summary,
        recommendation_summary=recommendation_summary,
        data_model_stage="Alpha 9D metadata foundation",
        governance_note=(
            "The workspace/site/analysis-run layer is metadata for organising product workflows. "
            "Existing stream and recommendation IDs remain the locked analysis records until a later "
            "migration introduces fully scoped project/site datasets."
        ),
    )


@router.post("/analysis-runs/snapshot", response_model=schemas.AnalysisRunRead)
def create_analysis_run_snapshot(db: Session = Depends(get_db)) -> schemas.AnalysisRunRead:
    """Create a metadata snapshot of the current loaded data and rules run."""
    organisation, site = crud.ensure_default_workspace(db)
    snapshot = crud.create_analysis_run_snapshot(db, organisation_id=organisation.id, site_id=site.id)
    crud.create_audit_event(
        db,
        event_type="analysis_run_snapshot",
        entity_type="analysis_run",
        entity_id=str(snapshot.id),
        actor_type="operator",
        actor_id="local_user",
        source="workspace_router",
        action="create_analysis_run_snapshot",
        summary=f"Created analysis-run metadata snapshot {snapshot.id} for the current workflow state.",
        decision_source="metadata_snapshot",
        claim_boundary="Analysis-run snapshot records current workflow outputs; it does not verify operational impact.",
        metadata={
            "analysis_run_id": snapshot.id,
            "stream_count": snapshot.stream_count,
            "recommendation_count": snapshot.recommendation_count,
            "human_review_required_count": snapshot.human_review_required_count,
        },
    )
    return snapshot


@router.get("/analysis-runs", response_model=list[schemas.AnalysisRunRead])
def list_analysis_runs(db: Session = Depends(get_db)) -> list[schemas.AnalysisRunRead]:
    """Return analysis-run metadata snapshots for the default site."""
    _, site = crud.ensure_default_workspace(db)
    return crud.get_analysis_runs(db, site_id=site.id, limit=50)

