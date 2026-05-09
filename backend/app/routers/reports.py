"""Circular action report endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.circular_resolution.resolution_engine import build_resolution_plan
from app.database import get_db
from app.evidence_register import build_evidence_record
from app.procurement.supplier_loop_engine import build_supplier_loop_plan
from app.report_builder.service import generate_circular_action_report

router = APIRouter(prefix="/api/reports", tags=["circular action reports"])


@router.post("/streams/{stream_id}/circular-action-report", response_model=schemas.CircularActionReport)
def build_stream_circular_action_report(stream_id: str, db: Session = Depends(get_db)):
    """Generate a controlled circular action report for one stream."""
    stream = crud.get_stream_by_stream_id(db, stream_id)
    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)

    if not stream:
        raise HTTPException(status_code=404, detail=f"No stream found for stream ID {stream_id}.")
    if not recommendation:
        raise HTTPException(status_code=404, detail="No recommendation found. Run POST /api/recommendations/run first.")

    evidence = build_evidence_record(stream, recommendation)
    resolution = build_resolution_plan(stream, recommendation)
    supplier_plan = build_supplier_loop_plan(stream, recommendation, resolution)

    return generate_circular_action_report(stream, recommendation, evidence, resolution, supplier_plan)
