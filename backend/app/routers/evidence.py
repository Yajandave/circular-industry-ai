"""Evidence register and export endpoints."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.evidence_explainer.service import generate_evidence_gap_explanation
from app.evidence_register import build_evidence_record, build_evidence_register, build_evidence_summary

router = APIRouter(prefix="/api", tags=["evidence and exports"])


def _require_register(db: Session) -> list[dict]:
    streams = crud.get_streams(db, limit=500)
    recommendations = crud.get_recommendations(db, limit=500)
    if not streams:
        raise HTTPException(status_code=404, detail="No streams found. Load a dataset first.")
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Run POST /api/recommendations/run first.",
        )
    return build_evidence_register(streams, recommendations)


def _csv_response(rows: Iterable[dict], filename: str) -> StreamingResponse:
    rows = list(rows)
    buffer = StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    else:
        buffer.write("")
    buffer.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers=headers)


@router.get("/evidence-register", response_model=list[schemas.EvidenceRegisterRecord])
def list_evidence_register(db: Session = Depends(get_db)):
    """Return the evidence register behind the current recommendation run."""
    return _require_register(db)


@router.get("/evidence-register/summary", response_model=schemas.EvidenceRegisterSummary)
def evidence_register_summary(db: Session = Depends(get_db)):
    """Return evidence maturity and claim-readiness metrics."""
    records = _require_register(db)
    return build_evidence_summary(records)



@router.post("/evidence-register/{stream_id}/ai-explainer", response_model=schemas.AIEvidenceGapExplanation)
def explain_evidence_gap(stream_id: str, db: Session = Depends(get_db)):
    """Generate an advisory evidence-gap explanation for one locked recommendation."""
    stream = crud.get_stream_by_stream_id(db, stream_id)
    recommendation = crud.get_recommendation_by_stream_id(db, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail=f"No stream found for stream ID {stream_id}.")
    if not recommendation:
        raise HTTPException(status_code=404, detail="No recommendation found. Run POST /api/recommendations/run first.")
    evidence = build_evidence_record(stream, recommendation)
    return generate_evidence_gap_explanation(stream, recommendation, evidence)
@router.get("/export/evidence-register.csv")
def export_evidence_register(db: Session = Depends(get_db)):
    """Export the evidence register as CSV."""
    records = _require_register(db)
    return _csv_response(records, "circular-industry-ai-evidence-register.csv")


@router.get("/export/recommendations.csv")
def export_recommendations(db: Session = Depends(get_db)):
    """Export the rules-engine recommendation table as CSV."""
    recommendations = crud.get_recommendations(db, limit=500)
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Run POST /api/recommendations/run first.",
        )
    rows = [
        {
            "stream_id": rec.stream_id,
            "recommended_circular_action": rec.recommended_circular_action,
            "circular_strategy_category": rec.circular_strategy_category,
            "risk_level": rec.risk_level,
            "confidence_score": rec.confidence_score,
            "evidence_quality_score": rec.evidence_quality_score,
            "human_review_required": rec.human_review_required,
            "estimated_annual_waste_diverted_kg": rec.estimated_annual_waste_diverted_kg,
            "estimated_annual_disposal_cost_avoided": rec.estimated_annual_disposal_cost_avoided,
            "missing_data": rec.missing_data,
            "next_action": rec.next_action,
            "dashboard_priority": rec.dashboard_priority,
            "rule_applied": rec.rule_applied,
        }
        for rec in recommendations
    ]
    return _csv_response(rows, "circular-industry-ai-recommendations.csv")


