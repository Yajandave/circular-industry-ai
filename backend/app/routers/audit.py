"""Audit and traceability endpoints for Circular Industry AI."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/audit", tags=["audit trail"])


@router.get("/events", response_model=list[schemas.AuditEventRead])
def list_audit_events(
    event_type: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.AuditEventRead]:
    """Return recent audit events for workflow traceability."""
    return crud.get_audit_events(
        db,
        event_type=event_type,
        entity_type=entity_type,
        limit=limit,
    )


@router.get("/summary", response_model=schemas.AuditSummary)
def audit_summary(db: Session = Depends(get_db)) -> schemas.AuditSummary:
    """Return summary counts for the audit trail."""
    return crud.get_audit_summary(db)


@router.post("/events", response_model=schemas.AuditEventRead)
def create_manual_audit_event(
    event: schemas.AuditEventCreate,
    db: Session = Depends(get_db),
) -> schemas.AuditEventRead:
    """Create a manual audit event.

    This is useful for Alpha/Beta testing, operator notes and later UI-driven
    review checkpoints. It should not be used to fabricate verification evidence.
    """
    return crud.create_audit_event(
        db,
        event_type=event.event_type,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        actor_type=event.actor_type,
        actor_id=event.actor_id,
        source=event.source,
        action=event.action,
        summary=event.summary,
        decision_source=event.decision_source,
        claim_boundary=event.claim_boundary,
        metadata=event.metadata_json,
    )
