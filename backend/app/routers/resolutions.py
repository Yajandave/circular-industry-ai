"""Circular resolution plan endpoints."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.circular_resolution.resolution_engine import build_resolution_plans, build_resolution_summary
from app.database import get_db

router = APIRouter(prefix="/api", tags=["circular resolution engine"])


def _require_resolution_plans(db: Session) -> list[dict]:
    streams = crud.get_streams(db, limit=500)
    recommendations = crud.get_recommendations(db, limit=500)
    if not streams:
        raise HTTPException(status_code=404, detail="No streams found. Load a dataset first.")
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Run POST /api/recommendations/run first.",
        )
    return build_resolution_plans(streams, recommendations)


def _csv_response(rows: Iterable[dict], filename: str) -> StreamingResponse:
    rows = list(rows)
    buffer = StringIO()
    if rows:
        flattened = []
        for row in rows:
            flat = {
                key: "; ".join(value) if isinstance(value, list) else value
                for key, value in row.items()
            }
            flattened.append(flat)
        writer = csv.DictWriter(buffer, fieldnames=list(flattened[0].keys()))
        writer.writeheader()
        writer.writerows(flattened)
    buffer.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers=headers)


@router.post("/resolutions/run", response_model=schemas.RunCircularResolutionsResponse)
def run_circular_resolutions(db: Session = Depends(get_db)):
    """Generate circular resolution plans from the locked recommendation run.

    Plans are generated dynamically and do not override the rules engine.
    """
    plans = _require_resolution_plans(db)
    summary = build_resolution_summary(plans)
    return schemas.RunCircularResolutionsResponse(
        generated_plans=summary["total_plans"],
        controlled_review_plans=summary["controlled_review_plans"],
        claim_blocked_or_not_ready=summary["claim_blocked_or_not_ready"],
        message="Circular resolution plans generated from locked recommendation outputs.",
    )


@router.get("/resolutions", response_model=list[schemas.CircularResolutionPlan])
def list_resolution_plans(db: Session = Depends(get_db)):
    """Return circular resolution plans for all generated recommendations."""
    return _require_resolution_plans(db)


@router.get("/resolutions/summary", response_model=schemas.CircularResolutionSummary)
def resolution_summary(db: Session = Depends(get_db)):
    """Return summary metrics for circular resolution plans."""
    return build_resolution_summary(_require_resolution_plans(db))


@router.get("/resolutions/{stream_id}", response_model=schemas.CircularResolutionPlan)
def get_resolution_plan(stream_id: str, db: Session = Depends(get_db)):
    """Return one circular resolution plan by stream ID."""
    for plan in _require_resolution_plans(db):
        if plan["stream_id"] == stream_id:
            return plan
    raise HTTPException(status_code=404, detail=f"No resolution plan found for stream ID {stream_id}.")


@router.get("/export/resolution-plans.csv")
def export_resolution_plans(db: Session = Depends(get_db)):
    """Export circular resolution plans as CSV."""
    return _csv_response(_require_resolution_plans(db), "circular-industry-ai-resolution-plans.csv")
